"""Async database engine and session lifecycle helpers."""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import structlog
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings

logger = structlog.get_logger()

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def _sanitized_db_url(url: str) -> str:
    """Return a log-safe database URL without credentials."""
    return url.split("@")[-1]


def _engine_defaults(engine_url: str) -> dict:
    """Build engine options for the current database backend."""
    defaults = {"echo": settings.server.debug}
    if "sqlite" not in str(engine_url):
        defaults.update(
            {
                "pool_size": settings.postgres.pool_size,
                "max_overflow": settings.postgres.max_overflow,
                "pool_timeout": 30,
                "pool_recycle": 1800,
            }
        )
    return defaults


def _schedule_engine_dispose(engine: AsyncEngine) -> None:
    """Best-effort disposal for an old engine during sync re-initialization."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(engine.dispose())


def get_engine() -> AsyncEngine:
    """Return the shared async engine, creating it lazily on first use."""
    global _engine
    if _engine is None:
        engine_url = settings.postgres.async_url
        _engine = create_async_engine(engine_url, **_engine_defaults(engine_url))
        logger.info("db_engine_created", url=_sanitized_db_url(engine_url))
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared async session factory, creating it lazily."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


def init_engine(url: Optional[str] = None, **kwargs) -> AsyncEngine:
    """Reinitialize the shared engine, primarily for tests or overrides."""
    global _engine, _session_factory
    if _engine is not None:
        _schedule_engine_dispose(_engine)

    engine_url = url or settings.postgres.async_url
    defaults = _engine_defaults(engine_url)
    defaults.update(kwargs)

    _engine = create_async_engine(engine_url, **defaults)
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    logger.info("db_engine_initialized", url=_sanitized_db_url(engine_url))
    return _engine


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a managed async session with automatic commit or rollback."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        # Roll back for any application/database exception raised inside the scope.
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_db_health() -> dict:
    """Run a lightweight connectivity check against the active database."""
    start = time.monotonic()
    try:
        async with get_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()

        latency = (time.monotonic() - start) * 1000
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "details": "PostgreSQL baglantisi aktif",
        }
    except (SQLAlchemyError, OSError) as exc:
        latency = (time.monotonic() - start) * 1000
        logger.error("db_health_check_failed", error=str(exc))
        return {
            "status": "unhealthy",
            "latency_ms": round(latency, 2),
            "details": f"Baglanti hatasi: {type(exc).__name__}: {exc}",
        }


async def dispose_engine() -> None:
    """Dispose the shared engine and session factory, typically on shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("db_engine_disposed")
