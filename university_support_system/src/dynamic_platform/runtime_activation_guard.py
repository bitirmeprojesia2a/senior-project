"""Live adapter activation guard for dynamic tenants.

This module does not wire the dynamic platform into Slack/API/router. It only
codifies the gates a future live adapter must satisfy before it is allowed to
answer a user-facing request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class RuntimeActivationInput:
    package_audit_ok: bool = False
    runtime_isolation_ok: bool = False
    secret_readiness_ok: bool = False
    golden_replay_ok: bool = False
    narrow_live_replay_ok: bool = False
    explicit_operator_approval: bool = False
    adapter_live_binding_implemented: bool = False
    requested_live_mode: str = "shadow"
    allowed_tenants: list[str] = field(default_factory=list)
    allowed_capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_audit_ok": self.package_audit_ok,
            "runtime_isolation_ok": self.runtime_isolation_ok,
            "secret_readiness_ok": self.secret_readiness_ok,
            "golden_replay_ok": self.golden_replay_ok,
            "narrow_live_replay_ok": self.narrow_live_replay_ok,
            "explicit_operator_approval": self.explicit_operator_approval,
            "adapter_live_binding_implemented": self.adapter_live_binding_implemented,
            "requested_live_mode": self.requested_live_mode,
            "allowed_tenants": self.allowed_tenants,
            "allowed_capabilities": self.allowed_capabilities,
        }


@dataclass(frozen=True)
class RuntimeActivationDecision:
    tenant_key: str
    runtime_strategy: str
    live_binding_allowed: bool
    status: str
    required_gates: list[str]
    passed_gates: list[str]
    blockers: list[str]
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "live_binding_allowed": self.live_binding_allowed,
            "status": self.status,
            "required_gates": self.required_gates,
            "passed_gates": self.passed_gates,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "notes": self.notes,
        }


REQUIRED_LIVE_GATES = [
    "runtime_strategy_dynamic_pilot_or_on",
    "tenant_allowlisted",
    "adapter_live_binding_implemented",
    "package_audit_ok",
    "runtime_isolation_ok",
    "secret_readiness_ok",
    "golden_replay_ok",
    "narrow_live_replay_ok",
    "explicit_operator_approval",
]


def evaluate_runtime_activation(
    bundle: DynamicPlatformBundle,
    activation: RuntimeActivationInput | None = None,
) -> RuntimeActivationDecision:
    activation = activation or RuntimeActivationInput()
    tenant_key = bundle.tenant.tenant_key
    runtime_strategy = bundle.tenant.runtime_strategy
    passed: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    if runtime_strategy in {"dynamic_pilot", "dynamic_on"} and activation.requested_live_mode in {"dynamic_pilot", "dynamic_on"}:
        passed.append("runtime_strategy_dynamic_pilot_or_on")
    else:
        blockers.append(
            "runtime_strategy_dynamic_pilot_or_on: tenant must request dynamic_pilot/dynamic_on and profile must match"
        )

    if tenant_key in set(activation.allowed_tenants):
        passed.append("tenant_allowlisted")
    else:
        blockers.append("tenant_allowlisted: tenant is not in the explicit live allowlist")

    _require_bool(
        activation.adapter_live_binding_implemented,
        "adapter_live_binding_implemented",
        passed,
        blockers,
        "adapter boundary is still not implemented for user-facing requests",
    )
    _require_bool(
        activation.package_audit_ok,
        "package_audit_ok",
        passed,
        blockers,
        "latest generated tenant package did not pass package audit",
    )
    _require_bool(
        activation.runtime_isolation_ok,
        "runtime_isolation_ok",
        passed,
        blockers,
        "tenant cache/state/upload isolation contract is not confirmed",
    )
    _require_bool(
        activation.secret_readiness_ok,
        "secret_readiness_ok",
        passed,
        blockers,
        "required pilot/live secrets are not ready outside tenant packages",
    )
    _require_bool(
        activation.golden_replay_ok,
        "golden_replay_ok",
        passed,
        blockers,
        "golden replay has not passed for this tenant/profile",
    )
    _require_bool(
        activation.narrow_live_replay_ok,
        "narrow_live_replay_ok",
        passed,
        blockers,
        "narrow live Slack/API replay has not passed",
    )
    _require_bool(
        activation.explicit_operator_approval,
        "explicit_operator_approval",
        passed,
        blockers,
        "manual operator approval is missing",
    )

    if activation.allowed_capabilities:
        warnings.append(
            "capability_allowlist_present: future adapter must enforce requested capability scope per request"
        )

    live_binding_allowed = not blockers
    return RuntimeActivationDecision(
        tenant_key=tenant_key,
        runtime_strategy=runtime_strategy,
        live_binding_allowed=live_binding_allowed,
        status="live_binding_allowed" if live_binding_allowed else "live_binding_blocked",
        required_gates=REQUIRED_LIVE_GATES,
        passed_gates=passed,
        blockers=blockers,
        warnings=warnings,
        notes=[
            "This decision is offline and does not connect Slack/API/router.",
            "Classic runtime remains the owner until this guard is wired by an explicit adapter phase.",
            "All gates must pass together; no single flag authorizes dynamic live answers.",
        ],
    )


def _require_bool(
    value: bool,
    gate_id: str,
    passed: list[str],
    blockers: list[str],
    blocker_message: str,
) -> None:
    if value:
        passed.append(gate_id)
    else:
        blockers.append(f"{gate_id}: {blocker_message}")
