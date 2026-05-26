"""Offline portability audit for dynamic tenant profiles.

Validation checks whether a profile is internally consistent. Portability adds a
different question: can this tenant stand on its own without leaking protected,
domain-specific, or another tenant's assumptions into its identifiers and source
contracts?
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.loader import (
    DynamicPlatformLoadError,
    DynamicPlatformPaths,
    load_tenant_bundle,
    load_yaml_model,
)
from src.dynamic_platform.models import DomainPack, DynamicPlatformBundle
from src.dynamic_platform.validator import validate_bundle


@dataclass(frozen=True)
class PortabilityIssue:
    severity: str
    code: str
    message: str
    field: str | None = None
    value: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "field": self.field,
            "value": self.value,
        }


@dataclass
class TenantPortabilityAuditReport:
    tenant_key: str
    ok: bool = True
    checks: dict[str, bool] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    errors: list[PortabilityIssue] = field(default_factory=list)
    warnings: list[PortabilityIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_error(self, code: str, message: str, *, field: str | None = None, value: str | None = None) -> None:
        self.errors.append(PortabilityIssue("error", code, message, field, value))
        self.ok = False

    def add_warning(self, code: str, message: str, *, field: str | None = None, value: str | None = None) -> None:
        self.warnings.append(PortabilityIssue("warning", code, message, field, value))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "checks": self.checks,
            "summary": self.summary,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
        }


@dataclass(frozen=True)
class TenantPortabilityPortfolioRecord:
    tenant_key: str
    ok: bool
    runtime_strategy: str | None = None
    domain_pack: str | None = None
    report: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "runtime_strategy": self.runtime_strategy,
            "domain_pack": self.domain_pack,
            "report": self.report,
            "error": self.error,
        }


@dataclass(frozen=True)
class TenantPortabilityPortfolioReport:
    ok: bool
    config_root: str
    summary: dict[str, Any]
    records: list[TenantPortabilityPortfolioRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "config_root": self.config_root,
            "summary": self.summary,
            "records": [record.to_dict() for record in self.records],
            "notes": self.notes,
        }


def run_tenant_portability_audit(
    bundle: DynamicPlatformBundle,
    *,
    known_tenant_keys: list[str] | None = None,
    known_tenant_source_identifiers: dict[str, set[str]] | None = None,
    restricted_identifier_terms: set[str] | None = None,
    restricted_entity_groups: set[str] | None = None,
) -> TenantPortabilityAuditReport:
    tenant = bundle.tenant
    validation = validate_bundle(bundle)
    known_tenants = sorted(set(known_tenant_keys or [tenant.tenant_key]))
    known_source_identifiers = known_tenant_source_identifiers or {}
    protected_classic = bool(tenant.metadata.get("classic_runtime_protected"))
    restricted_terms = {item for item in (restricted_identifier_terms or set()) if item}
    restricted_groups = {item for item in (restricted_entity_groups or set()) if item}
    report = TenantPortabilityAuditReport(
        tenant_key=tenant.tenant_key,
        summary={
            "runtime_strategy": tenant.runtime_strategy,
            "domain_pack": bundle.domain_pack.domain_pack,
            "agent_pack": bundle.agent_pack.agent_pack,
            "source_catalog": bundle.source_catalog.source_catalog,
            "classic_runtime_protected": protected_classic,
            "known_tenants": known_tenants,
            "entity_groups": sorted(tenant.entities.groups),
            "identifier_count": len(_identifier_records(bundle)),
            "known_source_contract_tenant_count": len(known_source_identifiers),
            "restricted_identifier_term_count": len(restricted_terms),
            "restricted_entity_group_count": len(restricted_groups),
        },
        notes=[
            "Portability audit is offline; it does not start Docker, Slack, API, router, agents, RAG, DB, or LLM.",
            "It checks that dynamic tenants remain profile-driven and do not leak another tenant's identifiers.",
            "Domain-specific restrictions come from domain pack metadata, not hardcoded core rules.",
        ],
    )
    _check_validation(report, validation.to_dict())
    _check_runtime_strategy(report, bundle)
    _check_cross_tenant_leakage(report, bundle, known_tenants)
    _check_restricted_identifier_terms(report, bundle, restricted_terms=restricted_terms)
    _check_entity_groups(report, bundle, restricted_groups=restricted_groups)
    _check_source_paths(report, bundle, known_tenants)
    _check_cross_tenant_source_contracts(report, bundle, known_source_identifiers)
    return report


def run_tenant_portability_portfolio_audit(
    *,
    config_root: str | Path = "configs/dynamic_platform",
) -> TenantPortabilityPortfolioReport:
    paths = DynamicPlatformPaths.from_root(config_root)
    tenant_keys = _tenant_keys(paths)
    domain_restrictions = _domain_restrictions(paths)
    source_identifiers = collect_source_contract_identifiers(config_root=config_root, tenant_keys=tenant_keys)
    records: list[TenantPortabilityPortfolioRecord] = []
    for tenant_key in tenant_keys:
        try:
            bundle = load_tenant_bundle(tenant_key, config_root=config_root)
            restricted_terms, restricted_groups = _restrictions_for_domain(
                bundle.domain_pack.domain_pack,
                domain_restrictions,
            )
            report = run_tenant_portability_audit(
                bundle,
                known_tenant_keys=tenant_keys,
                known_tenant_source_identifiers=source_identifiers,
                restricted_identifier_terms=restricted_terms,
                restricted_entity_groups=restricted_groups,
            )
        except (DynamicPlatformLoadError, OSError, ValueError) as exc:
            records.append(TenantPortabilityPortfolioRecord(tenant_key=tenant_key, ok=False, error=str(exc)))
            continue
        records.append(
            TenantPortabilityPortfolioRecord(
                tenant_key=tenant_key,
                ok=report.ok,
                runtime_strategy=bundle.tenant.runtime_strategy,
                domain_pack=bundle.domain_pack.domain_pack,
                report=report.to_dict(),
            )
        )
    summary = {
        "tenant_count": len(records),
        "passed": sum(1 for record in records if record.ok),
        "failed": sum(1 for record in records if not record.ok),
        "tenants": tenant_keys,
    }
    return TenantPortabilityPortfolioReport(
        ok=all(record.ok for record in records),
        config_root=str(paths.root),
        summary=summary,
        records=records,
        notes=[
            "Portfolio portability audit is offline and checks every configured tenant profile.",
            "Tenants marked as protected classic runtime remain isolated from dynamic live routing.",
        ],
    )


def _check_validation(report: TenantPortabilityAuditReport, validation: dict[str, Any]) -> None:
    ok = validation.get("ok") is True
    report.checks["profile_validation_ok"] = ok
    if not ok:
        report.add_error("profile_validation_failed", "Tenant profile validation must pass before portability handoff.")


def _check_runtime_strategy(report: TenantPortabilityAuditReport, bundle: DynamicPlatformBundle) -> None:
    tenant = bundle.tenant
    if tenant.metadata.get("classic_runtime_protected"):
        ok = tenant.runtime_strategy == "classic_protected"
        report.checks["protected_classic_runtime_strategy"] = ok
        if not ok:
            report.add_error(
                "protected_classic_tenant_not_classic_protected",
                "Protected classic tenant must remain classic_protected while dynamic platform is prepared offline.",
                field="runtime_strategy",
                value=tenant.runtime_strategy,
            )
        return
    ok = tenant.runtime_strategy != "classic_protected"
    report.checks["unprotected_tenant_runtime_not_classic_protected"] = ok
    if not ok:
        report.add_error(
            "unprotected_tenant_classic_runtime_strategy",
            "New dynamic tenants should not rely on a protected classic runtime strategy.",
            field="runtime_strategy",
            value=tenant.runtime_strategy,
        )


def _check_cross_tenant_leakage(
    report: TenantPortabilityAuditReport,
    bundle: DynamicPlatformBundle,
    known_tenants: list[str],
) -> None:
    other_tenants = [tenant for tenant in known_tenants if tenant != bundle.tenant.tenant_key]
    records = _identifier_records(bundle)
    leak_count = 0
    for field, value in records:
        normalized = _normalize_identifier(value)
        for other in other_tenants:
            for token in _tenant_tokens(other):
                if token and _contains_token(normalized, token):
                    leak_count += 1
                    report.add_error(
                        "cross_tenant_identifier_leak",
                        "Tenant identifier/source contract references a different tenant key.",
                        field=field,
                        value=value,
                    )
                    break
    report.checks["no_cross_tenant_identifier_leakage"] = leak_count == 0


def _check_restricted_identifier_terms(
    report: TenantPortabilityAuditReport,
    bundle: DynamicPlatformBundle,
    *,
    restricted_terms: set[str],
) -> None:
    if not restricted_terms:
        report.checks["identifiers_have_no_restricted_domain_terms"] = True
        return
    offenders: list[tuple[str, str, str]] = []
    for field, value in _identifier_records(bundle):
        normalized = _normalize_identifier(value)
        for term in restricted_terms:
            if _contains_token(normalized, term):
                offenders.append((field, value, term))
                report.add_error(
                    "restricted_domain_identifier_term",
                    "Tenant identifiers must not depend on a different domain pack's restricted concepts.",
                    field=field,
                    value=value,
                )
                break
    report.checks["identifiers_have_no_restricted_domain_terms"] = not offenders


def _check_entity_groups(
    report: TenantPortabilityAuditReport,
    bundle: DynamicPlatformBundle,
    *,
    restricted_groups: set[str],
) -> None:
    groups = set(bundle.tenant.entities.groups)
    if not restricted_groups:
        report.checks["entity_groups_match_domain_shape"] = True
        return
    forbidden_groups = sorted(groups & restricted_groups)
    report.checks["entity_groups_match_domain_shape"] = not forbidden_groups
    for group in forbidden_groups:
        report.add_error(
            "restricted_domain_entity_group",
            "Tenant should not require another domain pack's restricted entity groups.",
            field="tenant.entities.groups",
            value=group,
        )


def _check_source_paths(
    report: TenantPortabilityAuditReport,
    bundle: DynamicPlatformBundle,
    known_tenants: list[str],
) -> None:
    other_tenants = [tenant for tenant in known_tenants if tenant != bundle.tenant.tenant_key]
    leak_count = 0
    for source in bundle.source_catalog.sources:
        for field_name in ("path", "url", "collection"):
            raw = getattr(source, field_name)
            if not raw:
                continue
            normalized = _normalize_identifier(str(raw))
            for other in other_tenants:
                for token in _tenant_tokens(other):
                    if token and _contains_token(normalized, token):
                        leak_count += 1
                        report.add_error(
                            "source_location_cross_tenant_leak",
                            "Source location must not point at another tenant's path, URL, or collection.",
                            field=f"source.{source.source_id}.{field_name}",
                            value=str(raw),
                        )
                        break
    report.checks["source_locations_do_not_reference_other_tenants"] = leak_count == 0


def _check_cross_tenant_source_contracts(
    report: TenantPortabilityAuditReport,
    bundle: DynamicPlatformBundle,
    known_source_identifiers: dict[str, set[str]],
) -> None:
    other_sources: dict[str, set[str]] = {
        tenant_key: {
            normalized
            for normalized in identifiers
            if normalized and tenant_key != bundle.tenant.tenant_key
        }
        for tenant_key, identifiers in known_source_identifiers.items()
        if tenant_key != bundle.tenant.tenant_key
    }
    if not other_sources:
        report.checks["source_contracts_do_not_reference_other_tenant_sources"] = True
        return

    leak_count = 0
    for source in bundle.source_catalog.sources:
        fields = {
            "source_id": source.source_id,
            "collection": source.collection,
            "path": source.path,
            "url": source.url,
        }
        for field_name, raw in fields.items():
            if not raw:
                continue
            normalized = _normalize_identifier(str(raw))
            for other_tenant, identifiers in other_sources.items():
                if normalized in identifiers:
                    leak_count += 1
                    report.add_error(
                        "source_contract_cross_tenant_reference",
                        "Source contract references another tenant's source id, collection, path, or URL.",
                        field=f"source.{source.source_id}.{field_name}",
                        value=str(raw),
                    )
                    break
    report.checks["source_contracts_do_not_reference_other_tenant_sources"] = leak_count == 0


def _identifier_records(bundle: DynamicPlatformBundle) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = [
        ("tenant.tenant_key", bundle.tenant.tenant_key),
        ("tenant.domain_pack", bundle.tenant.domain_pack),
        ("tenant.agent_pack", bundle.tenant.agent_pack),
        ("tenant.source_catalog", bundle.tenant.source_catalog),
        ("domain_pack.domain_pack", bundle.domain_pack.domain_pack),
        ("agent_pack.agent_pack", bundle.agent_pack.agent_pack),
        ("source_catalog.source_catalog", bundle.source_catalog.source_catalog),
    ]
    for group, entities in bundle.tenant.entities.groups.items():
        records.append(("tenant.entities.group", group))
        for entity in entities:
            for key in ("id", "entity_id", "key"):
                value = entity.get(key)
                if isinstance(value, str):
                    records.append((f"tenant.entities.{group}.{key}", value))
    for capability in bundle.domain_pack.capabilities:
        records.append(("domain_pack.capability_id", capability.capability_id))
        if capability.core_capability:
            records.append(("domain_pack.core_capability", capability.core_capability))
    for agent in bundle.agent_pack.agents:
        records.append(("agent_pack.agent_id", agent.agent_id))
        records.extend(("agent_pack.agent_capability", capability) for capability in agent.capabilities)
        records.extend(("agent_pack.source_family", family) for family in agent.source_families)
        records.extend(("agent_pack.final_owner_for", item) for item in agent.final_owner_for)
        for specialist in agent.specialists:
            records.append(("agent_pack.specialist_id", specialist.specialist_id))
            records.extend(("agent_pack.specialist_capability", capability) for capability in specialist.capabilities)
    for source in bundle.source_catalog.sources:
        records.append(("source.source_id", source.source_id))
        records.append(("source.domain", source.domain))
        records.append(("source.owner_agent", source.owner_agent))
        records.append(("source.source_family", source.source_family))
        records.extend(("source.capability", capability) for capability in source.capabilities)
        if source.collection:
            records.append(("source.collection", source.collection))
    return records


def _tenant_keys(paths: DynamicPlatformPaths) -> list[str]:
    if not paths.tenants_dir.exists():
        return []
    return sorted(path.stem for path in paths.tenants_dir.glob("*.yaml"))


def collect_source_contract_identifiers(
    *,
    config_root: str | Path,
    tenant_keys: list[str] | None = None,
) -> dict[str, set[str]]:
    paths = DynamicPlatformPaths.from_root(config_root)
    keys = tenant_keys or _tenant_keys(paths)
    identifiers: dict[str, set[str]] = {}
    for tenant_key in keys:
        try:
            bundle = load_tenant_bundle(tenant_key, config_root=config_root)
        except (DynamicPlatformLoadError, OSError, ValueError):
            continue
        identifiers[tenant_key] = _source_contract_identifiers(bundle)
    return identifiers


def _source_contract_identifiers(bundle: DynamicPlatformBundle) -> set[str]:
    identifiers: set[str] = set()
    for source in bundle.source_catalog.sources:
        for value in (source.source_id, source.collection, source.path, source.url):
            if value:
                identifiers.add(_normalize_identifier(str(value)))
    return identifiers


def collect_portability_restrictions(
    *,
    config_root: str | Path,
    current_domain_pack: str,
) -> tuple[set[str], set[str]]:
    paths = DynamicPlatformPaths.from_root(config_root)
    return _restrictions_for_domain(current_domain_pack, _domain_restrictions(paths))


def _domain_restrictions(paths: DynamicPlatformPaths) -> dict[str, tuple[set[str], set[str]]]:
    restrictions: dict[str, tuple[set[str], set[str]]] = {}
    if not paths.domain_packs_dir.exists():
        return restrictions
    for path in sorted(paths.domain_packs_dir.glob("*.yaml")):
        domain_pack = load_yaml_model(path, DomainPack)
        portability = (domain_pack.metadata or {}).get("portability") or {}
        terms = {
            _normalize_identifier(str(item))
            for item in portability.get("domain_specific_identifier_terms") or []
            if str(item).strip()
        }
        groups = {
            _normalize_identifier(str(item))
            for item in portability.get("domain_specific_entity_groups") or []
            if str(item).strip()
        }
        restrictions[domain_pack.domain_pack] = (terms, groups)
    return restrictions


def _restrictions_for_domain(
    current_domain_pack: str,
    domain_restrictions: dict[str, tuple[set[str], set[str]]],
) -> tuple[set[str], set[str]]:
    restricted_terms: set[str] = set()
    restricted_groups: set[str] = set()
    for domain_pack, (terms, groups) in domain_restrictions.items():
        if domain_pack == current_domain_pack:
            continue
        restricted_terms.update(terms)
        restricted_groups.update(groups)
    return restricted_terms, restricted_groups


def _tenant_tokens(tenant_key: str) -> list[str]:
    return [token for token in _normalize_identifier(tenant_key).split("_") if token and token not in {"demo"}]


def _normalize_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _contains_token(normalized: str, token: str) -> bool:
    return token in normalized.split("_")
