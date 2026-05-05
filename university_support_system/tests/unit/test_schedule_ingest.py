from datetime import time
from pathlib import Path

from src.core.text_normalization import normalize_text
from src.db.schedule_ingest import (
    classify_schedule_document,
    _normalize_day_label,
    _looks_like_classroom,
    _looks_like_plausible_department,
    _infer_department_from_filename,
    _merge_source_override,
    _source_override_for,
    infer_schedule_context,
    parse_schedule_table,
)


def test_normalize_day_label_handles_vertical_reversed_text():
    assert _normalize_day_label("i\ns\ne\ntr\na\nz\na\nP") == "Pazartesi"
    assert _normalize_day_label("Çarşamba") == "Carsamba"


def test_normalize_day_label_handles_real_turkish_text():
    assert _normalize_day_label("\u00c7ar\u015famba") == "Carsamba"
    assert _normalize_day_label("Per\u015fembe") == "Persembe"


def test_classroom_token_regex_handles_turkish_letters_and_dash_forms():
    assert _looks_like_classroom("\u00d6\u011eR-101")
    assert _looks_like_classroom("MBG-L1")
    assert _looks_like_classroom("BD-206")


def test_parse_grouped_weekly_table_extracts_schedule_group_and_missing_code():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Molekuler Biyoloji ve Genetik",
    }
    table = [
        ["", "SAAT", None, "I.SINIF", None, None, "II.SINIF", None, None],
        [None, None, None, "DERS", "Derslik", "OE", "DERS", "Derslik", "OE"],
        ["PAZARTESI", "1", "08.15-09.00", "GENEL BIYOLOJI II", "MBG-L1", "KY", "", "", ""],
        [None, "2", "09.15-10.00", "", "", "", "ORGANIK KIMYA LAB", "Org.Kim.L", "HK"],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="schedule.pdf",
    )

    assert len(slots) == 2
    assert slots[0]["schedule_group"] == "I.SINIF"
    assert slots[0]["course_code"] is None
    assert slots[0]["course_key"] == "genel biyoloji ii"
    assert slots[0]["classroom"] == "MBG-L1"
    assert slots[0]["instructor"] == "KY"
    assert slots[1]["schedule_group"] == "II.SINIF"
    assert slots[1]["course_name"] == "ORGANIK KIMYA LAB"


def test_parse_row_day_matrix_table_extracts_class_year_rows():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Endustri Muhendisligi",
    }
    table = [
        ["Gun", "Sinif", "815-900", "915-1000", "1015-1100"],
        ["Pazartesi", "I", "TBMAT112 Matematik II (MF101)", "", ""],
        [None, "IV", "", "END400 Bitirme Projesi D101", ""],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="endustri.pdf",
    )

    assert len(slots) == 2
    assert slots[0]["schedule_group"] == "I"
    assert slots[0]["day_of_week"] == "Pazartesi"
    assert slots[0]["start_time"] == time(8, 15)
    assert slots[1]["schedule_group"] == "IV"
    assert slots[1]["course_code"] == "END400"


def test_parse_two_column_grouped_weekly_table_extracts_classroom_pairs():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Insaat Muhendisligi",
    }
    table = [
        ["", None, "1. SINIF", None, "2. SINIF", None, "3. SINIF", None],
        [None, None, "Ders", "Derslik", "Ders", "Derslik", "Ders", "Derslik"],
        ["P\nA\nZ\nA\nR\nT\nE\nS\nI", "08:15-09:00", "Matematik - II", "102", "", "", "Zemin Mekanigi - II", "103"],
        [None, "09:15-10:00", "Matematik - II", "102", "", "", "Zemin Mekanigi - II", "103"],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="insaat.pdf",
    )

    assert len(slots) == 4
    assert slots[0]["schedule_group"] == "1. SINIF"
    assert slots[0]["classroom"] == "102"
    assert slots[0]["day_of_week"] == "Pazartesi"
    assert slots[1]["schedule_group"] == "3. SINIF"
    assert slots[1]["classroom"] == "103"


def test_parse_two_column_grouped_weekly_table_with_title_row():
    context = {
        "academic_year": "2025-2026",
        "term": "guz",
        "department": "Matematik",
    }
    table = [
        [None, "2025-2026 EGITIM OGRETIM YILI GUZ DONEMI DERS PROGRAMI", None, None, None, None, None, None],
        [None, "Saat", "1. SINIF", None, "2. SINIF", None, "3. SINIF", None],
        ["I\nL\nA\nS", "8:15", "Analiz II", "F1", "", "", "Cebir II", "F4"],
        [None, "9:15", "Fizik II", "F1", "Lineer Cebir II", "F3", "", ""],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="matematik.pdf",
    )

    assert len(slots) == 4
    assert slots[0]["day_of_week"] == "Sali"
    assert slots[0]["schedule_group"] == "1. SINIF"
    assert slots[0]["course_name"] == "Analiz II"
    assert slots[1]["schedule_group"] == "3. SINIF"
    assert slots[1]["classroom"] == "F4"
    assert slots[0]["start_time"] == time(8, 15)
    assert slots[0]["end_time"] == time(9, 15)


