"""Contract-aware retrieval execution budgets.

This module is an execution guardrail: it does not decide intent, ownership, or
specialist selection. It translates an already-built decision contract into
retrieval fan-out limits so support branches and query variants cannot consume
the same budget as the primary owner path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from src.core.config import settings
from src.core.constants import Department
from src.core.text_normalization import normalize_text

BranchRole = Literal["primary", "support", "fallback", "unknown"]

RETRIEVAL_EXECUTION_POLICY_SCHEMA = "omu.retrieval_execution_policy.v1"


@dataclass(frozen=True)
class RetrievalExecutionPolicy:
    schema: str = RETRIEVAL_EXECUTION_POLICY_SCHEMA
    branch_role: BranchRole = "unknown"
    source_owner: str | None = None
    capability: str | None = None
    policy_facet: str | None = None
    preferred_specialist: str | None = None
    top_k: int | None = None
    reranker_candidate_limit: int | None = None
    max_multi_query_variants: int = 2
    variant_top_k: int = 3
    variant_reranker_candidate_limit: int | None = None
    support_lite: bool = False
    reason: str = "default_budget"

    @property
    def multi_query_enabled(self) -> bool:
        return self.max_multi_query_variants > 0

    def to_metadata(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "branch_role": self.branch_role,
            "source_owner": self.source_owner,
            "capability": self.capability,
            "policy_facet": self.policy_facet,
            "preferred_specialist": self.preferred_specialist,
            "top_k": self.top_k,
            "reranker_candidate_limit": self.reranker_candidate_limit,
            "multi_query_enabled": self.multi_query_enabled,
            "max_multi_query_variants": self.max_multi_query_variants,
            "variant_top_k": self.variant_top_k,
            "variant_reranker_candidate_limit": self.variant_reranker_candidate_limit,
            "support_lite": self.support_lite,
            "reason": self.reason,
        }


def build_branch_retrieval_metadata(
    *,
    department: Department,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Return metadata with branch role/policy attached for a department."""

    branch_role = resolve_branch_role(department=department, metadata=metadata)
    policy = resolve_retrieval_execution_policy(
        department=department,
        branch_role=branch_role,
        metadata=metadata,
    )
    enriched = dict(metadata or {})
    enriched["branch_role"] = branch_role
    enriched["retrieval_execution_policy"] = policy.to_metadata()
    return enriched


def resolve_branch_role(*, department: Department, metadata: dict[str, Any]) -> BranchRole:
    gate = metadata.get("branch_dispatch_gate")
    if not isinstance(gate, dict):
        return "unknown"
    owner_policy = gate.get("owner_routing_policy")
    if not isinstance(owner_policy, dict):
        return "unknown"
    primary = str(owner_policy.get("primary_department") or "").strip()
    support = {
        str(item).strip()
        for item in owner_policy.get("support_departments") or []
        if str(item).strip()
    }
    if department.value == primary:
        return "primary"
    if department.value in support:
        return "support"
    return "fallback"


def resolve_retrieval_execution_policy(
    *,
    department: Department | str | None,
    branch_role: BranchRole | str | None,
    metadata: dict[str, Any],
) -> RetrievalExecutionPolicy:
    existing = metadata.get("retrieval_execution_policy")
    if isinstance(existing, dict) and existing.get("schema") == RETRIEVAL_EXECUTION_POLICY_SCHEMA:
        return _policy_from_metadata(existing)

    role = _normalize_branch_role(branch_role)
    capability = _extract_capability(metadata)
    source_owner = _extract_source_owner(metadata)
    facet = _extract_policy_facet(metadata)
    preferred = _extract_preferred_specialist(metadata)

    if role == "support":
        return RetrievalExecutionPolicy(
            branch_role="support",
            source_owner=source_owner,
            capability=capability,
            policy_facet=facet,
            preferred_specialist=preferred,
            top_k=settings.rag.support_lite_top_k,
            reranker_candidate_limit=settings.rag.support_lite_reranker_candidate_limit,
            max_multi_query_variants=0,
            variant_top_k=settings.rag.multi_query_variant_top_k,
            variant_reranker_candidate_limit=settings.rag.multi_query_variant_reranker_candidate_limit,
            support_lite=True,
            reason="support_branch_lite_budget",
        )

    if role == "primary":
        return RetrievalExecutionPolicy(
            branch_role="primary",
            source_owner=source_owner,
            capability=capability,
            policy_facet=facet,
            preferred_specialist=preferred,
            top_k=None,
            reranker_candidate_limit=settings.rag.primary_reranker_candidate_limit,
            max_multi_query_variants=settings.rag.primary_multi_query_max_variants,
            variant_top_k=settings.rag.multi_query_variant_top_k,
            variant_reranker_candidate_limit=settings.rag.multi_query_variant_reranker_candidate_limit,
            support_lite=False,
            reason="primary_branch_budget",
        )

    return RetrievalExecutionPolicy(
        branch_role=role,
        source_owner=source_owner,
        capability=capability,
        policy_facet=facet,
        preferred_specialist=preferred,
        top_k=None,
        reranker_candidate_limit=None,
        max_multi_query_variants=settings.rag.primary_multi_query_max_variants,
        variant_top_k=settings.rag.multi_query_variant_top_k,
        variant_reranker_candidate_limit=settings.rag.multi_query_variant_reranker_candidate_limit,
        support_lite=False,
        reason="unknown_branch_default_budget",
    )


