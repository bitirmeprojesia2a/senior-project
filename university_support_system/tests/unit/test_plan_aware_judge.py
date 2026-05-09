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
