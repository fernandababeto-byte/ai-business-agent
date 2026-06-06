import json
import os
import re

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from agents.agent_router import AgentRouter

from database.db import (
    attach_marketing_lead_trial,
    create_tenant,
    create_tables,
    create_user,
    create_marketing_lead,
    get_marketing_lead,
    get_notification_deliveries,
    get_notification_preferences,
    get_revenue_alerts,
    list_marketing_leads,
    save_notification_preferences,
    save_chat_message,
    get_chat_history,
    update_marketing_lead_status,
)
from services.auth_service import (
    authenticate_user,
    bootstrap_admin_user,
    create_access_token,
    get_current_user_from_token,
    hash_password,
)
from services.billing_service import (
    create_checkout_session,
    get_billing_status,
    list_tenant_commercial_statuses,
    process_paddle_webhook,
)
from services.plan_catalog import PLAN_CATALOG, get_plan
from services.shopify_service import (
    build_install_url,
    complete_oauth_callback,
    get_connection_status,
    shopify_graphql,
    sync_shopify_store,
)
from services.shopify_sync_scheduler import (
    get_shopify_sync_automation_status,
    start_shopify_sync_scheduler,
)


app = FastAPI(
    title="API de Agente de Negócios de IA",
    version="0.1.0",
)

router = AgentRouter()
bearer_scheme = HTTPBearer()


class BusinessQuestion(BaseModel):
    question: str = Field(min_length=1)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class TenantUserCreate(BaseModel):
    tenant_name: str = Field(min_length=2)
    tenant_slug: str = Field(min_length=2)
    name: str = Field(min_length=2)
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    role: str = "owner"


class ShopifyInstallRequest(BaseModel):
    shop: str = Field(min_length=3)


class NotificationPreferencesUpdate(BaseModel):
    email_enabled: bool = False
    email_recipients: str = ""
    whatsapp_enabled: bool = False
    whatsapp_phone: str = ""
    whatsapp_opt_in: bool = False
    sms_enabled: bool = False
    sms_phone: str = ""
    minimum_severity: str = "high"


class BillingCheckoutRequest(BaseModel):
    plan_key: str = Field(min_length=3)


class MarketingLeadCreate(BaseModel):
    email: str = Field(min_length=5)
    store_url: str = ""
    revenue_band: str = ""
    source: str = "landing"


class MarketingLeadStatusUpdate(BaseModel):
    status: str = Field(min_length=3)
    notes: str = ""


class MarketingLeadTrialActivation(BaseModel):
    tenant_name: str = ""
    tenant_slug: str = ""
    owner_name: str = ""
    password: str = Field(min_length=8)
    plan_key: str = "revenue_intelligence"


def slugify(value: str, fallback: str = "revenue-os-client"):
    prepared = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    prepared = prepared.strip("-")
    return prepared or fallback


def lead_display_name(lead: dict):
    store_url = str(lead.get("store_url") or "").strip()
    if store_url:
        domain = store_url.replace("https://", "").replace("http://", "").split("/")[0]
        clean_domain = domain.replace(".myshopify.com", "").replace("-", " ")
        if clean_domain:
            return clean_domain.title()

    email_prefix = str(lead.get("email") or "Shopify Store").split("@")[0]
    return email_prefix.replace(".", " ").replace("_", " ").title()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    try:
        user = get_current_user_from_token(credentials.credentials)
    except Exception as error:
        raise HTTPException(status_code=401, detail="Token invalido.") from error

    if not user:
        raise HTTPException(status_code=401, detail="Usuario inativo ou inexistente.")

    return user


