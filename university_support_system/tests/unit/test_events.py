from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

import pytest

import src.db.events as events_module
from src.db.support_models import Event, EventLink


@pytest.mark.asyncio
async def test_fetch_relevant_events_prefers_upcoming_matches(db_session, monkeypatch):
    older = Event(
        title="Yapay Zeka Semineri",
        summary="Gecen ay yapilan seminer",
        display_summary="Gecen ay yapilan seminer",
        source_url="https://omu.edu.tr/tr/etkinlikler/yapay-zeka-semineri-gecen",
        department="academic_programs",
        starts_at=datetime.now(UTC) - timedelta(days=5),
        is_active=True,
    )
    upcoming = Event(
        title="Yapay Zeka Semineri",
        summary="Gelecek hafta duzenlenecek seminer",
        display_summary="Gelecek hafta duzenlenecek seminer",
        source_url="https://omu.edu.tr/tr/etkinlikler/yapay-zeka-semineri-yeni",
        department="academic_programs",
        starts_at=datetime.now(UTC) + timedelta(days=3),
        is_active=True,
    )
    db_session.add_all([older, upcoming])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(events_module, "get_session", fake_get_session)

    rows = await events_module.fetch_relevant_events(
        "Yapay zeka semineri var mi?",
        department="academic_programs",
        limit=1,
    )

    assert len(rows) == 1
    assert rows[0].source_url == "https://omu.edu.tr/tr/etkinlikler/yapay-zeka-semineri-yeni"


@pytest.mark.asyncio
async def test_fetch_relevant_events_detects_unit_scope_from_query(db_session, monkeypatch):
    faculty_row = Event(
        title="Muhendislik Fakultesi Kariyer Gunleri",
        summary="Fakulte geneli etkinlik",
        display_summary="Fakulte geneli etkinlik",
        source_url="https://omu.edu.tr/tr/etkinlikler/muh-kariyer-gunleri",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        starts_at=datetime.now(UTC) + timedelta(days=5),
        is_active=True,
    )
    unit_row = Event(
        title="Bilgisayar Muhendisligi Hackathon",
        summary="Bolume ozel hackathon etkinligi",
        display_summary="Bolume ozel hackathon etkinligi",
        source_url="https://omu.edu.tr/tr/etkinlikler/bil-muh-hackathon",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        starts_at=datetime.now(UTC) + timedelta(days=3),
        is_active=True,
    )
    db_session.add_all([faculty_row, unit_row])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(events_module, "get_session", fake_get_session)

    rows = await events_module.fetch_relevant_events(
        "Bilgisayar muhendisligindeki etkinlikler neler?",
        department="academic_programs",
        limit=1,
    )

    assert len(rows) == 1
    assert rows[0].title == "Bilgisayar Muhendisligi Hackathon"


@pytest.mark.asyncio
async def test_fetch_relevant_events_unit_scope_excludes_other_faculty_general_rows(db_session, monkeypatch):
    wrong_faculty_general = Event(
        title="Universite Ici Spor Senligi",
        summary="Egitim fakultesinde genel etkinlik",
        display_summary="Egitim fakultesinde genel etkinlik",
        source_url="https://omu.edu.tr/tr/etkinlikler/spor-senligi",
        faculty="Egitim Fakultesi",
        unit_name=None,
        department="academic_programs",
        starts_at=datetime.now(UTC) + timedelta(days=1),
        is_active=True,
    )
    right_faculty_general = Event(
        title="Muhendislik Kariyer Bulusmasi",
        summary="Muhendislik fakultesi genel etkinligi",
        display_summary="Muhendislik fakultesi genel etkinligi",
        source_url="https://omu.edu.tr/tr/etkinlikler/muh-kariyer",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        starts_at=datetime.now(UTC) + timedelta(days=2),
        is_active=True,
    )
    db_session.add_all([wrong_faculty_general, right_faculty_general])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(events_module, "get_session", fake_get_session)

    rows = await events_module.fetch_relevant_events(
        "Bilgisayar muhendisligindeki etkinlikler neler?",
        department="academic_programs",
        limit=3,
    )

    assert all(row.faculty != "Egitim Fakultesi" for row in rows)


@pytest.mark.asyncio
async def test_fetch_relevant_events_includes_event_links(db_session, monkeypatch):
    event = Event(
        title="Kariyer Gunleri",
        summary="Katilim formu ve program duyuruldu",
        display_summary="Katilim formu ve program duyuruldu",
        source_url="https://omu.edu.tr/tr/etkinlikler/kariyer-gunleri",
        department="academic_programs",
        starts_at=datetime.now(UTC) + timedelta(days=2),
        is_active=True,
    )
    db_session.add(event)
    await db_session.flush()
    db_session.add(
        EventLink(
            event_id=event.id,
            label="Program PDF",
            url="https://omu.edu.tr/dosyalar/kariyer-gunleri-program.pdf",
            link_type="attachment",
            sort_order=0,
        )
    )
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(events_module, "get_session", fake_get_session)

    rows = await events_module.fetch_relevant_events(
        "Kariyer gunleri programi var mi?",
        department="academic_programs",
        limit=1,
    )

    assert len(rows) == 1
    assert len(rows[0].links) == 1
    assert rows[0].links[0].label == "Program PDF"


