"""Auth & user routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..services import user_service
from skills_registry_shared.schemas.user import (
    UserCreate, UserRegister, UserLogin, UserResponse, APIKeyResponse, AuthResponse, PublishStats,
)

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.post("/auth/register", response_model=AuthResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await user_service.register_with_password(
        db, username=data.username, email=data.email, password=data.password
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await user_service.login_with_password(db, email=data.email, password=data.password)


@router.post("/auth/api-key", response_model=APIKeyResponse)
async def generate_api_key(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.regenerate_api_key(db, user.id)


@router.get("/users/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    )


@router.get("/users/me/published")
async def get_my_published(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.get_published_assets(db, user.id)


@router.get("/users/me/installed")
async def get_my_installed(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.get_installed_assets(db, user.id)


@router.get("/users/me/stats", response_model=PublishStats)
async def get_my_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.get_publish_stats(db, user.id)


@router.post("/users/me/api-key/regenerate", response_model=APIKeyResponse)
async def regenerate_api_key(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.regenerate_api_key(db, user.id)
