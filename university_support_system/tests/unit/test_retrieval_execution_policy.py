from __future__ import annotations

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.retrieval_execution_policy import (
    build_branch_retrieval_metadata,
    resolve_retrieval_execution_policy,
    strong_primary_evidence,
)


def _metadata() -> dict:
    return {
        "capability_planner": {
            "action": {
                "capability": "student_affairs.policy_lookup",
                "answer_contract": {"must_answer": ["muafiyet basvuru zamani"]},
            }
        },
        "source_owner": {"primary": "student_affairs_policy"},
        "branch_dispatch_gate": {
            "owner_routing_policy": {
                "primary_department": "student_affairs",
                "support_departments": ["academic_programs"],
            }
        },
    }


def test_branch_metadata_marks_primary_and_support_budget() -> None:
    primary = build_branch_retrieval_metadata(
        department=Department.STUDENT_AFFAIRS,
        metadata=_metadata(),
    )
    support = build_branch_retrieval_metadata(
        department=Department.ACADEMIC_PROGRAMS,
        metadata=_metadata(),
    )

    assert primary["branch_role"] == "primary"
    assert primary["retrieval_execution_policy"]["support_lite"] is False
    assert primary["retrieval_execution_policy"]["max_multi_query_variants"] == 1
    assert primary["retrieval_execution_policy"]["reranker_candidate_limit"] == 8

    assert support["branch_role"] == "support"
    assert support["retrieval_execution_policy"]["support_lite"] is True
    assert support["retrieval_execution_policy"]["top_k"] == 4
    assert support["retrieval_execution_policy"]["max_multi_query_variants"] == 0
    assert support["retrieval_execution_policy"]["reranker_candidate_limit"] == 4


def test_strong_primary_evidence_can_skip_multi_query() -> None:
    policy = resolve_retrieval_execution_policy(
        department=Department.STUDENT_AFFAIRS,
        branch_role="primary",
        metadata=_metadata(),
    )
    results = [
        {
            "content": "Muafiyet basvurusu egitim ogretimin basladigi tarihten itibaren 3 hafta icinde yapilir.",
            "score": 0.82,
            "metadata": {
                "source_owner": "student_affairs_policy",
                "policy_alignment": {"status": "match"},
            },
        }
    ]

    strong, reason = strong_primary_evidence(results, policy=policy)

    assert strong is True
    assert reason == "strong_primary_evidence"


def test_multi_query_skips_when_primary_evidence_is_strong() -> None:
    agent = BaseSpecialistAgent(
        AgentDefinition(
            agent_id="registration_agent",
            name="Registration",
            department=Department.STUDENT_AFFAIRS,
            description="",
            task_types=(TaskType.REGISTRATION_QUERY,),
            examples=(),
            tags=(),
        ),
        llm_service=object(),  # type: ignore[arg-type]
    )
    policy = resolve_retrieval_execution_policy(
        department=Department.STUDENT_AFFAIRS,
        branch_role="primary",
        metadata=_metadata(),
    )
    stats = {"search_calls": 1}

    class _Retriever:
        def search(self, *args, **kwargs):  # pragma: no cover - should not be reached
            raise AssertionError("variant search should be skipped")

    results = [{"content": "Muafiyet basvurusu 3 hafta icinde yapilir.", "metadata": {}}]

    returned = agent._apply_multi_query_expansion(
        "Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?",
        results,
        retriever=_Retriever(),
        top_k=8,
        department=Department.STUDENT_AFFAIRS,
        policy=policy,
        skip=True,
        stats=stats,
    )

    assert returned == results
    assert stats["search_calls"] == 1
    assert stats["multi_query_skipped"] is True


def test_support_policy_disables_multi_query() -> None:
    support_meta = build_branch_retrieval_metadata(
        department=Department.ACADEMIC_PROGRAMS,
        metadata=_metadata(),
    )
    policy = resolve_retrieval_execution_policy(
        department=Department.ACADEMIC_PROGRAMS,
        branch_role=support_meta["branch_role"],
        metadata=support_meta,
    )

    assert policy.support_lite is True
    assert policy.multi_query_enabled is False
    assert policy.top_k == 4


def test_runtime_authority_overrides_legacy_retrieval_contract_values() -> None:
    metadata = _metadata()
    metadata["source_owner"] = {"primary": "student_affairs_policy"}
    metadata["resolved_decision"] = {
        "schema": "omu.resolved_decision.v1",
        "source_owner": "student_affairs_policy",
        "capability": "student_affairs.policy_lookup",
    }
    metadata["runtime_authority"] = {
        "schema": "omu.runtime_authority.v1",
        "mode": "active",
        "source_owner": "tuition_fee_catalog",
        "capability": "finance.tuition_fee",
    }

    policy = resolve_retrieval_execution_policy(
        department=Department.FINANCE,
        branch_role="primary",
        metadata=metadata,
    )

    assert policy.source_owner == "tuition_fee_catalog"
    assert policy.capability == "finance.tuition_fee"
