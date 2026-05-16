"""Tuition utility tests."""

import json
from pathlib import Path

from src.agents.finance.tuition_utils import (
    blocks_regular_tuition_catalog,
    extract_requested_unit,
    has_explicit_program_without_fee_unit,
    infer_fee_scope,
    is_explicit_fee_amount_query,
    is_other_fee_query,
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


def test_summer_school_fee_does_not_use_regular_tuition_catalog():
    query = "Yaz okulu ucreti ne kadar?"

    assert infer_fee_scope(query) == "summer_school_fee"
    assert blocks_regular_tuition_catalog(query) is True
    assert is_explicit_fee_amount_query(query) is False
    assert is_structured_fee_query(query) is False
    assert needs_fee_context_clarification(query, None, None) is False


def test_cap_and_erasmus_fee_questions_do_not_use_regular_tuition_catalog():
    assert infer_fee_scope("CAP programinda ders ucreti ayrica odenir mi?") == "cap_extra_fee"
    assert blocks_regular_tuition_catalog("Erasmus ogrencisi yaz okulu ucreti ne kadar?") is True
    assert is_explicit_fee_amount_query("CAP programinda ders ucreti ayrica odenir mi?") is False
    assert is_explicit_fee_amount_query("Erasmus ogrencisi yaz okulu ucreti ne kadar?") is False


def test_other_fee_follow_up_does_not_reenter_tuition_amount_slot_loop():
    query = "Baska ucret var mi?"

    assert is_other_fee_query(query) is True
    assert infer_fee_scope(query) == "other_fee_policy"
    assert is_explicit_fee_amount_query(query) is False
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
