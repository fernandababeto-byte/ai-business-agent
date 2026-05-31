import hashlib
import hmac
import os
import secrets
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from database.db import (
    consume_shopify_oauth_state,
    get_shopify_connection,
    get_shopify_connection_with_token,
    get_latest_shopify_sync_snapshot,
    get_recent_shopify_sync_snapshots,
    save_shopify_connection,
    save_shopify_oauth_state,
    save_revenue_alerts,
    save_shopify_sync_snapshot,
)
from services.notification_service import dispatch_alert_notifications


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_SCOPES = "read_orders,read_products,read_inventory,read_locations,read_customers"
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-04")


def get_shopify_client_id():
    client_id = os.getenv("SHOPIFY_CLIENT_ID")
    if not client_id:
        raise RuntimeError("SHOPIFY_CLIENT_ID precisa estar definido no .env.")
    return client_id


def get_shopify_client_secret():
    client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")
    if not client_secret:
        raise RuntimeError("SHOPIFY_CLIENT_SECRET precisa estar definido no .env.")
    return client_secret


def get_shopify_app_url():
    return os.getenv("SHOPIFY_APP_URL", "http://localhost:8000").rstrip("/")


def normalize_shop_domain(shop: str) -> str:
    shop = (shop or "").strip().lower()
    shop = shop.replace("https://", "").replace("http://", "").split("/")[0]
    if "." not in shop:
        shop = f"{shop}.myshopify.com"
    if not shop.endswith(".myshopify.com"):
        raise ValueError("Use a valid Shopify store domain, for example mystore.myshopify.com.")
    return shop


def build_install_url(shop: str, tenant_id: int, user_id: int) -> str:
    shop_domain = normalize_shop_domain(shop)
    state = secrets.token_urlsafe(32)
    save_shopify_oauth_state(state, tenant_id, user_id, shop_domain)

    redirect_uri = f"{get_shopify_app_url()}/shopify/callback"
    query = urlencode(
        {
            "client_id": get_shopify_client_id(),
            "scope": os.getenv("SHOPIFY_SCOPES", DEFAULT_SCOPES),
            "redirect_uri": redirect_uri,
            "state": state,
            "grant_options[]": "offline",
        }
    )
    return f"https://{shop_domain}/admin/oauth/authorize?{query}"


