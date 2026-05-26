"""Tests for the optional LLM answer verifier."""

import asyncio
from unittest.mock import AsyncMock

import pytest

from src.quality.answer_verifier import (
    VerifierResult,
    _build_verifier_prompt,
    is_verifier_enabled,
    should_verify,
    verify_answer,
)
from src.quality.evidence import EvidenceItem


def _make_evidence(
    content: str = "Test content",
    score: float = 0.75,
) -> EvidenceItem:
    return EvidenceItem(
        source_name="test.pdf",
        source_id="abc",
        department="student_affairs",
        score=score,
        score_type="reranker",
        content_snippet=content,
        selected_sentences=content,
        matched_query_terms=["test"],
        relevance_score=0.50,
        extracted_facts=[],
    )


def test_verifier_disabled_by_default():
    assert is_verifier_enabled() is False


def test_should_verify_returns_false_when_disabled():
    items = [_make_evidence()]
    assert should_verify(items, global_synthesis_used=True, department_count=3) is False


def test_build_verifier_prompt_includes_answer_and_sources():
    items = [_make_evidence("Kayit islemi yapilir.")]
    prompt = _build_verifier_prompt("Test cevap", items)
    assert "Test cevap" in prompt
    assert "Kayit islemi yapilir" in prompt
    assert "JSON" in prompt


@pytest.mark.asyncio
async def test_verify_answer_returns_error_on_timeout():
    items = [_make_evidence()]
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(side_effect=asyncio.TimeoutError())
    result = await verify_answer("Test", items, llm_service, timeout=0.1)
    assert result.error == "timeout"
    assert result.verified is False


@pytest.mark.asyncio
async def test_verify_answer_parses_valid_json():
    items = [_make_evidence()]
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value='{"supported": ["iddia1"], "unsupported": ["iddia2"], "missing": ["bilgi1"]}'
    )
    result = await verify_answer("Test", items, llm_service, timeout=5.0)
    assert result.verified is True
    assert "iddia1" in result.supported_claims
    assert "iddia2" in result.unsupported_claims
    assert "bilgi1" in result.missing_info


@pytest.mark.asyncio
async def test_verify_answer_handles_malformed_json():
    items = [_make_evidence()]
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(return_value="Bu bir JSON degildir.")
    result = await verify_answer("Test", items, llm_service, timeout=5.0)
    assert result.error is not None
    assert "no_json" in result.error or "parse_error" in result.error


@pytest.mark.asyncio
async def test_verify_answer_returns_error_on_empty_evidence():
    llm_service = AsyncMock()
    result = await verify_answer("Test", [], llm_service, timeout=5.0)
    assert result.error == "no_evidence_items"
