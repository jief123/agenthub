"""Skill-related schemas."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from .user import UserBrief


class SkillMetadata(BaseModel):
    """Parsed output from SKILL.md frontmatter."""
    name: str
    description: str
    version: str | None = None
    license: str | None = None
    compatibility: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    body: str = ""  # Markdown content after frontmatter


class SkillCreate(BaseModel):
    name: str = Field(..., pattern=r"^[a-z0-9-]+$", max_length=64)
    description: str = Field(..., max_length=1024)
    version: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)
    git_url: str
    git_ref: str | None = None
    commit_hash: str = Field(..., pattern=r"^[0-9a-f]{40}$")
    skill_path: str
    readme_content: str


class SkillResponse(BaseModel):
    id: int
    name: str
    description: str
    version: str | None = None
    tags: list[str]
    git_url: str
    git_ref: str | None = None
    commit_hash: str
    skill_path: str
    readme_html: str
    readme_content: str = ""
    author: UserBrief
    installs: int
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillInstallPackage(BaseModel):
    name: str
    git_url: str
    commit_hash: str
    skill_path: str
    files: dict[str, str]  # relative_path -> file_content