def verify_shopify_hmac(query_params: dict) -> bool:
    received_hmac = query_params.get("hmac")
    if not received_hmac:
        return False

    message_items = []
    for key in sorted(query_params):
        if key in {"hmac", "signature"}:
            continue
        value = query_params[key]
        if isinstance(value, list):
            value = ",".join(value)
        message_items.append(f"{key}={value}")

    message = "&".join(message_items)
    digest = hmac.new(
        get_shopify_client_secret().encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(digest, received_hmac)


def exchange_code_for_token(shop_domain: str, code: str) -> dict:
    response = requests.post(
        f"https://{shop_domain}/admin/oauth/access_token",
        json={
            "client_id": get_shopify_client_id(),
            "client_secret": get_shopify_client_secret(),
            "code": code,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def complete_oauth_callback(query_params: dict):
    if not verify_shopify_hmac(query_params):
        raise ValueError("Invalid Shopify HMAC.")

    state_row = consume_shopify_oauth_state(query_params.get("state", ""))
    if not state_row:
        raise ValueError("Invalid or expired Shopify OAuth state.")

    shop_domain = normalize_shop_domain(query_params.get("shop", ""))
    if shop_domain != state_row["shop_domain"]:
        raise ValueError("Shopify shop does not match OAuth state.")

    token_data = exchange_code_for_token(shop_domain, query_params.get("code", ""))
    access_token = token_data["access_token"]
    scopes = token_data.get("scope", os.getenv("SHOPIFY_SCOPES", DEFAULT_SCOPES))

    return save_shopify_connection(
        tenant_id=state_row["tenant_id"],
        shop_domain=shop_domain,
        access_token=access_token,
        scopes=scopes,
    )


def get_connection_status(tenant_id: int):
    connection = get_shopify_connection(tenant_id)
    if not connection:
        return {
            "status": "not_connected",
            "shop_domain": None,
            "connected_at": None,
            "last_sync_at": None,
            "scopes": None,
            "latest_sync": None,
            "recent_syncs": [],
        }
    status = dict(connection)
    latest_sync = get_latest_shopify_sync_snapshot(tenant_id)
    status["latest_sync"] = dict(latest_sync) if latest_sync else None
    status["recent_syncs"] = [
        dict(snapshot)
        for snapshot in get_recent_shopify_sync_snapshots(tenant_id)
    ]
    return status


def shopify_graphql(tenant_id: int, query: str, variables: dict | None = None):
    connection = get_shopify_connection_with_token(tenant_id)
    if not connection or connection["status"] != "connected":
        raise ValueError("Shopify is not connected for this tenant.")

    response = requests.post(
        f"https://{connection['shop_domain']}/admin/api/{SHOPIFY_API_VERSION}/graphql.json",
        headers={
            "X-Shopify-Access-Token": connection["access_token"],
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "variables": variables or {},
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        messages = ", ".join(error.get("message", "Unknown Shopify error") for error in payload["errors"])
        raise ValueError(f"Shopify GraphQL error: {messages}")
    return payload


def _collect_connection_nodes(tenant_id: int, query: str, root_key: str) -> list[dict]:
    nodes = []
    cursor = None
    while True:
        payload = shopify_graphql(tenant_id, query, {"cursor": cursor})
        connection = payload["data"][root_key]
        nodes.extend(connection["nodes"])
        page_info = connection["pageInfo"]
        if not page_info["hasNextPage"]:
            return nodes
        cursor = page_info["endCursor"]


def _calculate_sync_comparison(previous_snapshot: dict | None, summary: dict) -> dict:
    if not previous_snapshot:
        return {
            "has_baseline": False,
            "new_orders": 0,
            "revenue_delta": Decimal("0"),
            "inventory_delta": 0,
            "inventory_change_rate": None,
            "new_order_average": None,
            "new_order_average_change_rate": None,
        }

    previous_revenue = Decimal(previous_snapshot.get("revenue_total") or 0)
    previous_inventory = int(previous_snapshot.get("inventory_units") or 0)
    previous_order_count = int(previous_snapshot.get("order_count") or 0)
    previous_average_order_value = Decimal(previous_snapshot.get("average_order_value") or 0)
    revenue_delta = summary["revenue_total"] - previous_revenue
    inventory_delta = summary["inventory_units"] - previous_inventory
    new_orders = max(0, summary["order_count"] - previous_order_count)
    inventory_change_rate = None
    if previous_inventory:
        inventory_change_rate = (Decimal(inventory_delta) / Decimal(previous_inventory)) * 100
    new_order_average = None
    new_order_average_change_rate = None
    if new_orders and revenue_delta >= 0:
        new_order_average = revenue_delta / Decimal(new_orders)
        if previous_average_order_value:
            new_order_average_change_rate = (
                (new_order_average - previous_average_order_value)
                / previous_average_order_value
            ) * 100

    return {
        "has_baseline": True,
        "new_orders": new_orders,
        "revenue_delta": revenue_delta,
        "inventory_delta": inventory_delta,
        "inventory_change_rate": inventory_change_rate,
        "new_order_average": new_order_average,
        "new_order_average_change_rate": new_order_average_change_rate,
    }


def _serialize_sync_comparison(comparison: dict) -> dict:
    return {
        key: str(value) if isinstance(value, Decimal) else value
        for key, value in comparison.items()
    }


def sync_shopify_store(tenant_id: int):
    connection = get_shopify_connection(tenant_id)
    if not connection or connection["status"] != "connected":
        raise ValueError("Connect a Shopify store before starting synchronization.")

    shop_query = """
    query ShopSyncInfo {
      shop {
        name
        myshopifyDomain
        currencyCode
      }
    }
    """
    orders_query = """
    query SyncOrders($cursor: String) {
      orders(first: 100, after: $cursor, sortKey: CREATED_AT, reverse: true) {
        nodes {
          id
          name
          createdAt
          displayFinancialStatus
          currentTotalPriceSet { shopMoney { amount currencyCode } }
          lineItems(first: 100) {
            nodes {
              title
              quantity
              discountedTotalSet { shopMoney { amount currencyCode } }
              product { productType }
            }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
    """
    products_query = """
    query SyncProducts($cursor: String) {
      products(first: 100, after: $cursor, sortKey: CREATED_AT, reverse: true) {
        nodes {
          id
          title
          status
          productType
          totalInventory
          variants(first: 100) {
            nodes { id title inventoryQuantity }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
    """
    locations_query = """
    query SyncLocations($cursor: String) {
      locations(first: 100, after: $cursor) {
        nodes { id name isActive }
        pageInfo { hasNextPage endCursor }
      }
    }
    """

    shop = shopify_graphql(tenant_id, shop_query)["data"]["shop"]
    orders = _collect_connection_nodes(tenant_id, orders_query, "orders")
    products = _collect_connection_nodes(tenant_id, products_query, "products")
    locations = _collect_connection_nodes(tenant_id, locations_query, "locations")

    revenue_total = sum(
        Decimal(order["currentTotalPriceSet"]["shopMoney"]["amount"])
        for order in orders
    )
    order_values = [
        Decimal(order["currentTotalPriceSet"]["shopMoney"]["amount"])
        for order in orders
    ]
    average_order_value = revenue_total / len(order_values) if order_values else Decimal("0")
    category_revenue = {}
    for order in orders:
        for line_item in order.get("lineItems", {}).get("nodes", []):
            product = line_item.get("product") or {}
            category = (product.get("productType") or "").strip() or "Uncategorized"
            amount = Decimal(line_item["discountedTotalSet"]["shopMoney"]["amount"])
            category_revenue[category] = category_revenue.get(category, Decimal("0")) + amount
    category_revenue_rows = [
        {"category": category, "revenue": str(amount)}
        for category, amount in sorted(
            category_revenue.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]
    growth_rate = None
    if len(order_values) >= 2 and order_values[1] != 0:
        growth_rate = ((order_values[0] - order_values[1]) / order_values[1]) * 100
    recent_values = order_values[:3]
    recent_average = sum(recent_values, Decimal("0")) / len(recent_values) if recent_values else Decimal("0")
    forecast_revenue = revenue_total + recent_average
    variants = [
        variant
        for product in products
        for variant in product["variants"]["nodes"]
    ]
    inventory_units = sum(int(product.get("totalInventory") or 0) for product in products)
    low_inventory_products = sum(int(product.get("totalInventory") or 0) <= 10 for product in products)
    concentration_ratio = (max(order_values) / revenue_total) if revenue_total else Decimal("0")
    risk_score = min(
        Decimal("100"),
        (concentration_ratio * 55)
        + (Decimal(low_inventory_products) / max(Decimal(len(products)), Decimal("1")) * 30)
        + (Decimal("15") if len(order_values) < 10 else Decimal("0")),
    )
    summary = {
        "currency_code": shop["currencyCode"],
        "order_count": len(orders),
        "product_count": len(products),
        "active_product_count": sum(product["status"] == "ACTIVE" for product in products),
        "variant_count": len(variants),
        "location_count": len(locations),
        "inventory_units": inventory_units,
        "revenue_total": revenue_total,
        "average_order_value": average_order_value,
        "growth_rate": growth_rate,
        "forecast_revenue": forecast_revenue,
        "risk_score": risk_score,
    }
    previous_snapshot = get_latest_shopify_sync_snapshot(tenant_id)
    comparison = _calculate_sync_comparison(previous_snapshot, summary)
    serialized_comparison = _serialize_sync_comparison(comparison)
    payload = {
        "shop": shop,
        "orders": orders,
        "products": products,
        "locations": locations,
        "category_revenue": category_revenue_rows,
        "sync_comparison": serialized_comparison,
    }
    snapshot = save_shopify_sync_snapshot(
        tenant_id=tenant_id,
        shop_domain=connection["shop_domain"],
        summary=summary,
        payload=payload,
    )
    alerts = []
    if risk_score >= Decimal("40"):
        alerts.append(
            {
                "alert_key": "operational-risk-elevated",
                "alert_type": "operational_risk",
                "severity": "high" if risk_score >= Decimal("70") else "medium",
                "title": "Operational risk requires review",
                "message": (
                    f"Shopify operational risk reached {risk_score:.0f}/100 due to "
                    "revenue concentration and inventory exposure."
                ),
                "metric_value": risk_score,
            }
        )
    if low_inventory_products:
        alerts.append(
            {
                "alert_key": "inventory-low-stock",
                "alert_type": "inventory_risk",
                "severity": "high" if low_inventory_products >= 3 else "medium",
                "title": "Low inventory exposure detected",
                "message": (
                    f"{low_inventory_products} Shopify products have 10 or fewer "
                    "inventory units available."
                ),
                "metric_value": low_inventory_products,
            }
        )
    if concentration_ratio >= Decimal("0.35"):
        alerts.append(
            {
                "alert_key": "revenue-concentration",
                "alert_type": "revenue_risk",
                "severity": "high" if concentration_ratio >= Decimal("0.50") else "medium",
                "title": "Revenue concentration is elevated",
                "message": (
                    f"{concentration_ratio * 100:.1f}% of synced revenue depends on "
                    "a single order."
                ),
                "metric_value": concentration_ratio * 100,
            }
        )
    if growth_rate is not None and growth_rate < 0:
        alerts.append(
            {
                "alert_key": "revenue-momentum-decline",
                "alert_type": "revenue_drop",
                "severity": "high" if growth_rate <= Decimal("-15") else "medium",
                "title": "Revenue momentum declined",
                "message": (
                    f"The latest Shopify order value decreased {abs(growth_rate):.1f}% "
                    "versus the previous order."
                ),
                "metric_value": growth_rate,
            }
        )
    elif growth_rate is not None and growth_rate >= Decimal("5"):
        alerts.append(
            {
                "alert_key": "growth-opportunity",
                "alert_type": "growth_opportunity",
                "severity": "info",
                "title": "Growth opportunity detected",
                "message": (
                    f"The latest Shopify order value increased {growth_rate:.1f}% "
                    "versus the previous order."
                ),
                "metric_value": growth_rate,
            }
        )
    if comparison["has_baseline"] and comparison["revenue_delta"] < 0:
        alerts.append(
            {
                "alert_key": "revenue-total-anomaly",
                "alert_type": "revenue_anomaly",
                "severity": "high",
                "title": "Revenue anomaly detected",
                "message": (
                    f"Synchronized Shopify revenue decreased "
                    f"{abs(comparison['revenue_delta']):.2f} {shop['currencyCode']} "
                    "since the previous sync. Review refunds, cancellations or order changes."
                ),
                "metric_value": comparison["revenue_delta"],
            }
        )
    new_order_average_change_rate = comparison["new_order_average_change_rate"]
    if (
        comparison["has_baseline"]
        and new_order_average_change_rate is not None
        and new_order_average_change_rate <= Decimal("-25")
    ):
        alerts.append(
            {
                "alert_key": "average-order-value-anomaly",
                "alert_type": "revenue_anomaly",
                "severity": "high" if new_order_average_change_rate <= Decimal("-40") else "medium",
                "title": "Average order value anomaly detected",
                "message": (
                    f"New Shopify orders average {comparison['new_order_average']:.2f} "
                    f"{shop['currencyCode']}, {abs(new_order_average_change_rate):.1f}% "
                    "below the previous synchronized average."
                ),
                "metric_value": new_order_average_change_rate,
            }
        )
    inventory_change_rate = comparison["inventory_change_rate"]
    if (
        comparison["has_baseline"]
        and comparison["inventory_delta"] <= -5
        and inventory_change_rate is not None
        and inventory_change_rate <= Decimal("-20")
    ):
        alerts.append(
            {
                "alert_key": "inventory-movement-anomaly",
                "alert_type": "inventory_anomaly",
                "severity": "high" if inventory_change_rate <= Decimal("-35") else "medium",
                "title": "Inventory movement requires review",
                "message": (
                    f"Shopify inventory decreased by {abs(comparison['inventory_delta'])} units "
                    f"({abs(inventory_change_rate):.1f}%) since the previous sync."
                ),
                "metric_value": inventory_change_rate,
            }
        )
    saved_alerts = save_revenue_alerts(tenant_id, snapshot["id"], alerts)
    dispatch_alert_notifications(tenant_id, saved_alerts)
    snapshot["active_alert_count"] = len(saved_alerts)
    snapshot["comparison"] = serialized_comparison
    return dict(snapshot)
