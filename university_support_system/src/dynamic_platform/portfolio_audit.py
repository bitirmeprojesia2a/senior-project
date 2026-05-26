"""Portfolio-wide offline audit for all configured dynamic tenants."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.genericity_audit import run_genericity_audit
from src.dynamic_platform.loader import DynamicPlatformLoadError, DynamicPlatformPaths, load_tenant_bundle
from src.dynamic_platform.quality_gates import run_quality_gates
from src.dynamic_platform.runtime_adapter_contract import build_runtime_adapter_contract
from src.dynamic_platform.source_ingestion_plan import build_source_ingestion_plan
from src.dynamic_platform.validator import validate_bundle


@dataclass(frozen=True)
class TenantPortfolioRecord:
    tenant_key: str
    ok: bool
    runtime_strategy: str | None
    validation: dict[str, Any] | None = None
    quality_gates: dict[str, Any] | None = None
    source_ingestion_summary: dict[str, Any] | None = None
    runtime_adapter_contract: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "runtime_strategy": self.runtime_strategy,
            "validation": self.validation,
            "quality_gates": self.quality_gates,
            "source_ingestion_summary": self.source_ingestion_summary,
            "runtime_adapter_contract": self.runtime_adapter_contract,
            "error": self.error,
        }


@dataclass(frozen=True)
class TenantPortfolioAuditReport:
    ok: bool
    config_root: str
    summary: dict[str, Any]
    genericity_audit: dict[str, Any]
    records: list[TenantPortfolioRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "config_root": self.config_root,
            "summary": self.summary,
            "genericity_audit": self.genericity_audit,
            "records": [record.to_dict() for record in self.records],
            "notes": self.notes,
        }


def run_tenant_portfolio_audit(
    *,
    config_root: str | Path = "configs/dynamic_platform",
    require_shadow_fixture: bool = True,
) -> TenantPortfolioAuditReport:
    root = Path(config_root)
    paths = DynamicPlatformPaths.from_root(root)
    tenant_keys = _tenant_keys(paths)
    genericity = run_genericity_audit()
    records = [
        _audit_tenant(tenant_key, config_root=root, require_shadow_fixture=require_shadow_fixture)
        for tenant_key in tenant_keys
    ]
    strategies: dict[str, int] = {}
    for record in records:
        if record.runtime_strategy:
            strategies[record.runtime_strategy] = strategies.get(record.runtime_strategy, 0) + 1
    summary = {
        "tenant_count": len(records),
        "passed": sum(1 for record in records if record.ok),
        "failed": sum(1 for record in records if not record.ok),
        "runtime_strategy_counts": dict(sorted(strategies.items())),
        "tenants": tenant_keys,
    }
    ok = genericity.ok and all(record.ok for record in records)
    return TenantPortfolioAuditReport(
        ok=ok,
        config_root=str(root),
        summary=summary,
        genericity_audit=genericity.to_dict(),
        records=records,
        notes=[
            "Portfolio audit is offline; it does not start Docker or call Slack/API/router/agents/RAG/DB/LLM.",
            "Each tenant is checked through validation, quality gates, source ingestion summary, and runtime adapter boundary.",
            "Dynamic live binding remains blocked until an explicit adapter implementation and replay gate are added.",
        ],
    )


def _tenant_keys(paths: DynamicPlatformPaths) -> list[str]:
    if not paths.tenants_dir.exists():
        return []
    return sorted(path.stem for path in paths.tenants_dir.glob("*.yaml"))


def _audit_tenant(
    tenant_key: str,
    *,
    config_root: Path,
    require_shadow_fixture: bool,
) -> TenantPortfolioRecord:
    try:
        bundle = load_tenant_bundle(tenant_key, config_root=config_root)
    except DynamicPlatformLoadError as exc:
        return TenantPortfolioRecord(
            tenant_key=tenant_key,
            ok=False,
            runtime_strategy=None,
            error=str(exc),
        )

    validation = validate_bundle(bundle)
    quality = run_quality_gates(bundle, require_shadow_fixture=require_shadow_fixture)
    source_ingestion = build_source_ingestion_plan(bundle)
    adapter_contract = build_runtime_adapter_contract(bundle)
    adapter_payload = adapter_contract.to_dict()
    ok = (
        validation.ok
        and quality.ok
        and source_ingestion.ok
        and adapter_payload["adapter_status"] == "not_wired"
        and adapter_payload["dynamic_live_binding_allowed"] is False
    )
    return TenantPortfolioRecord(
        tenant_key=tenant_key,
        ok=ok,
        runtime_strategy=bundle.tenant.runtime_strategy,
        validation=validation.to_dict(),
        quality_gates=quality.to_dict(),
        source_ingestion_summary=source_ingestion.to_dict()["summary"],
        runtime_adapter_contract={
            "adapter_status": adapter_payload["adapter_status"],
            "dynamic_live_binding_allowed": adapter_payload["dynamic_live_binding_allowed"],
            "classic_runtime_must_remain_owner": adapter_payload["classic_runtime_must_remain_owner"],
            "allowed_modes": adapter_payload["allowed_modes"],
            "blocked_modes": adapter_payload["blocked_modes"],
        },
    )
