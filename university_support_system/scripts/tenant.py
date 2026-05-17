"""Dynamic tenant profile CLI.

This CLI does not change the OMU classic runtime. It validates and plans
profile-driven tenant topologies so new institutions can be prepared without
touching production behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from src.dynamic_platform.loader import DynamicPlatformLoadError, DynamicPlatformPaths, load_tenant_bundle
from src.dynamic_platform.classic_compare import compare_bundle_to_classic
from src.dynamic_platform.decision_shadow import (
    compare_shadow_decisions,
    default_shadow_fixture_path,
    load_shadow_decision_cases,
)
from src.dynamic_platform.quality_gates import run_quality_gates
from src.dynamic_platform.runtime_env_check import check_runtime_env
from src.dynamic_platform.runtime_plan import build_runtime_launch_plan
from src.dynamic_platform.source_audit import audit_source_adapters
from src.dynamic_platform.validator import build_execution_plan, validate_bundle

DEFAULT_CONFIG_ROOT = Path("configs/dynamic_platform")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 2
    try:
        return int(args.handler(args))
    except DynamicPlatformLoadError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.tenant",
        description="Validate, plan, and scaffold dynamic tenant support profiles.",
    )
    parser.add_argument(
        "--config-root",
        default=str(DEFAULT_CONFIG_ROOT),
        help="Dynamic platform config root. Default: configs/dynamic_platform",
    )
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="Validate a tenant profile bundle.")
    validate_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    validate_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    validate_parser.set_defaults(handler=_cmd_validate)

    plan_parser = subparsers.add_parser("plan", help="Print a dry-run topology execution plan.")
    plan_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    plan_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    plan_parser.set_defaults(handler=_cmd_plan)

    compare_parser = subparsers.add_parser(
        "compare-classic",
        help="Compare a dynamic profile to the published OMU classic topology shape.",
    )
    compare_parser.add_argument("--tenant", required=True, help="Tenant key, usually omu.")
    compare_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    compare_parser.set_defaults(handler=_cmd_compare_classic)

    shadow_parser = subparsers.add_parser(
        "shadow-decisions",
        help="Compare expected golden decision contracts against the dynamic tenant profile.",
    )
    shadow_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu.")
    shadow_parser.add_argument(
        "--fixture",
        help="Decision fixture JSON. Default: tests/fixtures/dynamic_platform/<tenant>_shadow_decisions.json",
    )
    shadow_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    shadow_parser.set_defaults(handler=_cmd_shadow_decisions)

    source_audit_parser = subparsers.add_parser(
        "source-audit",
        help="Audit tenant source adapter contracts without touching external systems.",
    )
    source_audit_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    source_audit_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    source_audit_parser.set_defaults(handler=_cmd_source_audit)

    quality_parser = subparsers.add_parser(
        "quality-gates",
        help="Run offline readiness gates without touching the live runtime.",
    )
    quality_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu.")
    quality_parser.add_argument(
        "--shadow-fixture",
        help="Decision fixture JSON. Default: tests/fixtures/dynamic_platform/<tenant>_shadow_decisions.json",
    )
    quality_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Skip missing shadow fixture instead of failing. Intended only for early draft tenants.",
    )
    quality_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    quality_parser.set_defaults(handler=_cmd_quality_gates)

    runtime_parser = subparsers.add_parser(
        "runtime-plan",
        help="Print Docker/runtime environment plan for a tenant without enabling live dynamic runtime.",
    )
    runtime_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    runtime_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    runtime_parser.add_argument("--env-output", help="Optional .env output path for the tenant runtime plan.")
    runtime_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without a shadow decision fixture.",
    )
    runtime_parser.set_defaults(handler=_cmd_runtime_plan)

    runtime_env_parser = subparsers.add_parser(
        "runtime-env-check",
        help="Check a tenant .env file against the profile contract without enabling live dynamic runtime.",
    )
    runtime_env_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    runtime_env_parser.add_argument("--env-file", help="Optional .env file. Uses process environment when omitted.")
    runtime_env_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    runtime_env_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without a shadow decision fixture.",
    )
    runtime_env_parser.set_defaults(handler=_cmd_runtime_env_check)

    export_parser = subparsers.add_parser("export", help="Export validation and topology summary.")
    export_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    export_parser.add_argument("--output", help="Optional output JSON path. Prints to stdout when omitted.")
    export_parser.set_defaults(handler=_cmd_export)

    init_parser = subparsers.add_parser("init", help="Create a new tenant/profile skeleton.")
    init_parser.add_argument("--tenant", required=True, help="New tenant key.")
    init_parser.add_argument("--display-name", required=True, help="Institution display name.")
    init_parser.add_argument("--bot-name", required=True, help="Support bot display name.")
    init_parser.add_argument("--domain", required=True, help="Existing domain pack id.")
    init_parser.add_argument("--agent-pack", required=True, help="Existing agent pack id.")
    init_parser.add_argument("--dry-run", action="store_true", help="Print files that would be written.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    init_parser.set_defaults(handler=_cmd_init)

    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="Create a fuller tenant skeleton: profile, source catalog, replay fixture, and runbook.",
    )
    scaffold_parser.add_argument("--tenant", required=True, help="New tenant key.")
    scaffold_parser.add_argument("--display-name", required=True, help="Institution display name.")
    scaffold_parser.add_argument("--bot-name", required=True, help="Support bot display name.")
    scaffold_parser.add_argument("--domain", required=True, help="Existing domain pack id.")
    scaffold_parser.add_argument("--agent-pack", required=True, help="Existing agent pack id.")
    scaffold_parser.add_argument("--dry-run", action="store_true", help="Print files that would be written.")
    scaffold_parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    scaffold_parser.set_defaults(handler=_cmd_scaffold)

    return parser


def _cmd_validate(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = validate_bundle(bundle)
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        _print_report(report.to_dict())
    return 0 if report.ok else 1


def _cmd_plan(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = validate_bundle(bundle)
    plan = build_execution_plan(bundle)
    payload = {
        "validation": report.to_dict(),
        "plan": plan,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_report(report.to_dict())
        _print_plan(plan)
    return 0 if report.ok else 1


def _cmd_compare_classic(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    validation = validate_bundle(bundle)
    compare = compare_bundle_to_classic(bundle)
    payload = {
        "validation": validation.to_dict(),
        "classic_compare": compare.to_dict(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_report(validation.to_dict())
        _print_classic_compare(compare.to_dict())
    return 0 if validation.ok and compare.ok else 1


def _cmd_shadow_decisions(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    validation = validate_bundle(bundle)
    fixture_path = Path(args.fixture) if args.fixture else default_shadow_fixture_path(args.tenant)
    cases = load_shadow_decision_cases(fixture_path)
    shadow = compare_shadow_decisions(bundle, cases, fixture_path=fixture_path)
    payload = {
        "validation": validation.to_dict(),
        "shadow_decisions": shadow.to_dict(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_report(validation.to_dict())
        _print_shadow_decisions(shadow.to_dict())
    return 0 if validation.ok and shadow.ok else 1


def _cmd_source_audit(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    validation = validate_bundle(bundle)
    audit = audit_source_adapters(bundle)
    payload = {
        "validation": validation.to_dict(),
        "source_audit": audit.to_dict(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_report(validation.to_dict())
        _print_source_audit(audit.to_dict())
    return 0 if validation.ok and audit.ok else 1


def _cmd_quality_gates(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = run_quality_gates(
        bundle,
        shadow_fixture_path=args.shadow_fixture,
        require_shadow_fixture=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_quality_gates(payload)
    return 0 if report.ok else 1


def _cmd_runtime_plan(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    plan = build_runtime_launch_plan(
        bundle,
        config_root=args.config_root,
        require_quality_gates=not args.allow_missing_shadow,
    )
    payload = plan.to_dict()
    if args.env_output:
        output_path = Path(args.env_output)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(plan.to_env_text(), encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: Could not write env output {output_path}: {exc}", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_plan(payload, env_output=args.env_output)
    return 0 if plan.compose_env_ready else 1


def _cmd_runtime_env_check(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = check_runtime_env(
        bundle,
        config_root=args.config_root,
        env_file=args.env_file,
        require_quality_gates=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_env_check(payload)
    return 0 if report.ok else 1


def _cmd_export(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = validate_bundle(bundle)
    payload = {
        "tenant": bundle.tenant.model_dump(mode="json"),
        "domain_pack": bundle.domain_pack.model_dump(mode="json"),
        "agent_pack": bundle.agent_pack.model_dump(mode="json"),
        "source_catalog": bundle.source_catalog.model_dump(mode="json"),
        "validation": report.to_dict(),
        "plan": build_execution_plan(bundle),
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized + "\n", encoding="utf-8")
        print(f"Export written: {output_path}")
    else:
        print(serialized)
    return 0 if report.ok else 1


def _cmd_init(args: argparse.Namespace) -> int:
    files = _build_tenant_skeleton_files(args, include_replay_and_runbook=False)
    return _write_or_print_skeleton(files, dry_run=args.dry_run, force=args.force)


def _cmd_scaffold(args: argparse.Namespace) -> int:
    files = _build_tenant_skeleton_files(args, include_replay_and_runbook=True)
    return _write_or_print_skeleton(files, dry_run=args.dry_run, force=args.force)


def _build_tenant_skeleton_files(
    args: argparse.Namespace,
    *,
    include_replay_and_runbook: bool,
) -> dict[Path, str]:
    paths = DynamicPlatformPaths.from_root(args.config_root)
    tenant_path = paths.tenant_path(args.tenant)
    source_catalog_id = f"{args.tenant}_sources"
    source_catalog_path = paths.source_catalog_path(source_catalog_id)
    replay_path = Path("tests/fixtures/dynamic_platform") / f"{args.tenant}_golden.json"
    shadow_decisions_path = Path("tests/fixtures/dynamic_platform") / f"{args.tenant}_shadow_decisions.json"
    runbook_path = Path("docs/dynamic_platform") / f"{args.tenant}_runbook.md"

    tenant_payload = {
        "schema_version": 1,
        "tenant_key": args.tenant,
        "display_name": args.display_name,
        "bot_name": args.bot_name,
        "locale": "tr-TR",
        "timezone": "Europe/Istanbul",
        "runtime_strategy": "dynamic_shadow",
        "domain_pack": args.domain,
        "agent_pack": args.agent_pack,
        "source_catalog": source_catalog_id,
        "replay_suite": f"{args.tenant}_golden",
        "entities": {
            "groups": {
                "departments": [],
                "teams": [],
                "services": [],
                "products": [],
            }
        },
        "metadata": {
            "generated_by": "scripts.tenant scaffold" if include_replay_and_runbook else "scripts.tenant init",
            "classic_runtime_protected": False,
        },
    }
    catalog_payload = {
        "schema_version": 1,
        "source_catalog": source_catalog_id,
        "tenant_key": args.tenant,
        "sources": [],
    }
    files: dict[Path, str] = {
        tenant_path: yaml.safe_dump(tenant_payload, sort_keys=False, allow_unicode=True),
        source_catalog_path: yaml.safe_dump(catalog_payload, sort_keys=False, allow_unicode=True),
    }
    if include_replay_and_runbook:
        replay_payload = {
            "schema_version": 1,
            "tenant_key": args.tenant,
            "cases": [
                {
                    "id": "SMOKE01",
                    "query": "Kisa bir destek sorusu buraya eklenir.",
                    "expected_capability": None,
                    "expected_agent": None,
                    "notes": "Tenant kaynaklari eklendikten sonra doldurulacak smoke case.",
                }
            ],
        }
        shadow_decisions_payload = {
            "schema_version": 1,
            "tenant_key": args.tenant,
            "description": "Tenant decision contract fixture. Fill this before enabling dynamic pilot/on mode.",
            "cases": [
                {
                    "id": "SMOKE-DECISION-01",
                    "query": "Kisa bir destek sorusu buraya eklenir.",
                    "expected_capabilities": [],
                    "expected_agents": [],
                    "expected_source_families": [],
                    "expected_source_owners": [],
                    "expected_authority_levels": [],
                    "notes": "Bu case bilincli olarak bos baslar; tenant kaynaklari eklendikten sonra doldurulmalidir.",
                }
            ],
        }
        files[replay_path] = json.dumps(replay_payload, ensure_ascii=False, indent=2) + "\n"
        files[shadow_decisions_path] = json.dumps(shadow_decisions_payload, ensure_ascii=False, indent=2) + "\n"
        files[runbook_path] = (
            f"# {args.display_name} Dynamic Tenant Runbook\n\n"
            "Bu dosya scaffold tarafindan uretilen baslangic runbook'udur.\n\n"
            "## Kontrol Komutlari\n\n"
            "```powershell\n"
            f"python -m scripts.tenant validate --tenant {args.tenant}\n"
            f"python -m scripts.tenant plan --tenant {args.tenant}\n"
            f"python -m scripts.tenant source-audit --tenant {args.tenant}\n"
            f"python -m scripts.tenant shadow-decisions --tenant {args.tenant}\n"
            f"python -m scripts.tenant quality-gates --tenant {args.tenant}\n"
            f"python -m scripts.tenant runtime-plan --tenant {args.tenant}\n"
            f"python -m scripts.tenant runtime-env-check --tenant {args.tenant} --env-file .env\n"
            f"python -m scripts.tenant export --tenant {args.tenant}\n"
            "```\n\n"
            "## Doldurulacaklar\n\n"
            "- Source catalog kayitlari\n"
            "- Entity registry aliaslari\n"
            "- Tenant golden replay case'leri\n"
            "- Tenant shadow decision contract case'leri\n"
            "- Slack/API onboarding metinleri\n"
        )
    return files


def _write_or_print_skeleton(
    files: dict[Path, str],
    *,
    dry_run: bool,
    force: bool,
) -> int:
    if dry_run:
        for path, content in files.items():
            print(f"Would write: {path.resolve()}")
            print(content)
        return 0

    for path in files:
        if path.exists() and not force:
            print(f"ERROR: {path} already exists. Use --force to overwrite.", file=sys.stderr)
            return 1
        path.parent.mkdir(parents=True, exist_ok=True)

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        print(f"Created: {path}")
    return 0


def _print_report(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")
    summary = report.get("summary") or {}
    print(
        "Topology: "
        f"domain={summary.get('domain_pack')} "
        f"agents={summary.get('agent_count')} "
        f"specialists={summary.get('specialist_count')} "
        f"capabilities={summary.get('capability_count')} "
        f"sources={summary.get('enabled_source_count')}/{summary.get('source_count')} "
        f"runtime={summary.get('runtime_strategy')}"
    )
    for issue in report.get("errors") or []:
        print(f"ERROR {issue['code']}: {issue['message']}")
    for issue in report.get("warnings") or []:
        print(f"WARNING {issue['code']}: {issue['message']}")


def _print_plan(plan: dict[str, Any]) -> None:
    print("\nAgents:")
    for agent in plan["agents"]:
        specialists = ", ".join(agent["specialists"]) or "-"
        capabilities = ", ".join(agent["capabilities"]) or "-"
        print(f"- {agent['agent_id']} [{agent['role']}] capabilities={capabilities} specialists={specialists}")
    print("\nCapability routes:")
    for capability, agents in plan["capability_to_agents"].items():
        sources = plan["capability_to_sources"].get(capability, [])
        print(f"- {capability}: agents={', '.join(agents)} sources={', '.join(sources) or '-'}")


def _print_classic_compare(report: dict[str, Any]) -> None:
    print("\nClassic topology compare:")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")
    for group in ("department_agents", "capability_agents", "specialist_agents"):
        classic_values = ", ".join(report["classic"].get(group, [])) or "-"
        dynamic_values = ", ".join(report["dynamic"].get(group, [])) or "-"
        print(f"- {group}: classic=[{classic_values}] dynamic=[{dynamic_values}]")
    for issue in report.get("errors") or []:
        print(f"ERROR {issue['code']}: {issue['message']}")
    for issue in report.get("warnings") or []:
        print(f"WARNING {issue['code']}: {issue['message']}")


def _print_shadow_decisions(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print("\nShadow decision compare:")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Cases: "
        f"{summary.get('passed', 0)}/{summary.get('case_count', 0)} passed "
        f"({summary.get('failed', 0)} failed)"
    )
    print(f"Fixture: {report.get('fixture_path')}")
    for record in report.get("records") or []:
        status = "OK" if record.get("ok") else "FAILED"
        capabilities = ", ".join(record.get("expected_capabilities") or []) or "-"
        agents = ", ".join(record.get("dynamic_agents") or []) or "-"
        sources = ", ".join(record.get("dynamic_source_families") or []) or "-"
        print(f"- {record.get('case_id')}: {status} capabilities=[{capabilities}] agents=[{agents}] sources=[{sources}]")
        for issue in record.get("issues") or []:
            print(f"  {issue['severity'].upper()} {issue['code']}: {issue['message']}")


def _print_source_audit(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print("\nSource adapter audit:")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Sources: "
        f"{summary.get('enabled_source_count', 0)}/{summary.get('source_count', 0)} enabled "
        f"adapters=[{', '.join(summary.get('adapters') or []) or '-'}]"
    )
    for issue in report.get("errors") or []:
        print(f"ERROR {issue['code']} {issue['source_id']}: {issue['message']}")
    for issue in report.get("warnings") or []:
        print(f"WARNING {issue['code']} {issue['source_id']}: {issue['message']}")


def _print_quality_gates(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Quality gates: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Gates: "
        f"{summary.get('passed', 0)} passed, "
        f"{summary.get('failed', 0)} failed, "
        f"{summary.get('skipped', 0)} skipped"
    )
    for gate in report.get("gates") or []:
        print(f"- {gate['gate_id']}: {gate['status']} - {gate['message']}")


def _print_runtime_plan(report: dict[str, Any], *, env_output: str | None = None) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(f"Compose env ready: {'yes' if report['compose_env_ready'] else 'no'}")
    print(f"Live runtime enabled: {'yes' if report['live_runtime_enabled'] else 'no'}")
    print(f"Binding status: {report['runtime_binding_status']}")
    if env_output:
        print(f"Env file written: {env_output}")
    print("\nEnvironment:")
    for key, value in report.get("env", {}).items():
        print(f"- {key}={value}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_runtime_env_check(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime env check: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Env source: {report['env_source']}")
    print(f"Binding status: {report['runtime_binding_status']}")
    print("\nObserved tenant env:")
    for key, value in report.get("observed_env", {}).items():
        print(f"- {key}={value}")
    for issue in report.get("errors") or []:
        key = f" {issue['key']}" if issue.get("key") else ""
        print(f"ERROR {issue['code']}{key}: {issue['message']}")
    for issue in report.get("warnings") or []:
        key = f" {issue['key']}" if issue.get("key") else ""
        print(f"WARNING {issue['code']}{key}: {issue['message']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


if __name__ == "__main__":
    raise SystemExit(main())
