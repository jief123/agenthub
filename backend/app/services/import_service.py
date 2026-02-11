"""External source import service."""

import markdown
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.skill import Skill
from skills_registry_shared.parsers import parse_skill_md
from skills_registry_shared.schemas.skill import SkillResponse
from . import git_service
from .skill_service import _to_response


async def import_from_url(db: AsyncSession, git_url: str, admin_id: int) -> list[SkillResponse]:
    """Import skills from an external git URL."""
    repo_dir = await git_service.clone_shallow(git_url)
    imported = []

    try:
        commit_hash = await git_service.get_commit_hash(repo_dir)
        discovered = await git_service.discover_skills(repo_dir)

        for info in discovered:
            skill_md_path = info["skill_md"]
            skill_path = info["path"]

            try:
                content = open(skill_md_path, encoding="utf-8").read()
                meta = parse_skill_md(content)
            except Exception:
                continue  # Skip unparseable skills

            # Check if already exists
            existing = await db.execute(select(Skill).where(Skill.name == meta.name))
            if existing.scalar_one_or_none():
                continue  # Skip duplicates

            # Render only the body portion (frontmatter already stripped by parser)
            readme_html = markdown.markdown(meta.body, extensions=["fenced_code", "tables"])

            skill = Skill(
                name=meta.name,
                description=meta.description,
                version=meta.version,
                git_url=git_url,
                commit_hash=commit_hash,
                skill_path=skill_path,
                readme_content=content,
                readme_html=readme_html,
                source="external",
                author_id=admin_id,
            )
            tags = meta.metadata.get("tags", [])
            if isinstance(tags, list):
                skill.tags = tags
            else:
                skill.tags = []

            db.add(skill)
            await db.commit()
            await db.refresh(skill)
            imported.append(_to_response(skill))
    finally:
        git_service.cleanup(repo_dir)

    return imported
