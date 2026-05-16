from __future__ import annotations

from src.core.constants import Department
from src.db.schemas import DepartmentResponse
from src.quality.answer_value_conflict import validate_answer_value_conflicts


def test_value_conflict_flags_competing_gpa_thresholds() -> None:
    result = validate_answer_value_conflicts(
        query="Peki not ortalamasi kac olmali?",
        answer=(
            "Not ortalamasinin 4,00 uzerinden en az 2,00 olmasi zorunludur. "
            "Bazi durumlarda ana dal not ortalamasi 4,00 uzerinden en az 3,00 olmasi gerekir. "
            "Ortalama en fazla 2,50'ye kadar dusebilir."
        ),
    )

    assert result.status == "check"
    assert result.reason == "multiple_competing_threshold_values"
    assert result.primary_answer_value == "2,00"
    assert result.competing_values == ["3,00", "2,50"]


def test_value_conflict_passes_single_cap_gpa_threshold_with_scale_and_percent() -> None:
    result = validate_answer_value_conflicts(
        query="Peki not ortalamasi kac olmali?",
        answer=(
            "CAP basvurusu icin ana dal not ortalamasi 4,00 uzerinden en az 3,00 "
            "olmalidir; ayrica basari siralamasinda ilk %20 sarti aranir."
        ),
    )

    assert result.status == "pass"
    assert result.primary_answer_value == "3,00"
    roles = {role.value: role.role for role in result.value_roles}
    assert roles["4,00"] == "scale_value"
    assert roles["3,00"] == "answer_threshold"
    assert roles["%20"] == "related_condition"


def test_value_conflict_checks_primary_answer_against_evidence_threshold() -> None:
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "facts": [
                    {
                        "claim": (
                            "Ana dal not ortalamasinin 4,00 uzerinden en az 3,00 "
                            "olmasi ve basari siralamasi itibari ile en az ilk % 20'sinde "
                            "bulunmasi gerekir."
                        ),
                        "source": "yonerge_cift_anadal_yandal.pdf",
                        "policy_alignment": {
                            "status": "match",
                            "matched_programs": ["double_major"],
                        },
                    }
                ]
            }
        },
    )

    result = validate_answer_value_conflicts(
        query="Peki not ortalamasi kac olmali?",
        answer="Not ortalamasinin 4,00 uzerinden en az 2,00 olmasi sarttir.",
        responses=[response],
    )

    assert result.status == "check"
    assert result.reason == "answer_primary_value_conflicts_with_evidence"
    assert result.primary_answer_value == "2,00"
    assert result.competing_values == ["3,00"]


def test_value_conflict_passes_yandal_threshold_when_question_targets_yandal() -> None:
    result = validate_answer_value_conflicts(
        query="Yandal icin not ortalamasi kac olmali?",
        answer="Yandal icin not ortalamasi 4,00 uzerinden en az 2,00 olmalidir.",
    )

    assert result.status == "pass"
    assert result.primary_answer_value == "2,00"


def test_value_conflict_skips_calendar_multi_date_answers() -> None:
    result = validate_answer_value_conflicts(
        query="Final sinavlari ne zaman basliyor?",
        answer="Guz donemi finalleri 5 Ocak, bahar donemi finalleri 10 Haziran tarihinde baslar.",
    )

    assert result.status == "skipped"
    assert result.aspect is None


def test_value_conflict_skips_akts_credit_answers() -> None:
    result = validate_answer_value_conflicts(
        query="BIL203 dersinin AKTS'si ve kredisi nedir?",
        answer="BIL203 dersi 5 AKTS ve 3 kredidir.",
    )

    assert result.status == "skipped"


def test_value_conflict_skips_fee_answers() -> None:
    result = validate_answer_value_conflicts(
        query="Harc ucreti ne kadar?",
        answer="Ikinci ogretim harc ucreti 5.000,00 TL'dir.",
    )

    assert result.status == "skipped"
