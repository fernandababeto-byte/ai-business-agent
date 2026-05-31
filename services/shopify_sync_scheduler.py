import logging
import os
import threading

from database.db import list_connected_shopify_tenants
from services.shopify_service import sync_shopify_store


logger = logging.getLogger(__name__)
_scheduler_started = False
_scheduler_lock = threading.Lock()
_stop_event = threading.Event()


def get_shopify_sync_automation_status():
    return {
        "enabled": os.getenv("SHOPIFY_AUTO_SYNC_ENABLED", "true").lower() == "true",
        "interval_seconds": int(os.getenv("SHOPIFY_AUTO_SYNC_INTERVAL_SECONDS", "900")),
        "initial_delay_seconds": int(os.getenv("SHOPIFY_AUTO_SYNC_INITIAL_DELAY_SECONDS", "5")),
    }


def sync_all_connected_shopify_stores():
    results = []
    for connection in list_connected_shopify_tenants():
        tenant_id = connection["tenant_id"]
        try:
            snapshot = sync_shopify_store(tenant_id)
            results.append(
                {
                    "tenant_id": tenant_id,
                    "shop_domain": connection["shop_domain"],
                    "status": "synced",
                    "snapshot_id": snapshot["id"],
                }
            )
        except Exception as error:
            logger.exception("Automatic Shopify sync failed for tenant %s", tenant_id)
            results.append(
                {
                    "tenant_id": tenant_id,
                    "shop_domain": connection["shop_domain"],
                    "status": "failed",
                    "error": str(error),
                }
            )
    return results


def _scheduler_loop():
    settings = get_shopify_sync_automation_status()
    if _stop_event.wait(settings["initial_delay_seconds"]):
        return

    while not _stop_event.is_set():
        sync_all_connected_shopify_stores()
        if _stop_event.wait(settings["interval_seconds"]):
            return


def start_shopify_sync_scheduler():
    global _scheduler_started
    settings = get_shopify_sync_automation_status()
    if not settings["enabled"]:
        logger.info("Automatic Shopify sync is disabled.")
        return False

    with _scheduler_lock:
        if _scheduler_started:
            return False
        thread = threading.Thread(
            target=_scheduler_loop,
            name="shopify-auto-sync",
            daemon=True,
        )
        thread.start()
        _scheduler_started = True
        logger.info(
            "Automatic Shopify sync started with a %s second interval.",
            settings["interval_seconds"],
        )
        return True