def require_owner(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Permissao insuficiente.")
    return current_user


def require_platform_admin(current_user: dict = Depends(require_owner)):
    platform_admin_email = os.getenv(
        "PLATFORM_ADMIN_EMAIL",
        os.getenv("BOOTSTRAP_ADMIN_EMAIL", ""),
    ).strip().lower()
    if not platform_admin_email or current_user["email"].strip().lower() != platform_admin_email:
        raise HTTPException(
            status_code=403,
            detail="Platform administrator permission required.",
        )
    return current_user


def require_commercial_access(current_user: dict = Depends(get_current_user)):
    billing_status = get_billing_status(current_user["tenant_id"])
    if not billing_status["has_access"]:
        raise HTTPException(
            status_code=402,
            detail="Trial expired. Choose a subscription plan to continue.",
        )
    return current_user


def build_shopify_category_dataframe(snapshot):
    if not snapshot:
        return pd.DataFrame(columns=["setor", "vendas"])

    payload = snapshot.get("payload") or {}
    category_rows = payload.get("category_revenue") or []
    prepared_rows = []
    for row in category_rows:
        category = str(row.get("category") or "").strip() or "Uncategorized"
        try:
            revenue = float(row.get("revenue") or 0)
        except (TypeError, ValueError):
            continue
        if revenue > 0:
            prepared_rows.append({"setor": category, "vendas": revenue})

    if prepared_rows:
        return pd.DataFrame(prepared_rows)

    return pd.DataFrame(
        [
            {
                "setor": "No Shopify sales synced yet",
                "vendas": float(snapshot.get("revenue_total") or 0),
            }
        ]
    )


def load_tenant_dataframe(tenant_id):
    status = get_connection_status(tenant_id)
    if status.get("status") != "connected":
        raise ValueError("Connect Shopify before requesting operational analysis.")

    snapshot = status.get("latest_sync")
    if not snapshot:
        raise ValueError("Run the initial Shopify sync before requesting operational analysis.")

    return build_shopify_category_dataframe(snapshot)


@app.on_event("startup")
def startup_event():
    create_tables()
    bootstrap_admin_user()
    start_shopify_sync_scheduler()


@app.get("/")
def home():
    return {
        "message": "API AI Business Agent online"
    }


@app.post("/auth/login")
def login(data: LoginRequest):
    user = authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos.")

    access_token = create_access_token(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "tenant_id": user["tenant_id"],
            "tenant_name": user["tenant_name"],
            "tenant_slug": user["tenant_slug"],
            "tenant_plan": user["tenant_plan"],
            "tenant_trial_ends_at": user["tenant_trial_ends_at"],
        }
    }


@app.get("/auth/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "tenant_id": current_user["tenant_id"],
        "tenant_name": current_user["tenant_name"],
        "tenant_slug": current_user["tenant_slug"],
        "tenant_plan": current_user["tenant_plan"],
        "tenant_plan_name": get_plan(current_user["tenant_plan"])["name"],
        "tenant_trial_ends_at": current_user["tenant_trial_ends_at"],
    }


@app.get("/plans")
def plans():
    return {
        "trial_days": 14,
        "minimum_price": 99,
        "plans": PLAN_CATALOG,
    }


@app.post("/leads")
def capture_marketing_lead(data: MarketingLeadCreate):
    email = data.email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=422, detail="Provide a valid business email.")

    store_url = data.store_url.strip()
    if store_url and "myshopify.com" not in store_url and "." not in store_url:
        raise HTTPException(status_code=422, detail="Provide a valid Shopify store URL.")

    lead = create_marketing_lead(
        email=email,
        store_url=store_url,
        revenue_band=data.revenue_band,
        source=data.source,
    )
    return {
        "status": "received",
        "message": "Early access request received.",
        "lead": {
            "id": lead["id"],
            "email": lead["email"],
            "status": lead["status"],
        },
    }


@app.get("/leads")
def marketing_leads(
    limit: int = 100,
    current_user: dict = Depends(require_platform_admin),
):
    safe_limit = min(max(limit, 1), 250)
    return {"leads": list_marketing_leads(safe_limit)}


@app.patch("/leads/{lead_id}")
def update_marketing_lead(
    lead_id: int,
    data: MarketingLeadStatusUpdate,
    current_user: dict = Depends(require_platform_admin),
):
    allowed_statuses = {"new", "qualified", "trial_active", "converted", "lost"}
    status = data.status.strip().lower()
    if status not in allowed_statuses:
        raise HTTPException(status_code=422, detail="Unsupported lead status.")

    lead = update_marketing_lead_status(lead_id, status, data.notes)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return {"lead": lead}


