"""Offline Docker deployment readiness for tenant profiles.

This module does not modify compose files or start services. It explains
whether a tenant profile can be carried by the current Docker layout and which
parts still block a separate side-by-side institution deployment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.runtime_plan import build_runtime_launch_plan


DEFAULT_COMPOSE_FILES = (
    Path("docker-compose.yml"),
    Path("docker-compose.a2a.yml"),
    Path("docker-compose.slack.yml"),
)


@dataclass(frozen=True)
class DockerPlanIssue:
    severity: str
    code: str
    message: str
    file: str | None = None
    service: str | None = None
    value: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "service": self.service,
            "value": self.value,
        }


@dataclass(frozen=True)
class DockerDeploymentPlan:
    tenant_key: str
    runtime_strategy: str
    single_instance_env_ready: bool
    side_by_side_ready: bool
    live_dynamic_runtime_ready: bool
    compose_files: list[str]
    env_file_strategy: str
    suggested_env_file: str
    blockers: list[DockerPlanIssue] = field(default_factory=list)
    warnings: list[DockerPlanIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    suggested_commands: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "single_instance_env_ready": self.single_instance_env_ready,
            "side_by_side_ready": self.side_by_side_ready,
            "live_dynamic_runtime_ready": self.live_dynamic_runtime_ready,
            "compose_files": self.compose_files,
            "env_file_strategy": self.env_file_strategy,
            "suggested_env_file": self.suggested_env_file,
            "blockers": [issue.to_dict() for issue in self.blockers],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
            "suggested_commands": self.suggested_commands,
        }


def build_docker_deployment_plan(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    compose_files: Iterable[str | Path] = DEFAULT_COMPOSE_FILES,
    require_quality_gates: bool = True,
) -> DockerDeploymentPlan:
    runtime_plan = build_runtime_launch_plan(
        bundle,
        config_root=config_root,
        require_quality_gates=require_quality_gates,
    )
    compose_paths = [Path(path) for path in compose_files]
    blockers: list[DockerPlanIssue] = []
    warnings: list[DockerPlanIssue] = []
    env_file_uses: list[str] = []

    for compose_path in compose_paths:
        if not compose_path.exists():
            warnings.append(
                DockerPlanIssue(
                    severity="warning",
                    code="compose_file_missing",
                    file=str(compose_path),
                    message="Compose file was not found; it was skipped.",
                )
            )
            continue
        payload = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
        services = payload.get("services") or {}
        if isinstance(services, dict):
            for service_name, service in services.items():
                if not isinstance(service, dict):
                    continue
                container_name = service.get("container_name")
                if container_name:
                    blockers.append(
                        DockerPlanIssue(
                            severity="blocker",
                            code="fixed_container_name",
                            file=str(compose_path),
                            service=str(service_name),
                            value=str(container_name),
                            message="Fixed container_name blocks side-by-side tenant deployments on the same Docker host.",
                        )
                    )
                for env_file in _as_list(service.get("env_file")):
                    env_file_uses.append(str(env_file))
                    if str(env_file) == ".env":
                        blockers.append(
                            DockerPlanIssue(
                                severity="blocker",
                                code="literal_env_file",
                                file=str(compose_path),
                                service=str(service_name),
                                value=".env",
                                message="Service uses literal .env; a tenant-specific env file needs an overlay or controlled .env swap.",
                            )
                        )
                for port in _as_list(service.get("ports")):
                    if isinstance(port, str) and ":-" in port:
                        warnings.append(
                            DockerPlanIssue(
                                severity="warning",
                                code="default_port_may_collide",
                                file=str(compose_path),
                                service=str(service_name),
                                value=port,
                                message="Published port has a default value; side-by-side deployments must override it per tenant.",
                            )
                        )
        volumes = payload.get("volumes") or {}
        if isinstance(volumes, dict):
            for volume_name, volume in volumes.items():
                if isinstance(volume, dict) and volume.get("name"):
                    blockers.append(
                        DockerPlanIssue(
                            severity="blocker",
                            code="fixed_volume_name",
                            file=str(compose_path),
                            value=f"{volume_name}:{volume.get('name')}",
                            message="Fixed named volume blocks isolated side-by-side tenant data stores.",
                        )
                    )
        networks = payload.get("networks") or {}
        if isinstance(networks, dict):
            for network_name, network in networks.items():
                if isinstance(network, dict) and network.get("external"):
                    warnings.append(
                        DockerPlanIssue(
                            severity="warning",
                            code="external_network_reuse",
                            file=str(compose_path),
                            value=f"{network_name}:{network.get('name')}",
                            message="External network reuse is fine for current OMU, but side-by-side tenants need deliberate network naming.",
                        )
                    )

    live_dynamic_ready = bundle.tenant.runtime_strategy == "classic_protected"
    if bundle.tenant.runtime_strategy != "classic_protected":
        blockers.append(
            DockerPlanIssue(
                severity="blocker",
                code="dynamic_runtime_adapter_not_wired",
                message="Tenant profile can be validated, but live dynamic routing adapter is not wired yet.",
                value=bundle.tenant.runtime_strategy,
            )
        )

    side_by_side_ready = not blockers
    env_strategy = (
        "classic .env is safe for OMU; generated tenant env files are inspection/shadow artifacts until an overlay is added."
    )
    suggested_env_file = f"tmp/{bundle.tenant.tenant_key}.tenant.env"
    notes = [
        "This plan is read-only: it does not generate compose overrides, copy .env, or start containers.",
        "Current Docker files are suitable for one active OMU-style deployment, not simultaneous isolated tenants.",
        "Tenant packages can include draft compose artifacts, but they must be validated before any side-by-side Docker run.",
    ]
    suggested_commands = [
        f".\\venv\\Scripts\\python.exe -m scripts.tenant runtime-plan --tenant {bundle.tenant.tenant_key} --env-output {suggested_env_file}",
        f".\\venv\\Scripts\\python.exe -m scripts.tenant runtime-env-check --tenant {bundle.tenant.tenant_key} --env-file {suggested_env_file}",
    ]

    return DockerDeploymentPlan(
        tenant_key=bundle.tenant.tenant_key,
        runtime_strategy=bundle.tenant.runtime_strategy,
        single_instance_env_ready=runtime_plan.compose_env_ready,
        side_by_side_ready=side_by_side_ready,
        live_dynamic_runtime_ready=live_dynamic_ready,
        compose_files=[str(path) for path in compose_paths],
        env_file_strategy=env_strategy,
        suggested_env_file=suggested_env_file,
        blockers=blockers,
        warnings=warnings,
        notes=notes,
        suggested_commands=suggested_commands,
    )


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
