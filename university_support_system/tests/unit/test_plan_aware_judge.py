from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.quality.judge import run_judge


@pytest.mark.asyncio
async def test_judge_runs_for_plan_contract_even_when_answer_is_not_otherwise_risky():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "approved": False,
            "action": "retrieve_again",
            "failure_reason": "answer contract missing eligibility detail",
            "missing_intents": ["eligibility"],
            "suggested_query": "tek ders hic alinmamis ders devam sarti",
            "retry_plan": {
                "capability": "student_affairs.policy_lookup",
                "query": "tek ders hic alinmamis ders devam sarti",
                "reason": "missing eligibility evidence",
            },
        }
    )

    result = await run_judge(
        query="Hic almadigim bir dersten tek derse girebilir miyim?",
        answer="Tek ders hakkinda bilgi verilebilir.",
        evidence_summary="Tek ders sinavi genel kurallari.",
        plan_decision={
            "capability": "student_affairs.policy_lookup",
            "intent": "single_exam_eligibility",
        },
        answer_contract={"must_answer": ["hic alinmamis ders", "devam sarti"]},
        evidence_contract={"preferred_sources": ["sik_sorulan_sorular"]},
        llm_service=llm_service,
    )

    assert result is not None
    assert result.action == "retrieve_again"
    assert result.retry_plan["capability"] == "student_affairs.policy_lookup"
    prompt = llm_service.generate.await_args.kwargs["prompt"]
    assert "answer_contract" in prompt
    assert "hic alinmamis ders" in prompt


@pytest.mark.asyncio
async def test_judge_can_be_forced_by_deterministic_validator():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "approved": False,
            "action": "rewrite_only",
            "failure_reason": "validator found a missing evidence value",
        }
    )

    result = await run_judge(
        query="CAP icin not ortalamasi kac olmali?",
        answer="Kaynakta net bilgi yok.",
        evidence_summary="Deterministic validator status: fail",
        llm_service=llm_service,
        force=True,
        validator_result={
            "status": "fail",
            "missing_values": ["3,00"],
            "reason": "answer_denies_available_evidence",
        },
    )

    assert result is not None
    assert result.action == "rewrite_only"
    prompt = llm_service.generate.await_args.kwargs["prompt"]
    assert "forced_by_validator" in prompt
    assert "3,00" in prompt


@pytest.mark.asyncio
async def test_judge_runs_for_answer_coverage_check_even_without_other_risk():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "approved": False,
            "action": "rewrite_only",
            "failure_reason": "payment process part is missing",
            "missing_intents": ["payment_process"],
        }
    )

    result = await run_judge(
        query="Harc borcumu nasil odeyebilirim?",
        answer="Basvuru kosullari aciklanmistir.",
        evidence_summary="Harc odeme sureci kaynaklarda acik degil.",
        llm_service=llm_service,
        answer_coverage_result={
            "status": "check",
            "expected_facet": "payment_process",
            "reason": "answer_missing_payment_process_markers",
        },
    )

    assert result is not None
    assert result.action == "rewrite_only"
    prompt = llm_service.generate.await_args.kwargs["prompt"]
    assert "answer_coverage_needs_check" in prompt
    assert "payment_process" in prompt


@pytest.mark.asyncio
async def test_judge_parse_failure_is_not_approved():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(return_value="judge failed to return json")

    result = await run_judge(
        query="CAP icin not ortalamasi kac olmali?",
        answer="CAP icin not ortalamasi bilgisi verilebilir.",
        evidence_summary="CAP kosullari kaynaklarda yer aliyor.",
        llm_service=llm_service,
        force=True,
    )

    assert result is not None
    assert result.approved is False
    assert result.action == "rewrite_only"
    assert result.failure_reason == "judge_response_parse_failed"