@app.post("/leads/{lead_id}/activate-trial")
def activate_marketing_lead_trial(
    lead_id: int,
    data: MarketingLeadTrialActivation,
    current_user: dict = Depends(require_platform_admin),
):
    lead = get_marketing_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    platform_admin_email = os.getenv(
        "PLATFORM_ADMIN_EMAIL",
        os.getenv("BOOTSTRAP_ADMIN_EMAIL", ""),
    ).strip().lower()
    if platform_admin_email and lead["email"].strip().lower() == platform_admin_email:
        raise HTTPException(
            status_code=400,
            detail="Use a customer email, not the platform administrator email.",
        )

    if lead.get("tenant_id") and lead.get("user_id"):
        return {
            "status": "trial_active",
            "message": "Trial workspace already exists for this lead.",
            "lead": lead,
            "login_url": os.getenv("DASHBOARD_URL", ""),
        }

    if data.plan_key not in PLAN_CATALOG:
        raise HTTPException(status_code=422, detail="Unknown plan key.")

    tenant_name = data.tenant_name.strip() or lead_display_name(lead)
    tenant_slug = slugify(data.tenant_slug or tenant_name)
    owner_name = data.owner_name.strip() or lead_display_name(lead)

    try:
        tenant = create_tenant(tenant_name, tenant_slug, plan=data.plan_key)
        user = create_user(
            tenant_id=tenant["id"],
            name=owner_name,
            email=lead["email"],
            password_hash=hash_password(data.password),
            role="owner",
        )
        updated_lead = attach_marketing_lead_trial(
            lead_id=lead["id"],
            tenant_id=tenant["id"],
            user_id=user["id"],
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "status": "trial_active",
        "message": "14-day trial workspace created.",
        "login_url": os.getenv("DASHBOARD_URL", ""),
        "lead": updated_lead,
        "tenant": tenant,
        "user": {
            "id": user["id"],
            "tenant_id": user["tenant_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"],
        },
    }


@app.get("/billing/status")
def billing_status(current_user: dict = Depends(get_current_user)):
    return get_billing_status(current_user["tenant_id"])


