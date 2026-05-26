"""Offline registry inventory for dynamic platform configuration.

This module lists tenant/domain/agent/source catalog files and checks their
cross references without touching any live runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.loader import DynamicPlatformLoadError, DynamicPlatformPaths, load_tenant_bundle, load_yaml_model
from src.dynamic_platform.models import AgentPack, DomainPack, SourceCatalog, TenantProfile
from src.dynamic_platform.validator import validate_bundle


@dataclass(frozen=True)
class RegistryIssue:
    severity: str
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass
class RegistryCatalogReport:
    ok: bool = True
    summary: dict[str, Any] = field(default_factory=dict)
    domain_packs: list[dict[str, Any]] = field(default_factory=list)
    agent_packs: list[dict[str, Any]] = field(default_factory=list)
    source_catalogs: list[dict[str, Any]] = field(default_factory=list)
    tenants: list[dict[str, Any]] = field(default_factory=list)
    errors: list[RegistryIssue] = field(default_factory=list)
    warnings: list[RegistryIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_error(self, code: str, message: str, *, path: str | None = None) -> None:
        self.errors.append(RegistryIssue("error", code, message, path))
        self.ok = False

    def add_warning(self, code: str, message: str, *, path: str | None = None) -> None:
        self.warnings.append(RegistryIssue("warning", code, message, path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "summary": self.summary,
            "domain_packs": self.domain_packs,
            "agent_packs": self.agent_packs,
            "source_catalogs": self.source_catalogs,
            "tenants": self.tenants,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
        }


def build_registry_catalog(*, config_root: str | Path = "configs/dynamic_platform") -> RegistryCatalogReport:
    paths = DynamicPlatformPaths.from_root(config_root)
    report = RegistryCatalogReport(
        notes=[
            "Registry catalog is offline and does not start Docker, Slack, API, router, agents, retrieval, DB, or LLM.",
            "It describes which domain packs, agent packs, source catalogs, and tenants are available for scaffold/package workflows.",
        ]
    )

    domain_packs = _load_all(paths.domain_packs_dir, DomainPack, report)
    agent_packs = _load_all(paths.agent_packs_dir, AgentPack, report)
    source_catalogs = _load_all(paths.source_catalogs_dir, SourceCatalog, report)
    tenants = _load_all(paths.tenants_dir, TenantProfile, report)

    domain_ids = {item.domain_pack for item in domain_packs}
    agent_pack_ids = {item.agent_pack for item in agent_packs}
    source_catalog_ids = {item.source_catalog for item in source_catalogs}
    source_catalog_tenants = {item.source_catalog: item.tenant_key for item in source_catalogs}

    report.domain_packs = [
        {
            "domain_pack": item.domain_pack,
            "display_name": item.display_name,
            "capability_count": len(item.capabilities),
            "capabilities": [capability.capability_id for capability in item.capabilities],
            "path": str(paths.domain_pack_path(item.domain_pack)),
        }
        for item in sorted(domain_packs, key=lambda pack: pack.domain_pack)
    ]
    report.agent_packs = [
        {
            "agent_pack": item.agent_pack,
            "display_name": item.display_name,
            "domain_pack": item.domain_pack,
            "domain_pack_exists": item.domain_pack in domain_ids,
            "agent_count": len(item.agents),
            "agents": [agent.agent_id for agent in item.agents],
            "path": str(paths.agent_pack_path(item.agent_pack)),
        }
        for item in sorted(agent_packs, key=lambda pack: pack.agent_pack)
    ]
    report.source_catalogs = [
        {
            "source_catalog": item.source_catalog,
            "tenant_key": item.tenant_key,
            "source_count": len(item.sources),
            "enabled_source_count": len([source for source in item.sources if source.enabled]),
            "adapters": sorted({source.adapter for source in item.sources}),
            "path": str(paths.source_catalog_path(item.source_catalog)),
        }
        for item in sorted(source_catalogs, key=lambda catalog: catalog.source_catalog)
    ]

    tenant_records: list[dict[str, Any]] = []
    runtime_counts: dict[str, int] = {}
    domain_tenant_counts: dict[str, int] = {}
    for tenant in sorted(tenants, key=lambda item: item.tenant_key):
        runtime_counts[tenant.runtime_strategy] = runtime_counts.get(tenant.runtime_strategy, 0) + 1
        domain_tenant_counts[tenant.domain_pack] = domain_tenant_counts.get(tenant.domain_pack, 0) + 1
        tenant_path = paths.tenant_path(tenant.tenant_key)
        tenant_record = {
            "tenant_key": tenant.tenant_key,
            "display_name": tenant.display_name,
            "runtime_strategy": tenant.runtime_strategy,
            "domain_pack": tenant.domain_pack,
            "agent_pack": tenant.agent_pack,
            "source_catalog": tenant.source_catalog,
            "domain_pack_exists": tenant.domain_pack in domain_ids,
            "agent_pack_exists": tenant.agent_pack in agent_pack_ids,
            "source_catalog_exists": tenant.source_catalog in source_catalog_ids,
            "source_catalog_tenant_matches": source_catalog_tenants.get(tenant.source_catalog) == tenant.tenant_key,
            "validation_ok": None,
            "path": str(tenant_path),
        }
        try:
            bundle = load_tenant_bundle(tenant.tenant_key, config_root=paths.root)
        except DynamicPlatformLoadError as exc:
            tenant_record["validation_ok"] = False
            report.add_error("tenant_bundle_load_failed", str(exc), path=str(tenant_path))
        else:
            validation = validate_bundle(bundle)
            tenant_record["validation_ok"] = validation.ok
            tenant_record["warning_count"] = len(validation.warnings)
            tenant_record["error_count"] = len(validation.errors)
            if not validation.ok:
                report.add_error(
                    "tenant_validation_failed",
                    f"Tenant {tenant.tenant_key} failed validation.",
                    path=str(tenant_path),
                )
        tenant_records.append(tenant_record)
        _audit_tenant_refs(tenant_record, report)
    report.tenants = tenant_records

    for agent_pack in report.agent_packs:
        if not agent_pack["domain_pack_exists"]:
            report.add_error(
                "agent_pack_domain_missing",
                f"Agent pack {agent_pack['agent_pack']} references missing domain pack {agent_pack['domain_pack']}.",
                path=agent_pack["path"],
            )

    report.summary = {
        "domain_pack_count": len(domain_packs),
        "agent_pack_count": len(agent_packs),
        "source_catalog_count": len(source_catalogs),
        "tenant_count": len(tenants),
        "runtime_strategy_counts": dict(sorted(runtime_counts.items())),
        "domain_tenant_counts": dict(sorted(domain_tenant_counts.items())),
        "error_count": len(report.errors),
        "warning_count": len(report.warnings),
    }
    return report


def _load_all(directory: Path, model_type: type[Any], report: RegistryCatalogReport) -> list[Any]:
    records: list[Any] = []
    if not directory.exists():
        report.add_error("registry_directory_missing", f"Registry directory does not exist: {directory}", path=str(directory))
        return records
    for path in sorted(directory.glob("*.yaml")):
        try:
            records.append(load_yaml_model(path, model_type))
        except DynamicPlatformLoadError as exc:
            report.add_error("registry_file_load_failed", str(exc), path=str(path))
    return records


def _audit_tenant_refs(record: dict[str, Any], report: RegistryCatalogReport) -> None:
    tenant_key = record["tenant_key"]
    for field_name, code in (
        ("domain_pack_exists", "tenant_domain_pack_missing"),
        ("agent_pack_exists", "tenant_agent_pack_missing"),
        ("source_catalog_exists", "tenant_source_catalog_missing"),
    ):
        if not record[field_name]:
            report.add_error(
                code,
                f"Tenant {tenant_key} has unresolved registry reference.",
                path=record["path"],
            )
    if not record["source_catalog_tenant_matches"]:
        report.add_error(
            "tenant_source_catalog_owner_mismatch",
            f"Tenant {tenant_key} references a source catalog owned by another tenant.",
            path=record["path"],
        )