def test_parse_row_day_time_matrix_table_extracts_section_prefixed_cells():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Biyoloji Egitimi",
    }
    table = [
        ["", "1\n8:15 - 9:00", "2\n9:15 - 10:00", "3\n10:15 - 11:00"],
        ["Pa", "", "", "ME1/BIYO1/FZK1/FBE1\nAtaturk Ilkeleri ve Inkilap Tarihi\n2\nBD-206 AEI"],
        ["Sa", "", "BIYO1\nGenel Biyoloji 2\nBD-306 M.H. Gunes", ""],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="biyoloji.pdf",
    )

    assert len(slots) == 2
    assert slots[0]["day_of_week"] == "Pazartesi"
    assert slots[0]["section"] == "ME1/BIYO1/FZK1/FBE1"
    assert slots[0]["classroom"] == "BD-206"
    assert slots[1]["day_of_week"] == "Sali"
    assert slots[1]["course_name"] == "Genel Biyoloji 2"


def test_parse_column_day_matrix_table_infers_end_time_from_next_start():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Pedagojik Formasyon",
    }
    table = [
        ["", "Pazartesi", "Sali", "Carsamba"],
        ["8.15", "", "", ""],
        ["9.15", "", "", ""],
        ["12.30", "", "", "LPFE402 Ozel Ogretim Yontemleri"],
        ["13.30", "", "", "LPFE402 Ozel Ogretim Yontemleri"],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="formasyon.pdf",
    )

    assert len(slots) == 2
    assert slots[0]["day_of_week"] == "Carsamba"
    assert slots[0]["start_time"] == time(12, 30)
    assert slots[0]["end_time"] == time(13, 30)
    assert slots[1]["start_time"] == time(13, 30)


def test_parse_column_day_matrix_table_keeps_single_line_course_code_cells():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Pedagojik Formasyon",
    }
    table = [
        ["", "Pazartesi", "Sali", "Carsamba"],
        ["12.30", "", "", "LPFE402 Ozel Ogretim Yontemleri"],
        ["13.30", "", "", "LPFE402 Ozel Ogretim Yontemleri"],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="formasyon.pdf",
    )

    assert len(slots) == 2
    assert slots[0]["course_code"] == "LPFE402"
    assert slots[0]["course_name"] == "Ozel Ogretim Yontemleri"
    assert slots[0]["day_of_week"] == "Carsamba"


def test_parse_single_column_grouped_weekly_table_skips_composite_office_cells():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Sinif Ogretmenligi",
    }
    table = [
        ["Gun", "Saat", "1.SINIF", "2.SINIF", "3.SINIF", "4.SINIF"],
        [
            "Pazartesi",
            "08:15",
            "",
            "",
            "",
            "Ogretmenlik Uygulamasi II - A K.T.CAGLAYAN B201-Ofis "
            "Ogretmenlik Uygulamasi II - B K.KIROGLU B202-Ofis",
        ],
        ["Pazartesi", "09:15", "", "", "", ""],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="sinif.pdf",
    )

    assert slots == []


def test_parse_grouped_table_skips_overlong_course_names():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Okul Oncesi",
    }
    long_course = " ".join(["Ogretmenlik Uygulamasi"] * 20)
    table = [
        ["", "SAAT", None, "I.SINIF", None, None],
        [None, None, None, "DERS", "Derslik", "OE"],
        ["PAZARTESI", "1", "08.15-09.00", long_course, "BD104", "OA"],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="okul_oncesi.pdf",
    )

    assert slots == []


def test_parse_explicit_schedule_table_uses_code_and_day_columns():
    context = {
        "academic_year": "2025-2026",
        "term": "bahar",
        "department": "Elektrik-Elektronik Muhendisligi",
    }
    table = [
        ["Ogretim Uyesi", "Ders Kodu", "Ders Adi", "Gun", "Saat"],
        ["Prof. Dr. A", "EEM 661", "Genellestirilmis Elektrik Makinalari", "Carsamba", "09:00-12:00"],
        [None, "EEM 721", "Dogrusal Devinimli Elektromekanik Sistemler", "Pazartesi", "09:00-12:00"],
    ]

    slots = parse_schedule_table(
        table,
        context,
        source_document="eem.pdf",
    )

    assert len(slots) == 2
    assert slots[0]["course_code"] == "EEM661"
    assert slots[0]["instructor"] == "Prof. Dr. A"
    assert slots[1]["day_of_week"] == "Pazartesi"


