"""User-facing dynamic runtime pilot engine.

This module is separate from the protected classic runtime. It turns a tenant profile
into a capability -> agent -> source answer path without importing classic
department routing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any

from src.dynamic_platform.generic_agent_host import GenericAgentHost, GenericAgentResult
from src.dynamic_platform.loader import load_tenant_bundle
from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.shadow_runtime import build_shadow_runtime_decision


@dataclass(frozen=True)
class DynamicRuntimeQuery:
    tenant_key: str
    query: str
    conversation_id: str = "dynamic-runtime"
    user_id: str = "anonymous"
    requested_capabilities: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DynamicRuntimeAnswer:
    tenant_key: str
    answer: str
    answer_status: str
    selected_capabilities: list[str]
    agents: list[str]
    sources: list[str]
    final_owner: str | None
    telemetry: dict[str, Any]
    safety_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "answer": self.answer,
            "answer_status": self.answer_status,
            "selected_capabilities": self.selected_capabilities,
            "agents": self.agents,
            "sources": self.sources,
            "final_owner": self.final_owner,
            "telemetry": self.telemetry,
            "safety_notes": self.safety_notes,
        }


class DynamicRuntimeOrchestrator:
    """Profile-driven runtime orchestrator for dynamic pilot tenants."""

    def __init__(self, bundle: DynamicPlatformBundle, *, project_root: str | Path = ".") -> None:
        self.bundle = bundle
        self.project_root = Path(project_root)

    @classmethod
    def from_tenant(
        cls,
        tenant_key: str,
        *,
        config_root: str | Path = "configs/dynamic_platform",
        project_root: str | Path = ".",
    ) -> "DynamicRuntimeOrchestrator":
        return cls(load_tenant_bundle(tenant_key, config_root=config_root), project_root=project_root)

    def answer(self, request: DynamicRuntimeQuery) -> DynamicRuntimeAnswer:
        start = perf_counter()
        if request.tenant_key != self.bundle.tenant.tenant_key:
            return self._unsafe(
                request,
                reason=(
                    f"Request tenant {request.tenant_key!r} does not match loaded tenant "
                    f"{self.bundle.tenant.tenant_key!r}."
                ),
                started_at=start,
            )
        if self.bundle.tenant.runtime_strategy == "classic_protected":
            return self._unsafe(
                request,
                reason="classic_protected tenants must stay on the classic runtime path.",
                started_at=start,
            )

        decision = build_shadow_runtime_decision(
            self.bundle,
            query=request.query,
            requested_capabilities=request.requested_capabilities,
        )
        selected_capabilities = decision.selected_capabilities
        if not selected_capabilities:
            return DynamicRuntimeAnswer(
                tenant_key=self.bundle.tenant.tenant_key,
                answer=(
                    f"{self.bundle.tenant.display_name} profili içinde bu soruyu güvenilir biçimde "
                    "eşleştirebildiğim bir capability bulunamadı."
                ),
                answer_status="needs_clarification",
                selected_capabilities=[],
                agents=[],
                sources=[],
                final_owner=None,
                telemetry=self._telemetry(start, decision=decision, agent_results=[]),
                safety_notes=["No protected classic fallback was used."],
            )

        agent_results = self._run_agents(request.query, selected_capabilities, decision.agents)
        answered = [result for result in agent_results if result.answer_status == "answered"]
        source_ids = sorted(
            {
                excerpt.source_id
                for result in agent_results
                for excerpt in result.source_excerpts
            }
        )
        status = "answered" if answered else "not_found"
        answer = "\n\n".join(result.answer for result in (answered or agent_results) if result.answer)
        final_owner = _first_or_none(decision.final_owner_candidates or decision.agents)
        return DynamicRuntimeAnswer(
            tenant_key=self.bundle.tenant.tenant_key,
            answer=answer,
            answer_status=status,
            selected_capabilities=selected_capabilities,
            agents=[result.agent_id for result in agent_results],
            sources=source_ids,
            final_owner=final_owner,
            telemetry=self._telemetry(start, decision=decision, agent_results=agent_results),
            safety_notes=[
                "Dynamic pilot response used only the loaded tenant profile and tenant-scoped source catalog.",
                "No protected classic department fallback was used.",
            ],
        )

    def topology(self) -> dict[str, Any]:
        return {
            "tenant_key": self.bundle.tenant.tenant_key,
            "display_name": self.bundle.tenant.display_name,
            "runtime_strategy": self.bundle.tenant.runtime_strategy,
            "domain_pack": self.bundle.domain_pack.domain_pack,
            "agent_pack": self.bundle.agent_pack.agent_pack,
            "source_catalog": self.bundle.source_catalog.source_catalog,
            "capabilities": [capability.model_dump(mode="json") for capability in self.bundle.domain_pack.capabilities],
            "agents": [agent.model_dump(mode="json") for agent in self.bundle.agent_pack.agents],
            "sources": [source.model_dump(mode="json") for source in self.bundle.source_catalog.sources],
        }

    def health(self) -> dict[str, Any]:
        source_count = len([source for source in self.bundle.source_catalog.sources if source.enabled])
        return {
            "status": "healthy" if self.bundle.tenant.runtime_strategy != "classic_protected" else "disabled",
            "tenant_key": self.bundle.tenant.tenant_key,
            "runtime_strategy": self.bundle.tenant.runtime_strategy,
            "domain_pack": self.bundle.domain_pack.domain_pack,
            "agent_count": len(self.bundle.agent_pack.agents),
            "capability_count": len(self.bundle.domain_pack.capabilities),
            "enabled_source_count": source_count,
        }

    def _run_agents(
        self,
        query: str,
        selected_capabilities: list[str],
        agent_ids: list[str],
    ) -> list[GenericAgentResult]:
        agents_by_id = {agent.agent_id: agent for agent in self.bundle.agent_pack.agents}
        results: list[GenericAgentResult] = []
        for agent_id in agent_ids:
            agent = agents_by_id.get(agent_id)
            if agent is None:
                continue
            results.append(
                GenericAgentHost(self.bundle, agent, project_root=self.project_root).handle(
                    query=query,
                    selected_capabilities=selected_capabilities,
                )
            )
        return results

    def _unsafe(self, request: DynamicRuntimeQuery, *, reason: str, started_at: float) -> DynamicRuntimeAnswer:
        return DynamicRuntimeAnswer(
            tenant_key=self.bundle.tenant.tenant_key,
            answer="",
            answer_status="unsafe_to_answer",
            selected_capabilities=[],
            agents=[],
            sources=[],
            final_owner=None,
            telemetry={
                "reason": reason,
                "requested_tenant": request.tenant_key,
                "latency_ms": round((perf_counter() - started_at) * 1000, 2),
            },
            safety_notes=[reason],
        )

    def _telemetry(
        self,
        started_at: float,
        *,
        decision,
        agent_results: list[GenericAgentResult],
    ) -> dict[str, Any]:
        return {
            "tenant_key": self.bundle.tenant.tenant_key,
            "runtime_strategy": self.bundle.tenant.runtime_strategy,
            "domain_pack": self.bundle.domain_pack.domain_pack,
            "agent_pack": self.bundle.agent_pack.agent_pack,
            "match_mode": decision.match_mode,
            "confidence": decision.confidence,
            "capability_scores": decision.capability_scores,
            "parallel_groups": decision.execution_plan,
            "agent_results": [result.to_dict() for result in agent_results],
            "latency_ms": round((perf_counter() - started_at) * 1000, 2),
        }


def _first_or_none(values: list[str]) -> str | None:
    return values[0] if values else None
