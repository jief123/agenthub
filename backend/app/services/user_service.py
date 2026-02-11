"""User business logic."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..auth import generate_api_key, hash_api_key, hash_password, verify_password, create_jwt_token
from skills_registry_shared.schemas.user import UserResponse, APIKeyResponse, AuthResponse, PublishStats
from skills_registry_shared.schemas.common import PaginatedResult


def _to_response(u: User) -> UserResponse:
    return UserResponse(
        id=u.id,
        username=u.username,
        display_name=u.display_name,
        email=u.email,
        role=u.role,
        created_at=u.created_at,
    )


async def create(db: AsyncSession, username: str, email: str, role: str = "user") -> UserResponse:
    existing = await db.execute(select(User).where(User.username == username))
    if existing.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=f"Username '{username}' already exists.")

    user = User(username=username, email=email, role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _to_response(user)


async def get_by_id(db: AsyncSession, user_id: int) -> UserResponse | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return _to_response(user) if user else None


async def regenerate_api_key(db: AsyncSession, user_id: int) -> APIKeyResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    key = generate_api_key()
    user.api_key_hash = hash_api_key(key)
    await db.commit()
    return APIKeyResponse(api_key=key)


async def list_users(db: AsyncSession, page: int = 1, size: int = 20) -> PaginatedResult[UserResponse]:
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar() or 0

    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset((page - 1) * size).limit(size)
    )
    items = [_to_response(u) for u in result.scalars().all()]
    pages = (total + size - 1) // size if total > 0 else 0
    return PaginatedResult(items=items, total=total, page=page, size=size, pages=pages)


async def update_role(db: AsyncSession, user_id: int, role: str) -> UserResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    await db.commit()
    await db.refresh(user)
    return _to_response(user)


async def disable(db: AsyncSession, user_id: int) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.is_active = False
        await db.commit()


async def register_with_password(
    db: AsyncSession, username: str, email: str, password: str
) -> AuthResponse:
    from fastapi import HTTPException

    # Check username uniqueness
    existing = await db.execute(select(User).where(User.username == username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Username '{username}' already exists.")

    # Check email uniqueness
    existing_email = await db.execute(select(User).where(User.email == email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Email '{email}' already registered.")

    key = generate_api_key()
    user = User(
        username=username,
        email=email,
        role="user",
        password_hash=hash_password(password),
        api_key_hash=hash_api_key(key),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_jwt_token(user.id)
    return AuthResponse(
        user=_to_response(user),
        api_key=key,
        token=token,
        message="Store your API Key securely — it won't be shown again.",
    )


async def login_with_password(db: AsyncSession, email: str, password: str) -> AuthResponse:
    from fastapi import HTTPException

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Return JWT token for frontend session — API key is NOT touched.
    token = create_jwt_token(user.id)
    return AuthResponse(user=_to_response(user), token=token)


async def get_published_assets(db: AsyncSession, user_id: int) -> dict:
    from ..models.skill import Skill
    from ..models.mcp_server import MCPServer
    from ..models.agent_config import AgentConfig

    skills_result = await db.execute(
        select(Skill).where(Skill.author_id == user_id).order_by(Skill.created_at.desc())
    )
    mcps_result = await db.execute(
        select(MCPServer).where(MCPServer.author_id == user_id).order_by(MCPServer.created_at.desc())
    )
    agents_result = await db.execute(
        select(AgentConfig).where(AgentConfig.author_id == user_id).order_by(AgentConfig.created_at.desc())
    )

    from ..services.skill_service import _to_response as skill_resp
    from ..services.mcp_service import _to_response as mcp_resp
    from ..services.agent_service import _to_response as agent_resp

    return {
        "skills": [skill_resp(s) for s in skills_result.scalars().all()],
        "mcps": [mcp_resp(m) for m in mcps_result.scalars().all()],
        "agents": [agent_resp(a) for a in agents_result.scalars().all()],
    }


async def get_installed_assets(db: AsyncSession, user_id: int) -> list[dict]:
    from ..models.install_log import InstallLog

    result = await db.execute(
        select(InstallLog)
        .where(InstallLog.user_id == user_id)
        .order_by(InstallLog.installed_at.desc())
        .limit(100)
    )
    logs = result.scalars().all()
    return [
        {
            "asset_type": log.asset_type,
            "asset_id": log.asset_id,
            "agent_type": log.agent_type,
            "installed_at": log.installed_at.isoformat(),
        }
        for log in logs
    ]


async def get_publish_stats(db: AsyncSession, user_id: int) -> PublishStats:
    from ..models.skill import Skill
    from ..models.mcp_server import MCPServer
    from ..models.agent_config import AgentConfig

    skill_stats = await db.execute(
        select(func.count(Skill.id), func.coalesce(func.sum(Skill.installs), 0))
        .where(Skill.author_id == user_id)
    )
    s_count, s_installs = skill_stats.one()

    mcp_stats = await db.execute(
        select(func.count(MCPServer.id), func.coalesce(func.sum(MCPServer.installs), 0))
        .where(MCPServer.author_id == user_id)
    )
    m_count, m_installs = mcp_stats.one()

    agent_stats = await db.execute(
        select(func.count(AgentConfig.id), func.coalesce(func.sum(AgentConfig.installs), 0))
        .where(AgentConfig.author_id == user_id)
    )
    a_count, a_installs = agent_stats.one()

    return PublishStats(
        skill_count=s_count,
        mcp_count=m_count,
        agent_count=a_count,
        total_installs=int(s_installs) + int(m_installs) + int(a_installs),
    )
