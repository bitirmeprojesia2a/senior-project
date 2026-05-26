"""Runtime container audit for dynamic tenant smoke runs.

This audit only reads Docker metadata. It does not start, stop, recreate,
build, pull, or remove containers.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.compose_config_audit import (
    CLASSIC_SERVICE_PREFIXES,
    ComposeConfigIssue,
    run_compose_config_audit,
)
from src.dynamic_platform.loader import load_tenant_bundle


DYNAMIC_API_COMMAND = ["python", "-m", "scripts.run_dynamic_runtime"]
DYNAMIC_AGENT_COMMAND = ["python", "-m", "scripts.run_generic_agent_host"]


@dataclass(frozen=True)
class RuntimeContainerRecord:
    name: str
    service: str | None
    image: str | None
    command: list[str]
    status: str | None
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "service": self.service,
            "image": self.image,
            "command": self.command,
            "status": self.status,
            "labels": self.labels,
        }


@dataclass
class RuntimeContainerAuditReport:
    tenant_key: str
    package_dir: str
    runtime_strategy: str
    ok: bool = True
    expected_default_services: list[str] = field(default_factory=list)
    expected_dynamic_agent_services: list[str] = field(default_factory=list)
    containers: list[RuntimeContainerRecord] = field(default_factory=list)
    errors: list[ComposeConfigIssue] = field(default_factory=list)
    warnings: list[ComposeConfigIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_error(self, code: str, message: str, *, service: str | None = None, value: str | None = None) -> None:
        self.ok = False
        self.errors.append(ComposeConfigIssue("error", code, message, service, value))

    def add_warning(self, code: str, message: str, *, service: str | None = None, value: str | None = None) -> None:
        self.warnings.append(ComposeConfigIssue("warning", code, message, service, value))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "package_dir": self.package_dir,
            "runtime_strategy": self.runtime_strategy,
            "ok": self.ok,
            "expected_default_services": self.expected_default_services,
            "expected_dynamic_agent_services": self.expected_dynamic_agent_services,
            "containers": [container.to_dict() for container in self.containers],
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
        }


def run_runtime_container_audit(
    *,
    tenant_key: str,
    config_root: str | Path = "configs/dynamic_platform",
    package_dir: str | Path | None = None,
    expected_image: str | None = None,
    allow_dynamic_agents: bool = False,
) -> RuntimeContainerAuditReport:
    bundle = load_tenant_bundle(tenant_key, config_root=config_root)
    package_path = Path(package_dir or Path("tmp/tenant_packages") / tenant_key)
    compose_report = run_compose_config_audit(
        tenant_key=tenant_key,
        config_root=config_root,
        package_dir=package_path,
    )
    report = RuntimeContainerAuditReport(
        tenant_key=tenant_key,
        package_dir=str(package_path),
        runtime_strategy=bundle.tenant.runtime_strategy,
        expected_default_services=compose_report.default_services,
        expected_dynamic_agent_services=compose_report.dynamic_agent_services,
        notes=[
            "This audit reads docker metadata only; it does not start, stop, build, pull, recreate, or remove containers.",
            "Use it after a dynamic smoke to catch stale classic containers and wrong image/command drift.",
        ],
    )
    if not compose_report.ok:
        report.add_error("compose_config_audit_failed", "Compose config audit failed; runtime containers cannot be trusted.")
        return report

    containers = _list_tenant_containers(tenant_key)
    report.containers = containers
    if not containers:
        report.add_warning("no_tenant_containers_found", "No Docker containers with this tenant label were found.")
        return report

    allowed_services = set(compose_report.default_services)
    if allow_dynamic_agents:
        allowed_services.update(compose_report.dynamic_agent_services)

    for container in containers:
        service = container.service
        if service is None:
            report.add_warning(
                "container_missing_compose_service_label",
                "Container is tenant-labelled but has no compose service label.",
                value=container.name,
            )
            continue
        if any(service.startswith(prefix) for prefix in CLASSIC_SERVICE_PREFIXES):
            report.add_error(
                "classic_container_present_in_dynamic_runtime",
                "Classic agent or Slack container is present in a dynamic tenant runtime.",
                service=service,
                value=container.name,
            )
        if service not in allowed_services:
            report.add_error(
                "unexpected_tenant_container_service",
                "Container service is not part of the expected resolved compose service set.",
                service=service,
                value=container.name,
            )
        if bundle.tenant.runtime_strategy != "classic_protected" and service == "api":
            if container.command != DYNAMIC_API_COMMAND:
                report.add_error(
                    "dynamic_api_container_wrong_command",
                    "Dynamic tenant API container is not running scripts.run_dynamic_runtime.",
                    service=service,
                    value=" ".join(container.command),
                )
            if expected_image and container.image != expected_image:
                report.add_error(
                    "dynamic_api_container_wrong_image",
                    "Dynamic tenant API container image does not match expected image.",
                    service=service,
                    value=f"{container.image} != {expected_image}",
                )
        if bundle.tenant.runtime_strategy != "classic_protected" and service.startswith("dynamic-agent-"):
            if container.command != DYNAMIC_AGENT_COMMAND:
                report.add_error(
                    "dynamic_agent_container_wrong_command",
                    "Dynamic agent container is not running scripts.run_generic_agent_host.",
                    service=service,
                    value=" ".join(container.command),
                )
            if expected_image and container.image != expected_image:
                report.add_error(
                    "dynamic_agent_container_wrong_image",
                    "Dynamic agent container image does not match expected image.",
                    service=service,
                    value=f"{container.image} != {expected_image}",
                )
    return report


def _list_tenant_containers(tenant_key: str) -> list[RuntimeContainerRecord]:
    ps = subprocess.run(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"label=dynamic-platform.tenant={tenant_key}",
            "--format",
            "{{.Names}}",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if ps.returncode != 0:
        raise RuntimeError((ps.stderr or ps.stdout or "docker ps failed").strip())
    names = [line.strip() for line in ps.stdout.splitlines() if line.strip()]
    records: list[RuntimeContainerRecord] = []
    for name in names:
        records.append(_inspect_container(name))
    return records


def _inspect_container(name: str) -> RuntimeContainerRecord:
    completed = subprocess.run(
        ["docker", "inspect", name],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or f"docker inspect failed for {name}").strip())
    payload = json.loads(completed.stdout or "[]")
    first = payload[0] if isinstance(payload, list) and payload else {}
    config = first.get("Config") or {}
    state = first.get("State") or {}
    labels = config.get("Labels") or {}
    if not isinstance(labels, dict):
        labels = {}
    command = config.get("Cmd") or []
    if isinstance(command, str):
        command = [command]
    return RuntimeContainerRecord(
        name=name,
        service=labels.get("com.docker.compose.service"),
        image=config.get("Image"),
        command=list(command),
        status=state.get("Status"),
        labels={str(key): str(value) for key, value in labels.items()},
    )
