"""Agent Config business logic."""

import json
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.agent_config import AgentConfig
from ..models.install_log import InstallLog
from skills_registry_shared.schemas.agent import (
    AgentConfigCreate, AgentConfigResponse, AgentInstallPackage,
    EmbeddedSkill, EmbeddedMCP,
)
from skills_registry_shared.schemas.user import UserBrief
from skills_registry_shared.schemas.common import PaginatedResult


def _to_response(a: AgentConfig) -> AgentConfigResponse:
    return AgentConfigResponse(
        id=a.id,
        name=a.name,
        description=a.description,
        tags=a.tags,
        prompt=a.prompt,
        embedded_skills=[EmbeddedSkill(**s) for s in a.embedded_skills],
        embedded_mcps=[EmbeddedMCP(**m) for m in a.embedded_mcps],
        author=UserBrief(id=a.author.id, username=a.author.username, display_name=a.author.display_name),
        installs=a.installs,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


async def register(db: AsyncSession, data: AgentConfigCreate, author_id: int) -> AgentConfigResponse:
    existing = await db.execute(select(AgentConfig).where(AgentConfig.name == data.name))
    if existing.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=f"Agent '{data.name}' already exists.")

    agent = AgentConfig(
        name=data.name,
        description=data.description,
        prompt=data.prompt,
        git_url=data.git_url,
        git_ref=data.git_ref,
        commit_hash=data.commit_hash,
        author_id=author_id,
    )
    agent.tags = data.tags
    agent.embedded_skills = [s.model_dump() for s in data.embedded_skills]
    agent.embedded_mcps = [m.model_dump() for m in data.embedded_mcps]
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return _to_response(agent)


async def get_by_id(db: AsyncSession, agent_id: int) -> AgentConfigResponse | None:
    result = await db.execute(select(AgentConfig).where(AgentConfig.id == agent_id))
    agent = result.scalar_one_or_none()
    return _to_response(agent) if agent else None


async def search(
    db: AsyncSession,
    keyword: str | None = None,
    tag: str | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResult[AgentConfigResponse]:
    query = select(AgentConfig)
    count_query = select(func.count(AgentConfig.id))

    if keyword:
        kw = f"%{keyword.lower()}%"
        filt = func.lower(AgentConfig.name).like(kw) | func.lower(AgentConfig.description).like(kw)
        query = query.where(filt)
        count_query = count_query.where(filt)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(AgentConfig.installs.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    agents = result.scalars().all()

    if tag:
        agents = [a for a in agents if tag in a.tags]
        total = len(agents)

    items = [_to_response(a) for a in agents]
    pages = (total + size - 1) // size if total > 0 else 0
    return PaginatedResult(items=items, total=total, page=page, size=size, pages=pages)


async def list_top(db: AsyncSession, limit: int = 10) -> list[AgentConfigResponse]:
    result = await db.execute(
        select(AgentConfig).order_by(AgentConfig.installs.desc()).limit(limit)
    )
    return [_to_response(a) for a in result.scalars().all()]


async def get_install_package(db: AsyncSession, agent_id: int) -> AgentInstallPackage:
    result = await db.execute(select(AgentConfig).where(AgentConfig.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Agent config not found")

    return AgentInstallPackage(
        name=agent.name,
        prompt=agent.prompt,
        embedded_skills=[EmbeddedSkill(**s) for s in agent.embedded_skills],
        embedded_mcps=[EmbeddedMCP(**m) for m in agent.embedded_mcps],
    )


async def record_install(db: AsyncSession, agent_id: int, user_id: int, agent_type: str = "kiro") -> None:
    result = await db.execute(select(AgentConfig).where(AgentConfig.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent:
        agent.installs += 1
        db.add(InstallLog(asset_type="agent", asset_id=agent_id, user_id=user_id, agent_type=agent_type))
        await db.commit()


async def delete(db: AsyncSession, agent_id: int) -> None:
    result = await db.execute(select(AgentConfig).where(AgentConfig.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent:
        await db.delete(agent)
        await db.commit()
