"""Claim guard regression tests."""

from src.quality.claim_guard import guard_answer
from src.quality.evidence import extract_evidence_items


def _evidence_item(content: str, *, source: str = "kaynak.pdf"):
    source_obj = {"content": content, "source": source, "score": 0.9, "metadata": {"source": source}}
    return extract_evidence_items("test sorgusu", [source_obj], "student_affairs")[0]


def test_claim_guard_rewrites_simple_staj_duration_arithmetic_error():
    answer = (
        "20 günlük 2 farklı staj, toplam 30 iş gününe ulaşırsa kabul edilebilir. "
        "Resmi tatil günleri staj süresinden sayılmaz."
    )
    evidence = [
        _evidence_item(
            "Zorunlu staj toplam 30 iş günüdür. Resmi tatil günleri staj süresinden sayılmaz."
        )
    ]

    result = guard_answer(answer, evidence)

    assert result.modifications_made >= 1
    assert "toplam gün hesabı 40 gündür" in result.cleaned_answer
    assert "toplam 30 iş gününe ulaşırsa kabul edilebilir" not in result.cleaned_answer
    assert any(issue["type"] == "arithmetic" for issue in result.unsupported_claims)


def test_claim_guard_softens_tek_ders_attendance_contradiction():
    answer = (
        "Tek ders sınavları, akademik takvimde belirtilen tarihlerde Üniversitede açılır. "
        "Bu sınavlara, dersi hiç almamış olan veya devam şartını yerine getiremeyen öğrenciler girebilir."
    )
    evidence = [
        _evidence_item(
            "Tek ders sınavına, mezuniyet için tek dersi kalan ve bu dersten daha önce devam şartını yerine getirdiği halde başarısız olan öğrenci başvurabilir."
        )
    ]

    result = guard_answer(answer, evidence)

    assert result.modifications_made >= 1
    assert "dersi hiç almamış olan" not in result.cleaned_answer
    assert "devam şartını daha önce sağlamış" in result.cleaned_answer
    assert any(issue["type"] == "policy_contradiction" for issue in result.unsupported_claims)
