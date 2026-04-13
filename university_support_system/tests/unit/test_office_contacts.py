"""Office contact helper tests."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.constants import Department
from src.db.models import OfficeContact
import src.db.office_contacts as office_contacts_module
from src.db.office_contacts import fetch_office_contacts, format_office_contact


@pytest.fixture
def office_contact_session_provider(db_engine):
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def _seed():
        async with session_factory() as session:
            session.add_all(
                [
                    OfficeContact(
                        unit_name="Ders Kayit Ofisi",
                        department="student_affairs",
                        person_name="Ayse Kaya",
                        title="Uzman",
                        phone_ext="7304",
                        email="ayse.kaya@omu.edu.tr",
                        related_agents=["registration_agent", "graduation_agent"],
                        is_active=True,
                    ),
                    OfficeContact(
                        unit_name="Mali Isler",
                        department="finance",
                        person_name="Mehmet Demir",
                        title="Memur",
                        phone_ext="7401",
                        email="mehmet.demir@omu.edu.tr",
                        related_agents=["tuition_agent"],
                        is_active=True,
                    ),
                ]
            )
            await session.commit()

    return session_factory, _seed


@pytest.mark.asyncio
async def test_fetch_office_contacts_filters_by_department_and_agent(monkeypatch, office_contact_session_provider):
    session_factory, seed = office_contact_session_provider
    await seed()

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def fake_get_session():
        async with session_factory() as session:
            yield session
            await session.commit()

    monkeypatch.setattr("src.db.office_contacts.get_session", fake_get_session)

    contacts = await fetch_office_contacts(
        department=Department.STUDENT_AFFAIRS,
        agent_id="registration_agent",
    )

    assert len(contacts) == 1
    assert contacts[0].unit_name == "Ders Kayit Ofisi"
    assert contacts[0].related_agents == ["registration_agent", "graduation_agent"]


@pytest.mark.asyncio
async def test_format_office_contact_returns_plain_payload(monkeypatch, office_contact_session_provider):
    session_factory, seed = office_contact_session_provider
    await seed()

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def fake_get_session():
        async with session_factory() as session:
            yield session
            await session.commit()

    monkeypatch.setattr("src.db.office_contacts.get_session", fake_get_session)

    contacts = await fetch_office_contacts(department="finance")
    payload = format_office_contact(contacts[0])

    assert payload["department"] == "finance"
    assert payload["unit_name"] == "Mali Isler"


@pytest.mark.asyncio
async def test_fetch_office_contacts_skips_repeated_missing_table_checks(monkeypatch):
    call_count = 0

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def failing_get_session():
        nonlocal call_count
        call_count += 1
        raise OperationalError("select office_contacts", {}, Exception("missing table"))
        yield

    monkeypatch.setattr("src.db.office_contacts.get_session", failing_get_session)
    monkeypatch.setattr(office_contacts_module, "_office_contacts_table_available", None)
    monkeypatch.setattr(office_contacts_module, "_office_contacts_last_check_at", 0.0)

    monotonic_values = iter([100.0, 120.0])
    monkeypatch.setattr("src.db.office_contacts.monotonic", lambda: next(monotonic_values))

    first = await fetch_office_contacts(department="student_affairs")
    second = await fetch_office_contacts(department="student_affairs")

    assert first == []
    assert second == []
    assert call_count == 1
