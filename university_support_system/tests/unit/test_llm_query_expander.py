"""LLM query expansion tests."""

from __future__ import annotations

import json

import pytest

from src.core.config import settings
from src.rag.llm_query_expander import LLMQueryExpander


class _FakeLLMService:
    def __init__(self) -> None:
        self.calls = []

    async def generate(self, **kwargs):
        self.calls.append(kwargs)
        return json.dumps(
            {
                "expanded_query": "Staj başvurusu nasıl yapılır zorunlu staj formu staj komisyonu",
                "added_terms": ["zorunlu staj formu", "staj komisyonu"],
            },
            ensure_ascii=False,
        )


def test_llm_query_expander_disabled_by_default(monkeypatch):
    monkeypatch.setattr(settings.rag, "llm_query_expansion_enabled", False)

    expander = LLMQueryExpander(llm_service=_FakeLLMService())

    assert expander.expand("Staj başvurusu nasıl yapılır") is None


def test_llm_query_expander_uses_query_expansion_role(monkeypatch):
    fake_llm = _FakeLLMService()
    monkeypatch.setattr(settings.rag, "llm_query_expansion_enabled", True)
    monkeypatch.setattr(settings.rag, "llm_query_expansion_timeout_seconds", 5)
    monkeypatch.setattr(settings.rag, "llm_query_expansion_max_chars", 220)

    expander = LLMQueryExpander(llm_service=fake_llm)
    result = expander.expand(
        "Staj başvurusu nasıl yapılır",
        rule_expanded_query="Staj başvurusu nasıl yapılır",
    )

    assert result is not None
    assert "zorunlu staj formu" in result.expanded_query
    assert result.added_terms == ["zorunlu staj formu", "staj komisyonu"]
    assert fake_llm.calls[0]["model_role"] == "query_expansion"
    assert fake_llm.calls[0]["json_mode"] is True


@pytest.mark.asyncio
async def test_llm_query_expander_skips_inside_running_loop(monkeypatch):
    monkeypatch.setattr(settings.rag, "llm_query_expansion_enabled", True)

    expander = LLMQueryExpander(llm_service=_FakeLLMService())

    assert expander.expand("Staj başvurusu nasıl yapılır") is None
