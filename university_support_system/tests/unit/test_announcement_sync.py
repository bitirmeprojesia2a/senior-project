"""Announcement sync helper tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from src.agents.announcement.sync import (
    AnnouncementReference,
    AnnouncementSourceSyncResult,
    _extract_paginated_news_page_urls,
    _build_display_summary_base,
    _clean_refined_display_summary,
    _collect_references_for_source,
    _should_refine_display_summary,
    build_candidate_from_reference,
    extract_announcement_references_from_html,
    extract_announcement_links_from_html,
    extract_omu_announcement_references_from_html,
    extract_omu_announcement_text_from_html,
    extract_omu_faculty_home_references_from_html,
    extract_omu_faculty_home_text_from_html,
    extract_readable_text_from_html,
    sync_announcement_source,
)
from src.db.announcement_sources import (
    AnnouncementCandidate,
    AnnouncementLinkCandidate,
    AnnouncementSourceRecord,
    get_or_create_announcement_source,
    upsert_announcements_for_source,
)
from src.db.support_models import Announcement, AnnouncementLink


def test_extract_announcement_references_from_html_filters_navigation_and_dedupes():
    html = """
    <html>
      <body>
        <nav><a href="/iletisim">Iletisim</a></nav>
        <section>
          <a href="/duyuru/cap-2026">CAP Basvurulari 2026 Bahar Donemi Icin Acildi</a>
          <a href="/duyuru/cap-2026">CAP Basvurulari 2026 Bahar Donemi Icin Acildi</a>
          <a href="/duyuru/erasmus-takvim">Erasmus Basvuru Takvimi Guncellendi</a>
        </section>
      </body>
    </html>
    """

    references = extract_announcement_references_from_html(
        html,
        base_url="https://omu.edu.tr/duyurular",
        max_items=5,
    )

    assert len(references) == 2
    assert references[0].source_url == "https://omu.edu.tr/duyuru/cap-2026"
    assert references[1].title == "Erasmus Basvuru Takvimi Guncellendi"


def test_extract_omu_announcement_references_from_html_keeps_only_detail_pages():
    html = """
    <html>
      <body>
        <a href="/tr/duyurular">Tum Duyurular</a>
        <a href="/tr/icerik/duyuru/erasmus-ilani">Erasmus Ogrenci Hareketliligi Ilani</a>
        <a href="/tr/icerik/haber/bilim-senligi">Bilim Senligi Haberi</a>
        <a href="/tr/icerik/duyuru/cap-2026">CAP Basvurulari 2026 Bahar Donemi Icin Acildi</a>
      </body>
    </html>
    """

    references = extract_omu_announcement_references_from_html(
        html,
        base_url="https://www.omu.edu.tr",
        max_items=10,
    )

    assert [item.source_url for item in references] == [
        "https://www.omu.edu.tr/tr/icerik/duyuru/erasmus-ilani",
        "https://www.omu.edu.tr/tr/icerik/duyuru/cap-2026",
    ]


def test_extract_omu_announcement_references_from_html_parses_list_dates():
    html = """
    <html>
      <body>
        <div class="view-content">
          <ul>
            <li class="ht-layout aos-init aos-animate">
              <div class="ht-item">
                <div class="ht-body-container">
                  <div class="ht-heading-title-text">
                    <a href="/tr/icerik/duyuru/turk-dunyasi-sehircilik-zirvesi-omude-toplaniyor">
                      Turk Dunyasi Sehircilik Zirvesi OMU'de toplaniyor
                    </a>
                  </div>
                  <div class="ht-timestamp"><i class="far fa-clock"></i> 15 Nisan 2026, Carsamba</div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </body>
    </html>
    """

    references = extract_omu_announcement_references_from_html(
        html,
        base_url="https://www.omu.edu.tr",
        max_items=10,
    )

    assert len(references) == 1
    assert references[0].source_url == "https://www.omu.edu.tr/tr/icerik/duyuru/turk-dunyasi-sehircilik-zirvesi-omude-toplaniyor"
    assert references[0].published_at == datetime(2026, 4, 15, tzinfo=UTC)


def test_extract_omu_faculty_home_references_from_html_filters_only_news_links():
    html = """
    <html>
      <body>
        <a href="/tr">Muhendislik Fakultesi</a>
        <article class="news-item page-row has-divider clearfix row">
          <div class="details col-md-10 col-sm-9 col-xs-8">
            <h2 class="title"><a href="/tr/haberler/vefat-ve-bassagligi-060426">Vefat ve Bassagligi</a></h2>
            <p>Fakultemiz mensuplarinin basi sag olsun.</p>
            <a class="btn btn-theme read-more" href="/tr/haberler/vefat-ve-bassagligi-060426">Daha fazlasi</a>
          </div>
        </article>
        <a href="/tr/haberler/mezuniyet/duyuru.pdf">Pdf Duyuru</a>
        <a href="/tr/fakulte-hakkinda">Fakulte Hakkinda</a>
      </body>
    </html>
    """

    references = extract_omu_faculty_home_references_from_html(
        html,
        base_url="https://muhendislik.omu.edu.tr",
        max_items=10,
    )

    assert [item.title for item in references] == ["Vefat ve Bassagligi"]
    assert [item.source_url for item in references] == [
        "https://muhendislik.omu.edu.tr/tr/haberler/vefat-ve-bassagligi-060426"
    ]
    assert references[0].teaser == "Fakultemiz mensuplarinin basi sag olsun."


def test_extract_omu_faculty_home_references_from_html_skips_sidebar_news_items_and_parses_teaser_date():
    html = """
    <html>
      <body>
        <article class="news-item page-row has-divider clearfix row">
          <div class="details col-md-10 col-sm-9 col-xs-8">
            <h3 class="title">
              <a href="/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi">
                2025-2026 Bahar Yariyili Ara Sinav Programi
              </a>
            </h3>
            <p>2025-2026 Bahar Yariyili Ara Sinav Programi icin tiklayiniz. Son guncelleme 27.03.2026</p>
            <a class="btn btn-theme read-more" href="/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi">Daha fazlasi</a>
          </div>
        </article><!--//news-item-->
        <article class="news-item row">
          <div class="details col-md-10 col-sm-9 col-xs-9">
            <p class="people">
              <span class="name">
                <a href="/tr/haberler/2022-2023-bahar-yariyili-hesaplamali-bilimler-ders-programi">
                  2022-2023 Bahar Yariyili Hesaplamali Bilimler Ders Programi
                </a>
              </span><br>
              <span class="title">27 Mart 2026</span>
            </p>
          </div>
        </article><!--//news-item-->
      </body>
    </html>
    """

    references = extract_omu_faculty_home_references_from_html(
        html,
        base_url="https://bil-muhendislik.omu.edu.tr",
        max_items=10,
    )

    assert [item.title for item in references] == ["2025-2026 Bahar Yariyili Ara Sinav Programi"]
    assert references[0].published_at is None
    assert references[0].source_url == (
        "https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi"
    )


def test_extract_announcement_links_from_html_keeps_pdf_and_tiklayiniz_targets():
    html = """
    <html>
      <body>
        <a href="/dosyalar/ara-sinav-programi.pdf">2025-2026 Bahar Ara Sinav Programi</a>
        <a href="/dosyalar/basvuru-formu.docx">Tiklayiniz</a>
        <a href="https://facebook.com/omu">Facebook</a>
      </body>
    </html>
    """

    links = extract_announcement_links_from_html(
        html,
        base_url="https://bil-muhendislik.omu.edu.tr",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-1",
    )

    assert [link.url for link in links] == [
        "https://bil-muhendislik.omu.edu.tr/dosyalar/ara-sinav-programi.pdf",
        "https://bil-muhendislik.omu.edu.tr/dosyalar/basvuru-formu.docx",
    ]
    assert links[1].label == "basvuru formu"


def test_extract_announcement_links_from_html_skips_site_shell_navigation_links():
    html = """
    <html>
      <body>
        <a href="/en/haberler/duyuru-1">EN</a>
        <a href="/tr/egitim-ogretim/lisans-programi">Lisans Programı</a>
        <a href="/dosyalar/2025-2026-bahar-ara-sinav-programi.pdf">Ara Sinav Programi PDF</a>
      </body>
    </html>
    """

    links = extract_announcement_links_from_html(
        html,
        base_url="https://bil-muhendislik.omu.edu.tr",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-1",
    )

    assert links == (
        AnnouncementLinkCandidate(
            label="Ara Sinav Programi PDF",
            url="https://bil-muhendislik.omu.edu.tr/dosyalar/2025-2026-bahar-ara-sinav-programi.pdf",
            link_type="attachment",
            sort_order=0,
        ),
    )


def test_extract_announcement_links_from_html_skips_unrelated_same_domain_sections():
    html = """
    <html>
      <body>
        <a href="/tr/personel/akademik-personel-emekli">Akademik Personel Emekli</a>
        <a href="/tr/haberler/duyuru-1/ek-program.pdf">Program PDF</a>
      </body>
    </html>
    """

    links = extract_announcement_links_from_html(
        html,
        base_url="https://bil-muhendislik.omu.edu.tr",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-1",
    )

    assert links == (
        AnnouncementLinkCandidate(
            label="Program PDF",
            url="https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-1/ek-program.pdf",
            link_type="attachment",
            sort_order=0,
        ),
    )


def test_extract_announcement_links_from_html_skips_unscoped_global_attachment_for_omu_main():
    html = """
    <html>
      <body>
        <a href="/Upload/KesinKayitKilavuzu2025-2026.pdf">2025-2026 Kesin Kayıt Kılavuzu</a>
        <a href="/sites/default/files/files/ogretim-uyesi-alim-ilani-3-nisan-2026/ilan.pdf">Ilan PDF</a>
      </body>
    </html>
    """

    links = extract_announcement_links_from_html(
        html,
        base_url="https://www.omu.edu.tr",
        source_url="https://www.omu.edu.tr/tr/icerik/duyuru/ogretim-uyesi-alim-ilani-3-nisan-2026",
        title="Ogretim Uyesi Alim Ilani 3 Nisan 2026",
    )

    assert links == (
        AnnouncementLinkCandidate(
            label="Ilan PDF",
            url="https://www.omu.edu.tr/sites/default/files/files/ogretim-uyesi-alim-ilani-3-nisan-2026/ilan.pdf",
            link_type="attachment",
            sort_order=0,
        ),
    )


def test_extract_paginated_news_page_urls_sorts_unique_pages():
    html = """
    <html>
      <body>
        <a href="/tr/haberler/page:3">3</a>
        <a href="/tr/haberler/page:2">2</a>
        <a href="/tr/haberler/page:10">10</a>
        <a href="/tr/haberler/page:2">2 tekrar</a>
      </body>
    </html>
    """

    urls = _extract_paginated_news_page_urls(
        html,
        base_url="https://bil-muhendislik.omu.edu.tr",
        list_url="https://bil-muhendislik.omu.edu.tr/tr/haberler",
    )

    assert urls == [
        "https://bil-muhendislik.omu.edu.tr/tr/haberler/page:2",
        "https://bil-muhendislik.omu.edu.tr/tr/haberler/page:3",
        "https://bil-muhendislik.omu.edu.tr/tr/haberler/page:10",
    ]


def test_extract_readable_text_from_html_removes_script_noise():
    html = """
    <html>
      <head><script>console.log('ignore');</script></head>
      <body>
        <article>
          <h1>CAP Basvurulari Acildi</h1>
          <p>Basvurular 15 Nisan 2026 tarihine kadar aciktir.</p>
        </article>
      </body>
    </html>
    """

    text = extract_readable_text_from_html(html)

    assert "console.log" not in text
    assert "CAP Basvurulari Acildi" in text
    assert "15 Nisan 2026" in text


def test_extract_omu_announcement_text_from_html_trims_shell_noise():
    html = """
    <html>
      <body>
        <div>Ondokuz Mayis Universitesi</div>
        <div>Duyuru</div>
        <h1>Erasmus Ogrenci Hareketliligi Ilani</h1>
        <div>02 Subat 2026, Pazartesi - 16:23</div>
        <div>Paylas</div>
        <p>Basvurular 14 Subat 2026 tarihine kadar devam edecektir.</p>
        <p>Detayli bilgi icin koordinatorluk sayfasini inceleyiniz.</p>
        <div>Ilginizi Cekebilir</div>
        <div>Menu Baglantisi</div>
      </body>
    </html>
    """

    text = extract_omu_announcement_text_from_html(
        html,
        title="Erasmus Ogrenci Hareketliligi Ilani",
    )

    assert "Paylas" not in text
    assert "Ilginizi Cekebilir" not in text
    assert "Basvurular 14 Subat 2026 tarihine kadar devam edecektir." in text
    assert "Detayli bilgi icin koordinatorluk sayfasini inceleyiniz." in text


def test_extract_omu_announcement_text_from_html_skips_author_and_update_metadata():
    html = """
    <html>
      <body>
        <div>duyuru</div>
        <h1>Orta Karadeniz Kariyer Fuari</h1>
        <div>duyuru</div>
        <div>Orta Karadeniz Kariyer Fuari</div>
        <div>gulcan.akdag</div>
        <div>08 Nisan 2026, Carsamba - 10:38</div>
        <div>Guncelleme: 08 Nisan 2026, Carsamba - 10:40</div>
        <div>Paylas</div>
        <p>Universitemiz ev sahipliginde acilis toreni canli yayinda gerceklestirilecektir.</p>
      </body>
    </html>
    """

    text = extract_omu_announcement_text_from_html(
        html,
        title="Orta Karadeniz Kariyer Fuari",
    )

    assert text.startswith("Universitemiz ev sahipliginde")


def test_extract_omu_announcement_text_from_html_keeps_body_when_first_sentence_mentions_omu():
    html = """
    <html>
      <body>
        <div>duyuru</div>
        <h1>Turk Dunyasi Sehircilik Zirvesi</h1>
        <div>duyuru</div>
        <div>Turk Dunyasi Sehircilik Zirvesi</div>
        <div>mursel.kan</div>
        <div>15 Nisan 2026, Carsamba - 17:30</div>
        <div>Guncelleme: 16 Nisan 2026, Persembe - 00:36</div>
        <div>Paylas</div>
        <p>Ondokuz Mayis Universitesi, 20 Nisan 2026 tarihinde Turk dunyasinin sehircilik vizyonuna yon verecek zirveye ev sahipligi yapacaktir.</p>
        <div>Ilginizi Cekebilir</div>
      </body>
    </html>
    """

    text = extract_omu_announcement_text_from_html(
        html,
        title="Turk Dunyasi Sehircilik Zirvesi",
    )

    assert text.startswith("Ondokuz Mayis Universitesi, 20 Nisan 2026 tarihinde Turk dunyasinin sehircilik vizyonuna")


def test_display_summary_base_prefers_summary_and_trims_length():
    display_summary = _build_display_summary_base(
        title="Baslik",
        summary="Bu duyuru ogrencilere yonelik onemli basvuru takvimini aciklamaktadir.",
        original_text="X" * 800,
    )

    assert display_summary == "Bu duyuru ogrencilere yonelik onemli basvuru takvimini aciklamaktadir."


def test_should_refine_display_summary_for_tiklayiniz_style_summary():
    assert _should_refine_display_summary(
        summary="Ders programını görüntülemek için tıklayınız.",
        original_text="Ders programı ekte verilmiştir.",
    ) is True
    assert _should_refine_display_summary(
        summary="2025-2026 bahar yarıyılı ara sınav programı yayımlandı.",
        original_text="2025-2026 bahar yarıyılı ara sınav programı yayımlandı.",
    ) is False


def test_clean_refined_display_summary_removes_url_and_emoji():
    cleaned = _clean_refined_display_summary(
        "📢 Ders programi yayinlandi. https://omu.edu.tr/dosya.pdf"
    )

    assert cleaned == "Ders programi yayinlandi."


def test_extract_omu_faculty_home_text_from_html_trims_faculty_shell():
    html = """
    <html>
      <body>
        <div>Muhendislik Fakultesi</div>
        <div>Ara ...</div>
        <div>Toggle navigation</div>
        <h1>Profesör Kadrosuna Atama ve Tebrik</h1>
        <div>Haberler</div>
        <div>Profesör Kadrosuna Atama ve Tebrik</div>
        <div>Yazar: muhendislik | Tarih: 31 Mart 2026</div>
        <p>Fakultemiz Harita Muhendisligi Bolumu ogretim uyelerinden Doc. Dr. Veli ILCI, Profesor kadrosuna atanmistir.</p>
        <p>Kıymetli Hocamızı tebrik eder, başarılarının devamını dileriz.</p>
        <div>Profesör Kadrosuna Atama ve Tebrik</div>
        <div>Baglantilar</div>
        <div>Akademik Takvim</div>
      </body>
    </html>
    """

    text = extract_omu_faculty_home_text_from_html(
        html,
        title="Profesör Kadrosuna Atama ve Tebrik",
    )

    assert "Toggle navigation" not in text
    assert "Baglantilar" not in text
    assert "Fakultemiz Harita Muhendisligi Bolumu ogretim uyelerinden" in text
    assert "Kıymetli Hocamızı tebrik eder" in text


def test_build_candidate_from_reference_for_omu_extracts_turkish_date():
    source = AnnouncementSourceRecord(
        id=1,
        name="OMU Merkez Duyurular",
        source_type="html_list",
        parser_key="omu_main_announcements",
        base_url="https://www.omu.edu.tr",
        list_url="https://www.omu.edu.tr/tr/duyurular",
        faculty=None,
        unit_name=None,
        department=None,
        fetch_interval_minutes=360,
        max_items_per_run=20,
    )
    reference = AnnouncementReference(
        title="CAP Basvurulari 2026 Bahar Donemi Icin Acildi",
        source_url="https://www.omu.edu.tr/tr/icerik/duyuru/cap-2026",
    )
    detail_html = """
    <html>
      <body>
        <h1>CAP Basvurulari 2026 Bahar Donemi Icin Acildi</h1>
        <div>03 Mart 2026, Sali - 09:00</div>
        <p>Basvurular 21 Mart 2026 tarihine kadar alinacaktir.</p>
      </body>
    </html>
    """

    candidate = build_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty=None,
    )

    assert candidate.published_at == datetime(2026, 3, 3, tzinfo=UTC)
    assert candidate.summary == "Basvurular 21 Mart 2026 tarihine kadar alinacaktir."
    assert candidate.display_summary == "Basvurular 21 Mart 2026 tarihine kadar alinacaktir."
    assert candidate.department == "academic_programs"


def test_build_candidate_from_reference_includes_attachment_links():
    source = AnnouncementSourceRecord(
        id=1,
        name="OMU Bil Muh Duyurular",
        source_type="html_list",
        parser_key="omu_faculty_home_announcements",
        base_url="https://bil-muhendislik.omu.edu.tr",
        list_url="https://bil-muhendislik.omu.edu.tr/tr/haberler",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=20,
    )
    reference = AnnouncementReference(
        title="Ara Sinav Programi",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/ara-sinav-programi",
    )
    detail_html = """
    <html>
      <body>
        <h1>Ara Sinav Programi</h1>
        <p>Sinav programi aciklanmistir.</p>
        <a href="/dosyalar/ara-sinav-programi.pdf">Program PDF</a>
      </body>
    </html>
    """

    candidate = build_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty="Muhendislik Fakultesi",
    )

    assert candidate.links == (
        AnnouncementLinkCandidate(
            label="Program PDF",
            url="https://bil-muhendislik.omu.edu.tr/dosyalar/ara-sinav-programi.pdf",
            link_type="attachment",
            sort_order=0,
        ),
    )


def test_build_candidate_from_reference_uses_teaser_when_detail_is_low_signal():
    source = AnnouncementSourceRecord(
        id=1,
        name="OMU Muhendislik Duyurular",
        source_type="html_list",
        parser_key="omu_faculty_home_announcements",
        base_url="https://muhendislik.omu.edu.tr",
        list_url="https://muhendislik.omu.edu.tr/tr",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=12,
    )
    reference = AnnouncementReference(
        title="Is Sagligi ve Guvenligi Egitimi",
        source_url="https://muhendislik.omu.edu.tr/tr/haberler/isg-egitimi",
        teaser="Akademik ve idari personellerimize yonelik temel is sagligi ve guvenligi egitimi gerceklestirildi.",
    )
    detail_html = """
    <html>
      <body>
        <h1>Is Sagligi ve Guvenligi Egitimi</h1>
        <div>31 Mart 2026</div>
        <div>Son Haberler</div>
        <div>Profesorluk Atamasi</div>
        <div>27 Mart 2026</div>
        <div>Etkinlikler</div>
      </body>
    </html>
    """

    candidate = build_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty="Muhendislik Fakultesi",
    )

    assert candidate.summary == (
        "Akademik ve idari personellerimize yonelik temel is sagligi ve guvenligi egitimi gerceklestirildi."
    )
    assert candidate.display_summary == (
        "Akademik ve idari personellerimize yonelik temel is sagligi ve guvenligi egitimi gerceklestirildi."
    )
    assert candidate.original_text == (
        "Akademik ve idari personellerimize yonelik temel is sagligi ve guvenligi egitimi gerceklestirildi."
    )


def test_build_candidate_from_reference_uses_teaser_when_detail_is_pdf_payload():
    source = AnnouncementSourceRecord(
        id=1,
        name="OMU EEM Duyurular",
        source_type="html_list",
        parser_key="omu_faculty_home_announcements",
        base_url="https://eem-muhendislik.omu.edu.tr",
        list_url="https://eem-muhendislik.omu.edu.tr/tr/haberler",
        faculty="Muhendislik Fakultesi",
        unit_name="Elektrik Elektronik Muhendisligi",
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=20,
    )
    reference = AnnouncementReference(
        title="Ara Sinav Programi",
        source_url="https://eem-muhendislik.omu.edu.tr/tr/haberler/ara-sinav-programi",
        teaser="2025-2026 bahar yariyili ara sinav programi aciklanmistir.",
    )
    detail_html = "%PDF-1.4\x00binary payload"

    candidate = build_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty="Muhendislik Fakultesi",
    )

    assert candidate.summary == "2025-2026 bahar yariyili ara sinav programi aciklanmistir."
    assert candidate.display_summary == "2025-2026 bahar yariyili ara sinav programi aciklanmistir."
    assert candidate.original_text == "2025-2026 bahar yariyili ara sinav programi aciklanmistir."


def test_build_candidate_from_reference_for_faculty_source_ignores_unreliable_teaser_and_sidebar_dates():
    source = AnnouncementSourceRecord(
        id=1,
        name="OMU Bilgisayar Muhendisligi Duyurular",
        source_type="html_list",
        parser_key="omu_faculty_home_announcements",
        base_url="https://bil-muhendislik.omu.edu.tr",
        list_url="https://bil-muhendislik.omu.edu.tr/tr/haberler",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=20,
    )
    reference = AnnouncementReference(
        title="2025-2026 Bahar Yariyili Ara Sinav Programi",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi",
        published_at=None,
        teaser="2025-2026 Bahar Yariyili Ara Sinav Programi icin tiklayiniz. Son guncelleme 27.03.2026",
    )
    detail_html = """
    <html>
      <body>
        <h1>2025-2026 Bahar Yariyili Ara Sinav Programi</h1>
        <div>Paylas</div>
        <p>2025-2026 Bahar Yariyili Ara Sinav Programi icin tiklayiniz.</p>
        <div>Son Haberler</div>
        <article class="news-item row">
          <span class="title">11 Mart 2026</span>
        </article>
      </body>
    </html>
    """

    candidate = build_candidate_from_reference(
        reference,
        source=source,
        detail_html=detail_html,
        fallback_department="academic_programs",
        fallback_faculty="Muhendislik Fakultesi",
    )

    assert candidate.published_at is None


class _FakeAnnouncementHTTPClient:
    def __init__(self, responses: dict[str, str]) -> None:
        self.responses = responses

    async def get_text(self, url: str) -> str:
        return self.responses[url]


@pytest.mark.asyncio
async def test_collect_references_for_source_follows_paginated_news_pages():
    source = AnnouncementSourceRecord(
        id=2,
        name="OMU Bilgisayar Muhendisligi Duyurular",
        source_type="html_list",
        parser_key="omu_faculty_home_announcements",
        base_url="https://bil-muhendislik.omu.edu.tr",
        list_url="https://bil-muhendislik.omu.edu.tr/tr/haberler",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        fetch_interval_minutes=360,
        max_items_per_run=10,
    )
    http_client = _FakeAnnouncementHTTPClient(
        {
            "https://bil-muhendislik.omu.edu.tr/tr/haberler": """
                <html><body>
                  <div class="col-md-4 news-item">
                    <h2 class="title"><a href="/tr/haberler/a1">Kisa Baslik</a></h2>
                    <p>Ozet 1</p>
                  </div><!--//news-item-->
                  <div class="col-md-4 news-item">
                    <h2 class="title"><a href="/tr/haberler/a2">A2 haber basligi uzun</a></h2>
                    <p>Ozet 2</p>
                  </div><!--//news-item-->
                  <a href="/tr/haberler/page:2">2</a>
                  <a href="/tr/haberler/page:3">3</a>
                </body></html>
            """,
            "https://bil-muhendislik.omu.edu.tr/tr/haberler/page:2": """
                <html><body>
                  <div class="col-md-4 news-item">
                    <h2 class="title"><a href="/tr/haberler/b1">B1 haber basligi uzun</a></h2>
                    <p>Ozet 3</p>
                  </div><!--//news-item-->
                  <div class="col-md-4 news-item">
                    <h2 class="title"><a href="/tr/haberler/b2">B2 haber basligi uzun</a></h2>
                    <p>Ozet 4</p>
                  </div><!--//news-item-->
                </body></html>
            """,
            "https://bil-muhendislik.omu.edu.tr/tr/haberler/page:3": """
                <html><body>
                  <div class="col-md-4 news-item">
                    <h2 class="title"><a href="/tr/haberler/c1">C1 haber basligi uzun</a></h2>
                    <p>Ozet 5</p>
                  </div><!--//news-item-->
                </body></html>
            """,
        }
    )

    refs = await _collect_references_for_source(
        source,
        http_client=http_client,
    )

    assert [ref.source_url for ref in refs] == [
        "https://bil-muhendislik.omu.edu.tr/tr/haberler/a2",
        "https://bil-muhendislik.omu.edu.tr/tr/haberler/b1",
        "https://bil-muhendislik.omu.edu.tr/tr/haberler/b2",
        "https://bil-muhendislik.omu.edu.tr/tr/haberler/c1",
    ]


@pytest.mark.asyncio
async def test_sync_announcement_source_dry_run_skips_db_for_transient_source():
    source = AnnouncementSourceRecord(
        id=0,
        name="OMU Merkez Duyurular",
        source_type="html_list",
        parser_key="omu_main_announcements",
        base_url="https://www.omu.edu.tr",
        list_url="https://www.omu.edu.tr/tr/duyurular",
        faculty=None,
        unit_name=None,
        department=None,
        fetch_interval_minutes=360,
        max_items_per_run=20,
    )
    http_client = _FakeAnnouncementHTTPClient(
        {
            "https://www.omu.edu.tr/tr/duyurular": """
                <html><body>
                  <a href="/tr/icerik/duyuru/erasmus-ilani">Erasmus Ogrenci Hareketliligi Ilani</a>
                  <a href="/tr/icerik/duyuru/erasmus-ilani">Erasmus Ogrenci Hareketliligi Ilani</a>
                </body></html>
            """,
            "https://www.omu.edu.tr/tr/icerik/duyuru/erasmus-ilani": """
                <html><body>
                  <h1>Erasmus Ogrenci Hareketliligi Ilani</h1>
                  <div>02 Subat 2026, Pazartesi - 16:23</div>
                  <p>Basvurular 14 Subat 2026 tarihine kadar devam edecektir.</p>
                </body></html>
            """,
        }
    )

    result = await sync_announcement_source(
        source,
        http_client=http_client,
        dry_run=True,
    )

    assert isinstance(result, AnnouncementSourceSyncResult)
    assert result.status == "dry_run"
    assert result.stats.items_found == 1
    assert result.stats.items_inserted == 1
    assert result.stats.items_updated == 0


@pytest.mark.asyncio
async def test_upsert_announcements_for_source_inserts_and_updates_existing_row(db_session):
    source = await get_or_create_announcement_source(
        db_session,
        name="OMU Duyurular",
        list_url="https://omu.edu.tr/duyurular",
        department="student_affairs",
    )

    existing = Announcement(
        source_id=source.id,
        title="Eski Duyuru Basligi",
        original_text="Eski icerik",
        summary="Eski ozet",
        source_url="https://omu.edu.tr/duyuru/cap-2026",
        faculty=None,
        department="student_affairs",
        published_at=None,
        last_seen_at=datetime.now(UTC) - timedelta(days=3),
        fetched_at=datetime.now(UTC) - timedelta(days=3),
        is_active=True,
    )
    db_session.add(existing)
    await db_session.flush()

    stats = await upsert_announcements_for_source(
        db_session,
        source=source,
        candidates=[
            AnnouncementCandidate(
                title="CAP Basvurulari Acildi",
                source_url="https://omu.edu.tr/duyuru/cap-2026",
                original_text="CAP basvurulari 15 Nisan 2026 tarihine kadar devam eder.",
                department="academic_programs",
            )
        ],
        seen_at=datetime.now(UTC),
    )

    refreshed = await db_session.scalar(
        select(Announcement).where(Announcement.source_url == "https://omu.edu.tr/duyuru/cap-2026")
    )

    assert refreshed is not None
    assert refreshed.title == "CAP Basvurulari Acildi"
    assert refreshed.department == "academic_programs"
    assert refreshed.is_active is True
    assert stats.items_inserted == 0
    assert stats.items_updated == 1


@pytest.mark.asyncio
async def test_upsert_announcements_for_source_replaces_attachment_links(db_session):
    source = await get_or_create_announcement_source(
        db_session,
        name="OMU Duyurular",
        list_url="https://omu.edu.tr/duyurular-linkli",
        department="student_affairs",
    )

    stats = await upsert_announcements_for_source(
        db_session,
        source=source,
        candidates=[
            AnnouncementCandidate(
                title="Sinav Programi",
                source_url="https://omu.edu.tr/duyuru/sinav-programi",
                original_text="Program yayinlandi.",
                links=(
                    AnnouncementLinkCandidate(
                        label="Program PDF",
                        url="https://omu.edu.tr/dosyalar/program.pdf",
                        link_type="attachment",
                        sort_order=0,
                    ),
                    AnnouncementLinkCandidate(
                        label="Basvuru Formu",
                        url="https://omu.edu.tr/dosyalar/form.docx",
                        link_type="attachment",
                        sort_order=1,
                    ),
                ),
            )
        ],
        seen_at=datetime.now(UTC),
    )

    announcement = await db_session.scalar(
        select(Announcement).where(Announcement.source_url == "https://omu.edu.tr/duyuru/sinav-programi")
    )
    assert announcement is not None

    links = list(
        (
            await db_session.execute(
                select(AnnouncementLink)
                .where(AnnouncementLink.announcement_id == announcement.id)
                .order_by(AnnouncementLink.sort_order.asc())
            )
        )
        .scalars()
        .all()
    )

    assert stats.items_inserted == 1
    assert [link.label for link in links] == ["Program PDF", "Basvuru Formu"]


@pytest.mark.asyncio
async def test_upsert_announcements_for_source_strips_null_bytes(db_session):
    source = await get_or_create_announcement_source(
        db_session,
        name="OMU Duyurular Null Byte",
        list_url="https://omu.edu.tr/duyurular-null",
        department="student_affairs",
    )

    stats = await upsert_announcements_for_source(
        db_session,
        source=source,
        candidates=[
            AnnouncementCandidate(
                title="Binary Benzeri Duyuru",
                source_url="https://omu.edu.tr/duyuru/binary",
                original_text="satir\x00ici metin",
                summary="ozet\x00metni",
                display_summary="gorunum\x00ozeti",
            )
        ],
        seen_at=datetime.now(UTC),
    )

    announcement = await db_session.scalar(
        select(Announcement).where(Announcement.source_url == "https://omu.edu.tr/duyuru/binary")
    )

    assert announcement is not None
    assert "\x00" not in (announcement.original_text or "")
    assert "\x00" not in (announcement.summary or "")
    assert "\x00" not in (announcement.display_summary or "")
    assert stats.items_inserted == 1


@pytest.mark.asyncio
async def test_upsert_announcements_for_source_deactivates_stale_missing_rows(db_session):
    source = await get_or_create_announcement_source(
        db_session,
        name="Muhendislik Duyurulari",
        list_url="https://omu.edu.tr/muhendislik/duyurular",
        department="academic_programs",
    )

    stale = Announcement(
        source_id=source.id,
        title="Artik Gorunmeyen Duyuru",
        original_text="Eski duyuru govdesi",
        summary="Eski duyuru govdesi",
        source_url="https://omu.edu.tr/duyuru/eski",
        faculty="Muhendislik Fakultesi",
        department="academic_programs",
        published_at=None,
        last_seen_at=datetime.now(UTC) - timedelta(days=4),
        fetched_at=datetime.now(UTC) - timedelta(days=4),
        is_active=True,
    )
    db_session.add(stale)
    await db_session.flush()

    stats = await upsert_announcements_for_source(
        db_session,
        source=source,
        candidates=[
            AnnouncementCandidate(
                title="Yeni Duyuru",
                source_url="https://omu.edu.tr/duyuru/yeni",
                original_text="Yeni duyuru govdesi",
            )
        ],
        seen_at=datetime.now(UTC),
    )

    old_row = await db_session.scalar(
        select(Announcement).where(Announcement.source_url == "https://omu.edu.tr/duyuru/eski")
    )
    new_row = await db_session.scalar(
        select(Announcement).where(Announcement.source_url == "https://omu.edu.tr/duyuru/yeni")
    )

    assert old_row is not None
    assert old_row.is_active is False
    assert old_row.inactive_reason == "missing_from_source"
    assert new_row is not None
    assert stats.items_inserted == 1
    assert stats.items_deactivated == 1
