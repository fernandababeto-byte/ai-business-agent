import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json, RealDictCursor

from services.plan_catalog import TRIAL_DAYS


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_password = os.getenv("POSTGRES_PASSWORD")
    if not db_password:
        raise RuntimeError(
            "DATABASE_URL ou POSTGRES_PASSWORD precisa estar definido no ambiente."
        )

    db_user = os.getenv("POSTGRES_USER", "ai_user")
    db_name = os.getenv("POSTGRES_DB", "ai_business_db")
    db_host = os.getenv("POSTGRES_HOST", "db")
    db_port = os.getenv("POSTGRES_PORT", "5432")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_connection():
    return psycopg2.connect(
        get_database_url(),
        cursor_factory=RealDictCursor
    )


def get_connection_with_retry(max_attempts: int = 10, delay_seconds: float = 2):
    last_error = None

    for _ in range(max_attempts):
        try:
            return get_connection()
        except psycopg2.OperationalError as error:
            last_error = error
            time.sleep(delay_seconds)

    raise RuntimeError("Nao foi possivel conectar ao banco de dados.") from last_error


def create_tables():
    with get_connection_with_retry() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    plan TEXT NOT NULL DEFAULT 'revenue_intelligence',
                    trial_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    trial_ends_at TIMESTAMP,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'member',
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS shopify_connections (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER UNIQUE NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    shop_domain TEXT NOT NULL,
                    access_token TEXT,
                    scopes TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    connected_at TIMESTAMP,
                    last_sync_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS shopify_oauth_states (
                    state TEXT PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    shop_domain TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_at TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS shopify_sync_snapshots (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    shop_domain TEXT NOT NULL,
                    currency_code TEXT,
                    order_count INTEGER NOT NULL DEFAULT 0,
                    product_count INTEGER NOT NULL DEFAULT 0,
                    active_product_count INTEGER NOT NULL DEFAULT 0,
                    variant_count INTEGER NOT NULL DEFAULT 0,
                    location_count INTEGER NOT NULL DEFAULT 0,
                    inventory_units INTEGER NOT NULL DEFAULT 0,
                    revenue_total NUMERIC(18, 2) NOT NULL DEFAULT 0,
                    average_order_value NUMERIC(18, 2) NOT NULL DEFAULT 0,
                    growth_rate NUMERIC(10, 2),
                    forecast_revenue NUMERIC(18, 2),
                    risk_score NUMERIC(10, 2),
                    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS revenue_alerts (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    snapshot_id INTEGER REFERENCES shopify_sync_snapshots(id) ON DELETE SET NULL,
                    alert_key TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_value NUMERIC(18, 2),
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    occurrence_count INTEGER NOT NULL DEFAULT 1,
                    UNIQUE (tenant_id, alert_key)
                );
                """
            )
            cursor.execute(
                """
                ALTER TABLE revenue_alerts
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                """
            )
            cursor.execute(
                """
                ALTER TABLE revenue_alerts
                ADD COLUMN IF NOT EXISTS occurrence_count INTEGER NOT NULL DEFAULT 1;
                """
            )
            cursor.execute(
                """
                ALTER TABLE revenue_alerts
                DROP CONSTRAINT IF EXISTS revenue_alerts_tenant_id_snapshot_id_alert_key_key;
                """
            )
            cursor.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_revenue_alerts_active_key
                ON revenue_alerts (tenant_id, alert_key);
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notification_preferences (
                    tenant_id INTEGER PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
                    email_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    email_recipients TEXT NOT NULL DEFAULT '',
                    whatsapp_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    whatsapp_phone TEXT NOT NULL DEFAULT '',
                    whatsapp_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
                    sms_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    sms_phone TEXT NOT NULL DEFAULT '',
                    minimum_severity TEXT NOT NULL DEFAULT 'high',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notification_deliveries (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    alert_id INTEGER NOT NULL REFERENCES revenue_alerts(id) ON DELETE CASCADE,
                    channel TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    status TEXT NOT NULL,
                    provider_message_id TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (alert_id, channel)
                );
                """
            )

            cursor.execute(
                """
                ALTER TABLE chat_history
                ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE;
                """
            )
            cursor.execute(
                """
                ALTER TABLE chat_history
                ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
                """
            )
            cursor.execute(
                """
                ALTER TABLE tenants
                ADD COLUMN IF NOT EXISTS trial_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                """
            )
            cursor.execute(
                """
                ALTER TABLE tenants
                ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMP;
                """
            )
            cursor.execute(
                """
                UPDATE tenants
                SET plan = 'revenue_intelligence'
                WHERE plan = 'trial';
                """
            )
            cursor.execute(
                """
                UPDATE tenants
                SET trial_ends_at = COALESCE(trial_ends_at, created_at + INTERVAL '14 days')
                WHERE trial_ends_at IS NULL;
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_shopify_connections_tenant
                ON shopify_connections (tenant_id);
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_shopify_oauth_states_tenant
                ON shopify_oauth_states (tenant_id);
                """
            )
            cursor.execute(
                """
                ALTER TABLE shopify_sync_snapshots
                ADD COLUMN IF NOT EXISTS average_order_value NUMERIC(18, 2) NOT NULL DEFAULT 0;
                ALTER TABLE shopify_sync_snapshots
                ADD COLUMN IF NOT EXISTS growth_rate NUMERIC(10, 2);
                ALTER TABLE shopify_sync_snapshots
                ADD COLUMN IF NOT EXISTS forecast_revenue NUMERIC(18, 2);
                ALTER TABLE shopify_sync_snapshots
                ADD COLUMN IF NOT EXISTS risk_score NUMERIC(10, 2);
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_shopify_sync_snapshots_tenant
                ON shopify_sync_snapshots (tenant_id, synced_at DESC);
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_revenue_alerts_tenant
                ON revenue_alerts (tenant_id, created_at DESC);
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_notification_deliveries_tenant
                ON notification_deliveries (tenant_id, updated_at DESC);
                """
            )
        connection.commit()


def create_tenant(name: str, slug: str, plan: str = "revenue_intelligence"):
    now = datetime.now(timezone.utc)
    trial_ends_at = now + timedelta(days=TRIAL_DAYS)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tenants (name, slug, plan, trial_started_at, trial_ends_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (slug) DO UPDATE
                SET name = EXCLUDED.name
                RETURNING id, name, slug, plan, trial_started_at, trial_ends_at, is_active;
                """,
                (name, slug, plan, now, trial_ends_at)
            )
            tenant = cursor.fetchone()
        connection.commit()
        return tenant


def get_tenant_by_slug(slug: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, slug, plan, trial_started_at, trial_ends_at, is_active
                FROM tenants
                WHERE slug = %s;
                """,
                (slug,)
            )
            return cursor.fetchone()


def create_user(
    tenant_id: int,
    name: str,
    email: str,
    password_hash: str,
    role: str = "member",
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (tenant_id, name, email, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE
                SET name = EXCLUDED.name,
                    password_hash = EXCLUDED.password_hash,
                    role = EXCLUDED.role,
                    is_active = TRUE
                RETURNING id, tenant_id, name, email, role, is_active;
                """,
                (tenant_id, name, email.lower(), password_hash, role)
            )
            user = cursor.fetchone()
        connection.commit()
        return user


def get_user_by_email(email: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    users.id,
                    users.tenant_id,
                    users.name,
                    users.email,
                    users.password_hash,
                    users.role,
                    users.is_active,
                    tenants.name AS tenant_name,
                    tenants.slug AS tenant_slug,
                    tenants.plan AS tenant_plan,
                    tenants.trial_started_at AS tenant_trial_started_at,
                    tenants.trial_ends_at AS tenant_trial_ends_at,
                    tenants.is_active AS tenant_is_active
                FROM users
                JOIN tenants ON tenants.id = users.tenant_id
                WHERE users.email = %s;
                """,
                (email.lower(),)
            )
            return cursor.fetchone()


def get_user_by_id(user_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    users.id,
                    users.tenant_id,
                    users.name,
                    users.email,
                    users.role,
                    users.is_active,
                    tenants.name AS tenant_name,
                    tenants.slug AS tenant_slug,
                    tenants.plan AS tenant_plan,
                    tenants.trial_started_at AS tenant_trial_started_at,
                    tenants.trial_ends_at AS tenant_trial_ends_at,
                    tenants.is_active AS tenant_is_active
                FROM users
                JOIN tenants ON tenants.id = users.tenant_id
                WHERE users.id = %s;
                """,
                (user_id,)
            )
            return cursor.fetchone()


def save_chat_message(
    question: str,
    answer: str,
    tenant_id: int | None = None,
    user_id: int | None = None,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO chat_history (tenant_id, user_id, question, answer)
                VALUES (%s, %s, %s, %s);
                """,
                (tenant_id, user_id, question, answer)
            )
        connection.commit()


def get_chat_history(tenant_id: int | None = None, limit: int = 10):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if tenant_id is None:
                cursor.execute(
                    """
                    SELECT created_at, question, answer
                    FROM chat_history
                    ORDER BY created_at DESC
                    LIMIT %s;
                    """,
                    (limit,)
                )
            else:
                cursor.execute(
                    """
                    SELECT created_at, question, answer
                    FROM chat_history
                    WHERE tenant_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s;
                    """,
                    (tenant_id, limit)
                )

            return cursor.fetchall()


def save_shopify_oauth_state(
    state: str,
    tenant_id: int,
    user_id: int,
    shop_domain: str,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO shopify_oauth_states (state, tenant_id, user_id, shop_domain)
                VALUES (%s, %s, %s, %s);
                """,
                (state, tenant_id, user_id, shop_domain)
            )
        connection.commit()


def consume_shopify_oauth_state(state: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE shopify_oauth_states
                SET used_at = CURRENT_TIMESTAMP
                WHERE state = %s
                  AND used_at IS NULL
                  AND created_at >= CURRENT_TIMESTAMP - INTERVAL '15 minutes'
                RETURNING state, tenant_id, user_id, shop_domain;
                """,
                (state,)
            )
            row = cursor.fetchone()
        connection.commit()
        return row


def save_shopify_connection(
    tenant_id: int,
    shop_domain: str,
    access_token: str,
    scopes: str,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO shopify_connections (
                    tenant_id,
                    shop_domain,
                    access_token,
                    scopes,
                    status,
                    connected_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, 'connected', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (tenant_id) DO UPDATE
                SET shop_domain = EXCLUDED.shop_domain,
                    access_token = EXCLUDED.access_token,
                    scopes = EXCLUDED.scopes,
                    status = 'connected',
                    connected_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id, tenant_id, shop_domain, scopes, status, connected_at, last_sync_at;
                """,
                (tenant_id, shop_domain, access_token, scopes)
            )
            row = cursor.fetchone()
        connection.commit()
        return row


def get_shopify_connection(tenant_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tenant_id, shop_domain, scopes, status, connected_at, last_sync_at
                FROM shopify_connections
                WHERE tenant_id = %s;
                """,
                (tenant_id,)
            )
            return cursor.fetchone()


def get_shopify_connection_with_token(tenant_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tenant_id, shop_domain, access_token, scopes, status, connected_at, last_sync_at
                FROM shopify_connections
                WHERE tenant_id = %s;
                """,
                (tenant_id,)
            )
            return cursor.fetchone()


def list_connected_shopify_tenants():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT tenant_id, shop_domain, last_sync_at
                FROM shopify_connections
                WHERE status = 'connected'
                ORDER BY tenant_id;
                """
            )
            return cursor.fetchall()


def save_shopify_sync_snapshot(tenant_id: int, shop_domain: str, summary: dict, payload: dict):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO shopify_sync_snapshots (
                    tenant_id,
                    shop_domain,
                    currency_code,
                    order_count,
                    product_count,
                    active_product_count,
                    variant_count,
                    location_count,
                    inventory_units,
                    revenue_total,
                    average_order_value,
                    growth_rate,
                    forecast_revenue,
                    risk_score,
                    payload
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, tenant_id, shop_domain, currency_code, order_count,
                          product_count, active_product_count, variant_count,
                          location_count, inventory_units, revenue_total, average_order_value,
                          growth_rate, forecast_revenue, risk_score, synced_at;
                """,
                (
                    tenant_id,
                    shop_domain,
                    summary["currency_code"],
                    summary["order_count"],
                    summary["product_count"],
                    summary["active_product_count"],
                    summary["variant_count"],
                    summary["location_count"],
                    summary["inventory_units"],
                    summary["revenue_total"],
                    summary["average_order_value"],
                    summary["growth_rate"],
                    summary["forecast_revenue"],
                    summary["risk_score"],
                    Json(payload),
                )
            )
            snapshot = cursor.fetchone()
            cursor.execute(
                """
                UPDATE shopify_connections
                SET last_sync_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE tenant_id = %s;
                """,
                (tenant_id,)
            )
        connection.commit()
        return snapshot


def get_latest_shopify_sync_snapshot(tenant_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tenant_id, shop_domain, currency_code, order_count,
                       product_count, active_product_count, variant_count,
                       location_count, inventory_units, revenue_total, average_order_value,
                       growth_rate, forecast_revenue, risk_score, payload, synced_at
                FROM shopify_sync_snapshots
                WHERE tenant_id = %s
                ORDER BY synced_at DESC, id DESC
                LIMIT 1;
                """,
                (tenant_id,)
            )
            return cursor.fetchone()


def get_recent_shopify_sync_snapshots(tenant_id: int, limit: int = 8):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tenant_id, shop_domain, currency_code, order_count,
                       product_count, active_product_count, variant_count,
                       location_count, inventory_units, revenue_total, average_order_value,
                       growth_rate, forecast_revenue, risk_score, synced_at
                FROM shopify_sync_snapshots
                WHERE tenant_id = %s
                ORDER BY synced_at DESC, id DESC
                LIMIT %s;
                """,
                (tenant_id, limit)
            )
            return cursor.fetchall()


def save_revenue_alerts(tenant_id: int, snapshot_id: int, alerts: list[dict]):
    saved_alerts = []
    active_keys = [alert["alert_key"] for alert in alerts]
    with get_connection() as connection:
        with connection.cursor() as cursor:
            for alert in alerts:
                cursor.execute(
                    """
                    INSERT INTO revenue_alerts (
                        tenant_id,
                        snapshot_id,
                        alert_key,
                        alert_type,
                        severity,
                        title,
                        message,
                        metric_value
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tenant_id, alert_key) DO UPDATE SET
                        snapshot_id = EXCLUDED.snapshot_id,
                        alert_type = EXCLUDED.alert_type,
                        severity = EXCLUDED.severity,
                        title = EXCLUDED.title,
                        message = EXCLUDED.message,
                        metric_value = EXCLUDED.metric_value,
                        status = 'open',
                        updated_at = CURRENT_TIMESTAMP,
                        resolved_at = NULL,
                        occurrence_count = revenue_alerts.occurrence_count + 1
                    RETURNING id, tenant_id, snapshot_id, alert_key, alert_type,
                              severity, title, message, metric_value, status, created_at,
                              updated_at, resolved_at, occurrence_count;
                    """,
                    (
                        tenant_id,
                        snapshot_id,
                        alert["alert_key"],
                        alert["alert_type"],
                        alert["severity"],
                        alert["title"],
                        alert["message"],
                        alert.get("metric_value"),
                    )
                )
                row = cursor.fetchone()
                if row:
                    saved_alerts.append(row)
            if active_keys:
                cursor.execute(
                    """
                    UPDATE revenue_alerts
                    SET status = 'resolved',
                        resolved_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE tenant_id = %s
                      AND status = 'open'
                      AND NOT (alert_key = ANY(%s));
                    """,
                    (tenant_id, active_keys)
                )
            else:
                cursor.execute(
                    """
                    UPDATE revenue_alerts
                    SET status = 'resolved',
                        resolved_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE tenant_id = %s
                      AND status = 'open';
                    """,
                    (tenant_id,)
                )
        connection.commit()
    return saved_alerts


def get_revenue_alerts(tenant_id: int, limit: int = 20):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tenant_id, snapshot_id, alert_key, alert_type,
                       severity, title, message, metric_value, status, created_at,
                       updated_at, resolved_at, occurrence_count
                FROM revenue_alerts
                WHERE tenant_id = %s
                ORDER BY
                    CASE status WHEN 'open' THEN 0 ELSE 1 END,
                    updated_at DESC,
                    id DESC
                LIMIT %s;
                """,
                (tenant_id, limit)
            )
            return cursor.fetchall()


def get_notification_preferences(tenant_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notification_preferences (tenant_id)
                VALUES (%s)
                ON CONFLICT (tenant_id) DO NOTHING;
                """,
                (tenant_id,)
            )
            cursor.execute(
                """
                SELECT tenant_id, email_enabled, email_recipients, whatsapp_enabled,
                       whatsapp_phone, whatsapp_opt_in, sms_enabled, sms_phone,
                       minimum_severity, updated_at
                FROM notification_preferences
                WHERE tenant_id = %s;
                """,
                (tenant_id,)
            )
            preferences = cursor.fetchone()
        connection.commit()
        return preferences


def save_notification_preferences(tenant_id: int, preferences: dict):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notification_preferences (
                    tenant_id, email_enabled, email_recipients, whatsapp_enabled,
                    whatsapp_phone, whatsapp_opt_in, sms_enabled, sms_phone,
                    minimum_severity, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (tenant_id) DO UPDATE SET
                    email_enabled = EXCLUDED.email_enabled,
                    email_recipients = EXCLUDED.email_recipients,
                    whatsapp_enabled = EXCLUDED.whatsapp_enabled,
                    whatsapp_phone = EXCLUDED.whatsapp_phone,
                    whatsapp_opt_in = EXCLUDED.whatsapp_opt_in,
                    sms_enabled = EXCLUDED.sms_enabled,
                    sms_phone = EXCLUDED.sms_phone,
                    minimum_severity = EXCLUDED.minimum_severity,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING tenant_id, email_enabled, email_recipients, whatsapp_enabled,
                          whatsapp_phone, whatsapp_opt_in, sms_enabled, sms_phone,
                          minimum_severity, updated_at;
                """,
                (
                    tenant_id,
                    preferences["email_enabled"],
                    preferences["email_recipients"],
                    preferences["whatsapp_enabled"],
                    preferences["whatsapp_phone"],
                    preferences["whatsapp_opt_in"],
                    preferences["sms_enabled"],
                    preferences["sms_phone"],
                    preferences["minimum_severity"],
                )
            )
            saved_preferences = cursor.fetchone()
        connection.commit()
        return saved_preferences


def upsert_notification_delivery(
    tenant_id: int,
    alert_id: int,
    channel: str,
    destination: str,
    status: str,
    provider_message_id: str | None = None,
    error_message: str | None = None,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notification_deliveries (
                    tenant_id, alert_id, channel, destination, status,
                    provider_message_id, error_message
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (alert_id, channel) DO UPDATE SET
                    destination = EXCLUDED.destination,
                    status = EXCLUDED.status,
                    provider_message_id = EXCLUDED.provider_message_id,
                    error_message = EXCLUDED.error_message,
                    updated_at = CURRENT_TIMESTAMP
                WHERE notification_deliveries.status <> 'sent'
                RETURNING id, tenant_id, alert_id, channel, destination, status,
                          provider_message_id, error_message, created_at, updated_at;
                """,
                (
                    tenant_id,
                    alert_id,
                    channel,
                    destination,
                    status,
                    provider_message_id,
                    error_message,
                )
            )
            delivery = cursor.fetchone()
        connection.commit()
        return delivery


def get_notification_delivery(alert_id: int, channel: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tenant_id, alert_id, channel, destination, status,
                       provider_message_id, error_message, created_at, updated_at
                FROM notification_deliveries
                WHERE alert_id = %s
                  AND channel = %s;
                """,
                (alert_id, channel)
            )
            return cursor.fetchone()


def get_notification_deliveries(tenant_id: int, limit: int = 30):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT notification_deliveries.id, notification_deliveries.alert_id,
                       notification_deliveries.channel, notification_deliveries.destination,
                       notification_deliveries.status,
                       notification_deliveries.provider_message_id,
                       notification_deliveries.error_message,
                       notification_deliveries.created_at,
                       notification_deliveries.updated_at,
                       revenue_alerts.title AS alert_title,
                       revenue_alerts.severity AS alert_severity
                FROM notification_deliveries
                JOIN revenue_alerts ON revenue_alerts.id = notification_deliveries.alert_id
                WHERE notification_deliveries.tenant_id = %s
                ORDER BY notification_deliveries.updated_at DESC
                LIMIT %s;
                """,
                (tenant_id, limit)
            )
            return cursor.fetchall()
