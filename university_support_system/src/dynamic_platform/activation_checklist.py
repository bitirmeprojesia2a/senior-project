"""Offline activation checklist for dynamic tenant pilots.

The checklist answers one operational question: "What is still left before a
dynamic tenant can be tried safely?"  It is deliberately offline and does not
wire Slack/API/router traffic, start Docker, write runtime caches, or authorize
live dynamic answers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.package_audit import run_tenant_package_portfolio_audit
from src.dynamic_platform.pilot_readiness import run_tenant_pilot_readiness
from src.dynamic_platform.runtime_isolation_contract import build_runtime_isolation_contract
from src.dynamic_platform.tenant_package import PACKAGE_MANIFEST_NAME


@dataclass(frozen=True)
class ActivationChecklistStep:
    step_id: str
    ok: bool
    severity: str
    status: str
    message: str
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "ok": self.ok,
            "severity": self.severity,
            "status": self.status,
            "message": self.message,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class DynamicActivationChecklistReport:
    tenant_key: str
    ok: bool
    status: str
    live_runtime_authorized: bool
    config_root: str
    package_root: str
    package_dir: str
    runtime_secrets_dir: str
    output_root: str
    summary: dict[str, Any]
    steps: list[ActivationChecklistStep]
    remaining_work: list[str] = field(default_factory=list)
    safe_next_commands: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "status": self.status,
            "live_runtime_authorized": self.live_runtime_authorized,
            "config_root": self.config_root,
            "package_root": self.package_root,
            "package_dir": self.package_dir,
            "runtime_secrets_dir": self.runtime_secrets_dir,
            "output_root": self.output_root,
            "summary": self.summary,
            "steps": [step.to_dict() for step in self.steps],
            "remaining_work": self.remaining_work,
            "safe_next_commands": self.safe_next_commands,
            "notes": self.notes,
            "artifacts": self.artifacts,
        }


def run_dynamic_activation_checklist(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path = "configs/dynamic_platform",
    package_root: str | Path = "tmp/tenant_packages",
    runtime_secrets_dir: str | Path = "tmp/dynamic_platform_runtime_secrets",
    output_root: str | Path = "tmp/dynamic_platform_activation_checklist",
    include_slack: bool = False,
    require_quality_gates: bool = True,
) -> DynamicActivationChecklistReport:
    tenant_key = bundle.tenant.tenant_key
    package_root_path = Path(package_root)
    package_dir = package_root_path / tenant_key
    runtime_secrets_path = Path(runtime_secrets_dir)
    output_dir = Path(output_root) / tenant_key
    package_env = package_dir / "tenant.env"
    package_manifest = package_dir / PACKAGE_MANIFEST_NAME
    secret_env = runtime_secrets_path / f"{tenant_key}.dynamic_pilot.secrets.env"
    secret_manifest = runtime_secrets_path / f"{tenant_key}.dynamic_pilot.secrets_manifest.json"

    package_audit = run_tenant_package_portfolio_audit(
        config_root=config_root,
        package_root=package_root_path,
        require_quality_gates=require_quality_gates,
    )
    package_record = _find_package_record(package_audit.to_dict(), tenant_key)
    isolation = build_runtime_isolation_contract(bundle)
    no_secret_smoke = run_tenant_pilot_readiness(
        bundle,
        config_root=config_root,
        package_root=package_root_path,
        output_root=output_dir / "pilot_readiness",
        secrets_env_file=package_env,
        mode="no_secret_smoke",
        include_slack=False,
        require_quality_gates=require_quality_gates,
    )
    pilot_env = secret_env if secret_env.exists() else package_env
    dynamic_pilot = run_tenant_pilot_readiness(
        bundle,
        config_root=config_root,
        package_root=package_root_path,
        output_root=output_dir / "pilot_readiness",
        secrets_env_file=pilot_env,
        mode="dynamic_pilot",
        include_slack=include_slack,
        require_quality_gates=require_quality_gates,
    )

    secret_scaffold_ok = _secret_scaffold_ok(
        secret_env=secret_env,
        secret_manifest=secret_manifest,
        package_dir=package_dir,
    )
    steps = [
        _package_step(package_dir=package_dir, package_env=package_env, package_manifest=package_manifest, record=package_record),
        ActivationChecklistStep(
            step_id="package_portfolio_audit",
            ok=package_audit.ok,
            severity="error",
            status="passed" if package_audit.ok else "failed",
            message="All generated tenant packages pass offline package audit."
            if package_audit.ok
            else "One or more generated tenant packages failed offline package audit.",
            detail=package_audit.to_dict().get("summary") or {},
        ),
        ActivationChecklistStep(
            step_id="runtime_isolation_contract",
            ok=isolation.ok and not isolation.live_runtime_allowed,
            severity="error",
            status="passed" if isolation.ok and not isolation.live_runtime_allowed else "failed",
            message="Tenant cache/state/upload isolation contract is present and live runtime remains blocked.",
            detail={
                "namespace_count": len(isolation.namespaces),
                "uploaded_context_source_count": len(isolation.uploaded_context_sources),
                "live_runtime_allowed": isolation.live_runtime_allowed,
            },
        ),
        ActivationChecklistStep(
            step_id="pilot_secret_scaffold",
            ok=secret_scaffold_ok,
            severity="warning",
            status="present" if secret_scaffold_ok else "missing",
            message="Package-external pilot secret scaffold is present."
            if secret_scaffold_ok
            else "Package-external pilot secret scaffold is missing; create it before a dynamic pilot.",
            detail={
                "env_path": str(secret_env),
                "manifest_path": str(secret_manifest),
                "env_exists": secret_env.exists(),
                "manifest_exists": secret_manifest.exists(),
                "outside_tenant_package": _outside_path(secret_env, package_dir),
            },
        ),
        ActivationChecklistStep(
            step_id="no_secret_smoke_readiness",
            ok=no_secret_smoke.ok,
            severity="error",
            status=no_secret_smoke.status,
            message="No-secret smoke readiness passes." if no_secret_smoke.ok else "No-secret smoke readiness is blocked.",
            detail={
                "status": no_secret_smoke.status,
                "live_binding_allowed": no_secret_smoke.live_binding_allowed,
                "blocker_count": len(no_secret_smoke.blockers),
            },
        ),
        _dynamic_pilot_guard_step(dynamic_pilot.to_dict()),
        ActivationChecklistStep(
            step_id="runtime_side_effects",
            ok=_no_runtime_side_effects(no_secret_smoke.to_dict()) and _no_runtime_side_effects(dynamic_pilot.to_dict()),
            severity="error",
            status="clean"
            if _no_runtime_side_effects(no_secret_smoke.to_dict()) and _no_runtime_side_effects(dynamic_pilot.to_dict())
            else "dirty",
            message="Checklist did not start Docker, run build/pull, or touch user-facing runtime.",
            detail={
                "no_secret_smoke": no_secret_smoke.to_dict().get("summary") or {},
                "dynamic_pilot": dynamic_pilot.to_dict().get("summary") or {},
            },
        ),
    ]

    blocking_errors = [step for step in steps if step.severity == "error" and not step.ok]
    warning_count = sum(1 for step in steps if step.severity == "warning" and not step.ok)
    live_ready = bool(dynamic_pilot.ok and dynamic_pilot.live_binding_allowed)
    ok = not blocking_errors
    status = "offline_activation_ready_live_blocked" if ok and not live_ready else "dynamic_pilot_ready" if ok else "offline_activation_blocked"
    summary = {
        "runtime_strategy": bundle.tenant.runtime_strategy,
        "offline_gate_count": len([step for step in steps if step.severity == "error"]),
        "offline_gate_passed": len([step for step in steps if step.severity == "error" and step.ok]),
        "warning_count": warning_count,
        "offline_preparation_percent": _percent(
            len([step for step in steps if step.severity == "error" and step.ok]),
            len([step for step in steps if step.severity == "error"]),
        ),
        "dynamic_pilot_prerequisite_percent": _dynamic_pilot_percent(
            package_ok=bool(package_record and package_record.get("ok")),
            isolation_ok=isolation.ok,
            secret_scaffold_ok=secret_scaffold_ok,
            secret_readiness_ok=bool((dynamic_pilot.to_dict().get("secret_readiness") or {}).get("ok")),
            adapter_ready=dynamic_pilot.live_binding_allowed,
        ),
        "dynamic_pilot_status": dynamic_pilot.status,
        "live_runtime_authorized": False,
        "docker_started": False,
        "build_or_pull_run": False,
        "user_facing_runtime_touched": False,
    }
    report = DynamicActivationChecklistReport(
        tenant_key=tenant_key,
        ok=ok,
        status=status,
        live_runtime_authorized=False,
        config_root=str(Path(config_root)),
        package_root=str(package_root_path),
        package_dir=str(package_dir),
        runtime_secrets_dir=str(runtime_secrets_path),
        output_root=str(output_dir),
        summary=summary,
        steps=steps,
        remaining_work=_remaining_work(dynamic_pilot.to_dict(), secret_scaffold_ok=secret_scaffold_ok),
        safe_next_commands=[
            f"python -m scripts.tenant activation-checklist --tenant {tenant_key} --package-root {package_root_path} --allow-missing-shadow",
            f"python -m scripts.tenant pilot-readiness --tenant {tenant_key} --mode no_secret_smoke --package-root {package_root_path} --secrets-env-file {package_env} --allow-missing-shadow",
            f"python -m scripts.tenant pilot-readiness --tenant {tenant_key} --mode dynamic_pilot --package-root {package_root_path} --secrets-env-file {pilot_env} --allow-missing-shadow",
        ],
        notes=[
            "Activation checklist is offline and does not authorize live runtime.",
            "An OK checklist currently means offline preparation is safe while dynamic live binding remains blocked.",
            "Existing classic runtime remains the protected production path.",
        ],
        artifacts=[
            str(output_dir / "activation_checklist_report.json"),
            str(output_dir / "README.md"),
        ],
    )
    _write_activation_artifacts(report, output_dir)
    return report


def _find_package_record(package_payload: dict[str, Any], tenant_key: str) -> dict[str, Any] | None:
    for record in package_payload.get("records") or []:
        if record.get("tenant_key") == tenant_key:
            return record
    return None


def _package_step(
    *,
    package_dir: Path,
    package_env: Path,
    package_manifest: Path,
    record: dict[str, Any] | None,
) -> ActivationChecklistStep:
    exists = package_dir.exists() and package_env.exists() and package_manifest.exists()
    ok = exists and bool(record and record.get("ok"))
    return ActivationChecklistStep(
        step_id="tenant_package",
        ok=ok,
        severity="error",
        status="passed" if ok else "failed",
        message="Tenant package exists and passes package safety audit."
        if ok
        else "Tenant package is missing, stale, or failed package safety audit.",
        detail={
            "package_dir": str(package_dir),
            "tenant_env": str(package_env),
            "package_manifest": str(package_manifest),
            "package_dir_exists": package_dir.exists(),
            "tenant_env_exists": package_env.exists(),
            "package_manifest_exists": package_manifest.exists(),
            "package_audit_ok": bool(record and record.get("ok")),
            "package_error": (record or {}).get("error"),
        },
    )


def _dynamic_pilot_guard_step(dynamic_payload: dict[str, Any]) -> ActivationChecklistStep:
    status = str(dynamic_payload.get("status") or "")
    live_binding_allowed = bool(dynamic_payload.get("live_binding_allowed"))
    expected_block = status == "pilot_blocked_adapter_not_wired"
    ready = status == "ready_for_dynamic_pilot" and live_binding_allowed
    ok = expected_block or ready
    return ActivationChecklistStep(
        step_id="dynamic_pilot_guard",
        ok=ok,
        severity="error",
        status=status or "unknown",
        message="Dynamic pilot is still blocked by the live adapter guard, as expected."
        if expected_block
        else "Dynamic pilot readiness is fully ready."
        if ready
        else "Dynamic pilot is blocked for an unexpected reason.",
        detail={
            "live_binding_allowed": live_binding_allowed,
            "blocker_count": len(dynamic_payload.get("blockers") or []),
            "secret_readiness_ok": bool((dynamic_payload.get("secret_readiness") or {}).get("ok")),
            "adapter_live_binding_allowed_now": bool((dynamic_payload.get("adapter_plan") or {}).get("live_binding_allowed_now")),
        },
    )


def _secret_scaffold_ok(*, secret_env: Path, secret_manifest: Path, package_dir: Path) -> bool:
    return (
        secret_env.exists()
        and secret_manifest.exists()
        and _outside_path(secret_env, package_dir)
        and _outside_path(secret_manifest, package_dir)
    )


def _outside_path(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return True
    return False


def _no_runtime_side_effects(payload: dict[str, Any]) -> bool:
    summary = payload.get("summary") or {}
    return not any(
        bool(summary.get(key))
        for key in ("docker_started", "build_or_pull_run", "user_facing_runtime_touched")
    )


def _percent(passed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(100 * passed / total, 1)


def _dynamic_pilot_percent(
    *,
    package_ok: bool,
    isolation_ok: bool,
    secret_scaffold_ok: bool,
    secret_readiness_ok: bool,
    adapter_ready: bool,
) -> float:
    checks = [package_ok, isolation_ok, secret_scaffold_ok, secret_readiness_ok, adapter_ready]
    return _percent(sum(1 for item in checks if item), len(checks))


def _remaining_work(dynamic_payload: dict[str, Any], *, secret_scaffold_ok: bool) -> list[str]:
    work = []
    secret_payload = dynamic_payload.get("secret_readiness") or {}
    adapter_payload = dynamic_payload.get("adapter_plan") or {}
    if not secret_scaffold_ok:
        work.append("Create a package-external dynamic pilot secret scaffold.")
    if not secret_payload.get("ok"):
        work.append("Fill real pilot secrets only in the package-external secret env after explicit approval.")
    if not adapter_payload.get("live_binding_allowed_now"):
        work.append("Review, wire, and approve the explicit live dynamic runtime adapter boundary.")
    work.extend(
        [
            "Run golden replay and narrow live Slack replay before any user-facing pilot.",
            "Run manual docker compose config checks and require explicit rollout approval before starting side-by-side services.",
        ]
    )
    return work


def _write_activation_artifacts(report: DynamicActivationChecklistReport, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    (output_dir / "activation_checklist_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    readme = [
        "# Dynamic Platform Activation Checklist",
        "",
        f"Tenant: `{report.tenant_key}`",
        f"Status: `{report.status}`",
        f"OK: `{str(report.ok).lower()}`",
        f"Live runtime authorized: `{str(report.live_runtime_authorized).lower()}`",
        f"Offline preparation: `{report.summary.get('offline_preparation_percent')}%`",
        f"Dynamic pilot prerequisite: `{report.summary.get('dynamic_pilot_prerequisite_percent')}%`",
        "",
        "Steps:",
    ]
    readme.extend(
        f"- `{step.step_id}`: {'OK' if step.ok else 'FAILED'} ({step.status})"
        for step in report.steps
    )
    readme.extend(["", "Remaining work:"])
    readme.extend(f"- {item}" for item in report.remaining_work)
    readme.extend(
        [
            "",
            "Safety:",
            "- Docker containers were not started.",
            "- Docker build or pull was not run.",
            "- Existing classic runtime was not modified.",
            "- This checklist does not authorize live dynamic runtime.",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
