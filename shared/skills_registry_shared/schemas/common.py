"""Common schemas shared across all asset types."""

from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class SearchRequest(BaseModel):
    q: str | None = None
    type: str | None = Field(None, pattern=r"^(skill|mcp|agent)$")
    tag: str | None = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