def test_infer_schedule_context_uses_preview_text_before_filename():
    context = infer_schedule_context(
        Path("2025_2026_bahar_program.pdf"),
        "ONDOKUZ MAYIS UNIVERSITESI MUHENDISLIK FAKULTESI INSAAT BOLUMU 2025-2026 BAHAR DONEMI HAFTALIK DERS PROGRAMI",
    )

    assert context["academic_year"] == "2025-2026"
    assert context["term"] == "bahar"
    assert context["department"] == "INSAAT"


def test_infer_schedule_context_handles_real_turkish_department_text():
    context = infer_schedule_context(
        Path("2025_2026_bahar_program.pdf"),
        (
            "ONDOKUZ MAYIS \u00dcNIVERSITESI M\u00dcHENDISLIK FAK\u00dcLTESI "
            "ELEKTRIK-ELEKTRONIK M\u00dcHENDISLIGI B\u00d6L\u00dcM\u00dc "
            "2025-2026 BAHAR D\u00d6NEMI HAFTALIK DERS PROGRAMI"
        ),
    )

    assert normalize_text(context["department"]) == "elektrik-elektronik muhendisligi"


def test_infer_schedule_context_rejects_filename_fragments_as_department():
    context = infer_schedule_context(
        Path("2526baharfizikson.pdf"),
        "2025-2026 BAHAR DONEMI HAFTALIK DERS PROGRAMI Pazartesi 08:15-09:00",
    )

    assert context["department"] == "bilinmiyor"


def test_infer_schedule_context_rejects_explanatory_sentence_as_department():
    context = infer_schedule_context(
        Path("lisans_pedagojik_formasyon_ders_programi.pdf"),
        (
            "Bu ders ogretmenlik uygulamasi kapsaminda alinan bir derstir. "
            "Bu dersin 2025-2026 BAHAR DONEMI HAFTALIK DERS PROGRAMI"
        ),
    )

    assert context["department"] == "bilinmiyor"


def test_plausible_department_allows_explicit_program_names():
    assert _looks_like_plausible_department("Fizik")
    assert _looks_like_plausible_department("Elektrik-Elektronik Muhendisligi")
    assert not _looks_like_plausible_department("2526baharfizikson")
    assert not _looks_like_plausible_department("derstir. Bu dersin")


def test_infer_department_from_descriptive_schedule_filename():
    assert _infer_department_from_filename(
        Path("2025_2026_bahar_resim_is_ogretmenligi_ders_programi.xlsx")
    ) == "Resim Is Ogretmenligi"
    assert _infer_department_from_filename(
        Path("25_26_bahar_sinif_egt_ders_prog.pdf")
    ) == "Sinif Ogretmenligi"
    assert _infer_department_from_filename(
        Path("2526baharfizikson.pdf")
    ) is None


def test_source_override_supplies_context_for_compact_schedule_filename():
    override = _source_override_for(Path("2526baharfizikson.pdf"))

    assert override["academic_year"] == "2025-2026"
    assert override["term"] == "bahar"
    assert override["department"] == "Fizik Eğitimi"

    academic_year, term, department, source_url, skip = _merge_source_override(
        Path("2526baharfizikson.pdf"),
        academic_year=None,
        term=None,
        department=None,
        source_url=None,
    )

    assert academic_year == "2025-2026"
    assert term == "bahar"
    assert department == "Fizik Eğitimi"
    assert source_url is None
    assert skip is False


def test_explicit_ingest_context_takes_precedence_over_source_override():
    academic_year, term, department, _, _ = _merge_source_override(
        Path("2526baharfizikson.pdf"),
        academic_year="2024-2025",
        term="guz",
        department="Fizik",
        source_url=None,
    )

    assert academic_year == "2024-2025"
    assert term == "guz"
    assert department == "Fizik"


def test_classify_schedule_document_distinguishes_weekly_and_catalog_sources():
    weekly = classify_schedule_document(
        "insaat_program.pdf",
        "OMU INSAAT BOLUMU 2025-2026 BAHAR HAFTALIK DERS PROGRAMI Pazartesi 08:15-09:00",
    )
    catalog = classify_schedule_document(
        "kimya_lisans.pdf",
        "KIMYA BOLUMU LISANS PROGRAMI 2024-2025 DERSIN KODU DERSIN ADI AKTS",
    )

    assert weekly == "weekly_schedule"
    assert catalog == "non_weekly_program"
