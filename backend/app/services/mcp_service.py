"""MCP Server business logic."""

import json
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.mcp_server import MCPServer
from ..models.install_log import InstallLog
from skills_registry_shared.schemas.mcp import MCPServerCreate, MCPServerResponse, MCPInstallConfig
from skills_registry_shared.schemas.user import UserBrief
from skills_registry_shared.schemas.common import PaginatedResult


def _to_response(m: MCPServer) -> MCPServerResponse:
    return MCPServerResponse(
        id=m.id,
        name=m.name,
        description=m.description,
        version=m.version,
        tags=m.tags,
        transport=m.transport,
        config=m.config,
        author=UserBrief(id=m.author.id, username=m.author.username, display_name=m.author.display_name),
        installs=m.installs,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


async def register(db: AsyncSession, data: MCPServerCreate, author_id: int) -> MCPServerResponse:
    existing = await db.execute(select(MCPServer).where(MCPServer.name == data.name))
    if existing.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=f"MCP Server '{data.name}' already exists.")

    config = {
        "command": data.command,
        "args": data.args,
        "env": data.env,
        "autoApprove": data.auto_approve,
    }

    mcp = MCPServer(
        name=data.name,
        description=data.description,
        version=data.version,
        transport=data.transport,
        author_id=author_id,
    )
    mcp.tags = data.tags
    mcp.config = config
    db.add(mcp)
    await db.commit()
    await db.refresh(mcp)
    return _to_response(mcp)


async def get_by_id(db: AsyncSession, mcp_id: int) -> MCPServerResponse | None:
    result = await db.execute(select(MCPServer).where(MCPServer.id == mcp_id))
    mcp = result.scalar_one_or_none()
    return _to_response(mcp) if mcp else None


async def search(
    db: AsyncSession,
    keyword: str | None = None,
    tag: str | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResult[MCPServerResponse]:
    query = select(MCPServer)
    count_query = select(func.count(MCPServer.id))

    if keyword:
        kw = f"%{keyword.lower()}%"
        filt = func.lower(MCPServer.name).like(kw) | func.lower(MCPServer.description).like(kw)
        query = query.where(filt)
        count_query = count_query.where(filt)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(MCPServer.installs.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    mcps = result.scalars().all()

    if tag:
        mcps = [m for m in mcps if tag in m.tags]
        total = len(mcps)

    items = [_to_response(m) for m in mcps]
    pages = (total + size - 1) // size if total > 0 else 0
    return PaginatedResult(items=items, total=total, page=page, size=size, pages=pages)


async def list_top(db: AsyncSession, limit: int = 10) -> list[MCPServerResponse]:
    result = await db.execute(
        select(MCPServer).order_by(MCPServer.installs.desc()).limit(limit)
    )
    return [_to_response(m) for m in result.scalars().all()]


async def get_install_config(db: AsyncSession, mcp_id: int) -> MCPInstallConfig:
    result = await db.execute(select(MCPServer).where(MCPServer.id == mcp_id))
    mcp = result.scalar_one_or_none()
    if not mcp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="MCP Server not found")

    config_snippet = {"mcpServers": {mcp.name: mcp.config}}
    env_vars = list(mcp.config.get("env", {}).keys())

    return MCPInstallConfig(name=mcp.name, config=config_snippet, env_vars_needed=env_vars)


async def record_install(db: AsyncSession, mcp_id: int, user_id: int, agent_type: str = "kiro") -> None:
    result = await db.execute(select(MCPServer).where(MCPServer.id == mcp_id))
    mcp = result.scalar_one_or_none()
    if mcp:
        mcp.installs += 1
        db.add(InstallLog(asset_type="mcp", asset_id=mcp_id, user_id=user_id, agent_type=agent_type))
        await db.commit()


async def delete(db: AsyncSession, mcp_id: int) -> None:
    result = await db.execute(select(MCPServer).where(MCPServer.id == mcp_id))
    mcp = result.scalar_one_or_none()
    if mcp:
        await db.delete(mcp)
        await db.commit()
