"""Curriculum utility tests."""

from src.agents.academic.curriculum_utils import (
    extract_schedule_groups,
    extract_curriculum_semester,
    infer_department_from_query,
    is_course_list_query,
    is_prerequisite_query,
)
from src.core.text_normalization import normalize_text


def _normalized_inferred(query: str) -> str:
    inferred = infer_department_from_query(query)
    assert inferred is not None
    return normalize_text(inferred)


def test_infer_department_prefers_specific_education_programs():
    assert _normalized_inferred("Fizik egitimi ders programi var mi?") == "fizik egitimi"
    assert _normalized_inferred("Biyoloji egitimi ders programi var mi?") == "biyoloji egitimi"


def test_infer_department_supports_short_department_names():
    assert _normalized_inferred("Biyoloji ders programi var mi?") == "biyoloji"
    assert _normalized_inferred("Matematik ders programi var mi?") == "matematik"


def test_infer_department_supports_preschool_education_program():
    assert (
        _normalized_inferred("Okul oncesi ogretmenligi ders programi var mi?")
        == "okul oncesi ogretmenligi"
    )


def test_extract_curriculum_semester_maps_class_year_and_term():
    assert (
        extract_curriculum_semester(
            "Bilgisayar muhendisligi 4. sinif ilk donem dersleri hakkinda bilgi"
        )
        == 7
    )
    assert extract_curriculum_semester("4. sinif ikinci donem dersleri neler?") == 8


def test_extract_curriculum_semester_accepts_locative_suffix():
    assert extract_curriculum_semester("Bilgisayar muhendisligi 5. yariyildaki dersler neler?") == 5


def test_course_list_query_accepts_dersleri_hakkinda_variants():
    assert is_course_list_query(
        normalize_text("4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum")
    )
    assert is_course_list_query(normalize_text("dersler neler"))


def test_extract_schedule_groups_maps_curriculum_semester_to_class_group():
    groups = extract_schedule_groups(normalize_text("Bilgisayar Muhendisligi 7. yariyil ders programi"))

    assert "4. SINIF" in groups
    assert "IV" in groups


def test_prerequisite_query_accepts_natural_language_course_dependency_question():
    assert is_prerequisite_query(
        normalize_text("Veri Yapilari dersini alabilmek icin hangi dersi almam gerekiyor?")
    )
    assert not is_prerequisite_query(normalize_text("Yaz okulunda ders alabilmek icin sartlar nelerdir?"))
