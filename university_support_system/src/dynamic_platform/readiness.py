"""Combined offline readiness report for tenant profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.docker_plan import build_docker_deployment_plan
from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.quality_gates import run_quality_gates
from src.dynamic_platform.runtime_env_check import RuntimeEnvCheckReport, check_runtime_env
from src.dynamic_platform.runtime_plan import build_runtime_launch_plan


@dataclass(frozen=True)
class TenantReadinessReport:
    tenant_key: str
    ok: bool
    profile_ready: bool
    runtime_env_ready: bool
    docker_single_instance_ready: bool
    docker_side_by_side_ready: bool
    live_dynamic_runtime_ready: bool
    quality_gates: dict[str, Any]
    runtime_plan: dict[str, Any]
    docker_plan: dict[str, Any]
    runtime_env_check: dict[str, Any] | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "profile_ready": self.profile_ready,
            "runtime_env_ready": self.runtime_env_ready,
            "docker_single_instance_ready": self.docker_single_instance_ready,
            "docker_side_by_side_ready": self.docker_side_by_side_ready,
            "live_dynamic_runtime_ready": self.live_dynamic_runtime_ready,
            "quality_gates": self.quality_gates,
            "runtime_plan": self.runtime_plan,
            "runtime_env_check": self.runtime_env_check,
            "docker_plan": self.docker_plan,
            "notes": self.notes,
        }


def build_tenant_readiness_report(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    env_file: str | Path | None = None,
    require_quality_gates: bool = True,
) -> TenantReadinessReport:
    quality = run_quality_gates(
        bundle,
        require_shadow_fixture=require_quality_gates,
    )
    runtime_plan = build_runtime_launch_plan(
        bundle,
        config_root=config_root,
        require_quality_gates=require_quality_gates,
    )
    docker_plan = build_docker_deployment_plan(
        bundle,
        config_root=config_root,
        require_quality_gates=require_quality_gates,
    )
    env_report: RuntimeEnvCheckReport | None = None
    if env_file:
        env_report = check_runtime_env(
            bundle,
            config_root=config_root,
            env_file=env_file,
            require_quality_gates=require_quality_gates,
        )

    runtime_env_ready = runtime_plan.compose_env_ready and (env_report.ok if env_report else True)
    ok = quality.ok and runtime_env_ready and docker_plan.single_instance_env_ready
    notes = [
        "Readiness is offline and does not modify Docker, Slack, API, router, or agent runtime.",
        "Side-by-side Docker readiness is reported separately because the current OMU compose files are intentionally preserved.",
    ]
    if not docker_plan.side_by_side_ready:
        notes.append(
            "Side-by-side tenant deployment requires a validated compose draft; tenant packages include draft artifacts only."
        )
    if bundle.tenant.runtime_strategy != "classic_protected":
        notes.append("Dynamic tenant profile is shadow/planning only until the live runtime adapter is explicitly wired.")

    return TenantReadinessReport(
        tenant_key=bundle.tenant.tenant_key,
        ok=ok,
        profile_ready=quality.ok,
        runtime_env_ready=runtime_env_ready,
        docker_single_instance_ready=docker_plan.single_instance_env_ready,
        docker_side_by_side_ready=docker_plan.side_by_side_ready,
        live_dynamic_runtime_ready=docker_plan.live_dynamic_runtime_ready,
        quality_gates=quality.to_dict(),
        runtime_plan=runtime_plan.to_dict(),
        runtime_env_check=env_report.to_dict() if env_report else None,
        docker_plan=docker_plan.to_dict(),
        notes=notes,
    )
