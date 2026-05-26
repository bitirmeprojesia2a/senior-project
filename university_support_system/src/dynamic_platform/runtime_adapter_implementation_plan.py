"""Offline implementation plan for a future dynamic runtime adapter.

This module does not implement live routing. It records the gates, phases, and
rollback rules that must exist before any dynamic adapter can be connected to a
user-facing runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.runtime_adapter_contract import build_runtime_adapter_contract


@dataclass(frozen=True)
class RuntimeAdapterImplementationPhase:
    phase_id: str
    status: str
    title: str
    allowed_work: list[str] = field(default_factory=list)
    forbidden_work: list[str] = field(default_factory=list)
    required_gates: list[str] = field(default_factory=list)
    rollback_policy: str = ""
    output_artifacts: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase_id": self.phase_id,
            "status": self.status,
            "title": self.title,
            "allowed_work": self.allowed_work,
            "forbidden_work": self.forbidden_work,
            "required_gates": self.required_gates,
            "rollback_policy": self.rollback_policy,
            "output_artifacts": self.output_artifacts,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class RuntimeAdapterImplementationPlan:
    tenant_key: str
    ok: bool
    runtime_strategy: str
    implementation_status: str
    live_binding_allowed_now: bool
    adapter_contract: dict[str, Any]
    summary: dict[str, Any]
    phases: list[RuntimeAdapterImplementationPhase]
    non_goals: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "runtime_strategy": self.runtime_strategy,
            "implementation_status": self.implementation_status,
            "live_binding_allowed_now": self.live_binding_allowed_now,
            "adapter_contract": self.adapter_contract,
            "summary": self.summary,
            "phases": [phase.to_dict() for phase in self.phases],
            "non_goals": self.non_goals,
            "notes": self.notes,
        }


def build_runtime_adapter_implementation_plan(
    bundle: DynamicPlatformBundle,
) -> RuntimeAdapterImplementationPlan:
    contract = build_runtime_adapter_contract(bundle).to_dict()
    phases = _phases(bundle)
    live_binding_allowed = False
    return RuntimeAdapterImplementationPlan(
        tenant_key=bundle.tenant.tenant_key,
        ok=True,
        runtime_strategy=bundle.tenant.runtime_strategy,
        implementation_status="guarded_boundary_available_not_wired",
        live_binding_allowed_now=live_binding_allowed,
        adapter_contract=contract,
        summary={
            "phase_count": len(phases),
            "ready_now": [
                phase.phase_id for phase in phases if phase.status in {"ready", "available_offline"}
            ],
            "future_work": [
                phase.phase_id for phase in phases if phase.status in {"future_work", "blocked_until_approved"}
            ],
            "blocked_modes": contract.get("blocked_modes") or [],
            "allowed_modes": contract.get("allowed_modes") or [],
        },
        phases=phases,
        non_goals=[
            "No live request routing is implemented by this plan.",
            "No user-facing answer is produced by this plan.",
            "No cache, conversation state, external source, index, model, or Docker service is touched.",
            "No existing runtime module should import this planning module.",
        ],
        notes=[
            "This is a planning artifact for a future adapter phase.",
            "A tenant can be packaged and audited while live dynamic binding remains disabled.",
            "Any future live adapter must pass package, replay, safety, and narrow live validation gates first.",
        ],
    )


def _phases(bundle: DynamicPlatformBundle) -> list[RuntimeAdapterImplementationPhase]:
    tenant = bundle.tenant.tenant_key
    return [
        RuntimeAdapterImplementationPhase(
            phase_id="offline_profile_and_package",
            status="available_offline",
            title="Freeze tenant profile and generated package before adapter work",
            allowed_work=[
                "Validate tenant, domain, agent, source, and entity registry metadata.",
                "Generate offline package artifacts under tmp/tenant_packages.",
                "Run package and handoff audits.",
            ],
            forbidden_work=[
                "Start services from generated package artifacts.",
                "Replace production environment files without env and replay gates.",
            ],
            required_gates=[
                f"python -m scripts.tenant bootstrap-plan --tenant {tenant}",
                f"python -m scripts.tenant package --tenant {tenant} --force",
                "python -m scripts.tenant handoff-readiness --package-root tmp\\tenant_packages --allow-missing-shadow",
            ],
            rollback_policy="Delete or regenerate package artifacts; no live state should exist in this phase.",
            output_artifacts=[
                "bootstrap_plan.json",
                "package_manifest.json",
                "adapter_handoff_checklist.json",
            ],
        ),
        RuntimeAdapterImplementationPhase(
            phase_id="adapter_boundary_code",
            status="available_offline",
            title="Guarded adapter boundary is implemented but not wired",
            allowed_work=[
                "Use the guarded adapter module in isolated tests or approved pilot harnesses only.",
                "Keep request, response, telemetry, and error fields explicit.",
                "Require activation guard input before producing any dynamic answer.",
            ],
            forbidden_work=[
                "Mix tenant routing into existing runtime logic without an adapter layer.",
                "Import the adapter from protected classic runtime modules.",
                "Write cache or conversation state before tenant isolation tests exist.",
            ],
            required_gates=[
                "Unit tests for request conversion and response conversion.",
                "Safety audit proving the adapter is the only dynamic import boundary.",
                "Shadow replay proving selected capability, agent, source, and final owner telemetry.",
            ],
            rollback_policy="Disable adapter env flag and return to existing runtime path.",
            output_artifacts=[
                "adapter request/response tests",
                "adapter telemetry tests",
                "safety audit report",
            ],
        ),
        RuntimeAdapterImplementationPhase(
            phase_id="tenant_state_and_cache_isolation",
            status="future_work",
            title="Tenant-scoped state, cache, and uploaded context isolation",
            allowed_work=[
                "Namespace cache keys by tenant and runtime strategy.",
                "Namespace conversation state by tenant and conversation id.",
                "Treat uploaded files as runtime-scoped context until explicitly promoted.",
            ],
            forbidden_work=[
                "Share answer cache entries across tenants.",
                "Persist uploaded context into global source catalogs by default.",
                "Reuse one tenant's entity registry for another tenant.",
            ],
            required_gates=[
                "Cache isolation tests.",
                "Conversation state isolation tests.",
                "Uploaded context privacy tests.",
            ],
            rollback_policy="Clear tenant-specific cache namespace and disable adapter env flag.",
        ),
        RuntimeAdapterImplementationPhase(
            phase_id="shadow_runtime_comparison",
            status="available_offline",
            title="Compare shadow decisions before pilot",
            allowed_work=[
                "Run shadow decision fixtures.",
                "Run adapter draft preview.",
                "Compare selected capability, agent, source, owner, and contract telemetry.",
            ],
            forbidden_work=[
                "Post shadow output to users.",
                "Write shadow output to production answer cache.",
            ],
            required_gates=[
                f"python -m scripts.tenant runtime-adapter-draft --tenant {tenant} --query \"...\"",
                f"python -m scripts.tenant shadow-runtime-replay --tenant {tenant}",
                "python -m scripts.tenant handoff-readiness --package-root tmp\\tenant_packages --allow-missing-shadow",
            ],
            rollback_policy="No rollback needed; shadow output should be telemetry only.",
            output_artifacts=[
                "runtime_adapter_draft_preview.json",
                "shadow_runtime_replay.json",
            ],
        ),
        RuntimeAdapterImplementationPhase(
            phase_id="pilot_gate",
            status="blocked_until_approved",
            title="Manual pilot gate for user-facing dynamic behavior",
            allowed_work=[
                "Use a narrow allowlist of tenants, users, channels, and capabilities.",
                "Keep classic response fallback available.",
                "Record route, source, contract, and quality telemetry for every pilot answer.",
            ],
            forbidden_work=[
                "Enable broad dynamic live routing by default.",
                "Enable live behavior without rollback instructions.",
                "Enable pilot for tenants whose package audit is stale.",
            ],
            required_gates=[
                "Fresh package-audit-all.",
                "Runtime activation guard must pass for the exact tenant and requested live mode.",
                "Fresh handoff-readiness.",
                "Golden replay and narrow live replay.",
                "Manual approval for pilot scope.",
            ],
            rollback_policy="Turn runtime strategy back to shadow/disabled and restore the existing runtime owner.",
        ),
        RuntimeAdapterImplementationPhase(
            phase_id="live_rollout",
            status="blocked_until_approved",
            title="Controlled live rollout after pilot",
            allowed_work=[
                "Gradually expand tenant/capability scope.",
                "Keep quality/error telemetry visible.",
                "Keep rollback commands documented with the release.",
            ],
            forbidden_work=[
                "Remove classic fallback before sustained replay and live evidence is clean.",
                "Skip source-owner and answer-quality gates.",
            ],
            required_gates=[
                "Pilot success report.",
                "Fresh golden replay.",
                "Fresh safety audit.",
                "Documented rollback path.",
            ],
            rollback_policy="Disable live adapter mode and route requests through the previous runtime path.",
        ),
    ]
