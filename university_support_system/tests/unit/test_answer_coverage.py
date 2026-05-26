from src.quality.answer_coverage import validate_answer_coverage
from src.core.constants import Department
from src.db.schemas import DepartmentResponse, RAGSource


def test_answer_coverage_flags_process_question_answered_as_eligibility_only():
    result = validate_answer_coverage(
        query="CAP basvurusu nasil yapilir?",
        answer="CAP icin GANO en az 3,00 olmali ve mezuniyet kosullari saglanmalidir.",
        responses=[],
    )

    assert result.status == "check"
    assert result.expected_facet == "application_process"
    assert result.reason == "answer_missing_process_markers"
    assert result.positive_markers == []


def test_answer_coverage_uses_evidence_text_separately_for_process_drift():
    result = validate_answer_coverage(
        query="CAP basvurusu nasil yapilir?",
        answer="CAP icin GANO en az 3,00 olmali.",
        responses=[
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="",
                sources=[
                    RAGSource(
                        content="",
                        score=0.8,
                        metadata={
                            "supporting_claims": [
                                "Basvuru form ve belgelerle ogrenci islerine yapilir."
                            ]
                        },
                    )
                ],
            )
        ],
    )

    assert result.status == "check"
    assert result.reason == "answer_drifted_to_eligibility_while_process_evidence_exists"
    assert result.positive_markers


def test_answer_coverage_passes_process_answer_with_application_markers():
    result = validate_answer_coverage(
        query="CAP basvurusu nasil yapilir?",
        answer="Basvuru duyurudaki tarihlerde form ve belgelerle ogrenci islerine yapilir.",
        responses=[],
    )

    assert result.status == "pass"
    assert result.expected_facet == "application_process"


def test_answer_coverage_passes_gpa_followup_when_eligibility_value_present():
    result = validate_answer_coverage(
        query="Peki not ortalamasi kac olmali?",
        answer="CAP basvurusu icin GANO en az 3,00 olmalidir.",
        responses=[],
    )

    assert result.status == "pass"
    assert result.expected_facet == "eligibility_value"


def test_answer_coverage_flags_missing_payment_process_in_compound_question():
    result = validate_answer_coverage(
        query="CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?",
        answer=(
            "CAP basvurusu icin genel kosullar: ana dal not ortalamasi en az "
            "3,00 olmali ve basari siralamasinda ilk yuzde 20 icinde olunmalidir."
        ),
        responses=[],
    )

    assert result.status == "check"
    assert result.expected_facet == "payment_process"
    assert result.reason == "answer_missing_payment_process_markers"


def test_answer_coverage_passes_payment_process_when_answer_addresses_no_info():
    result = validate_answer_coverage(
        query="CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?",
        answer=(
            "CAP kosullari kaynaklarda yer aliyor; harc borcunun odeme yontemi "
            "icin kaynaklarda net bilgi bulunamadi."
        ),
        responses=[],
    )

    assert result.status == "pass"
    assert result.expected_facet == "payment_process"


def test_answer_coverage_treats_payment_nasil_yapilir_as_payment_process():
    result = validate_answer_coverage(
        query="Harc odemesi nasil yapilir?",
        answer="Odeme yontemi kaynaklarda net bilgi bulunamadi.",
        responses=[],
    )

    assert result.status == "pass"
    assert result.expected_facet == "payment_process"
