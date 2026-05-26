"""Offline rehearsal for creating a brand-new dynamic tenant.

The rehearsal writes only under a tmp output directory. It proves that a new
institution can be assembled from an existing domain pack and agent pack,
validated, packaged, and audited without touching the classic runtime or live
dynamic config.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from src.dynamic_platform.loader import DynamicPlatformLoadError, DynamicPlatformPaths, load_tenant_bundle, load_yaml_model
from src.dynamic_platform.models import (
    AgentDefinition,
    AgentPack,
    CapabilityDefinition,
    DomainPack,
    EntityScope,
    SourceCatalog,
    SourceCatalogEntry,
    TenantProfile,
)
from src.dynamic_platform.package_audit import run_tenant_package_portfolio_audit
from src.dynamic_platform.portability_audit import collect_portability_restrictions, run_tenant_portability_audit
from src.dynamic_platform.source_audit import audit_source_adapters
from src.dynamic_platform.tenant_package import write_tenant_package
from src.dynamic_platform.validator import validate_bundle


@dataclass(frozen=True)
class TenantCreationRehearsalIssue:
    severity: str
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass
class TenantCreationRehearsalReport:
    tenant_key: str
    ok: bool = True
    output_dir: str = ""
    rehearsal_config_root: str = ""
    package_root: str = ""
    package_dir: str = ""
    checks: dict[str, bool] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    validation: dict[str, Any] | None = None
    source_audit: dict[str, Any] | None = None
    portability_audit: dict[str, Any] | None = None
    package_audit: dict[str, Any] | None = None
    errors: list[TenantCreationRehearsalIssue] = field(default_factory=list)
    warnings: list[TenantCreationRehearsalIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_error(self, code: str, message: str, *, path: str | None = None) -> None:
        self.errors.append(TenantCreationRehearsalIssue("error", code, message, path))
        self.ok = False

    def add_warning(self, code: str, message: str, *, path: str | None = None) -> None:
        self.warnings.append(TenantCreationRehearsalIssue("warning", code, message, path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "output_dir": self.output_dir,
            "rehearsal_config_root": self.rehearsal_config_root,
            "package_root": self.package_root,
            "package_dir": self.package_dir,
            "checks": self.checks,
            "summary": self.summary,
            "artifacts": self.artifacts,
            "validation": self.validation,
            "source_audit": self.source_audit,
            "portability_audit": self.portability_audit,
            "package_audit": self.package_audit,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
        }


def run_tenant_creation_rehearsal(
    *,
    tenant_key: str,
    display_name: str,
    bot_name: str,
    domain_pack: str,
    agent_pack: str,
    config_root: str | Path = "configs/dynamic_platform",
    output_dir: str | Path | None = None,
    force: bool = False,
) -> TenantCreationRehearsalReport:
    live_paths = DynamicPlatformPaths.from_root(config_root)
    try:
        source_domain = load_yaml_model(live_paths.domain_pack_path(domain_pack), DomainPack)
        source_agents = load_yaml_model(live_paths.agent_pack_path(agent_pack), AgentPack)
    except DynamicPlatformLoadError as exc:
        report = _new_report(tenant_key)
        _prepare_output_guards(report, tenant_key=tenant_key, config_root=config_root, output_dir=output_dir)
        report.add_error("rehearsal_input_load_failed", str(exc))
        return report

    if source_agents.domain_pack != source_domain.domain_pack:
        report = _new_report(tenant_key)
        _prepare_output_guards(report, tenant_key=tenant_key, config_root=config_root, output_dir=output_dir)
        report.checks["domain_agent_pack_match"] = False
        report.add_error(
            "rehearsal_domain_agent_pack_mismatch",
            f"Agent pack {agent_pack} targets {source_agents.domain_pack}, not {domain_pack}.",
        )
        return report
    return _run_rehearsal_with_models(
        tenant_key=tenant_key,
        display_name=display_name,
        bot_name=bot_name,
        domain_pack_model=source_domain,
        agent_pack_model=source_agents,
        config_root=config_root,
        output_dir=output_dir,
        force=force,
        copy_pack_sources=True,
    )


def run_draft_pack_creation_rehearsal(
    *,
    tenant_key: str,
    display_name: str,
    bot_name: str,
    domain_pack: str,
    domain_display_name: str,
    agent_pack: str,
    agent_pack_display_name: str,
    capability_specs: list[str] | None = None,
    agent_specs: list[str] | None = None,
    config_root: str | Path = "configs/dynamic_platform",
    output_dir: str | Path | None = None,
    force: bool = False,
) -> TenantCreationRehearsalReport:
    """Rehearse a tenant plus a brand-new draft domain/agent pack."""

    capability_pairs = [_parse_id_label(value) for value in (capability_specs or [])]
    agent_pairs = [_parse_id_label(value) for value in (agent_specs or [])]
    if not capability_pairs:
        capability_pairs = [
            ("policy_qa", "Policy QA"),
            ("contact_lookup", "Contact Lookup"),
        ]
    if not agent_pairs:
        agent_pairs = [("support", "Support")]
    capability_ids = [capability_id for capability_id, _ in capability_pairs]
    domain_model = DomainPack(
        domain_pack=domain_pack,
        display_name=domain_display_name,
        description="Draft domain pack generated for offline creation rehearsal.",
        capabilities=[
            CapabilityDefinition(
                capability_id=capability_id,
                display_name=label,
                description=f"{label} capability.",
                core_capability=capability_id,
                answer_mode="rag",
            )
            for capability_id, label in capability_pairs
        ],
    )
    agent_model = AgentPack(
        agent_pack=agent_pack,
        display_name=agent_pack_display_name,
        domain_pack=domain_pack,
        agents=[
            AgentDefinition(
                agent_id=agent_id,
                display_name=label,
                role="service_agent",
                capabilities=list(capability_ids),
                source_families=[f"{agent_id}_documents"],
                final_owner_for=[],
                llm_allowed=True,
                deterministic_allowed=True,
            )
            for agent_id, label in agent_pairs
        ],
    )
    return _run_rehearsal_with_models(
        tenant_key=tenant_key,
        display_name=display_name,
        bot_name=bot_name,
        domain_pack_model=domain_model,
        agent_pack_model=agent_model,
        config_root=config_root,
        output_dir=output_dir,
        force=force,
        copy_pack_sources=False,
    )


def _run_rehearsal_with_models(
    *,
    tenant_key: str,
    display_name: str,
    bot_name: str,
    domain_pack_model: DomainPack,
    agent_pack_model: AgentPack,
    config_root: str | Path,
    output_dir: str | Path | None,
    force: bool,
    copy_pack_sources: bool,
) -> TenantCreationRehearsalReport:
    report = _new_report(tenant_key)
    live_paths = DynamicPlatformPaths.from_root(config_root)
    output_path = _prepare_output_guards(
        report,
        tenant_key=tenant_key,
        config_root=config_root,
        output_dir=output_dir,
    )
    if not report.ok:
        return report
    report.checks["domain_agent_pack_match"] = agent_pack_model.domain_pack == domain_pack_model.domain_pack
    if not report.checks["domain_agent_pack_match"]:
        report.add_error(
            "rehearsal_domain_agent_pack_mismatch",
            (
                f"Agent pack {agent_pack_model.agent_pack} targets {agent_pack_model.domain_pack}, "
                f"not {domain_pack_model.domain_pack}."
            ),
        )
        return report

    rehearsal_config_root = output_path / "config"
    package_root = output_path / "packages"
    package_dir = package_root / tenant_key
    report.rehearsal_config_root = str(rehearsal_config_root)
    report.package_root = str(package_root)
    report.package_dir = str(package_dir)

    if output_path.exists() and not force and any(output_path.iterdir()):
        report.add_error(
            "rehearsal_output_exists",
            "Rehearsal output already exists. Use --force to refresh the tmp rehearsal artifacts.",
            path=str(output_path),
        )
        return report

    try:
        _prepare_rehearsal_config(
            tenant_key=tenant_key,
            display_name=display_name,
            bot_name=bot_name,
            domain_pack_model=domain_pack_model,
            agent_pack_model=agent_pack_model,
            live_paths=live_paths,
            rehearsal_config_root=rehearsal_config_root,
            copy_pack_sources=copy_pack_sources,
        )
        report.checks["rehearsal_config_written"] = True
    except OSError as exc:
        report.checks["rehearsal_config_written"] = False
        report.add_error("rehearsal_config_write_failed", str(exc), path=str(rehearsal_config_root))
        return report

    try:
        bundle = load_tenant_bundle(tenant_key, config_root=rehearsal_config_root)
    except DynamicPlatformLoadError as exc:
        report.add_error("rehearsal_bundle_load_failed", str(exc), path=str(rehearsal_config_root))
        return report

    validation = validate_bundle(bundle)
    source_audit = audit_source_adapters(bundle)
    restricted_terms, restricted_groups = collect_portability_restrictions(
        config_root=rehearsal_config_root,
        current_domain_pack=bundle.domain_pack.domain_pack,
    )
    portability = run_tenant_portability_audit(
        bundle,
        known_tenant_keys=[tenant_key],
        restricted_identifier_terms=restricted_terms,
        restricted_entity_groups=restricted_groups,
    )
    report.validation = validation.to_dict()
    report.source_audit = source_audit.to_dict()
    report.portability_audit = portability.to_dict()
    report.checks["profile_validation_ok"] = validation.ok
    report.checks["source_audit_ok"] = source_audit.ok
    report.checks["portability_audit_ok"] = portability.ok
    if not validation.ok:
        report.add_error("rehearsal_validation_failed", "Generated tenant profile did not validate.")
    if not source_audit.ok:
        report.add_error("rehearsal_source_audit_failed", "Generated source catalog did not pass source audit.")
    if not portability.ok:
        report.add_error("rehearsal_portability_failed", "Generated tenant did not pass portability audit.")
    if not report.ok:
        return report

    try:
        package_result = write_tenant_package(
            bundle,
            config_root=rehearsal_config_root,
            output_dir=package_dir,
            require_quality_gates=False,
            force=True,
        )
    except (OSError, FileExistsError, DynamicPlatformLoadError) as exc:
        report.checks["package_written"] = False
        report.add_error("rehearsal_package_write_failed", str(exc), path=str(package_dir))
        return report
    report.checks["package_written"] = True
    report.artifacts = [str(path) for path in _artifact_paths(rehearsal_config_root, package_dir)]
    if package_result.files:
        report.artifacts.extend(package_result.files)

    package_audit = run_tenant_package_portfolio_audit(
        config_root=rehearsal_config_root,
        package_root=package_root,
        require_quality_gates=False,
    )
    report.package_audit = package_audit.to_dict()
    report.checks["package_audit_ok"] = package_audit.ok
    report.checks["package_compose_isolation_ok"] = all(
        ((record.safety_audit or {}).get("checks") or {}).get("package_compose_isolation_ok") is True
        for record in package_audit.records
    )
    if not package_audit.ok:
        report.add_error("rehearsal_package_audit_failed", "Generated tenant package did not pass package audit.")

    report.summary = {
        "domain_pack": bundle.domain_pack.domain_pack,
        "agent_pack": bundle.agent_pack.agent_pack,
        "source_catalog": bundle.source_catalog.source_catalog,
        "runtime_strategy": bundle.tenant.runtime_strategy,
        "capability_count": len(bundle.domain_pack.capabilities),
        "agent_count": len(bundle.agent_pack.agents),
        "source_count": len(bundle.source_catalog.sources),
        "enabled_source_count": sum(1 for source in bundle.source_catalog.sources if source.enabled),
        "capabilities_without_agent": validation.summary.get("capabilities_without_agent", []),
        "capabilities_without_enabled_source": validation.summary.get("capabilities_without_enabled_source", []),
    }
    return report


def _new_report(tenant_key: str) -> TenantCreationRehearsalReport:
    return TenantCreationRehearsalReport(
        tenant_key=tenant_key,
        notes=[
            "Creation rehearsal is offline; it does not start Docker, Slack, API, router, agents, RAG, DB, or LLM.",
            "Generated files are rehearsal artifacts under tmp and are not imported by the classic runtime.",
            "Passing this rehearsal does not authorize dynamic live runtime.",
        ],
    )


def _prepare_output_guards(
    report: TenantCreationRehearsalReport,
    *,
    tenant_key: str,
    config_root: str | Path,
    output_dir: str | Path | None,
) -> Path:
    live_paths = DynamicPlatformPaths.from_root(config_root)
    output_path = Path(output_dir) if output_dir else Path("tmp/dynamic_platform_rehearsals") / tenant_key
    output_path = output_path.resolve()
    tmp_root = Path("tmp").resolve()
    report.output_dir = str(output_path)

    report.checks["output_under_tmp"] = _is_relative_to(output_path, tmp_root)
    if not report.checks["output_under_tmp"]:
        report.add_error(
            "rehearsal_output_outside_tmp",
            "Rehearsal output must stay under tmp so it cannot overwrite live tenant config.",
            path=str(output_path),
        )
        return output_path

    live_tenant_path = live_paths.tenant_path(tenant_key)
    live_source_path = live_paths.source_catalog_path(f"{tenant_key}_sources")
    report.checks["live_tenant_profile_absent"] = not live_tenant_path.exists()
    report.checks["live_source_catalog_absent"] = not live_source_path.exists()
    if live_tenant_path.exists():
        report.add_error(
            "tenant_already_exists_in_live_config",
            "Creation rehearsal must use a tenant key that is not already present in live dynamic config.",
            path=str(live_tenant_path),
        )
    if live_source_path.exists():
        report.add_error(
            "source_catalog_already_exists_in_live_config",
            "Creation rehearsal must not collide with an existing live source catalog.",
            path=str(live_source_path),
        )
    return output_path


def _prepare_rehearsal_config(
    *,
    tenant_key: str,
    display_name: str,
    bot_name: str,
    domain_pack_model: DomainPack,
    agent_pack_model: AgentPack,
    live_paths: DynamicPlatformPaths,
    rehearsal_config_root: Path,
    copy_pack_sources: bool,
) -> None:
    paths = DynamicPlatformPaths.from_root(rehearsal_config_root)
    paths.tenants_dir.mkdir(parents=True, exist_ok=True)
    paths.domain_packs_dir.mkdir(parents=True, exist_ok=True)
    paths.agent_packs_dir.mkdir(parents=True, exist_ok=True)
    paths.source_catalogs_dir.mkdir(parents=True, exist_ok=True)

    if copy_pack_sources:
        shutil.copy2(
            live_paths.domain_pack_path(domain_pack_model.domain_pack),
            paths.domain_pack_path(domain_pack_model.domain_pack),
        )
        shutil.copy2(
            live_paths.agent_pack_path(agent_pack_model.agent_pack),
            paths.agent_pack_path(agent_pack_model.agent_pack),
        )
    else:
        paths.domain_pack_path(domain_pack_model.domain_pack).write_text(
            yaml.safe_dump(domain_pack_model.model_dump(mode="json", exclude_none=True), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        paths.agent_pack_path(agent_pack_model.agent_pack).write_text(
            yaml.safe_dump(agent_pack_model.model_dump(mode="json", exclude_none=True), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    tenant = TenantProfile(
        tenant_key=tenant_key,
        display_name=display_name,
        bot_name=bot_name,
        runtime_strategy="dynamic_shadow",
        domain_pack=domain_pack_model.domain_pack,
        agent_pack=agent_pack_model.agent_pack,
        source_catalog=f"{tenant_key}_sources",
        replay_suite=f"{tenant_key}_golden",
        entities={
            "groups": {
                "departments": [],
                "teams": [],
                "services": [],
                "products": [],
                "units": [],
            }
        },
        metadata={
            "generated_by": "tenant_creation_rehearsal",
            "classic_runtime_protected": False,
            "rehearsal_only": True,
        },
    )
    source_catalog = SourceCatalog(
        source_catalog=f"{tenant_key}_sources",
        tenant_key=tenant_key,
        sources=_build_placeholder_sources(
            tenant_key=tenant_key,
            domain_pack=domain_pack_model,
            agent_pack=agent_pack_model,
        ),
    )
    paths.tenant_path(tenant_key).write_text(
        yaml.safe_dump(tenant.model_dump(mode="json", exclude_none=True), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    paths.source_catalog_path(source_catalog.source_catalog).write_text(
        yaml.safe_dump(source_catalog.model_dump(mode="json", exclude_none=True), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    rehearsal_input = {
        "tenant_key": tenant_key,
        "display_name": display_name,
        "bot_name": bot_name,
        "domain_pack": domain_pack_model.domain_pack,
        "agent_pack": agent_pack_model.agent_pack,
        "safety_status": "tmp_rehearsal_only",
        "live_runtime_authorized": False,
    }
    (rehearsal_config_root / "creation_rehearsal_input.json").write_text(
        json.dumps(rehearsal_input, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _build_placeholder_sources(
    *,
    tenant_key: str,
    domain_pack: DomainPack,
    agent_pack: AgentPack,
) -> list[SourceCatalogEntry]:
    capability_ids = {capability.capability_id for capability in domain_pack.capabilities}
    sources: list[SourceCatalogEntry] = []
    used_source_ids: set[str] = set()
    for agent in agent_pack.agents:
        capabilities = [capability for capability in agent.capabilities if capability in capability_ids]
        if not capabilities:
            continue
        families = agent.source_families or [f"{agent.agent_id}_documents"]
        for family in families:
            adapter, authority = _source_contract_for_family(family)
            source_id = _unique_id(_sanitize_id(f"{tenant_key}_{family}"), used_source_ids)
            sources.append(
                SourceCatalogEntry(
                    source_id=source_id,
                    adapter=adapter,
                    domain=domain_pack.domain_pack,
                    owner_agent=agent.agent_id,
                    source_family=family,
                    capabilities=capabilities,
                    entity_scope=EntityScope(type="global"),
                    authority_level=authority,
                    collection=f"{tenant_key}_{family}",
                    enabled=True,
                    metadata={
                        "generated_by": "tenant_creation_rehearsal",
                        "placeholder": "true",
                        "replace_before_pilot": "true",
                    },
                )
            )
    return sources


def _parse_id_label(raw: str) -> tuple[str, str]:
    if ":" in raw:
        item_id, label = raw.split(":", 1)
        item_id = item_id.strip()
        label = label.strip()
    else:
        item_id = raw.strip()
        label = item_id.replace("_", " ").replace(".", " ").title()
    return item_id, label or item_id


def _source_contract_for_family(source_family: str) -> tuple[str, str]:
    family = source_family.lower()
    if "announcement" in family or "notice" in family:
        return "announcement_page", "official_announcement"
    if "contact" in family or "directory" in family:
        return "structured_csv", "official_structured"
    if "calendar" in family or "schedule" in family:
        return "calendar_pdf", "official_structured"
    if "table" in family or "structured" in family or "catalog" in family:
        return "structured_csv", "official_structured"
    if "api" in family:
        return "api_endpoint", "official_structured"
    if "web" in family or "knowledge" in family:
        return "web_page", "department_document"
    return "pdf_document", "official_policy"


def _sanitize_id(value: str) -> str:
    normalized = value.lower().replace("-", "_").replace(".", "_")
    normalized = re.sub(r"[^a-z0-9_]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    if not normalized or not normalized[0].isalpha():
        normalized = f"tenant_{normalized}"
    return normalized


def _unique_id(base: str, used: set[str]) -> str:
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def _artifact_paths(config_root: Path, package_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for root in (config_root, package_dir):
        if not root.exists():
            continue
        paths.extend(sorted(path for path in root.rglob("*") if path.is_file()))
    return paths


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
