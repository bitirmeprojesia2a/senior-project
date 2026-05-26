"""Tenant-scoped runtime namespace helpers for future dynamic adapters.

The helpers generate cache/state/upload keys only. They do not connect to
Redis, databases, filesystems, Slack, APIs, or model services.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from src.dynamic_platform.models import DynamicPlatformBundle

NamespaceKind = Literal[
    "answer_cache",
    "retrieval_cache",
    "conversation_state",
    "uploaded_context",
    "model_artifacts",
]

_TENANT_DATA_KINDS: set[NamespaceKind] = {
    "answer_cache",
    "retrieval_cache",
    "conversation_state",
    "uploaded_context",
}
_ALL_KINDS: set[NamespaceKind] = _TENANT_DATA_KINDS | {"model_artifacts"}


@dataclass(frozen=True)
class RuntimeNamespaceKey:
    kind: NamespaceKind
    key: str
    tenant_key: str
    shared_between_tenants: bool
    writes_allowed_in_shadow: bool
    components: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "key": self.key,
            "tenant_key": self.tenant_key,
            "shared_between_tenants": self.shared_between_tenants,
            "writes_allowed_in_shadow": self.writes_allowed_in_shadow,
            "components": self.components,
        }


@dataclass(frozen=True)
class RuntimeNamespaceValidation:
    ok: bool
    tenant_key: str
    checked_keys: list[dict[str, Any]]
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "tenant_key": self.tenant_key,
            "checked_keys": self.checked_keys,
            "errors": self.errors,
        }


class RuntimeNamespaceBuilder:
    def __init__(self, bundle: DynamicPlatformBundle):
        self.bundle = bundle
        self.tenant_key = bundle.tenant.tenant_key

    def prefix(self, kind: NamespaceKind) -> str:
        if kind not in _ALL_KINDS:
            raise ValueError(f"Unsupported runtime namespace kind: {kind}")
        if kind == "model_artifacts":
            return "shared:model_cache:"
        return f"tenant:{self.tenant_key}:{kind}:"

    def answer_cache_key(self, *, query: str, source_scope: dict[str, Any] | None = None) -> RuntimeNamespaceKey:
        scope = _stable_hash(source_scope or {})
        digest = _stable_hash({"query": query.strip(), "source_scope": source_scope or {}})
        return self._key(
            "answer_cache",
            f"scope:{scope}:query:{digest}",
            {"query_hash": digest, "source_scope_hash": scope},
        )

    def retrieval_cache_key(self, *, query: str, source_family: str, source_ids: list[str] | None = None) -> RuntimeNamespaceKey:
        digest = _stable_hash(
            {
                "query": query.strip(),
                "source_family": source_family,
                "source_ids": sorted(source_ids or []),
            }
        )
        return self._key(
            "retrieval_cache",
            f"family:{_slug(source_family)}:query:{digest}",
            {"query_hash": digest, "source_family": source_family},
        )

    def conversation_state_key(self, *, conversation_id: str) -> RuntimeNamespaceKey:
        return self._key(
            "conversation_state",
            f"conversation:{_slug(conversation_id)}",
            {"conversation_id": conversation_id},
        )

    def uploaded_context_key(self, *, conversation_id: str, user_id: str, file_id: str) -> RuntimeNamespaceKey:
        return self._key(
            "uploaded_context",
            f"conversation:{_slug(conversation_id)}:user:{_slug(user_id)}:file:{_slug(file_id)}",
            {"conversation_id": conversation_id, "user_id": user_id, "file_id": file_id},
        )

    def model_artifact_key(self, *, model_id: str) -> RuntimeNamespaceKey:
        return RuntimeNamespaceKey(
            kind="model_artifacts",
            key=f"{self.prefix('model_artifacts')}model:{_slug(model_id)}",
            tenant_key=self.tenant_key,
            shared_between_tenants=True,
            writes_allowed_in_shadow=False,
            components={"model_id": model_id},
        )

    def expected_prefixes(self) -> dict[str, str]:
        return {kind: self.prefix(kind) for kind in sorted(_ALL_KINDS)}

    def validate_keys(self, keys: list[RuntimeNamespaceKey]) -> RuntimeNamespaceValidation:
        errors: list[str] = []
        checked: list[dict[str, Any]] = []
        for item in keys:
            payload = item.to_dict()
            checked.append(payload)
            if item.kind in _TENANT_DATA_KINDS:
                expected = self.prefix(item.kind)
                if not item.key.startswith(expected):
                    errors.append(f"{item.kind}: key does not start with tenant prefix {expected}")
                if item.shared_between_tenants:
                    errors.append(f"{item.kind}: tenant data key cannot be shared between tenants")
            elif item.kind == "model_artifacts":
                if not item.key.startswith(self.prefix("model_artifacts")):
                    errors.append("model_artifacts: key does not start with shared model cache prefix")
            else:
                errors.append(f"{item.kind}: unsupported namespace kind")
            if item.writes_allowed_in_shadow:
                errors.append(f"{item.kind}: shadow runtime writes must be blocked")
        return RuntimeNamespaceValidation(
            ok=not errors,
            tenant_key=self.tenant_key,
            checked_keys=checked,
            errors=errors,
        )

    def _key(self, kind: NamespaceKind, suffix: str, components: dict[str, str]) -> RuntimeNamespaceKey:
        return RuntimeNamespaceKey(
            kind=kind,
            key=f"{self.prefix(kind)}{suffix}",
            tenant_key=self.tenant_key,
            shared_between_tenants=False,
            writes_allowed_in_shadow=False,
            components=components,
        )


def build_runtime_namespace_preview(bundle: DynamicPlatformBundle) -> dict[str, Any]:
    builder = RuntimeNamespaceBuilder(bundle)
    sample_keys = [
        builder.answer_cache_key(query="sample query", source_scope={"source_family": "sample"}),
        builder.retrieval_cache_key(query="sample query", source_family="sample_documents"),
        builder.conversation_state_key(conversation_id="sample-conversation"),
        builder.uploaded_context_key(conversation_id="sample-conversation", user_id="sample-user", file_id="sample-file"),
        builder.model_artifact_key(model_id="sample-model"),
    ]
    validation = builder.validate_keys(sample_keys)
    return {
        "tenant_key": bundle.tenant.tenant_key,
        "runtime_strategy": bundle.tenant.runtime_strategy,
        "ok": validation.ok,
        "expected_prefixes": builder.expected_prefixes(),
        "sample_keys": [item.to_dict() for item in sample_keys],
        "validation": validation.to_dict(),
        "notes": [
            "This preview generates keys only; it performs no writes.",
            "Tenant data namespaces are tenant-scoped; model artifacts may use shared cache.",
            "Shadow runtime writes remain blocked for every namespace.",
        ],
    }


def _stable_hash(value: Any) -> str:
    return hashlib.sha256(repr(_normalize(value)).encode("utf-8")).hexdigest()[:16]


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple, set)):
        return [_normalize(item) for item in value]
    return value


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(value).strip())
    return slug[:160] or "empty"
