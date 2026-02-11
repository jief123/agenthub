"""InstallLog ORM model."""

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class InstallLog(Base):
    __tablename__ = "install_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_type: Mapped[str] = mapped_column(String(16), nullable=False)  # skill | mcp | agent
    asset_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(32), nullable=False, default="kiro")
    installed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (
        Index("ix_install_logs_asset", "asset_type", "asset_id"),
    )
