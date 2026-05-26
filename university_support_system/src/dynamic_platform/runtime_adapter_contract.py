"""Runtime adapter boundary report for the dynamic platform.

This module documents the future live binding contract without importing or
patching the current Slack/API/router runtime. It is a guardrail artifact: the
dynamic platform can be prepared, but live request handling stays classic until
an explicit adapter implementation is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class RuntimeAdapterContract:
    tenant_key: str
    runtime_strategy: str
    adapter_status: str
    classic_runtime_must_remain_owner: bool
    dynamic_live_binding_allowed: bool
    allowed_modes: list[str]
    blocked_modes: list[str]
    request_contract: dict[str, Any]
    response_contract: dict[str, Any]
    telemetry_contract: list[str]
    safety_requirements: list[str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "adapter_status": self.adapter_status,
            "classic_runtime_must_remain_owner": self.classic_runtime_must_remain_owner,
            "dynamic_live_binding_allowed": self.dynamic_live_binding_allowed,
            "allowed_modes": self.allowed_modes,
            "blocked_modes": self.blocked_modes,
            "request_contract": self.request_contract,
            "response_contract": self.response_contract,
            "telemetry_contract": self.telemetry_contract,
            "safety_requirements": self.safety_requirements,
            "notes": self.notes,
        }


def build_runtime_adapter_contract(bundle: DynamicPlatformBundle) -> RuntimeAdapterContract:
    is_classic = bundle.tenant.runtime_strategy == "classic_protected"
    allowed_modes = ["offline_plan", "shadow_decision_preview", "shadow_runtime_replay"]
    blocked_modes = ["dynamic_pilot_live_requests", "dynamic_on_live_requests"]
    if is_classic:
        blocked_modes.append("dynamic_shadow_as_user_response")

    return RuntimeAdapterContract(
        tenant_key=bundle.tenant.tenant_key,
        runtime_strategy=bundle.tenant.runtime_strategy,
        adapter_status="not_wired",
        classic_runtime_must_remain_owner=is_classic,
        dynamic_live_binding_allowed=False,
        allowed_modes=allowed_modes,
        blocked_modes=blocked_modes,
        request_contract={
            "required_fields": [
                "tenant_key",
                "conversation_id",
                "user_id",
                "query",
                "locale",
                "timezone",
            ],
            "optional_fields": [
                "uploaded_files",
                "conversation_state",
                "requested_capabilities",
                "source_scope",
            ],
            "forbidden_side_effects_in_shadow": [
                "write_conversation_state",
                "write_answer_cache",
                "post_slack_message",
                "mutate_classic_router_context",
            ],
        },
        response_contract={
            "required_fields": [
                "answer",
                "answer_status",
                "selected_capabilities",
                "agents",
                "sources",
                "final_owner",
                "telemetry",
            ],
            "answer_status_values": [
                "shadow_decision_only",
                "answered",
                "needs_clarification",
                "not_found",
                "unsafe_to_answer",
                "runtime_error",
            ],
            "shadow_response_rule": "Shadow output is telemetry only; it must not replace the user-facing classic answer.",
        },
        telemetry_contract=[
            "tenant_key",
            "runtime_strategy",
            "capability",
            "agent_order",
            "parallel_groups",
            "final_owner",
            "source_ids",
            "source_families",
            "contract_violations",
            "answer_quality",
            "latency_ms",
        ],
        safety_requirements=[
            "Classic runtime directories must not import src.dynamic_platform before an explicit adapter phase.",
            "OMU must stay runtime_strategy=classic_protected until golden replay and Slack replay pass.",
            "Dynamic shadow mode may compute decisions, but cannot write cache/state or post answers.",
            "Dynamic pilot/on modes require a separate adapter implementation and acceptance gate.",
            "Live dynamic answers require runtime activation guard: package audit, tenant isolation, secrets, golden replay, narrow live replay, tenant allowlist, adapter implementation, and explicit operator approval.",
            "Tenant env changes require runtime-env-check and readiness before Docker use.",
        ],
        notes=[
            "This report is offline documentation, not a live adapter.",
            "It does not call Slack, API, router, agents, RAG, DB, OCR, or LLM.",
            "Use it to keep future dynamic runtime work from leaking into the current OMU flow.",
        ],
    )
