"""Event sync helper tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.agents.event.sync import (
    EventReference,
    EventSourceSyncResult,
    build_event_candidate_from_reference,
    extract_event_references_from_html,
    sync_event_source,
)
from src.db.event_sources import EventSourceRecord


def test_extract_event_references_from_html_keeps_only_event_links():
    html = """
    <html>
      <body>
        <a href="/tr/iletisim">Iletisim</a>
        <a href="/tr/etkinlikler/yapay-zeka-zirvesi">Yapay Zeka Zirvesi 2026</a>
        <a href="/tr/haberler/bilim-senligi">Bilim Senligi Haberi</a>
      </body>
    </html>
    """

    references = extract_event_references_from_html(
        html,
        base_url="https://www.omu.edu.tr",
        max_items=10,
    )

    assert [item.source_url for item in references] == [
        "https://www.omu.edu.tr/tr/etkinlikler/yapay-zeka-zirvesi"
    ]


def test_extract_event_references_from_html_enriches_listing_time_and_location():
    html = """
    <html>
      <body>
        <div>Eki 31</div>
        <a href="/tr/etkinlikler/ozdemir-bayraktar">2024 Ozdemir Bayraktar Burs Programi Bilgilendirme Toplantisi</a>
        <div>15:00</div>
        <div>Muhendislik Fakultesi Konferans Salonu</div>
      </body>
    </html>
    """

    references = extract_event_references_from_html(
        html,
        base_url="https://muhendislik.omu.edu.tr",
        max_items=10,
    )

    assert len(references) == 1
    assert references[0].date_hint == "Eki 31"
    assert references[0].time_hint == "15:00"
    assert references[0].location == "Muhendislik Fakultesi Konferans Salonu"


def test_extract_event_references_from_html_handles_inline_time_and_location():
    html = """
    <html>
      <body>
        <a href="/tr/etkinlikler/teknofest">Teknofest Karadeniz</a>
        <div>09:00 Samsun Uluslararasi Carsamba Havalimani</div>
      </body>
    </html>
    """

    references = extract_event_references_from_html(
        html,
        base_url="https://bil-muhendislik.omu.edu.tr",
        max_items=10,
    )

    assert len(references) == 1
    assert references[0].time_hint == "09:00"
    assert references[0].location == "Samsun Uluslararasi Carsamba Havalimani"


def test_build_event_candidate_from_reference_extracts_datetime_location_and_type():
    source = EventSourceRecord(
        id=1,
        name="OMU Etkinlikler",
        source_type="html_list",
        parser_key="generic_html",
        base_url="https://www.omu.edu.tr",
        list_url="https://www.omu.edu.tr/tr/etkinlikler",
        faculty=None,
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=20,
        parser_options={},
        is_active=True,
        last_success_at=None,
        last_error=None,
    )
    reference = EventReference(
        title="Yapay Zeka Zirvesi 2026",
        source_url="https://www.omu.edu.tr/tr/etkinlikler/yapay-zeka-zirvesi",
    )
    detail_html = """
    <html>
      <body>
        <h1>Yapay Zeka Zirvesi 2026</h1>
        <p>Tarih: 20 Nisan 2026 10:30</p>
        <p>Yer: Ataturk Kongre Merkezi</p>
        <p>Duzenleyen: OMU Kariyer Merkezi</p>
        <p>Akademi ve sanayi temsilcileri zirve kapsaminda bir araya gelecek.</p>
      </body>
    </html>
    """

    candidate = build_event_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty=None,
    )

    assert candidate.starts_at == datetime(2026, 4, 20, 10, 30, tzinfo=UTC)
    assert candidate.location == "Ataturk Kongre Merkezi"
    assert candidate.organizer == "OMU Kariyer Merkezi"
    assert candidate.event_type == "zirve"
    assert candidate.department == "academic_programs"


def test_build_event_candidate_from_reference_uses_listing_and_publication_fallback_for_low_quality_detail():
    source = EventSourceRecord(
        id=1,
        name="OMU Muhendislik Etkinlikler",
        source_type="html_list",
        parser_key="omu_faculty_home_events",
        base_url="https://muhendislik.omu.edu.tr",
        list_url="https://muhendislik.omu.edu.tr/tr/etkinlikler",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=20,
        parser_options={},
        is_active=True,
        last_success_at=None,
        last_error=None,
    )
    reference = EventReference(
        title="2024 Ozdemir Bayraktar Burs Programi Bilgilendirme Toplantisi",
        source_url="https://muhendislik.omu.edu.tr/tr/etkinlikler/ozdemir-bayraktar",
        date_hint="Eki 31",
        time_hint="15:00",
        location="Muhendislik Fakultesi Konferans Salonu",
    )
    detail_html = """
    <html>
      <body>
        <h1>2024 Ozdemir Bayraktar Burs Programi Bilgilendirme Toplantisi</h1>
        <div>Yazar: meryem | Tarih: 31 Ekim 2023</div>
        <div>Toggle navigation</div>
        <div>Hizli Linkler</div>
        <div>Copyright</div>
      </body>
    </html>
    """

    candidate = build_event_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty="Muhendislik Fakultesi",
    )

    assert candidate.starts_at == datetime(2023, 10, 31, 15, 0, tzinfo=UTC)
    assert candidate.location == "Muhendislik Fakultesi Konferans Salonu"
    assert candidate.summary == (
        "2024 Ozdemir Bayraktar Burs Programi Bilgilendirme Toplantisi. Tarih: 31.10.2023 15:00. Konum: Muhendislik Fakultesi Konferans Salonu"
    )
    assert "Toggle navigation" not in (candidate.original_text or "")


def test_build_event_candidate_from_reference_for_omu_faculty_source_trims_shell_and_keeps_single_event_date():
    source = EventSourceRecord(
        id=1,
        name="OMU Muhendislik Etkinlikler",
        source_type="html_list",
        parser_key="generic_html",
        base_url="https://muhendislik.omu.edu.tr",
        list_url="https://muhendislik.omu.edu.tr/tr/etkinlikler",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=20,
        parser_options={},
        is_active=True,
        last_success_at=None,
        last_error=None,
    )
    reference = EventReference(
        title="TUBITAK 2244,2209-A ve 2209-B Programlari Bilgilendirme Gunu",
        source_url="https://muhendislik.omu.edu.tr/tr/etkinlikler/tubitak-bilgilendirme",
    )
    detail_html = """
    <html>
      <body>
        <div>MUHENDISLIK FAKULTESI</div>
        <div>Anasayfa</div>
        <h1>TUBITAK 2244,2209-A ve 2209-B Programlari Bilgilendirme Gunu</h1>
        <div>TUBITAK 2244,2209-A ve 2209-B Programlari Bilgilendirme Gunu</div>
        <p>Degerli Akademisyenlerimiz ve Kiymetli Ogrencilerimiz,</p>
        <p>Universitemiz Teknoloji Transfer Ofisi tarafindan 31 Ekim 2023 Sali gunu saat 13:30'da Muhendislik Fakultesi Konferans Salonunda bilgilendirme toplantisi yapilacaktir.</p>
        <p>Muhendislik Fakultesi Dekanligi</p>
        <div>Etkinlikler</div>
        <div>Copyright</div>
      </body>
    </html>
    """

    candidate = build_event_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty="Muhendislik Fakultesi",
    )

    assert "Anasayfa" not in (candidate.original_text or "")
    assert "Degerli Akademisyenlerimiz" not in (candidate.original_text or "")
    assert candidate.summary == (
        "Universitemiz Teknoloji Transfer Ofisi tarafindan 31 Ekim 2023 Sali gunu saat 13:30'da Muhendislik Fakultesi Konferans Salonunda bilgilendirme toplantisi yapilacaktir. Konum: Muhendislik Fakultesi Konferans Salonu"
    )
    assert candidate.starts_at == datetime(2023, 10, 31, 13, 30, tzinfo=UTC)
    assert candidate.ends_at is None
    assert candidate.location == "Muhendislik Fakultesi Konferans Salonu"
    assert candidate.organizer == "Universitemiz Teknoloji Transfer Ofisi"
    assert candidate.event_type == "bilgilendirme"


def test_build_event_candidate_from_reference_rejects_historical_date_when_publication_date_exists():
    source = EventSourceRecord(
        id=1,
        name="OMU Muhendislik Etkinlikler",
        source_type="html_list",
        parser_key="omu_faculty_home_events",
        base_url="https://muhendislik.omu.edu.tr",
        list_url="https://muhendislik.omu.edu.tr/tr/etkinlikler",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=20,
        parser_options={},
        is_active=True,
        last_success_at=None,
        last_error=None,
    )
    reference = EventReference(
        title="OMU 47. Yasini Kutluyor",
        source_url="https://muhendislik.omu.edu.tr/tr/etkinlikler/omu-47-yasini-kutluyor",
    )
    detail_html = """
    <html>
      <body>
        <h1>OMU 47. Yasini Kutluyor</h1>
        <div>Yazar: editor | Tarih: 1 Nisan 2022</div>
        <p>Adini bagimsizlik mucadelesinin basladigi gun olan 19 Mayis 1919'dan alan universitemizin 47. kurulus yil donumunu kutluyoruz.</p>
      </body>
    </html>
    """

    candidate = build_event_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty="Muhendislik Fakultesi",
    )

    assert candidate.starts_at == datetime(2022, 4, 1, 0, 0, tzinfo=UTC)


def test_build_event_candidate_from_reference_prefers_title_specific_type_over_body_location_words():
    source = EventSourceRecord(
        id=1,
        name="OMU Muhendislik Etkinlikler",
        source_type="html_list",
        parser_key="omu_faculty_home_events",
        base_url="https://muhendislik.omu.edu.tr",
        list_url="https://muhendislik.omu.edu.tr/tr/etkinlikler",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=20,
        parser_options={},
        is_active=True,
        last_success_at=None,
        last_error=None,
    )
    reference = EventReference(
        title="Turk Sanat Muzigi Konseri",
        source_url="https://muhendislik.omu.edu.tr/tr/etkinlikler/konser",
    )
    detail_html = """
    <html>
      <body>
        <h1>Turk Sanat Muzigi Konseri</h1>
        <p>7 Haziran 2022 tarihinde Muhendislik Fakultesi Konferans Salonunda gerceklestirilecektir.</p>
      </body>
    </html>
    """

    candidate = build_event_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty="Muhendislik Fakultesi",
    )

    assert candidate.event_type == "konser"


class _FakeEventHTTPClient:
    def __init__(self, responses: dict[str, str]) -> None:
        self.responses = responses
        self.requested_urls: list[str] = []

    async def get_text(self, url: str) -> str:
        self.requested_urls.append(url)
        return self.responses[url]


@pytest.mark.asyncio
async def test_sync_event_source_dry_run_estimates_counts():
    source = EventSourceRecord(
        id=0,
        name="OMU Etkinlikler",
        source_type="html_list",
        parser_key="generic_html",
        base_url="https://www.omu.edu.tr",
        list_url="https://www.omu.edu.tr/tr/etkinlikler",
        faculty=None,
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=10,
        parser_options={},
        is_active=True,
        last_success_at=None,
        last_error=None,
    )
    http_client = _FakeEventHTTPClient(
        {
            "https://www.omu.edu.tr/tr/etkinlikler": """
                <html><body>
                  <a href="/tr/etkinlikler/yapay-zeka-zirvesi">Yapay Zeka Zirvesi 2026</a>
                </body></html>
            """,
            "https://www.omu.edu.tr/tr/etkinlikler/yapay-zeka-zirvesi": """
                <html><body>
                  <h1>Yapay Zeka Zirvesi 2026</h1>
                  <p>Tarih: 20 Nisan 2026 10:30</p>
                  <p>Yer: Ataturk Kongre Merkezi</p>
                </body></html>
            """,
        }
    )

    result = await sync_event_source(
        source,
        http_client=http_client,
        dry_run=True,
    )

    assert isinstance(result, EventSourceSyncResult)
    assert result.status == "dry_run"
    assert result.stats.items_found == 1
    assert result.stats.items_inserted == 1


@pytest.mark.asyncio
async def test_sync_event_source_can_skip_detail_fetches_in_fast_refresh():
    source = EventSourceRecord(
        id=0,
        name="OMU Etkinlikler",
        source_type="html_list",
        parser_key="generic_html",
        base_url="https://www.omu.edu.tr",
        list_url="https://www.omu.edu.tr/tr/etkinlikler",
        faculty=None,
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=10,
        parser_options={},
        is_active=True,
        last_success_at=None,
        last_error=None,
    )
    http_client = _FakeEventHTTPClient(
        {
            "https://www.omu.edu.tr/tr/etkinlikler": """
                <html><body>
                  <a href="/tr/etkinlikler/yapay-zeka-zirvesi">Yapay Zeka Zirvesi 2026</a>
                </body></html>
            """,
        }
    )

    result = await sync_event_source(
        source,
        http_client=http_client,
        dry_run=True,
        fetch_details=False,
    )

    assert result.status == "dry_run"
    assert result.stats.items_found == 1
    assert http_client.requested_urls == ["https://www.omu.edu.tr/tr/etkinlikler"]
