"""Guarded live adapter boundary for dynamic tenant runtime experiments.

This module is deliberately kept inside ``src.dynamic_platform``. It does not
wire itself into Slack, API, router, or the protected classic runtime. Callers
must pass an explicit activation decision input; otherwise the adapter refuses
to answer.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.runtime import DynamicRuntimeOrchestrator, DynamicRuntimeQuery
from src.dynamic_platform.runtime_activation_guard import RuntimeActivationInput, evaluate_runtime_activation
from src.dynamic_platform.runtime_adapter_draft import DynamicRuntimeRequest, DynamicRuntimeResponse
from src.dynamic_platform.runtime_namespace import RuntimeNamespaceBuilder


@dataclass(frozen=True)
class DynamicLiveAdapterOptions:
    project_root: str | Path = "."
    enforce_capability_allowlist: bool = True


class DynamicRuntimeLiveAdapter:
    """Small guarded adapter around the profile-driven dynamic runtime."""

    adapter_status = "implemented_guarded_not_wired"

    def __init__(self, bundle: DynamicPlatformBundle, *, options: DynamicLiveAdapterOptions | None = None) -> None:
        self.bundle = bundle
        self.options = options or DynamicLiveAdapterOptions()

    def handle(
        self,
        request: DynamicRuntimeRequest,
        activation: RuntimeActivationInput | None = None,
    ) -> DynamicRuntimeResponse:
        started = perf_counter()
        namespace = RuntimeNamespaceBuilder(self.bundle)
        namespace_keys = [
            namespace.answer_cache_key(query=request.query, source_scope=request.source_scope),
            namespace.conversation_state_key(conversation_id=request.conversation_id),
        ]
        namespace_validation = namespace.validate_keys(namespace_keys)

        if request.tenant_key != self.bundle.tenant.tenant_key:
            return self._refuse(
                request,
                started_at=started,
                reason="request_tenant_mismatch",
                detail=(
                    f"Request tenant {request.tenant_key!r} does not match loaded tenant "
                    f"{self.bundle.tenant.tenant_key!r}."
                ),
                namespace_payload={
                    "ok": namespace_validation.ok,
                    "keys": [item.to_dict() for item in namespace_keys],
                    "errors": namespace_validation.errors,
                },
            )

        activation_decision = evaluate_runtime_activation(self.bundle, activation)
        if not activation_decision.live_binding_allowed:
            return self._refuse(
                request,
                started_at=started,
                reason="activation_guard_blocked",
                detail="Dynamic live request handling is blocked by runtime activation guard.",
                activation_guard=activation_decision.to_dict(),
                namespace_payload={
                    "ok": namespace_validation.ok,
                    "keys": [item.to_dict() for item in namespace_keys],
                    "errors": namespace_validation.errors,
                },
            )

        capability_blocker = self._capability_allowlist_blocker(request, activation)
        if capability_blocker:
            return self._refuse(
                request,
                started_at=started,
                reason="capability_not_allowlisted",
                detail=capability_blocker,
                activation_guard=activation_decision.to_dict(),
                namespace_payload={
                    "ok": namespace_validation.ok,
                    "keys": [item.to_dict() for item in namespace_keys],
                    "errors": namespace_validation.errors,
                },
            )

        runtime = DynamicRuntimeOrchestrator(self.bundle, project_root=self.options.project_root)
        runtime_answer = runtime.answer(
            DynamicRuntimeQuery(
                tenant_key=request.tenant_key,
                query=request.query,
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                requested_capabilities=request.requested_capabilities,
            )
        )
        payload = runtime_answer.to_dict()
        telemetry = dict(payload.get("telemetry") or {})
        telemetry.update(
            {
                "adapter_status": self.adapter_status,
                "activation_guard": activation_decision.to_dict(),
                "namespace_preview": {
                    "ok": namespace_validation.ok,
                    "keys": [item.to_dict() for item in namespace_keys],
                    "errors": namespace_validation.errors,
                },
                "adapter_latency_ms": round((perf_counter() - started) * 1000, 2),
                "side_effect_policy": "no_cache_or_state_writes_in_adapter",
            }
        )
        return DynamicRuntimeResponse(
            tenant_key=self.bundle.tenant.tenant_key,
            answer=str(payload.get("answer") or ""),
            answer_status=str(payload.get("answer_status") or "runtime_error"),
            selected_capabilities=list(payload.get("selected_capabilities") or []),
            agents=list(payload.get("agents") or []),
            sources=list(payload.get("sources") or []),
            final_owner=payload.get("final_owner"),
            telemetry=telemetry,
            safety_notes=[
                "Guarded dynamic adapter handled this request only after activation guard passed.",
                "Adapter did not write cache, conversation state, uploaded context, or classic runtime state.",
                "This module is not wired into Slack/API/router by itself.",
            ],
        )

    def _capability_allowlist_blocker(
        self,
        request: DynamicRuntimeRequest,
        activation: RuntimeActivationInput | None,
    ) -> str | None:
        if not self.options.enforce_capability_allowlist:
            return None
        allowed = set((activation or RuntimeActivationInput()).allowed_capabilities)
        if not allowed:
            return None
        requested = set(request.requested_capabilities)
        if not requested:
            return "Capability allowlist is present, but the request did not declare requested_capabilities."
        missing = sorted(requested - allowed)
        if missing:
            return f"Requested capabilities are outside the explicit allowlist: {', '.join(missing)}"
        return None

    def _refuse(
        self,
        request: DynamicRuntimeRequest,
        *,
        started_at: float,
        reason: str,
        detail: str,
        activation_guard: dict[str, Any] | None = None,
        namespace_payload: dict[str, Any] | None = None,
    ) -> DynamicRuntimeResponse:
        return DynamicRuntimeResponse(
            tenant_key=self.bundle.tenant.tenant_key,
            answer="",
            answer_status="unsafe_to_answer",
            selected_capabilities=[],
            agents=[],
            sources=[],
            final_owner=None,
            telemetry={
                "adapter_status": self.adapter_status,
                "runtime_strategy": self.bundle.tenant.runtime_strategy,
                "reason": reason,
                "detail": detail,
                "requested_tenant": request.tenant_key,
                "activation_guard": activation_guard,
                "namespace_preview": namespace_payload or {},
                "adapter_latency_ms": round((perf_counter() - started_at) * 1000, 2),
            },
            safety_notes=[
                detail,
                "No user-facing dynamic answer was produced.",
                "No cache, conversation state, uploaded context, Slack, API, router, DB, or classic runtime side effect was performed.",
            ],
        )