def strong_primary_evidence(
    results: list[dict[str, Any]],
    *,
    policy: RetrievalExecutionPolicy,
) -> tuple[bool, str]:
    """Return whether primary evidence is strong enough to skip MQE."""

    if policy.branch_role != "primary" or not results:
        return False, "not_primary_or_empty"
    if not policy.source_owner and not policy.capability:
        return False, "missing_contract"

    top_results = list(results)[:3]
    compatible = 0
    has_value_or_claim = False
    for item in top_results:
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        source_owner = str(
            metadata.get("source_owner")
            or metadata.get("source_owner_primary")
            or item.get("source_owner")
            or ""
        ).strip()
        alignment = metadata.get("policy_alignment") if isinstance(metadata.get("policy_alignment"), dict) else {}
        alignment_status = str(alignment.get("status") or "").strip()
        content = str(item.get("content") or "")
        if policy.source_owner and source_owner and source_owner != policy.source_owner:
            continue
        if alignment_status in {"conflict", "weak_conflict"}:
            continue
        compatible += 1
        if _has_answer_like_content(content):
            has_value_or_claim = True

    if compatible and has_value_or_claim:
        return True, "strong_primary_evidence"
    if compatible:
        return False, "compatible_but_no_answer_value"
    return False, "no_contract_compatible_evidence"


def _policy_from_metadata(payload: dict[str, Any]) -> RetrievalExecutionPolicy:
    return RetrievalExecutionPolicy(
        branch_role=_normalize_branch_role(payload.get("branch_role")),
        source_owner=_none_if_empty(payload.get("source_owner")),
        capability=_none_if_empty(payload.get("capability")),
        policy_facet=_none_if_empty(payload.get("policy_facet")),
        preferred_specialist=_none_if_empty(payload.get("preferred_specialist")),
        top_k=_int_or_none(payload.get("top_k")),
        reranker_candidate_limit=_int_or_none(payload.get("reranker_candidate_limit")),
        max_multi_query_variants=max(0, _int_or_none(payload.get("max_multi_query_variants")) or 0),
        variant_top_k=max(1, _int_or_none(payload.get("variant_top_k")) or 3),
        variant_reranker_candidate_limit=_int_or_none(payload.get("variant_reranker_candidate_limit")),
        support_lite=bool(payload.get("support_lite")),
        reason=str(payload.get("reason") or "metadata_budget"),
    )


def _extract_capability(metadata: dict[str, Any]) -> str | None:
    planner = metadata.get("capability_planner") if isinstance(metadata.get("capability_planner"), dict) else {}
    action = planner.get("action") if isinstance(planner.get("action"), dict) else {}
    capability = action.get("capability") or planner.get("capability")
    if capability:
        return str(capability).strip() or None
    resolved = metadata.get("resolved_decision") if isinstance(metadata.get("resolved_decision"), dict) else {}
    if resolved.get("capability"):
        return _none_if_empty(resolved.get("capability"))
    contract = _decision_contract_body(metadata)
    capabilities = contract.get("capabilities") if isinstance(contract.get("capabilities"), dict) else {}
    return _none_if_empty(capabilities.get("selected"))


def _extract_source_owner(metadata: dict[str, Any]) -> str | None:
    source_owner = metadata.get("source_owner") if isinstance(metadata.get("source_owner"), dict) else {}
    owner = source_owner.get("primary")
    if owner:
        return str(owner).strip() or None
    resolved = metadata.get("resolved_decision") if isinstance(metadata.get("resolved_decision"), dict) else {}
    if resolved.get("source_owner"):
        return _none_if_empty(resolved.get("source_owner"))
    contract = _decision_contract_body(metadata)
    source_contract = contract.get("source_owner") if isinstance(contract.get("source_owner"), dict) else {}
    return _none_if_empty(source_contract.get("primary"))


def _extract_policy_facet(metadata: dict[str, Any]) -> str | None:
    facet = metadata.get("policy_facet") if isinstance(metadata.get("policy_facet"), dict) else {}
    for key in ("facet", "policy_facet", "question_aspect", "target_program"):
        value = facet.get(key)
        if value:
            return str(value).strip() or None
    return None


def _extract_preferred_specialist(metadata: dict[str, Any]) -> str | None:
    selection = metadata.get("specialist_selection") if isinstance(metadata.get("specialist_selection"), dict) else {}
    value = selection.get("selected_agent_id") or selection.get("agent_id")
    return _none_if_empty(value)


def _decision_contract_body(metadata: dict[str, Any]) -> dict[str, Any]:
    decision = metadata.get("decision_contract") if isinstance(metadata.get("decision_contract"), dict) else {}
    contract = decision.get("contract") if isinstance(decision.get("contract"), dict) else {}
    return contract


def _normalize_branch_role(value: Any) -> BranchRole:
    text = str(value or "").strip().lower()
    if text in {"primary", "support", "fallback"}:
        return text  # type: ignore[return-value]
    return "unknown"


def _none_if_empty(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _has_answer_like_content(text: str) -> bool:
    normalized = normalize_text(text)
    if any(char.isdigit() for char in normalized):
        return True
    return any(marker in normalized for marker in ("hafta", "gun", "ay", "yil", "akts"))
