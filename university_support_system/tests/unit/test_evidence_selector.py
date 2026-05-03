"""Tests for the optional LLM evidence selector."""

from __future__ import annotations

import json

from src.core.config import settings
from src.quality.evidence import EvidenceItem
from src.quality.evidence_selector import select_evidence_with_llm


class FakeLLMService:
    def __init__(self, payload: str):
        self.payload = payload
        self.calls: list[dict] = []

    async def generate(self, **kwargs) -> str:
        self.calls.append(kwargs)
        return self.payload


def _item(source_id: str, source_name: str, text: str, *, score: float = 0.5) -> EvidenceItem:
    return EvidenceItem(
        source_name=source_name,
        source_id=source_id,
        department="student_affairs",
        score=score,
        score_type="reranker",
        content_snippet=text,
        selected_sentences=text,
        matched_query_terms=["final"],
        relevance_score=score,
        extracted_facts=[],
        source_rank=1,
    )


async def test_evidence_selector_uses_llm_choice(monkeypatch):
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_enabled", True)
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_min_candidates", 2)
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_max_candidates", 3)

    first = _item("a", "generic.pdf", "Sinavlar hakkinda genel yonetmelik bilgisi.", score=0.62)
    second = _item(
        "b",
        "2025_2026_genel_akademik_takvim.pdf",
        "Yariyil Sonu Sinav Sonuclarinin Internetten Girilmesinin Son Gunu 16 Haziran 2026.",
        score=0.58,
    )
    fake_llm = FakeLLMService(
        json.dumps(
            {
                "selected_ids": ["b"],
                "ranking": [{"source_id": "b", "answer_usefulness": 0.95, "reason": "direct date"}],
                "reason": "calendar source has the exact deadline",
            }
        )
    )

    selected, decision = await select_evidence_with_llm(
        "Final sinav sonuclarinin sisteme girilmesinin son gunu ne zaman?",
        [first, second],
        fake_llm,
        max_selected=2,
    )

    assert decision.used_llm is True
    assert decision.status == "selected"
    assert selected[0].source_id == "b"
    assert [item.source_id for item in selected] == ["b", "a"]
    assert fake_llm.calls[0]["model_role"] == "evidence_selection"
    assert fake_llm.calls[0]["json_mode"] is True


async def test_evidence_selector_falls_back_on_invalid_json(monkeypatch):
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_enabled", True)
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_min_candidates", 2)

    items = [
        _item("a", "first.pdf", "Birinci kaynak."),
        _item("b", "second.pdf", "Ikinci kaynak."),
    ]

    selected, decision = await select_evidence_with_llm(
        "Soru",
        items,
        FakeLLMService("not json"),
        max_selected=2,
    )

    assert selected == items
    assert decision.used_llm is False
    assert decision.status == "fallback_error"


async def test_evidence_selector_falls_back_when_llm_returns_unknown_ids(monkeypatch):
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_enabled", True)
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_min_candidates", 2)

    items = [
        _item("a", "first.pdf", "Birinci kaynak."),
        _item("b", "second.pdf", "Ikinci kaynak."),
    ]
    fake_llm = FakeLLMService(json.dumps({"selected_ids": ["missing"], "ranking": []}))

    selected, decision = await select_evidence_with_llm(
        "Soru",
        items,
        fake_llm,
        max_selected=2,
    )

    assert selected == items
    assert decision.used_llm is False
    assert decision.status == "fallback_empty_selection"
    assert decision.selected_ids == ["missing"]


async def test_evidence_selector_can_reject_all_candidates(monkeypatch):
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_enabled", True)
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_min_candidates", 2)

    items = [
        _item("a", "staj.pdf", "Staj raporu teslim sureci."),
        _item("b", "itiraz.pdf", "Sinav sonucuna itiraz dilekceyle yapilir."),
    ]
    fake_llm = FakeLLMService(
        json.dumps(
            {
                "insufficient_evidence": True,
                "selected_ids": [],
                "ranking": [],
                "reason": "No candidate says where grades can be viewed.",
            }
        )
    )

    selected, decision = await select_evidence_with_llm(
        "Sinav notlarimi nereden gorebilirim?",
        items,
        fake_llm,
        max_selected=2,
    )

    assert selected == []
    assert decision.used_llm is True
    assert decision.status == "insufficient_evidence"
    assert decision.candidate_count == 2


async def test_evidence_selector_skips_when_disabled(monkeypatch):
    monkeypatch.setattr(settings.rag, "llm_evidence_selection_enabled", False)
    items = [_item("a", "first.pdf", "Birinci kaynak.")]

    selected, decision = await select_evidence_with_llm(
        "Soru",
        items,
        FakeLLMService("{}"),
        max_selected=1,
    )

    assert selected == items
    assert decision.used_llm is False
    assert decision.status == "disabled"
