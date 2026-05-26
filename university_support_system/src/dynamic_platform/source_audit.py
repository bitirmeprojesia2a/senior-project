"""Offline source adapter audit for dynamic tenant profiles.

The audit checks source catalog contracts without opening files, calling web
pages, touching databases, or changing runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle, SourceCatalogEntry


@dataclass(frozen=True)
class SourceAuditIssue:
    severity: str
    code: str
    source_id: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "source_id": self.source_id,
            "message": self.message,
        }


@dataclass
class SourceAuditReport:
    tenant_key: str
    ok: bool = True
    errors: list[SourceAuditIssue] = field(default_factory=list)
    warnings: list[SourceAuditIssue] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def add_error(self, code: str, source_id: str, message: str) -> None:
        self.errors.append(SourceAuditIssue("error", code, source_id, message))
        self.ok = False

    def add_warning(self, code: str, source_id: str, message: str) -> None:
        self.warnings.append(SourceAuditIssue("warning", code, source_id, message))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "summary": self.summary,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
        }


_ADAPTER_AUTHORITY_ALLOWLIST: dict[str, set[str]] = {
    "pdf_document": {"official_policy", "department_document", "external_reference"},
    "docx_document": {"official_policy", "department_document", "external_reference"},
    "web_page": {"official_policy", "department_document", "official_announcement", "external_reference"},
    "announcement_page": {"official_announcement"},
    "calendar_pdf": {"official_structured", "official_policy"},
    "structured_csv": {"official_structured", "department_document"},
    "sql_table": {"official_structured"},
    "api_endpoint": {"official_structured", "external_reference"},
    "slack_uploaded_file": {"uploaded_user_context"},
    "ocr_document": {"uploaded_user_context", "official_policy", "department_document"},
}


def audit_source_adapters(bundle: DynamicPlatformBundle) -> SourceAuditReport:
    enabled_sources = [source for source in bundle.source_catalog.sources if source.enabled]
    report = SourceAuditReport(
        tenant_key=bundle.tenant.tenant_key,
        summary={
            "source_count": len(bundle.source_catalog.sources),
            "enabled_source_count": len(enabled_sources),
            "adapters": sorted({source.adapter for source in bundle.source_catalog.sources}),
            "domains": sorted({source.domain for source in bundle.source_catalog.sources}),
            "source_families": sorted({source.source_family for source in bundle.source_catalog.sources}),
        },
    )
    agents_by_id = {agent.agent_id: agent for agent in bundle.agent_pack.agents}

    for source in bundle.source_catalog.sources:
        _audit_domain(source, bundle, report)
        _audit_authority(source, report)
        _audit_entity_scope(source, bundle, report)
        _audit_connection_hint(source, report)

        owner = agents_by_id.get(source.owner_agent)
        if owner is None:
            continue
        owner_capabilities = set(owner.capabilities)
        missing = sorted(set(source.capabilities) - owner_capabilities)
        if missing:
            report.add_error(
                "source_owner_lacks_capability",
                source.source_id,
                (
                    f"Owner agent {source.owner_agent} does not list source capability/capabilities: "
                    f"{', '.join(missing)}."
                ),
            )
        if source.source_family and source.source_family not in owner.source_families:
            report.add_warning(
                "source_family_not_declared_by_owner",
                source.source_id,
                f"Owner agent {source.owner_agent} does not declare source family {source.source_family}.",
            )

    return report


def _audit_domain(source: SourceCatalogEntry, bundle: DynamicPlatformBundle, report: SourceAuditReport) -> None:
    if source.domain != bundle.domain_pack.domain_pack:
        report.add_error(
            "source_domain_mismatch",
            source.source_id,
            f"Source targets domain {source.domain}, not tenant domain {bundle.domain_pack.domain_pack}.",
        )


def _audit_authority(source: SourceCatalogEntry, report: SourceAuditReport) -> None:
    allowed = _ADAPTER_AUTHORITY_ALLOWLIST.get(source.adapter, set())
    if allowed and source.authority_level not in allowed:
        report.add_error(
            "adapter_authority_mismatch",
            source.source_id,
            (
                f"Adapter {source.adapter} cannot use authority_level {source.authority_level}. "
                f"Allowed: {', '.join(sorted(allowed))}."
            ),
        )


def _audit_entity_scope(source: SourceCatalogEntry, bundle: DynamicPlatformBundle, report: SourceAuditReport) -> None:
    scope = source.entity_scope
    if scope.type == "entity" and not scope.entity_group:
        report.add_error(
            "entity_scope_missing_group",
            source.source_id,
            "Entity-scoped sources must declare entity_group.",
        )
    if scope.type == "entity" and scope.entity_group and scope.entity_group not in bundle.tenant.entities.groups:
        report.add_error(
            "entity_scope_group_unknown",
            source.source_id,
            (
                f"Entity-scoped source references entity_group {scope.entity_group}, "
                "but the tenant profile does not define that entity group."
            ),
        )
    if scope.type != "entity" and scope.entity_ids:
        report.add_warning(
            "entity_ids_without_entity_scope",
            source.source_id,
            f"Source has entity_ids but scope type is {scope.type}.",
        )
    if scope.type == "uploaded_user_context" and source.authority_level != "uploaded_user_context":
        report.add_error(
            "uploaded_scope_authority_mismatch",
            source.source_id,
            "Uploaded user context sources must use uploaded_user_context authority.",
        )


def _audit_connection_hint(source: SourceCatalogEntry, report: SourceAuditReport) -> None:
    has_hint = bool(source.path or source.url or source.collection or source.metadata)
    if has_hint:
        return
    report.add_warning(
        "source_has_no_connection_hint",
        source.source_id,
        "Source has no path, url, collection, or metadata connection hint yet.",
    )
