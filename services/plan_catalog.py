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
