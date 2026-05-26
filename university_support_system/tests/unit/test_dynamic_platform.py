from __future__ import annotations

import json
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from scripts.tenant import main as tenant_cli_main
from src.dynamic_platform.activation_checklist import run_dynamic_activation_checklist
from src.dynamic_platform.bootstrap_plan import build_tenant_bootstrap_plan
from src.dynamic_platform.classic_compare import compare_bundle_to_classic
from src.dynamic_platform.completion_report import run_dynamic_platform_completion_report
from src.dynamic_platform.compose_config_audit import run_compose_config_audit
from src.dynamic_platform.api import create_dynamic_app
from src.dynamic_platform.contract_matrix import build_capability_contract_matrix
from src.dynamic_platform.decision_shadow import (
    ShadowDecisionCase,
    compare_shadow_decisions,
    default_shadow_fixture_path,
    load_shadow_decision_cases,
)
from src.dynamic_platform.compose_isolation_audit import run_compose_isolation_audit
from src.dynamic_platform.compose_template import build_compose_launch_template_files
from src.dynamic_platform.docker_plan import build_docker_deployment_plan
from src.dynamic_platform.genericity_audit import run_genericity_audit
from src.dynamic_platform.handoff_readiness import run_handoff_readiness
from src.dynamic_platform.loader import load_tenant_bundle
from src.dynamic_platform.model_runtime_contract import build_model_runtime_contract
from src.dynamic_platform.models import CapabilityDefinition
from src.dynamic_platform.onboarding import build_onboarding_preview
from src.dynamic_platform.package_audit import run_tenant_package_portfolio_audit
from src.dynamic_platform.pilot_readiness import run_tenant_pilot_readiness
from src.dynamic_platform.pilot_secret_scaffold import write_tenant_pilot_secret_scaffold
from src.dynamic_platform.preflight import run_dynamic_platform_preflight
from src.dynamic_platform.portfolio_audit import run_tenant_portfolio_audit
from src.dynamic_platform.portability_audit import run_tenant_portability_audit, run_tenant_portability_portfolio_audit
from src.dynamic_platform.quality_gates import run_quality_gates
from src.dynamic_platform.registry_catalog import build_registry_catalog
from src.dynamic_platform.readiness import build_tenant_readiness_report
from src.dynamic_platform.retrieval_contract import build_retrieval_contract
from src.dynamic_platform.runtime_adapter_contract import build_runtime_adapter_contract
from src.dynamic_platform.runtime_adapter_draft import DynamicRuntimeAdapterDraft, DynamicRuntimeRequest
from src.dynamic_platform.runtime_adapter_implementation_plan import build_runtime_adapter_implementation_plan
from src.dynamic_platform.runtime_live_adapter import DynamicRuntimeLiveAdapter
from src.dynamic_platform.runtime_activation_guard import RuntimeActivationInput, evaluate_runtime_activation
from src.dynamic_platform.runtime import DynamicRuntimeOrchestrator, DynamicRuntimeQuery
from src.dynamic_platform.runtime_env_check import check_runtime_env, parse_env_file
from src.dynamic_platform.runtime_isolation_contract import build_runtime_isolation_contract
from src.dynamic_platform.runtime_namespace import RuntimeNamespaceBuilder, build_runtime_namespace_preview
from src.dynamic_platform.runtime_plan import build_runtime_launch_plan
from src.dynamic_platform.runtime_query_smoke import run_dynamic_query_smoke
from src.dynamic_platform.runtime_smoke_readiness import run_runtime_smoke_readiness
from src.dynamic_platform.runtime_container_audit import run_runtime_container_audit
from src.dynamic_platform.safety_audit import run_safety_audit
from src.dynamic_platform.secret_readiness import check_tenant_secret_readiness
from src.dynamic_platform.secrets_contract import build_tenant_secrets_contract
from src.dynamic_platform.shadow_runtime import build_shadow_runtime_decision
from src.dynamic_platform.shadow_runtime_replay import run_shadow_runtime_replay
from src.dynamic_platform.source_audit import audit_source_adapters
from src.dynamic_platform.source_ingestion_plan import build_source_ingestion_plan
from src.dynamic_platform.tenant_rehearsal import run_draft_pack_creation_rehearsal, run_tenant_creation_rehearsal
from src.dynamic_platform.tenant_package import build_tenant_package_files, write_tenant_package
from src.dynamic_platform.validator import build_execution_plan, validate_bundle

CONFIG_ROOT = Path("configs/dynamic_platform")
CLASSIC_RUNTIME_DIRS = (
    Path("src/orchestrators"),
    Path("src/routing"),
    Path("src/agents"),
    Path("src/slack"),
    Path("src/api"),
)


def _write_acme_compose_config_package() -> Path:
    package_dir = Path("tmp/tenant_packages/acme_demo")
    write_tenant_package(
        load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT),
        config_root=CONFIG_ROOT,
        output_dir=package_dir,
        force=True,
    )
    return package_dir


def test_omu_dynamic_profile_validates_without_changing_classic_runtime():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    report = validate_bundle(bundle)

    assert report.ok is True
    assert bundle.tenant.runtime_strategy == "classic_protected"
    assert bundle.tenant.metadata["classic_runtime_protected"] is True
    assert report.summary["agent_count"] == 5
    assert "student_affairs" in report.summary["agents"]
    assert "graduation_akts" in report.summary["capabilities"]


def test_non_university_demo_tenant_does_not_require_program_entities():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    report = validate_bundle(bundle)

    assert report.ok is True
    assert bundle.tenant.domain_pack == "corporate_support"
    assert "programs" not in bundle.tenant.entities.groups
    assert "hr_policy" in report.summary["agents"]
    assert "leave_policy" in report.summary["capabilities"]


def test_public_service_demo_tenant_uses_public_service_entities():
    bundle = load_tenant_bundle("city_demo", config_root=CONFIG_ROOT)
    report = validate_bundle(bundle)

    assert report.ok is True
    assert bundle.tenant.domain_pack == "public_service_support"
    assert "programs" not in bundle.tenant.entities.groups
    assert {"units", "services", "districts", "desks"} <= set(bundle.tenant.entities.groups)
    assert "citizen_services" in report.summary["agents"]
    assert "service_application" in report.summary["capabilities"]
    assert report.summary["capabilities_without_agent"] == []
    assert report.summary["capabilities_without_enabled_source"] == []


def test_portability_audit_accepts_non_school_demo_tenants():
    known_tenants = ["omu", "acme_demo", "city_demo"]
    acme = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    city = load_tenant_bundle("city_demo", config_root=CONFIG_ROOT)
    omu = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    source_identifiers = {
        "omu": {
            source.collection
            for source in omu.source_catalog.sources
            if source.collection
        }
    }

    acme_report = run_tenant_portability_audit(
        acme,
        known_tenant_keys=known_tenants,
        known_tenant_source_identifiers=source_identifiers,
    )
    city_report = run_tenant_portability_audit(
        city,
        known_tenant_keys=known_tenants,
        known_tenant_source_identifiers=source_identifiers,
    )

    assert acme_report.ok is True
    assert city_report.ok is True
    assert acme_report.to_dict()["checks"]["identifiers_have_no_restricted_domain_terms"] is True
    assert city_report.to_dict()["checks"]["source_locations_do_not_reference_other_tenants"] is True
    assert acme_report.to_dict()["checks"]["source_contracts_do_not_reference_other_tenant_sources"] is True


def test_portability_audit_rejects_omu_identifier_leak_in_non_education_tenant():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.source_catalog.sources[0].source_id = "omu_hr_documents"

    report = run_tenant_portability_audit(bundle, known_tenant_keys=["omu", "acme_demo", "city_demo"])
    payload = report.to_dict()

    assert report.ok is False
    assert payload["checks"]["no_cross_tenant_identifier_leakage"] is False
    assert any(error["code"] == "cross_tenant_identifier_leak" for error in payload["errors"])


def test_portability_audit_rejects_cross_tenant_source_collection_reference():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.source_catalog.sources[0].collection = "student_affairs_docs"

    report = run_tenant_portability_audit(
        bundle,
        known_tenant_keys=["omu", "acme_demo", "city_demo"],
        known_tenant_source_identifiers={"omu": {"student_affairs_docs"}},
    )
    payload = report.to_dict()

    assert report.ok is False
    assert payload["checks"]["source_contracts_do_not_reference_other_tenant_sources"] is False
    assert any(error["code"] == "source_contract_cross_tenant_reference" for error in payload["errors"])


def test_portability_portfolio_audit_checks_all_configured_tenants():
    report = run_tenant_portability_portfolio_audit(config_root=CONFIG_ROOT)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["summary"]["tenant_count"] == 3
    assert payload["summary"]["failed"] == 0


def test_tenant_cli_portability_audit_reports_tenant_status(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "portability-audit", "--tenant", "acme_demo"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Portability audit: OK" in captured.out
    assert "no_cross_tenant_identifier_leakage: yes" in captured.out


def test_tenant_cli_portability_audit_all_reports_portfolio_status(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "portability-audit", "--all"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tenant portability portfolio audit: OK" in captured.out
    assert "Tenants: 3/3 passed" in captured.out


def test_dynamic_validation_catches_unknown_source_capability():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.source_catalog.sources[0].capabilities.append("missing_capability")

    report = validate_bundle(bundle)

    assert report.ok is False
    assert any(issue.code == "source_capability_unknown" for issue in report.errors)


def test_dynamic_validation_warns_when_domain_capability_has_no_agent_or_source():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.domain_pack.capabilities.append(
        CapabilityDefinition(
            capability_id="orphan_capability",
            display_name="Orphan Capability",
            description="Capability intentionally not represented by agents or sources.",
        )
    )

    report = validate_bundle(bundle)

    assert report.ok is True
    assert "orphan_capability" in report.summary["capabilities_without_agent"]
    assert "orphan_capability" in report.summary["capabilities_without_enabled_source"]
    assert any(issue.code == "capability_without_agent" for issue in report.warnings)
    assert any(issue.code == "capability_without_enabled_source" for issue in report.warnings)


def test_topology_plan_maps_capabilities_to_agents_and_sources():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    plan = build_execution_plan(bundle)

    assert plan["runtime_strategy"] == "classic_protected"
    assert "student_affairs" in plan["capability_to_agents"]["graduation_akts"]
    assert "omu_uploaded_transcripts" in plan["capability_to_sources"]["transcript_analysis"]
    assert "academic_programs" in plan["capability_to_agents"]["course_schedule"]


def test_capability_contract_matrix_explains_agents_sources_and_final_owners():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    matrix = build_capability_contract_matrix(bundle)
    payload = matrix.to_dict()
    rows = {row["capability_id"]: row for row in payload["rows"]}

    assert matrix.ok is True
    assert rows["graduation_akts"]["agents"] == ["student_affairs"]
    assert "omu_student_policy_documents" in rows["graduation_akts"]["source_ids"]
    assert rows["graduation_akts"]["final_owner_candidates"] == ["student_affairs"]
    assert rows["course_schedule"]["final_owner_candidates"] == ["academic_programs"]
    assert rows["course_schedule"]["authority_levels"] == ["official_structured"]
    assert rows["tuition_fee"]["final_owner_candidates"] == []
    assert rows["tuition_fee"]["operation_owner_refs"]["finance"] == ["exact_fee_lookup", "payment_deadline"]
    assert payload["summary"]["operation_owner_ref_count"] > 0


def test_tenant_cli_contract_matrix_reports_profile_contracts(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "contract-matrix", "--tenant", "acme_demo"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Capability contract matrix" in captured.out
    assert "leave_policy" in captured.out
    assert "hr_policy" in captured.out
    assert "acme_hr_documents" in captured.out
    assert "operation_owner_refs" in captured.out


def test_omu_dynamic_profile_matches_classic_topology_shape():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    report = compare_bundle_to_classic(bundle)

    assert report.ok is True
    payload = report.to_dict()
    assert payload["classic"]["department_agents"] == payload["dynamic"]["department_agents"]
    assert payload["classic"]["capability_agents"] == payload["dynamic"]["capability_agents"]
    assert payload["classic"]["specialist_agents"] == payload["dynamic"]["specialist_agents"]


def test_tenant_cli_validate_and_plan_do_not_require_runtime_imports(capsys):
    validate_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "validate", "--tenant", "omu"])
    plan_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "plan", "--tenant", "acme_demo"])

    captured = capsys.readouterr()
    assert validate_code == 0
    assert plan_code == 0
    assert "Tenant: omu" in captured.out
    assert "hr_policy" in captured.out


def test_dynamic_registry_catalog_lists_domain_agent_source_and_tenant_inventory():
    report = build_registry_catalog(config_root=CONFIG_ROOT)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["summary"]["domain_pack_count"] == 3
    assert payload["summary"]["agent_pack_count"] == 3
    assert payload["summary"]["source_catalog_count"] == 3
    assert payload["summary"]["tenant_count"] == 3
    assert payload["summary"]["runtime_strategy_counts"] == {"classic_protected": 1, "dynamic_shadow": 2}
    assert {domain["domain_pack"] for domain in payload["domain_packs"]} == {
        "education_university",
        "corporate_support",
        "public_service_support",
    }
    assert {tenant["tenant_key"] for tenant in payload["tenants"]} == {"omu", "acme_demo", "city_demo"}
    assert all(tenant["validation_ok"] for tenant in payload["tenants"])


