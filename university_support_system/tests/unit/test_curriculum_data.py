from __future__ import annotations

from src.db.curriculum_data import _should_include_course_for_department, _title_tokens


def test_department_filter_excludes_other_department_elective_slots() -> None:
    course = {
        "department": "Elektrik-Elektronik Mühendisliği",
        "course_type": "secmeli_grup",
        "course_name": "Sosyal Seçmeli Dersler Grup-II",
    }

    assert not _should_include_course_for_department(
        course,
        "matematik ogretmenligi",
    )


def test_department_filter_keeps_shared_curriculum_courses() -> None:
    course = {
        "department": "Sosyal Secmeli",
        "course_type": "sosyal_secmeli",
        "course_name": "Kultur ve Sanat",
    }

    assert _should_include_course_for_department(
        course,
        "matematik ogretmenligi",
    )


def test_title_tokens_keep_course_name_but_drop_question_words() -> None:
    assert _title_tokens("Olasilik ve istatistige giris dersi hangi sinifta?") == {
        "olasilik",
        "istatistige",
        "giris",
    }