@app.post("/billing/checkout")
def billing_checkout(
    data: BillingCheckoutRequest,
    current_user: dict = Depends(require_owner),
):
    try:
        checkout_url = create_checkout_session(
            tenant_id=current_user["tenant_id"],
            email=current_user["email"],
            plan_key=data.plan_key,
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {"checkout_url": checkout_url}


@app.post("/billing/webhook")
async def billing_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("paddle-signature", "")
    try:
        return process_paddle_webhook(payload, signature)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/tenants/commercial")
def tenant_commercial_summary(current_user: dict = Depends(require_platform_admin)):
    return {"tenants": list_tenant_commercial_statuses()}


@app.post("/tenants")
def create_tenant_user(
    data: TenantUserCreate,
    current_user: dict = Depends(require_platform_admin),
):
    tenant = create_tenant(data.tenant_name, data.tenant_slug)
    user = create_user(
        tenant_id=tenant["id"],
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )

    return {
        "tenant": tenant,
        "user": {
            "id": user["id"],
            "tenant_id": user["tenant_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"],
        }
    }


@app.post("/shopify/install")
def shopify_install(
    data: ShopifyInstallRequest,
    current_user: dict = Depends(require_owner),
):
    try:
        install_url = build_install_url(
            shop=data.shop,
            tenant_id=current_user["tenant_id"],
            user_id=current_user["id"],
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "install_url": install_url,
    }


@app.get("/shopify/callback")
def shopify_callback(request: Request):
    try:
        connection = complete_oauth_callback(dict(request.query_params))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8501").rstrip("/")
    dashboard_url = f"{dashboard_url}/?shopify=connected"
    return HTMLResponse(
        f"""
        <html>
            <head>
                <meta name="robots" content="noindex">
                <title>Shopify Connected</title>
            </head>
            <body style="font-family: Inter, Arial, sans-serif; background:#020617; color:#f8fafc; padding:40px;">
                <h1>Shopify connected</h1>
                <p>{connection["shop_domain"]} is now connected to the Revenue Operating System.</p>
                <p>You can return to the dashboard.</p>
                <a href="{dashboard_url}" style="color:#93c5fd;">Open dashboard</a>
            </body>
        </html>
        """
    )


@app.get("/shopify/status")
def shopify_status(current_user: dict = Depends(get_current_user)):
    return get_connection_status(current_user["tenant_id"])


@app.get("/shopify/test")
def shopify_test(current_user: dict = Depends(require_owner)):
    query = """
    query ShopInfo {
      shop {
        name
        myshopifyDomain
        currencyCode
      }
    }
    """
    try:
        return shopify_graphql(current_user["tenant_id"], query)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/shopify/sync")
def shopify_sync(current_user: dict = Depends(require_commercial_access)):
    if current_user["role"] not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Permissao insuficiente.")
    try:
        return sync_shopify_store(current_user["tenant_id"])
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/shopify/sync/automation")
def shopify_sync_automation(current_user: dict = Depends(get_current_user)):
    return get_shopify_sync_automation_status()


@app.get("/alerts")
def revenue_alerts(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    safe_limit = min(max(limit, 1), 100)
    return {
        "alerts": get_revenue_alerts(current_user["tenant_id"], safe_limit),
    }


@app.get("/notifications/preferences")
def notification_preferences(current_user: dict = Depends(get_current_user)):
    return get_notification_preferences(current_user["tenant_id"])


@app.put("/notifications/preferences")
def update_notification_preferences(
    data: NotificationPreferencesUpdate,
    current_user: dict = Depends(require_owner),
):
    minimum_severity = data.minimum_severity.strip().lower()
    if minimum_severity not in {"info", "medium", "high", "critical"}:
        raise HTTPException(status_code=422, detail="Invalid minimum severity.")

    email_recipients = ",".join(
        email.strip().lower()
        for email in data.email_recipients.split(",")
        if email.strip()
    )
    if data.email_enabled and (
        not email_recipients
        or any("@" not in email for email in email_recipients.split(","))
    ):
        raise HTTPException(status_code=422, detail="Provide valid email recipients.")

    whatsapp_phone = data.whatsapp_phone.strip()
    sms_phone = data.sms_phone.strip()
    if data.whatsapp_enabled and not data.whatsapp_opt_in:
        raise HTTPException(status_code=422, detail="WhatsApp requires recipient opt-in.")
    if data.whatsapp_enabled and not whatsapp_phone.startswith("+"):
        raise HTTPException(status_code=422, detail="Use an international WhatsApp number.")
    if data.sms_enabled and not sms_phone.startswith("+"):
        raise HTTPException(status_code=422, detail="Use an international SMS number.")

    return save_notification_preferences(
        current_user["tenant_id"],
        {
            "email_enabled": data.email_enabled,
            "email_recipients": email_recipients,
            "whatsapp_enabled": data.whatsapp_enabled,
            "whatsapp_phone": whatsapp_phone,
            "whatsapp_opt_in": data.whatsapp_opt_in,
            "sms_enabled": data.sms_enabled,
            "sms_phone": sms_phone,
            "minimum_severity": minimum_severity,
        },
    )


@app.get("/notifications/deliveries")
def notification_deliveries(
    limit: int = 30,
    current_user: dict = Depends(get_current_user),
):
    safe_limit = min(max(limit, 1), 100)
    return {
        "deliveries": get_notification_deliveries(current_user["tenant_id"], safe_limit),
    }


def process_question(question: str, current_user: dict):
    question = question.strip()
    if not question:
        raise HTTPException(
            status_code=422,
            detail="A pergunta nao pode estar vazia."
        )

    try:
        dataframe = load_tenant_dataframe(current_user["tenant_id"])

        response = router.route_question(
            question=question,
            dataframe=dataframe
        )

        if isinstance(response, str):
            response_to_save = response
        else:
            response_to_save = json.dumps(
                response,
                ensure_ascii=False,
                default=str
            )

        save_chat_message(
            question=question,
            answer=response_to_save,
            tenant_id=current_user["tenant_id"],
            user_id=current_user["id"],
        )

        return {
            "question": question,
            "response": response
        }

    except Exception as error:
        error_message = f"Erro ao processar pergunta: {str(error)}"

        try:
            save_chat_message(
                question=question,
                answer=error_message,
                tenant_id=current_user["tenant_id"],
                user_id=current_user["id"],
            )
        except Exception:
            pass

        raise HTTPException(status_code=500, detail=error_message) from error


@app.post("/consultar")
def consultar(data: BusinessQuestion, current_user: dict = Depends(require_commercial_access)):
    return process_question(data.question, current_user)


@app.post("/consult")
def consult(data: BusinessQuestion, current_user: dict = Depends(require_commercial_access)):
    return process_question(data.question, current_user)


@app.get("/historia")
def historia(current_user: dict = Depends(get_current_user)):
    history = get_chat_history(tenant_id=current_user["tenant_id"])

    return {
        "history": history
    }


@app.get("/history")
def history(current_user: dict = Depends(get_current_user)):
    history_data = get_chat_history(tenant_id=current_user["tenant_id"])

    return {
        "history": history_data
    }
