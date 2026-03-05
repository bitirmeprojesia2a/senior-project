"""
Connection Modülü Unit Testleri

connection.py'deki lazy initialization, session yönetimi ve
dispose fonksiyonlarının testleri.
"""

import pytest

from src.db.connection import (
    _engine,
    _session_factory,
    dispose_engine,
    get_engine,
    get_session,
    get_session_factory,
    init_engine,
)
from src.db.models import Base


class TestLazyInitialization:
    """Lazy initialization pattern testleri."""

    @pytest.fixture(autouse=True)
    async def reset_engine(self):
        """Her test öncesi engine state'ini sıfırla."""
        import src.db.connection as conn_module
        conn_module._engine = None
        conn_module._session_factory = None
        yield
        # Test sonrası temizlik
        if conn_module._engine is not None:
            await conn_module._engine.dispose()
            conn_module._engine = None
            conn_module._session_factory = None

    def test_engine_starts_none(self):
        """Engine başlangıçta None olmalı."""
        import src.db.connection as conn_module
        assert conn_module._engine is None
        assert conn_module._session_factory is None

    async def test_init_engine_creates_engine(self):
        """init_engine çağrıldığında engine oluşturulur."""
        engine = init_engine("sqlite+aiosqlite:///:memory:", echo=False)
        assert engine is not None

        import src.db.connection as conn_module
        assert conn_module._engine is engine

    async def test_init_engine_creates_session_factory(self):
        """init_engine session factory'yi de oluşturur."""
        init_engine("sqlite+aiosqlite:///:memory:", echo=False)

        import src.db.connection as conn_module
        assert conn_module._session_factory is not None


class TestSessionManagement:
    """Session yönetimi testleri."""

    @pytest.fixture(autouse=True)
    async def setup_test_engine(self):
        """Test için SQLite engine oluştur."""
        engine = init_engine("sqlite+aiosqlite:///:memory:", echo=False)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        await dispose_engine()

    async def test_get_session_returns_session(self):
        """get_session çalışan bir session döndürür."""
        async with get_session() as session:
            assert session is not None
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    async def test_get_session_commits_on_success(self):
        """Başarılı işlemlerde session commit eder."""
        from src.db.models import Student

        async with get_session() as session:
            student = Student(
                student_id="TEST001",
                full_name="Test Kullanıcı",
            )
            session.add(student)

        # Yeni session'da verinin persist edildiğini kontrol et
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Student).where(Student.student_id == "TEST001")
            )
            found = result.scalar_one_or_none()
            assert found is not None
            assert found.full_name == "Test Kullanıcı"

    async def test_get_session_rollbacks_on_error(self):
        """Hata durumunda session rollback yapar."""
        from src.db.models import Student

        with pytest.raises(ValueError):
            async with get_session() as session:
                student = Student(
                    student_id="TEST002",
                    full_name="Hatalı Kullanıcı",
                )
                session.add(student)
                raise ValueError("Test hatası")

        # Rollback sonrası veri kaydedilmemiş olmalı
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Student).where(Student.student_id == "TEST002")
            )
            assert result.scalar_one_or_none() is None


class TestDisposeEngine:
    """Engine dispose testleri."""

    async def test_dispose_clears_state(self):
        """dispose_engine engine ve factory'yi temizler."""
        import src.db.connection as conn_module

        init_engine("sqlite+aiosqlite:///:memory:", echo=False)
        assert conn_module._engine is not None

        await dispose_engine()
        assert conn_module._engine is None
        assert conn_module._session_factory is None

    async def test_dispose_noop_when_no_engine(self):
        """Engine yokken dispose_engine hata vermez."""
        import src.db.connection as conn_module
        conn_module._engine = None
        conn_module._session_factory = None

        await dispose_engine()  # Hata vermemeli
