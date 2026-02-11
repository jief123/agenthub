"""MCP Server API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user, require_admin
from ..database import get_db
from ..models.user import User
from ..services import mcp_service
from skills_registry_shared.schemas.mcp import MCPServerCreate, MCPServerResponse, MCPInstallConfig
from skills_registry_shared.schemas.common import PaginatedResult

router = APIRouter(prefix="/api/v1/mcps", tags=["mcps"])


@router.get("", response_model=PaginatedResult[MCPServerResponse])
async def list_mcps(
    keyword: str | None = None,
    tag: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await mcp_service.search(db, keyword=keyword, tag=tag, page=page, size=size)


@router.get("/top", response_model=list[MCPServerResponse])
async def top_mcps(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    return await mcp_service.list_top(db, limit=limit)


@router.get("/{mcp_id}", response_model=MCPServerResponse)
async def get_mcp(mcp_id: int, db: AsyncSession = Depends(get_db)):
    mcp = await mcp_service.get_by_id(db, mcp_id)
    if not mcp:
        raise HTTPException(status_code=404, detail="MCP Server not found")
    return mcp


@router.post("", response_model=MCPServerResponse, status_code=201)
async def create_mcp(
    data: MCPServerCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await mcp_service.register(db, data, author_id=user.id)


@router.delete("/{mcp_id}", status_code=204)
async def delete_mcp(
    mcp_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await mcp_service.delete(db, mcp_id)


@router.get("/{mcp_id}/install", response_model=MCPInstallConfig)
async def get_install_config(
    mcp_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await mcp_service.get_install_config(db, mcp_id)


@router.post("/{mcp_id}/install", status_code=204)
async def record_install(
    mcp_id: int,
    agent_type: str = Query("kiro"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await mcp_service.record_install(db, mcp_id, user_id=user.id, agent_type=agent_type)
