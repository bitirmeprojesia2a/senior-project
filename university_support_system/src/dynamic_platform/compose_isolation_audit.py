"""Offline tenant compose isolation audit.

This module inspects generated draft compose artifacts only. It never calls
Docker, never resolves images, and never validates against live infrastructure.
The goal is to catch accidental non-tenant-prefixed compose output before a
future `docker compose config` handoff step.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml

from src.dynamic_platform.compose_template import DRAFT_OVERRIDE_NAME, LAUNCH_MANIFEST_NAME
from src.dynamic_platform.models import DynamicPlatformBundle

REQUIRED_SERVICE_ENV = (
    "TENANT_KEY",
    "TENANT_CONFIG_ROOT",
    "TENANT_RUNTIME_STRATEGY",
    "TENANT_DOMAIN_PACK",
    "TENANT_AGENT_PACK",
    "TENANT_SOURCE_CATALOG",
    "DYNAMIC_PLATFORM_RUNTIME",
)


class _ComposeDraftLoader(yaml.SafeLoader):
    pass


def _construct_compose_override(loader: yaml.SafeLoader, node: yaml.Node) -> Any:
    return loader.construct_sequence(node)


_ComposeDraftLoader.add_constructor("!override", _construct_compose_override)
_ComposeDraftLoader.add_constructor("!reset", _construct_compose_override)


@dataclass(frozen=True)
class ComposeIsolationIssue:
    severity: str
    code: str
    message: str
    path: str | None = None
    service: str | None = None
    value: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "service": self.service,
            "value": self.value,
        }


@dataclass
class ComposeIsolationAuditReport:
    tenant_key: str
    package_dir: str
    manifest_path: str
    override_path: str
    ok: bool = True
    checks: dict[str, bool] = field(default_factory=dict)
    services_checked: list[str] = field(default_factory=list)
    volumes_checked: list[str] = field(default_factory=list)
    networks_checked: list[str] = field(default_factory=list)
    errors: list[ComposeIsolationIssue] = field(default_factory=list)
    warnings: list[ComposeIsolationIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_error(
        self,
        code: str,
        message: str,
        *,
        path: str | None = None,
        service: str | None = None,
        value: str | None = None,
    ) -> None:
        self.errors.append(ComposeIsolationIssue("error", code, message, path, service, value))
        self.ok = False

    def add_warning(
        self,
        code: str,
        message: str,
        *,
        path: str | None = None,
        service: str | None = None,
        value: str | None = None,
    ) -> None:
        self.warnings.append(ComposeIsolationIssue("warning", code, message, path, service, value))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "package_dir": self.package_dir,
            "manifest_path": self.manifest_path,
            "override_path": self.override_path,
            "ok": self.ok,
            "checks": self.checks,
            "summary": {
                "service_count": len(self.services_checked),
                "volume_count": len(self.volumes_checked),
                "network_count": len(self.networks_checked),
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
            },
            "services_checked": self.services_checked,
            "volumes_checked": self.volumes_checked,
            "networks_checked": self.networks_checked,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
        }


def run_compose_isolation_audit(
    bundle: DynamicPlatformBundle,
    *,
    package_dir: str | Path,
    draft_files: Mapping[str, str] | None = None,
) -> ComposeIsolationAuditReport:
    """Audit generated draft compose files without executing Docker."""

    package_path = Path(package_dir)
    manifest_path = package_path / LAUNCH_MANIFEST_NAME
    override_path = package_path / DRAFT_OVERRIDE_NAME
    report = ComposeIsolationAuditReport(
        tenant_key=bundle.tenant.tenant_key,
        package_dir=str(package_path),
        manifest_path=str(manifest_path),
        override_path=str(override_path),
        notes=[
            "Compose isolation audit is offline; it does not run docker compose, build images, or start services.",
            "A passing audit only means the draft artifacts follow tenant-prefix and safety-marker contracts.",
            "A future rollout still requires docker compose config, replay, and a separate live adapter approval.",
        ],
    )

    manifest = _load_manifest(report, manifest_path, draft_files)
    override = _load_override(report, override_path, draft_files)
    if not isinstance(manifest, dict) or not isinstance(override, dict):
        return report

    tenant_key = bundle.tenant.tenant_key
    env_prefix = tenant_key.upper()
    expected_container_prefix = str(manifest.get("container_prefix") or tenant_key)
    expected_volume_prefix = str(manifest.get("volume_prefix") or f"{tenant_key}_")
    expected_project_name = str(manifest.get("compose_project_name") or f"{tenant_key}_support")
    expected_network_name = str(manifest.get("network_name") or f"{tenant_key}_a2a_infra")
    expected_env_file = _normalize_path(str(manifest.get("env_file") or package_path / "tenant.env"))

    _check_manifest(report, manifest)
    _check_draft_marker(report, override)
    _check_project_name(report, override, expected_project_name)
    _check_services(report, override, tenant_key, env_prefix, expected_container_prefix, expected_env_file)
    _check_volumes(report, override, expected_volume_prefix)
    _check_networks(report, override, env_prefix, expected_network_name)
    _check_validation_commands(report, manifest)
    return report


def _load_manifest(
    report: ComposeIsolationAuditReport,
    path: Path,
    draft_files: Mapping[str, str] | None,
) -> dict[str, Any] | None:
    text = _read_artifact(report, path, LAUNCH_MANIFEST_NAME, draft_files)
    if text is None:
        report.checks["manifest_readable"] = False
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        report.checks["manifest_readable"] = False
        report.add_error("compose_manifest_invalid_json", f"Could not parse compose launch manifest: {exc}", path=str(path))
        return None
    if not isinstance(payload, dict):
        report.checks["manifest_readable"] = False
        report.add_error("compose_manifest_not_object", "Compose launch manifest must be a JSON object.", path=str(path))
        return None
    report.checks["manifest_readable"] = True
    return payload


def _load_override(
    report: ComposeIsolationAuditReport,
    path: Path,
    draft_files: Mapping[str, str] | None,
) -> dict[str, Any] | None:
    text = _read_artifact(report, path, DRAFT_OVERRIDE_NAME, draft_files)
    if text is None:
        report.checks["override_readable"] = False
        return None
    try:
        payload = yaml.load(text, Loader=_ComposeDraftLoader) or {}
    except yaml.YAMLError as exc:
        report.checks["override_readable"] = False
        report.add_error("compose_override_invalid_yaml", f"Could not parse draft compose override: {exc}", path=str(path))
        return None
    if not isinstance(payload, dict):
        report.checks["override_readable"] = False
        report.add_error("compose_override_not_object", "Draft compose override must be a YAML object.", path=str(path))
        return None
    report.checks["override_readable"] = True
    return payload


def _read_artifact(
    report: ComposeIsolationAuditReport,
    path: Path,
    name: str,
    draft_files: Mapping[str, str] | None,
) -> str | None:
    if draft_files is not None:
        text = draft_files.get(name)
        if text is None:
            report.add_error("compose_artifact_missing", f"Draft compose artifact is missing from payload: {name}", path=str(path))
        return text
    if not path.exists():
        report.add_error("compose_artifact_missing", f"Draft compose artifact is missing: {name}", path=str(path))
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        report.add_error("compose_artifact_unreadable", f"Could not read draft compose artifact: {exc}", path=str(path))
        return None


def _check_manifest(report: ComposeIsolationAuditReport, manifest: dict[str, Any]) -> None:
    is_draft = manifest.get("safety_status") == "draft_do_not_run"
    report.checks["manifest_safety_status_draft"] = is_draft
    if not is_draft:
        report.add_error(
            "compose_manifest_not_draft",
            "compose_launch_manifest.json must declare safety_status=draft_do_not_run.",
            path=report.manifest_path,
            value=str(manifest.get("safety_status")),
        )


def _check_draft_marker(report: ComposeIsolationAuditReport, override: dict[str, Any]) -> None:
    warning = override.get("x-draft-warning")
    warning_text = " ".join(str(item) for item in _as_list(warning))
    has_marker = "DRAFT ONLY" in warning_text
    report.checks["override_has_draft_marker"] = has_marker
    if not has_marker:
        report.add_error(
            "compose_override_missing_draft_marker",
            "Draft compose override must include a DRAFT ONLY marker.",
            path=report.override_path,
        )


def _check_project_name(
    report: ComposeIsolationAuditReport,
    override: dict[str, Any],
    expected_project_name: str,
) -> None:
    name = str(override.get("name") or "")
    ok = "COMPOSE_PROJECT_NAME" in name and expected_project_name in name
    report.checks["project_name_tenant_default"] = ok
    if not ok:
        report.add_error(
            "compose_project_name_not_tenant_scoped",
            "Draft compose project name must be tenant-scoped and configurable via COMPOSE_PROJECT_NAME.",
            path=report.override_path,
            value=name,
        )


def _check_services(
    report: ComposeIsolationAuditReport,
    override: dict[str, Any],
    tenant_key: str,
    env_prefix: str,
    expected_container_prefix: str,
    expected_env_file: str,
) -> None:
    services = override.get("services") or {}
    if not isinstance(services, dict) or not services:
        report.checks["services_present"] = False
        report.add_error("compose_services_missing", "Draft compose override must contain service overrides.", path=report.override_path)
        return
    report.checks["services_present"] = True

    container_ok = True
    labels_ok = True
    env_ok = True
    env_file_ok = True
    ports_ok = True
    slack_profiles_ok = True
    for service_name, service in services.items():
        service_key = str(service_name)
        report.services_checked.append(service_key)
        if not isinstance(service, dict):
            report.add_error(
                "compose_service_override_invalid",
                "Service override must be a YAML object.",
                path=report.override_path,
                service=service_key,
            )
            container_ok = labels_ok = env_ok = False
            continue

        container_name = str(service.get("container_name") or "")
        if not container_name.startswith(f"{expected_container_prefix}_"):
            container_ok = False
            report.add_error(
                "compose_container_name_not_tenant_prefixed",
                "Service container_name must start with the tenant container prefix.",
                path=report.override_path,
                service=service_key,
                value=container_name,
            )

        labels = service.get("labels") or {}
        if not isinstance(labels, dict):
            labels = {}
        if labels.get("dynamic-platform.tenant") != tenant_key or labels.get("dynamic-platform.compose-template") != "draft":
            labels_ok = False
            report.add_error(
                "compose_service_labels_missing",
                "Service labels must include tenant key and draft compose-template marker.",
                path=report.override_path,
                service=service_key,
            )

        env = service.get("environment") or {}
        if not isinstance(env, dict):
            env = {}
        missing_env = [key for key in REQUIRED_SERVICE_ENV if key not in env]
        if missing_env:
            env_ok = False
            report.add_error(
                "compose_service_tenant_env_missing",
                "Service environment is missing required tenant runtime fields.",
                path=report.override_path,
                service=service_key,
                value=", ".join(missing_env),
            )

        env_file = service.get("env_file")
        if env_file is not None and expected_env_file not in {_normalize_path(str(item)) for item in _as_list(env_file)}:
            env_file_ok = False
            report.add_error(
                "compose_service_env_file_not_tenant_package",
                "Service env_file overrides must point at the tenant.env in the handoff package.",
                path=report.override_path,
                service=service_key,
                value=str(env_file),
            )

        for port in _as_list(service.get("ports")):
            port_text = str(port)
            match = re.match(r"^\$\{(?P<name>[A-Z0-9_]+):-", port_text)
            if match and not match.group("name").startswith(f"{env_prefix}_"):
                ports_ok = False
                report.add_error(
                    "compose_port_env_not_tenant_prefixed",
                    "Port environment variable must be tenant-prefixed.",
                    path=report.override_path,
                    service=service_key,
                    value=port_text,
                )

        if service_key.startswith("slack-bot"):
            profiles = [str(item) for item in _as_list(service.get("profiles"))]
            if not profiles:
                slack_profiles_ok = False
                report.add_error(
                    "compose_slack_service_not_profile_scoped",
                    "Slack services must be profile-scoped in tenant drafts to avoid accidentally starting multiple bots.",
                    path=report.override_path,
                    service=service_key,
                )

    report.checks["container_names_tenant_prefixed"] = container_ok
    report.checks["service_labels_tenant_scoped"] = labels_ok
    report.checks["service_tenant_environment_present"] = env_ok
    report.checks["service_env_files_package_scoped"] = env_file_ok
    report.checks["port_env_vars_tenant_prefixed"] = ports_ok
    report.checks["slack_services_profile_scoped"] = slack_profiles_ok
    report.services_checked.sort()


def _check_volumes(
    report: ComposeIsolationAuditReport,
    override: dict[str, Any],
    expected_volume_prefix: str,
) -> None:
    volumes = override.get("volumes") or {}
    if not isinstance(volumes, dict):
        report.checks["volumes_tenant_prefixed"] = False
        report.add_error("compose_volumes_invalid", "Draft compose volumes must be a YAML object.", path=report.override_path)
        return
    volumes_ok = True
    for volume_key, volume in volumes.items():
        report.volumes_checked.append(str(volume_key))
        if not isinstance(volume, dict):
            volumes_ok = False
            report.add_error(
                "compose_volume_override_invalid",
                "Volume override must be a YAML object.",
                path=report.override_path,
                value=str(volume_key),
            )
            continue
        name = str(volume.get("name") or "")
        if not name.startswith(expected_volume_prefix):
            volumes_ok = False
            report.add_error(
                "compose_volume_name_not_tenant_prefixed",
                "Volume name must start with the tenant volume prefix.",
                path=report.override_path,
                value=name,
            )
    report.checks["volumes_tenant_prefixed"] = volumes_ok
    report.volumes_checked.sort()


def _check_networks(
    report: ComposeIsolationAuditReport,
    override: dict[str, Any],
    env_prefix: str,
    expected_network_name: str,
) -> None:
    networks = override.get("networks") or {}
    if not isinstance(networks, dict):
        report.checks["external_networks_tenant_prefixed"] = False
        report.add_error("compose_networks_invalid", "Draft compose networks must be a YAML object.", path=report.override_path)
        return
    networks_ok = True
    for network_key, network in networks.items():
        report.networks_checked.append(str(network_key))
        if not isinstance(network, dict):
            networks_ok = False
            report.add_error(
                "compose_network_override_invalid",
                "Network override must be a YAML object.",
                path=report.override_path,
                value=str(network_key),
            )
            continue
        if network.get("external"):
            name = str(network.get("name") or "")
            if f"${{{env_prefix}_" not in name or expected_network_name not in name:
                networks_ok = False
                report.add_error(
                    "compose_external_network_not_tenant_prefixed",
                    "External network name must use a tenant-prefixed environment variable and default.",
                    path=report.override_path,
                    value=name,
                )
    report.checks["external_networks_tenant_prefixed"] = networks_ok
    report.networks_checked.sort()


def _check_validation_commands(report: ComposeIsolationAuditReport, manifest: dict[str, Any]) -> None:
    commands = [str(item) for item in _as_list(manifest.get("validation_commands"))]
    executable_commands = [command for command in commands if command.strip() and not command.strip().startswith("#")]
    has_config = any("docker compose" in command and " config" in command for command in commands)
    disables_root_env = any("COMPOSE_DISABLE_ENV_FILE" in command for command in commands)
    has_run_like = any(re.search(r"\b(up|run|start)\b", command) for command in executable_commands)
    report.checks["manifest_has_validate_only_command"] = has_config
    report.checks["manifest_disables_root_env_file"] = disables_root_env
    report.checks["manifest_has_no_run_command"] = not has_run_like
    if not has_config:
        report.add_warning(
            "compose_manifest_missing_config_command",
            "Manifest should include a validate-only docker compose config command for later human review.",
            path=report.manifest_path,
        )
    if not disables_root_env:
        report.add_warning(
            "compose_manifest_root_env_not_disabled",
            "Manifest validation command should set COMPOSE_DISABLE_ENV_FILE=1 to avoid loading the project .env automatically.",
            path=report.manifest_path,
        )
    if has_run_like:
        report.add_error(
            "compose_manifest_contains_run_command",
            "Manifest validation commands must not include up/run/start commands.",
            path=report.manifest_path,
            value=" | ".join(commands),
        )


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")
