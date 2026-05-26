"""Tenant runtime isolation contract for future dynamic live adapters.

The contract is offline and descriptive. It does not read or write runtime
cache, conversation state, uploaded files, databases, or external services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle, SourceCatalogEntry


@dataclass(frozen=True)
class IsolationNamespace:
    namespace_id: str
    storage_area: str
    prefix: str
    shared_between_tenants: bool
    writes_allowed_in_shadow: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "namespace_id": self.namespace_id,
            "storage_area": self.storage_area,
            "prefix": self.prefix,
            "shared_between_tenants": self.shared_between_tenants,
            "writes_allowed_in_shadow": self.writes_allowed_in_shadow,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class IsolationCheck:
    check_id: str
    ok: bool
    message: str
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "ok": self.ok,
            "message": self.message,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class RuntimeIsolationContract:
    tenant_key: str
    runtime_strategy: str
    ok: bool
    live_runtime_allowed: bool
    namespaces: list[IsolationNamespace]
    uploaded_context_sources: list[dict[str, Any]]
    checks: list[IsolationCheck]
    required_before_live_runtime: list[str]
    forbidden_in_shadow: list[str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "ok": self.ok,
            "live_runtime_allowed": self.live_runtime_allowed,
            "namespaces": [namespace.to_dict() for namespace in self.namespaces],
            "uploaded_context_sources": self.uploaded_context_sources,
            "checks": [check.to_dict() for check in self.checks],
            "required_before_live_runtime": self.required_before_live_runtime,
            "forbidden_in_shadow": self.forbidden_in_shadow,
            "notes": self.notes,
        }


def build_runtime_isolation_contract(bundle: DynamicPlatformBundle) -> RuntimeIsolationContract:
    tenant_key = bundle.tenant.tenant_key
    namespaces = _namespaces(tenant_key)
    uploaded_sources = [_uploaded_source_record(source) for source in bundle.source_catalog.sources if _is_uploaded_source(source)]
    checks = [
        IsolationCheck(
            check_id="tenant_key_namespace_prefix",
            ok=bool(tenant_key),
            message="Tenant-scoped runtime prefixes can be derived from tenant_key.",
            detail={"tenant_key": tenant_key},
        ),
        IsolationCheck(
            check_id="tenant_data_namespaces_not_shared",
            ok=all(
                not namespace.shared_between_tenants
                for namespace in namespaces
                if namespace.storage_area != "model_cache"
            ),
            message="Tenant data namespaces are not shared between tenants.",
            detail={
                "tenant_data_namespaces": [
                    namespace.namespace_id
                    for namespace in namespaces
                    if namespace.storage_area != "model_cache"
                ]
            },
        ),
        IsolationCheck(
            check_id="shadow_runtime_writes_blocked",
            ok=all(not namespace.writes_allowed_in_shadow for namespace in namespaces),
            message="Shadow runtime cannot write cache, state, or uploaded context.",
            detail={"runtime_strategy": bundle.tenant.runtime_strategy},
        ),
        IsolationCheck(
            check_id="uploaded_context_runtime_scoped",
            ok=all(record["runtime_scoped"] for record in uploaded_sources),
            message="Uploaded context sources are runtime-scoped and are not pre-indexed globally."
            if uploaded_sources
            else "No uploaded context sources are configured.",
            detail={"uploaded_context_source_count": len(uploaded_sources)},
        ),
        IsolationCheck(
            check_id="live_runtime_still_blocked",
            ok=True,
            message="This contract does not authorize live dynamic runtime binding.",
            detail={"live_runtime_allowed": False},
        ),
    ]
    return RuntimeIsolationContract(
        tenant_key=tenant_key,
        runtime_strategy=bundle.tenant.runtime_strategy,
        ok=all(check.ok for check in checks),
        live_runtime_allowed=False,
        namespaces=namespaces,
        uploaded_context_sources=uploaded_sources,
        checks=checks,
        required_before_live_runtime=[
            "Implement explicit tenant namespace use in answer cache keys.",
            "Implement explicit tenant namespace use in conversation state keys.",
            "Keep uploaded file context scoped to tenant, conversation, and user unless promoted by an approved source-ingestion flow.",
            "Run golden replay and narrow live replay with tenant namespace telemetry visible.",
            "Keep model cache sharing separate from tenant data cache sharing.",
        ],
        forbidden_in_shadow=[
            "write_answer_cache",
            "write_conversation_state",
            "persist_uploaded_context_globally",
            "reuse_other_tenant_entity_registry",
            "post_user_facing_dynamic_answer",
        ],
        notes=[
            "This is an offline contract for future adapter implementation.",
            "Model artifacts may share a host cache to reduce downloads; tenant data/state must not share keys.",
            "Passing this contract does not start services or grant live runtime permission.",
        ],
    )


def _namespaces(tenant_key: str) -> list[IsolationNamespace]:
    tenant_prefix = f"tenant:{tenant_key}:"
    return [
        IsolationNamespace(
            namespace_id="answer_cache",
            storage_area="runtime_cache",
            prefix=f"{tenant_prefix}answer_cache:",
            shared_between_tenants=False,
            writes_allowed_in_shadow=False,
            notes=["Cache lookup/store keys must include this prefix before any live dynamic adapter is enabled."],
        ),
        IsolationNamespace(
            namespace_id="retrieval_cache",
            storage_area="runtime_cache",
            prefix=f"{tenant_prefix}retrieval_cache:",
            shared_between_tenants=False,
            writes_allowed_in_shadow=False,
            notes=["Retriever cache keys must include tenant and source scope metadata."],
        ),
        IsolationNamespace(
            namespace_id="conversation_state",
            storage_area="conversation_store",
            prefix=f"{tenant_prefix}conversation:",
            shared_between_tenants=False,
            writes_allowed_in_shadow=False,
            notes=["Conversation state must be partitioned by tenant and conversation id."],
        ),
        IsolationNamespace(
            namespace_id="uploaded_context",
            storage_area="uploaded_user_context",
            prefix=f"{tenant_prefix}uploaded_context:",
            shared_between_tenants=False,
            writes_allowed_in_shadow=False,
            notes=["Uploaded files are runtime context until explicitly promoted by a source ingestion workflow."],
        ),
        IsolationNamespace(
            namespace_id="model_artifacts",
            storage_area="model_cache",
            prefix="shared:model_cache:",
            shared_between_tenants=True,
            writes_allowed_in_shadow=False,
            notes=["Model cache can be shared because it stores model artifacts, not tenant answers or user data."],
        ),
    ]


def _is_uploaded_source(source: SourceCatalogEntry) -> bool:
    return source.adapter in {"slack_uploaded_file", "ocr_document"} or source.authority_level == "uploaded_user_context"


def _uploaded_source_record(source: SourceCatalogEntry) -> dict[str, Any]:
    runtime_scoped = source.entity_scope.type == "uploaded_user_context" and source.authority_level == "uploaded_user_context"
    return {
        "source_id": source.source_id,
        "adapter": source.adapter,
        "source_family": source.source_family,
        "entity_scope_type": source.entity_scope.type,
        "authority_level": source.authority_level,
        "runtime_scoped": runtime_scoped,
    }
