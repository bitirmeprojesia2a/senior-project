"""
Test Konfigürasyonu ve Fixture'lar

pytest için ortak fixture'lar, mock servisleri ve test veritabanı ayarları.

NOT: pyproject.toml'da asyncio_mode = "auto" ayarı kullanıldığından
     event_loop fixture'ına gerek yoktur. pytest-asyncio 0.21+'da
     event_loop override etmek deprecated'dir.

Kullanım:
    # Fixture'lar testlerde otomatik olarak kullanılabilir:
    async def test_example(db_session, mock_llm_service):
        ...
"""

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.models import Base


# ── Test Veritabanı ─────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """
    Test veritabanı engine'i.
    Her test fonksiyonu için yeni bir SQLite in-memory veritabanı oluşturur.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Test veritabanı oturumu.
    Her test sonrasında otomatik rollback yapar.
    """
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


# ── Mock LLM Service ────────────────────────────
@pytest.fixture
def mock_llm_service():
    """
    Mock LLM servisi.
    Gerçek LLM çağrısı yapmadan test etmek için kullanılır.
    """
    service = MagicMock()
    service.generate = AsyncMock(return_value="Bu bir test yanıtıdır.")
    service.generate_json = AsyncMock(return_value={
        "departments": ["finance"],
        "confidence": 0.9,
        "clarification_needed": False,
    })
    service.is_available = AsyncMock(return_value=True)
    return service


# ── Mock RAG Service ────────────────────────────
@pytest.fixture
def mock_rag_service():
    """
    Mock RAG servisi.
    Gerçek vektör veritabanı araması yapmadan test etmek için kullanılır.
    """
    service = MagicMock()
    service.query = AsyncMock(return_value={
        "answer": "Harç borcu 5000 TL'dir.",
        "sources": [
            {
                "content": "Harç ödemesi her dönem başında yapılmalıdır.",
                "score": 0.85,
                "metadata": {"source": "harc_prosedur.md", "department": "finance"},
            }
        ],
        "department": "finance",
    })
    return service


# ── Mock Redis ──────────────────────────────────
@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    client = MagicMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=True)
    client.lpush = AsyncMock(return_value=1)
    client.rpop = AsyncMock(return_value=None)
    return client


# ── Örnek Test Verileri ─────────────────────────
@pytest.fixture
def sample_student_data():
    """Örnek öğrenci verisi."""
    return {
        "student_id": "20210001",
        "full_name": "Ahmet Yılmaz",
        "email": "ahmet.yilmaz@uni.edu.tr",
        "department": "Bilgisayar Mühendisliği",
        "faculty": "Mühendislik Fakültesi",
        "grade": 3,
        "enrollment_year": 2021,
        "gpa": 3.45,
        "total_credits": 180,
        "completed_credits": 120,
        "current_semester": 6,
    }


@pytest.fixture
def sample_query():
    """Örnek kullanıcı sorgusu."""
    return "Harç borcum ne kadar?"
