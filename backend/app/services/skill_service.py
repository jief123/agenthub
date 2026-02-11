"""Skill business logic."""

import json
import markdown
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.skill import Skill
from ..models.install_log import InstallLog
from skills_registry_shared.schemas.skill import SkillCreate, SkillResponse, SkillInstallPackage
from skills_registry_shared.schemas.user import UserBrief
from skills_registry_shared.schemas.common import PaginatedResult
from skills_registry_shared.parsers import parse_skill_md
from . import git_service


def _to_response(s: Skill) -> SkillResponse:
    return SkillResponse(
        id=s.id,
        name=s.name,
        description=s.description,
        version=s.version,
        tags=s.tags,
        git_url=s.git_url,
        git_ref=s.git_ref,
        commit_hash=s.commit_hash,
        skill_path=s.skill_path,
        readme_html=s.readme_html,
        readme_content=s.readme_content,
        author=UserBrief(id=s.author.id, username=s.author.username, display_name=s.author.display_name),
        installs=s.installs,
        source=s.source,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


async def register(db: AsyncSession, data: SkillCreate, author_id: int) -> SkillResponse:
    existing = await db.execute(select(Skill).where(Skill.name == data.name))
    if existing.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=f"Skill '{data.name}' already exists. Use PUT to update.")

    # Parse frontmatter and render only the body (not the YAML frontmatter)
    try:
        meta = parse_skill_md(data.readme_content)
        readme_html = markdown.markdown(meta.body, extensions=["fenced_code", "tables"])
    except Exception:
        # Fallback: render as-is if parsing fails
        readme_html = markdown.markdown(data.readme_content, extensions=["fenced_code", "tables"])

    skill = Skill(
        name=data.name,
        description=data.description,
        version=data.version,
        git_url=data.git_url,
        git_ref=data.git_ref,
        commit_hash=data.commit_hash,
        skill_path=data.skill_path,
        readme_content=data.readme_content,
        readme_html=readme_html,
        source="internal",
        author_id=author_id,
    )
    skill.tags = data.tags
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return _to_response(skill)


async def get_by_id(db: AsyncSession, skill_id: int) -> SkillResponse | None:
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    return _to_response(skill) if skill else None


async def search(
    db: AsyncSession,
    keyword: str | None = None,
    tag: str | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResult[SkillResponse]:
    query = select(Skill)
    count_query = select(func.count(Skill.id))

    if keyword:
        kw = f"%{keyword.lower()}%"
        filt = func.lower(Skill.name).like(kw) | func.lower(Skill.description).like(kw)
        query = query.where(filt)
        count_query = count_query.where(filt)

    # Tag filtering via JSON string — application-level
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Skill.installs.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    skills = result.scalars().all()

    # Filter by tag in application layer if needed
    if tag:
        skills = [s for s in skills if tag in s.tags]
        total = len(skills)

    items = [_to_response(s) for s in skills]
    pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResult(items=items, total=total, page=page, size=size, pages=pages)


async def list_top(db: AsyncSession, limit: int = 10) -> list[SkillResponse]:
    result = await db.execute(
        select(Skill).order_by(Skill.installs.desc()).limit(limit)
    )
    return [_to_response(s) for s in result.scalars().all()]


async def get_install_package(db: AsyncSession, skill_id: int) -> SkillInstallPackage:
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Skill not found")

    # Clone repo and read files
    repo_dir = await git_service.clone_shallow(skill.git_url, skill.git_ref)
    try:
        skill_dir = repo_dir / skill.skill_path
        files: dict[str, str] = {}
        if skill_dir.is_dir():
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = str(f.relative_to(skill_dir))
                    try:
                        files[rel] = f.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        pass  # Skip binary files
    finally:
        git_service.cleanup(repo_dir)

    return SkillInstallPackage(
        name=skill.name,
        git_url=skill.git_url,
        commit_hash=skill.commit_hash,
        skill_path=skill.skill_path,
        files=files,
    )


async def record_install(db: AsyncSession, skill_id: int, user_id: int, agent_type: str = "kiro") -> None:
    # Increment counter
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if skill:
        skill.installs += 1
        db.add(InstallLog(asset_type="skill", asset_id=skill_id, user_id=user_id, agent_type=agent_type))
        await db.commit()


async def delete(db: AsyncSession, skill_id: int) -> None:
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if skill:
        await db.delete(skill)
        await db.commit()
