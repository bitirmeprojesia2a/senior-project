"""Resolved runtime decision metadata.

This module does not make routing decisions.  It records the single effective
decision surface that downstream dispatch, synthesis, cache, and replay audits
should inspect.  The goal is to keep diagnostics and behavioral contracts from
drifting into several incompatible metadata shapes.
"""

from __future__ import annotations

from typing import Any

from src.core.answer_contracts import should_use_deterministic_final
from src.core.source_ownership import normalize_source_owner

RESOLVED_DECISION_SCHEMA = "omu.resolved_decision.v1"
RUNTIME_AUTHORITY_SCHEMA = "omu.runtime_authority.v1"


def build_resolved_decision_metadata(
    *,
    original_query: str,
    effective_query: str,
    routing: Any | None = None,
    conversation_resolution: Any | None = None,
    answer_contract: Any | None = None,
    capability_planner_payload: dict[str, Any] | None = None,
    source_owner_payload: dict[str, Any] | None = None,
    final_answer_owner: str | None = None,
    cache_lookup_policy: str | None = None,
    cache_store_policy: str | None = None,
    decision_contract_payload: dict[str, Any] | None = None,
    stage: str = "runtime",
) -> dict[str, Any]:
    """Build a compact decision object for traces and downstream checks."""

    action = (
        capability_planner_payload.get("action")
        if isinstance(capability_planner_payload, dict)
        else None
    )
    capability = None
    if isinstance(action, dict):
        capability = str(action.get("capability") or "").strip() or None
    if not capability and answer_contract is not None:
        capability = getattr(answer_contract, "capability", None)

    contract_id = getattr(answer_contract, "contract_id", None)
    contract_policy = getattr(answer_contract, "synthesis_policy", None)
    source_owner = None
    if isinstance(source_owner_payload, dict):
        source_owner = normalize_source_owner(source_owner_payload.get("primary"))
    if not source_owner and answer_contract is not None:
        source_owner = normalize_source_owner(getattr(answer_contract, "source_owner", None))

    route_departments = [
        getattr(department, "value", str(department))
        for department in (getattr(routing, "departments", None) or [])
    ]
    frame = getattr(conversation_resolution, "frame", None)
    frame_facet = None
    frame_question_type = None
    if frame is not None:
        frame_facet = getattr(frame, "policy_facet", None)
        frame_question_type = getattr(frame, "question_type", None)

    precedence: list[str] = ["conversation_context", "router"]
    if contract_id:
        precedence.append("answer_contract")
    if source_owner:
        precedence.append("source_owner")
    if capability:
        precedence.append("capability_planner")
    precedence.extend(["dispatch", "synthesis", "quality_gate"])

    return {
        "schema": RESOLVED_DECISION_SCHEMA,
        "stage": stage,
        "original_query": original_query,
        "effective_query": effective_query,
        "conversation": {
            "is_follow_up": bool(getattr(conversation_resolution, "is_follow_up", False)),
            "topic": getattr(conversation_resolution, "active_topic", None),
            "policy_facet": frame_facet,
            "question_type": frame_question_type,
        },
        "routing": {
            "task_type": getattr(getattr(routing, "task_type", None), "value", getattr(routing, "task_type", None)),
            "departments": route_departments,
            "confidence": getattr(routing, "confidence", None),
        },
        "contract": {
            "id": contract_id,
            "facet": getattr(answer_contract, "facet", None),
            "synthesis_policy": contract_policy,
            "deterministic_final": bool(should_use_deterministic_final(answer_contract)),
        },
        "source_owner": source_owner,
        "capability": capability,
        "final_answer_owner": final_answer_owner,
        "cache": {
            "lookup": cache_lookup_policy,
            "store": cache_store_policy,
        },
        "precedence": precedence,
        "diagnostic_contract": {
            "schema": decision_contract_payload.get("schema"),
            "mode": decision_contract_payload.get("mode"),
        } if isinstance(decision_contract_payload, dict) else None,
    }


def build_runtime_authority_metadata(
    *,
    resolved_decision_payload: dict[str, Any] | None,
    source_owner_payload: dict[str, Any] | None = None,
    decision_contract_payload: dict[str, Any] | None = None,
    branch_dispatch_gate: dict[str, Any] | None = None,
    specialist_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the active runtime authority surface carried across agents.

    ``decision_contract`` remains read-only diagnostic metadata. This payload is
    the compact active contract downstream components should prefer when they
    need the effective owner/capability decision.
    """

    resolved = dict(resolved_decision_payload or {})
    source_owner = normalize_source_owner(resolved.get("source_owner"))
    if source_owner is None and isinstance(source_owner_payload, dict):
        source_owner = normalize_source_owner(source_owner_payload.get("primary"))

    diagnostic_contract = resolved.get("diagnostic_contract")
    if not isinstance(diagnostic_contract, dict):
        diagnostic_contract = {}
    if isinstance(decision_contract_payload, dict):
        diagnostic_contract = {
            "schema": decision_contract_payload.get("schema"),
            "mode": decision_contract_payload.get("mode"),
        }

    payload: dict[str, Any] = {
        "schema": RUNTIME_AUTHORITY_SCHEMA,
        "mode": "active",
        "stage": resolved.get("stage"),
        "original_query": resolved.get("original_query"),
        "effective_query": resolved.get("effective_query"),
        "conversation": dict(resolved.get("conversation") or {}),
        "routing": dict(resolved.get("routing") or {}),
        "contract": dict(resolved.get("contract") or {}),
        "source_owner": source_owner,
        "source_owner_payload": (
            dict(source_owner_payload) if isinstance(source_owner_payload, dict) else None
        ),
        "capability": _none_if_empty(resolved.get("capability")),
        "final_answer_owner": _none_if_empty(resolved.get("final_answer_owner")),
        "cache": dict(resolved.get("cache") or {}),
        "branch_dispatch_gate": (
            dict(branch_dispatch_gate) if isinstance(branch_dispatch_gate, dict) else None
        ),
        "specialist_selection": (
            dict(specialist_selection) if isinstance(specialist_selection, dict) else None
        ),
        "diagnostic_contract": diagnostic_contract or None,
        "compatibility": {
            "resolved_decision_schema": resolved.get("schema"),
        },
        "precedence": list(resolved.get("precedence") or []),
    }
    return payload


def _none_if_empty(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
