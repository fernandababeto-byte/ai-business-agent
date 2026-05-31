import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import jwt
from dotenv import load_dotenv

from database.db import (
    create_tenant,
    create_user,
    get_user_by_email,
    get_user_by_id,
)


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


def get_auth_secret():
    secret = os.getenv("JWT_SECRET_KEY") or os.getenv("DASHBOARD_COOKIE_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY precisa estar definido no ambiente.")
    return secret


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


def create_access_token(user: dict) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user["id"]),
        "tenant_id": user["tenant_id"],
        "email": user["email"],
        "role": user["role"],
        "exp": expires_at,
    }
    return jwt.encode(payload, get_auth_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, get_auth_secret(), algorithms=[JWT_ALGORITHM])


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None

    if not user["is_active"] or not user["tenant_is_active"]:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user


def bootstrap_admin_user():
    tenant_name = os.getenv("BOOTSTRAP_TENANT_NAME", "My Shopify Store")
    tenant_slug = os.getenv("BOOTSTRAP_TENANT_SLUG", "my-shopify-store")
    admin_name = os.getenv("BOOTSTRAP_ADMIN_NAME", os.getenv("DASHBOARD_NAME", "Administrator"))
    admin_email = os.getenv("BOOTSTRAP_ADMIN_EMAIL") or os.getenv("DASHBOARD_USERNAME")
    admin_password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD") or os.getenv("DASHBOARD_PASSWORD")
    admin_password_hash = os.getenv("BOOTSTRAP_ADMIN_PASSWORD_HASH") or os.getenv(
        "DASHBOARD_PASSWORD_HASH"
    )

    if not admin_email or not (admin_password or admin_password_hash):
        return None

    existing_user = get_user_by_email(admin_email)
    if existing_user:
        return existing_user

    tenant = create_tenant(tenant_name, tenant_slug, plan="revenue_intelligence")
    password_hash = admin_password_hash or hash_password(admin_password)

    return create_user(
        tenant_id=tenant["id"],
        name=admin_name,
        email=admin_email,
        password_hash=password_hash,
        role="owner",
    )


def get_current_user_from_token(token: str):
    payload = decode_access_token(token)
    user_id = int(payload["sub"])
    user = get_user_by_id(user_id)

    if not user or not user["is_active"] or not user["tenant_is_active"]:
        return None

    return user
