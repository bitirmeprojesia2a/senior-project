"""
Veritabanı Bağlantı Yönetimi

Async SQLAlchemy engine ve session factory.
Bağlantı havuzu, transaction yönetimi ve health check sağlar.

Lazy initialization pattern: Engine, ilk kullanımda oluşturulur.
Bu sayede import sırasında veritabanı bağlantısı denenmez
ve testlerde kolayca mock'lanabilir.

Kullanım:
    from src.db.connection import get_session, check_db_health

    async with get_session() as session:
        result = await session.execute(query)
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
import structlog

from src.core.config import settings

logger = structlog.get_logger()

# ── Lazy Engine ─────────────────────────────────
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """
    Veritabanı engine'ini döndürür. İlk çağrıda oluşturur (lazy init).

    Bu pattern, modül import edildiğinde DB bağlantısı kurulmasını
    engeller. Testlerde engine'i override etmek için
    `init_engine()` kullanılabilir.
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.postgres.async_url,
            pool_size=settings.postgres.pool_size,
            max_overflow=settings.postgres.max_overflow,
            pool_timeout=30,
            pool_recycle=1800,
            echo=settings.server.debug,
        )
        logger.info(
            "db_engine_created",
            url=settings.postgres.async_url.split("@")[-1],  # Şifreyi loglamadan
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Session factory'yi döndürür. İlk çağrıda oluşturur."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


def init_engine(url: Optional[str] = None, **kwargs) -> AsyncEngine:
    """
    Engine'i belirtilen URL ile (yeniden) oluşturur.

    Testlerde farklı bir veritabanı kullanmak için:
        init_engine("sqlite+aiosqlite:///:memory:")

    Args:
        url: Veritabanı bağlantı URL'si. None ise config'den okunur.
        **kwargs: SQLAlchemy create_async_engine parametreleri.
    """
    global _engine, _session_factory
    if _engine is not None:
        # Mevcut engine'i kapat (senkron context'te çağrılmamalı)
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_engine.dispose())
        except RuntimeError:
            pass

    engine_url = url or settings.postgres.async_url
    defaults = {
        "echo": settings.server.debug,
    }
    # Pool parametreleri sadece PostgreSQL için geçerli
    # SQLite StaticPool kullandığı için bu parametreleri kabul etmez
    if "sqlite" not in str(engine_url):
        defaults.update({
            "pool_size": 10,
            "max_overflow": 5,
            "pool_timeout": 30,
            "pool_recycle": 1800,
        })
    defaults.update(kwargs)

    _engine = create_async_engine(engine_url, **defaults)
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    logger.info("db_engine_initialized", url=engine_url.split("@")[-1])
    return _engine


# ── Session Context Manager ─────────────────────
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async veritabanı oturumu sağlar.

    Context manager ile kullanılır, otomatik commit/rollback yapar.

    Kullanım:
        async with get_session() as session:
            result = await session.execute(query)
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# ── Health Check ─────────────────────────────────
async def check_db_health() -> dict:
    """
    Veritabanı sağlık kontrolü yapar.

    Returns:
        {
            "status": "healthy" | "unhealthy",
            "latency_ms": float,
            "details": str
        }
    """
    import time

    start = time.monotonic()
    try:
        async with get_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()

        latency = (time.monotonic() - start) * 1000

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "details": "PostgreSQL bağlantısı aktif",
        }
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        logger.error("db_health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "latency_ms": round(latency, 2),
            "details": f"Bağlantı hatası: {type(e).__name__}: {e}",
        }


# ── Engine Lifecycle ─────────────────────────────
async def dispose_engine() -> None:
    """Engine'i kapatır. Uygulama kapanışında çağrılmalıdır."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("db_engine_disposed")
