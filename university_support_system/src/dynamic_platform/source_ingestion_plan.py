"""Offline source ingestion and indexing plan for tenant profiles.

The plan translates source catalog entries into adapter-specific preparation
steps. It deliberately does not open files, call websites, connect to
databases, or build indexes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle, SourceCatalogEntry


@dataclass(frozen=True)
class SourceIngestionStep:
    source_id: str
    adapter: str
    action: str
    owner_agent: str
    source_family: str
    capabilities: list[str]
    authority_level: str
    enabled: bool
    live_connector_required: bool
    preindex_required: bool
    index_target: str | None
    entity_scope: dict[str, Any]
    connection_hints: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "adapter": self.adapter,
            "action": self.action,
            "owner_agent": self.owner_agent,
            "source_family": self.source_family,
            "capabilities": self.capabilities,
            "authority_level": self.authority_level,
            "enabled": self.enabled,
            "live_connector_required": self.live_connector_required,
            "preindex_required": self.preindex_required,
            "index_target": self.index_target,
            "entity_scope": self.entity_scope,
            "connection_hints": self.connection_hints,
            "warnings": self.warnings,
            "notes": self.notes,
        }


@dataclass
class SourceIngestionPlan:
    tenant_key: str
    runtime_strategy: str
    ok: bool
    summary: dict[str, Any]
    steps: list[SourceIngestionStep] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "ok": self.ok,
            "summary": self.summary,
            "steps": [step.to_dict() for step in self.steps],
            "warnings": self.warnings,
            "notes": self.notes,
        }


_ADAPTER_ACTIONS: dict[str, dict[str, Any]] = {
    "pdf_document": {
        "action": "document_parse_chunk_embed",
        "live_connector_required": False,
        "preindex_required": True,
        "hint_policy": "document",
    },
    "docx_document": {
        "action": "document_parse_chunk_embed",
        "live_connector_required": False,
        "preindex_required": True,
        "hint_policy": "document",
    },
    "ocr_document": {
        "action": "ocr_parse_chunk_embed",
        "live_connector_required": False,
        "preindex_required": True,
        "hint_policy": "document",
    },
    "calendar_pdf": {
        "action": "calendar_parse_event_index",
        "live_connector_required": False,
        "preindex_required": True,
        "hint_policy": "document",
    },
    "web_page": {
        "action": "web_snapshot_parse_index",
        "live_connector_required": True,
        "preindex_required": True,
        "hint_policy": "web",
    },
    "announcement_page": {
        "action": "announcement_sync_index",
        "live_connector_required": True,
        "preindex_required": True,
        "hint_policy": "web",
    },
    "structured_csv": {
        "action": "structured_csv_import",
        "live_connector_required": False,
        "preindex_required": True,
        "hint_policy": "file_or_metadata",
    },
    "sql_table": {
        "action": "structured_table_mapping",
        "live_connector_required": True,
        "preindex_required": False,
        "hint_policy": "table",
    },
    "api_endpoint": {
        "action": "api_sync_index",
        "live_connector_required": True,
        "preindex_required": True,
        "hint_policy": "api",
    },
    "slack_uploaded_file": {
        "action": "runtime_uploaded_context_only",
        "live_connector_required": False,
        "preindex_required": False,
        "hint_policy": "runtime_upload",
    },
}


def build_source_ingestion_plan(bundle: DynamicPlatformBundle) -> SourceIngestionPlan:
    steps = [_build_step(source) for source in bundle.source_catalog.sources]
    warnings = [
        f"{step.source_id}: {warning}"
        for step in steps
        for warning in step.warnings
    ]
    enabled_steps = [step for step in steps if step.enabled]
    actions: dict[str, int] = {}
    adapters: dict[str, int] = {}
    for step in enabled_steps:
        actions[step.action] = actions.get(step.action, 0) + 1
        adapters[step.adapter] = adapters.get(step.adapter, 0) + 1

    summary = {
        "source_count": len(steps),
        "enabled_source_count": len(enabled_steps),
        "adapter_counts": dict(sorted(adapters.items())),
        "action_counts": dict(sorted(actions.items())),
        "live_connector_required_count": sum(1 for step in enabled_steps if step.live_connector_required),
        "preindex_required_count": sum(1 for step in enabled_steps if step.preindex_required),
        "warning_count": len(warnings),
    }
    return SourceIngestionPlan(
        tenant_key=bundle.tenant.tenant_key,
        runtime_strategy=bundle.tenant.runtime_strategy,
        ok=True,
        summary=summary,
        steps=steps,
        warnings=warnings,
        notes=[
            "This is an offline source preparation plan.",
            "It does not open files, crawl websites, connect to SQL/API services, or build vector indexes.",
            "Existing OMU runtime remains unchanged; the plan is a handoff/audit artifact.",
        ],
    )


def _build_step(source: SourceCatalogEntry) -> SourceIngestionStep:
    policy = _ADAPTER_ACTIONS[source.adapter]
    hints = _connection_hints(source)
    warnings = _hint_warnings(source, hint_policy=policy["hint_policy"])
    notes = _source_notes(source)
    return SourceIngestionStep(
        source_id=source.source_id,
        adapter=source.adapter,
        action=policy["action"],
        owner_agent=source.owner_agent,
        source_family=source.source_family,
        capabilities=list(source.capabilities),
        authority_level=source.authority_level,
        enabled=source.enabled,
        live_connector_required=bool(policy["live_connector_required"]),
        preindex_required=bool(policy["preindex_required"]),
        index_target=source.collection or source.metadata.get("table") or source.metadata.get("index"),
        entity_scope=source.entity_scope.model_dump(mode="json", exclude_none=True),
        connection_hints=hints,
        warnings=warnings,
        notes=notes,
    )


def _connection_hints(source: SourceCatalogEntry) -> dict[str, Any]:
    hints: dict[str, Any] = {}
    if source.path:
        hints["path"] = source.path
    if source.url:
        hints["url"] = source.url
    if source.collection:
        hints["collection"] = source.collection
    if source.metadata:
        hints["metadata"] = dict(source.metadata)
    return hints


def _hint_warnings(source: SourceCatalogEntry, *, hint_policy: str) -> list[str]:
    hints = _connection_hints(source)
    if not source.enabled:
        return ["source is disabled; ingestion step is informational only"]
    if hint_policy == "runtime_upload":
        return []
    if hint_policy == "document" and not (source.path or source.collection or source.metadata):
        return ["document source has no path, collection, or metadata hint"]
    if hint_policy == "web" and not (source.url or source.metadata):
        return ["web/announcement source has no url or metadata hint"]
    if hint_policy == "file_or_metadata" and not (source.path or source.url or source.metadata):
        return ["structured file source has no path, url, or metadata hint"]
    if hint_policy == "table" and not (source.collection or source.metadata):
        return ["table source has no collection or table metadata hint"]
    if hint_policy == "api" and not (source.url or source.metadata):
        return ["api source has no url or metadata hint"]
    return []


def _source_notes(source: SourceCatalogEntry) -> list[str]:
    notes: list[str] = []
    if source.adapter == "slack_uploaded_file":
        notes.append("Uploaded files are per-conversation context; do not pre-index globally.")
    if source.entity_scope.type == "entity":
        notes.append("Apply tenant entity registry/alias scoping before retrieval.")
    if source.authority_level == "uploaded_user_context":
        notes.append("Treat as user-provided context, not institution-wide policy authority.")
    return notes
