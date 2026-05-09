"""Tuition utility tests."""

import json
from pathlib import Path

from src.agents.finance.tuition_utils import (
    extract_requested_unit,
    has_explicit_program_without_fee_unit,
    is_explicit_fee_amount_query,
    is_personal_query,
    is_structured_fee_query,
    needs_fee_context_clarification,
)


def test_is_personal_query_treats_installment_policy_question_as_non_personal():
    assert is_personal_query("Taksitle odeyebilir miyim?") is False


def test_is_personal_query_keeps_real_personal_balance_question_personal():
    assert is_personal_query("Harc borcum var mi?") is True


def test_is_personal_query_keeps_personal_amount_question_personal():
    assert is_personal_query("Harc borcum ne kadar?") is True


def test_is_personal_query_treats_transfer_fee_policy_question_as_non_personal():
    assert is_personal_query("Yatay gecis yaparsam harc odemem gerekir mi?") is False


def test_explicit_fee_amount_query_rejects_application_policy_context():
    assert (
        is_explicit_fee_amount_query("Harc borcum olsaydi CAP'a basvurabilir miydim?")
        is False
    )


def test_explicit_fee_amount_query_accepts_program_fee_amount_context():
    assert is_explicit_fee_amount_query("Fizik ogretmenligi ucreti ne kadar?") is True


def test_extract_requested_unit_accepts_faculty_alias_without_suffix():
    assert extract_requested_unit("Dis hekimligi donem ucreti Turk ogrenci icin ne kadar?") == "dis hekimligi fakultesi"


def test_extract_requested_unit_maps_engineering_department_to_faculty():
    assert (
        extract_requested_unit("Elektrik elektronik muhendisligi ogrenim ucreti ne kadar?")
        == "muhendislik fakultesi"
    )


def test_extract_requested_unit_maps_teaching_program_to_education_faculty():
    assert (
        extract_requested_unit("Fizik ogretmenligi ucreti ne kadar?")
        == "egitim fakultesi"
    )


def test_explicit_program_without_fee_unit_blocks_profile_unit_fallback():
    assert has_explicit_program_without_fee_unit("Fizik ogretmenligi ucreti ne kadar?") is False
    assert has_explicit_program_without_fee_unit("Elektrik elektronik muhendisligi ucreti ne kadar?") is False


def test_meal_fee_does_not_trigger_tuition_clarification():
    query = "Yemekhane ucreti ne kadar?"

    assert is_structured_fee_query(query) is False
    assert needs_fee_context_clarification(query, None, None) is False


def test_tuition_fee_catalog_includes_dentistry_rows():
    path = Path("data/metadata/tuition_fee_catalog.json")
    rows = json.loads(path.read_text(encoding="utf-8"))
    indexed = {
        (row["student_type"], row["unit_name"]): row
        for row in rows
    }

    assert indexed[("domestic", "Diş Hekimliği Fakültesi")]["annual_amount"] == 3057.0
    assert indexed[("international", "Diş Hekimliği Fakültesi")]["annual_amount"] == 203000.0
