"""Pilot readiness gate for dynamic tenant experiments.

This module is deliberately offline. It combines the package/preflight,
secret-readiness, and adapter implementation contracts into one report so a
tenant can be prepared for a no-secret smoke test without accidentally
authorizing a user-facing dynamic runtime.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.preflight import run_dynamic_platform_preflight
from src.dynamic_platform.runtime_adapter_implementation_plan import build_runtime_adapter_implementation_plan
from src.dynamic_platform.secret_readiness import check_tenant_secret_readiness
from src.dynamic_platform.tenant_package import PACKAGE_MANIFEST_NAME

PILOT_READINESS_MODES = {"no_secret_smoke", "dynamic_pilot"}


@dataclass(frozen=True)
class PilotReadinessGate:
    gate_id: str
    ok: bool
    severity: str
    message: str
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "ok": self.ok,
            "severity": self.severity,
            "message": self.message,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class TenantPilotReadinessReport:
    tenant_key: str
    mode: str
    ok: bool
    status: str
    live_binding_allowed: bool
    config_root: str
    package_root: str
    package_dir: str
    output_root: str
    secrets_env_source: str
    summary: dict[str, Any]
    gates: list[PilotReadinessGate]
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    preflight: dict[str, Any] = field(default_factory=dict)
    secret_readiness: dict[str, Any] = field(default_factory=dict)
    adapter_plan: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "mode": self.mode,
            "ok": self.ok,
            "status": self.status,
            "live_binding_allowed": self.live_binding_allowed,
            "config_root": self.config_root,
            "package_root": self.package_root,
            "package_dir": self.package_dir,
            "output_root": self.output_root,
            "secrets_env_source": self.secrets_env_source,
            "summary": self.summary,
            "gates": [gate.to_dict() for gate in self.gates],
            "blockers": self.blockers,
            "warnings": self.warnings,
            "notes": self.notes,
            "artifacts": self.artifacts,
            "preflight": self.preflight,
            "secret_readiness": self.secret_readiness,
            "adapter_plan": self.adapter_plan,
        }


def run_tenant_pilot_readiness(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path = "configs/dynamic_platform",
    package_root: str | Path = "tmp/tenant_packages",
    output_root: str | Path = "tmp/dynamic_platform_pilot_readiness",
    secrets_env_file: str | Path | None = None,
    mode: str = "no_secret_smoke",
    include_slack: bool = False,
    require_quality_gates: bool = True,
) -> TenantPilotReadinessReport:
    if mode not in PILOT_READINESS_MODES:
        raise ValueError(f"Unsupported pilot readiness mode: {mode}")

    package_root_path = Path(package_root)
    package_dir = package_root_path / bundle.tenant.tenant_key
    output_root_path = Path(output_root) / bundle.tenant.tenant_key / mode
    env_file = Path(secrets_env_file) if secrets_env_file else package_dir / "tenant.env"

    preflight = run_dynamic_platform_preflight(
        config_root=config_root,
        package_root=package_root_path,
        output_root=output_root_path / "preflight",
        require_quality_gates=require_quality_gates,
    )
    secret_readiness = check_tenant_secret_readiness(
        bundle,
        mode="no_secret_smoke" if mode == "no_secret_smoke" else "dynamic_pilot",
        include_slack=include_slack,
        env_file=env_file,
    )
    adapter_plan = build_runtime_adapter_implementation_plan(bundle)
    adapter_payload = adapter_plan.to_dict()
    package_manifest = package_dir / PACKAGE_MANIFEST_NAME

    gates = [
        PilotReadinessGate(
            gate_id="tenant_package_present",
            ok=package_dir.exists() and package_manifest.exists(),
            severity="error",
            message="Tenant package and package_manifest.json are present."
            if package_dir.exists() and package_manifest.exists()
            else "Tenant package or package_manifest.json is missing.",
            detail={
                "package_dir": str(package_dir),
                "package_manifest": str(package_manifest),
                "package_dir_exists": package_dir.exists(),
                "package_manifest_exists": package_manifest.exists(),
            },
        ),
        PilotReadinessGate(
            gate_id="preflight",
            ok=preflight.ok,
            severity="error",
            message=f"Preflight status is {preflight.status}.",
            detail={
                "status": preflight.status,
                "manual_docker_config_required": preflight.summary.get("manual_docker_config_required"),
                "docker_started": preflight.summary.get("docker_started"),
                "build_or_pull_run": preflight.summary.get("build_or_pull_run"),
            },
        ),
        PilotReadinessGate(
            gate_id="secret_readiness",
            ok=secret_readiness.ok,
            severity="error",
            message=f"Secret readiness mode {secret_readiness.mode} is {'OK' if secret_readiness.ok else 'FAILED'}.",
            detail={
                "mode": secret_readiness.mode,
                "include_slack": secret_readiness.include_slack,
                "env_source": secret_readiness.env_source,
                "error_count": len(secret_readiness.errors),
                "warning_count": len(secret_readiness.warnings),
            },
        ),
        _adapter_gate(mode, adapter_payload),
    ]

    blockers = _blockers(mode, gates, secret_readiness.to_dict(), adapter_payload)
    warnings = _warnings(mode, secret_readiness.to_dict())
    live_binding_allowed = mode == "dynamic_pilot" and bool(adapter_payload.get("live_binding_allowed_now"))
    ok = all(gate.ok for gate in gates) and (mode == "no_secret_smoke" or live_binding_allowed)
    status = _status(mode, ok=ok, blockers=blockers, live_binding_allowed=live_binding_allowed)
    artifacts = [
        str(output_root_path / "pilot_readiness_report.json"),
        str(output_root_path / "README.md"),
    ]

    report = TenantPilotReadinessReport(
        tenant_key=bundle.tenant.tenant_key,
        mode=mode,
        ok=ok,
        status=status,
        live_binding_allowed=live_binding_allowed,
        config_root=str(Path(config_root)),
        package_root=str(package_root_path),
        package_dir=str(package_dir),
        output_root=str(output_root_path),
        secrets_env_source=secret_readiness.env_source,
        summary={
            "runtime_strategy": bundle.tenant.runtime_strategy,
            "preflight_ok": preflight.ok,
            "secret_readiness_ok": secret_readiness.ok,
            "adapter_live_binding_allowed_now": bool(adapter_payload.get("live_binding_allowed_now")),
            "live_binding_allowed": live_binding_allowed,
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "docker_started": False,
            "build_or_pull_run": False,
            "user_facing_runtime_touched": False,
        },
        gates=gates,
        blockers=blockers,
        warnings=warnings,
        notes=[
            "Pilot readiness is offline; it does not start Docker, Slack, API, router, agents, RAG, DB, LLM, or model downloads.",
            "no_secret_smoke can pass without LLM/Slack secrets because it is infrastructure-only.",
            "dynamic_pilot remains blocked until the live adapter is explicitly implemented, tested, and approved.",
            "Existing classic runtime remains the protected production path.",
        ],
        artifacts=artifacts,
        preflight=preflight.to_dict(),
        secret_readiness=secret_readiness.to_dict(),
        adapter_plan=adapter_payload,
    )
    _write_pilot_readiness_artifacts(report, output_root_path)
    return report


def _adapter_gate(mode: str, adapter_payload: dict[str, Any]) -> PilotReadinessGate:
    live_now = bool(adapter_payload.get("live_binding_allowed_now"))
    if mode == "no_secret_smoke":
        return PilotReadinessGate(
            gate_id="adapter_live_binding_blocked",
            ok=not live_now,
            severity="error",
            message="Live adapter binding is blocked, as expected for no-secret smoke.",
            detail={
                "implementation_status": adapter_payload.get("implementation_status"),
                "live_binding_allowed_now": live_now,
            },
        )
    return PilotReadinessGate(
        gate_id="adapter_live_binding_ready",
        ok=live_now,
        severity="error",
        message="Live adapter binding is ready."
        if live_now
        else "Live adapter binding is not wired; dynamic pilot cannot be user-facing yet.",
        detail={
            "implementation_status": adapter_payload.get("implementation_status"),
            "live_binding_allowed_now": live_now,
        },
    )


def _blockers(
    mode: str,
    gates: list[PilotReadinessGate],
    secret_payload: dict[str, Any],
    adapter_payload: dict[str, Any],
) -> list[str]:
    blockers = [
        f"{gate.gate_id}: {gate.message}"
        for gate in gates
        if not gate.ok and gate.severity == "error"
    ]
    for issue in secret_payload.get("errors") or []:
        scope = issue.get("key") or issue.get("group_id") or "-"
        blockers.append(f"secret_readiness/{issue.get('code')} {scope}: {issue.get('message')}")
    if mode == "dynamic_pilot" and not adapter_payload.get("live_binding_allowed_now"):
        blockers.append("dynamic_runtime_adapter_not_wired: live user-facing dynamic adapter is still blocked by design")
    return blockers


def _warnings(mode: str, secret_payload: dict[str, Any]) -> list[str]:
    warnings = [
        f"secret_readiness/{issue.get('code')}: {issue.get('message')}"
        for issue in secret_payload.get("warnings") or []
    ]
    if mode == "no_secret_smoke":
        warnings.append("no_secret_smoke_is_not_user_facing: passing this gate does not authorize Slack/API live answers")
    return warnings


def _status(
    mode: str,
    *,
    ok: bool,
    blockers: list[str],
    live_binding_allowed: bool,
) -> str:
    if mode == "no_secret_smoke":
        return "ready_for_no_secret_smoke" if ok else "no_secret_smoke_blocked"
    if live_binding_allowed and ok:
        return "ready_for_dynamic_pilot"
    if any("dynamic_runtime_adapter_not_wired" in blocker for blocker in blockers):
        return "pilot_blocked_adapter_not_wired"
    return "pilot_blocked"


def _write_pilot_readiness_artifacts(report: TenantPilotReadinessReport, output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    (output_root / "pilot_readiness_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    readme = [
        "# Dynamic Platform Pilot Readiness",
        "",
        f"Tenant: `{report.tenant_key}`",
        f"Mode: `{report.mode}`",
        f"Status: `{report.status}`",
        f"OK: `{str(report.ok).lower()}`",
        f"Live binding allowed: `{str(report.live_binding_allowed).lower()}`",
        "",
        "This artifact is offline. It does not authorize or start a live dynamic runtime.",
        "",
        "Blockers:",
    ]
    if report.blockers:
        readme.extend(f"- {blocker}" for blocker in report.blockers)
    else:
        readme.append("- none")
    readme.extend(
        [
            "",
            "Safety:",
            "- Docker containers were not started.",
            "- Docker build or pull was not run.",
            "- Existing classic runtime was not modified.",
        ]
    )
    (output_root / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
