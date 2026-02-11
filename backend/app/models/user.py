"""User ORM model."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="user")
    password_hash: Mapped[str | None] = mapped_column(String(256), nullable=True)
    api_key_hash: Mapped[str | None] = mapped_column(String(256), index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
