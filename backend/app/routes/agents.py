"""Agent Config API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user, require_admin
from ..database import get_db
from ..models.user import User
from ..services import agent_service
from skills_registry_shared.schemas.agent import AgentConfigCreate, AgentConfigResponse, AgentInstallPackage
from skills_registry_shared.schemas.common import PaginatedResult

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("", response_model=PaginatedResult[AgentConfigResponse])
async def list_agents(
    keyword: str | None = None,
    tag: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.search(db, keyword=keyword, tag=tag, page=page, size=size)


@router.get("/top", response_model=list[AgentConfigResponse])
async def top_agents(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.list_top(db, limit=limit)


@router.get("/{agent_id}", response_model=AgentConfigResponse)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    agent = await agent_service.get_by_id(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent config not found")
    return agent


@router.post("", response_model=AgentConfigResponse, status_code=201)
async def create_agent(
    data: AgentConfigCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.register(db, data, author_id=user.id)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await agent_service.delete(db, agent_id)


@router.get("/{agent_id}/install", response_model=AgentInstallPackage)
async def get_install_package(
    agent_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.get_install_package(db, agent_id)


@router.post("/{agent_id}/install", status_code=204)
async def record_install(
    agent_id: int,
    agent_type: str = Query("kiro"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await agent_service.record_install(db, agent_id, user_id=user.id, agent_type=agent_type)
