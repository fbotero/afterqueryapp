from typing import Any, Mapping, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from .config import get_settings


_engine: Optional[AsyncEngine] = None
_session_factory: Optional[sessionmaker] = None


def get_engine() -> AsyncEngine:
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        db_url = settings.database_url
        if not db_url:
            raise ValueError("DATABASE_URL is not set or is empty")
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif not db_url.startswith("postgresql+asyncpg://"):
            if "://" not in db_url:
                raise ValueError(f"Invalid database URL format: {db_url[:20]}...")
        _engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,  
            connect_args={
                "statement_cache_size": 0,
                "server_settings": {
                    "jit": "off"
                }
            }
        )
        _session_factory = sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False)
    return _engine 


def get_session_factory() -> sessionmaker:
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None
    return _session_factory


async def fetch_one(query: str, params: Optional[Mapping[str, Any]] = None) -> Optional[Mapping[str, Any]]:
    async_session = get_session_factory()
    async with async_session() as session:
        result = await session.execute(text(query), params or {})
        query_upper = query.strip().upper()
        is_write = any(
            query_upper.startswith(cmd) 
            for cmd in ("INSERT", "UPDATE", "DELETE")
        )
        if is_write:
            await session.commit()
        row = result.mappings().first()
        return dict(row) if row else None


async def fetch_all(query: str, params: Optional[Mapping[str, Any]] = None) -> Sequence[Mapping[str, Any]]:
    async_session = get_session_factory()
    async with async_session() as session:
        result = await session.execute(text(query), params or {})
        rows = result.mappings().all()
        return [dict(r) for r in rows]


async def execute(query: str, params: Optional[Mapping[str, Any]] = None) -> None:
    async_session = get_session_factory()
    async with async_session() as session:
        await session.execute(text(query), params or {})
        await session.commit()
