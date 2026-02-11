"""Unified search API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import skill_service, mcp_service, agent_service

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("")
async def search(
    q: str | None = None,
    type: str | None = Query(None, pattern=r"^(skill|mcp|agent)$"),
    tag: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Cross-asset type search. Returns combined results."""
    results = {}

    if type is None or type == "skill":
        results["skills"] = await skill_service.search(db, keyword=q, tag=tag, page=page, size=size)
    if type is None or type == "mcp":
        results["mcps"] = await mcp_service.search(db, keyword=q, tag=tag, page=page, size=size)
    if type is None or type == "agent":
        results["agents"] = await agent_service.search(db, keyword=q, tag=tag, page=page, size=size)

    return results
