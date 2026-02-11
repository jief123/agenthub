"""User-related schemas."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    email: str = Field(..., min_length=1)


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: "UserResponse"
    api_key: str | None = None
    token: str | None = None
    message: str = ""


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str | None = None
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    id: int
    username: str
    display_name: str | None = None

    model_config = {"from_attributes": True}


class APIKeyResponse(BaseModel):
    api_key: str
    message: str = "API Key generated. Store it securely — it won't be shown again."


class PublishStats(BaseModel):
    skill_count: int = 0
    mcp_count: int = 0
    agent_count: int = 0
    total_installs: int = 0
