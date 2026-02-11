"""AgentConfig ORM model."""

import json
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class AgentConfig(Base):
    __tablename__ = "agent_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    _tags: Mapped[str] = mapped_column("tags", Text, default="[]", nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    _embedded_skills: Mapped[str] = mapped_column("embedded_skills", Text, default="[]", nullable=False)
    _embedded_mcps: Mapped[str] = mapped_column("embedded_mcps", Text, default="[]", nullable=False)
    git_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    git_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    commit_hash: Mapped[str | None] = mapped_column(String(40), nullable=True)
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

    @property
    def embedded_skills(self) -> list[dict]:
        return json.loads(self._embedded_skills) if self._embedded_skills else []

    @embedded_skills.setter
    def embedded_skills(self, value: list[dict]) -> None:
        self._embedded_skills = json.dumps(value, ensure_ascii=False)

    @property
    def embedded_mcps(self) -> list[dict]:
        return json.loads(self._embedded_mcps) if self._embedded_mcps else []

    @embedded_mcps.setter
    def embedded_mcps(self, value: list[dict]) -> None:
        self._embedded_mcps = json.dumps(value, ensure_ascii=False)
