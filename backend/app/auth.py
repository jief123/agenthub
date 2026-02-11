"""Authentication module — API Key + JWT auth + RBAC."""

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db
from .models.user import User

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24


def hash_api_key(api_key: str) -> str:
    return bcrypt.hashpw(api_key.encode(), bcrypt.gensalt()).decode()


def verify_api_key(api_key: str, hashed: str) -> bool:
    return bcrypt.checkpw(api_key.encode(), hashed.encode())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def generate_api_key() -> str:
    return "sr_" + secrets.token_urlsafe(32)


def create_jwt_token(user_id: int) -> str:
    """Create a short-lived JWT for frontend sessions."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> int | None:
    """Decode JWT and return user_id, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, ValueError):
        return None


async def get_current_user(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Authenticate via API Key header OR Bearer JWT token."""

    # --- Path 1: JWT Bearer token (frontend) ---
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        user_id = decode_jwt_token(token)
        if user_id is not None:
            result = await db.execute(
                select(User).where(User.id == user_id, User.is_active == True)  # noqa: E712
            )
            user = result.scalar_one_or_none()
            if user:
                return user

    # --- Path 2: API Key (CLI / env admin key) ---
    if x_api_key:
        # Check env-based ADMIN_API_KEY first (never overwritten)
        if settings.ADMIN_API_KEY and x_api_key == settings.ADMIN_API_KEY:
            result = await db.execute(
                select(User).where(
                    User.username == settings.ADMIN_USERNAME,
                    User.is_active == True,  # noqa: E712
                )
            )
            admin = result.scalar_one_or_none()
            if admin:
                return admin

        # Check hashed keys in DB
        result = await db.execute(
            select(User).where(User.is_active == True)  # noqa: E712
        )
        users = result.scalars().all()
        for user in users:
            if user.api_key_hash and verify_api_key(x_api_key, user.api_key_hash):
                return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing credentials",
    )


async def get_optional_user(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Optional auth — returns None if no credentials provided."""
    if not x_api_key and not authorization:
        return None
    try:
        return await get_current_user(
            x_api_key=x_api_key, authorization=authorization, db=db
        )
    except HTTPException:
        return None


async def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Require admin role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
