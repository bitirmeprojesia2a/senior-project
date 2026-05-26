"""Offline bootstrap plan for tenant preparation.

The plan turns a tenant bundle into a generic implementation checklist. It is
safe to run before runtime wiring because it only inspects profile, agent, and
source catalog metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.decision_shadow import default_shadow_fixture_path
from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.source_ingestion_plan import build_source_ingestion_plan
from src.dynamic_platform.validator import validate_bundle


@dataclass(frozen=True)
class BootstrapStep:
    step_id: str
    status: str
    title: str
    required_artifacts: list[str] = field(default_factory=list)
    safe_commands: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "status": self.status,
            "title": self.title,
            "required_artifacts": self.required_artifacts,
            "safe_commands": self.safe_commands,
            "blockers": self.blockers,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class TenantBootstrapPlanReport:
    tenant_key: str
    ok: bool
    runtime_strategy: str
    summary: dict[str, Any]
    entity_groups: dict[str, int]
    capability_coverage: dict[str, Any]
    source_family_coverage: dict[str, Any]
    source_ingestion_summary: dict[str, Any]
    steps: list[BootstrapStep]
    safe_next_commands: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "runtime_strategy": self.runtime_strategy,
            "summary": self.summary,
            "entity_groups": self.entity_groups,
            "capability_coverage": self.capability_coverage,
            "source_family_coverage": self.source_family_coverage,
            "source_ingestion_summary": self.source_ingestion_summary,
            "steps": [step.to_dict() for step in self.steps],
            "safe_next_commands": self.safe_next_commands,
            "notes": self.notes,
        }


def build_tenant_bootstrap_plan(bundle: DynamicPlatformBundle) -> TenantBootstrapPlanReport:
    validation = validate_bundle(bundle)
    validation_payload = validation.to_dict()
    validation_summary = validation_payload.get("summary") or {}
    source_ingestion = build_source_ingestion_plan(bundle)
    source_ingestion_payload = source_ingestion.to_dict()

    capability_coverage = _capability_coverage(bundle, validation_summary)
    source_family_coverage = _source_family_coverage(bundle)
    entity_groups = {
        group: len(items)
        for group, items in sorted(bundle.tenant.entities.groups.items())
    }
    fixture_path = default_shadow_fixture_path(bundle.tenant.tenant_key)
    fixture_exists = fixture_path.exists()

    blockers = []
    if not validation.ok:
        blockers.append("tenant_bundle_validation_failed")
    blockers.extend(capability_coverage["capabilities_without_agent"])
    blockers.extend(capability_coverage["capabilities_without_enabled_source"])
    steps = [
        _step_profile(bundle, validation.ok),
        _step_entities(entity_groups),
        _step_sources(source_family_coverage, capability_coverage),
        _step_replay(bundle, fixture_path=fixture_path, fixture_exists=fixture_exists),
        _step_package(bundle),
        _step_handoff(bundle),
    ]
    ok = validation.ok and not capability_coverage["capabilities_without_agent"] and not capability_coverage[
        "capabilities_without_enabled_source"
    ]
    return TenantBootstrapPlanReport(
        tenant_key=bundle.tenant.tenant_key,
        ok=ok,
        runtime_strategy=bundle.tenant.runtime_strategy,
        summary={
            "domain_pack": bundle.domain_pack.domain_pack,
            "agent_pack": bundle.agent_pack.agent_pack,
            "source_catalog": bundle.source_catalog.source_catalog,
            "capability_count": len(bundle.domain_pack.capabilities),
            "agent_count": len(bundle.agent_pack.agents),
            "source_count": len(bundle.source_catalog.sources),
            "enabled_source_count": sum(1 for source in bundle.source_catalog.sources if source.enabled),
            "shadow_fixture_exists": fixture_exists,
            "blocker_count": len(blockers),
            "validation_ok": validation.ok,
        },
        entity_groups=entity_groups,
        capability_coverage=capability_coverage,
        source_family_coverage=source_family_coverage,
        source_ingestion_summary=source_ingestion_payload.get("summary") or {},
        steps=steps,
        safe_next_commands=[
            f"python -m scripts.tenant validate --tenant {bundle.tenant.tenant_key}",
            f"python -m scripts.tenant source-audit --tenant {bundle.tenant.tenant_key}",
            f"python -m scripts.tenant source-ingestion-plan --tenant {bundle.tenant.tenant_key}",
            f"python -m scripts.tenant quality-gates --tenant {bundle.tenant.tenant_key}",
            f"python -m scripts.tenant package --tenant {bundle.tenant.tenant_key} --force",
            "python -m scripts.tenant handoff-readiness --package-root tmp\\tenant_packages --allow-missing-shadow",
        ],
        notes=[
            "Bootstrap plan is offline and does not start services, open external sources, write indexes, or call models.",
            "It is intended to keep tenant setup explicit after scaffold/source/entity/replay changes.",
            "A passed bootstrap plan does not enable live dynamic routing.",
        ],
    )


def _capability_coverage(bundle: DynamicPlatformBundle, validation_summary: dict[str, Any]) -> dict[str, Any]:
    capability_ids = sorted(bundle.capability_ids())
    agent_capabilities = sorted({capability for agent in bundle.agent_pack.agents for capability in agent.capabilities})
    source_capabilities = sorted(
        {
            capability
            for source in bundle.source_catalog.sources
            if source.enabled
            for capability in source.capabilities
        }
    )
    return {
        "capabilities": capability_ids,
        "agent_capabilities": agent_capabilities,
        "enabled_source_capabilities": source_capabilities,
        "capabilities_without_agent": list(validation_summary.get("capabilities_without_agent") or []),
        "capabilities_without_enabled_source": list(
            validation_summary.get("capabilities_without_enabled_source") or []
        ),
    }


def _source_family_coverage(bundle: DynamicPlatformBundle) -> dict[str, Any]:
    required = sorted({family for agent in bundle.agent_pack.agents for family in agent.source_families})
    enabled = sorted({source.source_family for source in bundle.source_catalog.sources if source.enabled})
    return {
        "required_source_families": required,
        "enabled_source_families": enabled,
        "missing_source_families": sorted(set(required) - set(enabled)),
        "extra_source_families": sorted(set(enabled) - set(required)),
    }


def _step_profile(bundle: DynamicPlatformBundle, validation_ok: bool) -> BootstrapStep:
    return BootstrapStep(
        step_id="profile_contract",
        status="ready" if validation_ok else "blocked",
        title="Tenant profile, domain pack, agent pack, and source catalog references",
        required_artifacts=[
            f"configs/dynamic_platform/tenants/{bundle.tenant.tenant_key}.yaml",
            f"configs/dynamic_platform/domain_packs/{bundle.domain_pack.domain_pack}.yaml",
            f"configs/dynamic_platform/agent_packs/{bundle.agent_pack.agent_pack}.yaml",
            f"configs/dynamic_platform/source_catalogs/{bundle.source_catalog.source_catalog}.yaml",
        ],
        safe_commands=[f"python -m scripts.tenant validate --tenant {bundle.tenant.tenant_key}"],
        blockers=[] if validation_ok else ["validate_bundle_failed"],
    )


def _step_entities(entity_groups: dict[str, int]) -> BootstrapStep:
    return BootstrapStep(
        step_id="entity_registry",
        status="ready" if entity_groups else "draft",
        title="Tenant-specific entity registry",
        required_artifacts=["tenant profile entities.groups"],
        notes=[
            "Entity groups are tenant-defined. They can represent units, teams, services, products, departments, or any local structure.",
            f"Configured groups: {', '.join(entity_groups) if entity_groups else 'none'}",
        ],
    )


def _step_sources(source_family_coverage: dict[str, Any], capability_coverage: dict[str, Any]) -> BootstrapStep:
    blockers = list(source_family_coverage["missing_source_families"]) + list(
        capability_coverage["capabilities_without_enabled_source"]
    )
    return BootstrapStep(
        step_id="source_catalog",
        status="ready" if not blockers else "needs_attention",
        title="Source adapter coverage",
        required_artifacts=["source catalog entries with owner_agent, capabilities, authority_level, and entity_scope"],
        safe_commands=["python -m scripts.tenant source-audit --tenant <tenant>"],
        blockers=blockers,
        notes=[
            "Sources remain adapter metadata until sync/index commands are explicitly run.",
            "Missing source families may be acceptable for early drafts, but they must be understood before handoff.",
        ],
    )


def _step_replay(bundle: DynamicPlatformBundle, *, fixture_path: Path, fixture_exists: bool) -> BootstrapStep:
    return BootstrapStep(
        step_id="decision_fixture",
        status="ready" if fixture_exists else "missing",
        title="Golden decision fixture",
        required_artifacts=[str(fixture_path)],
        safe_commands=[f"python -m scripts.tenant shadow-runtime-replay --tenant {bundle.tenant.tenant_key}"],
        blockers=[] if fixture_exists else ["shadow_decision_fixture_missing"],
        notes=[
            "Decision fixtures prove that the tenant topology can represent expected capability/agent/source contracts.",
        ],
    )


def _step_package(bundle: DynamicPlatformBundle) -> BootstrapStep:
    return BootstrapStep(
        step_id="offline_package",
        status="ready_to_generate",
        title="Offline tenant preparation package",
        required_artifacts=[f"tmp/tenant_packages/{bundle.tenant.tenant_key}"],
        safe_commands=[f"python -m scripts.tenant package --tenant {bundle.tenant.tenant_key} --force"],
        notes=[
            "Package generation writes only text artifacts under tmp/tenant_packages.",
            "It does not start Docker, post Slack messages, or call external sources.",
        ],
    )


def _step_handoff(bundle: DynamicPlatformBundle) -> BootstrapStep:
    return BootstrapStep(
        step_id="handoff_gate",
        status="ready_to_check",
        title="Offline handoff readiness",
        required_artifacts=["generated tenant packages"],
        safe_commands=[
            "python -m scripts.tenant package-audit-all --package-root tmp\\tenant_packages --allow-missing-shadow",
            "python -m scripts.tenant handoff-readiness --package-root tmp\\tenant_packages --allow-missing-shadow",
        ],
        notes=[
            f"Runtime strategy remains {bundle.tenant.runtime_strategy}.",
            "Live dynamic routing remains disabled until a separate adapter rollout is implemented.",
        ],
    )
