from datetime import datetime, timezone


TRIAL_DAYS = 14

PLAN_CATALOG = {
    "revenue_intelligence": {
        "name": "Revenue Intelligence",
        "price": 99,
        "tagline": "Revenue protection for Shopify operators.",
        "features": [
            "Executive Dashboard",
            "Revenue Monitoring",
            "Revenue Risk Center",
            "AI Revenue Advisor",
            "Forecast Engine",
            "14-Day Free Trial",
        ],
    },
    "growth_intelligence": {
        "name": "Growth Intelligence",
        "price": 199,
        "tagline": "Advanced monitoring and opportunity prioritization.",
        "features": [
            "Everything in Revenue Intelligence",
            "Automatic Alerts",
            "Executive Reports",
            "Advanced Monitoring",
            "Opportunity Prioritization",
        ],
    },
    "revenue_os": {
        "name": "Revenue OS",
        "price": 399,
        "tagline": "Multi-store revenue control room for executive teams.",
        "features": [
            "Everything in Growth Intelligence",
            "Multi-store Shopify",
            "Executive Reports",
            "Advanced AI Recommendations",
            "Priority Support",
        ],
    },
}


def get_plan(plan_key: str | None):
    return PLAN_CATALOG.get(plan_key or "", PLAN_CATALOG["revenue_intelligence"])


def get_trial_days_left(tenant: dict) -> int:
    trial_ends_at = tenant.get("tenant_trial_ends_at") or tenant.get("trial_ends_at")
    if not trial_ends_at:
        return TRIAL_DAYS

    if isinstance(trial_ends_at, str):
        trial_ends_at = datetime.fromisoformat(trial_ends_at.replace("Z", "+00:00"))
    if trial_ends_at.tzinfo is None:
        trial_ends_at = trial_ends_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    return max(0, int((trial_ends_at - now).total_seconds() // 86400) + 1)


def get_commercial_status(tenant: dict) -> dict:
    subscription_status = str(
        tenant.get("tenant_subscription_status")
        or tenant.get("subscription_status")
        or "trialing"
    ).lower()
    trial_days_left = get_trial_days_left(tenant)
    has_active_subscription = subscription_status in {"active", "trialing_subscription"}
    is_trial_active = trial_days_left > 0 and subscription_status not in {"canceled", "past_due"}
    has_access = has_active_subscription or is_trial_active

    if has_active_subscription:
        status = "active"
    elif is_trial_active:
        status = "trialing"
    else:
        status = "expired"

    return {
        "status": status,
        "has_access": has_access,
        "is_trial_active": is_trial_active,
        "trial_days_left": trial_days_left,
        "subscription_status": subscription_status,
        "plan_key": tenant.get("tenant_plan") or tenant.get("plan") or "revenue_intelligence",
    }
