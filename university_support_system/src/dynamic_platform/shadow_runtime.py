"""Shadow-only dynamic runtime decision preview.

This module is deliberately not imported by the classic OMU runtime. It offers
an offline preview of how a future dynamic runtime could map a query to
tenant capabilities, agents, specialists, and source contracts.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import CapabilityDefinition, DynamicPlatformBundle

_STOPWORDS = {
    "a",
    "acaba",
    "bir",
    "bu",
    "da",
    "de",
    "diye",
    "icin",
    "için",
    "ile",
    "kadar",
    "mi",
    "mı",
    "misin",
    "miyim",
    "mu",
    "mü",
    "mudur",
    "musun",
    "ne",
    "nedir",
    "nasil",
    "nasıl",
    "var",
    "ve",
}

_TEMPORAL_TOKENS = {
    "basvuru",
    "deadline",
    "son",
    "sure",
    "takvim",
    "tarih",
    "zaman",
}

_UPLOADED_CONTEXT_TOKENS = {
    "belge",
    "dokum",
    "dosya",
    "incele",
    "inceleyip",
    "not",
    "ocr",
    "transkript",
}

_CASE_SUFFIXES = (
    "lerinden",
    "larindan",
    "lerinde",
    "larinda",
    "lerinin",
    "larinin",
    "leriyle",
    "lariyla",
    "leri",
    "lari",
    "lerden",
    "lardan",
    "lere",
    "lara",
    "lerde",
    "larda",
    "ler",
    "lar",
    "imizden",
    "imizde",
    "imiz",
    "imin",
    "imi",
    "ime",
    "ima",
    "inde",
    "inda",
    "inden",
    "indan",
    "inin",
    "siyle",
    "siyla",
    "yle",
    "yla",
    "den",
    "dan",
    "nin",
    "nun",
    "sin",
    "sun",
    "in",
    "un",
    "im",
    "um",
    "em",
    "de",
    "da",
    "ye",
    "ya",
)


@dataclass(frozen=True)
class ShadowRuntimeDecision:
    tenant_key: str
    query: str
    runtime_strategy: str
    runtime_binding_status: str
    match_mode: str
    confidence: float
    selected_capabilities: list[str] = field(default_factory=list)
    capability_scores: dict[str, int] = field(default_factory=dict)
    agents: list[str] = field(default_factory=list)
    specialists: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    source_families: list[str] = field(default_factory=list)
    source_owners: list[str] = field(default_factory=list)
    authority_levels: list[str] = field(default_factory=list)
    final_owner_candidates: list[str] = field(default_factory=list)
    execution_plan: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "query": self.query,
            "runtime_strategy": self.runtime_strategy,
            "runtime_binding_status": self.runtime_binding_status,
            "match_mode": self.match_mode,
            "confidence": self.confidence,
            "selected_capabilities": self.selected_capabilities,
            "capability_scores": self.capability_scores,
            "agents": self.agents,
            "specialists": self.specialists,
            "source_ids": self.source_ids,
            "source_families": self.source_families,
            "source_owners": self.source_owners,
            "authority_levels": self.authority_levels,
            "final_owner_candidates": self.final_owner_candidates,
            "execution_plan": self.execution_plan,
            "warnings": self.warnings,
            "notes": self.notes,
        }


def build_shadow_runtime_decision(
    bundle: DynamicPlatformBundle,
    *,
    query: str,
    requested_capabilities: list[str] | None = None,
) -> ShadowRuntimeDecision:
    requested = [item for item in (requested_capabilities or []) if item]
    capability_ids = bundle.capability_ids()
    warnings: list[str] = []
    if requested:
        unknown = sorted(set(requested) - capability_ids)
        if unknown:
            warnings.append(f"Requested capability not present in tenant profile: {', '.join(unknown)}.")
        selected_capabilities = [item for item in requested if item in capability_ids]
        scores = {item: 100 for item in selected_capabilities}
        match_mode = "explicit_capability"
        confidence = 1.0 if selected_capabilities else 0.0
    else:
        scores = _score_capabilities(bundle, query)
        selected_capabilities = _select_scored_capabilities(scores)
        selected_capabilities = _expand_supporting_capabilities(bundle, query, selected_capabilities, scores)
        match_mode = "keyword_shadow"
        confidence = _confidence(scores, selected_capabilities)
        if not selected_capabilities:
            warnings.append("No capability matched the query in the tenant profile keyword shadow matcher.")
        elif len(selected_capabilities) > 2:
            warnings.append("Multiple capabilities matched; a live runtime would need a stronger router/judge.")

    agents = _agents_for(bundle, selected_capabilities)
    specialists = _specialists_for(bundle, selected_capabilities)
    sources = _sources_for(bundle, selected_capabilities)
    final_owner_candidates = _final_owner_candidates(bundle, selected_capabilities, agents)
    execution_plan = [
        {
            "step": index + 1,
            "agent": agent_id,
            "parallel_group": 1,
            "role": _agent_role(bundle, agent_id),
            "final_owner_candidate": agent_id in final_owner_candidates,
        }
        for index, agent_id in enumerate(agents)
    ]
    notes = [
        "Shadow runtime decision is offline; it does not call router, agents, retrieval, databases, Slack, or LLMs.",
        "This preview must not be used as a live answer path until runtime adapter, replay, and safety gates are approved.",
    ]
    if bundle.tenant.runtime_strategy == "classic_protected":
        notes.append("Tenant is classic_protected; dynamic runtime remains disabled for live OMU behavior.")

    return ShadowRuntimeDecision(
        tenant_key=bundle.tenant.tenant_key,
        query=query,
        runtime_strategy=bundle.tenant.runtime_strategy,
        runtime_binding_status="shadow_only_runtime_not_wired",
        match_mode=match_mode,
        confidence=confidence,
        selected_capabilities=selected_capabilities,
        capability_scores={key: value for key, value in sorted(scores.items()) if value > 0},
        agents=agents,
        specialists=specialists,
        source_ids=sorted({source.source_id for source in sources}),
        source_families=sorted({source.source_family for source in sources}),
        source_owners=sorted({source.owner_agent for source in sources}),
        authority_levels=sorted({source.authority_level for source in sources}),
        final_owner_candidates=final_owner_candidates,
        execution_plan=execution_plan,
        warnings=warnings,
        notes=notes,
    )


def _score_capabilities(bundle: DynamicPlatformBundle, query: str) -> dict[str, int]:
    query_tokens = set(_tokens(query))
    scores: dict[str, int] = {}
    for capability in bundle.domain_pack.capabilities:
        keywords = _capability_keywords(bundle, capability)
        scores[capability.capability_id] = len(query_tokens & keywords)
    return scores


def _capability_keywords(bundle: DynamicPlatformBundle, capability: CapabilityDefinition) -> set[str]:
    raw: list[str] = [
        capability.capability_id,
        capability.display_name,
        capability.description,
        capability.core_capability or "",
        *capability.keywords,
    ]
    for source in bundle.source_catalog.sources:
        if capability.capability_id in source.capabilities:
            raw.extend([source.source_id, source.source_family, source.owner_agent])
            raw.extend(str(value) for value in source.metadata.values())
    for agent in bundle.agent_pack.agents:
        if capability.capability_id in agent.capabilities:
            raw.extend([agent.agent_id, agent.display_name])
            raw.extend(agent.source_families)
            raw.extend(agent.final_owner_for)
            for specialist in agent.specialists:
                if capability.capability_id in specialist.capabilities:
                    raw.extend([specialist.specialist_id, specialist.display_name])
    return set(_tokens(" ".join(raw)))


def _select_scored_capabilities(scores: dict[str, int]) -> list[str]:
    if not scores:
        return []
    max_score = max(scores.values())
    if max_score <= 0:
        return []
    return sorted(capability for capability, score in scores.items() if score == max_score)


def _expand_supporting_capabilities(
    bundle: DynamicPlatformBundle,
    query: str,
    selected_capabilities: list[str],
    scores: dict[str, int],
) -> list[str]:
    """Add profile-declared support capabilities for temporal/source lookups.

    The expansion is intentionally adapter/profile based. It does not know
    about OMU-specific concepts such as CAP; it only sees that a tenant has a
    calendar source or announcement source that can support a temporal query.
    """

    if not selected_capabilities:
        return []

    query_tokens = set(_tokens(query))
    expanded = set(selected_capabilities)

    if query_tokens & _UPLOADED_CONTEXT_TOKENS:
        expanded.update(
            capability
            for source in bundle.source_catalog.sources
            if source.enabled and source.adapter == "slack_uploaded_file"
            for capability in source.capabilities
        )

    if not (query_tokens & _TEMPORAL_TOKENS):
        return sorted(expanded)

    calendar_capabilities = {
        capability
        for source in bundle.source_catalog.sources
        if source.enabled and source.adapter == "calendar_pdf"
        for capability in source.capabilities
    }
    announcement_capabilities = {
        capability
        for source in bundle.source_catalog.sources
        if source.enabled and source.adapter == "announcement_page"
        for capability in source.capabilities
    }

    for capability in calendar_capabilities:
        if scores.get(capability, 0) > 0 or capability not in scores:
            expanded.add(capability)

    if "basvuru" in query_tokens or "son" in query_tokens:
        expanded.update(announcement_capabilities)

    return sorted(expanded)


def _confidence(scores: dict[str, int], selected: list[str]) -> float:
    if not selected:
        return 0.0
    ordered = sorted(scores.values(), reverse=True)
    top = ordered[0] if ordered else 0
    second = ordered[1] if len(ordered) > 1 else 0
    if top <= 0:
        return 0.0
    margin = max(top - second, 0)
    return round(min(0.95, 0.45 + (top * 0.12) + (margin * 0.08)), 2)


def _agents_for(bundle: DynamicPlatformBundle, capabilities: list[str]) -> list[str]:
    return sorted(
        {
            agent.agent_id
            for agent in bundle.agent_pack.agents
            if set(agent.capabilities) & set(capabilities)
        }
    )


def _specialists_for(bundle: DynamicPlatformBundle, capabilities: list[str]) -> list[str]:
    return sorted(
        {
            specialist.specialist_id
            for agent in bundle.agent_pack.agents
            for specialist in agent.specialists
            if set(specialist.capabilities) & set(capabilities)
        }
    )


def _sources_for(bundle: DynamicPlatformBundle, capabilities: list[str]):
    return [
        source
        for source in bundle.source_catalog.sources
        if source.enabled and set(source.capabilities) & set(capabilities)
    ]


def _final_owner_candidates(bundle: DynamicPlatformBundle, capabilities: list[str], agents: list[str]) -> list[str]:
    capability_set = set(capabilities)
    candidates = [
        agent.agent_id
        for agent in bundle.agent_pack.agents
        if agent.agent_id in agents and capability_set & set(agent.final_owner_for)
    ]
    return sorted(candidates or agents)


def _agent_role(bundle: DynamicPlatformBundle, agent_id: str) -> str:
    for agent in bundle.agent_pack.agents:
        if agent.agent_id == agent_id:
            return agent.role
    return "unknown"


def _tokens(text: str) -> list[str]:
    normalized = _normalize(text)
    tokens: list[str] = []
    for token in re.findall(r"[a-z0-9]+", normalized):
        if token in _STOPWORDS or len(token) <= 1:
            continue
        tokens.append(token)
        tokens.extend(_token_variants(token))
    return [token for token in dict.fromkeys(tokens) if token not in _STOPWORDS and len(token) > 1]


def _normalize(text: str) -> str:
    lowered = text.lower().replace("ı", "i").replace("İ", "i")
    decomposed = unicodedata.normalize("NFKD", lowered)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _token_variants(token: str) -> list[str]:
    variants: list[str] = []
    for suffix in _CASE_SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            variants.append(token[: -len(suffix)])
            break
    if token.endswith(("i", "u", "e", "a")) and len(token) >= 5:
        variants.append(token[:-1])
    return variants
