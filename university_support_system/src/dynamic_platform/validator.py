"""Validation and planning helpers for dynamic tenant profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import AgentDefinition, DynamicPlatformBundle


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }


@dataclass
class ValidationReport:
    tenant_key: str
    ok: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def add_error(self, code: str, message: str) -> None:
        self.errors.append(ValidationIssue("error", code, message))
        self.ok = False

    def add_warning(self, code: str, message: str) -> None:
        self.warnings.append(ValidationIssue("warning", code, message))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "summary": self.summary,
        }


def validate_bundle(bundle: DynamicPlatformBundle) -> ValidationReport:
    report = ValidationReport(
        tenant_key=bundle.tenant.tenant_key,
        ok=True,
        summary=build_topology_summary(bundle),
    )
    _validate_references(bundle, report)
    _validate_topology_shape(bundle, report)
    return report


def build_topology_summary(bundle: DynamicPlatformBundle) -> dict[str, Any]:
    agents = bundle.agent_pack.agents
    specialists = [specialist for agent in agents for specialist in agent.specialists]
    enabled_sources = [source for source in bundle.source_catalog.sources if source.enabled]
    capability_ids = sorted(bundle.capability_ids())
    agent_ids = sorted(bundle.agent_ids())
    source_families = sorted({source.source_family for source in bundle.source_catalog.sources})
    return {
        "runtime_strategy": bundle.tenant.runtime_strategy,
        "domain_pack": bundle.domain_pack.domain_pack,
        "agent_pack": bundle.agent_pack.agent_pack,
        "source_catalog": bundle.source_catalog.source_catalog,
        "capability_count": len(capability_ids),
        "agent_count": len(agents),
        "specialist_count": len(specialists),
        "source_count": len(bundle.source_catalog.sources),
        "enabled_source_count": len(enabled_sources),
        "capabilities": capability_ids,
        "agents": agent_ids,
        "source_families": source_families,
    }


def build_execution_plan(bundle: DynamicPlatformBundle) -> dict[str, Any]:
    """Return a dry-run topology plan without touching the classic runtime."""

    capability_to_agents: dict[str, list[str]] = {}
    for agent in bundle.agent_pack.agents:
        for capability in agent.capabilities:
            capability_to_agents.setdefault(capability, []).append(agent.agent_id)

    capability_to_sources: dict[str, list[str]] = {}
    for source in bundle.source_catalog.sources:
        if not source.enabled:
            continue
        for capability in source.capabilities:
            capability_to_sources.setdefault(capability, []).append(source.source_id)

    agents = []
    for agent in bundle.agent_pack.agents:
        agents.append(
            {
                "agent_id": agent.agent_id,
                "display_name": agent.display_name,
                "role": agent.role,
                "capabilities": list(agent.capabilities),
                "specialists": [specialist.specialist_id for specialist in agent.specialists],
                "source_families": list(agent.source_families),
                "llm_allowed": agent.llm_allowed,
                "deterministic_allowed": agent.deterministic_allowed,
            }
        )

    return {
        "tenant_key": bundle.tenant.tenant_key,
        "runtime_strategy": bundle.tenant.runtime_strategy,
        "agents": agents,
        "capability_to_agents": {key: sorted(value) for key, value in sorted(capability_to_agents.items())},
        "capability_to_sources": {key: sorted(value) for key, value in sorted(capability_to_sources.items())},
    }


def _validate_references(bundle: DynamicPlatformBundle, report: ValidationReport) -> None:
    if bundle.agent_pack.domain_pack != bundle.domain_pack.domain_pack:
        report.add_error(
            "agent_pack_domain_mismatch",
            (
                f"Agent pack {bundle.agent_pack.agent_pack} targets domain "
                f"{bundle.agent_pack.domain_pack}, but tenant uses {bundle.domain_pack.domain_pack}."
            ),
        )

    if bundle.source_catalog.tenant_key != bundle.tenant.tenant_key:
        report.add_error(
            "source_catalog_tenant_mismatch",
            (
                f"Source catalog {bundle.source_catalog.source_catalog} belongs to "
                f"{bundle.source_catalog.tenant_key}, not {bundle.tenant.tenant_key}."
            ),
        )

    if bundle.source_catalog.source_catalog != bundle.tenant.source_catalog:
        report.add_error(
            "source_catalog_reference_mismatch",
            (
                f"Tenant references source catalog {bundle.tenant.source_catalog}, "
                f"but loaded catalog is {bundle.source_catalog.source_catalog}."
            ),
        )


def _validate_topology_shape(bundle: DynamicPlatformBundle, report: ValidationReport) -> None:
    capabilities = bundle.capability_ids()
    agents = {agent.agent_id: agent for agent in bundle.agent_pack.agents}

    if not bundle.domain_pack.capabilities:
        report.add_error("domain_pack_has_no_capabilities", "Domain pack must define at least one capability.")
    if not bundle.agent_pack.agents:
        report.add_error("agent_pack_has_no_agents", "Agent pack must define at least one agent.")

    for agent in bundle.agent_pack.agents:
        _validate_agent(agent, capabilities, report)

    for source in bundle.source_catalog.sources:
        if source.domain != bundle.domain_pack.domain_pack:
            report.add_error(
                "source_domain_mismatch",
                f"Source {source.source_id} targets domain {source.domain}, not {bundle.domain_pack.domain_pack}.",
            )
        if source.owner_agent not in agents:
            report.add_error(
                "source_owner_agent_missing",
                f"Source {source.source_id} references missing owner agent {source.owner_agent}.",
            )
        for capability in source.capabilities:
            if capability not in capabilities:
                report.add_error(
                    "source_capability_unknown",
                    f"Source {source.source_id} references unknown capability {capability}.",
                )

    source_capabilities = {
        capability
        for source in bundle.source_catalog.sources
        if source.enabled
        for capability in source.capabilities
    }
    agent_capabilities = {
        capability
        for agent in bundle.agent_pack.agents
        for capability in agent.capabilities
    }
    capabilities_without_agent = sorted(capabilities - agent_capabilities)
    capabilities_without_enabled_source = sorted(capabilities - source_capabilities)
    report.summary["capabilities_without_agent"] = capabilities_without_agent
    report.summary["capabilities_without_enabled_source"] = capabilities_without_enabled_source

    for capability in capabilities_without_agent:
        report.add_warning(
            "capability_without_agent",
            f"Capability {capability} is defined by the domain pack but no agent handles it.",
        )
    for capability in capabilities_without_enabled_source:
        report.add_warning(
            "capability_without_enabled_source",
            f"Capability {capability} is defined by the domain pack but has no enabled source in the catalog.",
        )


def _validate_agent(agent: AgentDefinition, capabilities: set[str], report: ValidationReport) -> None:
    for capability in agent.capabilities:
        if capability not in capabilities:
            report.add_error(
                "agent_capability_unknown",
                f"Agent {agent.agent_id} references unknown capability {capability}.",
            )
    agent_caps = set(agent.capabilities)
    for specialist in agent.specialists:
        for capability in specialist.capabilities:
            if capability not in capabilities:
                report.add_error(
                    "specialist_capability_unknown",
                    f"Specialist {specialist.specialist_id} references unknown capability {capability}.",
                )
            if capability not in agent_caps:
                report.add_error(
                    "specialist_capability_not_owned_by_agent",
                    (
                        f"Specialist {specialist.specialist_id} handles {capability}, "
                        f"but parent agent {agent.agent_id} does not list it."
                    ),
                )
