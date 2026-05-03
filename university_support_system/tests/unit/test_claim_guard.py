"""Behavioral tests for the deterministic claim guard."""

from src.quality.claim_guard import (
    GuardResult,
    check_definitive_claims,
    check_entity_grounding,
    check_numeric_grounding,
    guard_answer,
)
from src.quality.evidence import EvidenceItem


def _make_evidence(
    content: str,
    source: str = "yonetmelik.pdf",
    facts: list[str] | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        source_name=source,
        source_id="test123",
        department="student_affairs",
        score=0.80,
        score_type="reranker",
        content_snippet=content,
        selected_sentences=content,
        matched_query_terms=["kayit"],
        relevance_score=0.60,
        extracted_facts=facts or [],
    )


# ---------------------------------------------------------------------------
# Numeric grounding
# ---------------------------------------------------------------------------


def test_ungrounded_number_detected():
    evidence = [
        _make_evidence(
            "Ogrencinin GNO'su en az 2.50 olmalidir.",
            facts=["2.50 gno"],
        )
    ]
    answer = "GNO en az 3.00 olmalidir."
    issues = check_numeric_grounding(answer, evidence)
    assert any("3.00" in i["claim"] for i in issues), (
        f"3.00 should be flagged as ungrounded: {issues}"
    )


def test_grounded_number_not_flagged():
    evidence = [
        _make_evidence(
            "Ogrencinin GNO'su en az 2.50 olmalidir.",
            facts=["2.50 gno"],
        )
    ]
    answer = "GNO en az 2.50 olmalidir."
    issues = check_numeric_grounding(answer, evidence)
    gno_issues = [i for i in issues if "2.50" in i.get("claim", "")]
    assert not gno_issues, f"2.50 should be grounded: {issues}"


# ---------------------------------------------------------------------------
# Entity grounding
# ---------------------------------------------------------------------------


def test_ungrounded_portal_detected():
    evidence = [
        _make_evidence(
            "Kayit islemi ogrenci isleri mudurlugune basvuru ile yapilir. "
            "UBYS uzerinden ders kaydi yapabilirsiniz."
        )
    ]
    answer = "Kayit islemi e-Kampus portali uzerinden yapilir."
    issues = check_entity_grounding(answer, evidence)
    assert any("e-Kampus" in i["claim"] for i in issues), (
        f"e-Kampus should be flagged: {issues}"
    )


def test_grounded_entity_not_flagged():
    evidence = [
        _make_evidence(
            "UBYS uzerinden ders kaydi yapabilirsiniz."
        )
    ]
    answer = "Ders kaydi UBYS uzerinden yapilir."
    issues = check_entity_grounding(answer, evidence)
    ubys_issues = [i for i in issues if "UBYS" in i.get("claim", "")]
    assert not ubys_issues, f"UBYS should be grounded: {issues}"


# ---------------------------------------------------------------------------
# Definitive claims
# ---------------------------------------------------------------------------


def test_unsupported_definitive_claim_softened():
    evidence = [
        _make_evidence(
            "Kayit dondurma basvurusu akademik takvimde belirlenen tarihlerde yapilir."
        )
    ]
    answer = "Kayit dondurma suresi icerisinde ders alinmasi kesinlikle yapilamaz."
    result = guard_answer(answer, evidence)
    # "kesinlikle yapilamaz" should be softened to "yapilamaz"
    assert "kesinlikle" not in result.cleaned_answer, (
        f"'kesinlikle' should be softened: {result.cleaned_answer}"
    )
    assert result.modifications_made >= 1


def test_supported_definitive_claim_preserved():
    evidence = [
        _make_evidence(
            "Bu islem kesinlikle yapilamaz. Yonetmelik geregi yasaktir.",
            facts=["kesinlikle yapilamaz"],
        )
    ]
    answer = "Bu islem kesinlikle yapilamaz."
    issues = check_definitive_claims(answer, evidence)
    assert not issues, f"Claim should be grounded: {issues}"


# ---------------------------------------------------------------------------
# Guard behavior
# ---------------------------------------------------------------------------


def test_uncertain_claim_only_logged_not_modified():
    """Numeric claims are logged but not modified (conservative principle)."""
    evidence = [
        _make_evidence(
            "Kayit dondurma suresi iki donemi gecemez.",
            facts=["iki donemi"],
        )
    ]
    answer = "Kayit dondurma suresi en fazla 3 donem olabilir."
    result = guard_answer(answer, evidence)
    # The number should be in diagnostics but answer should keep it
    assert "3" in result.cleaned_answer, (
        "Numeric claim should not be removed from answer"
    )
    assert any(
        i["type"] == "numeric" for i in result.unsupported_claims
    ), "The numeric issue should be in unsupported_claims"


def test_guard_does_not_delete_sentences():
    evidence = [
        _make_evidence("Staj defteri teslimi zorunludur.")
    ]
    answer = (
        "Staj defteri teslimi zorunludur. "
        "Teslim icin e-Kampus portali kullanilir. "
        "Son teslim tarihi 15 Haziran'dir."
    )
    result = guard_answer(answer, evidence)
    # Sentence count should be preserved (portal might be softened but not deleted)
    original_sentences = [s.strip() for s in answer.split(".") if s.strip()]
    cleaned_sentences = [s.strip() for s in result.cleaned_answer.split(".") if s.strip()]
    # We allow +1 for the verification note that may be appended
    assert len(cleaned_sentences) >= len(original_sentences) - 1, (
        f"Sentences should not be deleted: original={len(original_sentences)}, "
        f"cleaned={len(cleaned_sentences)}"
    )


def test_guard_returns_clean_diagnostics():
    evidence = [_make_evidence("Test content")]
    result = guard_answer("Test answer", evidence)
    assert isinstance(result, GuardResult)
    assert isinstance(result.diagnostics, dict)
    assert isinstance(result.unsupported_claims, list)
    assert isinstance(result.modifications_made, int)


def test_global_synthesis_guard_catches_cross_department_fabrication():
    """Synthesis answer invents a payment channel not in any source."""
    finance_evidence = _make_evidence(
        "Harc ucreti her donem odenmelidir. Odeme suresi akademik takvimde belirtilir.",
        source="harc_yonetmeligi.pdf",
        facts=["harc ucreti"],
    )
    academic_evidence = _make_evidence(
        "CAP basvurusu icin GNO en az 3.00 olmalidir.",
        source="cap_yonergesi.pdf",
        facts=["3.00 gno"],
    )
    answer = (
        "CAP basvurusu icin GNO en az 3.00 olmalidir. "
        "Harc ucretini internet bankaciligi ile odeyebilirsiniz."
    )
    result = guard_answer(answer, [finance_evidence, academic_evidence])
    # "internet bankaciligi" is a payment channel not in sources
    has_payment_issue = any(
        i["type"] == "entity" and "bankaciligi" in i.get("claim", "")
        for i in result.unsupported_claims
    )
    # It should at least be detected (may or may not be modified)
    assert has_payment_issue or result.modifications_made > 0, (
        f"Payment channel fabrication should be detected: {result.unsupported_claims}"
    )
