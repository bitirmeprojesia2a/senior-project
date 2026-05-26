"""Generic tenant agent host for dynamic pilot runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.generic_sources import SourceExcerpt
from src.dynamic_platform.models import AgentDefinition, DynamicPlatformBundle
from src.dynamic_platform.retrieval_service import (
    DynamicRetrievalService,
    LocalSourceRetrievalService,
    RetrievalQuery,
)


@dataclass(frozen=True)
class GenericAgentResult:
    agent_id: str
    display_name: str
    capabilities: list[str]
    answer: str
    answer_status: str
    source_excerpts: list[SourceExcerpt] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    retrieval_telemetry: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "capabilities": self.capabilities,
            "answer": self.answer,
            "answer_status": self.answer_status,
            "sources": [excerpt.to_dict() for excerpt in self.source_excerpts],
            "warnings": self.warnings,
            "retrieval": self.retrieval_telemetry,
        }


class GenericAgentHost:
    """Execute one configured agent using tenant-scoped source contracts."""

    def __init__(
        self,
        bundle: DynamicPlatformBundle,
        agent: AgentDefinition,
        *,
        project_root: str | Path = ".",
        retrieval_service: DynamicRetrievalService | None = None,
    ) -> None:
        self.bundle = bundle
        self.agent = agent
        self.retrieval_service = retrieval_service or LocalSourceRetrievalService(
            bundle,
            project_root=project_root,
        )

    def handle(self, *, query: str, selected_capabilities: list[str]) -> GenericAgentResult:
        owned_capabilities = [cap for cap in selected_capabilities if cap in self.agent.capabilities]
        if not owned_capabilities:
            return GenericAgentResult(
                agent_id=self.agent.agent_id,
                display_name=self.agent.display_name,
                capabilities=[],
                answer="",
                answer_status="not_applicable",
                warnings=["agent_does_not_own_selected_capabilities"],
            )
        retrieval = self.retrieval_service.search(
            RetrievalQuery(
                tenant_key=self.bundle.tenant.tenant_key,
                query=query,
                capabilities=owned_capabilities,
                source_families=self.agent.source_families,
            )
        )
        excerpts = retrieval.excerpts
        warnings = retrieval.warnings
        if not excerpts:
            return GenericAgentResult(
                agent_id=self.agent.agent_id,
                display_name=self.agent.display_name,
                capabilities=owned_capabilities,
                answer=(
                    f"{self.agent.display_name} ajanı bu soru için yetkili görünüyor; "
                    "ancak tenant kaynaklarında net bir kayıt bulunamadı."
                ),
                answer_status="not_found",
                warnings=warnings or ["no_matching_tenant_source_excerpt"],
                retrieval_telemetry=retrieval.telemetry,
            )
        answer = _compose_agent_answer(
            bundle=self.bundle,
            agent=self.agent,
            query=query,
            capabilities=owned_capabilities,
            excerpts=excerpts,
        )
        return GenericAgentResult(
            agent_id=self.agent.agent_id,
            display_name=self.agent.display_name,
            capabilities=owned_capabilities,
            answer=answer,
            answer_status="answered",
            source_excerpts=excerpts,
            warnings=warnings,
            retrieval_telemetry=retrieval.telemetry,
        )


def _compose_agent_answer(
    *,
    bundle: DynamicPlatformBundle,
    agent: AgentDefinition,
    query: str,
    capabilities: list[str],
    excerpts: list[SourceExcerpt],
) -> str:
    capability_names = {
        capability.capability_id: capability.display_name for capability in bundle.domain_pack.capabilities
    }
    capability_text = ", ".join(capability_names.get(capability, capability) for capability in capabilities)
    lead = f"{bundle.tenant.display_name} kaynaklarına göre {agent.display_name} ({capability_text}) cevabı:"
    lines = [lead]
    for excerpt in excerpts[:3]:
        cleaned = " ".join(excerpt.text.split())
        if len(cleaned) > 420:
            cleaned = cleaned[:417].rstrip() + "..."
        lines.append(f"- {cleaned}")
    source_ids = ", ".join(dict.fromkeys(excerpt.source_id for excerpt in excerpts))
    lines.append(f"Kaynaklar: {source_ids}")
    return "\n".join(lines)