def test_tenant_cli_registry_reports_config_inventory(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "registry"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dynamic platform registry: OK" in captured.out
    assert "public_service_support" in captured.out
    assert "city_demo" in captured.out
    assert "domains=3" in captured.out


def test_tenant_cli_compare_classic_for_omu(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "compare-classic", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Classic topology compare" in captured.out
    assert "Status: OK" in captured.out


def test_tenant_cli_export_includes_runtime_and_source_contracts(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "export", "--tenant", "acme_demo"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["tenant"]["tenant_key"] == "acme_demo"
    assert payload["contract_matrix"]["summary"]["capability_count"] == 6
    assert payload["source_audit"]["ok"] is True
    assert payload["source_ingestion_plan"]["summary"]["source_count"] == 5
    assert payload["runtime_adapter_contract"]["adapter_status"] == "not_wired"
    assert payload["runtime_adapter_contract"]["dynamic_live_binding_allowed"] is False


def test_tenant_cli_scaffold_dry_run_creates_full_skeleton_preview(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "scaffold",
            "--tenant",
            "gamma_demo",
            "--display-name",
            "Gamma Kurum",
            "--bot-name",
            "Gamma Destek Botu",
            "--domain",
            "corporate_support",
            "--agent-pack",
            "corporate_hr_it_support",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Gamma Kurum" in captured.out
    assert "gamma_demo_sources" in captured.out
    assert "gamma_demo_golden.json" in captured.out
    assert "gamma_demo_shadow_decisions.json" in captured.out
    assert "gamma_demo_runbook.md" in captured.out
    assert "quality-gates --tenant gamma_demo" in captured.out
    assert "source-ingestion-plan --tenant gamma_demo" in captured.out
    assert "genericity-audit" in captured.out
    assert "runtime-adapter-contract --tenant gamma_demo" in captured.out
    assert "audit-all" in captured.out
    assert "runtime-plan --tenant gamma_demo" in captured.out
    assert "scripts.tenant scaffold" in captured.out


def test_tenant_creation_rehearsal_generates_tmp_package_without_live_config_writes():
    tenant_key = "zeta_rehearsal"
    output_dir = Path("tmp/dynamic_platform_creation_rehearsal_test")

    report = run_tenant_creation_rehearsal(
        tenant_key=tenant_key,
        display_name="Zeta Kurum",
        bot_name="Zeta Destek Botu",
        domain_pack="corporate_support",
        agent_pack="corporate_hr_it_support",
        config_root=CONFIG_ROOT,
        output_dir=output_dir,
        force=True,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["checks"]["output_under_tmp"] is True
    assert payload["checks"]["live_tenant_profile_absent"] is True
    assert payload["checks"]["live_source_catalog_absent"] is True
    assert payload["checks"]["profile_validation_ok"] is True
    assert payload["checks"]["source_audit_ok"] is True
    assert payload["checks"]["portability_audit_ok"] is True
    assert payload["checks"]["package_audit_ok"] is True
    assert payload["checks"]["package_compose_isolation_ok"] is True
    assert payload["summary"]["enabled_source_count"] > 0
    assert (output_dir / "config" / "tenants" / f"{tenant_key}.yaml").exists()
    assert (output_dir / "packages" / tenant_key / "tenant.env").exists()
    assert not (CONFIG_ROOT / "tenants" / f"{tenant_key}.yaml").exists()
    assert not (CONFIG_ROOT / "source_catalogs" / f"{tenant_key}_sources.yaml").exists()


def test_tenant_cli_creation_rehearsal_reports_end_to_end_status(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "creation-rehearsal",
            "--tenant",
            "eta_rehearsal",
            "--display-name",
            "Eta Kurum",
            "--bot-name",
            "Eta Destek Botu",
            "--domain",
            "corporate_support",
            "--agent-pack",
            "corporate_hr_it_support",
            "--output-dir",
            "tmp/dynamic_platform_creation_rehearsal_cli_test",
            "--force",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Creation rehearsal: OK" in captured.out
    assert "profile_validation_ok: yes" in captured.out
    assert "package_audit_ok: yes" in captured.out
    assert "Package directory:" in captured.out


def test_tenant_creation_rehearsal_rejects_live_tenant_key_collision():
    report = run_tenant_creation_rehearsal(
        tenant_key="acme_demo",
        display_name="Collision",
        bot_name="Collision Bot",
        domain_pack="corporate_support",
        agent_pack="corporate_hr_it_support",
        config_root=CONFIG_ROOT,
        output_dir="tmp/dynamic_platform_creation_rehearsal_collision_test",
        force=True,
    )
    payload = report.to_dict()

    assert report.ok is False
    assert payload["checks"]["live_tenant_profile_absent"] is False
    assert any(error["code"] == "tenant_already_exists_in_live_config" for error in payload["errors"])


def test_draft_pack_creation_rehearsal_builds_new_domain_agents_and_package():
    report = run_draft_pack_creation_rehearsal(
        tenant_key="lambda_rehearsal",
        display_name="Lambda Kurum",
        bot_name="Lambda Destek Botu",
        domain_pack="logistics_support_rehearsal",
        domain_display_name="Logistics Support",
        agent_pack="logistics_ops_agents_rehearsal",
        agent_pack_display_name="Logistics Ops Agents",
        capability_specs=[
            "shipment_policy:Shipment Policy",
            "warehouse_contact:Warehouse Contact",
        ],
        agent_specs=[
            "operations:Operations",
            "warehouse:Warehouse",
        ],
        config_root=CONFIG_ROOT,
        output_dir="tmp/dynamic_platform_pack_creation_rehearsal_test",
        force=True,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["checks"]["profile_validation_ok"] is True
    assert payload["checks"]["package_audit_ok"] is True
    assert payload["summary"]["domain_pack"] == "logistics_support_rehearsal"
    assert payload["summary"]["agent_pack"] == "logistics_ops_agents_rehearsal"
    assert payload["summary"]["capability_count"] == 2
    assert payload["summary"]["agent_count"] == 2
    assert payload["summary"]["capabilities_without_agent"] == []
    assert payload["summary"]["capabilities_without_enabled_source"] == []
    assert not (CONFIG_ROOT / "domain_packs" / "logistics_support_rehearsal.yaml").exists()
    assert not (CONFIG_ROOT / "agent_packs" / "logistics_ops_agents_rehearsal.yaml").exists()


def test_tenant_cli_pack_creation_rehearsal_reports_tmp_only_package(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "pack-creation-rehearsal",
            "--tenant",
            "mu_rehearsal",
            "--display-name",
            "Mu Kurum",
            "--bot-name",
            "Mu Destek Botu",
            "--domain",
            "operations_support_rehearsal",
            "--domain-display-name",
            "Operations Support",
            "--agent-pack",
            "operations_agents_rehearsal",
            "--agent-pack-display-name",
            "Operations Agents",
            "--capability",
            "policy_lookup:Policy Lookup",
            "--agent",
            "support:Support",
            "--output-dir",
            "tmp/dynamic_platform_pack_creation_rehearsal_cli_test",
            "--force",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Creation rehearsal: OK" in captured.out
    assert "domain=operations_support_rehearsal" in captured.out
    assert "package_audit_ok: yes" in captured.out


def test_tenant_cli_pack_scaffold_dry_run_creates_custom_domain_and_agents(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "pack-scaffold",
            "--domain",
            "municipality_support",
            "--domain-display-name",
            "Municipality Support",
            "--agent-pack",
            "municipality_service_agents",
            "--agent-pack-display-name",
            "Municipality Service Agents",
            "--capability",
            "permit_application:Permit Application",
            "--capability",
            "appointment_schedule:Appointment Schedule",
            "--agent",
            "citizen_services:Citizen Services",
            "--agent",
            "fee_office:Fee Office",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "municipality_support.yaml" in captured.out
    assert "municipality_service_agents.yaml" in captured.out
    assert "permit_application" in captured.out
    assert "citizen_services" in captured.out
    assert "programs" not in captured.out


def test_tenant_cli_source_scaffold_dry_run_adds_valid_source_preview(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "source-scaffold",
            "--tenant",
            "acme_demo",
            "--source-id",
            "acme_benefits_documents",
            "--adapter",
            "pdf_document",
            "--owner-agent",
            "hr_policy",
            "--source-family",
            "hr_documents",
            "--capability",
            "policy_qa",
            "--path",
            "data/acme/benefits.pdf",
            "--metadata",
            "owner=hr",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Would update" in captured.out
    assert "acme_benefits_documents" in captured.out
    assert "authority_level: official_policy" in captured.out
    assert "validation: OK" in captured.out
    assert "source audit: OK" in captured.out
    assert "acme_benefits_documents" not in Path(
        "configs/dynamic_platform/source_catalogs/acme_demo_sources.yaml"
    ).read_text(encoding="utf-8")


def test_tenant_cli_source_scaffold_rejects_owner_capability_mismatch(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "source-scaffold",
            "--tenant",
            "acme_demo",
            "--source-id",
            "acme_bad_it_source",
            "--adapter",
            "web_page",
            "--owner-agent",
            "hr_policy",
            "--source-family",
            "hr_documents",
            "--capability",
            "it_ticket_guidance",
            "--url",
            "https://example.invalid/it",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "source_owner_lacks_capability" in captured.out
    assert "catalog was not written" in captured.err


def test_tenant_cli_entity_scaffold_dry_run_adds_non_school_entity_preview(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "entity-scaffold",
            "--tenant",
            "acme_demo",
            "--group",
            "teams",
            "--entity-id",
            "platform_team",
            "--display-name",
            "Platform Team",
            "--alias",
            "Platform",
            "--alias",
            "Core Engineering",
            "--metadata",
            "cost_center=eng-platform",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Would update" in captured.out
    assert "platform_team" in captured.out
    assert "Core Engineering" in captured.out
    assert "cost_center: eng-platform" in captured.out
    assert "platform_team" not in Path("configs/dynamic_platform/tenants/acme_demo.yaml").read_text(
        encoding="utf-8"
    )


def test_tenant_cli_decision_case_scaffold_dry_run_validates_case(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "decision-case-scaffold",
            "--tenant",
            "acme_demo",
            "--case-id",
            "ACME-CONTACT-DRY-RUN",
            "--query",
            "IT ekibiyle nasil iletisime gecerim?",
            "--expected-capability",
            "department_contact",
            "--expected-agent",
            "it_support",
            "--expected-source-family",
            "contact_directory",
            "--expected-source-owner",
            "hr_policy",
            "--expected-authority-level",
            "official_structured",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Would update" in captured.out
    assert "ACME-CONTACT-DRY-RUN" in captured.out
    assert "Shadow decision compare" in captured.out
    assert "Status: OK" in captured.out
    assert "ACME-CONTACT-DRY-RUN" not in Path(
        "tests/fixtures/dynamic_platform/acme_demo_shadow_decisions.json"
    ).read_text(encoding="utf-8")


def test_tenant_cli_decision_case_scaffold_rejects_unrepresented_contract(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "decision-case-scaffold",
            "--tenant",
            "acme_demo",
            "--case-id",
            "ACME-BAD-DRY-RUN",
            "--query",
            "Izin politikasi nedir?",
            "--expected-capability",
            "leave_policy",
            "--expected-agent",
            "payroll",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "agent_not_represented" in captured.out
    assert "fixture was not written" in captured.err


def test_onboarding_preview_is_tenant_specific_and_offline():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    content = build_onboarding_preview(bundle)

    assert "ACME Ic Destek Botu" in content
    assert "Leave Policy" in content
    assert "IT Support" in content
    assert "Slack'e otomatik mesaj gondermez" in content
    assert "program" not in content.lower()


def test_tenant_cli_onboarding_preview_writes_markdown(capsys):
    output_path = Path("tmp/acme_onboarding_preview_test.md")
    output_path.unlink(missing_ok=True)
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "onboarding-preview",
            "--tenant",
            "acme_demo",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Onboarding preview written" in captured.out
    content = output_path.read_text(encoding="utf-8")
    assert "ACME Ic Destek Botu" in content
    assert "Dynamic runtime aktif edilmeden once" in content


def test_safety_audit_confirms_classic_runtime_isolation_and_package_draft_markers():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    package_files = build_tenant_package_files(bundle, config_root=CONFIG_ROOT)
    package_dir = Path("tmp/dynamic_platform_safety_package")
    package_dir.mkdir(parents=True, exist_ok=True)
    for name, content in package_files.items():
        (package_dir / name).write_text(content, encoding="utf-8")

    report = run_safety_audit(
        bundle,
        config_root=CONFIG_ROOT,
        env_file=".env.example",
        package_dir=package_dir,
    )

    assert report.ok is True
    payload = report.to_dict()
    assert payload["checks"]["classic_runtime_import_isolated"] is True
    assert payload["checks"]["omu_runtime_strategy_classic_protected"] is True
    assert payload["checks"]["package_manifest_offline_handoff"] is True
    assert payload["checks"]["package_manifest_hashes_ok"] is True
    assert payload["checks"]["package_config_snapshot_exists"] is True
    assert payload["checks"]["package_config_snapshot_hashes_match"] is True
    assert payload["checks"]["package_handoff_index_exists"] is True
    assert payload["checks"]["package_handoff_index_offline_safe"] is True
    assert payload["checks"]["package_handoff_required_artifacts_present"] is True
    assert payload["checks"]["package_handoff_verification_order_present"] is True
    assert payload["checks"]["package_portability_audit_ok"] is True
    assert payload["checks"]["package_compose_manifest_draft"] is True
    assert payload["checks"]["package_compose_override_draft_marker"] is True
    assert payload["checks"]["package_compose_isolation_ok"] is True


def test_tenant_cli_safety_audit_for_omu_package(capsys):
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    output_dir = Path("tmp/dynamic_platform_safety_cli_package")
    write_tenant_package(bundle, config_root=CONFIG_ROOT, output_dir=output_dir, force=True)

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "safety-audit",
            "--tenant",
            "omu",
            "--env-file",
            ".env.example",
            "--package-dir",
            str(output_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Safety audit: OK" in captured.out
    assert "classic_runtime_import_isolated: yes" in captured.out
    assert "package_manifest_offline_handoff: yes" in captured.out
    assert "package_config_snapshot_exists: yes" in captured.out
    assert "package_config_snapshot_hashes_match: yes" in captured.out
    assert "package_handoff_index_offline_safe: yes" in captured.out
    assert "package_portability_audit_ok: yes" in captured.out
    assert "package_compose_manifest_draft: yes" in captured.out


def test_safety_audit_detects_stale_config_snapshot():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    package_files = build_tenant_package_files(bundle, config_root=CONFIG_ROOT)
    snapshot = json.loads(package_files["config_snapshot.json"])
    snapshot["files"][0]["sha256"] = "0" * 64
    package_files["config_snapshot.json"] = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    package_dir = Path("tmp/dynamic_platform_stale_config_package")
    package_dir.mkdir(parents=True, exist_ok=True)
    for name, content in package_files.items():
        (package_dir / name).write_text(content, encoding="utf-8")

    report = run_safety_audit(
        bundle,
        config_root=CONFIG_ROOT,
        env_file=".env.example",
        package_dir=package_dir,
    )

    payload = report.to_dict()
    assert report.ok is False
    assert payload["checks"]["package_config_snapshot_hashes_match"] is False
    assert any(error["code"] == "package_config_snapshot_hash_mismatch" for error in payload["errors"])


def test_shadow_runtime_preview_maps_acme_query_to_agents_and_sources():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    decision = build_shadow_runtime_decision(bundle, query="Yillik izin politikasi nedir?")
    payload = decision.to_dict()

    assert payload["runtime_binding_status"] == "shadow_only_runtime_not_wired"
    assert payload["match_mode"] == "keyword_shadow"
    assert payload["selected_capabilities"] == ["leave_policy"]
    assert payload["agents"] == ["hr_policy"]
    assert payload["specialists"] == ["leave_specialist"]
    assert payload["source_families"] == ["hr_documents"]
    assert payload["final_owner_candidates"] == ["hr_policy"]


def test_runtime_adapter_draft_preview_is_shadow_only_and_side_effect_free():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    adapter = DynamicRuntimeAdapterDraft(bundle)
    request = DynamicRuntimeRequest(
        tenant_key="acme_demo",
        conversation_id="conv-1",
        user_id="user-1",
        query="Yillik izin politikasi nedir?",
        locale="tr-TR",
        timezone="Europe/Istanbul",
    )

    response = adapter.preview(request)
    payload = response.to_dict()

    assert payload["answer"] == ""
    assert payload["answer_status"] == "shadow_decision_only"
    assert payload["selected_capabilities"] == ["leave_policy"]
    assert payload["agents"] == ["hr_policy"]
    assert payload["telemetry"]["adapter_status"] == "draft_shadow_only_not_wired"
    assert "No cache" in " ".join(payload["safety_notes"])


def test_runtime_adapter_draft_refuses_live_request():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    adapter = DynamicRuntimeAdapterDraft(bundle)
    request = DynamicRuntimeRequest(
        tenant_key="omu",
        conversation_id="conv-1",
        user_id="user-1",
        query="ÇAP başvuru tarihi nedir?",
        locale="tr-TR",
        timezone="Europe/Istanbul",
    )

    response = adapter.handle_live_request(request)
    payload = response.to_dict()

    assert payload["answer_status"] == "unsafe_to_answer"
    assert payload["answer"] == ""
    assert payload["telemetry"]["adapter_status"] == "draft_shadow_only_not_wired"
    assert payload["telemetry"]["activation_guard"]["status"] == "live_binding_blocked"
    assert payload["telemetry"]["activation_guard"]["live_binding_allowed"] is False
    assert "Classic runtime" in " ".join(payload["safety_notes"])


def test_runtime_activation_guard_blocks_until_every_live_gate_passes():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    blocked = evaluate_runtime_activation(
        bundle,
        RuntimeActivationInput(
            package_audit_ok=True,
            runtime_isolation_ok=True,
            secret_readiness_ok=True,
            golden_replay_ok=True,
            narrow_live_replay_ok=True,
            explicit_operator_approval=True,
            adapter_live_binding_implemented=True,
            requested_live_mode="dynamic_pilot",
            allowed_tenants=["acme_demo"],
        ),
    )
    blocked_payload = blocked.to_dict()

    assert blocked.live_binding_allowed is False
    assert blocked_payload["status"] == "live_binding_blocked"
    assert any("runtime_strategy_dynamic_pilot_or_on" in blocker for blocker in blocked_payload["blockers"])

    bundle.tenant.runtime_strategy = "dynamic_pilot"
    allowed = evaluate_runtime_activation(
        bundle,
        RuntimeActivationInput(
            package_audit_ok=True,
            runtime_isolation_ok=True,
            secret_readiness_ok=True,
            golden_replay_ok=True,
            narrow_live_replay_ok=True,
            explicit_operator_approval=True,
            adapter_live_binding_implemented=True,
            requested_live_mode="dynamic_pilot",
            allowed_tenants=["acme_demo"],
        ),
    )
    allowed_payload = allowed.to_dict()

    assert allowed.live_binding_allowed is True
    assert allowed_payload["status"] == "live_binding_allowed"
    assert set(allowed_payload["passed_gates"]) == set(allowed_payload["required_gates"])


def test_runtime_adapter_draft_still_refuses_even_if_activation_input_is_ready():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.tenant.runtime_strategy = "dynamic_pilot"
    adapter = DynamicRuntimeAdapterDraft(bundle)
    request = DynamicRuntimeRequest(
        tenant_key="acme_demo",
        conversation_id="conv-1",
        user_id="user-1",
        query="Yillik izin politikasi nedir?",
        locale="tr-TR",
        timezone="Europe/Istanbul",
    )

    response = adapter.handle_live_request(
        request,
        RuntimeActivationInput(
            package_audit_ok=True,
            runtime_isolation_ok=True,
            secret_readiness_ok=True,
            golden_replay_ok=True,
            narrow_live_replay_ok=True,
            explicit_operator_approval=True,
            adapter_live_binding_implemented=True,
            requested_live_mode="dynamic_pilot",
            allowed_tenants=["acme_demo"],
        ),
    )
    payload = response.to_dict()

    assert payload["answer_status"] == "unsafe_to_answer"
    assert payload["answer"] == ""
    assert payload["telemetry"]["activation_guard"]["live_binding_allowed"] is True
    assert "not_wired" in payload["telemetry"]["adapter_status"]


def test_runtime_live_adapter_refuses_when_activation_guard_blocks():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    adapter = DynamicRuntimeLiveAdapter(bundle)
    request = DynamicRuntimeRequest(
        tenant_key="acme_demo",
        conversation_id="conv-1",
        user_id="user-1",
        query="Yıllık izin politikası nedir?",
        locale="tr-TR",
        timezone="Europe/Istanbul",
    )

    response = adapter.handle(request)
    payload = response.to_dict()

    assert payload["answer_status"] == "unsafe_to_answer"
    assert payload["answer"] == ""
    assert payload["telemetry"]["adapter_status"] == "implemented_guarded_not_wired"
    assert payload["telemetry"]["activation_guard"]["live_binding_allowed"] is False
    assert "No user-facing dynamic answer" in " ".join(payload["safety_notes"])


def test_runtime_live_adapter_answers_only_after_all_activation_gates_pass():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.tenant.runtime_strategy = "dynamic_pilot"
    adapter = DynamicRuntimeLiveAdapter(bundle)
    request = DynamicRuntimeRequest(
        tenant_key="acme_demo",
        conversation_id="conv-1",
        user_id="user-1",
        query="Yıllık izin politikası nedir?",
        locale="tr-TR",
        timezone="Europe/Istanbul",
        requested_capabilities=["leave_policy"],
    )
    activation = RuntimeActivationInput(
        package_audit_ok=True,
        runtime_isolation_ok=True,
        secret_readiness_ok=True,
        golden_replay_ok=True,
        narrow_live_replay_ok=True,
        explicit_operator_approval=True,
        adapter_live_binding_implemented=True,
        requested_live_mode="dynamic_pilot",
        allowed_tenants=["acme_demo"],
        allowed_capabilities=["leave_policy"],
    )

    response = adapter.handle(request, activation)
    payload = response.to_dict()

    assert payload["answer_status"] == "answered"
    assert payload["selected_capabilities"] == ["leave_policy"]
    assert payload["agents"] == ["hr_policy"]
    assert payload["sources"] == ["acme_hr_documents"]
    assert payload["telemetry"]["adapter_status"] == "implemented_guarded_not_wired"
    assert payload["telemetry"]["activation_guard"]["live_binding_allowed"] is True
    assert payload["telemetry"]["namespace_preview"]["ok"] is True
    assert "ACME Teknoloji kaynaklarına göre" in payload["answer"]
    assert "student_affairs" not in json.dumps(payload, ensure_ascii=False)


def test_runtime_live_adapter_enforces_capability_allowlist():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.tenant.runtime_strategy = "dynamic_pilot"
    adapter = DynamicRuntimeLiveAdapter(bundle)
    request = DynamicRuntimeRequest(
        tenant_key="acme_demo",
        conversation_id="conv-1",
        user_id="user-1",
        query="VPN erişimi için nasıl talep açarım?",
        locale="tr-TR",
        timezone="Europe/Istanbul",
        requested_capabilities=["it_ticket_guidance"],
    )
    activation = RuntimeActivationInput(
        package_audit_ok=True,
        runtime_isolation_ok=True,
        secret_readiness_ok=True,
        golden_replay_ok=True,
        narrow_live_replay_ok=True,
        explicit_operator_approval=True,
        adapter_live_binding_implemented=True,
        requested_live_mode="dynamic_pilot",
        allowed_tenants=["acme_demo"],
        allowed_capabilities=["leave_policy"],
    )

    response = adapter.handle(request, activation)
    payload = response.to_dict()

    assert payload["answer_status"] == "unsafe_to_answer"
    assert payload["telemetry"]["reason"] == "capability_not_allowlisted"
    assert "it_ticket_guidance" in payload["telemetry"]["detail"]


def test_tenant_cli_runtime_activation_guard_reports_blockers(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-activation-guard",
            "--tenant",
            "acme_demo",
            "--requested-live-mode",
            "dynamic_pilot",
            "--allowed-tenant",
            "acme_demo",
            "--package-audit-ok",
            "--runtime-isolation-ok",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Runtime activation guard: BLOCKED" in captured.out
    assert "Live binding allowed: no" in captured.out
    assert "secret_readiness_ok" in captured.out
    assert "adapter_live_binding_implemented" in captured.out


def test_tenant_cli_runtime_adapter_draft_preview_is_not_user_facing(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-adapter-draft",
            "--tenant",
            "acme_demo",
            "--query",
            "Yillik izin politikasi nedir?",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Adapter draft status: draft_shadow_only_not_wired" in captured.out
    assert "Answer status: shadow_decision_only" in captured.out
    assert "User-facing answer emitted: no" in captured.out


def test_runtime_adapter_implementation_plan_is_planning_only():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = build_runtime_adapter_implementation_plan(bundle)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["implementation_status"] == "guarded_boundary_available_not_wired"
    assert payload["live_binding_allowed_now"] is False
    assert payload["adapter_contract"]["dynamic_live_binding_allowed"] is False
    assert payload["summary"]["phase_count"] == 6
    assert "adapter_boundary_code" in payload["summary"]["ready_now"]
    assert any(phase["phase_id"] == "pilot_gate" for phase in payload["phases"])
    assert any("No live request routing" in item for item in payload["non_goals"])


def test_tenant_cli_runtime_adapter_implementation_plan_reports_phases(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-adapter-implementation-plan",
            "--tenant",
            "city_demo",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Runtime adapter implementation plan: OK" in captured.out
    assert "Live binding allowed now: no" in captured.out
    assert "adapter_boundary_code" in captured.out


def test_runtime_isolation_contract_namespaces_tenant_state_and_uploaded_context():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    report = build_runtime_isolation_contract(bundle)
    payload = report.to_dict()
    namespaces = {record["namespace_id"]: record for record in payload["namespaces"]}

    assert report.ok is True
    assert payload["live_runtime_allowed"] is False
    assert namespaces["answer_cache"]["prefix"] == "tenant:omu:answer_cache:"
    assert namespaces["conversation_state"]["shared_between_tenants"] is False
    assert namespaces["uploaded_context"]["writes_allowed_in_shadow"] is False
    assert namespaces["model_artifacts"]["shared_between_tenants"] is True
    assert any(source["source_id"] == "omu_uploaded_transcripts" for source in payload["uploaded_context_sources"])
    assert all(source["runtime_scoped"] for source in payload["uploaded_context_sources"])
    assert "write_answer_cache" in payload["forbidden_in_shadow"]


def test_runtime_isolation_contract_for_non_uploaded_tenant_is_still_tenant_scoped():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = build_runtime_isolation_contract(bundle)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["uploaded_context_sources"] == []
    assert all(
        namespace["prefix"].startswith("tenant:acme_demo:") or namespace["prefix"] == "shared:model_cache:"
        for namespace in payload["namespaces"]
    )
    assert any(check["check_id"] == "uploaded_context_runtime_scoped" and check["ok"] for check in payload["checks"])


def test_tenant_cli_runtime_isolation_contract_reports_namespaces(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-isolation-contract",
            "--tenant",
            "city_demo",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Runtime isolation contract: OK" in captured.out
    assert "tenant:city_demo:answer_cache:" in captured.out
    assert "Live runtime allowed: no" in captured.out
    assert "Forbidden in shadow" in captured.out


def test_runtime_namespace_builder_generates_tenant_scoped_keys_without_writes():
    omu = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    acme = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    omu_builder = RuntimeNamespaceBuilder(omu)
    acme_builder = RuntimeNamespaceBuilder(acme)

    omu_answer = omu_builder.answer_cache_key(query="Mezuniyet icin kac AKTS?", source_scope={"family": "student"})
    acme_answer = acme_builder.answer_cache_key(query="Mezuniyet icin kac AKTS?", source_scope={"family": "student"})
    omu_model = omu_builder.model_artifact_key(model_id="bge-reranker")
    validation = omu_builder.validate_keys(
        [
            omu_answer,
            omu_builder.retrieval_cache_key(query="q", source_family="student_policy_documents"),
            omu_builder.conversation_state_key(conversation_id="conv-1"),
            omu_builder.uploaded_context_key(conversation_id="conv-1", user_id="user-1", file_id="file-1"),
            omu_model,
        ]
    )

    assert omu_answer.key.startswith("tenant:omu:answer_cache:")
    assert acme_answer.key.startswith("tenant:acme_demo:answer_cache:")
    assert omu_answer.key != acme_answer.key
    assert omu_model.key.startswith("shared:model_cache:")
    assert omu_model.shared_between_tenants is True
    assert validation.ok is True
    assert all(not item["writes_allowed_in_shadow"] for item in validation.to_dict()["checked_keys"])


def test_runtime_namespace_validation_rejects_cross_tenant_data_key():
    omu = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    acme = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    omu_key = RuntimeNamespaceBuilder(omu).answer_cache_key(query="same")

    validation = RuntimeNamespaceBuilder(acme).validate_keys([omu_key])

    assert validation.ok is False
    assert any("tenant:acme_demo:answer_cache:" in error for error in validation.errors)


def test_runtime_namespace_preview_cli_reports_prefixes(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-namespace-preview",
            "--tenant",
            "acme_demo",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Runtime namespace preview: OK" in captured.out
    assert "tenant:acme_demo:answer_cache:" in captured.out
    assert "shared:model_cache:" in captured.out


def test_runtime_adapter_draft_preview_includes_namespace_telemetry():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    adapter = DynamicRuntimeAdapterDraft(bundle)
    request = DynamicRuntimeRequest(
        tenant_key="acme_demo",
        conversation_id="conv-namespace",
        user_id="user-1",
        query="Yillik izin politikasi nedir?",
        locale="tr-TR",
        timezone="Europe/Istanbul",
    )

    payload = adapter.preview(request).to_dict()
    namespace = payload["telemetry"]["namespace_preview"]

    assert namespace["ok"] is True
    assert any(key["key"].startswith("tenant:acme_demo:answer_cache:") for key in namespace["keys"])
    assert any(key["key"] == "tenant:acme_demo:conversation_state:conversation:conv-namespace" for key in namespace["keys"])


def test_shadow_runtime_preview_maps_public_service_query_to_agent_and_source():
    bundle = load_tenant_bundle("city_demo", config_root=CONFIG_ROOT)

    decision = build_shadow_runtime_decision(bundle, query="Ruhsat başvurusu için hangi belgeler gerekli?")
    payload = decision.to_dict()

    assert payload["runtime_binding_status"] == "shadow_only_runtime_not_wired"
    assert payload["selected_capabilities"] == ["document_requirement"]
    assert payload["agents"] == ["citizen_services"]
    assert payload["source_families"] == ["service_policy_documents"]
    assert payload["final_owner_candidates"] == ["citizen_services"]


def test_shadow_runtime_preview_can_use_explicit_capability_for_omu():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    decision = build_shadow_runtime_decision(
        bundle,
        query="Cap basvuru tarihleri ne zaman?",
        requested_capabilities=["double_major_minor", "academic_calendar", "announcement_lookup"],
    )
    payload = decision.to_dict()

    assert payload["runtime_strategy"] == "classic_protected"
    assert payload["match_mode"] == "explicit_capability"
    assert payload["confidence"] == 1.0
    assert "student_affairs" in payload["agents"]
    assert "academic_programs" in payload["agents"]
    assert "announcement" in payload["agents"]
    assert "Tenant is classic_protected" in " ".join(payload["notes"])


def test_tenant_cli_shadow_runtime_preview_is_offline(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "shadow-runtime",
            "--tenant",
            "acme_demo",
            "--query",
            "Maas bordrom hakkinda kime sorabilirim?",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Binding status: shadow_only_runtime_not_wired" in captured.out
    assert "Capabilities: payroll_question" in captured.out
    assert "Agents: payroll" in captured.out
    assert "does not call router" in captured.out


def test_shadow_runtime_replay_contract_mode_passes_for_omu_fixture():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    report = run_shadow_runtime_replay(bundle, match_mode="contract")
    payload = report.to_dict()

    assert report.ok is True
    assert payload["match_mode"] == "contract"
    assert payload["runtime_binding_status"] == "shadow_only_runtime_not_wired"
    assert payload["summary"]["case_count"] >= 8
    assert payload["summary"]["failed"] == 0


def test_shadow_runtime_replay_keyword_mode_passes_for_omu_fixture():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    report = run_shadow_runtime_replay(bundle, match_mode="keyword")
    payload = report.to_dict()

    assert report.ok is True
    assert payload["match_mode"] == "keyword"
    assert payload["runtime_binding_status"] == "shadow_only_runtime_not_wired"
    assert payload["summary"]["case_count"] >= 8
    assert payload["summary"]["failed"] == 0


def test_shadow_runtime_replay_keyword_mode_passes_for_acme_demo_fixture():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = run_shadow_runtime_replay(bundle, match_mode="keyword")
    payload = report.to_dict()

    assert report.ok is True
    assert payload["match_mode"] == "keyword"
    assert payload["summary"]["case_count"] == 4
    assert payload["summary"]["failed"] == 0


def test_shadow_runtime_replay_keyword_mode_passes_for_public_service_fixture():
    bundle = load_tenant_bundle("city_demo", config_root=CONFIG_ROOT)

    report = run_shadow_runtime_replay(bundle, match_mode="keyword")
    payload = report.to_dict()

    assert report.ok is True
    assert payload["match_mode"] == "keyword"
    assert payload["summary"]["case_count"] == 4
    assert payload["summary"]["failed"] == 0


def test_tenant_cli_shadow_runtime_replay_reports_fixture_cases(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "shadow-runtime-replay",
            "--tenant",
            "acme_demo",
            "--match-mode",
            "keyword",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Shadow runtime replay: OK" in captured.out
    assert "Match mode: keyword" in captured.out
    assert "ACME-HR-LEAVE" in captured.out


def test_omu_shadow_decision_fixture_is_represented_by_dynamic_profile():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    fixture_path = default_shadow_fixture_path("omu")
    cases = load_shadow_decision_cases(fixture_path)

    report = compare_shadow_decisions(bundle, cases, fixture_path=fixture_path)

    payload = report.to_dict()
    assert report.ok is True
    assert payload["summary"]["case_count"] >= 8
    assert payload["summary"]["failed"] == 0


def test_shadow_decision_compare_catches_missing_capability():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    case = ShadowDecisionCase(
        case_id="BROKEN",
        query="Bilinmeyen capability testi",
        expected_capabilities=["missing_capability"],
    )

    report = compare_shadow_decisions(bundle, [case], fixture_path="inline")

    assert report.ok is False
    record = report.records[0]
    assert any(issue.code == "capability_missing" for issue in record.issues)


def test_tenant_cli_shadow_decisions_for_omu(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "shadow-decisions", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Shadow decision compare" in captured.out
    assert "OMU-CAP-DATE" in captured.out
    assert "9/9 passed" in captured.out


def test_source_adapter_audit_passes_for_omu_acme_and_public_service_demo():
    omu_bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    acme_bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    city_bundle = load_tenant_bundle("city_demo", config_root=CONFIG_ROOT)

    omu_report = audit_source_adapters(omu_bundle)
    acme_report = audit_source_adapters(acme_bundle)
    city_report = audit_source_adapters(city_bundle)

    assert omu_report.ok is True
    assert acme_report.ok is True
    assert city_report.ok is True
    assert omu_report.summary["source_count"] == 8
    assert omu_report.summary["domains"] == ["education_university"]
    assert "announcement_page" in acme_report.summary["adapters"]
    assert "api_endpoint" in city_report.summary["adapters"]


def test_source_adapter_audit_catches_authority_mismatch():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    announcement_source = next(source for source in bundle.source_catalog.sources if source.adapter == "announcement_page")
    announcement_source.authority_level = "official_policy"

    report = audit_source_adapters(bundle)

    assert report.ok is False
    assert any(issue.code == "adapter_authority_mismatch" for issue in report.errors)


def test_source_adapter_audit_catches_domain_mismatch():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.source_catalog.sources[0].domain = "education_university"

    report = audit_source_adapters(bundle)

    assert report.ok is False
    assert any(issue.code == "source_domain_mismatch" for issue in report.errors)


def test_source_adapter_audit_catches_owner_capability_mismatch():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    contact_source = next(source for source in bundle.source_catalog.sources if source.source_id == "omu_contact_directory")
    contact_source.capabilities = ["course_schedule"]

    report = audit_source_adapters(bundle)

    assert report.ok is False
    assert any(issue.code == "source_owner_lacks_capability" for issue in report.errors)


def test_source_adapter_audit_catches_unknown_entity_scope_group():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    schedule_source = next(source for source in bundle.source_catalog.sources if source.source_id == "omu_weekly_schedule")
    schedule_source.entity_scope.entity_group = "unknown_group"

    report = audit_source_adapters(bundle)

    assert report.ok is False
    assert any(issue.code == "entity_scope_group_unknown" for issue in report.errors)


def test_retrieval_contract_makes_demo_local_reader_limitation_explicit():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = build_retrieval_contract(bundle)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["current_mode"] == "local_source_retrieval_service_no_download_smoke"
    assert payload["dedicated_retrieval_service_wired"] is False
    assert "acme_demo_hr_documents" in payload["tenant_collections"]
    assert any("local_retrieval_service" in warning for warning in payload["warnings"])
    assert "tenant-scoped collection selection" in payload["required_live_capabilities"]


def test_tenant_cli_retrieval_contract_reports_current_mode(capsys):
    exit_code = tenant_cli_main(
        ["--config-root", str(CONFIG_ROOT), "retrieval-contract", "--tenant", "acme_demo"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Retrieval contract:" in captured.out
    assert "Status: OK" in captured.out
    assert "local_source_retrieval_service_no_download_smoke" in captured.out
    assert "acme_demo_hr_documents" in captured.out


def test_model_runtime_contract_keeps_cache_fp16_and_reranker_switches_explicit():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = build_model_runtime_contract(bundle)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["safety_status"] == "offline_contract_only_no_model_load"
    assert payload["model_cache"]["default_host_dir"] == "./data/models"
    assert payload["model_cache"]["shared_model_artifacts_allowed"] is True
    assert payload["model_cache"]["tenant_data_cache_shared"] is False
    assert payload["reranker_policy"]["current_configured_model"] == "BAAI/bge-reranker-v2-m3"
    assert payload["reranker_policy"]["current_configured_torch_dtype"] == "float16"
    assert payload["reranker_policy"]["rollback_baseline"] == "nreimers/mmarco-mMiniLMv2-L6-H384-v1"
    assert payload["reranker_policy"]["primary_bge_candidate"] == "BAAI/bge-reranker-v2-m3"
    assert payload["reranker_policy"]["turkish_shadow_candidate"] == "seroe/bge-reranker-v2-m3-turkish-triplet"
    assert payload["reranker_policy"]["turkish_candidate_default_enabled"] is False
    assert payload["precision_policy"]["fp16_allowed_only_on_cuda"] is True
    assert payload["precision_policy"]["cpu_uses_fp32"] is True
    assert payload["offline_generation"]["downloads_models"] is False


def test_tenant_cli_model_runtime_contract_reports_cache_and_fp16(capsys):
    exit_code = tenant_cli_main(
        ["--config-root", str(CONFIG_ROOT), "model-runtime-contract", "--tenant", "acme_demo"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Model runtime contract:" in captured.out
    assert "MODEL_CACHE_HOST_DIR=./data/models" in captured.out
    assert "Current configured reranker: BAAI/bge-reranker-v2-m3" in captured.out
    assert "Current configured dtype: float16" in captured.out
    assert "Turkish shadow candidate: seroe/bge-reranker-v2-m3-turkish-triplet" in captured.out
    assert "FP16 allowed only on CUDA: True" in captured.out


def test_source_ingestion_plan_maps_omu_sources_without_touching_connectors():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    report = build_source_ingestion_plan(bundle)
    payload = report.to_dict()
    steps = {step["source_id"]: step for step in payload["steps"]}

    assert report.ok is True
    assert payload["summary"]["source_count"] == 8
    assert steps["omu_student_policy_documents"]["action"] == "document_parse_chunk_embed"
    assert steps["omu_weekly_schedule"]["action"] == "structured_table_mapping"
    assert steps["omu_announcements"]["action"] == "announcement_sync_index"
    assert steps["omu_announcements"]["live_connector_required"] is True
    assert steps["omu_uploaded_transcripts"]["action"] == "runtime_uploaded_context_only"
    assert steps["omu_uploaded_transcripts"]["preindex_required"] is False
    assert "does not open files" in " ".join(payload["notes"])


def test_source_ingestion_plan_maps_non_university_sources():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = build_source_ingestion_plan(bundle)
    payload = report.to_dict()
    action_counts = payload["summary"]["action_counts"]
    steps = {step["source_id"]: step for step in payload["steps"]}

    assert action_counts["document_parse_chunk_embed"] == 2
    assert action_counts["web_snapshot_parse_index"] == 1
    assert action_counts["structured_csv_import"] == 1
    assert steps["acme_it_knowledge_base"]["owner_agent"] == "it_support"
    assert steps["acme_internal_announcements"]["authority_level"] == "official_announcement"
    assert "program" not in json.dumps(payload, ensure_ascii=False).lower()


def test_tenant_cli_source_ingestion_plan_reports_offline_steps(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "source-ingestion-plan", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Source ingestion plan" in captured.out
    assert "omu_uploaded_transcripts" in captured.out
    assert "runtime_uploaded_context_only" in captured.out
    assert "does not open files" in captured.out


def test_genericity_audit_keeps_domain_terms_out_of_dynamic_core():
    report = run_genericity_audit()
    payload = report.to_dict()

    assert report.ok is True
    assert payload["summary"]["scanned_file_count"] >= 10
    assert payload["summary"]["error_count"] == 0
    assert payload["summary"]["allowed_mention_count"] > 0


def test_tenant_cli_genericity_audit_reports_allowed_protection_refs(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "genericity-audit"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Genericity audit: OK" in captured.out
    assert "allowed_mentions=" in captured.out
    assert "domain packs/configs" in captured.out.lower()


def test_tenant_cli_source_audit_for_omu(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "source-audit", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Source adapter audit" in captured.out
    assert "Status: OK" in captured.out


def test_omu_quality_gates_pass_offline_without_runtime_wiring():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    report = run_quality_gates(bundle)

    payload = report.to_dict()
    assert report.ok is True
    assert payload["summary"]["failed"] == 0
    assert {gate["gate_id"] for gate in payload["gates"]} == {
        "validate_bundle",
        "classic_topology_compare",
        "source_adapter_audit",
        "dynamic_core_genericity_audit",
        "shadow_decision_contracts",
    }


def test_quality_gates_fail_when_shadow_fixture_is_required_but_missing():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = run_quality_gates(bundle, shadow_fixture_path="missing_shadow_fixture.json")

    assert report.ok is False
    payload = report.to_dict()
    assert any(
        gate["gate_id"] == "shadow_decision_contracts" and gate["status"] == "failed"
        for gate in payload["gates"]
    )


def test_acme_demo_quality_gates_pass_with_non_university_shadow_fixture():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = run_quality_gates(bundle)

    assert report.ok is True
    payload = report.to_dict()
    assert any(
        gate["gate_id"] == "shadow_decision_contracts" and gate["status"] == "passed"
        for gate in payload["gates"]
    )


def test_tenant_cli_quality_gates_for_omu(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "quality-gates", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Quality gates: OK" in captured.out
    assert "source_adapter_audit: passed" in captured.out
    assert "dynamic_core_genericity_audit: passed" in captured.out
    assert "shadow_decision_contracts: passed" in captured.out


def test_tenant_portfolio_audit_checks_all_configured_tenants_offline():
    report = run_tenant_portfolio_audit(config_root=CONFIG_ROOT)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["summary"]["tenant_count"] == 3
    assert payload["summary"]["passed"] == 3
    assert payload["genericity_audit"]["ok"] is True
    assert {record["tenant_key"] for record in payload["records"]} == {"omu", "acme_demo", "city_demo"}
    assert all(record["runtime_adapter_contract"]["adapter_status"] == "not_wired" for record in payload["records"])


def test_tenant_cli_audit_all_reports_portfolio_status(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "audit-all"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tenant portfolio audit: OK" in captured.out
    assert "3/3 passed" in captured.out
    assert "classic_protected" in captured.out
    assert "dynamic_shadow" in captured.out


def test_omu_runtime_plan_is_classic_safe_and_env_ready():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    plan = build_runtime_launch_plan(bundle, config_root=CONFIG_ROOT)
    payload = plan.to_dict()

    assert payload["compose_env_ready"] is True
    assert payload["live_runtime_enabled"] is True
    assert payload["runtime_binding_status"] == "classic_runtime_active_dynamic_runtime_disabled"
    assert payload["env"]["TENANT_KEY"] == "omu"
    assert payload["env"]["DYNAMIC_PLATFORM_RUNTIME"] == "disabled"


def test_runtime_adapter_contract_keeps_omu_classic_runtime_owner():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    contract = build_runtime_adapter_contract(bundle)
    payload = contract.to_dict()

    assert payload["adapter_status"] == "not_wired"
    assert payload["classic_runtime_must_remain_owner"] is True
    assert payload["dynamic_live_binding_allowed"] is False
    assert "dynamic_shadow_as_user_response" in payload["blocked_modes"]
    assert "Classic runtime directories must not import src.dynamic_platform" in " ".join(
        payload["safety_requirements"]
    )


def test_runtime_adapter_contract_for_demo_tenant_is_shadow_only():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    contract = build_runtime_adapter_contract(bundle)
    payload = contract.to_dict()

    assert payload["runtime_strategy"] == "dynamic_shadow"
    assert payload["adapter_status"] == "not_wired"
    assert payload["dynamic_live_binding_allowed"] is False
    assert "shadow_decision_preview" in payload["allowed_modes"]
    assert "dynamic_pilot_live_requests" in payload["blocked_modes"]


def test_tenant_cli_runtime_adapter_contract_reports_boundary(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "runtime-adapter-contract", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Adapter status: not_wired" in captured.out
    assert "Dynamic live binding allowed: no" in captured.out
    assert "Classic runtime owner: yes" in captured.out


def test_acme_runtime_plan_is_shadow_only_without_live_runtime():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    plan = build_runtime_launch_plan(bundle, config_root=CONFIG_ROOT, require_quality_gates=False)
    payload = plan.to_dict()

    assert payload["compose_env_ready"] is True
    assert payload["live_runtime_enabled"] is False
    assert payload["runtime_binding_status"] == "dynamic_profile_ready_shadow_only_runtime_not_wired"
    assert payload["env"]["TENANT_KEY"] == "acme_demo"
    assert payload["env"]["DYNAMIC_PLATFORM_RUNTIME"] == "shadow"


def test_tenant_cli_runtime_plan_for_omu(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "runtime-plan", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Compose env ready: yes" in captured.out
    assert "TENANT_KEY=omu" in captured.out
    assert "classic_runtime_active_dynamic_runtime_disabled" in captured.out


def test_env_example_contains_informational_tenant_runtime_defaults():
    content = Path(".env.example").read_text(encoding="utf-8")

    assert "TENANT_KEY=omu" in content
    assert "TENANT_CONFIG_ROOT=configs/dynamic_platform" in content
    assert "TENANT_RUNTIME_STRATEGY=classic_protected" in content
    assert "TENANT_DOMAIN_PACK=education_university" in content
    assert "DYNAMIC_PLATFORM_RUNTIME=disabled" in content
    assert "dynamic runtime adapter ayri fazda baglanacaktir" in content


def test_runtime_env_check_accepts_omu_env_example():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    report = check_runtime_env(bundle, config_root=CONFIG_ROOT, env_file=".env.example")

    assert report.ok is True
    payload = report.to_dict()
    assert payload["observed_env"]["TENANT_KEY"] == "omu"
    assert payload["observed_env"]["DYNAMIC_PLATFORM_RUNTIME"] == "disabled"


def test_runtime_env_check_accepts_shadow_demo_env_mapping():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    plan = build_runtime_launch_plan(bundle, config_root=CONFIG_ROOT, require_quality_gates=False)

    report = check_runtime_env(
        bundle,
        config_root=CONFIG_ROOT,
        env_values=plan.env,
        require_quality_gates=False,
    )

    assert report.ok is True
    assert report.runtime_binding_status == "dynamic_profile_ready_shadow_only_runtime_not_wired"


def test_runtime_env_check_rejects_cross_tenant_env_mapping():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    plan = build_runtime_launch_plan(bundle, config_root=CONFIG_ROOT)
    env = dict(plan.env)
    env["TENANT_KEY"] = "acme_demo"

    report = check_runtime_env(bundle, config_root=CONFIG_ROOT, env_values=env)

    assert report.ok is False
    assert any(issue.code == "env_value_mismatch" and issue.key == "TENANT_KEY" for issue in report.errors)


def test_runtime_env_check_rejects_live_dynamic_flag_before_adapter_is_wired():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    plan = build_runtime_launch_plan(bundle, config_root=CONFIG_ROOT)
    env = dict(plan.env)
    env["DYNAMIC_PLATFORM_RUNTIME"] = "on"

    report = check_runtime_env(bundle, config_root=CONFIG_ROOT, env_values=env)

    assert report.ok is False
    assert any(issue.code == "live_dynamic_runtime_not_wired" for issue in report.errors)


def test_parse_env_file_supports_quotes_and_export_prefix():
    env_path = Path("tmp/dynamic_platform_env_parser_test.env")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        env_path.write_text(
            "\n".join(
                [
                    "# comment",
                    "export TENANT_KEY='omu'",
                    'TENANT_BOT_NAME="OMU Destek Bot"',
                    "DYNAMIC_PLATFORM_RUNTIME=disabled",
                ]
            ),
            encoding="utf-8",
        )

        values = parse_env_file(env_path)

        assert values["TENANT_KEY"] == "omu"
        assert values["TENANT_BOT_NAME"] == "OMU Destek Bot"
        assert values["DYNAMIC_PLATFORM_RUNTIME"] == "disabled"
    finally:
        env_path.unlink(missing_ok=True)


def test_tenant_secrets_contract_declares_names_without_values():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    contract = build_tenant_secrets_contract(bundle)
    payload = contract.to_dict()
    example = contract.to_example_env()

    assert payload["secret_values_allowed_in_package"] is False
    assert payload["smoke_test_allowed_without_llm_secret"] is True
    assert payload["full_answering_requires_llm_secret"] is True
    assert any(group["group_id"] == "llm_provider_key" and group["mode"] == "one_of" for group in payload["groups"])
    assert "OPENAI_API_KEY=" in example
    assert "SLACK_BOT_TOKEN=" in example
    assert "local-a2a-secret" not in example


def test_tenant_cli_secrets_contract_reports_no_secret_values(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "secrets-contract", "--tenant", "acme_demo"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Secret values allowed in package: no" in captured.out
    assert "llm_provider_key" in captured.out
    assert "OPENAI_API_KEY" in captured.out


def test_pilot_secret_scaffold_writes_blank_env_outside_tenant_package():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    output_dir = Path("tmp/dynamic_platform_runtime_secrets_test")

    result = write_tenant_pilot_secret_scaffold(
        bundle,
        output_dir=output_dir,
        include_slack=True,
        force=True,
    )
    payload = result.to_dict()
    env_text = Path(payload["env_path"]).read_text(encoding="utf-8")
    manifest = json.loads(Path(payload["manifest_path"]).read_text(encoding="utf-8"))
    readiness = check_tenant_secret_readiness(
        bundle,
        mode="dynamic_pilot",
        include_slack=True,
        env_file=payload["env_path"],
    )

    assert result.ok is True
    assert payload["checks"]["output_outside_tenant_package"] is True
    assert payload["checks"]["secret_values_written"] is False
    assert "OPENAI_API_KEY=" in env_text
    assert "SLACK_BOT_TOKEN=" in env_text
    assert "sk-" not in env_text
    assert "xox" not in env_text.lower()
    assert manifest["secret_values_written"] is False
    assert "slack_socket_mode" in manifest["required_categories"]
    assert readiness.ok is False
    assert not any(issue.code == "secret_file_inside_tenant_package" for issue in readiness.errors)
    assert any(issue.code == "secret_group_not_ready" for issue in readiness.errors)


def test_tenant_cli_pilot_secret_scaffold_reports_blank_files(capsys):
    output_dir = Path("tmp/dynamic_platform_runtime_secrets_cli_test")

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "pilot-secret-scaffold",
            "--tenant",
            "city_demo",
            "--output-dir",
            str(output_dir),
            "--include-slack",
            "--force",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Pilot secret scaffold: OK" in captured.out
    assert "secret_values_written: no" in captured.out
    assert (output_dir / "city_demo.dynamic_pilot.secrets.env").exists()
    assert "SLACK_APP_TOKEN=" in (output_dir / "city_demo.dynamic_pilot.secrets.env").read_text(encoding="utf-8")


def test_secret_readiness_allows_no_secret_smoke_but_blocks_llm_answering_without_key():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    smoke = check_tenant_secret_readiness(bundle, mode="no_secret_smoke", env_values={})
    llm_missing = check_tenant_secret_readiness(bundle, mode="llm_answering", env_values={})
    llm_ready = check_tenant_secret_readiness(bundle, mode="llm_answering", env_values={"OPENAI_API_KEY": "sk-test"})

    assert smoke.ok is True
    assert llm_missing.ok is False
    assert any(issue.code == "secret_group_not_ready" and issue.group_id == "llm_provider_key" for issue in llm_missing.errors)
    assert llm_ready.ok is True
    assert all("sk-test" not in str(status.to_dict()) for status in llm_ready.key_statuses)


def test_secret_readiness_blocks_pilot_secret_file_inside_package():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    env_path = Path("tmp/tenant_packages/acme_demo/runtime.secret.env")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        env_path.write_text(
            "\n".join(
                [
                    "OPENAI_API_KEY=sk-test",
                    "SERVER_INTERNAL_API_KEY=internal",
                    "A2A_INTERNAL_API_KEY=internal",
                    "A2A_REQUEST_SIGNATURE_SECRET=signature",
                ]
            ),
            encoding="utf-8",
        )

        report = check_tenant_secret_readiness(bundle, mode="dynamic_pilot", env_file=env_path)

        assert report.ok is False
        assert any(issue.code == "secret_file_inside_tenant_package" for issue in report.errors)
    finally:
        env_path.unlink(missing_ok=True)


def test_tenant_cli_secret_readiness_masks_values(capsys):
    env_path = Path("tmp/acme_demo_runtime_secret_test.env")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        env_path.write_text("OPENAI_API_KEY=sk-test\n", encoding="utf-8")

        exit_code = tenant_cli_main(
            [
                "--config-root",
                str(CONFIG_ROOT),
                "secret-readiness",
                "--tenant",
                "acme_demo",
                "--mode",
                "llm_answering",
                "--env-file",
                str(env_path),
            ]
        )

        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Secret readiness: OK" in captured.out
        assert "OPENAI_API_KEY" in captured.out
        assert "sk-test" not in captured.out
    finally:
        env_path.unlink(missing_ok=True)


def test_tenant_cli_runtime_env_check_for_omu_env_example(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-env-check",
            "--tenant",
            "omu",
            "--env-file",
            ".env.example",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Runtime env check: OK" in captured.out
    assert "TENANT_KEY=omu" in captured.out


def test_docker_deployment_plan_marks_current_compose_as_single_instance_only():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    report = build_docker_deployment_plan(bundle, config_root=CONFIG_ROOT)
    payload = report.to_dict()

    assert payload["single_instance_env_ready"] is True
    assert payload["side_by_side_ready"] is False
    assert any(issue["code"] == "fixed_container_name" for issue in payload["blockers"])
    assert any(issue["code"] == "literal_env_file" for issue in payload["blockers"])


def test_docker_deployment_plan_blocks_dynamic_shadow_live_runtime_until_adapter_exists():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = build_docker_deployment_plan(bundle, config_root=CONFIG_ROOT, require_quality_gates=False)
    payload = report.to_dict()

    assert payload["single_instance_env_ready"] is True
    assert payload["live_dynamic_runtime_ready"] is False
    assert any(issue["code"] == "dynamic_runtime_adapter_not_wired" for issue in payload["blockers"])


def test_tenant_cli_docker_plan_reports_side_by_side_blockers(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "docker-plan",
            "--tenant",
            "omu",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Side-by-side Docker ready: no" in captured.out
    assert "fixed_container_name" in captured.out
    assert "literal_env_file" in captured.out


def test_compose_launch_template_files_are_draft_and_tenant_prefixed():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    files = build_compose_launch_template_files(
        bundle,
        config_root=CONFIG_ROOT,
        package_dir=Path("tmp/tenant_packages/acme_demo"),
    )
    manifest = json.loads(files["compose_launch_manifest.json"])
    override = files["docker-compose.tenant.override.draft.yml"]
    notes = files["COMPOSE_NOTES.md"]

    assert manifest["safety_status"] == "draft_do_not_run"
    assert manifest["container_prefix"] == "acme_demo"
    assert manifest["suggested_env_overrides"]["MODEL_CACHE_HOST_DIR"] == "./data/models"
    assert manifest["suggested_env_overrides"]["A2A_IMAGE_REF"] == "university_support_system-app:latest"
    assert "COMPOSE_DISABLE_ENV_FILE" in "\n".join(manifest["validation_commands"])
    assert "acme_demo_postgres" in override
    assert "acme_demo_agent_hr_policy" in override
    assert "acme_demo_agent_it_support" in override
    assert "acme_demo_agent_payroll" in override
    assert "scripts.run_dynamic_runtime" in override
    assert "scripts.run_generic_agent_host" in override
    assert "tenant-dynamic-agents" in override
    assert "AGENT_ID: hr_policy" in override
    assert "ACME_DEMO_POSTGRES_PORT" in override
    assert "tmp/tenant_packages/acme_demo/tenant.env" in override
    assert "env_file: !override" in override
    assert "ports: !override" in override
    assert "agent-finance:" in override
    assert "slack-bot-a2a:" in override
    assert "slack-bot-inprocess:" in override
    assert "disabled-classic-runtime" in override
    assert "dynamic-platform.classic-service-disabled: 'true'" in override
    assert "DRAFT ONLY" in override
    assert "dogrudan calistirmayin" in notes
    assert "docker compose config" in notes
    assert "Dynamic Slack adapter" in notes
    assert "Cache ve Internet Kullanimi" in notes
    assert "COMPOSE_DISABLE_ENV_FILE=1" in notes


def test_compose_launch_template_uses_tenant_port_offsets():
    acme = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    city = load_tenant_bundle("city_demo", config_root=CONFIG_ROOT)

    acme_files = build_compose_launch_template_files(
        acme,
        config_root=CONFIG_ROOT,
        package_dir=Path("tmp/tenant_packages/acme_demo"),
    )
    city_files = build_compose_launch_template_files(
        city,
        config_root=CONFIG_ROOT,
        package_dir=Path("tmp/tenant_packages/city_demo"),
    )
    acme_manifest = json.loads(acme_files["compose_launch_manifest.json"])
    city_manifest = json.loads(city_files["compose_launch_manifest.json"])

    assert acme_manifest["suggested_env_overrides"]["ACME_DEMO_API_PORT"] == "18000"
    assert city_manifest["suggested_env_overrides"]["CITY_DEMO_API_PORT"] == "28000"
    assert "${CITY_DEMO_API_PORT:-28000}:8000" in city_files["docker-compose.tenant.override.draft.yml"]


def test_tenant_cli_compose_template_writes_draft_files(capsys):
    output_dir = Path("tmp/dynamic_platform_compose_template_test")
    for name in (
        "compose_launch_manifest.json",
        "docker-compose.tenant.override.draft.yml",
        "COMPOSE_NOTES.md",
    ):
        (output_dir / name).unlink(missing_ok=True)
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "compose-template",
            "--tenant",
            "acme_demo",
            "--output-dir",
            str(output_dir),
            "--force",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Compose template directory" in captured.out
    assert (output_dir / "compose_launch_manifest.json").exists()
    assert "draft_do_not_run" in (output_dir / "compose_launch_manifest.json").read_text(encoding="utf-8")
    assert "acme_demo_postgres" in (output_dir / "docker-compose.tenant.override.draft.yml").read_text(
        encoding="utf-8"
    )


def test_compose_isolation_audit_accepts_generated_tenant_draft():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    package_dir = Path("tmp/tenant_packages/acme_demo")
    files = build_compose_launch_template_files(bundle, config_root=CONFIG_ROOT, package_dir=package_dir)

    report = run_compose_isolation_audit(bundle, package_dir=package_dir, draft_files=files)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["checks"]["manifest_safety_status_draft"] is True
    assert payload["checks"]["override_has_draft_marker"] is True
    assert payload["checks"]["container_names_tenant_prefixed"] is True
    assert payload["checks"]["service_labels_tenant_scoped"] is True
    assert payload["checks"]["service_tenant_environment_present"] is True
    assert payload["checks"]["port_env_vars_tenant_prefixed"] is True
    assert payload["checks"]["slack_services_profile_scoped"] is True
    assert payload["checks"]["manifest_disables_root_env_file"] is True
    assert "postgres" in payload["services_checked"]


def test_compose_isolation_audit_rejects_unprefixed_container_name():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    package_dir = Path("tmp/tenant_packages/acme_demo")
    files = build_compose_launch_template_files(bundle, config_root=CONFIG_ROOT, package_dir=package_dir)
    files["docker-compose.tenant.override.draft.yml"] = files["docker-compose.tenant.override.draft.yml"].replace(
        "container_name: acme_demo_postgres",
        "container_name: postgres",
    )

    report = run_compose_isolation_audit(bundle, package_dir=package_dir, draft_files=files)
    payload = report.to_dict()

    assert report.ok is False
    assert payload["checks"]["container_names_tenant_prefixed"] is False
    assert any(error["code"] == "compose_container_name_not_tenant_prefixed" for error in payload["errors"])


def test_compose_config_audit_accepts_dynamic_tenant_resolved_config(monkeypatch):
    package_dir = _write_acme_compose_config_package()

    def fake_run(cmd, **kwargs):
        command_text = " ".join(cmd)
        if "--format json" in command_text:
            payload = {
                "services": {
                    "postgres": {},
                    "redis": {},
                    "chromadb": {},
                    "api": {
                        "command": ["python", "-m", "scripts.run_dynamic_runtime"],
                        "depends_on": {
                            "postgres": {"condition": "service_started"},
                            "redis": {"condition": "service_started"},
                            "chromadb": {"condition": "service_started"},
                        },
                    },
                    "agent-finance": {
                        "profiles": ["disabled-classic-runtime"],
                        "ports": [],
                    },
                    "slack-bot-a2a": {
                        "profiles": ["disabled-classic-runtime"],
                        "ports": [],
                    },
                    "dynamic-agent-hr-policy": {
                        "profiles": ["tenant-dynamic-agents"],
                    },
                }
            }
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")
        if "--profile tenant-dynamic-agents" in command_text:
            return subprocess.CompletedProcess(
                cmd,
                0,
                stdout="dynamic-agent-hr-policy\npostgres\nredis\nchromadb\napi\n",
                stderr="",
            )
        return subprocess.CompletedProcess(cmd, 0, stdout="postgres\nredis\nchromadb\napi\n", stderr="")

    monkeypatch.setattr("src.dynamic_platform.compose_config_audit.subprocess.run", fake_run)

    report = run_compose_config_audit(
        tenant_key="acme_demo",
        config_root=CONFIG_ROOT,
        package_dir=package_dir,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["checks"]["dynamic_default_has_no_classic_services"] is True
    assert payload["checks"]["dynamic_api_uses_dynamic_runtime"] is True
    assert payload["checks"]["dynamic_api_depends_only_on_infra"] is True
    assert payload["checks"]["dynamic_classic_services_disabled"] is True
    assert payload["checks"]["dynamic_agent_profile_services_present"] is True


def test_compose_config_audit_rejects_classic_service_in_dynamic_default(monkeypatch):
    package_dir = _write_acme_compose_config_package()

    def fake_run(cmd, **kwargs):
        command_text = " ".join(cmd)
        if "--format json" in command_text:
            payload = {
                "services": {
                    "postgres": {},
                    "redis": {},
                    "chromadb": {},
                    "api": {
                        "command": ["python", "-m", "scripts.run_dynamic_runtime"],
                        "depends_on": {"agent-finance": {"condition": "service_started"}},
                    },
                    "agent-finance": {
                        "profiles": [],
                        "ports": [{"published": "18103", "target": 8103}],
                    },
                }
            }
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")
        if "--profile tenant-dynamic-agents" in command_text:
            return subprocess.CompletedProcess(cmd, 0, stdout="dynamic-agent-hr-policy\napi\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="postgres\nredis\nchromadb\napi\nagent-finance\n", stderr="")

    monkeypatch.setattr("src.dynamic_platform.compose_config_audit.subprocess.run", fake_run)

    report = run_compose_config_audit(
        tenant_key="acme_demo",
        config_root=CONFIG_ROOT,
        package_dir=package_dir,
    )
    payload = report.to_dict()

    assert report.ok is False
    error_codes = {error["code"] for error in payload["errors"]}
    assert "compose_config_dynamic_default_includes_classic_services" in error_codes
    assert "compose_config_dynamic_api_depends_on_classic_service" in error_codes
    assert "compose_config_classic_service_not_disabled" in error_codes


def test_tenant_cli_compose_config_audit_reports_summary(monkeypatch, capsys):
    package_dir = _write_acme_compose_config_package()

    def fake_run(cmd, **kwargs):
        command_text = " ".join(cmd)
        if "--format json" in command_text:
            payload = {
                "services": {
                    "postgres": {},
                    "redis": {},
                    "chromadb": {},
                    "api": {
                        "command": ["python", "-m", "scripts.run_dynamic_runtime"],
                        "depends_on": {
                            "postgres": {"condition": "service_started"},
                            "redis": {"condition": "service_started"},
                            "chromadb": {"condition": "service_started"},
                        },
                    },
                    "agent-finance": {
                        "profiles": ["disabled-classic-runtime"],
                        "ports": [],
                    },
                    "dynamic-agent-hr-policy": {
                        "profiles": ["tenant-dynamic-agents"],
                    },
                }
            }
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")
        if "--profile tenant-dynamic-agents" in command_text:
            return subprocess.CompletedProcess(cmd, 0, stdout="dynamic-agent-hr-policy\npostgres\nredis\nchromadb\napi\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="postgres\nredis\nchromadb\napi\n", stderr="")

    monkeypatch.setattr("src.dynamic_platform.compose_config_audit.subprocess.run", fake_run)

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "compose-config-audit",
            "--tenant",
            "acme_demo",
            "--package-dir",
            str(package_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Compose config audit: OK" in captured.out
    assert "Default services: postgres, redis, chromadb, api" in captured.out
    assert "dynamic_api_uses_dynamic_runtime: yes" in captured.out


def test_runtime_smoke_readiness_accepts_cached_image(monkeypatch):
    package_dir = Path("tmp/test_runtime_smoke_ready/acme_demo_package")
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "tenant.env").write_text("A2A_IMAGE_REF=local/acme-demo:test\n", encoding="utf-8")

    class FakeComposeReport:
        ok = True
        default_services = ["postgres", "redis", "chromadb", "api"]
        dynamic_agent_services = ["dynamic-agent-hr-policy"]
        errors = []

    monkeypatch.setattr(
        "src.dynamic_platform.runtime_smoke_readiness.run_compose_config_audit",
        lambda **kwargs: FakeComposeReport(),
    )

    def fake_run(cmd, **kwargs):
        assert cmd[:3] == ["docker", "image", "inspect"]
        payload = [{"Id": "sha256:test-image", "Created": "2026-05-24T00:00:00Z"}]
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr("src.dynamic_platform.runtime_smoke_readiness.subprocess.run", fake_run)

    report = run_runtime_smoke_readiness(
        tenant_key="acme_demo",
        config_root=CONFIG_ROOT,
        package_dir=package_dir,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["status"] == "ready_for_no_download_smoke"
    assert payload["image_ref"] == "local/acme-demo:test"
    assert all(gate["ok"] for gate in payload["gates"])
    assert any("--no-build --pull never" in command for command in payload["suggested_commands"])
    assert any("--profile tenant-dynamic-agents" in command for command in payload["suggested_commands"])


def test_runtime_smoke_readiness_blocks_when_image_is_missing(monkeypatch):
    package_dir = Path("tmp/test_runtime_smoke_missing/acme_demo_package")
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "tenant.env").write_text("A2A_IMAGE_REF=missing/acme-demo:test\n", encoding="utf-8")

    class FakeComposeReport:
        ok = True
        default_services = ["postgres", "redis", "chromadb", "api"]
        dynamic_agent_services = ["dynamic-agent-hr-policy"]
        errors = []

    monkeypatch.setattr(
        "src.dynamic_platform.runtime_smoke_readiness.run_compose_config_audit",
        lambda **kwargs: FakeComposeReport(),
    )
    monkeypatch.setattr(
        "src.dynamic_platform.runtime_smoke_readiness.subprocess.run",
        lambda cmd, **kwargs: subprocess.CompletedProcess(cmd, 1, stdout="", stderr="No such image"),
    )

    report = run_runtime_smoke_readiness(
        tenant_key="acme_demo",
        config_root=CONFIG_ROOT,
        package_dir=package_dir,
    )

    assert report.ok is False
    assert report.status == "runtime_smoke_blocked"
    assert any("required Docker image is not present locally" in blocker for blocker in report.blockers)


def test_runtime_smoke_readiness_reports_docker_access_blocker(monkeypatch):
    package_dir = Path("tmp/test_runtime_smoke_docker_blocked/acme_demo_package")
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "tenant.env").write_text("A2A_IMAGE_REF=local/acme-demo:test\n", encoding="utf-8")

    class FakeComposeReport:
        ok = True
        default_services = ["postgres", "redis", "chromadb", "api"]
        dynamic_agent_services = ["dynamic-agent-hr-policy"]
        errors = []

    monkeypatch.setattr(
        "src.dynamic_platform.runtime_smoke_readiness.run_compose_config_audit",
        lambda **kwargs: FakeComposeReport(),
    )
    monkeypatch.setattr(
        "src.dynamic_platform.runtime_smoke_readiness.subprocess.run",
        lambda cmd, **kwargs: subprocess.CompletedProcess(cmd, 1, stdout="", stderr="permission denied"),
    )

    report = run_runtime_smoke_readiness(
        tenant_key="acme_demo",
        config_root=CONFIG_ROOT,
        package_dir=package_dir,
    )
    payload = report.to_dict()

    assert report.ok is False
    assert payload["gates"][2]["detail"]["inspect_available"] is False
    assert any("Docker image inspect is not available" in blocker for blocker in report.blockers)


def test_tenant_cli_runtime_smoke_readiness_reports_summary(monkeypatch, capsys):
    package_dir = Path("tmp/test_runtime_smoke_cli/acme_demo_package")
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "tenant.env").write_text("A2A_IMAGE_REF=local/acme-demo:test\n", encoding="utf-8")

    class FakeComposeReport:
        ok = True
        default_services = ["postgres", "redis", "chromadb", "api"]
        dynamic_agent_services = ["dynamic-agent-hr-policy"]
        errors = []

    monkeypatch.setattr(
        "src.dynamic_platform.runtime_smoke_readiness.run_compose_config_audit",
        lambda **kwargs: FakeComposeReport(),
    )
    monkeypatch.setattr(
        "src.dynamic_platform.runtime_smoke_readiness.subprocess.run",
        lambda cmd, **kwargs: subprocess.CompletedProcess(
            cmd,
            0,
            stdout=json.dumps([{"Id": "sha256:test-image", "Created": "2026-05-24T00:00:00Z"}]),
            stderr="",
        ),
    )

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-smoke-readiness",
            "--tenant",
            "acme_demo",
            "--package-dir",
            str(package_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Runtime smoke readiness: OK" in captured.out
    assert "Status: ready_for_no_download_smoke" in captured.out
    assert "tenant_package_exists: OK" in captured.out
    assert "--pull never" in captured.out


def test_runtime_container_audit_accepts_dynamic_api_container(monkeypatch):
    class FakeComposeReport:
        ok = True
        default_services = ["postgres", "redis", "chromadb", "api"]
        dynamic_agent_services = ["dynamic-agent-hr-policy"]
        errors = []

    monkeypatch.setattr(
        "src.dynamic_platform.runtime_container_audit.run_compose_config_audit",
        lambda **kwargs: FakeComposeReport(),
    )

    def fake_run(cmd, **kwargs):
        command_text = " ".join(cmd)
        if "docker ps" in command_text:
            return subprocess.CompletedProcess(
                cmd,
                0,
                stdout="acme_demo_api\nacme_demo_redis\nacme_demo_agent_hr_policy\n",
                stderr="",
            )
        if cmd[:2] == ["docker", "inspect"]:
            name = cmd[-1]
            if name == "acme_demo_api":
                service = "api"
                image = "university_support_system-dynamic-local:latest"
                command = ["python", "-m", "scripts.run_dynamic_runtime"]
            elif name == "acme_demo_agent_hr_policy":
                service = "dynamic-agent-hr-policy"
                image = "university_support_system-dynamic-local:latest"
                command = ["python", "-m", "scripts.run_generic_agent_host"]
            else:
                service = "redis"
                image = "redis:7-alpine"
                command = ["redis-server"]
            payload = [
                {
                    "Config": {
                        "Image": image,
                        "Cmd": command,
                        "Labels": {
                            "dynamic-platform.tenant": "acme_demo",
                            "com.docker.compose.service": service,
                        },
                    },
                    "State": {"Status": "running"},
                }
            ]
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")
        raise AssertionError(command_text)

    monkeypatch.setattr("src.dynamic_platform.runtime_container_audit.subprocess.run", fake_run)

    report = run_runtime_container_audit(
        tenant_key="acme_demo",
        config_root=CONFIG_ROOT,
        package_dir=Path("tmp/tenant_packages/acme_demo"),
        expected_image="university_support_system-dynamic-local:latest",
        allow_dynamic_agents=True,
    )

    assert report.ok is True
    assert [container.name for container in report.containers] == [
        "acme_demo_api",
        "acme_demo_redis",
        "acme_demo_agent_hr_policy",
    ]


def test_runtime_container_audit_rejects_classic_orphan_and_wrong_api_command(monkeypatch):
    class FakeComposeReport:
        ok = True
        default_services = ["postgres", "redis", "chromadb", "api"]
        dynamic_agent_services = []
        errors = []

    monkeypatch.setattr(
        "src.dynamic_platform.runtime_container_audit.run_compose_config_audit",
        lambda **kwargs: FakeComposeReport(),
    )

    def fake_run(cmd, **kwargs):
        command_text = " ".join(cmd)
        if "docker ps" in command_text:
            return subprocess.CompletedProcess(cmd, 0, stdout="acme_demo_api\nacme_demo_agent_finance\n", stderr="")
        if cmd[:2] == ["docker", "inspect"]:
            name = cmd[-1]
            service = "api" if name == "acme_demo_api" else "agent-finance"
            command = ["python", "-m", "uvicorn", "src.api.main:app"] if service == "api" else ["python", "-m", "scripts.run_agent_service"]
            payload = [
                {
                    "Config": {
                        "Image": "university_support_system-app:latest",
                        "Cmd": command,
                        "Labels": {
                            "dynamic-platform.tenant": "acme_demo",
                            "com.docker.compose.service": service,
                        },
                    },
                    "State": {"Status": "running"},
                }
            ]
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")
        raise AssertionError(command_text)

    monkeypatch.setattr("src.dynamic_platform.runtime_container_audit.subprocess.run", fake_run)

    report = run_runtime_container_audit(
        tenant_key="acme_demo",
        config_root=CONFIG_ROOT,
        package_dir=Path("tmp/tenant_packages/acme_demo"),
        expected_image="university_support_system-dynamic-local:latest",
    )
    error_codes = {error.code for error in report.errors}

    assert report.ok is False
    assert "dynamic_api_container_wrong_command" in error_codes
    assert "dynamic_api_container_wrong_image" in error_codes
    assert "classic_container_present_in_dynamic_runtime" in error_codes
    assert "unexpected_tenant_container_service" in error_codes


def test_tenant_cli_runtime_container_audit_reports_summary(monkeypatch, capsys):
    class FakeComposeReport:
        ok = True
        default_services = ["postgres", "redis", "chromadb", "api"]
        dynamic_agent_services = []
        errors = []

    monkeypatch.setattr(
        "src.dynamic_platform.runtime_container_audit.run_compose_config_audit",
        lambda **kwargs: FakeComposeReport(),
    )

    def fake_run(cmd, **kwargs):
        command_text = " ".join(cmd)
        if "docker ps" in command_text:
            return subprocess.CompletedProcess(cmd, 0, stdout="acme_demo_api\n", stderr="")
        if cmd[:2] == ["docker", "inspect"]:
            payload = [
                {
                    "Config": {
                        "Image": "university_support_system-dynamic-local:latest",
                        "Cmd": ["python", "-m", "scripts.run_dynamic_runtime"],
                        "Labels": {
                            "dynamic-platform.tenant": "acme_demo",
                            "com.docker.compose.service": "api",
                        },
                    },
                    "State": {"Status": "running"},
                }
            ]
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")
        raise AssertionError(command_text)

    monkeypatch.setattr("src.dynamic_platform.runtime_container_audit.subprocess.run", fake_run)

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-container-audit",
            "--tenant",
            "acme_demo",
            "--package-dir",
            "tmp/tenant_packages/acme_demo",
            "--expected-image",
            "university_support_system-dynamic-local:latest",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Runtime container audit: OK" in captured.out
    assert "acme_demo_api" in captured.out


def test_dynamic_query_smoke_calls_running_runtime_with_utf8_payload(monkeypatch):
    captured: dict[str, object] = {}

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return json.dumps(
                {
                    "tenant_key": "acme_demo",
                    "answer": "ACME kaynaklarına göre VPN erişimi için IT destek portalında talep açılır.",
                    "answer_status": "answered",
                    "selected_capabilities": ["it_ticket_guidance"],
                    "agents": ["it_support"],
                    "sources": ["acme_it_knowledge_base"],
                    "final_owner": "it_support",
                },
                ensure_ascii=False,
            ).encode("utf-8")

    def fake_urlopen(request, timeout):
        captured["timeout"] = timeout
        captured["url"] = request.full_url
        captured["body"] = request.data.decode("utf-8")
        return FakeResponse()

    monkeypatch.setattr("src.dynamic_platform.runtime_query_smoke.urlopen", fake_urlopen)

    report = run_dynamic_query_smoke(
        tenant_key="acme_demo",
        base_url="http://127.0.0.1:18000",
        query="VPN erişimi nasıl açılır?",
    )

    assert report.ok is True
    assert report.answer_status == "answered"
    assert report.sources == ["acme_it_knowledge_base"]
    assert "VPN erişimi" in report.answer_preview
    assert captured["url"] == "http://127.0.0.1:18000/dynamic/query"
    assert "VPN erişimi nasıl açılır?" in captured["body"]


def test_tenant_cli_runtime_query_smoke_reports_summary(monkeypatch, capsys):
    class FakeReport:
        ok = True

        def to_dict(self):
            return {
                "tenant_key": "city_demo",
                "ok": True,
                "status": "ok",
                "endpoint": "http://127.0.0.1:28000/dynamic/query",
                "http_status": 200,
                "latency_ms": 3.2,
                "answer_status": "answered",
                "final_owner": "citizen_services",
                "selected_capabilities": ["service_application"],
                "agents": ["citizen_services"],
                "sources": ["city_service_policy_documents"],
                "query": "Ruhsat ön başvurusu nasıl yapılır?",
                "answer_preview": "Ruhsat ön başvurusu için başvuru formu gerekir.",
                "errors": [],
                "warnings": [],
                "notes": ["no mutation"],
            }

    monkeypatch.setattr("scripts.tenant.run_dynamic_query_smoke", lambda **kwargs: FakeReport())

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "runtime-query-smoke",
            "--tenant",
            "city_demo",
            "--query",
            "Ruhsat ön başvurusu nasıl yapılır?",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Runtime query smoke: OK" in captured.out
    assert "city_service_policy_documents" in captured.out
    assert "Ruhsat ön başvurusu" in captured.out


def test_tenant_cli_compose_isolation_audit_reports_ok(capsys):
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    output_dir = Path("tmp/dynamic_platform_compose_isolation_cli_test")
    write_tenant_package(
        bundle,
        config_root=CONFIG_ROOT,
        output_dir=output_dir,
        require_quality_gates=False,
        force=True,
    )

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "compose-isolation-audit",
            "--tenant",
            "acme_demo",
            "--package-dir",
            str(output_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Compose isolation audit: OK" in captured.out
    assert "container_names_tenant_prefixed: yes" in captured.out


def test_tenant_readiness_report_combines_quality_runtime_and_docker_status():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    report = build_tenant_readiness_report(bundle, config_root=CONFIG_ROOT, env_file=".env.example")
    payload = report.to_dict()

    assert report.ok is True
    assert payload["profile_ready"] is True
    assert payload["runtime_env_ready"] is True
    assert payload["docker_single_instance_ready"] is True
    assert payload["docker_side_by_side_ready"] is False


def test_tenant_cli_readiness_for_omu(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "readiness",
            "--tenant",
            "omu",
            "--env-file",
            ".env.example",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Readiness: OK" in captured.out
    assert "Docker side-by-side ready: no" in captured.out


def test_tenant_bootstrap_plan_reports_setup_coverage_without_runtime_calls():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = build_tenant_bootstrap_plan(bundle)
    payload = report.to_dict()

    assert report.ok is True
    assert payload["summary"]["domain_pack"] == "corporate_support"
    assert payload["summary"]["agent_pack"] == "corporate_hr_it_support"
    assert payload["summary"]["shadow_fixture_exists"] is True
    assert payload["capability_coverage"]["capabilities_without_agent"] == []
    assert payload["capability_coverage"]["capabilities_without_enabled_source"] == []
    assert payload["source_family_coverage"]["missing_source_families"] == []
    assert {step["step_id"] for step in payload["steps"]} == {
        "profile_contract",
        "entity_registry",
        "source_catalog",
        "decision_fixture",
        "offline_package",
        "handoff_gate",
    }


def test_tenant_cli_bootstrap_plan_reports_safe_next_commands(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "bootstrap-plan", "--tenant", "city_demo"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Bootstrap plan: OK" in captured.out
    assert "Runtime strategy: dynamic_shadow" in captured.out
    assert "handoff-readiness" in captured.out


def test_tenant_package_files_are_offline_handoff_artifacts():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    files = build_tenant_package_files(bundle, config_root=CONFIG_ROOT)

    assert "tenant.env" in files
    assert "TENANT_KEY=omu" in files["tenant.env"]
    assert "readiness.json" in files
    assert "bootstrap_plan.json" in files
    assert "docker_plan.json" in files
    assert "onboarding_preview.md" in files
    assert "capability_contract_matrix.json" in files
    assert "source_ingestion_plan.json" in files
    assert "retrieval_contract.json" in files
    assert "model_runtime_contract.json" in files
    assert "runtime_adapter_contract.json" in files
    assert "runtime_adapter_draft_preview.json" in files
    assert "runtime_adapter_implementation_plan.json" in files
    assert "runtime_isolation_contract.json" in files
    assert "runtime_namespace_preview.json" in files
    assert "secrets_contract.json" in files
    assert "tenant.secrets.example.env" in files
    assert "adapter_handoff_checklist.json" in files
    assert "cache_strategy.json" in files
    assert "compose_isolation_audit.json" in files
    assert "portability_audit.json" in files
    assert "handoff_index.json" in files
    assert "genericity_audit.json" in files
    assert "registry_snapshot.json" in files
    assert "config_snapshot.json" in files
    assert "shadow_runtime_replay.json" in files
    assert "package_manifest.json" in files
    assert "compose_launch_manifest.json" in files
    assert "docker-compose.tenant.override.draft.yml" in files
    assert "COMPOSE_NOTES.md" in files
    assert "servis baslatmaz" in files["README.md"]
    assert "override dosyasi yalniz taslaktir" in files["README.md"]
    assert "Slack'e otomatik mesaj gondermez" in files["onboarding_preview.md"]
    assert "profile_contract" in files["bootstrap_plan.json"]
    assert "graduation_akts" in files["capability_contract_matrix.json"]
    assert "runtime_uploaded_context_only" in files["source_ingestion_plan.json"]
    assert "local_source_retrieval_service_no_download_smoke" in files["retrieval_contract.json"]
    assert "seroe/bge-reranker-v2-m3-turkish-triplet" in files["model_runtime_contract.json"]
    assert '"fp16_allowed_only_on_cuda": true' in files["model_runtime_contract.json"]
    assert "not_wired" in files["runtime_adapter_contract.json"]
    assert "shadow_decision_only" in files["runtime_adapter_draft_preview.json"]
    assert "guarded_boundary_available_not_wired" in files["runtime_adapter_implementation_plan.json"]
    assert "tenant:omu:answer_cache:" in files["runtime_isolation_contract.json"]
    assert "tenant:omu:answer_cache:" in files["runtime_namespace_preview.json"]
    assert '"secret_values_allowed_in_package": false' in files["secrets_contract.json"]
    assert "OPENAI_API_KEY=" in files["tenant.secrets.example.env"]
    assert "OPENAI_API_KEY=" not in files["tenant.env"]
    assert "SLACK_BOT_TOKEN=" not in files["tenant.env"]
    assert "prepared_not_wired" in files["adapter_handoff_checklist.json"]
    cache_strategy = json.loads(files["cache_strategy.json"])
    assert cache_strategy["model_cache"]["default_host_dir"] == "./data/models"
    assert cache_strategy["offline_package_generation"]["downloads_models"] is False
    assert '"container_names_tenant_prefixed": true' in files["compose_isolation_audit.json"]
    assert '"no_cross_tenant_identifier_leakage": true' in files["portability_audit.json"]
    assert "offline_prepared_not_wired" in files["handoff_index.json"]
    assert "portability-audit" in files["handoff_index.json"]
    assert "compose-isolation-audit" in files["handoff_index.json"]
    assert "compose-config-audit" in files["handoff_index.json"]
    assert "runtime-smoke-readiness" in files["handoff_index.json"]
    assert "runtime-query-smoke" in files["handoff_index.json"]
    acme_files = build_tenant_package_files(load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT), config_root=CONFIG_ROOT)
    assert "image: ${A2A_IMAGE_REF:-university_support_system-app:latest}" in acme_files["docker-compose.tenant.override.draft.yml"]
    assert "scripts.run_dynamic_runtime" in acme_files["docker-compose.tenant.override.draft.yml"]
    assert '"ok": true' in files["genericity_audit.json"]
    assert '"tenant_count": 3' in files["registry_snapshot.json"]
    assert '"tenant_profile"' in files["config_snapshot.json"]
    assert "shadow_only_runtime_not_wired" in files["shadow_runtime_replay.json"]
    manifest = json.loads(files["package_manifest.json"])
    assert manifest["safety_status"] == "offline_handoff_only"
    assert manifest["dynamic_live_binding_allowed"] is False
    assert any(record["path"] == "tenant.env" and len(record["sha256"]) == 64 for record in manifest["files"])


def test_tenant_package_writer_creates_expected_files():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    output_dir = Path("tmp/dynamic_platform_package_test")
    for name in (
        "tenant.env",
        "runtime_plan.json",
        "docker_plan.json",
        "readiness.json",
        "bootstrap_plan.json",
        "validation.json",
        "execution_plan.json",
        "capability_contract_matrix.json",
        "source_audit.json",
        "source_ingestion_plan.json",
        "retrieval_contract.json",
        "model_runtime_contract.json",
        "runtime_adapter_contract.json",
        "runtime_adapter_draft_preview.json",
        "runtime_adapter_implementation_plan.json",
        "runtime_isolation_contract.json",
        "runtime_namespace_preview.json",
        "secrets_contract.json",
        "tenant.secrets.example.env",
        "adapter_handoff_checklist.json",
        "cache_strategy.json",
        "compose_isolation_audit.json",
        "portability_audit.json",
        "handoff_index.json",
        "genericity_audit.json",
        "registry_snapshot.json",
        "config_snapshot.json",
        "shadow_runtime_replay.json",
        "onboarding_preview.md",
        "package_manifest.json",
        "compose_launch_manifest.json",
        "docker-compose.tenant.override.draft.yml",
        "COMPOSE_NOTES.md",
        "README.md",
    ):
        (output_dir / name).unlink(missing_ok=True)

    result = write_tenant_package(
        bundle,
        config_root=CONFIG_ROOT,
        output_dir=output_dir,
        require_quality_gates=False,
        force=True,
    )

    assert (output_dir / "tenant.env").exists()
    assert (output_dir / "readiness.json").exists()
    assert (output_dir / "bootstrap_plan.json").exists()
    assert (output_dir / "capability_contract_matrix.json").exists()
    assert (output_dir / "source_ingestion_plan.json").exists()
    assert (output_dir / "retrieval_contract.json").exists()
    assert (output_dir / "model_runtime_contract.json").exists()
    assert (output_dir / "runtime_adapter_contract.json").exists()
    assert (output_dir / "runtime_adapter_draft_preview.json").exists()
    assert (output_dir / "runtime_adapter_implementation_plan.json").exists()
    assert (output_dir / "runtime_isolation_contract.json").exists()
    assert (output_dir / "runtime_namespace_preview.json").exists()
    assert (output_dir / "secrets_contract.json").exists()
    assert (output_dir / "tenant.secrets.example.env").exists()
    assert (output_dir / "adapter_handoff_checklist.json").exists()
    assert (output_dir / "cache_strategy.json").exists()
    assert (output_dir / "compose_isolation_audit.json").exists()
    assert (output_dir / "portability_audit.json").exists()
    assert (output_dir / "handoff_index.json").exists()
    assert (output_dir / "genericity_audit.json").exists()
    assert (output_dir / "registry_snapshot.json").exists()
    assert (output_dir / "config_snapshot.json").exists()
    assert (output_dir / "shadow_runtime_replay.json").exists()
    assert (output_dir / "onboarding_preview.md").exists()
    assert (output_dir / "package_manifest.json").exists()
    assert (output_dir / "compose_launch_manifest.json").exists()
    tenant_env = (output_dir / "tenant.env").read_text(encoding="utf-8")
    assert "TENANT_KEY=acme_demo" in tenant_env
    assert "ACME_DEMO_API_PORT=18000" in tenant_env
    assert "MODEL_CACHE_HOST_DIR=./data/models" in tenant_env
    assert "OPENAI_API_KEY=" not in tenant_env
    assert "SLACK_BOT_TOKEN=" not in tenant_env
    assert "OPENAI_API_KEY=" in (output_dir / "tenant.secrets.example.env").read_text(encoding="utf-8")
    assert "draft_do_not_run" in (output_dir / "compose_launch_manifest.json").read_text(encoding="utf-8")
    assert str(output_dir / "README.md") in result.files


def test_tenant_cli_package_dry_artifacts_without_runtime_side_effects(capsys):
    output_dir = Path("tmp/dynamic_platform_cli_package_test")
    for name in (
        "tenant.env",
        "runtime_plan.json",
        "docker_plan.json",
        "readiness.json",
        "bootstrap_plan.json",
        "validation.json",
        "execution_plan.json",
        "capability_contract_matrix.json",
        "source_audit.json",
        "source_ingestion_plan.json",
        "retrieval_contract.json",
        "model_runtime_contract.json",
        "runtime_adapter_contract.json",
        "runtime_adapter_draft_preview.json",
        "runtime_adapter_implementation_plan.json",
        "runtime_isolation_contract.json",
        "runtime_namespace_preview.json",
        "secrets_contract.json",
        "tenant.secrets.example.env",
        "adapter_handoff_checklist.json",
        "cache_strategy.json",
        "compose_isolation_audit.json",
        "portability_audit.json",
        "handoff_index.json",
        "genericity_audit.json",
        "registry_snapshot.json",
        "config_snapshot.json",
        "shadow_runtime_replay.json",
        "onboarding_preview.md",
        "package_manifest.json",
        "compose_launch_manifest.json",
        "docker-compose.tenant.override.draft.yml",
        "COMPOSE_NOTES.md",
        "README.md",
    ):
        (output_dir / name).unlink(missing_ok=True)
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "package",
            "--tenant",
            "acme_demo",
            "--output-dir",
            str(output_dir),
            "--allow-missing-shadow",
            "--force",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Package directory" in captured.out
    assert (output_dir / "tenant.env").exists()
    assert (output_dir / "bootstrap_plan.json").exists()
    assert (output_dir / "capability_contract_matrix.json").exists()
    assert (output_dir / "source_ingestion_plan.json").exists()
    assert (output_dir / "retrieval_contract.json").exists()
    assert (output_dir / "model_runtime_contract.json").exists()
    assert (output_dir / "runtime_adapter_contract.json").exists()
    assert (output_dir / "runtime_adapter_draft_preview.json").exists()
    assert (output_dir / "runtime_adapter_implementation_plan.json").exists()
    assert (output_dir / "runtime_isolation_contract.json").exists()
    assert (output_dir / "runtime_namespace_preview.json").exists()
    assert (output_dir / "secrets_contract.json").exists()
    assert (output_dir / "tenant.secrets.example.env").exists()
    assert (output_dir / "adapter_handoff_checklist.json").exists()
    assert (output_dir / "cache_strategy.json").exists()
    assert (output_dir / "compose_isolation_audit.json").exists()
    assert (output_dir / "portability_audit.json").exists()
    assert (output_dir / "handoff_index.json").exists()
    assert (output_dir / "genericity_audit.json").exists()
    assert (output_dir / "registry_snapshot.json").exists()
    assert (output_dir / "config_snapshot.json").exists()
    assert (output_dir / "shadow_runtime_replay.json").exists()
    assert (output_dir / "onboarding_preview.md").exists()
    assert (output_dir / "package_manifest.json").exists()
    assert (output_dir / "docker-compose.tenant.override.draft.yml").exists()
    assert str(output_dir / "tenant.env") in (output_dir / "README.md").read_text(encoding="utf-8")


def test_package_portfolio_audit_checks_all_generated_tenant_packages():
    package_root = Path("tmp/dynamic_platform_package_audit_all_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    report = run_tenant_package_portfolio_audit(
        config_root=CONFIG_ROOT,
        package_root=package_root,
        require_quality_gates=False,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["summary"]["tenant_count"] == 3
    assert payload["summary"]["failed"] == 0
    assert all(
        record["safety_audit"]["checks"]["package_config_snapshot_hashes_match"]
        for record in payload["records"]
    )
    assert all(record["safety_audit"]["checks"]["package_compose_isolation_ok"] for record in payload["records"])
    assert all(record["safety_audit"]["checks"]["package_handoff_index_offline_safe"] for record in payload["records"])
    assert all(record["safety_audit"]["checks"]["package_portability_audit_ok"] for record in payload["records"])


def test_tenant_cli_package_audit_all_reports_generated_packages(capsys):
    package_root = Path("tmp/dynamic_platform_package_audit_cli_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "package-audit-all",
            "--package-root",
            str(package_root),
            "--allow-missing-shadow",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tenant package portfolio audit: OK" in captured.out
    assert "Packages: 3/3 passed" in captured.out
    assert "package_config_snapshot_hashes_match: yes" in captured.out


def test_handoff_readiness_combines_registry_packages_and_adapter_smoke():
    package_root = Path("tmp/dynamic_platform_handoff_readiness_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    report = run_handoff_readiness(
        config_root=CONFIG_ROOT,
        package_root=package_root,
        require_quality_gates=False,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["summary"]["tenant_count"] == 3
    assert payload["summary"]["registry_ok"] is True
    assert payload["summary"]["portability_ok"] is True
    assert payload["summary"]["package_audit_ok"] is True
    assert payload["summary"]["package_compose_isolation_ok"] is True
    assert payload["summary"]["adapter_draft_smoke_passed"] == 3
    assert all(record["preview"]["answer"] == "" for record in payload["adapter_draft_smoke"])
    assert all(record["live_refusal"]["answer_status"] == "unsafe_to_answer" for record in payload["adapter_draft_smoke"])


def test_tenant_cli_handoff_readiness_reports_offline_status(capsys):
    package_root = Path("tmp/dynamic_platform_handoff_readiness_cli_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "handoff-readiness",
            "--package-root",
            str(package_root),
            "--allow-missing-shadow",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dynamic platform handoff readiness: OK" in captured.out
    assert "portability=OK" in captured.out
    assert "compose_iso=OK" in captured.out
    assert "adapter_smoke=3/3" in captured.out
    assert "preview=shadow_decision_only" in captured.out


def test_dynamic_platform_completion_report_combines_final_offline_gates():
    package_root = Path("tmp/dynamic_platform_completion_report_packages_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    report = run_dynamic_platform_completion_report(
        config_root=CONFIG_ROOT,
        package_root=package_root,
        output_root="tmp/dynamic_platform_completion_report_test",
        require_quality_gates=False,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["status"] == "offline_handoff_ready"
    assert payload["summary"]["offline_completion_percent"] == 100.0
    assert payload["summary"]["live_runtime_authorized"] is False
    assert payload["summary"]["classic_runtime_import_isolated"] is True
    assert {gate["gate_id"] for gate in payload["gates"]} == {
        "registry_catalog",
        "genericity_audit",
        "portfolio_audit",
        "portability_audit",
        "package_audit",
        "handoff_readiness",
        "tenant_creation_rehearsal",
        "pack_creation_rehearsal",
    }
    assert all(gate["ok"] for gate in payload["gates"])
    assert any("Live dynamic Slack/API/router adapter" in item for item in payload["blocked_live_items"])
    assert payload["optional_no_download_smoke_commands"] == [
        "python -m scripts.tenant runtime-query-smoke --tenant acme_demo",
        "python -m scripts.tenant runtime-query-smoke --tenant city_demo",
    ]


def test_tenant_cli_completion_report_reports_offline_handoff_ready(capsys):
    package_root = Path("tmp/dynamic_platform_completion_report_cli_packages_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "completion-report",
            "--package-root",
            str(package_root),
            "--output-root",
            "tmp/dynamic_platform_completion_report_cli_test",
            "--allow-missing-shadow",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dynamic platform completion: OK" in captured.out
    assert "Status: offline_handoff_ready" in captured.out
    assert "tenant_creation_rehearsal: OK" in captured.out
    assert "pack_creation_rehearsal: OK" in captured.out
    assert "live_authorized=no" in captured.out
    assert "Optional no-download smoke commands:" in captured.out
    assert "runtime-query-smoke --tenant acme_demo" in captured.out


def test_dynamic_platform_preflight_prepares_manual_compose_config_gate():
    package_root = Path("tmp/dynamic_platform_preflight_packages_test")
    output_root = Path("tmp/dynamic_platform_preflight_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    report = run_dynamic_platform_preflight(
        config_root=CONFIG_ROOT,
        package_root=package_root,
        output_root=output_root,
        require_quality_gates=False,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["status"] == "ready_for_manual_compose_config"
    assert payload["summary"]["manual_docker_config_required"] is True
    assert payload["summary"]["docker_started"] is False
    assert payload["summary"]["build_or_pull_run"] is False
    assert payload["summary"]["live_runtime_authorized"] is False
    assert {record["tenant_key"] for record in payload["tenant_compose_drafts"]} == {
        "omu",
        "acme_demo",
        "city_demo",
    }
    assert all(record["checks"]["override_uses_env_file_override"] for record in payload["tenant_compose_drafts"])
    assert all(record["checks"]["override_uses_ports_override"] for record in payload["tenant_compose_drafts"])
    assert all(record["checks"]["manifest_disables_root_env_file"] for record in payload["tenant_compose_drafts"])
    assert all(record["checks"]["tenant_env_contains_suggested_overrides"] for record in payload["tenant_compose_drafts"])
    assert all("docker compose" in command for command in payload["manual_docker_config_checks"])
    assert all(" config --services" in command for command in payload["manual_docker_config_checks"])
    assert any(gate["gate_id"] == "manual_docker_config_required" for gate in payload["gates"])
    assert (output_root / "preflight_report.json").exists()
    assert (output_root / "manual_docker_config_checks.ps1").exists()
    assert (output_root / "README.md").exists()


def test_tenant_cli_preflight_reports_manual_compose_config_gate(capsys):
    package_root = Path("tmp/dynamic_platform_preflight_cli_packages_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "preflight",
            "--package-root",
            str(package_root),
            "--output-root",
            "tmp/dynamic_platform_preflight_cli_test",
            "--allow-missing-shadow",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dynamic platform preflight: OK" in captured.out
    assert "Status: ready_for_manual_compose_config" in captured.out
    assert "Manual Docker config required: yes" in captured.out
    assert "Docker started: no" in captured.out
    assert "Build or pull run: no" in captured.out
    assert "Live runtime authorized: no" in captured.out
    assert "manual_docker_config_required: OK" in captured.out


def test_pilot_readiness_allows_no_secret_smoke_but_not_live_binding():
    package_root = Path("tmp/dynamic_platform_pilot_readiness_packages_test")
    output_root = Path("tmp/dynamic_platform_pilot_readiness_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = run_tenant_pilot_readiness(
        bundle,
        config_root=CONFIG_ROOT,
        package_root=package_root,
        output_root=output_root,
        secrets_env_file=package_root / "acme_demo" / "tenant.env",
        mode="no_secret_smoke",
        require_quality_gates=False,
    )
    payload = report.to_dict()

    assert report.ok is True
    assert payload["status"] == "ready_for_no_secret_smoke"
    assert payload["live_binding_allowed"] is False
    assert payload["summary"]["docker_started"] is False
    assert payload["summary"]["build_or_pull_run"] is False
    assert any(gate["gate_id"] == "adapter_live_binding_blocked" and gate["ok"] for gate in payload["gates"])
    assert any("not_user_facing" in warning for warning in payload["warnings"])
    assert (output_root / "acme_demo" / "no_secret_smoke" / "pilot_readiness_report.json").exists()


def test_pilot_readiness_blocks_dynamic_pilot_until_adapter_and_secrets_are_ready():
    package_root = Path("tmp/dynamic_platform_pilot_readiness_blocked_packages_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    report = run_tenant_pilot_readiness(
        bundle,
        config_root=CONFIG_ROOT,
        package_root=package_root,
        output_root="tmp/dynamic_platform_pilot_readiness_blocked_test",
        secrets_env_file=package_root / "acme_demo" / "tenant.env",
        mode="dynamic_pilot",
        include_slack=True,
        require_quality_gates=False,
    )
    payload = report.to_dict()

    assert report.ok is False
    assert payload["status"] == "pilot_blocked_adapter_not_wired"
    assert payload["live_binding_allowed"] is False
    assert any("dynamic_runtime_adapter_not_wired" in blocker for blocker in payload["blockers"])
    assert any("secret_group_not_ready" in blocker for blocker in payload["blockers"])
    assert any(gate["gate_id"] == "adapter_live_binding_ready" and not gate["ok"] for gate in payload["gates"])


def test_tenant_cli_pilot_readiness_reports_no_secret_smoke_status(capsys):
    package_root = Path("tmp/dynamic_platform_pilot_readiness_cli_packages_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "pilot-readiness",
            "--tenant",
            "acme_demo",
            "--mode",
            "no_secret_smoke",
            "--package-root",
            str(package_root),
            "--output-root",
            "tmp/dynamic_platform_pilot_readiness_cli_test",
            "--secrets-env-file",
            str(package_root / "acme_demo" / "tenant.env"),
            "--allow-missing-shadow",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Pilot readiness: OK" in captured.out
    assert "Status: ready_for_no_secret_smoke" in captured.out
    assert "Live binding allowed: no" in captured.out
    assert "adapter_live_binding_blocked: OK" in captured.out


def test_activation_checklist_summarizes_offline_ready_but_live_blocked_state():
    package_root = Path("tmp/dynamic_platform_activation_packages_test")
    secrets_dir = Path("tmp/dynamic_platform_activation_secrets_test")
    output_root = Path("tmp/dynamic_platform_activation_checklist_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    write_tenant_pilot_secret_scaffold(
        bundle,
        output_dir=secrets_dir,
        include_slack=True,
        force=True,
    )

    report = run_dynamic_activation_checklist(
        bundle,
        config_root=CONFIG_ROOT,
        package_root=package_root,
        runtime_secrets_dir=secrets_dir,
        output_root=output_root,
        include_slack=True,
        require_quality_gates=False,
    )
    payload = report.to_dict()
    steps = {step["step_id"]: step for step in payload["steps"]}

    assert report.ok is True
    assert payload["status"] == "offline_activation_ready_live_blocked"
    assert payload["live_runtime_authorized"] is False
    assert payload["summary"]["offline_preparation_percent"] == 100.0
    assert payload["summary"]["dynamic_pilot_prerequisite_percent"] == 60.0
    assert steps["pilot_secret_scaffold"]["ok"] is True
    assert steps["no_secret_smoke_readiness"]["status"] == "ready_for_no_secret_smoke"
    assert steps["dynamic_pilot_guard"]["status"] == "pilot_blocked_adapter_not_wired"
    assert steps["runtime_side_effects"]["ok"] is True
    assert any("adapter" in item.lower() for item in payload["remaining_work"])
    assert (output_root / "acme_demo" / "activation_checklist_report.json").exists()


def test_tenant_cli_activation_checklist_reports_remaining_work(capsys):
    package_root = Path("tmp/dynamic_platform_activation_cli_packages_test")
    secrets_dir = Path("tmp/dynamic_platform_activation_cli_secrets_test")
    for tenant_key in ("omu", "acme_demo", "city_demo"):
        bundle = load_tenant_bundle(tenant_key, config_root=CONFIG_ROOT)
        write_tenant_package(
            bundle,
            config_root=CONFIG_ROOT,
            output_dir=package_root / tenant_key,
            require_quality_gates=False,
            force=True,
        )
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    write_tenant_pilot_secret_scaffold(bundle, output_dir=secrets_dir, force=True)

    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "activation-checklist",
            "--tenant",
            "acme_demo",
            "--package-root",
            str(package_root),
            "--runtime-secrets-dir",
            str(secrets_dir),
            "--output-root",
            "tmp/dynamic_platform_activation_cli_test",
            "--allow-missing-shadow",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Activation checklist: OK" in captured.out
    assert "Status: offline_activation_ready_live_blocked" in captured.out
    assert "Live runtime authorized: no" in captured.out
    assert "pilot_prereq=60.0%" in captured.out
    assert "dynamic_pilot_guard: OK" in captured.out
    assert "Remaining work:" in captured.out


def test_tenant_cli_readiness_reports_missing_env_file_cleanly(capsys):
    exit_code = tenant_cli_main(
        [
            "--config-root",
            str(CONFIG_ROOT),
            "readiness",
            "--tenant",
            "omu",
            "--env-file",
            "tmp/does_not_exist.env",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Could not read env file" in captured.err


def test_dynamic_platform_is_not_imported_by_classic_runtime_modules():
    offenders: list[str] = []
    for root in CLASSIC_RUNTIME_DIRS:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "dynamic_platform" in text:
                offenders.append(str(path))

    assert offenders == []


def test_dynamic_runtime_answers_acme_with_tenant_agents_and_sources():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    runtime = DynamicRuntimeOrchestrator(bundle, project_root=Path("."))

    answer = runtime.answer(
        DynamicRuntimeQuery(
            tenant_key="acme_demo",
            query="Yillik izin politikasi nedir?",
        )
    )

    assert answer.answer_status == "answered"
    assert answer.selected_capabilities == ["leave_policy"]
    assert answer.agents == ["hr_policy"]
    assert answer.final_owner == "hr_policy"
    assert answer.sources == ["acme_hr_documents"]
    assert "ACME Teknoloji kaynaklarına göre" in answer.answer
    assert "Yıllık izin" in answer.answer
    assert "student_affairs" not in json.dumps(answer.to_dict(), ensure_ascii=False)
    assert "academic_programs" not in json.dumps(answer.to_dict(), ensure_ascii=False)


def test_dynamic_runtime_does_not_fallback_to_omu_for_unrelated_school_question():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    runtime = DynamicRuntimeOrchestrator(bundle, project_root=Path("."))

    answer = runtime.answer(
        DynamicRuntimeQuery(
            tenant_key="acme_demo",
            query="CAP basvuru tarihleri nelerdir?",
        )
    )

    assert answer.answer_status in {"needs_clarification", "not_found"}
    assert "ÇAP" not in answer.answer
    assert "01-05 Eylül" not in answer.answer
    assert "No protected classic fallback was used." in answer.safety_notes


def test_dynamic_runtime_answers_city_demo_with_public_service_agents_and_sources():
    bundle = load_tenant_bundle("city_demo", config_root=CONFIG_ROOT)
    runtime = DynamicRuntimeOrchestrator(bundle, project_root=Path("."))

    answer = runtime.answer(
        DynamicRuntimeQuery(
            tenant_key="city_demo",
            query="Ikamet belgesi basvurusu icin hangi belgeler gerekir?",
        )
    )

    assert answer.answer_status == "answered"
    assert answer.selected_capabilities == ["document_requirement", "service_application"]
    assert answer.agents == ["citizen_services"]
    assert answer.final_owner == "citizen_services"
    assert answer.sources == ["city_service_policy_documents"]
    assert "City Demo Municipality kaynaklar" in answer.answer
    assert "adres beyan formu" in answer.answer
    payload = json.dumps(answer.to_dict(), ensure_ascii=False)
    assert "student_affairs" not in payload
    assert "academic_programs" not in payload
    assert "acme_" not in payload


def test_dynamic_api_exposes_tenant_topology_and_query_surface():
    app = create_dynamic_app(tenant_key="acme_demo", config_root=str(CONFIG_ROOT), project_root=".")
    client = TestClient(app)

    health = client.get("/dynamic/health")
    assert health.status_code == 200
    health_payload = health.json()
    assert health_payload["tenant_key"] == "acme_demo"
    assert health_payload["runtime_strategy"] == "dynamic_shadow"

    topology = client.get("/dynamic/topology")
    assert topology.status_code == 200
    topology_payload = topology.json()
    assert topology_payload["tenant_key"] == "acme_demo"
    assert {agent["agent_id"] for agent in topology_payload["agents"]} >= {"hr_policy", "it_support", "payroll"}

    answer = client.post(
        "/dynamic/query",
        json={
            "query": "VPN erisim sorunu nasil cozulur?",
            "conversation_id": "api-test",
            "user_id": "tester",
        },
    )
    assert answer.status_code == 200
    answer_payload = answer.json()
    assert answer_payload["answer_status"] == "answered"
    assert answer_payload["agents"] == ["it_support"]
    assert answer_payload["sources"] == ["acme_it_knowledge_base"]
    assert "student_affairs" not in json.dumps(answer_payload, ensure_ascii=False)


def test_dynamic_api_refuses_classic_protected_tenant_answers():
    app = create_dynamic_app(tenant_key="omu", config_root=str(CONFIG_ROOT), project_root=".")
    client = TestClient(app)

    response = client.post("/dynamic/query", json={"query": "Mezuniyet icin kac AKTS gerekir?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer_status"] == "unsafe_to_answer"
    assert "classic_protected" in " ".join(payload["safety_notes"])


def test_dynamic_runtime_refuses_classic_protected_tenant():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    runtime = DynamicRuntimeOrchestrator(bundle, project_root=Path("."))

    answer = runtime.answer(
        DynamicRuntimeQuery(
            tenant_key="omu",
            query="Mezuniyet için kaç AKTS gerekir?",
        )
    )

    assert answer.answer_status == "unsafe_to_answer"
    assert "classic_protected" in " ".join(answer.safety_notes)

