import hashlib
import hmac
import json
import os
import time
from datetime import datetime

import requests

from database.db import (
    get_tenant_by_id,
    list_tenants,
    update_tenant_subscription,
    update_tenant_subscription_by_billing_id,
)
from services.plan_catalog import PLAN_CATALOG, get_commercial_status, get_plan


PADDLE_API_URLS = {
    "sandbox": "https://sandbox-api.paddle.com",
    "production": "https://api.paddle.com",
}


def get_paddle_api_url() -> str:
    environment = os.getenv("PADDLE_ENVIRONMENT", "sandbox").strip().lower()
    return PADDLE_API_URLS.get(environment, PADDLE_API_URLS["sandbox"])


def get_paddle_api_key() -> str:
    return os.getenv("PADDLE_API_KEY", "").strip()


def get_paddle_price_id(plan_key: str) -> str:
    return os.getenv(f"PADDLE_PRICE_{plan_key.upper()}", "").strip()


def is_paddle_configured() -> bool:
    return bool(
        get_paddle_api_key()
        and all(get_paddle_price_id(plan_key) for plan_key in PLAN_CATALOG)
    )


def get_billing_status(tenant_id: int) -> dict:
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        raise ValueError("Tenant not found.")

    status = get_commercial_status(dict(tenant))
    return {
        **status,
        "plan": get_plan(status["plan_key"]),
        "billing_provider": "paddle",
        "checkout_configured": is_paddle_configured(),
        "subscription_current_period_end": tenant.get("subscription_current_period_end"),
    }


def list_tenant_commercial_statuses() -> list[dict]:
    rows = []
    for tenant in list_tenants():
        commercial = get_commercial_status(dict(tenant))
        rows.append(
            {
                "id": tenant["id"],
                "company": tenant["name"],
                "plan": get_plan(commercial["plan_key"])["name"],
                "status": commercial["status"],
                "trial_days_left": commercial["trial_days_left"],
                "subscription_status": commercial["subscription_status"],
                "active": tenant["is_active"],
            }
        )
    return rows


def create_checkout_session(tenant_id: int, email: str, plan_key: str) -> str:
    if plan_key not in PLAN_CATALOG:
        raise ValueError("Invalid plan.")

    api_key = get_paddle_api_key()
    price_id = get_paddle_price_id(plan_key)
    if not api_key or not price_id:
        raise ValueError("Paddle checkout is not configured yet.")

    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        raise ValueError("Tenant not found.")

    response = requests.post(
        f"{get_paddle_api_url()}/transactions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "items": [{"price_id": price_id, "quantity": 1}],
            "collection_mode": "automatic",
            "custom_data": {
                "tenant_id": str(tenant_id),
                "plan_key": plan_key,
                "customer_email": email,
            },
        },
        timeout=15,
    )
    response.raise_for_status()
    checkout_url = response.json().get("data", {}).get("checkout", {}).get("url")
    if not checkout_url:
        raise ValueError(
            "Paddle did not return a checkout URL. Configure the default payment link in Paddle Checkout settings."
        )
    return checkout_url


def _parse_paddle_signature(signature_header: str) -> tuple[str, list[str]]:
    timestamp = ""
    signatures = []
    for part in signature_header.split(";"):
        key, _, value = part.partition("=")
        if key == "ts":
            timestamp = value
        elif key == "h1":
            signatures.append(value)
    return timestamp, signatures


def verify_paddle_webhook(payload: bytes, signature_header: str) -> None:
    webhook_secret = os.getenv("PADDLE_WEBHOOK_SECRET", "").strip()
    if not webhook_secret:
        raise ValueError("Paddle webhook secret is not configured.")

    timestamp, signatures = _parse_paddle_signature(signature_header)
    if not timestamp or not signatures:
        raise ValueError("Invalid Paddle signature.")
    if abs(time.time() - int(timestamp)) > 300:
        raise ValueError("Expired Paddle signature.")

    signed_payload = f"{timestamp}:".encode("utf-8") + payload
    expected = hmac.new(
        webhook_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    if not any(hmac.compare_digest(expected, signature) for signature in signatures):
        raise ValueError("Invalid Paddle signature.")


def _iso_to_datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _subscription_period_end(resource: dict):
    return _iso_to_datetime((resource.get("current_billing_period") or {}).get("ends_at"))


def process_paddle_webhook(payload: bytes, signature_header: str) -> dict:
    verify_paddle_webhook(payload, signature_header)
    event = json.loads(payload.decode("utf-8"))
    event_type = event.get("event_type", "")
    resource = event.get("data", {})
    custom_data = resource.get("custom_data") or {}

    if event_type == "subscription.created":
        tenant_id = int(custom_data["tenant_id"])
        update_tenant_subscription(
            tenant_id,
            plan=custom_data.get("plan_key"),
            subscription_status=resource.get("status") or "active",
            billing_customer_id=resource.get("customer_id"),
            billing_subscription_id=resource.get("id"),
            subscription_current_period_end=_subscription_period_end(resource),
        )
    elif event_type in {"subscription.updated", "subscription.canceled"}:
        update_tenant_subscription_by_billing_id(
            resource["id"],
            subscription_status=resource.get("status") or "canceled",
            subscription_current_period_end=_subscription_period_end(resource),
        )

    return {"received": True, "type": event_type}
