"""Skill ORM model."""

import json
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    _tags: Mapped[str] = mapped_column("tags", Text, default="[]", nullable=False)
    git_url: Mapped[str] = mapped_column(Text, nullable=False)
    git_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    skill_path: Mapped[str] = mapped_column(Text, nullable=False)
    readme_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    readme_html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source: Mapped[str] = mapped_column(String(16), nullable=False, default="internal")
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    installs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    author = relationship("User", lazy="joined")

    @property
    def tags(self) -> list[str]:
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value: list[str]) -> None:
        self._tags = json.dumps(value, ensure_ascii=False)
