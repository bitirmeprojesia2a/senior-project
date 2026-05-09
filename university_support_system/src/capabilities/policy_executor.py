"""Policy/RAG capability executors.

Policy capabilities do not query SQL directly. They carry an LLM-selected
retrieval and answer contract to the owning specialist agent, which then uses
the existing RAG pipeline. The executor exists so the registry remains fully
whitelisted and accidental direct execution falls back safely.
"""

from __future__ import annotations

from typing import Any

from src.capabilities.models import ExecutionResult


async def student_affairs_lookup(params: dict[str, Any]) -> ExecutionResult:
    """Return a safe planning result for guided Student Affairs RAG lookup."""
    query = str(params.get("query") or "").strip()
    if not query:
        return ExecutionResult(
            success=False,
            capability="student_affairs.policy_lookup",
            params=params,
            error="missing_params",
            missing_params=["query"],
            fallback_allowed=True,
        )
    return ExecutionResult(
        success=True,
        capability="student_affairs.policy_lookup",
        params=params,
        records=[],
        metadata={
            "policy_lookup": True,
            "query": query,
            "topic": params.get("topic"),
            "question_type": params.get("question_type"),
            "must_answer": params.get("must_answer") or [],
            "preferred_sources": params.get("preferred_sources") or [],
            "avoid_sources": params.get("avoid_sources") or [],
        },
        message="policy_lookup_plan_ready",
        fallback_allowed=True,
    )


async def international_lookup(params: dict[str, Any]) -> ExecutionResult:
    """Return a safe planning result for guided International RAG lookup."""
    query = str(params.get("query") or "").strip()
    if not query:
        return ExecutionResult(
            success=False,
            capability="international.policy_lookup",
            params=params,
            error="missing_params",
            missing_params=["query"],
            fallback_allowed=True,
        )
    return ExecutionResult(
        success=True,
        capability="international.policy_lookup",
        params=params,
        records=[],
        metadata={
            "policy_lookup": True,
            "query": query,
            "topic": params.get("topic"),
            "question_type": params.get("question_type"),
            "must_answer": params.get("must_answer") or [],
            "preferred_sources": params.get("preferred_sources") or [],
            "avoid_sources": params.get("avoid_sources") or [],
        },
        message="policy_lookup_plan_ready",
        fallback_allowed=True,
    )
