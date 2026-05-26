"""Draft dynamic runtime adapter boundary.

This module is intentionally not wired into Slack/API/router. It gives the
future adapter phase typed request/response objects and a shadow-only preview
implementation, while refusing live user-facing execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.runtime_activation_guard import RuntimeActivationInput, evaluate_runtime_activation
from src.dynamic_platform.runtime_namespace import RuntimeNamespaceBuilder
from src.dynamic_platform.shadow_runtime import build_shadow_runtime_decision


@dataclass(frozen=True)
class DynamicRuntimeRequest:
    tenant_key: str
    conversation_id: str
    user_id: str
    query: str
    locale: str
    timezone: str
    uploaded_files: list[dict[str, Any]] = field(default_factory=list)
    conversation_state: dict[str, Any] = field(default_factory=dict)
    requested_capabilities: list[str] = field(default_factory=list)
    source_scope: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "query": self.query,
            "locale": self.locale,
            "timezone": self.timezone,
            "uploaded_files": self.uploaded_files,
            "conversation_state": self.conversation_state,
            "requested_capabilities": self.requested_capabilities,
            "source_scope": self.source_scope,
        }


@dataclass(frozen=True)
class DynamicRuntimeResponse:
    tenant_key: str
    answer: str
    answer_status: str
    selected_capabilities: list[str]
    agents: list[str]
    sources: list[str]
    final_owner: str | None
    telemetry: dict[str, Any]
    safety_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "answer": self.answer,
            "answer_status": self.answer_status,
            "selected_capabilities": self.selected_capabilities,
            "agents": self.agents,
            "sources": self.sources,
            "final_owner": self.final_owner,
            "telemetry": self.telemetry,
            "safety_notes": self.safety_notes,
        }


class DynamicRuntimeAdapterDraft:
    """Shadow-only adapter skeleton for future live runtime work."""

    adapter_status = "draft_shadow_only_not_wired"

    def __init__(self, bundle: DynamicPlatformBundle):
        self.bundle = bundle

    def preview(self, request: DynamicRuntimeRequest) -> DynamicRuntimeResponse:
        """Return telemetry-only shadow decision output.

        The returned answer is deliberately not user-facing. Classic runtime
        must remain responsible for actual Slack/API answers until the explicit
        live adapter phase is approved.
        """

        decision = build_shadow_runtime_decision(
            self.bundle,
            query=request.query,
            requested_capabilities=request.requested_capabilities,
        )
        payload = decision.to_dict()
        final_owners = payload.get("final_owner_candidates") or []
        namespace = RuntimeNamespaceBuilder(self.bundle)
        namespace_keys = [
            namespace.answer_cache_key(query=request.query, source_scope=request.source_scope),
            namespace.conversation_state_key(conversation_id=request.conversation_id),
        ]
        namespace_validation = namespace.validate_keys(namespace_keys)
        return DynamicRuntimeResponse(
            tenant_key=self.bundle.tenant.tenant_key,
            answer="",
            answer_status="shadow_decision_only",
            selected_capabilities=list(payload.get("selected_capabilities") or []),
            agents=list(payload.get("agents") or []),
            sources=list(payload.get("source_ids") or []),
            final_owner=final_owners[0] if final_owners else None,
            telemetry={
                "adapter_status": self.adapter_status,
                "runtime_strategy": payload.get("runtime_strategy"),
                "runtime_binding_status": payload.get("runtime_binding_status"),
                "match_mode": payload.get("match_mode"),
                "confidence": payload.get("confidence"),
                "source_families": payload.get("source_families") or [],
                "authority_levels": payload.get("authority_levels") or [],
                "execution_plan": payload.get("execution_plan") or [],
                "warnings": payload.get("warnings") or [],
                "namespace_preview": {
                    "ok": namespace_validation.ok,
                    "keys": [item.to_dict() for item in namespace_keys],
                    "errors": namespace_validation.errors,
                },
            },
            safety_notes=[
                "Shadow preview only; do not post this as a user-facing answer.",
                "No cache, conversation state, Slack, API, RAG, DB, or LLM side effect was performed.",
                "Live handling requires an explicit adapter implementation and replay gate.",
            ],
        )

    def handle_live_request(
        self,
        request: DynamicRuntimeRequest,
        activation: RuntimeActivationInput | None = None,
    ) -> DynamicRuntimeResponse:
        """Refuse live execution until the adapter phase is explicitly built."""

        activation_decision = evaluate_runtime_activation(self.bundle, activation)
        namespace = RuntimeNamespaceBuilder(self.bundle)
        namespace_key = namespace.conversation_state_key(conversation_id=request.conversation_id)
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
                "requested_query_length": len(request.query),
                "activation_guard": activation_decision.to_dict(),
                "namespace_preview": {
                    "ok": namespace.validate_keys([namespace_key]).ok,
                    "keys": [namespace_key.to_dict()],
                },
            },
            safety_notes=[
                "Dynamic live request handling is blocked by runtime activation guard.",
                "Classic runtime must remain the user-facing owner.",
            ],
        )
