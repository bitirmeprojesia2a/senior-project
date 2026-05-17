from __future__ import annotations

from pathlib import Path

from scripts.tenant import main as tenant_cli_main
from src.dynamic_platform.classic_compare import compare_bundle_to_classic
from src.dynamic_platform.decision_shadow import (
    ShadowDecisionCase,
    compare_shadow_decisions,
    default_shadow_fixture_path,
    load_shadow_decision_cases,
)
from src.dynamic_platform.loader import load_tenant_bundle
from src.dynamic_platform.quality_gates import run_quality_gates
from src.dynamic_platform.runtime_env_check import check_runtime_env, parse_env_file
from src.dynamic_platform.runtime_plan import build_runtime_launch_plan
from src.dynamic_platform.source_audit import audit_source_adapters
from src.dynamic_platform.validator import build_execution_plan, validate_bundle

CONFIG_ROOT = Path("configs/dynamic_platform")
CLASSIC_RUNTIME_DIRS = (
    Path("src/orchestrators"),
    Path("src/routing"),
    Path("src/agents"),
    Path("src/slack"),
    Path("src/api"),
)


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


def test_dynamic_validation_catches_unknown_source_capability():
    bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)
    bundle.source_catalog.sources[0].capabilities.append("missing_capability")

    report = validate_bundle(bundle)

    assert report.ok is False
    assert any(issue.code == "source_capability_unknown" for issue in report.errors)


def test_topology_plan_maps_capabilities_to_agents_and_sources():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    plan = build_execution_plan(bundle)

    assert plan["runtime_strategy"] == "classic_protected"
    assert "student_affairs" in plan["capability_to_agents"]["graduation_akts"]
    assert "omu_uploaded_transcripts" in plan["capability_to_sources"]["transcript_analysis"]
    assert "academic_programs" in plan["capability_to_agents"]["course_schedule"]


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


def test_tenant_cli_compare_classic_for_omu(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "compare-classic", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Classic topology compare" in captured.out
    assert "Status: OK" in captured.out


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
    assert "runtime-plan --tenant gamma_demo" in captured.out
    assert "scripts.tenant scaffold" in captured.out


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


def test_source_adapter_audit_passes_for_omu_and_acme_demo():
    omu_bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    acme_bundle = load_tenant_bundle("acme_demo", config_root=CONFIG_ROOT)

    omu_report = audit_source_adapters(omu_bundle)
    acme_report = audit_source_adapters(acme_bundle)

    assert omu_report.ok is True
    assert acme_report.ok is True
    assert omu_report.summary["source_count"] == 8
    assert "announcement_page" in acme_report.summary["adapters"]


def test_source_adapter_audit_catches_authority_mismatch():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    announcement_source = next(source for source in bundle.source_catalog.sources if source.adapter == "announcement_page")
    announcement_source.authority_level = "official_policy"

    report = audit_source_adapters(bundle)

    assert report.ok is False
    assert any(issue.code == "adapter_authority_mismatch" for issue in report.errors)


def test_source_adapter_audit_catches_owner_capability_mismatch():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)
    contact_source = next(source for source in bundle.source_catalog.sources if source.source_id == "omu_contact_directory")
    contact_source.capabilities = ["course_schedule"]

    report = audit_source_adapters(bundle)

    assert report.ok is False
    assert any(issue.code == "source_owner_lacks_capability" for issue in report.errors)


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


def test_tenant_cli_quality_gates_for_omu(capsys):
    exit_code = tenant_cli_main(["--config-root", str(CONFIG_ROOT), "quality-gates", "--tenant", "omu"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Quality gates: OK" in captured.out
    assert "source_adapter_audit: passed" in captured.out
    assert "shadow_decision_contracts: passed" in captured.out


def test_omu_runtime_plan_is_classic_safe_and_env_ready():
    bundle = load_tenant_bundle("omu", config_root=CONFIG_ROOT)

    plan = build_runtime_launch_plan(bundle, config_root=CONFIG_ROOT)
    payload = plan.to_dict()

    assert payload["compose_env_ready"] is True
    assert payload["live_runtime_enabled"] is True
    assert payload["runtime_binding_status"] == "classic_runtime_active_dynamic_runtime_disabled"
    assert payload["env"]["TENANT_KEY"] == "omu"
    assert payload["env"]["DYNAMIC_PLATFORM_RUNTIME"] == "disabled"


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


def test_parse_env_file_supports_quotes_and_export_prefix(tmp_path):
    env_path = tmp_path / "tenant.env"
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


def test_dynamic_platform_is_not_imported_by_classic_runtime_modules():
    offenders: list[str] = []
    for root in CLASSIC_RUNTIME_DIRS:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "dynamic_platform" in text:
                offenders.append(str(path))

    assert offenders == []
