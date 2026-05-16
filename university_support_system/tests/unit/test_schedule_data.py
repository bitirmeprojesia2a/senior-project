from types import SimpleNamespace

from src.db.schedule_data import (
    _department_match_key,
    _schedule_sort_key,
    format_schedule_course_name,
    format_schedule_day,
    format_schedule_group,
    format_schedule_label,
    normalize_schedule_rows_for_answer,
    schedule_row_sort_key,
)


def test_department_match_key_normalizes_punctuation_and_suffixes():
    assert _department_match_key("Elektrik-Elektronik Mühendisliği Bölümü") == _department_match_key(
        "Elektrik Elektronik Muhendisligi"
    )
    assert _department_match_key("Fizik Programı") == _department_match_key("Fizik")


def test_schedule_sort_key_uses_weekday_order_before_time():
    rows = [
        SimpleNamespace(
            day_of_week="Carsamba",
            start_time="08:15:00",
            schedule_group="",
            course_key="C",
            section="",
        ),
        SimpleNamespace(
            day_of_week="Pazartesi",
            start_time="13:15:00",
            schedule_group="",
            course_key="A",
            section="",
        ),
        SimpleNamespace(
            day_of_week="Sali",
            start_time="09:15:00",
            schedule_group="",
            course_key="B",
            section="",
        ),
    ]

    sorted_rows = sorted(rows, key=_schedule_sort_key)

    assert [row.day_of_week for row in sorted_rows] == ["Pazartesi", "Sali", "Carsamba"]


def test_schedule_row_sort_key_matches_serialized_schedule_rows():
    rows = [
        {"day_of_week": "Cuma", "start_time": "08:15:00", "schedule_group": "", "course_key": "C"},
        {"day_of_week": "Pazartesi", "start_time": "13:15:00", "schedule_group": "", "course_key": "A"},
        {"day_of_week": "Carsamba", "start_time": "09:15:00", "schedule_group": "", "course_key": "B"},
    ]

    sorted_rows = sorted(rows, key=schedule_row_sort_key)

    assert [row["day_of_week"] for row in sorted_rows] == ["Pazartesi", "Carsamba", "Cuma"]


def test_normalize_schedule_rows_excludes_graduate_other_rows_by_default():
    rows = [
        {
            "department": "Elektrik-Elektronik Muhendisligi",
            "course_name": "Matematik II",
            "schedule_group": "1. Sinif",
            "day_of_week": "Pazartesi",
            "start_time": "08:15:00",
            "term": "Bahar",
        },
        {
            "department": "Elektrik-Elektronik Muhendisligi",
            "course_name": "Uzmanlik Alan Dersi II",
            "schedule_group": None,
            "day_of_week": "Pazartesi",
            "start_time": "08:00:00",
            "term": "Bahar",
        },
    ]

    filtered, metadata = normalize_schedule_rows_for_answer(rows, query_text="Ders programi ne?")

    assert [row["course_name"] for row in filtered] == ["Matematik II"]
    assert metadata["excluded_rows"] == 1


def test_schedule_display_helpers_naturalize_legacy_ascii_and_english_labels():
    assert format_schedule_label("Elektrik-Elektronik Muhendisligi") == "Elektrik-Elektronik Mühendisliği"
    assert format_schedule_day("Carsamba") == "Çarşamba"
    assert format_schedule_group("2. Sinif") == "2. Sınıf"
    assert format_schedule_course_name("Computer Programming (Lab)") == "Bilgisayar Programlama (Lab)"
    assert (
        format_schedule_course_name("Fundamentals of Electrical Engineering (Lab)")
        == "Elektrik Mühendisliği Temelleri (Lab)"
    )


def test_normalize_schedule_rows_derives_physics_teacher_groups_and_cleans_names():
    rows = [
        {
            "department": "Fizik Egitimi",
            "course_name": "Öğretmen lik Uygula ması 2",
            "schedule_group": None,
            "section": "FZK4",
            "day_of_week": "Sali",
            "start_time": "08:15:00",
            "term": "Bahar",
        },
        {
            "department": "Fizik Egitimi",
            "course_name": "Fizik Öğretimin de Laboratuvar Uyg. II",
            "schedule_group": None,
            "section": "FZK3",
            "day_of_week": "Carsamba",
            "start_time": "13:00:00",
            "term": "Bahar",
        },
    ]

    filtered, _ = normalize_schedule_rows_for_answer(rows, query_text="Fizik ogretmenligi ders programi")

    assert {row["schedule_group"] for row in filtered} == {"3. Sinif", "4. Sinif"}
    assert filtered[0]["course_name"] != "Öğretmen lik Uygula ması 2"
    assert all("Öğretimin de" not in row["course_name"] for row in filtered)
