from types import SimpleNamespace

from src.db.schedule_data import (
    _department_match_key,
    _schedule_sort_key,
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
