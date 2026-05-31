import json
import os

import requests

from database.db import (
    get_notification_delivery,
    get_notification_preferences,
    upsert_notification_delivery,
)


SEVERITY_RANK = {
    "info": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


def _meets_minimum_severity(alert: dict, minimum_severity: str) -> bool:
    return SEVERITY_RANK.get(alert["severity"], 0) >= SEVERITY_RANK.get(minimum_severity, 2)


def _notification_text(alert: dict) -> str:
    dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8501").rstrip("/")
    return (
        f"Revenue OS Alert: {alert['title']}\n"
        f"{alert['message']}\n"
        f"Priority: {alert['severity'].upper()}\n"
        f"Open dashboard: {dashboard_url}"
    )


def _send_resend_email(destination: str, alert: dict) -> tuple[str, str | None]:
    api_key = os.getenv("RESEND_API_KEY", "").strip()
    sender = os.getenv("ALERT_EMAIL_FROM", "").strip()
    if not api_key or not sender:
        return "pending_configuration", None

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": sender,
            "to": [email.strip() for email in destination.split(",") if email.strip()],
            "subject": f"[{alert['severity'].upper()}] {alert['title']}",
            "text": _notification_text(alert),
        },
        timeout=15,
    )
    response.raise_for_status()
    return "sent", response.json().get("id")


def _send_twilio_message(destination: str, alert: dict, channel: str) -> tuple[str, str | None]:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_number = os.getenv(
        "TWILIO_WHATSAPP_FROM" if channel == "whatsapp" else "TWILIO_SMS_FROM",
        "",
    ).strip()
    if not account_sid or not auth_token or not from_number:
        return "pending_configuration", None

    to_number = f"whatsapp:{destination}" if channel == "whatsapp" else destination
    source_number = f"whatsapp:{from_number}" if channel == "whatsapp" else from_number
    message_data = {
        "From": source_number,
        "To": to_number,
        "Body": _notification_text(alert),
    }
    whatsapp_content_sid = os.getenv("TWILIO_WHATSAPP_CONTENT_SID", "").strip()
    if channel == "whatsapp" and whatsapp_content_sid:
        message_data = {
            "From": source_number,
            "To": to_number,
            "ContentSid": whatsapp_content_sid,
            "ContentVariables": json.dumps(
                {
                    "1": alert["title"],
                    "2": alert["message"],
                    "3": alert["severity"].upper(),
                    "4": os.getenv("DASHBOARD_URL", "http://localhost:8501").rstrip("/"),
                }
            ),
        }
    response = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        auth=(account_sid, auth_token),
        data=message_data,
        timeout=15,
    )
    response.raise_for_status()
    return "sent", response.json().get("sid")


def dispatch_alert_notifications(tenant_id: int, alerts: list[dict]):
    preferences = get_notification_preferences(tenant_id)
    deliveries = []
    for alert in alerts:
        if not _meets_minimum_severity(alert, preferences["minimum_severity"]):
            continue

        channels = []
        if preferences["email_enabled"] and preferences["email_recipients"]:
            channels.append(("email", preferences["email_recipients"]))
        if (
            preferences["whatsapp_enabled"]
            and preferences["whatsapp_phone"]
            and preferences["whatsapp_opt_in"]
        ):
            channels.append(("whatsapp", preferences["whatsapp_phone"]))
        if preferences["sms_enabled"] and preferences["sms_phone"]:
            channels.append(("sms", preferences["sms_phone"]))

        for channel, destination in channels:
            existing_delivery = get_notification_delivery(alert["id"], channel)
            if existing_delivery and existing_delivery["status"] == "sent":
                continue
            try:
                if channel == "email":
                    status, provider_message_id = _send_resend_email(destination, alert)
                else:
                    status, provider_message_id = _send_twilio_message(destination, alert, channel)
                error_message = (
                    "Provider credentials are not configured."
                    if status == "pending_configuration"
                    else None
                )
            except requests.RequestException as error:
                status = "failed"
                provider_message_id = None
                error_message = str(error)[:500]

            delivery = upsert_notification_delivery(
                tenant_id=tenant_id,
                alert_id=alert["id"],
                channel=channel,
                destination=destination,
                status=status,
                provider_message_id=provider_message_id,
                error_message=error_message,
            )
            if delivery:
                deliveries.append(delivery)
    return deliveries
