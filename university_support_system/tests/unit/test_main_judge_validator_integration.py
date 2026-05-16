from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.core.constants import Department
from src.core.profiling import QueryProfiler, activate_profiler
from src.db.schemas import DepartmentResponse, RAGSource
from src.orchestrators.main import MainOrchestrator
from src.quality.evidence_answer_validator import validate_evidence_answer


def _response_with_cap_threshold() -> DepartmentResponse:
    claim = (
        "Ogrencinin CAP'a basvurabilmesi icin basvurusu sirasindaki ana dal "
        "not ortalamasinin 4,00 uzerinden en az 3,00 olmasi gerekir."
    )
    return DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[
            RAGSource(
                content=claim,
                score=0.9,
                metadata={"source": "yonerge_cift_anadal_yandal.pdf"},
            )
        ],
        metadata={
            "evidence_packet": {
                "specialist_response_mode": "evidence_packet",
                "final_answer_owner": "main_orchestrator",
                "answer_contract": {
                    "must_answer": ["not ortalamasi", "GNO kosulu"],
                },
                "facts": [
                    {
                        "claim": claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                    }
                ],
            }
        },
    )


@pytest.mark.asyncio
async def test_validator_forces_existing_main_judge_and_records_post_repair_status():
    query = "CAP icin not ortalamasi kac olmali?"
    bad_answer = "Kaynakta not ortalamasinin kac olacagi net degil."
    responses = [_response_with_cap_threshold()]
    initial_validation = validate_evidence_answer(
        query=query,
        answer=bad_answer,
        responses=responses,
        mode="contract_enforce",
    )
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        side_effect=[
            {
                "approved": False,
                "action": "rewrite_only",
                "failure_reason": "missing evidence value 3,00",
            },
            "CAP basvurusu icin ana dal not ortalamasinin en az 3,00 olmasi gerekir.",
        ]
    )
    orchestrator = MainOrchestrator(llm_service=llm_service)
    profiler = QueryProfiler(label="validator-main-judge")

    with activate_profiler(profiler):
        repaired = await orchestrator._apply_main_judge_gate(
            query=query,
            answer=bad_answer,
            responses=responses,
            answer_validation=initial_validation,
        )

    assert "3,00" in repaired
    assert llm_service.generate.await_count == 2
    attributes = profiler.snapshot()["attributes"]
    assert attributes["main_judge"]["triggered_by_validator"] is True
    assert attributes["evidence_answer_validator"]["status"] == "pass"
    assert attributes["evidence_answer_validator"]["pre_judge"]["status"] == "fail"


@pytest.mark.asyncio
async def test_main_judge_rejects_repair_that_loses_preserved_required_value():
    query = "CAP icin not ortalamasi kac olmali?"
    good_answer = "CAP basvurusu icin ana dal not ortalamasinin en az 3,00 olmasi gerekir."
    responses = [_response_with_cap_threshold()]
    initial_validation = validate_evidence_answer(
        query=query,
        answer=good_answer,
        responses=responses,
    )
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        side_effect=[
            {
                "approved": False,
                "action": "rewrite_only",
                "failure_reason": "rewrite requested",
            },
            "CAP basvurusu icin not ortalamasinin 4,00 uzerinden en az 2,00 olmasi gerekir.",
        ]
    )
    orchestrator = MainOrchestrator(llm_service=llm_service)
    profiler = QueryProfiler(label="validator-main-judge-reject")

    with activate_profiler(profiler):
        repaired = await orchestrator._apply_main_judge_gate(
            query=query,
            answer=good_answer,
            responses=responses,
            answer_validation=initial_validation,
            used_global_synthesis=True,
        )

    assert repaired == good_answer
    assert llm_service.generate.await_count == 2
    attributes = profiler.snapshot()["attributes"]
    assert attributes["main_judge"]["repair"]["accepted"] is False
    assert attributes["evidence_answer_validator"]["repair_rejected"] is True
    assert attributes["evidence_answer_validator"]["post_repair_validation"]["status"] == "fail"


@pytest.mark.asyncio
async def test_main_judge_marks_non_improving_repair_as_neutral():
    query = "CAP icin not ortalamasi kac olmali?"
    incomplete_answer = "CAP basvurusu icin sartlar kaynaklarda belirtilmistir."
    neutral_repair = "CAP basvurusu icin basvuru sartlari kaynaklarda yer alir."
    responses = [_response_with_cap_threshold()]
    initial_validation = validate_evidence_answer(
        query=query,
        answer=incomplete_answer,
        responses=responses,
    )
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        side_effect=[
            {
                "approved": False,
                "action": "rewrite_only",
                "failure_reason": "missing evidence value 3,00",
            },
            neutral_repair,
        ]
    )
    orchestrator = MainOrchestrator(llm_service=llm_service)
    profiler = QueryProfiler(label="validator-main-judge-neutral")

    with activate_profiler(profiler):
        repaired = await orchestrator._apply_main_judge_gate(
            query=query,
            answer=incomplete_answer,
            responses=responses,
            answer_validation=initial_validation,
            used_global_synthesis=True,
        )

    assert repaired == neutral_repair
    attributes = profiler.snapshot()["attributes"]
    assert attributes["main_judge"]["repair"]["outcome"] == "accepted_neutral"
    assert attributes["evidence_answer_validator"]["repair_neutral"] is True
    assert "repair_accepted" not in attributes["evidence_answer_validator"]
