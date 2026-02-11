"""Application configuration from environment variables."""

import os


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./skills_registry.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ADMIN_API_KEY: str | None = os.getenv("ADMIN_API_KEY")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@localhost.dev")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    SYNC_ENABLED: bool = os.getenv("SYNC_ENABLED", "false").lower() == "true"
    SYNC_INTERVAL: int = int(os.getenv("SYNC_INTERVAL", "86400"))  # default: 1 day
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    GIT_CLONE_TIMEOUT: int = int(os.getenv("GIT_CLONE_TIMEOUT", "60"))
    GIT_MAX_CONCURRENT: int = int(os.getenv("GIT_MAX_CONCURRENT", "5"))


settings = Settings()
