"""Admin API routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_admin
from ..database import get_db
from ..models.user import User
from ..services import user_service, import_service, skill_service, mcp_service, agent_service
from ..models.sync_source import SyncSource
from skills_registry_shared.schemas.user import UserResponse
from skills_registry_shared.schemas.skill import SkillResponse
from skills_registry_shared.schemas.common import PaginatedResult

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class ImportRequest(BaseModel):
    git_url: str


class SyncSourceCreate(BaseModel):
    git_url: str


class RoleUpdate(BaseModel):
    role: str


# --- User Management ---

@router.get("/users", response_model=PaginatedResult[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.list_users(db, page=page, size=size)


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_role(
    user_id: int,
    data: RoleUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.update_role(db, user_id, data.role)


@router.put("/users/{user_id}/disable", status_code=204)
async def disable_user(
    user_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await user_service.disable(db, user_id)


# --- Import ---

@router.post("/import", response_model=list[SkillResponse])
async def import_skills(
    data: ImportRequest,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await import_service.import_from_url(db, data.git_url, admin_id=user.id)


# --- Asset Management ---

@router.get("/assets")
async def list_all_assets(
    type: str | None = Query(None, pattern=r"^(skill|mcp|agent)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all assets across types for admin management."""
    results = {}
    if type is None or type == "skill":
        results["skills"] = await skill_service.search(db, page=page, size=size)
    if type is None or type == "mcp":
        results["mcps"] = await mcp_service.search(db, page=page, size=size)
    if type is None or type == "agent":
        results["agents"] = await agent_service.search(db, page=page, size=size)
    return results


@router.delete("/assets/{asset_type}/{asset_id}", status_code=204)
async def delete_asset(
    asset_type: str,
    asset_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete any asset by type and ID."""
    if asset_type == "skill":
        await skill_service.delete(db, asset_id)
    elif asset_type == "mcp":
        await mcp_service.delete(db, asset_id)
    elif asset_type == "agent":
        await agent_service.delete(db, asset_id)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid asset type: {asset_type}")


# --- Sync Sources ---

@router.get("/sync-sources")
async def list_sync_sources(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SyncSource).where(SyncSource.is_active == True).order_by(SyncSource.created_at.desc())
    )
    sources = result.scalars().all()
    return [
        {
            "id": s.id,
            "git_url": s.git_url,
            "last_synced_at": s.last_synced_at.isoformat() if s.last_synced_at else None,
            "last_commit_hash": s.last_commit_hash,
            "created_at": s.created_at.isoformat(),
        }
        for s in sources
    ]


@router.post("/sync-sources", status_code=201)
async def add_sync_source(
    data: SyncSourceCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    source = SyncSource(git_url=data.git_url, created_by=user.id)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return {"id": source.id, "git_url": source.git_url, "created_at": source.created_at.isoformat()}


@router.delete("/sync-sources/{source_id}", status_code=204)
async def delete_sync_source(
    source_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SyncSource).where(SyncSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Sync source not found")
    source.is_active = False
    await db.commit()


@router.post("/sync-sources/{source_id}/sync")
async def trigger_sync(
    source_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SyncSource).where(SyncSource.id == source_id, SyncSource.is_active == True))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Sync source not found")

    imported = await import_service.import_from_url(db, source.git_url, admin_id=user.id)
    source.last_synced_at = datetime.now(timezone.utc)
    await db.commit()
    return {"synced": len(imported), "git_url": source.git_url}
