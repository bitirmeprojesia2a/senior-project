"""Curriculum utility tests."""

from src.agents.academic.curriculum_utils import infer_department_from_query
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
