from datetime import time
from pathlib import Path

from src.db.schedule_ingest import (
    classify_schedule_document,
    _normalize_day_label,
    infer_schedule_context,
    parse_schedule_table,
)


def test_normalize_day_label_handles_vertical_reversed_text():
    assert _normalize_day_label("i\ns\ne\ntr\na\nz\na\nP") == "Pazartesi"
    assert _normalize_day_label("Çarşamba") == "Carsamba"


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
