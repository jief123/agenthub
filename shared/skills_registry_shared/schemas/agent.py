"""Agent configuration schemas."""

from datetime import datetime
from pydantic import BaseModel, Field

from .user import UserBrief


class EmbeddedSkill(BaseModel):
    name: str
    description: str
    files: dict[str, str]  # relative_path -> file_content


class EmbeddedMCP(BaseModel):
    name: str
    config: dict  # Full MCP server config


class AgentConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., max_length=1024)
    tags: list[str] = Field(default_factory=list, max_length=10)
    prompt: str
    embedded_skills: list[EmbeddedSkill] = Field(default_factory=list)
    embedded_mcps: list[EmbeddedMCP] = Field(default_factory=list)
    git_url: str | None = None
    git_ref: str | None = None
    commit_hash: str | None = None


class AgentConfigResponse(BaseModel):
    id: int
    name: str
    description: str
    tags: list[str]
    prompt: str
    embedded_skills: list[EmbeddedSkill]
    embedded_mcps: list[EmbeddedMCP]
    author: UserBrief
    installs: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentInstallPackage(BaseModel):
    name: str
    prompt: str
    embedded_skills: list[EmbeddedSkill]
    embedded_mcps: list[EmbeddedMCP]
