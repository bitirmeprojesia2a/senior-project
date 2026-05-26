"""Offline handoff readiness for dynamic tenant preparation.

This module is intentionally a reporting layer. It validates generated tenant
packages and the shadow-only adapter draft without starting Docker, Slack, API,
router, agents, RAG, DB, or LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.decision_shadow import default_shadow_fixture_path, load_shadow_decision_cases
from src.dynamic_platform.loader import DynamicPlatformLoadError, DynamicPlatformPaths, load_tenant_bundle
from src.dynamic_platform.package_audit import run_tenant_package_portfolio_audit
from src.dynamic_platform.portfolio_audit import run_tenant_portfolio_audit
from src.dynamic_platform.portability_audit import run_tenant_portability_portfolio_audit
from src.dynamic_platform.registry_catalog import build_registry_catalog
from src.dynamic_platform.runtime_adapter_draft import DynamicRuntimeAdapterDraft, DynamicRuntimeRequest


@dataclass(frozen=True)
class AdapterDraftSmokeRecord:
    tenant_key: str
    ok: bool
    query: str
    requested_capabilities: list[str]
    preview: dict[str, Any] | None = None
    live_refusal: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "query": self.query,
            "requested_capabilities": self.requested_capabilities,
            "preview": self.preview,
            "live_refusal": self.live_refusal,
            "error": self.error,
        }


@dataclass(frozen=True)
class DynamicPlatformHandoffReadinessReport:
    ok: bool
    config_root: str
    package_root: str
    summary: dict[str, Any]
    registry_catalog: dict[str, Any]
    portfolio_audit: dict[str, Any]
    portability_audit: dict[str, Any]
    package_audit: dict[str, Any]
    adapter_draft_smoke: list[AdapterDraftSmokeRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "config_root": self.config_root,
            "package_root": self.package_root,
            "summary": self.summary,
            "registry_catalog": self.registry_catalog,
            "portfolio_audit": self.portfolio_audit,
            "portability_audit": self.portability_audit,
            "package_audit": self.package_audit,
            "adapter_draft_smoke": [record.to_dict() for record in self.adapter_draft_smoke],
            "notes": self.notes,
        }


def run_handoff_readiness(
    *,
    config_root: str | Path = "configs/dynamic_platform",
    package_root: str | Path = "tmp/tenant_packages",
    require_quality_gates: bool = True,
) -> DynamicPlatformHandoffReadinessReport:
    paths = DynamicPlatformPaths.from_root(config_root)
    package_root_path = Path(package_root)
    config_root_value = config_root

    registry = build_registry_catalog(config_root=config_root_value)
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
    tenant_keys = _tenant_keys(paths)
    adapter_records = [_adapter_draft_smoke(tenant_key, config_root=config_root_value) for tenant_key in tenant_keys]
    compose_isolation_ok = _package_compose_isolation_ok(package_audit)

    summary = {
        "tenant_count": len(tenant_keys),
        "registry_ok": registry.ok,
        "portfolio_ok": portfolio.ok,
        "portability_ok": portability.ok,
        "package_audit_ok": package_audit.ok,
        "package_compose_isolation_ok": compose_isolation_ok,
        "adapter_draft_smoke_passed": sum(1 for record in adapter_records if record.ok),
        "adapter_draft_smoke_failed": sum(1 for record in adapter_records if not record.ok),
        "tenants": tenant_keys,
    }
    ok = (
        registry.ok
        and portfolio.ok
        and portability.ok
        and package_audit.ok
        and all(record.ok for record in adapter_records)
    )
    return DynamicPlatformHandoffReadinessReport(
        ok=ok,
        config_root=str(paths.root),
        package_root=str(package_root_path),
        summary=summary,
        registry_catalog=registry.to_dict(),
        portfolio_audit=portfolio.to_dict(),
        portability_audit=portability.to_dict(),
        package_audit=package_audit.to_dict(),
        adapter_draft_smoke=adapter_records,
        notes=[
            "Handoff readiness is offline; it does not start Docker, Slack, API, router, agents, RAG, DB, or LLM.",
            "Adapter draft smoke requires empty user-facing preview answers and explicit live-request refusal.",
            "Tenants with classic_protected strategy remain owned by their existing classic runtime.",
        ],
    )


def _tenant_keys(paths: DynamicPlatformPaths) -> list[str]:
    if not paths.tenants_dir.exists():
        return []
    return sorted(path.stem for path in paths.tenants_dir.glob("*.yaml"))


def _package_compose_isolation_ok(package_audit) -> bool:
    if not package_audit.records:
        return False
    for record in package_audit.records:
        checks = ((record.safety_audit or {}).get("checks") or {}) if record.safety_audit else {}
        if checks.get("package_compose_isolation_ok") is not True:
            return False
    return True


def _adapter_draft_smoke(tenant_key: str, *, config_root: str | Path) -> AdapterDraftSmokeRecord:
    try:
        bundle = load_tenant_bundle(tenant_key, config_root=config_root)
        sample = _sample_request(bundle)
        adapter = DynamicRuntimeAdapterDraft(bundle)
        preview = adapter.preview(sample)
        refusal = adapter.handle_live_request(sample)
    except (DynamicPlatformLoadError, OSError, ValueError) as exc:
        return AdapterDraftSmokeRecord(
            tenant_key=tenant_key,
            ok=False,
            query="",
            requested_capabilities=[],
            error=str(exc),
        )

    preview_payload = preview.to_dict()
    refusal_payload = refusal.to_dict()
    ok = (
        preview_payload["answer"] == ""
        and preview_payload["answer_status"] == "shadow_decision_only"
        and refusal_payload["answer"] == ""
        and refusal_payload["answer_status"] == "unsafe_to_answer"
        and preview_payload.get("telemetry", {}).get("adapter_status") == "draft_shadow_only_not_wired"
    )
    return AdapterDraftSmokeRecord(
        tenant_key=tenant_key,
        ok=ok,
        query=sample.query,
        requested_capabilities=sample.requested_capabilities,
        preview=preview_payload,
        live_refusal=refusal_payload,
        error=None if ok else "adapter_draft_contract_violation",
    )


def _sample_request(bundle) -> DynamicRuntimeRequest:
    fixture = default_shadow_fixture_path(bundle.tenant.tenant_key)
    query = "Tenant destek sorusu"
    capabilities: list[str] = []
    if fixture.exists():
        cases = load_shadow_decision_cases(fixture)
        if cases:
            query = cases[0].query
            capabilities = list(cases[0].expected_capabilities)
    if not capabilities and bundle.domain_pack.capabilities:
        first_capability = bundle.domain_pack.capabilities[0]
        capabilities = [first_capability.capability_id]
        query = first_capability.display_name or first_capability.capability_id
    return DynamicRuntimeRequest(
        tenant_key=bundle.tenant.tenant_key,
        conversation_id="handoff-readiness-shadow",
        user_id="offline-handoff",
        query=query,
        locale=bundle.tenant.locale,
        timezone=bundle.tenant.timezone,
        requested_capabilities=capabilities,
    )
