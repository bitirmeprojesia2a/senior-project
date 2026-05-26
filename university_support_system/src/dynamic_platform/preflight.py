"""Offline preflight gate before any dynamic tenant runtime experiment.

The preflight report intentionally does not call Docker. It combines the
existing completion gate with package-level compose draft checks and returns
manual validation commands for a future approved `docker compose config` step.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.completion_report import run_dynamic_platform_completion_report
from src.dynamic_platform.compose_template import COMPOSE_NOTES_NAME, DRAFT_OVERRIDE_NAME, LAUNCH_MANIFEST_NAME
from src.dynamic_platform.loader import DynamicPlatformPaths


@dataclass(frozen=True)
class PreflightGate:
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
class TenantComposeDraftPreflight:
    tenant_key: str
    ok: bool
    package_dir: str
    override_path: str
    manifest_path: str
    notes_path: str
    checks: dict[str, bool]
    validation_command: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "package_dir": self.package_dir,
            "override_path": self.override_path,
            "manifest_path": self.manifest_path,
            "notes_path": self.notes_path,
            "checks": self.checks,
            "validation_command": self.validation_command,
            "error": self.error,
        }


@dataclass(frozen=True)
class DynamicPlatformPreflightReport:
    ok: bool
    status: str
    config_root: str
    package_root: str
    output_root: str
    summary: dict[str, Any]
    gates: list[PreflightGate]
    tenant_compose_drafts: list[TenantComposeDraftPreflight] = field(default_factory=list)
    manual_docker_config_checks: list[str] = field(default_factory=list)
    blocked_live_items: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
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
            "tenant_compose_drafts": [record.to_dict() for record in self.tenant_compose_drafts],
            "manual_docker_config_checks": self.manual_docker_config_checks,
            "blocked_live_items": self.blocked_live_items,
            "artifacts": self.artifacts,
            "notes": self.notes,
        }


def run_dynamic_platform_preflight(
    *,
    config_root: str | Path = "configs/dynamic_platform",
    package_root: str | Path = "tmp/tenant_packages",
    output_root: str | Path = "tmp/dynamic_platform_preflight",
    require_quality_gates: bool = True,
) -> DynamicPlatformPreflightReport:
    paths = DynamicPlatformPaths.from_root(config_root)
    package_root_path = Path(package_root)
    output_root_path = Path(output_root)

    completion = run_dynamic_platform_completion_report(
        config_root=config_root,
        package_root=package_root_path,
        output_root=output_root_path / "completion",
        require_quality_gates=require_quality_gates,
    )
    completion_payload = completion.to_dict()
    tenant_keys = _tenant_keys(paths)
    compose_records = [_inspect_compose_draft(tenant_key, package_root=package_root_path) for tenant_key in tenant_keys]

    live_authorized = bool((completion_payload.get("summary") or {}).get("live_runtime_authorized"))
    compose_ok = bool(compose_records) and all(record.ok for record in compose_records)
    manual_commands = _manual_docker_config_commands(compose_records)
    gates = [
        PreflightGate(
            gate_id="completion_report",
            ok=completion.ok and completion.status == "offline_handoff_ready",
            message="Offline completion report is ready."
            if completion.ok and completion.status == "offline_handoff_ready"
            else "Offline completion report is not ready.",
            detail={
                "status": completion.status,
                "passed": (completion_payload.get("summary") or {}).get("passed"),
                "gate_count": (completion_payload.get("summary") or {}).get("gate_count"),
                "live_runtime_authorized": live_authorized,
            },
        ),
        PreflightGate(
            gate_id="compose_draft_safety",
            ok=compose_ok,
            message="Tenant compose drafts include offline safety markers and validation commands."
            if compose_ok
            else "One or more tenant compose drafts are missing safety markers.",
            detail={
                "tenant_count": len(compose_records),
                "passed": sum(1 for record in compose_records if record.ok),
                "failed": sum(1 for record in compose_records if not record.ok),
            },
        ),
        PreflightGate(
            gate_id="live_runtime_blocked",
            ok=not live_authorized,
            message="Live dynamic runtime is still blocked, as expected."
            if not live_authorized
            else "Live dynamic runtime appears authorized unexpectedly.",
            detail={"live_runtime_authorized": live_authorized},
        ),
        PreflightGate(
            gate_id="manual_docker_config_required",
            ok=bool(manual_commands),
            message="Manual docker compose config validation commands are prepared but not executed.",
            detail={
                "command_count": len(manual_commands),
                "docker_started": False,
                "build_or_pull_run": False,
            },
        ),
    ]
    ok = all(gate.ok for gate in gates)
    summary = {
        "tenant_count": len(tenant_keys),
        "package_root_exists": package_root_path.exists(),
        "completion_status": completion.status,
        "live_runtime_authorized": live_authorized,
        "compose_draft_count": len(compose_records),
        "compose_draft_passed": sum(1 for record in compose_records if record.ok),
        "manual_docker_config_required": True,
        "docker_started": False,
        "build_or_pull_run": False,
    }
    artifacts = [
        str(output_root_path / "preflight_report.json"),
        str(output_root_path / "manual_docker_config_checks.ps1"),
        str(output_root_path / "README.md"),
    ]
    report = DynamicPlatformPreflightReport(
        ok=ok,
        status="ready_for_manual_compose_config" if ok else "preflight_blocked",
        config_root=str(paths.root),
        package_root=str(package_root_path),
        output_root=str(output_root_path),
        summary=summary,
        gates=gates,
        tenant_compose_drafts=compose_records,
        manual_docker_config_checks=manual_commands,
        blocked_live_items=completion.blocked_live_items,
        artifacts=artifacts,
        notes=[
            "Preflight is offline and does not start Docker, Slack, API, router, agents, RAG, DB, LLM, or model downloads.",
            "A passing preflight means the package set is ready for a separate approved docker compose config check.",
            "Do not print full docker compose config output; use summarized secret/port checks from the runbook.",
        ],
    )
    _write_preflight_artifacts(report, output_root_path)
    return report


def _tenant_keys(paths: DynamicPlatformPaths) -> list[str]:
    if not paths.tenants_dir.exists():
        return []
    return sorted(path.stem for path in paths.tenants_dir.glob("*.yaml"))


def _inspect_compose_draft(tenant_key: str, *, package_root: Path) -> TenantComposeDraftPreflight:
    package_dir = package_root / tenant_key
    override_path = package_dir / DRAFT_OVERRIDE_NAME
    manifest_path = package_dir / LAUNCH_MANIFEST_NAME
    notes_path = package_dir / COMPOSE_NOTES_NAME
    checks = {
        "package_dir_exists": package_dir.exists(),
        "override_exists": override_path.exists(),
        "manifest_exists": manifest_path.exists(),
        "notes_exists": notes_path.exists(),
        "override_has_draft_marker": False,
        "override_uses_env_file_override": False,
        "override_uses_ports_override": False,
        "override_slack_services_profile_scoped": False,
        "manifest_disables_root_env_file": False,
        "manifest_validate_only_services_command": False,
        "tenant_env_contains_suggested_overrides": False,
        "notes_warns_no_full_config_output": False,
    }
    if not package_dir.exists():
        return TenantComposeDraftPreflight(
            tenant_key=tenant_key,
            ok=False,
            package_dir=str(package_dir),
            override_path=str(override_path),
            manifest_path=str(manifest_path),
            notes_path=str(notes_path),
            checks=checks,
            error="tenant_package_directory_missing",
        )

    try:
        override_text = override_path.read_text(encoding="utf-8") if override_path.exists() else ""
        manifest_text = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else ""
        notes_text = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""
        tenant_env_text = (package_dir / "tenant.env").read_text(encoding="utf-8") if (package_dir / "tenant.env").exists() else ""
        manifest = json.loads(manifest_text) if manifest_text else {}
    except (OSError, json.JSONDecodeError) as exc:
        return TenantComposeDraftPreflight(
            tenant_key=tenant_key,
            ok=False,
            package_dir=str(package_dir),
            override_path=str(override_path),
            manifest_path=str(manifest_path),
            notes_path=str(notes_path),
            checks=checks,
            error=str(exc),
        )

    validation_command = _validation_command(manifest)
    checks.update(
        {
            "override_has_draft_marker": "DRAFT ONLY" in override_text,
            "override_uses_env_file_override": "env_file: !override" in override_text,
            "override_uses_ports_override": "ports: !override" in override_text,
            "override_slack_services_profile_scoped": _slack_service_safety_ok(override_text, notes_text),
            "manifest_disables_root_env_file": "COMPOSE_DISABLE_ENV_FILE" in manifest_text,
            "manifest_validate_only_services_command": bool(validation_command)
            and "docker compose" in validation_command
            and " config --services" in validation_command
            and not _contains_run_command(validation_command),
            "tenant_env_contains_suggested_overrides": _tenant_env_contains_suggested_overrides(
                tenant_env_text,
                manifest,
            ),
            "notes_warns_no_full_config_output": _notes_warn_no_full_config_output(notes_text),
        }
    )
    required = [
        "package_dir_exists",
        "override_exists",
        "manifest_exists",
        "notes_exists",
        "override_has_draft_marker",
        "override_uses_env_file_override",
        "override_uses_ports_override",
        "override_slack_services_profile_scoped",
        "manifest_disables_root_env_file",
        "manifest_validate_only_services_command",
        "tenant_env_contains_suggested_overrides",
    ]
    ok = all(checks[key] for key in required)
    return TenantComposeDraftPreflight(
        tenant_key=tenant_key,
        ok=ok,
        package_dir=str(package_dir),
        override_path=str(override_path),
        manifest_path=str(manifest_path),
        notes_path=str(notes_path),
        checks=checks,
        validation_command=validation_command,
        error=None if ok else "compose_draft_preflight_failed",
    )


def _slack_service_safety_ok(override_text: str, notes_text: str) -> bool:
    classic_slack_present = "slack-bot-a2a:" in override_text or "slack-bot-inprocess:" in override_text
    if classic_slack_present:
        if "disabled-classic-runtime" in override_text and "classic-service-disabled" in override_text:
            return "Dynamic Slack adapter" in notes_text
        return "tenant-slack-a2a" in override_text and "manual-inprocess-slack" in override_text
    return "Dynamic Slack adapter" in notes_text and "classic Slack servislerini icermez" in notes_text


def _validation_command(manifest: dict[str, Any]) -> str | None:
    for command in manifest.get("validation_commands") or []:
        text = str(command)
        if "docker compose" in text:
            return text
    return None


def _contains_run_command(command: str) -> bool:
    words = {part.strip().lower() for part in command.replace(";", " ").split()}
    return bool({"up", "run", "start", "--build", "pull"} & words)


def _manual_docker_config_commands(records: list[TenantComposeDraftPreflight]) -> list[str]:
    return [
        record.validation_command
        for record in records
        if record.validation_command and record.ok
    ]


def _notes_warn_no_full_config_output(notes_text: str) -> bool:
    lowered = notes_text.lower()
    return (
        "tam `docker compose config` ciktisini kullanmayin" in lowered
        or "tam `docker compose config` ciktisi" in lowered
        or "full docker compose config" in lowered
    )


def _tenant_env_contains_suggested_overrides(tenant_env_text: str, manifest: dict[str, Any]) -> bool:
    suggested = manifest.get("suggested_env_overrides")
    if not isinstance(suggested, dict) or not suggested:
        return True
    keys = _env_keys(tenant_env_text)
    return all(str(key) in keys for key in suggested)


def _env_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        keys.add(stripped.split("=", 1)[0])
    return keys


def _write_preflight_artifacts(report: DynamicPlatformPreflightReport, output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    (output_root / "preflight_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    commands = [
        "# Dynamic platform manual docker compose config checks",
        "# Generated by scripts.tenant preflight.",
        "# These commands only run `docker compose config --services`; they do not start containers.",
        "# Do not print full `docker compose config` output because resolved config can include secrets.",
        "",
    ]
    commands.extend(report.manual_docker_config_checks)
    commands.append("")
    (output_root / "manual_docker_config_checks.ps1").write_text("\n".join(commands), encoding="utf-8")
    readme = [
        "# Dynamic Platform Preflight",
        "",
        f"Status: `{report.status}`",
        f"OK: `{str(report.ok).lower()}`",
        "",
        "This directory is an offline handoff artifact. It does not authorize a live dynamic runtime.",
        "",
        "Files:",
        "- `preflight_report.json`: machine-readable preflight result.",
        "- `manual_docker_config_checks.ps1`: manual config-only commands for a future approved step.",
        "",
        "Safety:",
        "- Docker containers were not started.",
        "- Docker build or pull was not run.",
        "- Live dynamic Slack/API/router adapter is still blocked.",
    ]
    (output_root / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
