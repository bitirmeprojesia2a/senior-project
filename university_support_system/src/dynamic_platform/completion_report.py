"""Final offline completion report for dynamic platform preparation.

This report is the top-level, no-runtime gate. It combines registry checks,
portfolio checks, package/handoff checks, and tmp-only creation rehearsals so
the team can decide whether the dynamic platform preparation is complete
without touching live services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.genericity_audit import run_genericity_audit
from src.dynamic_platform.handoff_readiness import run_handoff_readiness
from src.dynamic_platform.loader import DynamicPlatformLoadError, DynamicPlatformPaths, load_tenant_bundle
from src.dynamic_platform.package_audit import run_tenant_package_portfolio_audit
from src.dynamic_platform.portability_audit import run_tenant_portability_portfolio_audit
from src.dynamic_platform.portfolio_audit import run_tenant_portfolio_audit
from src.dynamic_platform.registry_catalog import build_registry_catalog
from src.dynamic_platform.tenant_rehearsal import run_draft_pack_creation_rehearsal, run_tenant_creation_rehearsal


@dataclass(frozen=True)
class CompletionGate:
    gate_id: str
    ok: bool
    message: str
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "ok": self.ok,
            "message": self.message,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class DynamicPlatformCompletionReport:
    ok: bool
    status: str
    config_root: str
    package_root: str
    output_root: str
    summary: dict[str, Any]
    gates: list[CompletionGate]
    blocked_live_items: list[str] = field(default_factory=list)
    safe_next_commands: list[str] = field(default_factory=list)
    optional_no_download_smoke_commands: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "config_root": self.config_root,
            "package_root": self.package_root,
            "output_root": self.output_root,
            "summary": self.summary,
            "gates": [gate.to_dict() for gate in self.gates],
            "blocked_live_items": self.blocked_live_items,
            "safe_next_commands": self.safe_next_commands,
            "optional_no_download_smoke_commands": self.optional_no_download_smoke_commands,
            "notes": self.notes,
        }


def run_dynamic_platform_completion_report(
    *,
    config_root: str | Path = "configs/dynamic_platform",
    package_root: str | Path = "tmp/tenant_packages",
    output_root: str | Path = "tmp/dynamic_platform_completion",
    require_quality_gates: bool = True,
) -> DynamicPlatformCompletionReport:
    paths = DynamicPlatformPaths.from_root(config_root)
    config_root_value = config_root
    package_root_path = Path(package_root)
    output_root_path = Path(output_root)

    registry = build_registry_catalog(config_root=config_root_value)
    genericity = run_genericity_audit()
    portfolio = run_tenant_portfolio_audit(
        config_root=config_root_value,
        require_shadow_fixture=require_quality_gates,
    )
    portability = run_tenant_portability_portfolio_audit(config_root=config_root_value)
    package_audit = run_tenant_package_portfolio_audit(
        config_root=config_root_value,
        package_root=package_root_path,
        require_quality_gates=require_quality_gates,
    )
    handoff = run_handoff_readiness(
        config_root=config_root_value,
        package_root=package_root_path,
        require_quality_gates=require_quality_gates,
    )
    creation = _run_seed_creation_rehearsal(
        registry.to_dict(),
        config_root=config_root_value,
        output_root=output_root_path,
    )
    pack_creation = run_draft_pack_creation_rehearsal(
        tenant_key="completion_pack_rehearsal",
        display_name="Completion Pack Rehearsal",
        bot_name="Completion Support Bot",
        domain_pack="completion_domain_rehearsal",
        domain_display_name="Completion Domain Rehearsal",
        agent_pack="completion_agents_rehearsal",
        agent_pack_display_name="Completion Agents Rehearsal",
        capability_specs=[
            "policy_lookup:Policy Lookup",
            "contact_lookup:Contact Lookup",
        ],
        agent_specs=["support:Support"],
        config_root=config_root_value,
        output_dir=output_root_path / "pack_creation",
        force=True,
    )

    gates = [
        CompletionGate(
            gate_id="registry_catalog",
            ok=registry.ok,
            message="Dynamic registry references are valid." if registry.ok else "Dynamic registry has errors.",
            detail=_compact_registry(registry.to_dict()),
        ),
        CompletionGate(
            gate_id="genericity_audit",
            ok=genericity.ok,
            message="Dynamic core stayed domain-neutral." if genericity.ok else "Dynamic core leaked domain-specific behavior.",
            detail=genericity.to_dict().get("summary") or {},
        ),
        CompletionGate(
            gate_id="portfolio_audit",
            ok=portfolio.ok,
            message="All configured tenant profiles pass offline portfolio checks."
            if portfolio.ok
            else "One or more tenant profiles failed portfolio checks.",
            detail=portfolio.to_dict().get("summary") or {},
        ),
        CompletionGate(
            gate_id="portability_audit",
            ok=portability.ok,
            message="Configured tenants pass portability checks."
            if portability.ok
            else "One or more tenants leak non-portable assumptions.",
            detail=portability.to_dict().get("summary") or {},
        ),
        CompletionGate(
            gate_id="package_audit",
            ok=package_audit.ok,
            message="Generated tenant packages pass safety audit."
            if package_audit.ok
            else "Generated tenant packages are missing or stale.",
            detail=package_audit.to_dict().get("summary") or {},
        ),
        CompletionGate(
            gate_id="handoff_readiness",
            ok=handoff.ok,
            message="Offline handoff readiness passed." if handoff.ok else "Offline handoff readiness failed.",
            detail=handoff.to_dict().get("summary") or {},
        ),
        CompletionGate(
            gate_id="tenant_creation_rehearsal",
            ok=creation.ok,
            message="A new tenant can be created, packaged, and audited under tmp."
            if creation.ok
            else "New tenant creation rehearsal failed.",
            detail=_compact_rehearsal(creation.to_dict()),
        ),
        CompletionGate(
            gate_id="pack_creation_rehearsal",
            ok=pack_creation.ok,
            message="A new domain pack, agent pack, and tenant can be created under tmp."
            if pack_creation.ok
            else "Draft pack creation rehearsal failed.",
            detail=_compact_rehearsal(pack_creation.to_dict()),
        ),
    ]
    ok = all(gate.ok for gate in gates)
    summary = {
        "gate_count": len(gates),
        "passed": sum(1 for gate in gates if gate.ok),
        "failed": sum(1 for gate in gates if not gate.ok),
        "configured_tenant_count": (registry.to_dict().get("summary") or {}).get("tenant_count", 0),
        "package_tenant_count": (package_audit.to_dict().get("summary") or {}).get("tenant_count", 0),
        "offline_completion_percent": round(100 * sum(1 for gate in gates if gate.ok) / len(gates), 1),
        "live_runtime_authorized": False,
        "classic_runtime_import_isolated": _classic_import_isolated(package_audit.to_dict()),
    }
    return DynamicPlatformCompletionReport(
        ok=ok,
        status="offline_handoff_ready" if ok else "offline_handoff_blocked",
        config_root=str(paths.root),
        package_root=str(package_root_path),
        output_root=str(output_root_path),
        summary=summary,
        gates=gates,
        blocked_live_items=[
            "Live dynamic Slack/API/router adapter is not wired in this phase.",
            "Dynamic runtime must remain shadow-only until explicit adapter rollout and replay approval.",
            "Draft compose artifacts still require docker compose config and a separate run approval before any container start.",
            "No package or completion report authorizes cache, conversation-state, uploaded-file, or DB writes from dynamic runtime.",
        ],
        safe_next_commands=[
            "python -m scripts.tenant package-audit-all --package-root tmp\\tenant_packages --allow-missing-shadow",
            "python -m scripts.tenant handoff-readiness --package-root tmp\\tenant_packages --allow-missing-shadow",
            "python -m scripts.tenant completion-report --package-root tmp\\tenant_packages --allow-missing-shadow",
        ],
        optional_no_download_smoke_commands=[
            "python -m scripts.tenant runtime-query-smoke --tenant acme_demo",
            "python -m scripts.tenant runtime-query-smoke --tenant city_demo",
        ],
        notes=[
            "Completion report is offline and does not start Docker, Slack, API, router, agents, RAG, DB, or LLM.",
            "The report proves preparation and portability, not production activation.",
            "Optional no-download smoke commands only call an already running dynamic endpoint.",
            "Configured classic tenants remain owned by their existing runtime.",
        ],
    )


def _run_seed_creation_rehearsal(
    registry_payload: dict[str, Any],
    *,
    config_root: str | Path,
    output_root: Path,
):
    seed = _seed_tenant(registry_payload)
    if seed is None:
        report = run_draft_pack_creation_rehearsal(
            tenant_key="completion_creation_rehearsal",
            display_name="Completion Creation Rehearsal",
            bot_name="Completion Support Bot",
            domain_pack="completion_seed_domain",
            domain_display_name="Completion Seed Domain",
            agent_pack="completion_seed_agents",
            agent_pack_display_name="Completion Seed Agents",
            capability_specs=["policy_lookup:Policy Lookup"],
            agent_specs=["support:Support"],
            config_root=config_root,
            output_dir=output_root / "tenant_creation",
            force=True,
        )
        return report
    try:
        bundle = load_tenant_bundle(seed["tenant_key"], config_root=config_root)
    except DynamicPlatformLoadError:
        return run_draft_pack_creation_rehearsal(
            tenant_key="completion_creation_rehearsal",
            display_name="Completion Creation Rehearsal",
            bot_name="Completion Support Bot",
            domain_pack="completion_seed_domain",
            domain_display_name="Completion Seed Domain",
            agent_pack="completion_seed_agents",
            agent_pack_display_name="Completion Seed Agents",
            capability_specs=["policy_lookup:Policy Lookup"],
            agent_specs=["support:Support"],
            config_root=config_root,
            output_dir=output_root / "tenant_creation",
            force=True,
        )
    return run_tenant_creation_rehearsal(
        tenant_key="completion_creation_rehearsal",
        display_name="Completion Creation Rehearsal",
        bot_name="Completion Support Bot",
        domain_pack=bundle.domain_pack.domain_pack,
        agent_pack=bundle.agent_pack.agent_pack,
        config_root=config_root,
        output_dir=output_root / "tenant_creation",
        force=True,
    )


def _seed_tenant(registry_payload: dict[str, Any]) -> dict[str, Any] | None:
    tenants = registry_payload.get("tenants") or []
    for tenant in tenants:
        if tenant.get("runtime_strategy") == "dynamic_shadow":
            return tenant
    return tenants[0] if tenants else None


def _compact_registry(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    return {
        "domain_pack_count": summary.get("domain_pack_count", 0),
        "agent_pack_count": summary.get("agent_pack_count", 0),
        "source_catalog_count": summary.get("source_catalog_count", 0),
        "tenant_count": summary.get("tenant_count", 0),
        "runtime_strategy_counts": summary.get("runtime_strategy_counts", {}),
        "error_count": summary.get("error_count", 0),
        "warning_count": summary.get("warning_count", 0),
    }


def _compact_rehearsal(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    return {
        "output_dir": payload.get("output_dir"),
        "package_dir": payload.get("package_dir"),
        "domain_pack": summary.get("domain_pack"),
        "agent_pack": summary.get("agent_pack"),
        "source_count": summary.get("source_count"),
        "enabled_source_count": summary.get("enabled_source_count"),
        "checks": payload.get("checks") or {},
    }


def _classic_import_isolated(package_audit_payload: dict[str, Any]) -> bool:
    records = package_audit_payload.get("records") or []
    if not records:
        return False
    for record in records:
        checks = ((record.get("safety_audit") or {}).get("checks") or {})
        if checks.get("classic_runtime_import_isolated") is not True:
            return False
    return True
