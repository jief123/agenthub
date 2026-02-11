"""Skills API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user, require_admin
from ..database import get_db
from ..models.user import User
from ..services import skill_service
from skills_registry_shared.schemas.skill import SkillCreate, SkillResponse, SkillInstallPackage
from skills_registry_shared.schemas.common import PaginatedResult

router = APIRouter(prefix="/api/v1/skills", tags=["skills"])


@router.get("", response_model=PaginatedResult[SkillResponse])
async def list_skills(
    keyword: str | None = None,
    tag: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await skill_service.search(db, keyword=keyword, tag=tag, page=page, size=size)


@router.get("/top", response_model=list[SkillResponse])
async def top_skills(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    return await skill_service.list_top(db, limit=limit)


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int, db: AsyncSession = Depends(get_db)):
    skill = await skill_service.get_by_id(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("", response_model=SkillResponse, status_code=201)
async def create_skill(
    data: SkillCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await skill_service.register(db, data, author_id=user.id)


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(
    skill_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await skill_service.delete(db, skill_id)


@router.get("/{skill_id}/install", response_model=SkillInstallPackage)
async def get_install_package(
    skill_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await skill_service.get_install_package(db, skill_id)


@router.post("/{skill_id}/install", status_code=204)
async def record_install(
    skill_id: int,
    agent_type: str = Query("kiro"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await skill_service.record_install(db, skill_id, user_id=user.id, agent_type=agent_type)