@pytest.mark.asyncio
async def test_fetch_relevant_events_detects_fen_edebiyat_scope_from_query(db_session, monkeypatch):
    fen_row = Event(
        title="Fen Edebiyat Kariyer Gunleri",
        summary="Fen Edebiyat fakultesine ozel etkinlik",
        display_summary="Fen Edebiyat fakultesine ozel etkinlik",
        source_url="https://omu.edu.tr/tr/etkinlikler/fef-kariyer-gunleri",
        faculty="Fen Edebiyat Fakultesi",
        department="academic_programs",
        starts_at=datetime.now(UTC) + timedelta(days=4),
        is_active=True,
    )
    egitim_row = Event(
        title="Egitim Fakultesi Semineri",
        summary="Egitim fakultesi etkinligi",
        display_summary="Egitim fakultesi etkinligi",
        source_url="https://omu.edu.tr/tr/etkinlikler/egitim-seminer",
        faculty="Egitim Fakultesi",
        department="academic_programs",
        starts_at=datetime.now(UTC) + timedelta(days=2),
        is_active=True,
    )
    db_session.add_all([fen_row, egitim_row])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(events_module, "get_session", fake_get_session)

    rows = await events_module.fetch_relevant_events(
        "Fen edebiyattaki etkinlikler neler?",
        limit=3,
    )

    assert len(rows) == 1
    assert rows[0].faculty == "Fen Edebiyat Fakultesi"


@pytest.mark.asyncio
async def test_fetch_relevant_events_applies_this_week_window(db_session, monkeypatch):
    upcoming = Event(
        title="Bu Hafta Semineri",
        summary="Bu hafta duzenlenecek seminer",
        display_summary="Bu hafta duzenlenecek seminer",
        source_url="https://omu.edu.tr/tr/etkinlikler/bu-hafta-seminer",
        department="academic_programs",
        starts_at=datetime(2026, 4, 20, tzinfo=UTC),
        is_active=True,
    )
    old = Event(
        title="Eski Seminer",
        summary="Gecen ay yapilan seminer",
        display_summary="Gecen ay yapilan seminer",
        source_url="https://omu.edu.tr/tr/etkinlikler/eski-seminer",
        department="academic_programs",
        starts_at=datetime(2026, 3, 20, tzinfo=UTC),
        is_active=True,
    )
    missing_date = Event(
        title="Tarihsiz Seminer",
        summary="Tarih bilgisi olmayan seminer",
        display_summary="Tarih bilgisi olmayan seminer",
        source_url="https://omu.edu.tr/tr/etkinlikler/tarihsiz-seminer",
        department="academic_programs",
        starts_at=None,
        is_active=True,
    )
    db_session.add_all([upcoming, old, missing_date])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(events_module, "get_session", fake_get_session)

    rows = await events_module.fetch_relevant_events(
        "Bu hafta seminer var mi?",
        department="academic_programs",
        limit=5,
        now=datetime(2026, 4, 18, tzinfo=UTC),
    )

    assert len(rows) == 1
    assert rows[0].title == "Bu Hafta Semineri"


@pytest.mark.asyncio
async def test_fetch_relevant_events_default_window_excludes_old_and_undated_rows(db_session, monkeypatch):
    upcoming = Event(
        title="Yakin Tarihli Etkinlik",
        summary="Yakin tarihte duzenlenecek etkinlik",
        display_summary="Yakin tarihte duzenlenecek etkinlik",
        source_url="https://omu.edu.tr/tr/etkinlikler/yakin-etkinlik",
        faculty="Fen Edebiyat Fakultesi",
        department="academic_programs",
        starts_at=datetime(2026, 4, 28, tzinfo=UTC),
        is_active=True,
    )
    stale = Event(
        title="Eski Mezuniyet",
        summary="Yillar onceki mezuniyet toreni",
        display_summary="Yillar onceki mezuniyet toreni",
        source_url="https://omu.edu.tr/tr/etkinlikler/eski-mezuniyet",
        faculty="Fen Edebiyat Fakultesi",
        department="academic_programs",
        starts_at=datetime(2017, 6, 1, tzinfo=UTC),
        is_active=True,
    )
    undated = Event(
        title="Tarihsiz Konusma",
        summary="Tarih bilgisi olmayan kayit",
        display_summary="Tarih bilgisi olmayan kayit",
        source_url="https://omu.edu.tr/tr/etkinlikler/tarihsiz-konusma",
        faculty="Fen Edebiyat Fakultesi",
        department="academic_programs",
        starts_at=None,
        is_active=True,
    )
    db_session.add_all([upcoming, stale, undated])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(events_module, "get_session", fake_get_session)

    rows = await events_module.fetch_relevant_events(
        "Fen edebiyattaki etkinlikler neler?",
        now=datetime(2026, 4, 18, tzinfo=UTC),
        limit=5,
    )

    assert len(rows) == 1
    assert rows[0].title == "Yakin Tarihli Etkinlik"
