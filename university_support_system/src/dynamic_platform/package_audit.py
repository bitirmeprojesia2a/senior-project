"""Portfolio-wide offline audit for generated tenant packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.loader import DynamicPlatformLoadError, DynamicPlatformPaths, load_tenant_bundle
from src.dynamic_platform.safety_audit import run_safety_audit


@dataclass(frozen=True)
class TenantPackageAuditRecord:
    tenant_key: str
    ok: bool
    package_dir: str
    env_file: str
    safety_audit: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "package_dir": self.package_dir,
            "env_file": self.env_file,
            "safety_audit": self.safety_audit,
            "error": self.error,
        }


@dataclass(frozen=True)
class TenantPackagePortfolioAuditReport:
    ok: bool
    config_root: str
    package_root: str
    summary: dict[str, Any]
    records: list[TenantPackageAuditRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "config_root": self.config_root,
            "package_root": self.package_root,
            "summary": self.summary,
            "records": [record.to_dict() for record in self.records],
            "notes": self.notes,
        }


def run_tenant_package_portfolio_audit(
    *,
    config_root: str | Path = "configs/dynamic_platform",
    package_root: str | Path = "tmp/tenant_packages",
    require_quality_gates: bool = True,
) -> TenantPackagePortfolioAuditReport:
    config_paths = DynamicPlatformPaths.from_root(config_root)
    package_root_path = Path(package_root)
    tenant_keys = _tenant_keys(config_paths)
    records = [
        _audit_package(
            tenant_key,
            config_root=config_root,
            package_root=package_root_path,
            require_quality_gates=require_quality_gates,
        )
        for tenant_key in tenant_keys
    ]
    summary = {
        "tenant_count": len(records),
        "passed": sum(1 for record in records if record.ok),
        "failed": sum(1 for record in records if not record.ok),
        "tenants": tenant_keys,
    }
    return TenantPackagePortfolioAuditReport(
        ok=all(record.ok for record in records),
        config_root=str(config_paths.root),
        package_root=str(package_root_path),
        summary=summary,
        records=records,
        notes=[
            "Package portfolio audit is offline; it does not start Docker, Slack, API, router, agents, RAG, DB, or LLM.",
            "Each generated tenant package is checked with safety-audit, including manifest hashes and config snapshot freshness.",
            "Missing packages are reported as failures; generate them with scripts.tenant package before handoff.",
        ],
    )


def _tenant_keys(paths: DynamicPlatformPaths) -> list[str]:
    if not paths.tenants_dir.exists():
        return []
    return sorted(path.stem for path in paths.tenants_dir.glob("*.yaml"))


def _audit_package(
    tenant_key: str,
    *,
    config_root: str | Path,
    package_root: Path,
    require_quality_gates: bool,
) -> TenantPackageAuditRecord:
    package_dir = package_root / tenant_key
    env_file = package_dir / "tenant.env"
    if not package_dir.exists():
        return TenantPackageAuditRecord(
            tenant_key=tenant_key,
            ok=False,
            package_dir=str(package_dir),
            env_file=str(env_file),
            error="tenant_package_directory_missing",
        )
    if not env_file.exists():
        return TenantPackageAuditRecord(
            tenant_key=tenant_key,
            ok=False,
            package_dir=str(package_dir),
            env_file=str(env_file),
            error="tenant_package_env_file_missing",
        )
    try:
        bundle = load_tenant_bundle(tenant_key, config_root=config_root)
        safety = run_safety_audit(
            bundle,
            config_root=config_root,
            env_file=env_file,
            package_dir=package_dir,
            require_quality_gates=require_quality_gates,
        )
    except (DynamicPlatformLoadError, OSError) as exc:
        return TenantPackageAuditRecord(
            tenant_key=tenant_key,
            ok=False,
            package_dir=str(package_dir),
            env_file=str(env_file),
            error=str(exc),
        )
    return TenantPackageAuditRecord(
        tenant_key=tenant_key,
        ok=safety.ok,
        package_dir=str(package_dir),
        env_file=str(env_file),
        safety_audit=safety.to_dict(),
    )
