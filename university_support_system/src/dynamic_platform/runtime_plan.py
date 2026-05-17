"""Offline runtime launch plan for dynamic tenant profiles.

The plan explains how a tenant would be passed to Docker/runtime environment
without wiring the dynamic platform into the live Slack/API path yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.quality_gates import run_quality_gates


@dataclass(frozen=True)
class RuntimeLaunchPlan:
    tenant_key: str
    runtime_strategy: str
    compose_env_ready: bool
    live_runtime_enabled: bool
    runtime_binding_status: str
    env: dict[str, str]
    notes: list[str] = field(default_factory=list)
    quality_gates: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "compose_env_ready": self.compose_env_ready,
            "live_runtime_enabled": self.live_runtime_enabled,
            "runtime_binding_status": self.runtime_binding_status,
            "env": self.env,
            "notes": self.notes,
            "quality_gates": self.quality_gates,
        }

    def to_env_text(self) -> str:
        lines = [f"{key}={value}" for key, value in self.env.items()]
        return "\n".join(lines) + "\n"


def build_runtime_launch_plan(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    require_quality_gates: bool = True,
) -> RuntimeLaunchPlan:
    quality_report = run_quality_gates(
        bundle,
        require_shadow_fixture=require_quality_gates,
    )
    runtime_strategy = bundle.tenant.runtime_strategy
    live_runtime_enabled = runtime_strategy == "classic_protected"
    compose_env_ready = quality_report.ok
    status = _runtime_binding_status(runtime_strategy)
    env = {
        "TENANT_KEY": bundle.tenant.tenant_key,
        "TENANT_CONFIG_ROOT": str(Path(config_root).as_posix()),
        "TENANT_RUNTIME_STRATEGY": runtime_strategy,
        "TENANT_DOMAIN_PACK": bundle.tenant.domain_pack,
        "TENANT_AGENT_PACK": bundle.tenant.agent_pack,
        "TENANT_SOURCE_CATALOG": bundle.tenant.source_catalog,
        "TENANT_DISPLAY_NAME": bundle.tenant.display_name,
        "TENANT_BOT_NAME": bundle.tenant.bot_name,
        "TENANT_LOCALE": bundle.tenant.locale,
        "TENANT_TIMEZONE": bundle.tenant.timezone,
        "DYNAMIC_PLATFORM_RUNTIME": "disabled" if runtime_strategy == "classic_protected" else "shadow",
    }
    notes = [
        "This plan is offline and does not modify Docker Compose or the live Slack/API runtime.",
        "Quality gates must pass before a tenant can be considered for runtime pilot/on mode.",
    ]
    if runtime_strategy == "classic_protected":
        notes.append("OMU remains served by the existing classic runtime; tenant env is informational for now.")
    elif runtime_strategy == "dynamic_shadow":
        notes.append("Dynamic tenant config is ready for shadow/profile validation, but live routing is not enabled yet.")
    else:
        notes.append("Runtime strategy requests pilot/on behavior; runtime adapter wiring is still required before Docker launch.")

    return RuntimeLaunchPlan(
        tenant_key=bundle.tenant.tenant_key,
        runtime_strategy=runtime_strategy,
        compose_env_ready=compose_env_ready,
        live_runtime_enabled=live_runtime_enabled,
        runtime_binding_status=status,
        env=env,
        notes=notes,
        quality_gates=quality_report.to_dict(),
    )


def _runtime_binding_status(runtime_strategy: str) -> str:
    if runtime_strategy == "classic_protected":
        return "classic_runtime_active_dynamic_runtime_disabled"
    if runtime_strategy == "dynamic_shadow":
        return "dynamic_profile_ready_shadow_only_runtime_not_wired"
    return "dynamic_runtime_requested_adapter_not_wired"
