"""Sync integration with simulated GraphQL and persistence; no live services."""
import importlib.util
from decimal import Decimal
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]


class ShopifySyncScenarioTests(unittest.TestCase):
    def setUp(self):
        # Import the complete service while replacing only external boundaries.
        self.db = MagicMock()
        self.notifications = MagicMock()
        self.http = MagicMock()
        spec = importlib.util.spec_from_file_location(
            "shopify_service_under_test", ROOT / "services/shopify_service.py")
        self.service = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {
            "database.db": self.db,
            "services.notification_service": self.notifications,
            "requests": self.http,
            "dotenv": MagicMock(),
        }):
            spec.loader.exec_module(self.service)
        self.db.get_shopify_connection.return_value = {
            "status": "connected", "shop_domain": "example.myshopify.com"}
        self.db.get_latest_shopify_sync_snapshot.return_value = None
        self.db.save_shopify_sync_snapshot.side_effect = (
            lambda **kwargs: {"id": 42, **kwargs["summary"]})
        self.db.save_revenue_alerts.return_value = []
        self.calls = []
        self.pages = [[]]
        self.service.shopify_graphql = MagicMock(side_effect=self.graphql)

    def graphql(self, tenant_id, query, variables=None):
        self.assertEqual(tenant_id, 7)
        self.calls.append((query, variables))
        if "ShopSyncInfo" in query:
            return {"data": {"shop": {"currencyCode": "CAD"}}}
        if "SyncOrders" in query:
            self.assertIn("sortKey: CREATED_AT, reverse: true", query)
            index = int(variables["cursor"] or 0)
            more = index + 1 < len(self.pages)
            nodes = [
                {"currentTotalPriceSet": {"shopMoney": {"amount": v}},
                 "lineItems": {"nodes": []}}
                for v in self.pages[index]
            ]
            key = "orders"
        else:
            key = "products" if "SyncProducts" in query else "locations"
            nodes, more, index = [], False, 0
        return {"data": {key: {
            "nodes": nodes,
            "pageInfo": {"hasNextPage": more, "endCursor": str(index + 1)},
        }}}

    def test_paginated_orders_feed_scenario_and_persistence(self):
        self.pages = [["30", "20"], ["10", "100"]]
        result = self.service.sync_shopify_store(7)
        self.assertEqual(result["forecast_revenue"], Decimal("180"))
        self.assertEqual(result["revenue_total"], Decimal("160"))
        self.assertEqual(result["order_count"], 4)
        self.assertEqual(result["currency_code"], "CAD")
        saved = self.db.save_shopify_sync_snapshot.call_args.kwargs
        self.assertEqual(saved["tenant_id"], 7)
        self.assertEqual(saved["summary"]["forecast_revenue"], Decimal("180"))
        self.assertEqual(len(saved["payload"]["orders"]), 4)
        order_calls = [v for q, v in self.calls if "SyncOrders" in q]
        self.assertEqual(order_calls, [{"cursor": None}, {"cursor": "1"}])
        self.http.post.assert_not_called()

    def test_empty_store_saves_zero_without_forecast_growth(self):
        result = self.service.sync_shopify_store(7)
        self.assertEqual(result["forecast_revenue"], Decimal("0"))
        self.assertIsNone(result["growth_rate"])
        self.assertEqual(result["order_count"], 0)

    def test_disconnected_store_does_not_fetch_or_save(self):
        self.db.get_shopify_connection.return_value = None
        with self.assertRaisesRegex(ValueError, "Connect a Shopify"):
            self.service.sync_shopify_store(7)
        self.service.shopify_graphql.assert_not_called()
        self.db.save_shopify_sync_snapshot.assert_not_called()

    def test_failed_second_page_does_not_persist_partial_revenue(self):
        self.pages = [["30"], ["20"]]
        original = self.graphql

        def fail_second_page(tenant, query, variables=None):
            if "SyncOrders" in query and variables["cursor"] == "1":
                raise ValueError("Simulated Shopify failure")
            return original(tenant, query, variables)

        self.service.shopify_graphql.side_effect = fail_second_page
        with self.assertRaisesRegex(ValueError, "Simulated Shopify"):
            self.service.sync_shopify_store(7)
        self.db.save_shopify_sync_snapshot.assert_not_called()
        self.notifications.dispatch_alert_notifications.assert_not_called()

    def test_repeat_sync_does_not_accumulate_hypothetical_order(self):
        self.pages = [["30", "20", "10", "100"]]
        first = self.service.sync_shopify_store(7)
        self.db.get_latest_shopify_sync_snapshot.return_value = first
        second = self.service.sync_shopify_store(7)
        self.assertEqual(second["forecast_revenue"], Decimal("180"))
        self.assertEqual(second["comparison"]["revenue_delta"], "0")
        self.assertEqual(second["comparison"]["new_orders"], 0)


if __name__ == "__main__":
    unittest.main()
