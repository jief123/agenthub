"""FastAPI application entry point."""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select

from .config import settings
from .database import engine, Base, async_session
from .models import *  # noqa: F401,F403 — ensure all models are registered
from .models.user import User
from .models.sync_source import SyncSource
from .auth import generate_api_key, hash_api_key, hash_password
from .services import import_service
from .routes import skills, mcps, agents, auth_routes, admin, search

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


async def init_db():
    """Create tables (for SQLite dev mode). Production uses Alembic."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_admin():
    """Create initial admin user if ADMIN_API_KEY is set and user doesn't exist."""
    if not settings.ADMIN_API_KEY:
        return

    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == settings.ADMIN_USERNAME))
        if result.scalar_one_or_none():
            return

        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            role="admin",
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            api_key_hash=hash_api_key(settings.ADMIN_API_KEY),
        )
        db.add(admin)
        await db.commit()
        logger.info(f"Admin user '{settings.ADMIN_USERNAME}' created.")


async def sync_sources_loop():
    """Background task: sync all active sync sources on SYNC_INTERVAL."""
    while True:
        await asyncio.sleep(settings.SYNC_INTERVAL)
        logger.info("Background sync: starting...")
        async with async_session() as db:
            result = await db.execute(
                select(SyncSource).where(SyncSource.is_active == True)  # noqa: E712
            )
            sources = result.scalars().all()
            # Find admin user for author_id
            admin_result = await db.execute(select(User).where(User.role == "admin"))
            admin_user = admin_result.scalar_one_or_none()
            if not admin_user:
                logger.warning("Background sync: no admin user found, skipping.")
                continue

            for source in sources:
                try:
                    imported = await import_service.import_from_url(db, source.git_url, admin_id=admin_user.id)
                    source.last_synced_at = datetime.now(timezone.utc)
                    await db.commit()
                    logger.info(f"Synced '{source.git_url}': {len(imported)} new assets.")
                except Exception as e:
                    logger.error(f"Sync failed for '{source.git_url}': {e}")
        logger.info("Background sync: done.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_admin()
    sync_task = None
    if settings.SYNC_ENABLED:
        sync_task = asyncio.create_task(sync_sources_loop())
        logger.info(f"Background sync enabled (interval: {settings.SYNC_INTERVAL}s).")
    logger.info("Skills Registry started.")
    yield
    if sync_task:
        sync_task.cancel()
    logger.info("Skills Registry shutting down.")


app = FastAPI(
    title="AgentHub",
    description="AI Agent Skills Registry and Distribution Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# API routes
app.include_router(skills.router)
app.include_router(mcps.router)
app.include_router(agents.router)
app.include_router(auth_routes.router)
app.include_router(admin.router)
app.include_router(search.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve React static files (production)
import os
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
logger.info(f"Static dir: {static_dir}, exists: {os.path.isdir(static_dir)}")
if os.path.isdir(static_dir):
    # Mount assets if the directory exists
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_index():
        """Serve React SPA index."""
        return FileResponse(os.path.join(static_dir, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA — all non-API routes return index.html."""
        # Try to serve static file first
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fallback to index.html for SPA routing
        index = os.path.join(static_dir, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"detail": "Frontend not built yet."}
