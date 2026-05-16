from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

import pytest

import src.db.announcements as announcements_module
from src.db.support_models import Announcement, AnnouncementLink


@pytest.mark.asyncio
async def test_supplemental_probe_requires_non_empty_keywords():
    rows = await announcements_module.fetch_relevant_announcements(
        "Son duyurular neler?",
        probe_mode="supplemental",
        require_keyword_match=True,
        allow_latest_fallback=False,
    )

    assert rows == []


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_prefers_exact_faculty_matches(db_session, monkeypatch):
    generic = Announcement(
        title="Genel Duyuru",
        summary="Universite geneli duyuru",
        display_summary="Universite geneli duyuru",
        source_url="https://omu.edu.tr/genel",
        faculty=None,
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    faculty_specific = Announcement(
        title="Fen Fakultesi Duyurusu",
        summary="Fen fakultesine ozel duyuru",
        display_summary="Fen fakultesine ozel duyuru",
        source_url="https://omu.edu.tr/fen",
        faculty="Fen Fakultesi",
        department="academic_programs",
        published_at=datetime.now(UTC) - timedelta(days=1),
        is_active=True,
    )
    db_session.add_all([generic, faculty_specific])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Son duyurular neler?",
        faculty="Fen Fakultesi",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Fen Fakultesi Duyurusu"


@pytest.mark.asyncio
async def test_fetch_announcement_by_source_ref_rejects_stale_hash(db_session, monkeypatch):
    announcement = Announcement(
        title="CAP Basvuru Duyurusu",
        summary="Guncel duyuru ozeti",
        display_summary="Guncel duyuru ozeti",
        source_url="https://omu.edu.tr/cap",
        content_hash="abcdef1234567890",
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add(announcement)
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    stale = await announcements_module.fetch_announcement_by_source_ref(
        f"announcement:{announcement.id}:000000abcdef"
    )
    fresh = await announcements_module.fetch_announcement_by_source_ref(
        f"announcement:{announcement.id}:abcdef123456"
    )

    assert stale is None
    assert fresh is not None
    assert fresh.content_hash == "abcdef1234567890"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_prefers_general_records_for_unscoped_latest_query(
    db_session,
    monkeypatch,
):
    general = Announcement(
        title="Universite Geneli Duyuru",
        summary="Universite geneli duyuru",
        display_summary="Universite geneli duyuru",
        source_url="https://omu.edu.tr/genel",
        faculty=None,
        unit_name=None,
        department=None,
        published_at=datetime.now(UTC) - timedelta(days=1),
        is_active=True,
    )
    faculty_specific = Announcement(
        title="Fen Fakultesi Daha Yeni Haber",
        summary="Fen fakultesine ozel haber",
        display_summary="Fen fakultesine ozel haber",
        source_url="https://fen.omu.edu.tr/tr/haberler/daha-yeni",
        faculty="Fen Fakultesi",
        unit_name=None,
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add_all([general, faculty_specific])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Son duyurular neler?",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Universite Geneli Duyuru"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_falls_back_to_general_when_exact_faculty_missing(
    db_session,
    monkeypatch,
):
    generic = Announcement(
        title="Genel Duyuru",
        summary="Universite geneli duyuru",
        display_summary="Universite geneli duyuru",
        source_url="https://omu.edu.tr/genel",
        faculty=None,
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add(generic)
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Son duyurular neler?",
        faculty="Fen Fakultesi",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Genel Duyuru"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_uses_latest_faculty_items_when_scope_keywords_do_not_match(
    db_session,
    monkeypatch,
):
    faculty_specific = Announcement(
        title="Mezuniyet Töreni Duyurusu",
        summary="Fen fakultesi ogrencileri icin mezuniyet duyurusu",
        display_summary="Fen fakultesi ogrencileri icin mezuniyet duyurusu",
        source_url="https://omu.edu.tr/fen-mezuniyet",
        faculty="Fen Fakultesi",
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add(faculty_specific)
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Fen fakultesindeki son duyurular neler?",
        faculty="Fen Fakultesi",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Mezuniyet Töreni Duyurusu"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_filters_known_noise_links(db_session, monkeypatch):
    announcement = Announcement(
        title="Fen Fakultesi Duyurusu",
        summary="Fen fakultesi duyurusu",
        display_summary="Fen fakultesi duyurusu",
        source_url="https://omu.edu.tr/fen-duyuru",
        faculty="Fen Fakultesi",
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add(announcement)
    await db_session.flush()

    db_session.add_all(
        [
            AnnouncementLink(
                announcement_id=announcement.id,
                label="İş Akış Süreçleri",
                url="https://egitim.omu.edu.tr/home/isakis.pdf",
                link_type="attachment",
                sort_order=0,
            ),
            AnnouncementLink(
                announcement_id=announcement.id,
                label="Sinav Programi",
                url="https://omu.edu.tr/dosyalar/sinav-programi.pdf",
                link_type="attachment",
                sort_order=1,
            ),
        ]
    )
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Fen fakultesindeki son duyurular neler?",
        faculty="Fen Fakultesi",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert len(rows[0].links) == 1
    assert rows[0].links[0].label == "Sinav Programi"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_detects_unit_scope_from_query(db_session, monkeypatch):
    faculty_row = Announcement(
        title="Muhendislik Fakultesi Haberi",
        summary="Fakulte geneli haber",
        display_summary="Fakulte geneli haber",
        source_url="https://omu.edu.tr/muh-fakulte",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    unit_row = Announcement(
        title="Bilgisayar Muhendisligi Duyurusu",
        summary="Bil muh ogrencileri icin duyuru",
        display_summary="Bil muh ogrencileri icin duyuru",
        source_url="https://omu.edu.tr/bil-muh",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=datetime.now(UTC) - timedelta(days=1),
        is_active=True,
    )
    db_session.add_all([faculty_row, unit_row])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Bilgisayar muhendisligindeki son duyurular neler?",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Bilgisayar Muhendisligi Duyurusu"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_detects_new_unit_scope_from_query(db_session, monkeypatch):
    faculty_row = Announcement(
        title="Fen Edebiyat Fakultesi Duyurusu",
        summary="Fakulte geneli duyuru",
        display_summary="Fakulte geneli duyuru",
        source_url="https://omu.edu.tr/fen-edebiyat",
        faculty="Fen Edebiyat Fakultesi",
        unit_name=None,
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    unit_row = Announcement(
        title="Fizik Bolumu Duyurusu",
        summary="Fizik ogrencileri icin duyuru",
        display_summary="Fizik ogrencileri icin duyuru",
        source_url="https://omu.edu.tr/fizik",
        faculty="Fen Edebiyat Fakultesi",
        unit_name="Fizik",
        department="academic_programs",
        published_at=datetime.now(UTC) - timedelta(days=1),
        is_active=True,
    )
    db_session.add_all([faculty_row, unit_row])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Fizik bolumundeki son duyurular neler?",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Fizik Bolumu Duyurusu"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_prefers_stronger_keyword_match_over_newer_noise(
    db_session,
    monkeypatch,
):
    newer_noise = Announcement(
        title="2022-2023 Bahar Yariyili Hesaplamali Bilimler Ders Programi",
        summary="Hesaplamali Bilimler ders programina erismek icin tiklayiniz.",
        display_summary="Hesaplamali Bilimler ders programina erismek icin tiklayiniz.",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/hesaplamali-bilimler-ders-programi",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    exact_match = Announcement(
        title="Bilgisayar Muhendisligi Tek Ders Sinavi Duyurusu",
        summary="Bilgisayar Muhendisligi ogrencileri icin tek ders sinavi programi duyuruldu.",
        display_summary="Bilgisayar Muhendisligi ogrencileri icin tek ders sinavi programi duyuruldu.",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/tek-ders-sinavi",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=datetime.now(UTC) - timedelta(days=20),
        is_active=True,
    )
    db_session.add_all([newer_noise, exact_match])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Bilgisayar muhendisligi tek ders sinavi duyurusu var mi?",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Bilgisayar Muhendisligi Tek Ders Sinavi Duyurusu"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_uses_last_seen_order_when_faculty_items_are_undated(
    db_session,
    monkeypatch,
):
    older_match = Announcement(
        title="2022-2023 Bahar Donemi Ara Sinav Programi",
        summary="Eski ara sinav programi",
        display_summary="Eski ara sinav programi",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/eski-ara-sinav",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=None,
        last_seen_at=datetime.now(UTC) - timedelta(minutes=2),
        is_active=True,
    )
    newer_match = Announcement(
        title="2025-2026 Bahar Yariyili Ara Sinav Programi",
        summary="Yeni ara sinav programi",
        display_summary="Yeni ara sinav programi",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/yeni-ara-sinav",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=None,
        last_seen_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add_all([older_match, newer_match])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Bilgisayar muhendisligi ara sinav programi duyurusu var mi?",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "2025-2026 Bahar Yariyili Ara Sinav Programi"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_matches_turkish_program_titles_with_normalized_query(
    db_session,
    monkeypatch,
):
    older_generic = Announcement(
        title="Lisansustu Sinavi Hakkinda Duyuru",
        summary="Bolumumuz yuksek lisans programi giris sinavi duyurusudur.",
        display_summary="Bolumumuz yuksek lisans programi giris sinavi duyurusudur.",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/lisansustu-sinav",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=None,
        last_seen_at=datetime.now(UTC) - timedelta(minutes=10),
        is_active=True,
    )
    newer_program = Announcement(
        title="2025-2026 Bahar Yariyili Ara Sinav Programi",
        summary="Bilgisayar Muhendisligi icin ara sinav programi yayimlandi.",
        display_summary="Bilgisayar Muhendisligi icin ara sinav programi yayimlandi.",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/yeni-ara-sinav-programi",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=None,
        last_seen_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add_all([older_generic, newer_program])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Bilgisayar muhendisligi icin sinav programi ile ilgili olan var mi?",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "2025-2026 Bahar Yariyili Ara Sinav Programi"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_uses_latest_unit_items_for_scoped_latest_query(
    db_session,
    monkeypatch,
):
    newer_unit = Announcement(
        title="Bolum Semineri Duyurusu",
        summary="Bilgisayar Muhendisligi bolumu icin yeni duyuru",
        display_summary="Bilgisayar Muhendisligi bolumu icin yeni duyuru",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/bolum-semineri",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    older_keyword_heavy = Announcement(
        title="Sayisal Denetim 2 ve Bilgisayarli Goruye Giris Derslerinin Degerlendirmeleri Hakkinda",
        summary="Bilgisayarli kelimesi gecen daha eski kayit",
        display_summary="Bilgisayarli kelimesi gecen daha eski kayit",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/sayisal-denetim",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=datetime.now(UTC) - timedelta(days=400),
        is_active=True,
    )
    db_session.add_all([newer_unit, older_keyword_heavy])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Bilgisayar muhendisligindeki son duyurular neler?",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Bolum Semineri Duyurusu"


@pytest.mark.asyncio
async def test_fetch_relevant_announcements_detects_faculty_scope_from_query_for_latest_requests(
    db_session,
    monkeypatch,
):
    newer_faculty = Announcement(
        title="Muhendislikte Yeni Laboratuvar Acilisi",
        summary="Muhendislik fakultesi icin guncel duyuru",
        display_summary="Muhendislik fakultesi icin guncel duyuru",
        source_url="https://muhendislik.omu.edu.tr/tr/haberler/laboratuvar-acilisi",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    general = Announcement(
        title="Universite Geneli Duyuru",
        summary="Universite geneli duyuru",
        display_summary="Universite geneli duyuru",
        source_url="https://omu.edu.tr/genel",
        faculty=None,
        unit_name=None,
        department=None,
        published_at=datetime.now(UTC) - timedelta(days=1),
        is_active=True,
    )
    db_session.add_all([newer_faculty, general])
    await db_session.flush()

    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)

    rows = await announcements_module.fetch_relevant_announcements(
        "Muhendislik fakultesindeki son duyurular neler?",
        limit=1,
        allow_latest_fallback=True,
    )

    assert len(rows) == 1
    assert rows[0].title == "Muhendislikte Yeni Laboratuvar Acilisi"
