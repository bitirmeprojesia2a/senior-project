"""No-download readiness gate for a future dynamic runtime smoke.

This module does not start services and does not pull/build images. It checks
whether the tenant package, resolved compose config, and local Docker image
cache are ready for a separately approved smoke run.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.compose_config_audit import run_compose_config_audit


DEFAULT_IMAGE_REF = "university_support_system-app:latest"


@dataclass(frozen=True)
class RuntimeSmokeGate:
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
class RuntimeSmokeReadinessReport:
    tenant_key: str
    package_dir: str
    image_ref: str
    ok: bool
    status: str
    gates: list[RuntimeSmokeGate]
    suggested_commands: list[str]
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "package_dir": self.package_dir,
            "image_ref": self.image_ref,
            "ok": self.ok,
            "status": self.status,
            "gates": [gate.to_dict() for gate in self.gates],
            "suggested_commands": self.suggested_commands,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "notes": self.notes,
        }


def run_runtime_smoke_readiness(
    *,
    tenant_key: str,
    config_root: str | Path = "configs/dynamic_platform",
    package_dir: str | Path | None = None,
    image_ref: str | None = None,
) -> RuntimeSmokeReadinessReport:
    package_path = Path(package_dir or Path("tmp/tenant_packages") / tenant_key)
    tenant_env = _read_env_file(package_path / "tenant.env")
    resolved_image = image_ref or tenant_env.get("A2A_IMAGE_REF") or DEFAULT_IMAGE_REF
    gates: list[RuntimeSmokeGate] = []
    blockers: list[str] = []
    warnings: list[str] = []

    package_exists = package_path.exists() and (package_path / "tenant.env").exists()
    gates.append(
        RuntimeSmokeGate(
            gate_id="tenant_package_exists",
            ok=package_exists,
            message="Tenant package and tenant.env are present." if package_exists else "Tenant package or tenant.env is missing.",
            detail={"package_dir": str(package_path)},
        )
    )
    if not package_exists:
        blockers.append("tenant package is missing; run scripts.tenant package first")

    compose_report = run_compose_config_audit(
        tenant_key=tenant_key,
        config_root=config_root,
        package_dir=package_path,
    )
    gates.append(
        RuntimeSmokeGate(
            gate_id="compose_config_audit",
            ok=compose_report.ok,
            message="Docker compose config safety audit passed."
            if compose_report.ok
            else "Docker compose config safety audit failed.",
            detail={
                "default_services": compose_report.default_services,
                "dynamic_agent_services": compose_report.dynamic_agent_services,
                "error_count": len(compose_report.errors),
            },
        )
    )
    if not compose_report.ok:
        blockers.append("compose-config-audit failed; do not run dynamic smoke")

    image_info = _inspect_local_image(resolved_image)
    image_present = image_info.get("present") is True
    gates.append(
        RuntimeSmokeGate(
            gate_id="local_image_present",
            ok=image_present,
            message="Requested Docker image is available locally."
            if image_present
            else "Requested Docker image is not available locally.",
            detail=image_info,
        )
    )
    if image_info.get("inspect_available") is False:
        blockers.append("Docker image inspect is not available; confirm Docker Desktop/API access before no-download smoke")
    elif not image_present:
        blockers.append("required Docker image is not present locally; a smoke would pull/build unless image is prepared")

    if image_present:
        warnings.append(
            "local image presence does not prove the image contains newly edited files; rebuild may still be required after code changes"
        )

    ok = all(gate.ok for gate in gates)
    return RuntimeSmokeReadinessReport(
        tenant_key=tenant_key,
        package_dir=str(package_path),
        image_ref=resolved_image,
        ok=ok,
        status="ready_for_no_download_smoke" if ok else "runtime_smoke_blocked",
        gates=gates,
        suggested_commands=_suggested_commands(tenant_key, package_path),
        blockers=blockers,
        warnings=warnings,
        notes=[
            "This readiness check does not start Docker services, build images, pull images, or call models.",
            "Use the suggested commands only after explicit approval for a runtime smoke.",
            "Use --pull never and --no-build for no-download smoke attempts.",
        ],
    )


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _inspect_local_image(image_ref: str) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["docker", "image", "inspect", image_ref],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return {"present": False, "inspect_available": False, "image_ref": image_ref, "error": str(exc)}
    if completed.returncode != 0:
        error_text = (completed.stderr or completed.stdout or "").strip()[:500]
        lowered = error_text.lower()
        inspect_available = not any(
            marker in lowered
            for marker in (
                "permission denied",
                "cannot connect",
                "is the docker daemon running",
                "error during connect",
            )
        )
        return {
            "present": False,
            "inspect_available": inspect_available,
            "image_ref": image_ref,
            "error": error_text,
        }
    try:
        payload = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError:
        payload = []
    first = payload[0] if isinstance(payload, list) and payload else {}
    if not isinstance(first, dict):
        first = {}
    return {
        "present": True,
        "image_ref": image_ref,
        "id": first.get("Id"),
        "created": first.get("Created"),
    }


def _suggested_commands(tenant_key: str, package_path: Path) -> list[str]:
    env_file = package_path / "tenant.env"
    override = package_path / "docker-compose.tenant.override.draft.yml"
    compose_prefix = (
        f"$env:COMPOSE_DISABLE_ENV_FILE='1'; docker compose --env-file {env_file} "
        f"-f docker-compose.yml -f docker-compose.a2a.yml -f docker-compose.slack.yml -f {override}"
    )
    compose_profile_prefix = (
        f"$env:COMPOSE_DISABLE_ENV_FILE='1'; docker compose --profile tenant-dynamic-agents "
        f"--env-file {env_file} -f docker-compose.yml -f docker-compose.a2a.yml "
        f"-f docker-compose.slack.yml -f {override}"
    )
    return [
        f"python -m scripts.tenant compose-config-audit --tenant {tenant_key} --package-dir {package_path}",
        f"{compose_prefix} config --services",
        f"{compose_prefix} up -d --no-build --pull never postgres redis chromadb api",
        f"{compose_profile_prefix} up -d --no-build --pull never postgres redis chromadb api",
    ]
