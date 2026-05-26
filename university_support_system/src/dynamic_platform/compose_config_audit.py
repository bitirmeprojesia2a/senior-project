"""Docker compose config audit for dynamic tenant drafts.

This audit is intentionally narrower than a rollout: it only runs
`docker compose config`, never `up`, `build`, or `pull`. It verifies that the
resolved compose model still respects dynamic tenant safety after Docker's
merge semantics are applied.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.compose_template import DRAFT_OVERRIDE_NAME, LAUNCH_MANIFEST_NAME
from src.dynamic_platform.docker_plan import DEFAULT_COMPOSE_FILES
from src.dynamic_platform.loader import DynamicPlatformPaths, load_tenant_bundle


INFRA_SERVICES = {"postgres", "redis", "chromadb"}
CLASSIC_SERVICE_PREFIXES = ("agent-", "slack-bot")
DYNAMIC_AGENT_PROFILE = "tenant-dynamic-agents"
DISABLED_CLASSIC_PROFILE = "disabled-classic-runtime"


@dataclass(frozen=True)
class ComposeConfigIssue:
    severity: str
    code: str
    message: str
    service: str | None = None
    value: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "service": self.service,
            "value": self.value,
        }


@dataclass
class ComposeConfigAuditReport:
    tenant_key: str
    package_dir: str
    runtime_strategy: str
    ok: bool = True
    default_services: list[str] = field(default_factory=list)
    dynamic_agent_services: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)
    errors: list[ComposeConfigIssue] = field(default_factory=list)
    warnings: list[ComposeConfigIssue] = field(default_factory=list)
    commands: dict[str, list[str]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def add_error(
        self,
        code: str,
        message: str,
        *,
        service: str | None = None,
        value: str | None = None,
    ) -> None:
        self.ok = False
        self.errors.append(ComposeConfigIssue("error", code, message, service, value))

    def add_warning(
        self,
        code: str,
        message: str,
        *,
        service: str | None = None,
        value: str | None = None,
    ) -> None:
        self.warnings.append(ComposeConfigIssue("warning", code, message, service, value))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "package_dir": self.package_dir,
            "runtime_strategy": self.runtime_strategy,
            "ok": self.ok,
            "default_services": self.default_services,
            "dynamic_agent_services": self.dynamic_agent_services,
            "checks": self.checks,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "commands": self.commands,
            "notes": self.notes,
        }


def run_compose_config_audit(
    *,
    tenant_key: str,
    config_root: str | Path = "configs/dynamic_platform",
    package_dir: str | Path | None = None,
    compose_files: list[str | Path] | None = None,
) -> ComposeConfigAuditReport:
    """Run Docker compose config validation without starting services."""

    bundle = load_tenant_bundle(tenant_key, config_root=config_root)
    package_path = Path(package_dir or Path("tmp/tenant_packages") / tenant_key)
    compose_paths = [Path(path) for path in (compose_files or DEFAULT_COMPOSE_FILES)]
    override_path = package_path / DRAFT_OVERRIDE_NAME
    env_file = package_path / "tenant.env"
    manifest_path = package_path / LAUNCH_MANIFEST_NAME
    report = ComposeConfigAuditReport(
        tenant_key=tenant_key,
        package_dir=str(package_path),
        runtime_strategy=bundle.tenant.runtime_strategy,
        notes=[
            "This audit runs docker compose config only; it does not start, build, pull, or recreate services.",
            "Resolved compose output can contain secrets, so this report stores only summarized service and safety fields.",
        ],
    )

    missing = [path for path in [env_file, override_path, manifest_path, *compose_paths] if not path.exists()]
    report.checks["required_files_exist"] = not missing
    if missing:
        report.add_error(
            "compose_config_required_file_missing",
            "Required compose/package file is missing.",
            value=", ".join(str(path) for path in missing),
        )
        return report

    default_json_cmd = _compose_cmd(env_file=env_file, compose_paths=compose_paths, override_path=override_path, fmt="json")
    default_services_cmd = _compose_cmd(env_file=env_file, compose_paths=compose_paths, override_path=override_path, services=True)
    dynamic_services_cmd = _compose_cmd(
        env_file=env_file,
        compose_paths=compose_paths,
        override_path=override_path,
        services=True,
        profile=DYNAMIC_AGENT_PROFILE,
    )
    report.commands = {
        "default_config_json": default_json_cmd,
        "default_services": default_services_cmd,
        "dynamic_agent_services": dynamic_services_cmd,
    }

    default_config = _run_json(default_json_cmd, report)
    default_services = _run_lines(default_services_cmd, report, command_name="default_services")
    dynamic_services = _run_lines(dynamic_services_cmd, report, command_name="dynamic_agent_services")
    if default_config is None or default_services is None or dynamic_services is None:
        return report

    report.default_services = default_services
    report.dynamic_agent_services = dynamic_services
    if bundle.tenant.runtime_strategy == "classic_protected":
        _audit_classic_config(report, default_config, default_services)
    else:
        _audit_dynamic_config(report, default_config, default_services, dynamic_services)
    return report


def _audit_classic_config(
    report: ComposeConfigAuditReport,
    config: dict[str, Any],
    default_services: list[str],
) -> None:
    services = _services(config)
    report.checks["classic_api_present"] = "api" in services and "api" in default_services
    if not report.checks["classic_api_present"]:
        report.add_error("compose_config_classic_api_missing", "Classic protected tenant config must include api service.")
    report.checks["classic_dynamic_command_absent"] = "scripts.run_dynamic_runtime" not in _command_text(services.get("api"))
    if not report.checks["classic_dynamic_command_absent"]:
        report.add_error("compose_config_classic_api_uses_dynamic_command", "Classic tenant api must not use dynamic runtime command.")


def _audit_dynamic_config(
    report: ComposeConfigAuditReport,
    config: dict[str, Any],
    default_services: list[str],
    dynamic_services: list[str],
) -> None:
    services = _services(config)
    default_set = set(default_services)
    dynamic_set = set(dynamic_services)
    classic_default = sorted(service for service in default_set if _is_classic_service(service))
    report.checks["dynamic_default_has_no_classic_services"] = not classic_default
    if classic_default:
        report.add_error(
            "compose_config_dynamic_default_includes_classic_services",
            "Dynamic tenant default service set must not include classic agent or Slack services.",
            value=", ".join(classic_default),
        )

    expected_default = INFRA_SERVICES | {"api"}
    report.checks["dynamic_default_core_services_present"] = expected_default.issubset(default_set)
    if not report.checks["dynamic_default_core_services_present"]:
        missing = sorted(expected_default - default_set)
        report.add_error(
            "compose_config_dynamic_default_core_missing",
            "Dynamic tenant default service set is missing required infra/api services.",
            value=", ".join(missing),
        )

    api_service = services.get("api")
    report.checks["dynamic_api_uses_dynamic_runtime"] = "scripts.run_dynamic_runtime" in _command_text(api_service)
    if not report.checks["dynamic_api_uses_dynamic_runtime"]:
        report.add_error("compose_config_dynamic_api_command_missing", "Dynamic tenant api must run scripts.run_dynamic_runtime.")

    api_depends = set(_depends_on_names(api_service))
    report.checks["dynamic_api_depends_only_on_infra"] = api_depends.issubset(INFRA_SERVICES)
    if not report.checks["dynamic_api_depends_only_on_infra"]:
        report.add_error(
            "compose_config_dynamic_api_depends_on_classic_service",
            "Dynamic tenant api must not depend on classic agent services.",
            service="api",
            value=", ".join(sorted(api_depends - INFRA_SERVICES)),
        )

    dynamic_agents = sorted(service for service in dynamic_set if service.startswith("dynamic-agent-"))
    report.checks["dynamic_agent_profile_services_present"] = bool(dynamic_agents)
    if not dynamic_agents:
        report.add_error("compose_config_dynamic_agents_missing", "Dynamic agent profile must expose generic dynamic-agent-* services.")

    for name, service in services.items():
        if not _is_classic_service(name):
            continue
        profiles = set(str(item) for item in _as_list(service.get("profiles")))
        ports = _as_list(service.get("ports"))
        disabled_ok = DISABLED_CLASSIC_PROFILE in profiles and not ports
        if not disabled_ok:
            report.add_error(
                "compose_config_classic_service_not_disabled",
                "Classic service in dynamic tenant must be behind disabled-classic-runtime profile with no host ports.",
                service=name,
                value=f"profiles={sorted(profiles)} ports={len(ports)}",
            )
    report.checks["dynamic_classic_services_disabled"] = not any(
        issue.code == "compose_config_classic_service_not_disabled" for issue in report.errors
    )


def _compose_cmd(
    *,
    env_file: Path,
    compose_paths: list[Path],
    override_path: Path,
    services: bool = False,
    fmt: str | None = None,
    profile: str | None = None,
) -> list[str]:
    cmd = ["docker", "compose"]
    if profile:
        cmd.extend(["--profile", profile])
    cmd.extend(["--env-file", str(env_file)])
    for path in compose_paths:
        cmd.extend(["-f", str(path)])
    cmd.extend(["-f", str(override_path), "config"])
    if services:
        cmd.append("--services")
    if fmt:
        cmd.extend(["--format", fmt])
    return cmd


def _run_json(cmd: list[str], report: ComposeConfigAuditReport) -> dict[str, Any] | None:
    completed = _run(cmd, report, command_name="default_config_json")
    if completed is None:
        return None
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        report.add_error("compose_config_json_invalid", f"Docker compose config JSON could not be parsed: {exc}")
        return None
    if not isinstance(payload, dict):
        report.add_error("compose_config_json_not_object", "Docker compose config JSON must be an object.")
        return None
    return payload


def _run_lines(cmd: list[str], report: ComposeConfigAuditReport, *, command_name: str) -> list[str] | None:
    completed = _run(cmd, report, command_name=command_name)
    if completed is None:
        return None
    return [line.strip() for line in (completed.stdout or "").splitlines() if line.strip()]


def _run(
    cmd: list[str],
    report: ComposeConfigAuditReport,
    *,
    command_name: str,
) -> subprocess.CompletedProcess[str] | None:
    env = os.environ.copy()
    env["COMPOSE_DISABLE_ENV_FILE"] = "1"
    try:
        completed = subprocess.run(
            cmd,
            cwd=Path.cwd(),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        report.add_error("compose_config_command_unavailable", f"Could not run docker compose config: {exc}")
        return None
    if completed.returncode != 0:
        report.add_error(
            "compose_config_command_failed",
            f"Docker compose config command failed for {command_name}.",
            value=(completed.stderr or completed.stdout or "").strip()[:500],
        )
        return None
    return completed


def _services(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    services = config.get("services") or {}
    if not isinstance(services, dict):
        return {}
    return {str(key): value for key, value in services.items() if isinstance(value, dict)}


def _is_classic_service(service_name: str) -> bool:
    return service_name.startswith(CLASSIC_SERVICE_PREFIXES)


def _command_text(service: dict[str, Any] | None) -> str:
    if not isinstance(service, dict):
        return ""
    command = service.get("command")
    if isinstance(command, list):
        return " ".join(str(item) for item in command)
    return str(command or "")


def _depends_on_names(service: dict[str, Any] | None) -> list[str]:
    if not isinstance(service, dict):
        return []
    depends = service.get("depends_on") or {}
    if isinstance(depends, dict):
        return [str(key) for key in depends]
    return [str(item) for item in _as_list(depends)]


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
