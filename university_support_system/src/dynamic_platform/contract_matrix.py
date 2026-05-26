"""Capability contract matrix for a dynamic tenant profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class CapabilityContractRow:
    capability_id: str
    display_name: str
    answer_mode: str
    core_capability: str | None
    agents: list[str]
    specialists: list[str]
    source_ids: list[str]
    source_families: list[str]
    authority_levels: list[str]
    final_owner_candidates: list[str]
    operation_owner_refs: dict[str, list[str]]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "display_name": self.display_name,
            "answer_mode": self.answer_mode,
            "core_capability": self.core_capability,
            "agents": self.agents,
            "specialists": self.specialists,
            "source_ids": self.source_ids,
            "source_families": self.source_families,
            "authority_levels": self.authority_levels,
            "final_owner_candidates": self.final_owner_candidates,
            "operation_owner_refs": self.operation_owner_refs,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class CapabilityContractMatrix:
    tenant_key: str
    runtime_strategy: str
    ok: bool
    summary: dict[str, Any]
    rows: list[CapabilityContractRow]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "ok": self.ok,
            "summary": self.summary,
            "rows": [row.to_dict() for row in self.rows],
            "notes": self.notes,
        }


def build_capability_contract_matrix(bundle: DynamicPlatformBundle) -> CapabilityContractMatrix:
    rows = [_build_row(bundle, capability.capability_id) for capability in bundle.domain_pack.capabilities]
    warning_count = sum(len(row.warnings) for row in rows)
    operation_owner_ref_count = sum(
        len(refs)
        for row in rows
        for refs in row.operation_owner_refs.values()
    )
    ok = warning_count == 0
    return CapabilityContractMatrix(
        tenant_key=bundle.tenant.tenant_key,
        runtime_strategy=bundle.tenant.runtime_strategy,
        ok=ok,
        summary={
            "capability_count": len(rows),
            "warning_count": warning_count,
            "without_agents": [row.capability_id for row in rows if not row.agents],
            "without_sources": [row.capability_id for row in rows if not row.source_ids],
            "without_final_owner_candidates": [
                row.capability_id for row in rows if not row.final_owner_candidates
            ],
            "operation_owner_ref_count": operation_owner_ref_count,
            "capabilities_with_operation_owner_refs": [
                row.capability_id for row in rows if row.operation_owner_refs
            ],
        },
        rows=rows,
        notes=[
            "This matrix is offline and reflects profile contracts only.",
            "It does not execute router, agents, retrieval, DB queries, Slack, or LLM calls.",
            "final_owner_candidates are capability-level final-owner declarations.",
            "operation_owner_refs show non-capability final_owner_for declarations such as exact lookup operations.",
        ],
    )


def _build_row(bundle: DynamicPlatformBundle, capability_id: str) -> CapabilityContractRow:
    capability = next(item for item in bundle.domain_pack.capabilities if item.capability_id == capability_id)
    agents = sorted(agent.agent_id for agent in bundle.agent_pack.agents if capability_id in agent.capabilities)
    specialists = sorted(
        specialist.specialist_id
        for agent in bundle.agent_pack.agents
        for specialist in agent.specialists
        if capability_id in specialist.capabilities
    )
    sources = [
        source
        for source in bundle.source_catalog.sources
        if source.enabled and capability_id in source.capabilities
    ]
    source_ids = sorted(source.source_id for source in sources)
    source_families = sorted({source.source_family for source in sources})
    authority_levels = sorted({source.authority_level for source in sources})
    final_owner_candidates = sorted(
        agent.agent_id
        for agent in bundle.agent_pack.agents
        if capability_id in agent.final_owner_for
    )
    capability_ids = bundle.capability_ids()
    operation_owner_refs = {
        agent.agent_id: sorted(ref for ref in agent.final_owner_for if ref not in capability_ids)
        for agent in bundle.agent_pack.agents
        if capability_id in agent.capabilities
        and any(ref not in capability_ids for ref in agent.final_owner_for)
    }
    warnings: list[str] = []
    if not agents:
        warnings.append("capability has no agent")
    if not sources:
        warnings.append("capability has no enabled source")
    return CapabilityContractRow(
        capability_id=capability.capability_id,
        display_name=capability.display_name,
        answer_mode=capability.answer_mode,
        core_capability=capability.core_capability,
        agents=agents,
        specialists=specialists,
        source_ids=source_ids,
        source_families=source_families,
        authority_levels=authority_levels,
        final_owner_candidates=final_owner_candidates,
        operation_owner_refs=operation_owner_refs,
        warnings=warnings,
    )
