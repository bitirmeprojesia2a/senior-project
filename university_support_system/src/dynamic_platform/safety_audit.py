"""Safety audit for keeping dynamic platform work out of the classic runtime."""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.compose_isolation_audit import run_compose_isolation_audit
from src.dynamic_platform.loader import DynamicPlatformPaths
from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.runtime_env_check import check_runtime_env

CLASSIC_RUNTIME_DIRS = (
    Path("src/orchestrators"),
    Path("src/routing"),
    Path("src/agents"),
    Path("src/slack"),
    Path("src/api"),
)


@dataclass(frozen=True)
class SafetyAuditIssue:
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
class SafetyAuditReport:
    tenant_key: str
    ok: bool = True
    checks: dict[str, bool] = field(default_factory=dict)
    errors: list[SafetyAuditIssue] = field(default_factory=list)
    warnings: list[SafetyAuditIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_error(self, code: str, message: str, *, path: str | None = None) -> None:
        self.errors.append(SafetyAuditIssue("error", code, message, path))
        self.ok = False

    def add_warning(self, code: str, message: str, *, path: str | None = None) -> None:
        self.warnings.append(SafetyAuditIssue("warning", code, message, path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "checks": self.checks,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
        }


def run_safety_audit(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    env_file: str | Path | None = None,
    package_dir: str | Path | None = None,
    classic_runtime_dirs: tuple[Path, ...] = CLASSIC_RUNTIME_DIRS,
    require_quality_gates: bool = True,
) -> SafetyAuditReport:
    report = SafetyAuditReport(
        tenant_key=bundle.tenant.tenant_key,
        notes=[
            "Safety audit is offline and does not start Docker, Slack, API, router, agents, or model downloads.",
            "Dynamic platform code must stay outside the classic runtime import path until an explicit adapter phase.",
        ],
    )
    _check_classic_runtime_imports(report, classic_runtime_dirs)
    _check_runtime_strategy(report, bundle)
    if env_file:
        _check_env_file(report, bundle, config_root=config_root, env_file=env_file, require_quality_gates=require_quality_gates)
    if package_dir:
        _check_package_draft_markers(report, bundle, config_root=config_root, package_dir=Path(package_dir))
    return report


def _check_classic_runtime_imports(report: SafetyAuditReport, runtime_dirs: tuple[Path, ...]) -> None:
    offenders: list[Path] = []
    for root in runtime_dirs:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if "dynamic_platform" in text:
                offenders.append(path)
    report.checks["classic_runtime_import_isolated"] = not offenders
    for path in offenders:
        report.add_error(
            "classic_runtime_imports_dynamic_platform",
            "Classic runtime module imports or references dynamic_platform.",
            path=str(path),
        )


def _check_runtime_strategy(report: SafetyAuditReport, bundle: DynamicPlatformBundle) -> None:
    if bundle.tenant.tenant_key == "omu":
        is_safe = bundle.tenant.runtime_strategy == "classic_protected"
        report.checks["omu_runtime_strategy_classic_protected"] = is_safe
        if not is_safe:
            report.add_error(
                "omu_runtime_strategy_not_classic_protected",
                f"OMU tenant must remain classic_protected, got {bundle.tenant.runtime_strategy}.",
            )
    else:
        report.checks["non_omu_runtime_strategy_not_forced_classic"] = True
        if bundle.tenant.runtime_strategy == "dynamic_on":
            report.add_warning(
                "dynamic_on_requires_live_adapter_review",
                "dynamic_on should not be used until live runtime adapter and replay gates are explicitly approved.",
            )


def _check_env_file(
    report: SafetyAuditReport,
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    env_file: str | Path,
    require_quality_gates: bool,
) -> None:
    env_report = check_runtime_env(
        bundle,
        config_root=config_root,
        env_file=env_file,
        require_quality_gates=require_quality_gates,
    )
    report.checks["runtime_env_check_ok"] = env_report.ok
    if not env_report.ok:
        for issue in env_report.errors:
            report.add_error(
                f"runtime_env_{issue.code}",
                issue.message,
                path=str(env_file),
            )


def _check_package_draft_markers(
    report: SafetyAuditReport,
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    package_dir: Path,
) -> None:
    package_manifest_path = package_dir / "package_manifest.json"
    manifest_path = package_dir / "compose_launch_manifest.json"
    override_path = package_dir / "docker-compose.tenant.override.draft.yml"
    onboarding_path = package_dir / "onboarding_preview.md"
    config_snapshot_path = package_dir / "config_snapshot.json"
    handoff_index_path = package_dir / "handoff_index.json"
    portability_audit_path = package_dir / "portability_audit.json"
    _check_package_manifest(report, package_manifest_path, package_dir)
    _check_config_snapshot(report, bundle, config_root=config_root, config_snapshot_path=config_snapshot_path)
    _check_handoff_index(report, bundle, package_dir=package_dir, handoff_index_path=handoff_index_path)
    _check_package_portability_audit(report, bundle, portability_audit_path=portability_audit_path)
    if not manifest_path.exists():
        report.checks["package_compose_manifest_draft"] = False
        report.add_warning("package_compose_manifest_missing", "Package has no compose launch manifest.", path=str(manifest_path))
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            report.checks["package_compose_manifest_draft"] = False
            report.add_error("package_compose_manifest_invalid", f"Could not read manifest: {exc}", path=str(manifest_path))
        else:
            is_draft = manifest.get("safety_status") == "draft_do_not_run"
            report.checks["package_compose_manifest_draft"] = is_draft
            if not is_draft:
                report.add_error(
                    "package_compose_manifest_not_draft",
                    "Compose launch manifest must stay draft_do_not_run.",
                    path=str(manifest_path),
                )
    if override_path.exists():
        text = override_path.read_text(encoding="utf-8")
        has_marker = "DRAFT ONLY" in text
        report.checks["package_compose_override_draft_marker"] = has_marker
        if not has_marker:
            report.add_error(
                "package_compose_override_missing_draft_marker",
                "Draft compose override must contain DRAFT ONLY marker.",
                path=str(override_path),
            )
    else:
        report.checks["package_compose_override_draft_marker"] = False
        report.add_warning("package_compose_override_missing", "Package has no draft compose override.", path=str(override_path))
    _check_compose_isolation(report, bundle, package_dir=package_dir)
    report.checks["package_onboarding_preview_exists"] = onboarding_path.exists()
    if not onboarding_path.exists():
        report.add_warning(
            "package_onboarding_preview_missing",
            "Package has no onboarding preview.",
            path=str(onboarding_path),
        )


def _check_handoff_index(
    report: SafetyAuditReport,
    bundle: DynamicPlatformBundle,
    *,
    package_dir: Path,
    handoff_index_path: Path,
) -> None:
    if not handoff_index_path.exists():
        report.checks["package_handoff_index_exists"] = False
        report.checks["package_handoff_index_offline_safe"] = False
        report.checks["package_handoff_required_artifacts_present"] = False
        report.add_error("package_handoff_index_missing", "Package has no handoff_index.json.", path=str(handoff_index_path))
        return
    try:
        payload = json.loads(handoff_index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.checks["package_handoff_index_exists"] = False
        report.checks["package_handoff_index_offline_safe"] = False
        report.checks["package_handoff_required_artifacts_present"] = False
        report.add_error("package_handoff_index_invalid", f"Could not read handoff index: {exc}", path=str(handoff_index_path))
        return

    report.checks["package_handoff_index_exists"] = True
    offline_safe = (
        payload.get("tenant_key") == bundle.tenant.tenant_key
        and payload.get("handoff_status") == "offline_prepared_not_wired"
        and payload.get("live_runtime_authorized") is False
    )
    report.checks["package_handoff_index_offline_safe"] = offline_safe
    if not offline_safe:
        report.add_error(
            "package_handoff_index_not_offline_safe",
            "handoff_index.json must match the tenant and keep live_runtime_authorized=false.",
            path=str(handoff_index_path),
        )

    missing_artifacts = [
        str(name)
        for name in payload.get("required_artifacts_before_handoff") or []
        if not (package_dir / str(name)).exists()
    ]
    report.checks["package_handoff_required_artifacts_present"] = not missing_artifacts
    if missing_artifacts:
        report.add_error(
            "package_handoff_required_artifact_missing",
            "handoff_index.json references required artifacts that are missing from the package.",
            path=str(handoff_index_path),
        )

    commands = "\n".join(str(item) for item in payload.get("safe_verification_order") or [])
    has_verification_order = all(
        needle in commands for needle in ("safety-audit", "compose-isolation-audit", "handoff-readiness")
    )
    report.checks["package_handoff_verification_order_present"] = has_verification_order
    if not has_verification_order:
        report.add_error(
            "package_handoff_verification_order_incomplete",
            "handoff_index.json must include safety, compose isolation, and handoff readiness verification commands.",
            path=str(handoff_index_path),
        )


def _check_package_portability_audit(
    report: SafetyAuditReport,
    bundle: DynamicPlatformBundle,
    *,
    portability_audit_path: Path,
) -> None:
    if not portability_audit_path.exists():
        report.checks["package_portability_audit_ok"] = False
        report.add_error(
            "package_portability_audit_missing",
            "Package has no portability_audit.json.",
            path=str(portability_audit_path),
        )
        return
    try:
        payload = json.loads(portability_audit_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.checks["package_portability_audit_ok"] = False
        report.add_error(
            "package_portability_audit_invalid",
            f"Could not read portability audit: {exc}",
            path=str(portability_audit_path),
        )
        return
    ok = payload.get("tenant_key") == bundle.tenant.tenant_key and payload.get("ok") is True
    report.checks["package_portability_audit_ok"] = ok
    if not ok:
        report.add_error(
            "package_portability_audit_failed",
            "portability_audit.json must match the tenant and report ok=true.",
            path=str(portability_audit_path),
        )


def _check_compose_isolation(
    report: SafetyAuditReport,
    bundle: DynamicPlatformBundle,
    *,
    package_dir: Path,
) -> None:
    audit = run_compose_isolation_audit(bundle, package_dir=package_dir)
    report.checks["package_compose_isolation_ok"] = audit.ok
    for issue in audit.errors:
        report.add_error(
            f"compose_isolation_{issue.code}",
            issue.message,
            path=issue.path,
        )
    for issue in audit.warnings:
        report.add_warning(
            f"compose_isolation_{issue.code}",
            issue.message,
            path=issue.path,
        )


def _check_config_snapshot(
    report: SafetyAuditReport,
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    config_snapshot_path: Path,
) -> None:
    if not config_snapshot_path.exists():
        report.checks["package_config_snapshot_exists"] = False
        report.add_warning("package_config_snapshot_missing", "Package has no config_snapshot.json.", path=str(config_snapshot_path))
        return
    try:
        snapshot = json.loads(config_snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.checks["package_config_snapshot_exists"] = False
        report.add_error("package_config_snapshot_invalid", f"Could not read config snapshot: {exc}", path=str(config_snapshot_path))
        return
    roles = {record.get("role") for record in snapshot.get("files") or []}
    required_roles = {"tenant_profile", "domain_pack", "agent_pack", "source_catalog"}
    is_safe = snapshot.get("safety_status") == "offline_handoff_only"
    is_complete = required_roles.issubset(roles)
    report.checks["package_config_snapshot_exists"] = is_safe and is_complete
    if not is_safe or not is_complete:
        report.add_error(
            "package_config_snapshot_incomplete",
            "config_snapshot.json must be offline_handoff_only and include tenant/domain/agent/source roles.",
            path=str(config_snapshot_path),
        )
        report.checks["package_config_snapshot_hashes_match"] = False
        return

    try:
        expected_hashes = _current_config_hashes(bundle, config_root=config_root)
    except OSError as exc:
        report.checks["package_config_snapshot_hashes_match"] = False
        report.add_error(
            "package_config_snapshot_current_config_unreadable",
            f"Could not read current dynamic config files: {exc}",
            path=str(config_snapshot_path),
        )
        return
    records_by_role = {record.get("role"): record for record in snapshot.get("files") or []}
    mismatch_count = 0
    for role, expected_hash in expected_hashes.items():
        record = records_by_role.get(role)
        actual_hash = record.get("sha256") if isinstance(record, dict) else None
        if actual_hash != expected_hash:
            mismatch_count += 1
            report.add_error(
                "package_config_snapshot_hash_mismatch",
                "config_snapshot.json does not match current tenant/domain/agent/source YAML content.",
                path=str(config_snapshot_path),
            )
    report.checks["package_config_snapshot_hashes_match"] = mismatch_count == 0


def _current_config_hashes(bundle: DynamicPlatformBundle, *, config_root: str | Path) -> dict[str, str]:
    paths = DynamicPlatformPaths.from_root(config_root)
    records = {
        "tenant_profile": paths.tenant_path(bundle.tenant.tenant_key),
        "domain_pack": paths.domain_pack_path(bundle.domain_pack.domain_pack),
        "agent_pack": paths.agent_pack_path(bundle.agent_pack.agent_pack),
        "source_catalog": paths.source_catalog_path(bundle.source_catalog.source_catalog),
    }
    return {role: hashlib.sha256(path.read_bytes()).hexdigest() for role, path in records.items()}


def _check_package_manifest(report: SafetyAuditReport, manifest_path: Path, package_dir: Path) -> None:
    if not manifest_path.exists():
        report.checks["package_manifest_offline_handoff"] = False
        report.checks["package_manifest_hashes_ok"] = False
        report.add_warning("package_manifest_missing", "Package has no package_manifest.json.", path=str(manifest_path))
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.checks["package_manifest_offline_handoff"] = False
        report.checks["package_manifest_hashes_ok"] = False
        report.add_error("package_manifest_invalid", f"Could not read package manifest: {exc}", path=str(manifest_path))
        return

    offline = manifest.get("safety_status") == "offline_handoff_only"
    live_blocked = manifest.get("dynamic_live_binding_allowed") is False
    report.checks["package_manifest_offline_handoff"] = offline and live_blocked
    if not offline or not live_blocked:
        report.add_error(
            "package_manifest_not_offline_safe",
            "package_manifest.json must declare offline_handoff_only and dynamic_live_binding_allowed=false.",
            path=str(manifest_path),
        )

    hash_errors = 0
    for record in manifest.get("files") or []:
        relative = record.get("path")
        expected_hash = record.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            hash_errors += 1
            report.add_error(
                "package_manifest_file_record_invalid",
                "Manifest file record must include string path and sha256.",
                path=str(manifest_path),
            )
            continue
        path = package_dir / relative
        if not path.exists():
            hash_errors += 1
            report.add_error("package_manifest_file_missing", "Manifest references a missing file.", path=str(path))
            continue
        try:
            content = path.read_text(encoding="utf-8").encode("utf-8")
        except OSError as exc:
            hash_errors += 1
            report.add_error("package_manifest_file_unreadable", f"Could not read manifest file entry: {exc}", path=str(path))
            continue
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != expected_hash:
            hash_errors += 1
            report.add_error(
                "package_manifest_hash_mismatch",
                "Manifest hash does not match package file content.",
                path=str(path),
            )
    report.checks["package_manifest_hashes_ok"] = hash_errors == 0
