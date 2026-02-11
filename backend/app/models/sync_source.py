"""SyncSource ORM model."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class SyncSource(Base):
    __tablename__ = "sync_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    git_url: Mapped[str] = mapped_column(Text, nullable=False)
    sync_interval: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_commit_hash: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
