"""MCP Server configuration schemas."""

from datetime import datetime
from pydantic import BaseModel, Field

from .user import UserBrief


class MCPServerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., max_length=1024)
    version: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)
    transport: str = Field(..., pattern=r"^(stdio|sse|streamable-http)$")
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    auto_approve: list[str] = Field(default_factory=list)


class MCPServerResponse(BaseModel):
    id: int
    name: str
    description: str
    version: str | None = None
    tags: list[str]
    transport: str
    config: dict
    author: UserBrief
    installs: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MCPInstallConfig(BaseModel):
    name: str
    config: dict  # {"mcpServers": {name: {...}}}
    env_vars_needed: list[str]
