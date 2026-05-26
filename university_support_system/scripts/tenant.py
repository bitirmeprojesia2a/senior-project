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

from src.dynamic_platform.bootstrap_plan import build_tenant_bootstrap_plan
from src.dynamic_platform.activation_checklist import run_dynamic_activation_checklist
from src.dynamic_platform.loader import DynamicPlatformLoadError, DynamicPlatformPaths, load_tenant_bundle
from src.dynamic_platform.classic_compare import compare_bundle_to_classic
from src.dynamic_platform.completion_report import run_dynamic_platform_completion_report
from src.dynamic_platform.compose_config_audit import run_compose_config_audit
from src.dynamic_platform.compose_isolation_audit import run_compose_isolation_audit
from src.dynamic_platform.contract_matrix import build_capability_contract_matrix
from src.dynamic_platform.decision_shadow import (
    ShadowDecisionCase,
    compare_shadow_decisions,
    default_shadow_fixture_path,
    load_shadow_decision_cases,
)
from src.dynamic_platform.compose_template import build_compose_launch_template_files
from src.dynamic_platform.docker_plan import DEFAULT_COMPOSE_FILES, build_docker_deployment_plan
from src.dynamic_platform.genericity_audit import run_genericity_audit
from src.dynamic_platform.handoff_readiness import run_handoff_readiness
from src.dynamic_platform.model_runtime_contract import build_model_runtime_contract
from src.dynamic_platform.quality_gates import run_quality_gates
from src.dynamic_platform.registry_catalog import build_registry_catalog
from src.dynamic_platform.readiness import build_tenant_readiness_report
from src.dynamic_platform.retrieval_contract import build_retrieval_contract
from src.dynamic_platform.runtime_env_check import check_runtime_env
from src.dynamic_platform.runtime_isolation_contract import build_runtime_isolation_contract
from src.dynamic_platform.runtime_plan import build_runtime_launch_plan
from src.dynamic_platform.runtime_query_smoke import run_dynamic_query_smoke
from src.dynamic_platform.runtime_smoke_readiness import run_runtime_smoke_readiness
from src.dynamic_platform.runtime_container_audit import run_runtime_container_audit
from src.dynamic_platform.runtime_adapter_contract import build_runtime_adapter_contract
from src.dynamic_platform.runtime_adapter_draft import DynamicRuntimeAdapterDraft, DynamicRuntimeRequest
from src.dynamic_platform.runtime_adapter_implementation_plan import build_runtime_adapter_implementation_plan
from src.dynamic_platform.runtime_activation_guard import RuntimeActivationInput, evaluate_runtime_activation
from src.dynamic_platform.runtime_namespace import build_runtime_namespace_preview
from src.dynamic_platform.models import DynamicPlatformBundle, EntityScope, SourceCatalogEntry
from src.dynamic_platform.onboarding import build_onboarding_preview
from src.dynamic_platform.package_audit import run_tenant_package_portfolio_audit
from src.dynamic_platform.pilot_readiness import PILOT_READINESS_MODES, run_tenant_pilot_readiness
from src.dynamic_platform.pilot_secret_scaffold import write_tenant_pilot_secret_scaffold
from src.dynamic_platform.preflight import run_dynamic_platform_preflight
from src.dynamic_platform.secret_readiness import SECRET_READINESS_MODES, check_tenant_secret_readiness
from src.dynamic_platform.secrets_contract import build_tenant_secrets_contract
from src.dynamic_platform.portfolio_audit import run_tenant_portfolio_audit
from src.dynamic_platform.portability_audit import (
    collect_source_contract_identifiers,
    collect_portability_restrictions,
    run_tenant_portability_audit,
    run_tenant_portability_portfolio_audit,
)
from src.dynamic_platform.safety_audit import run_safety_audit
from src.dynamic_platform.shadow_runtime import build_shadow_runtime_decision
from src.dynamic_platform.shadow_runtime_replay import run_shadow_runtime_replay
from src.dynamic_platform.source_audit import audit_source_adapters
from src.dynamic_platform.source_ingestion_plan import build_source_ingestion_plan
from src.dynamic_platform.tenant_rehearsal import run_draft_pack_creation_rehearsal, run_tenant_creation_rehearsal
from src.dynamic_platform.tenant_package import write_tenant_package
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

    matrix_parser = subparsers.add_parser(
        "contract-matrix",
        help="Print capability to agent/source/final-owner matrix for a tenant profile.",
    )
    matrix_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    matrix_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    matrix_parser.set_defaults(handler=_cmd_contract_matrix)

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

    source_ingestion_parser = subparsers.add_parser(
        "source-ingestion-plan",
        help="Plan source sync/index steps without opening files, web pages, DBs, or APIs.",
    )
    source_ingestion_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    source_ingestion_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    source_ingestion_parser.set_defaults(handler=_cmd_source_ingestion_plan)

    retrieval_contract_parser = subparsers.add_parser(
        "retrieval-contract",
        help="Print the tenant retrieval service boundary and current no-download retrieval mode.",
    )
    retrieval_contract_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    retrieval_contract_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    retrieval_contract_parser.set_defaults(handler=_cmd_retrieval_contract)

    model_runtime_contract_parser = subparsers.add_parser(
        "model-runtime-contract",
        help="Print model cache, reranker candidate, and FP16 rules without loading models.",
    )
    model_runtime_contract_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    model_runtime_contract_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    model_runtime_contract_parser.set_defaults(handler=_cmd_model_runtime_contract)

    genericity_parser = subparsers.add_parser(
        "genericity-audit",
        help="Check that dynamic platform core has not absorbed institution-specific behavior.",
    )
    genericity_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    genericity_parser.set_defaults(handler=_cmd_genericity_audit)

    audit_all_parser = subparsers.add_parser(
        "audit-all",
        help="Run offline portfolio audit for every configured dynamic tenant.",
    )
    audit_all_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without shadow fixture.",
    )
    audit_all_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    audit_all_parser.set_defaults(handler=_cmd_audit_all)

    registry_parser = subparsers.add_parser(
        "registry",
        help="List configured domain packs, agent packs, source catalogs, and tenants offline.",
    )
    registry_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    registry_parser.set_defaults(handler=_cmd_registry)

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

    adapter_contract_parser = subparsers.add_parser(
        "runtime-adapter-contract",
        help="Print the future dynamic runtime adapter boundary without wiring live runtime.",
    )
    adapter_contract_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    adapter_contract_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    adapter_contract_parser.set_defaults(handler=_cmd_runtime_adapter_contract)

    adapter_draft_parser = subparsers.add_parser(
        "runtime-adapter-draft",
        help="Preview the typed dynamic adapter response in shadow-only mode without live runtime wiring.",
    )
    adapter_draft_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    adapter_draft_parser.add_argument("--query", required=True, help="Representative user query.")
    adapter_draft_parser.add_argument(
        "--capability",
        action="append",
        default=[],
        help="Explicit capability hint. Can be repeated.",
    )
    adapter_draft_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    adapter_draft_parser.set_defaults(handler=_cmd_runtime_adapter_draft)

    adapter_impl_parser = subparsers.add_parser(
        "runtime-adapter-implementation-plan",
        help="Print the future live adapter implementation phases without wiring live runtime.",
    )
    adapter_impl_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    adapter_impl_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    adapter_impl_parser.set_defaults(handler=_cmd_runtime_adapter_implementation_plan)

    activation_guard_parser = subparsers.add_parser(
        "runtime-activation-guard",
        help="Evaluate future live adapter activation gates without wiring live runtime.",
    )
    activation_guard_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. acme_demo.")
    activation_guard_parser.add_argument(
        "--requested-live-mode",
        default="dynamic_pilot",
        choices=["shadow", "dynamic_pilot", "dynamic_on"],
        help="Requested future live mode to evaluate.",
    )
    activation_guard_parser.add_argument("--allowed-tenant", action="append", default=[], help="Tenant allowlist entry.")
    activation_guard_parser.add_argument("--allowed-capability", action="append", default=[], help="Capability allowlist entry.")
    activation_guard_parser.add_argument("--package-audit-ok", action="store_true")
    activation_guard_parser.add_argument("--runtime-isolation-ok", action="store_true")
    activation_guard_parser.add_argument("--secret-readiness-ok", action="store_true")
    activation_guard_parser.add_argument("--golden-replay-ok", action="store_true")
    activation_guard_parser.add_argument("--narrow-live-replay-ok", action="store_true")
    activation_guard_parser.add_argument("--operator-approved", action="store_true")
    activation_guard_parser.add_argument("--adapter-implemented", action="store_true")
    activation_guard_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    activation_guard_parser.set_defaults(handler=_cmd_runtime_activation_guard)

    isolation_contract_parser = subparsers.add_parser(
        "runtime-isolation-contract",
        help="Print tenant cache/state/upload isolation contract without touching runtime stores.",
    )
    isolation_contract_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    isolation_contract_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    isolation_contract_parser.set_defaults(handler=_cmd_runtime_isolation_contract)

    namespace_parser = subparsers.add_parser(
        "runtime-namespace-preview",
        help="Preview tenant-scoped runtime cache/state/upload keys without writing runtime stores.",
    )
    namespace_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    namespace_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    namespace_parser.set_defaults(handler=_cmd_runtime_namespace_preview)

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

    secrets_parser = subparsers.add_parser(
        "secrets-contract",
        help="Print tenant secret names and safe injection rules without reading or writing secret values.",
    )
    secrets_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    secrets_parser.add_argument("--example-env", action="store_true", help="Print blank example env instead of summary.")
    secrets_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    secrets_parser.set_defaults(handler=_cmd_secrets_contract)

    pilot_secret_scaffold_parser = subparsers.add_parser(
        "pilot-secret-scaffold",
        help="Write a blank, gitignored pilot secret env scaffold outside tenant packages.",
    )
    pilot_secret_scaffold_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. acme_demo.")
    pilot_secret_scaffold_parser.add_argument(
        "--output-dir",
        default="tmp/dynamic_platform_runtime_secrets",
        help="Output directory. Default: tmp/dynamic_platform_runtime_secrets",
    )
    pilot_secret_scaffold_parser.add_argument(
        "--include-slack",
        action="store_true",
        help="Mark Slack Socket Mode keys as required for the future pilot validation commands.",
    )
    pilot_secret_scaffold_parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files.")
    pilot_secret_scaffold_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    pilot_secret_scaffold_parser.set_defaults(handler=_cmd_pilot_secret_scaffold)

    secret_readiness_parser = subparsers.add_parser(
        "secret-readiness",
        help="Check whether required tenant secrets are present without printing secret values.",
    )
    secret_readiness_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    secret_readiness_parser.add_argument(
        "--mode",
        choices=sorted(SECRET_READINESS_MODES),
        default="no_secret_smoke",
        help="Secret readiness mode to evaluate.",
    )
    secret_readiness_parser.add_argument("--env-file", help="Optional secret env file. Uses process env when omitted.")
    secret_readiness_parser.add_argument(
        "--include-slack",
        action="store_true",
        help="Require Slack Socket Mode secrets when checking dynamic_pilot.",
    )
    secret_readiness_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    secret_readiness_parser.set_defaults(handler=_cmd_secret_readiness)

    docker_parser = subparsers.add_parser(
        "docker-plan",
        help="Audit current compose files for tenant deployment readiness without starting Docker.",
    )
    docker_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    docker_parser.add_argument(
        "--compose-file",
        action="append",
        dest="compose_files",
        help="Compose file to inspect. Can be repeated. Defaults to core A2A/Slack compose files.",
    )
    docker_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    docker_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without a shadow decision fixture.",
    )
    docker_parser.set_defaults(handler=_cmd_docker_plan)

    readiness_parser = subparsers.add_parser(
        "readiness",
        help="Run combined offline readiness gates for a tenant.",
    )
    readiness_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    readiness_parser.add_argument("--env-file", help="Optional .env file to include in readiness.")
    readiness_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    readiness_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without a shadow decision fixture.",
    )
    readiness_parser.set_defaults(handler=_cmd_readiness)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap-plan",
        help="Print an offline tenant setup checklist covering profile, sources, replay, package, and handoff.",
    )
    bootstrap_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    bootstrap_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    bootstrap_parser.set_defaults(handler=_cmd_bootstrap_plan)

    package_parser = subparsers.add_parser(
        "package",
        help="Write an offline tenant preparation package without starting Docker or downloading models.",
    )
    package_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    package_parser.add_argument("--output-dir", help="Output directory. Default: tmp/tenant_packages/<tenant>.")
    package_parser.add_argument("--force", action="store_true", help="Overwrite existing package files.")
    package_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    package_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without a shadow decision fixture.",
    )
    package_parser.set_defaults(handler=_cmd_package)

    package_audit_parser = subparsers.add_parser(
        "package-audit-all",
        help="Audit every generated tenant package with safety checks without starting runtime services.",
    )
    package_audit_parser.add_argument(
        "--package-root",
        default="tmp/tenant_packages",
        help="Package root directory. Default: tmp/tenant_packages",
    )
    package_audit_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without shadow fixture during package env checks.",
    )
    package_audit_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    package_audit_parser.set_defaults(handler=_cmd_package_audit_all)

    handoff_parser = subparsers.add_parser(
        "handoff-readiness",
        help="Run offline handoff readiness across registry, packages, and adapter draft smoke checks.",
    )
    handoff_parser.add_argument(
        "--package-root",
        default="tmp/tenant_packages",
        help="Package root directory. Default: tmp/tenant_packages",
    )
    handoff_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without shadow fixtures during handoff checks.",
    )
    handoff_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    handoff_parser.set_defaults(handler=_cmd_handoff_readiness)

    completion_parser = subparsers.add_parser(
        "completion-report",
        help="Run the final offline dynamic-platform completion gate without enabling live runtime.",
    )
    completion_parser.add_argument(
        "--package-root",
        default="tmp/tenant_packages",
        help="Package root directory. Default: tmp/tenant_packages",
    )
    completion_parser.add_argument(
        "--output-root",
        default="tmp/dynamic_platform_completion",
        help="Tmp root for creation rehearsals. Default: tmp/dynamic_platform_completion",
    )
    completion_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without shadow fixtures during completion checks.",
    )
    completion_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    completion_parser.set_defaults(handler=_cmd_completion_report)

    preflight_parser = subparsers.add_parser(
        "preflight",
        help="Run the offline preflight gate before any manual dynamic tenant compose validation.",
    )
    preflight_parser.add_argument(
        "--package-root",
        default="tmp/tenant_packages",
        help="Package root directory. Default: tmp/tenant_packages",
    )
    preflight_parser.add_argument(
        "--output-root",
        default="tmp/dynamic_platform_preflight",
        help="Tmp root for preflight artifacts. Default: tmp/dynamic_platform_preflight",
    )
    preflight_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without shadow fixtures during preflight checks.",
    )
    preflight_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    preflight_parser.set_defaults(handler=_cmd_preflight)

    pilot_readiness_parser = subparsers.add_parser(
        "pilot-readiness",
        help="Combine preflight, secret readiness, and adapter status before any dynamic pilot.",
    )
    pilot_readiness_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. acme_demo.")
    pilot_readiness_parser.add_argument(
        "--mode",
        choices=sorted(PILOT_READINESS_MODES),
        default="no_secret_smoke",
        help="Pilot readiness mode to evaluate.",
    )
    pilot_readiness_parser.add_argument(
        "--package-root",
        default="tmp/tenant_packages",
        help="Package root directory. Default: tmp/tenant_packages",
    )
    pilot_readiness_parser.add_argument(
        "--output-root",
        default="tmp/dynamic_platform_pilot_readiness",
        help="Tmp root for pilot-readiness artifacts. Default: tmp/dynamic_platform_pilot_readiness",
    )
    pilot_readiness_parser.add_argument(
        "--secrets-env-file",
        help="Optional secret env file. Defaults to <package-root>/<tenant>/tenant.env.",
    )
    pilot_readiness_parser.add_argument(
        "--include-slack",
        action="store_true",
        help="Require Slack Socket Mode secrets when checking dynamic_pilot.",
    )
    pilot_readiness_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without shadow fixtures during pilot readiness checks.",
    )
    pilot_readiness_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    pilot_readiness_parser.set_defaults(handler=_cmd_pilot_readiness)

    activation_checklist_parser = subparsers.add_parser(
        "activation-checklist",
        help="Summarize offline readiness and remaining work before any dynamic tenant activation.",
    )
    activation_checklist_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. acme_demo.")
    activation_checklist_parser.add_argument(
        "--package-root",
        default="tmp/tenant_packages",
        help="Package root directory. Default: tmp/tenant_packages",
    )
    activation_checklist_parser.add_argument(
        "--runtime-secrets-dir",
        default="tmp/dynamic_platform_runtime_secrets",
        help="Package-external runtime secret scaffold directory.",
    )
    activation_checklist_parser.add_argument(
        "--output-root",
        default="tmp/dynamic_platform_activation_checklist",
        help="Tmp root for activation checklist artifacts.",
    )
    activation_checklist_parser.add_argument(
        "--include-slack",
        action="store_true",
        help="Include Slack Socket Mode secret requirements in dynamic pilot readiness.",
    )
    activation_checklist_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without shadow fixtures during activation checklist checks.",
    )
    activation_checklist_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    activation_checklist_parser.set_defaults(handler=_cmd_activation_checklist)

    compose_template_parser = subparsers.add_parser(
        "compose-template",
        help="Write draft tenant compose launch artifacts without starting Docker.",
    )
    compose_template_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    compose_template_parser.add_argument("--output-dir", help="Output directory. Default: tmp/tenant_packages/<tenant>.")
    compose_template_parser.add_argument("--force", action="store_true", help="Overwrite existing draft compose files.")
    compose_template_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    compose_template_parser.set_defaults(handler=_cmd_compose_template)

    compose_isolation_parser = subparsers.add_parser(
        "compose-isolation-audit",
        help="Audit generated tenant compose draft isolation without starting Docker.",
    )
    compose_isolation_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    compose_isolation_parser.add_argument(
        "--package-dir",
        help="Tenant package directory. Default: tmp/tenant_packages/<tenant>.",
    )
    compose_isolation_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    compose_isolation_parser.set_defaults(handler=_cmd_compose_isolation_audit)

    compose_config_parser = subparsers.add_parser(
        "compose-config-audit",
        help="Run docker compose config safety checks without starting, building, or pulling services.",
    )
    compose_config_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. acme_demo or city_demo.")
    compose_config_parser.add_argument(
        "--package-dir",
        help="Tenant package directory. Default: tmp/tenant_packages/<tenant>.",
    )
    compose_config_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    compose_config_parser.set_defaults(handler=_cmd_compose_config_audit)

    runtime_smoke_parser = subparsers.add_parser(
        "runtime-smoke-readiness",
        help="Check no-download dynamic runtime smoke readiness without starting services.",
    )
    runtime_smoke_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. acme_demo.")
    runtime_smoke_parser.add_argument(
        "--package-dir",
        help="Tenant package directory. Default: tmp/tenant_packages/<tenant>.",
    )
    runtime_smoke_parser.add_argument("--image-ref", help="Docker image ref to inspect locally.")
    runtime_smoke_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    runtime_smoke_parser.set_defaults(handler=_cmd_runtime_smoke_readiness)

    runtime_container_audit_parser = subparsers.add_parser(
        "runtime-container-audit",
        help="Read Docker metadata and verify dynamic tenant containers match the resolved compose contract.",
    )
    runtime_container_audit_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. acme_demo.")
    runtime_container_audit_parser.add_argument(
        "--package-dir",
        help="Tenant package directory. Default: tmp/tenant_packages/<tenant>.",
    )
    runtime_container_audit_parser.add_argument("--expected-image", help="Expected dynamic API image ref.")
    runtime_container_audit_parser.add_argument(
        "--allow-dynamic-agents",
        action="store_true",
        help="Allow tenant-dynamic-agents profile containers in addition to default services.",
    )
    runtime_container_audit_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    runtime_container_audit_parser.set_defaults(handler=_cmd_runtime_container_audit)

    runtime_query_smoke_parser = subparsers.add_parser(
        "runtime-query-smoke",
        help="Call an already running dynamic /dynamic/query endpoint and print a UTF-8 safe smoke report.",
    )
    runtime_query_smoke_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. acme_demo.")
    runtime_query_smoke_parser.add_argument(
        "--base-url",
        help="Dynamic runtime base URL. Defaults are known for acme_demo and city_demo.",
    )
    runtime_query_smoke_parser.add_argument("--query", help="Query to send. Uses a tenant-specific demo query by default.")
    runtime_query_smoke_parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds. Default: 10.",
    )
    runtime_query_smoke_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    runtime_query_smoke_parser.set_defaults(handler=_cmd_runtime_query_smoke)

    portability_parser = subparsers.add_parser(
        "portability-audit",
        help="Audit tenant portability and cross-tenant leakage without starting runtime services.",
    )
    portability_parser.add_argument("--tenant", help="Tenant key, e.g. omu or acme_demo. Omit with --all.")
    portability_parser.add_argument("--all", action="store_true", help="Audit every configured tenant.")
    portability_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    portability_parser.set_defaults(handler=_cmd_portability_audit)

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

    rehearsal_parser = subparsers.add_parser(
        "creation-rehearsal",
        help="Run a tmp-only end-to-end rehearsal for creating and packaging a new tenant.",
    )
    rehearsal_parser.add_argument("--tenant", required=True, help="New tenant key.")
    rehearsal_parser.add_argument("--display-name", required=True, help="Institution display name.")
    rehearsal_parser.add_argument("--bot-name", required=True, help="Support bot display name.")
    rehearsal_parser.add_argument("--domain", required=True, help="Existing domain pack id.")
    rehearsal_parser.add_argument("--agent-pack", required=True, help="Existing agent pack id.")
    rehearsal_parser.add_argument(
        "--output-dir",
        help="Tmp output directory. Default: tmp/dynamic_platform_rehearsals/<tenant>.",
    )
    rehearsal_parser.add_argument("--force", action="store_true", help="Refresh existing tmp rehearsal artifacts.")
    rehearsal_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    rehearsal_parser.set_defaults(handler=_cmd_creation_rehearsal)

    pack_rehearsal_parser = subparsers.add_parser(
        "pack-creation-rehearsal",
        help="Run a tmp-only rehearsal for a brand-new domain pack, agent pack, and tenant package.",
    )
    pack_rehearsal_parser.add_argument("--tenant", required=True, help="New tenant key.")
    pack_rehearsal_parser.add_argument("--display-name", required=True, help="Institution display name.")
    pack_rehearsal_parser.add_argument("--bot-name", required=True, help="Support bot display name.")
    pack_rehearsal_parser.add_argument("--domain", required=True, help="New draft domain pack id.")
    pack_rehearsal_parser.add_argument("--domain-display-name", required=True, help="Domain pack display name.")
    pack_rehearsal_parser.add_argument("--agent-pack", required=True, help="New draft agent pack id.")
    pack_rehearsal_parser.add_argument("--agent-pack-display-name", required=True, help="Agent pack display name.")
    pack_rehearsal_parser.add_argument(
        "--capability",
        action="append",
        default=[],
        help="Capability id or id:Display Name. Can be repeated.",
    )
    pack_rehearsal_parser.add_argument(
        "--agent",
        action="append",
        default=[],
        help="Agent id or id:Display Name. Can be repeated.",
    )
    pack_rehearsal_parser.add_argument(
        "--output-dir",
        help="Tmp output directory. Default: tmp/dynamic_platform_rehearsals/<tenant>.",
    )
    pack_rehearsal_parser.add_argument("--force", action="store_true", help="Refresh existing tmp rehearsal artifacts.")
    pack_rehearsal_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    pack_rehearsal_parser.set_defaults(handler=_cmd_pack_creation_rehearsal)

    pack_scaffold_parser = subparsers.add_parser(
        "pack-scaffold",
        help="Create a draft domain pack and agent pack for a new institution type.",
    )
    pack_scaffold_parser.add_argument("--domain", required=True, help="New domain pack id.")
    pack_scaffold_parser.add_argument("--domain-display-name", required=True, help="Domain pack display name.")
    pack_scaffold_parser.add_argument("--agent-pack", required=True, help="New agent pack id.")
    pack_scaffold_parser.add_argument("--agent-pack-display-name", required=True, help="Agent pack display name.")
    pack_scaffold_parser.add_argument(
        "--capability",
        action="append",
        default=[],
        help="Capability id or id:Display Name. Can be repeated. Defaults to policy_qa and contact_lookup.",
    )
    pack_scaffold_parser.add_argument(
        "--agent",
        action="append",
        default=[],
        help="Agent id or id:Display Name. Can be repeated. Defaults to support.",
    )
    pack_scaffold_parser.add_argument("--dry-run", action="store_true", help="Print files that would be written.")
    pack_scaffold_parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    pack_scaffold_parser.set_defaults(handler=_cmd_pack_scaffold)

    source_scaffold_parser = subparsers.add_parser(
        "source-scaffold",
        help="Add or preview a source catalog entry for a tenant without indexing or downloading anything.",
    )
    source_scaffold_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    source_scaffold_parser.add_argument("--source-id", required=True, help="New source id.")
    source_scaffold_parser.add_argument("--adapter", required=True, help="Source adapter, e.g. pdf_document.")
    source_scaffold_parser.add_argument("--owner-agent", required=True, help="Owner agent id from the agent pack.")
    source_scaffold_parser.add_argument("--source-family", required=True, help="Source family label for routing/audit.")
    source_scaffold_parser.add_argument(
        "--capability",
        action="append",
        required=True,
        help="Capability served by this source. Can be repeated.",
    )
    source_scaffold_parser.add_argument(
        "--authority-level",
        help="Authority level. Defaults are derived from adapter when omitted.",
    )
    source_scaffold_parser.add_argument("--path", help="Optional local/source path hint.")
    source_scaffold_parser.add_argument("--url", help="Optional URL hint.")
    source_scaffold_parser.add_argument("--collection", help="Optional vector/SQL collection hint.")
    source_scaffold_parser.add_argument(
        "--entity-scope-type",
        default="global",
        choices=["global", "entity", "tenant", "uploaded_user_context"],
        help="Entity scope type. Default: global.",
    )
    source_scaffold_parser.add_argument("--entity-group", help="Entity group for entity-scoped sources.")
    source_scaffold_parser.add_argument("--entity-id", action="append", default=[], help="Entity id. Can be repeated.")
    source_scaffold_parser.add_argument(
        "--metadata",
        action="append",
        default=[],
        help="Metadata as KEY=VALUE. Can be repeated.",
    )
    source_scaffold_parser.add_argument("--disabled", action="store_true", help="Write source as enabled=false.")
    source_scaffold_parser.add_argument("--replace", action="store_true", help="Replace an existing source id.")
    source_scaffold_parser.add_argument("--dry-run", action="store_true", help="Print entry and audit result only.")
    source_scaffold_parser.set_defaults(handler=_cmd_source_scaffold)

    entity_scaffold_parser = subparsers.add_parser(
        "entity-scaffold",
        help="Add or preview a tenant entity such as a department, team, product, service, or program.",
    )
    entity_scaffold_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    entity_scaffold_parser.add_argument("--group", required=True, help="Entity group, e.g. departments or teams.")
    entity_scaffold_parser.add_argument("--entity-id", required=True, help="Entity id.")
    entity_scaffold_parser.add_argument("--display-name", required=True, help="Entity display name.")
    entity_scaffold_parser.add_argument("--alias", action="append", default=[], help="Alias. Can be repeated.")
    entity_scaffold_parser.add_argument(
        "--metadata",
        action="append",
        default=[],
        help="Metadata as KEY=VALUE. Can be repeated.",
    )
    entity_scaffold_parser.add_argument("--replace", action="store_true", help="Replace an existing entity id.")
    entity_scaffold_parser.add_argument("--dry-run", action="store_true", help="Print tenant profile preview only.")
    entity_scaffold_parser.set_defaults(handler=_cmd_entity_scaffold)

    decision_case_parser = subparsers.add_parser(
        "decision-case-scaffold",
        help="Add or preview a shadow decision contract case for a tenant.",
    )
    decision_case_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    decision_case_parser.add_argument("--case-id", required=True, help="Case id, e.g. ACME-LEAVE.")
    decision_case_parser.add_argument("--query", required=True, help="Representative user query.")
    decision_case_parser.add_argument(
        "--expected-capability",
        action="append",
        required=True,
        help="Expected capability. Can be repeated.",
    )
    decision_case_parser.add_argument("--expected-agent", action="append", default=[], help="Expected agent id.")
    decision_case_parser.add_argument(
        "--expected-specialist",
        action="append",
        default=[],
        help="Expected specialist id.",
    )
    decision_case_parser.add_argument(
        "--expected-source-family",
        action="append",
        default=[],
        help="Expected source family.",
    )
    decision_case_parser.add_argument(
        "--expected-source-owner",
        action="append",
        default=[],
        help="Expected source owner agent.",
    )
    decision_case_parser.add_argument(
        "--expected-authority-level",
        action="append",
        default=[],
        help="Expected authority level.",
    )
    decision_case_parser.add_argument("--expected-final-owner", help="Expected final owner agent.")
    decision_case_parser.add_argument("--notes", default="", help="Optional notes.")
    decision_case_parser.add_argument("--fixture", help="Fixture path. Default: tenant shadow decision fixture.")
    decision_case_parser.add_argument("--replace", action="store_true", help="Replace an existing case id.")
    decision_case_parser.add_argument("--dry-run", action="store_true", help="Print fixture preview only.")
    decision_case_parser.set_defaults(handler=_cmd_decision_case_scaffold)

    onboarding_parser = subparsers.add_parser(
        "onboarding-preview",
        help="Render a tenant-specific onboarding preview without sending Slack messages.",
    )
    onboarding_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    onboarding_parser.add_argument("--output", help="Optional output markdown path.")
    onboarding_parser.set_defaults(handler=_cmd_onboarding_preview)

    safety_parser = subparsers.add_parser(
        "safety-audit",
        help="Run offline safety checks that dynamic work has not leaked into classic runtime.",
    )
    safety_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    safety_parser.add_argument("--env-file", help="Optional env file to include in runtime safety check.")
    safety_parser.add_argument("--package-dir", help="Optional tenant package directory to check draft markers.")
    safety_parser.add_argument(
        "--allow-missing-shadow",
        action="store_true",
        help="Allow draft tenants without shadow fixture during env check.",
    )
    safety_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    safety_parser.set_defaults(handler=_cmd_safety_audit)

    shadow_runtime_parser = subparsers.add_parser(
        "shadow-runtime",
        help="Preview dynamic runtime capability/agent/source decision without touching live runtime.",
    )
    shadow_runtime_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    shadow_runtime_parser.add_argument("--query", required=True, help="Representative user query.")
    shadow_runtime_parser.add_argument(
        "--capability",
        action="append",
        default=[],
        help="Explicit capability hint. Can be repeated. When omitted, keyword shadow matching is used.",
    )
    shadow_runtime_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    shadow_runtime_parser.set_defaults(handler=_cmd_shadow_runtime)

    shadow_runtime_replay_parser = subparsers.add_parser(
        "shadow-runtime-replay",
        help="Replay shadow runtime decisions against a tenant decision fixture without live runtime calls.",
    )
    shadow_runtime_replay_parser.add_argument("--tenant", required=True, help="Tenant key, e.g. omu or acme_demo.")
    shadow_runtime_replay_parser.add_argument("--fixture", help="Decision fixture JSON. Defaults to tenant fixture.")
    shadow_runtime_replay_parser.add_argument(
        "--match-mode",
        choices=["contract", "keyword"],
        default="contract",
        help="contract uses expected capabilities as explicit hints; keyword tests the lightweight matcher.",
    )
    shadow_runtime_replay_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    shadow_runtime_replay_parser.set_defaults(handler=_cmd_shadow_runtime_replay)

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


def _cmd_contract_matrix(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    validation = validate_bundle(bundle)
    matrix = build_capability_contract_matrix(bundle)
    payload = {
        "validation": validation.to_dict(),
        "contract_matrix": matrix.to_dict(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_report(validation.to_dict())
        _print_contract_matrix(matrix.to_dict())
    return 0 if validation.ok and matrix.ok else 1


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


def _cmd_source_ingestion_plan(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    validation = validate_bundle(bundle)
    plan = build_source_ingestion_plan(bundle)
    payload = {
        "validation": validation.to_dict(),
        "source_ingestion_plan": plan.to_dict(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_report(validation.to_dict())
        _print_source_ingestion_plan(plan.to_dict())
    return 0 if validation.ok and plan.ok else 1


def _cmd_retrieval_contract(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    validation = validate_bundle(bundle)
    contract = build_retrieval_contract(bundle)
    payload = {
        "validation": validation.to_dict(),
        "retrieval_contract": contract.to_dict(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_report(validation.to_dict())
        _print_retrieval_contract(contract.to_dict())
    return 0 if validation.ok and contract.ok else 1


def _cmd_model_runtime_contract(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    validation = validate_bundle(bundle)
    contract = build_model_runtime_contract(bundle)
    payload = {
        "validation": validation.to_dict(),
        "model_runtime_contract": contract.to_dict(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_report(validation.to_dict())
        _print_model_runtime_contract(contract.to_dict())
    return 0 if validation.ok and contract.ok else 1


def _cmd_genericity_audit(args: argparse.Namespace) -> int:
    report = run_genericity_audit()
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_genericity_audit(payload)
    return 0 if report.ok else 1


def _cmd_audit_all(args: argparse.Namespace) -> int:
    report = run_tenant_portfolio_audit(
        config_root=args.config_root,
        require_shadow_fixture=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_portfolio_audit(payload)
    return 0 if report.ok else 1


def _cmd_registry(args: argparse.Namespace) -> int:
    report = build_registry_catalog(config_root=args.config_root)
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_registry_catalog(payload)
    return 0 if report.ok else 1


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


def _cmd_runtime_adapter_contract(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    contract = build_runtime_adapter_contract(bundle)
    payload = contract.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_adapter_contract(payload)
    return 0


def _cmd_runtime_adapter_draft(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    adapter = DynamicRuntimeAdapterDraft(bundle)
    request = DynamicRuntimeRequest(
        tenant_key=bundle.tenant.tenant_key,
        conversation_id="offline-preview",
        user_id="offline-preview",
        query=args.query,
        locale=bundle.tenant.locale,
        timezone=bundle.tenant.timezone,
        requested_capabilities=args.capability or [],
    )
    response = adapter.preview(request)
    payload = response.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_adapter_draft(payload)
    return 0 if payload.get("answer_status") == "shadow_decision_only" else 1


def _cmd_runtime_adapter_implementation_plan(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = build_runtime_adapter_implementation_plan(bundle)
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_adapter_implementation_plan(payload)
    return 0 if report.ok else 1


def _cmd_runtime_activation_guard(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = evaluate_runtime_activation(
        bundle,
        RuntimeActivationInput(
            package_audit_ok=args.package_audit_ok,
            runtime_isolation_ok=args.runtime_isolation_ok,
            secret_readiness_ok=args.secret_readiness_ok,
            golden_replay_ok=args.golden_replay_ok,
            narrow_live_replay_ok=args.narrow_live_replay_ok,
            explicit_operator_approval=args.operator_approved,
            adapter_live_binding_implemented=args.adapter_implemented,
            requested_live_mode=args.requested_live_mode,
            allowed_tenants=args.allowed_tenant,
            allowed_capabilities=args.allowed_capability,
        ),
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_activation_guard(payload)
    return 0 if report.live_binding_allowed else 1


def _cmd_runtime_isolation_contract(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = build_runtime_isolation_contract(bundle)
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_isolation_contract(payload)
    return 0 if report.ok else 1


def _cmd_runtime_namespace_preview(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    payload = build_runtime_namespace_preview(bundle)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_namespace_preview(payload)
    return 0 if payload.get("ok") else 1


def _cmd_runtime_env_check(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        report = check_runtime_env(
            bundle,
            config_root=args.config_root,
            env_file=args.env_file,
            require_quality_gates=not args.allow_missing_shadow,
        )
    except OSError as exc:
        print(f"ERROR: Could not read env file {args.env_file}: {exc}", file=sys.stderr)
        return 1
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_env_check(payload)
    return 0 if report.ok else 1


def _cmd_secrets_contract(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    contract = build_tenant_secrets_contract(bundle)
    if args.example_env:
        print(contract.to_example_env())
        return 0
    payload = contract.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_secrets_contract(payload)
    return 0


def _cmd_pilot_secret_scaffold(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        result = write_tenant_pilot_secret_scaffold(
            bundle,
            output_dir=args.output_dir,
            include_slack=args.include_slack,
            force=args.force,
        )
    except FileExistsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    payload = result.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_pilot_secret_scaffold(payload)
    return 0 if result.ok else 1


def _cmd_secret_readiness(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        report = check_tenant_secret_readiness(
            bundle,
            mode=args.mode,
            include_slack=args.include_slack,
            env_file=args.env_file,
        )
    except OSError as exc:
        print(f"ERROR: Could not read env file {args.env_file}: {exc}", file=sys.stderr)
        return 1
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_secret_readiness(payload)
    return 0 if report.ok else 1


def _cmd_docker_plan(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    compose_files = args.compose_files or [str(path) for path in DEFAULT_COMPOSE_FILES]
    report = build_docker_deployment_plan(
        bundle,
        config_root=args.config_root,
        compose_files=compose_files,
        require_quality_gates=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_docker_plan(payload)
    return 0 if report.single_instance_env_ready else 1


def _cmd_readiness(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        report = build_tenant_readiness_report(
            bundle,
            config_root=args.config_root,
            env_file=args.env_file,
            require_quality_gates=not args.allow_missing_shadow,
        )
    except OSError as exc:
        print(f"ERROR: Could not read env file {args.env_file}: {exc}", file=sys.stderr)
        return 1
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_readiness(payload)
    return 0 if report.ok else 1


def _cmd_bootstrap_plan(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = build_tenant_bootstrap_plan(bundle)
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_bootstrap_plan(payload)
    return 0 if report.ok else 1


def _cmd_package(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        result = write_tenant_package(
            bundle,
            config_root=args.config_root,
            output_dir=args.output_dir,
            require_quality_gates=not args.allow_missing_shadow,
            force=args.force,
        )
    except FileExistsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    payload = result.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_package(payload)
    return 0


def _cmd_package_audit_all(args: argparse.Namespace) -> int:
    report = run_tenant_package_portfolio_audit(
        config_root=args.config_root,
        package_root=args.package_root,
        require_quality_gates=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_package_portfolio_audit(payload)
    return 0 if report.ok else 1


def _cmd_handoff_readiness(args: argparse.Namespace) -> int:
    report = run_handoff_readiness(
        config_root=args.config_root,
        package_root=args.package_root,
        require_quality_gates=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_handoff_readiness(payload)
    return 0 if report.ok else 1


def _cmd_completion_report(args: argparse.Namespace) -> int:
    report = run_dynamic_platform_completion_report(
        config_root=args.config_root,
        package_root=args.package_root,
        output_root=args.output_root,
        require_quality_gates=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_completion_report(payload)
    return 0 if report.ok else 1


def _cmd_preflight(args: argparse.Namespace) -> int:
    report = run_dynamic_platform_preflight(
        config_root=args.config_root,
        package_root=args.package_root,
        output_root=args.output_root,
        require_quality_gates=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_preflight(payload)
    return 0 if report.ok else 1


def _cmd_compose_config_audit(args: argparse.Namespace) -> int:
    report = run_compose_config_audit(
        tenant_key=args.tenant,
        config_root=args.config_root,
        package_dir=args.package_dir,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_compose_config_audit(payload)
    return 0 if report.ok else 1


def _cmd_runtime_smoke_readiness(args: argparse.Namespace) -> int:
    report = run_runtime_smoke_readiness(
        tenant_key=args.tenant,
        config_root=args.config_root,
        package_dir=args.package_dir,
        image_ref=args.image_ref,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_smoke_readiness(payload)
    return 0 if report.ok else 1


def _cmd_runtime_container_audit(args: argparse.Namespace) -> int:
    report = run_runtime_container_audit(
        tenant_key=args.tenant,
        config_root=args.config_root,
        package_dir=args.package_dir,
        expected_image=args.expected_image,
        allow_dynamic_agents=args.allow_dynamic_agents,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_container_audit(payload)
    return 0 if report.ok else 1


def _cmd_runtime_query_smoke(args: argparse.Namespace) -> int:
    report = run_dynamic_query_smoke(
        tenant_key=args.tenant,
        base_url=args.base_url,
        query=args.query,
        timeout_seconds=args.timeout_seconds,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_query_smoke(payload)
    return 0 if report.ok else 1


def _cmd_pilot_readiness(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        report = run_tenant_pilot_readiness(
            bundle,
            config_root=args.config_root,
            package_root=args.package_root,
            output_root=args.output_root,
            secrets_env_file=args.secrets_env_file,
            mode=args.mode,
            include_slack=args.include_slack,
            require_quality_gates=not args.allow_missing_shadow,
        )
    except OSError as exc:
        print(f"ERROR: Could not read pilot readiness input: {exc}", file=sys.stderr)
        return 1
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_pilot_readiness(payload)
    return 0 if report.ok else 1


def _cmd_activation_checklist(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        report = run_dynamic_activation_checklist(
            bundle,
            config_root=args.config_root,
            package_root=args.package_root,
            runtime_secrets_dir=args.runtime_secrets_dir,
            output_root=args.output_root,
            include_slack=args.include_slack,
            require_quality_gates=not args.allow_missing_shadow,
        )
    except OSError as exc:
        print(f"ERROR: Could not read activation checklist input: {exc}", file=sys.stderr)
        return 1
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_activation_checklist(payload)
    return 0 if report.ok else 1


def _cmd_compose_template(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    target_dir = Path(args.output_dir) if args.output_dir else Path("tmp/tenant_packages") / bundle.tenant.tenant_key
    files = build_compose_launch_template_files(bundle, config_root=args.config_root, package_dir=target_dir)
    existing = [target_dir / name for name in files if (target_dir / name).exists()]
    if existing and not args.force:
        names = ", ".join(str(path) for path in existing)
        print(f"ERROR: Compose template files already exist. Use --force to overwrite: {names}", file=sys.stderr)
        return 1
    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for relative_name, content in files.items():
        path = target_dir / relative_name
        path.write_text(content, encoding="utf-8")
        written.append(str(path))
    payload = {
        "tenant_key": bundle.tenant.tenant_key,
        "output_dir": str(target_dir),
        "files": written,
        "notes": [
            "Draft only; no Docker service was started.",
            "Validate with docker compose config and replay before any run.",
            "Existing OMU compose files were not modified.",
        ],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_compose_template(payload)
    return 0


def _cmd_compose_isolation_audit(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    package_dir = Path(args.package_dir) if args.package_dir else Path("tmp/tenant_packages") / bundle.tenant.tenant_key
    report = run_compose_isolation_audit(bundle, package_dir=package_dir)
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_compose_isolation_audit(payload)
    return 0 if report.ok else 1


def _cmd_portability_audit(args: argparse.Namespace) -> int:
    if args.all:
        report = run_tenant_portability_portfolio_audit(config_root=args.config_root)
        payload = report.to_dict()
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            _print_portability_portfolio_audit(payload)
        return 0 if report.ok else 1
    if not args.tenant:
        print("ERROR: portability-audit requires --tenant or --all.", file=sys.stderr)
        return 2
    paths = DynamicPlatformPaths.from_root(args.config_root)
    known_tenants = sorted(path.stem for path in paths.tenants_dir.glob("*.yaml"))
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    restricted_terms, restricted_groups = collect_portability_restrictions(
        config_root=args.config_root,
        current_domain_pack=bundle.domain_pack.domain_pack,
    )
    report = run_tenant_portability_audit(
        bundle,
        known_tenant_keys=known_tenants,
        known_tenant_source_identifiers=collect_source_contract_identifiers(
            config_root=args.config_root,
            tenant_keys=known_tenants,
        ),
        restricted_identifier_terms=restricted_terms,
        restricted_entity_groups=restricted_groups,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_portability_audit(payload)
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
        "contract_matrix": build_capability_contract_matrix(bundle).to_dict(),
        "source_audit": audit_source_adapters(bundle).to_dict(),
        "source_ingestion_plan": build_source_ingestion_plan(bundle).to_dict(),
        "runtime_adapter_contract": build_runtime_adapter_contract(bundle).to_dict(),
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


def _cmd_creation_rehearsal(args: argparse.Namespace) -> int:
    report = run_tenant_creation_rehearsal(
        tenant_key=args.tenant,
        display_name=args.display_name,
        bot_name=args.bot_name,
        domain_pack=args.domain,
        agent_pack=args.agent_pack,
        config_root=args.config_root,
        output_dir=args.output_dir,
        force=args.force,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_creation_rehearsal(payload)
    return 0 if report.ok else 1


def _cmd_pack_creation_rehearsal(args: argparse.Namespace) -> int:
    report = run_draft_pack_creation_rehearsal(
        tenant_key=args.tenant,
        display_name=args.display_name,
        bot_name=args.bot_name,
        domain_pack=args.domain,
        domain_display_name=args.domain_display_name,
        agent_pack=args.agent_pack,
        agent_pack_display_name=args.agent_pack_display_name,
        capability_specs=args.capability,
        agent_specs=args.agent,
        config_root=args.config_root,
        output_dir=args.output_dir,
        force=args.force,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_creation_rehearsal(payload)
    return 0 if report.ok else 1


def _cmd_pack_scaffold(args: argparse.Namespace) -> int:
    files = _build_pack_skeleton_files(args)
    return _write_or_print_skeleton(files, dry_run=args.dry_run, force=args.force)


def _cmd_source_scaffold(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        entry = _build_source_catalog_entry(args, bundle)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    existing = [source for source in bundle.source_catalog.sources if source.source_id == entry.source_id]
    if existing and not args.replace:
        print(f"ERROR: Source {entry.source_id} already exists. Use --replace to replace it.", file=sys.stderr)
        return 1

    new_sources = [source for source in bundle.source_catalog.sources if source.source_id != entry.source_id]
    new_sources.append(entry)
    next_catalog = bundle.source_catalog.model_copy(update={"sources": new_sources})
    next_bundle = bundle.model_copy(update={"source_catalog": next_catalog})
    validation = validate_bundle(next_bundle)
    audit = audit_source_adapters(next_bundle)
    payload = {
        "source": entry.model_dump(mode="json"),
        "validation": validation.to_dict(),
        "source_audit": audit.to_dict(),
    }
    if not validation.ok or not audit.ok:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("ERROR: Source entry did not pass validation/audit; catalog was not written.", file=sys.stderr)
        return 1

    catalog_path = DynamicPlatformPaths.from_root(args.config_root).source_catalog_path(bundle.tenant.source_catalog)
    catalog_payload = next_catalog.model_dump(mode="json", exclude_none=True)
    rendered = yaml.safe_dump(catalog_payload, sort_keys=False, allow_unicode=True)
    if args.dry_run:
        print(f"Would update: {catalog_path}")
        print(rendered)
        _print_source_scaffold_audit(payload)
        return 0

    try:
        catalog_path.write_text(rendered, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write source catalog {catalog_path}: {exc}", file=sys.stderr)
        return 1
    print(f"Updated: {catalog_path}")
    _print_source_scaffold_audit(payload)
    return 0


def _cmd_entity_scaffold(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    try:
        metadata = _parse_metadata_values(args.metadata)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    entity = {
        "id": args.entity_id,
        "display_name": args.display_name,
        "aliases": args.alias or [],
        "metadata": metadata,
    }
    groups = {key: list(value) for key, value in bundle.tenant.entities.groups.items()}
    group_entities = list(groups.get(args.group, []))
    exists = any(item.get("id") == args.entity_id for item in group_entities)
    if exists and not args.replace:
        print(
            f"ERROR: Entity {args.entity_id} already exists in group {args.group}. Use --replace to replace it.",
            file=sys.stderr,
        )
        return 1
    groups[args.group] = [item for item in group_entities if item.get("id") != args.entity_id]
    groups[args.group].append(entity)
    tenant_payload = bundle.tenant.model_dump(mode="json", exclude_none=True)
    tenant_payload.setdefault("entities", {}).setdefault("groups", {})
    tenant_payload["entities"]["groups"] = groups
    tenant_path = DynamicPlatformPaths.from_root(args.config_root).tenant_path(bundle.tenant.tenant_key)
    rendered = yaml.safe_dump(tenant_payload, sort_keys=False, allow_unicode=True)
    if args.dry_run:
        print(f"Would update: {tenant_path}")
        print(rendered)
        return 0

    try:
        tenant_path.write_text(rendered, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write tenant profile {tenant_path}: {exc}", file=sys.stderr)
        return 1
    reloaded = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = validate_bundle(reloaded)
    if not report.ok:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        print("ERROR: Updated tenant profile did not pass validation.", file=sys.stderr)
        return 1
    print(f"Updated: {tenant_path}")
    print(f"Entity added: {args.group}/{args.entity_id}")
    return 0


def _cmd_decision_case_scaffold(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    fixture_path = Path(args.fixture) if args.fixture else default_shadow_fixture_path(args.tenant)
    payload = _load_or_new_shadow_fixture(fixture_path, args.tenant)
    cases = list(payload.get("cases") or [])
    exists = any((case.get("id") or case.get("case_id")) == args.case_id for case in cases)
    if exists and not args.replace:
        print(f"ERROR: Decision case {args.case_id} already exists. Use --replace to replace it.", file=sys.stderr)
        return 1
    new_case = {
        "id": args.case_id,
        "query": args.query,
        "expected_capabilities": args.expected_capability,
        "expected_agents": args.expected_agent or [],
        "expected_specialists": args.expected_specialist or [],
        "expected_source_families": args.expected_source_family or [],
        "expected_source_owners": args.expected_source_owner or [],
        "expected_authority_levels": args.expected_authority_level or [],
        "notes": args.notes,
    }
    if args.expected_final_owner:
        new_case["expected_final_owner"] = args.expected_final_owner
    cases = [case for case in cases if (case.get("id") or case.get("case_id")) != args.case_id]
    cases.append(new_case)
    payload["cases"] = cases

    report = compare_shadow_decisions(
        bundle,
        [ShadowDecisionCase.from_dict(new_case)],
        fixture_path=fixture_path,
    )
    if not report.ok:
        print(json.dumps({"case": new_case, "shadow_decisions": report.to_dict()}, ensure_ascii=False, indent=2))
        print("ERROR: Decision case is not represented by the dynamic profile; fixture was not written.", file=sys.stderr)
        return 1

    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.dry_run:
        print(f"Would update: {fixture_path}")
        print(serialized)
        _print_shadow_decisions(report.to_dict())
        return 0

    try:
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text(serialized, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write fixture {fixture_path}: {exc}", file=sys.stderr)
        return 1
    print(f"Updated: {fixture_path}")
    _print_shadow_decisions(report.to_dict())
    return 0


def _cmd_onboarding_preview(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    content = build_onboarding_preview(bundle)
    if args.output:
        output_path = Path(args.output)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: Could not write onboarding preview {output_path}: {exc}", file=sys.stderr)
            return 1
        print(f"Onboarding preview written: {output_path}")
    else:
        print(content)
    return 0


def _cmd_safety_audit(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = run_safety_audit(
        bundle,
        config_root=args.config_root,
        env_file=args.env_file,
        package_dir=args.package_dir,
        require_quality_gates=not args.allow_missing_shadow,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_safety_audit(payload)
    return 0 if report.ok else 1


def _cmd_shadow_runtime(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    decision = build_shadow_runtime_decision(
        bundle,
        query=args.query,
        requested_capabilities=args.capability,
    )
    payload = decision.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_shadow_runtime(payload)
    return 0 if payload.get("selected_capabilities") else 1


def _cmd_shadow_runtime_replay(args: argparse.Namespace) -> int:
    bundle = load_tenant_bundle(args.tenant, config_root=args.config_root)
    report = run_shadow_runtime_replay(
        bundle,
        fixture_path=args.fixture,
        match_mode=args.match_mode,
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_shadow_runtime_replay(payload)
    return 0 if report.ok else 1


def _load_or_new_shadow_fixture(path: Path, tenant_key: str) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": 1,
            "tenant_key": tenant_key,
            "description": "Expected dynamic tenant decision contracts.",
            "cases": [],
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DynamicPlatformLoadError(f"JSON parse error in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DynamicPlatformLoadError(f"Shadow decision fixture must be a JSON object: {path}")
    payload.setdefault("schema_version", 1)
    payload.setdefault("tenant_key", tenant_key)
    payload.setdefault("description", "Expected dynamic tenant decision contracts.")
    payload.setdefault("cases", [])
    if not isinstance(payload["cases"], list):
        raise DynamicPlatformLoadError(f"Shadow decision fixture cases must be a list: {path}")
    return payload


def _build_source_catalog_entry(args: argparse.Namespace, bundle: DynamicPlatformBundle) -> SourceCatalogEntry:
    metadata = _parse_metadata_values(args.metadata)
    authority = args.authority_level or _default_authority_for_adapter(args.adapter)
    if not authority:
        raise ValueError(f"No default authority_level for adapter {args.adapter}; pass --authority-level.")
    return SourceCatalogEntry(
        source_id=args.source_id,
        adapter=args.adapter,
        domain=bundle.tenant.domain_pack,
        owner_agent=args.owner_agent,
        source_family=args.source_family,
        capabilities=args.capability,
        entity_scope=EntityScope(
            type=args.entity_scope_type,
            entity_group=args.entity_group,
            entity_ids=args.entity_id or [],
        ),
        authority_level=authority,
        path=args.path,
        url=args.url,
        collection=args.collection,
        enabled=not args.disabled,
        metadata=metadata,
    )


def _parse_metadata_values(raw_values: list[str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for raw in raw_values:
        if "=" not in raw:
            raise ValueError(f"metadata value must be KEY=VALUE: {raw}")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"metadata key cannot be empty: {raw}")
        metadata[key] = value.strip()
    return metadata


def _default_authority_for_adapter(adapter: str) -> str | None:
    return {
        "pdf_document": "official_policy",
        "docx_document": "official_policy",
        "web_page": "department_document",
        "announcement_page": "official_announcement",
        "calendar_pdf": "official_structured",
        "structured_csv": "official_structured",
        "sql_table": "official_structured",
        "api_endpoint": "official_structured",
        "slack_uploaded_file": "uploaded_user_context",
        "ocr_document": "uploaded_user_context",
    }.get(adapter)


def _build_pack_skeleton_files(args: argparse.Namespace) -> dict[Path, str]:
    paths = DynamicPlatformPaths.from_root(args.config_root)
    capability_pairs = [_parse_id_label(value) for value in (args.capability or [])]
    agent_pairs = [_parse_id_label(value) for value in (args.agent or [])]
    if not capability_pairs:
        capability_pairs = [
            ("policy_qa", "Policy QA"),
            ("contact_lookup", "Contact Lookup"),
        ]
    if not agent_pairs:
        agent_pairs = [("support", "Support")]
    capability_ids = [capability_id for capability_id, _ in capability_pairs]

    domain_payload = {
        "schema_version": 1,
        "domain_pack": args.domain,
        "display_name": args.domain_display_name,
        "description": "Generated draft domain pack. Edit capabilities before production use.",
        "capabilities": [
            {
                "capability_id": capability_id,
                "display_name": label,
                "description": f"{label} capability.",
                "core_capability": capability_id,
                "answer_mode": "rag",
            }
            for capability_id, label in capability_pairs
        ],
    }
    agent_payload = {
        "schema_version": 1,
        "agent_pack": args.agent_pack,
        "display_name": args.agent_pack_display_name,
        "domain_pack": args.domain,
        "agents": [
            {
                "agent_id": agent_id,
                "display_name": label,
                "role": "service_agent",
                "capabilities": list(capability_ids),
                "specialists": [],
                "source_families": [],
                "final_owner_for": [],
                "llm_allowed": True,
                "deterministic_allowed": True,
            }
            for agent_id, label in agent_pairs
        ],
    }
    return {
        paths.domain_pack_path(args.domain): yaml.safe_dump(domain_payload, sort_keys=False, allow_unicode=True),
        paths.agent_pack_path(args.agent_pack): yaml.safe_dump(agent_payload, sort_keys=False, allow_unicode=True),
    }


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
            f"python -m scripts.tenant source-ingestion-plan --tenant {args.tenant}\n"
            "python -m scripts.tenant genericity-audit\n"
            f"python -m scripts.tenant shadow-decisions --tenant {args.tenant}\n"
            f"python -m scripts.tenant quality-gates --tenant {args.tenant}\n"
            f"python -m scripts.tenant runtime-plan --tenant {args.tenant}\n"
            f"python -m scripts.tenant runtime-adapter-contract --tenant {args.tenant}\n"
            f"python -m scripts.tenant runtime-env-check --tenant {args.tenant} --env-file .env\n"
            f"python -m scripts.tenant docker-plan --tenant {args.tenant}\n"
            f"python -m scripts.tenant readiness --tenant {args.tenant} --env-file .env\n"
            "python -m scripts.tenant audit-all\n"
            f"python -m scripts.tenant package --tenant {args.tenant}\n"
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


def _parse_id_label(raw: str) -> tuple[str, str]:
    if ":" in raw:
        item_id, label = raw.split(":", 1)
        item_id = item_id.strip()
        label = label.strip()
    else:
        item_id = raw.strip()
        label = item_id.replace("_", " ").replace(".", " ").title()
    return item_id, label or item_id


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


def _print_contract_matrix(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print("\nCapability contract matrix:")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Capabilities: "
        f"{summary.get('capability_count', 0)} total, "
        f"warnings={summary.get('warning_count', 0)}"
    )
    for row in report.get("rows") or []:
        agents = ", ".join(row.get("agents") or []) or "-"
        sources = ", ".join(row.get("source_ids") or []) or "-"
        final_owners = ", ".join(row.get("final_owner_candidates") or []) or "-"
        operation_refs = row.get("operation_owner_refs") or {}
        operation_text = (
            "; ".join(
                f"{agent}({', '.join(refs)})"
                for agent, refs in sorted(operation_refs.items())
            )
            or "-"
        )
        print(
            f"- {row['capability_id']} [{row['answer_mode']}]: "
            f"agents={agents} sources={sources} final_owner={final_owners} operation_owner_refs={operation_text}"
        )
        for warning in row.get("warnings") or []:
            print(f"  WARNING: {warning}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


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


def _print_source_scaffold_audit(payload: dict[str, Any]) -> None:
    source = payload.get("source") or {}
    validation = payload.get("validation") or {}
    audit = payload.get("source_audit") or {}
    print("\nSource scaffold:")
    print(f"- source_id: {source.get('source_id')}")
    print(f"- adapter: {source.get('adapter')}")
    print(f"- owner_agent: {source.get('owner_agent')}")
    print(f"- capabilities: {', '.join(source.get('capabilities') or [])}")
    print(f"- validation: {'OK' if validation.get('ok') else 'FAILED'}")
    print(f"- source audit: {'OK' if audit.get('ok') else 'FAILED'}")


def _print_source_ingestion_plan(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print("\nSource ingestion plan:")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Sources: "
        f"{summary.get('enabled_source_count', 0)}/{summary.get('source_count', 0)} enabled, "
        f"live connectors={summary.get('live_connector_required_count', 0)}, "
        f"preindex={summary.get('preindex_required_count', 0)}, "
        f"warnings={summary.get('warning_count', 0)}"
    )
    print("\nSteps:")
    for step in report.get("steps") or []:
        enabled = "enabled" if step.get("enabled") else "disabled"
        live = " live-connector" if step.get("live_connector_required") else ""
        index_target = step.get("index_target") or "-"
        print(
            f"- {step['source_id']} [{step['adapter']}] action={step['action']} "
            f"owner={step['owner_agent']} target={index_target} {enabled}{live}"
        )
        for warning in step.get("warnings") or []:
            print(f"  WARNING: {warning}")
        for note in step.get("notes") or []:
            print(f"  NOTE: {note}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_retrieval_contract(report: dict[str, Any]) -> None:
    print("\nRetrieval contract:")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Current mode: {report.get('current_mode')}")
    print(f"Dedicated indexed/vector retrieval wired: {report.get('dedicated_retrieval_service_wired')}")
    print(f"Enabled sources: {report.get('enabled_source_count')}/{report.get('source_count')}")
    print("Tenant collections:")
    for collection in report.get("tenant_collections") or []:
        print(f"- {collection}")
    if report.get("warnings"):
        print("Warnings:")
        for warning in report["warnings"]:
            print(f"- {warning}")
    print("Required live capabilities:")
    for capability in report.get("required_live_capabilities") or []:
        print(f"- {capability}")


def _print_model_runtime_contract(report: dict[str, Any]) -> None:
    print("\nModel runtime contract:")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Safety: {report.get('safety_status')}")
    model_cache = report.get("model_cache") or {}
    reranker = report.get("reranker_policy") or {}
    precision = report.get("precision_policy") or {}
    offline = report.get("offline_generation") or {}
    print(f"Model cache env: {model_cache.get('host_dir_env')}={model_cache.get('default_host_dir')}")
    print(f"Current configured reranker: {reranker.get('current_configured_model')}")
    print(f"Current configured dtype: {reranker.get('current_configured_torch_dtype')}")
    print(f"Rollback baseline: {reranker.get('rollback_baseline')}")
    print(f"Primary BGE candidate: {reranker.get('primary_bge_candidate')}")
    print(f"Turkish shadow candidate: {reranker.get('turkish_shadow_candidate')}")
    print(f"FP16 allowed only on CUDA: {precision.get('fp16_allowed_only_on_cuda')}")
    print(f"Downloads models during package generation: {offline.get('downloads_models')}")
    if report.get("warnings"):
        print("Warnings:")
        for warning in report["warnings"]:
            print(f"- {warning}")


def _print_genericity_audit(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Genericity audit: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Scanned: "
        f"{summary.get('scanned_file_count', 0)} files, "
        f"errors={summary.get('error_count', 0)}, "
        f"warnings={summary.get('warning_count', 0)}, "
        f"allowed_mentions={summary.get('allowed_mention_count', 0)}"
    )
    for issue in report.get("errors") or []:
        print(f"ERROR {issue['code']} {issue['path']}:{issue['line']} [{issue['term']}]: {issue['message']}")
    for issue in report.get("warnings") or []:
        print(f"WARNING {issue['code']} {issue['path']}:{issue['line']} [{issue['term']}]: {issue['message']}")
    print("\nAllowed protection references:")
    allowed = report.get("allowed_mentions") or []
    if not allowed:
        print("- none")
    for issue in allowed[:12]:
        print(f"- {issue['path']}:{issue['line']} [{issue['term']}]")
    if len(allowed) > 12:
        print(f"- ... {len(allowed) - 12} more")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_portfolio_audit(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant portfolio audit: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Tenants: "
        f"{summary.get('passed', 0)}/{summary.get('tenant_count', 0)} passed "
        f"({summary.get('failed', 0)} failed)"
    )
    strategy_counts = summary.get("runtime_strategy_counts") or {}
    if strategy_counts:
        print("Runtime strategies:")
        for strategy, count in strategy_counts.items():
            print(f"- {strategy}: {count}")
    genericity = report.get("genericity_audit") or {}
    genericity_summary = genericity.get("summary") or {}
    print(
        "Genericity: "
        f"{'OK' if genericity.get('ok') else 'FAILED'} "
        f"errors={genericity_summary.get('error_count', 0)}"
    )
    print("\nTenant records:")
    for record in report.get("records") or []:
        status = "OK" if record.get("ok") else "FAILED"
        runtime = record.get("runtime_strategy") or "-"
        adapter = (record.get("runtime_adapter_contract") or {}).get("adapter_status") or "-"
        quality = record.get("quality_gates") or {}
        quality_summary = quality.get("summary") or {}
        print(
            f"- {record['tenant_key']}: {status} runtime={runtime} adapter={adapter} "
            f"quality_failed={quality_summary.get('failed', '-')}"
        )
        if record.get("error"):
            print(f"  ERROR: {record['error']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_registry_catalog(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Dynamic platform registry: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Counts: "
        f"domains={summary.get('domain_pack_count', 0)} "
        f"agent_packs={summary.get('agent_pack_count', 0)} "
        f"source_catalogs={summary.get('source_catalog_count', 0)} "
        f"tenants={summary.get('tenant_count', 0)}"
    )
    strategy_counts = summary.get("runtime_strategy_counts") or {}
    if strategy_counts:
        print("Runtime strategies:")
        for strategy, count in strategy_counts.items():
            print(f"- {strategy}: {count}")
    print("\nDomain packs:")
    for domain in report.get("domain_packs") or []:
        capabilities = ", ".join(domain.get("capabilities") or []) or "-"
        print(f"- {domain['domain_pack']}: capabilities={domain['capability_count']} [{capabilities}]")
    print("\nAgent packs:")
    for pack in report.get("agent_packs") or []:
        status = "domain-ok" if pack.get("domain_pack_exists") else "domain-missing"
        agents = ", ".join(pack.get("agents") or []) or "-"
        print(f"- {pack['agent_pack']} -> {pack['domain_pack']} ({status}) agents=[{agents}]")
    print("\nTenants:")
    for tenant in report.get("tenants") or []:
        validation = "validation-ok" if tenant.get("validation_ok") else "validation-failed"
        refs = []
        for key, label in (
            ("domain_pack_exists", "domain"),
            ("agent_pack_exists", "agent_pack"),
            ("source_catalog_exists", "source_catalog"),
            ("source_catalog_tenant_matches", "source_owner"),
        ):
            refs.append(f"{label}={'ok' if tenant.get(key) else 'missing'}")
        print(
            f"- {tenant['tenant_key']} [{tenant['runtime_strategy']}]: "
            f"domain={tenant['domain_pack']} agent_pack={tenant['agent_pack']} "
            f"source_catalog={tenant['source_catalog']} {validation} {' '.join(refs)}"
        )
    print("\nErrors:")
    errors = report.get("errors") or []
    if not errors:
        print("- none")
    for issue in errors:
        path = f" [{issue['path']}]" if issue.get("path") else ""
        print(f"- {issue['code']}{path}: {issue['message']}")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if not warnings:
        print("- none")
    for issue in warnings:
        path = f" [{issue['path']}]" if issue.get("path") else ""
        print(f"- {issue['code']}{path}: {issue['message']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


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


def _print_runtime_adapter_contract(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(f"Adapter status: {report['adapter_status']}")
    print(f"Dynamic live binding allowed: {'yes' if report['dynamic_live_binding_allowed'] else 'no'}")
    print(
        "Classic runtime owner: "
        f"{'yes' if report['classic_runtime_must_remain_owner'] else 'no'}"
    )
    print("\nAllowed modes:")
    for mode in report.get("allowed_modes", []):
        print(f"- {mode}")
    print("\nBlocked modes:")
    for mode in report.get("blocked_modes", []):
        print(f"- {mode}")
    print("\nTelemetry fields:")
    for field in report.get("telemetry_contract", []):
        print(f"- {field}")
    print("\nSafety requirements:")
    for requirement in report.get("safety_requirements", []):
        print(f"- {requirement}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_runtime_adapter_draft(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Adapter draft status: {report.get('telemetry', {}).get('adapter_status')}")
    print(f"Answer status: {report['answer_status']}")
    print(f"User-facing answer emitted: {'yes' if report.get('answer') else 'no'}")
    print(f"Capabilities: {', '.join(report.get('selected_capabilities') or []) or '-'}")
    print(f"Agents: {', '.join(report.get('agents') or []) or '-'}")
    print(f"Sources: {', '.join(report.get('sources') or []) or '-'}")
    print(f"Final owner: {report.get('final_owner') or '-'}")
    telemetry = report.get("telemetry") or {}
    print(f"Binding status: {telemetry.get('runtime_binding_status')}")
    print("\nSafety notes:")
    for note in report.get("safety_notes", []):
        print(f"- {note}")


def _print_runtime_adapter_implementation_plan(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime adapter implementation plan: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Implementation status: {report['implementation_status']}")
    print(f"Live binding allowed now: {'yes' if report['live_binding_allowed_now'] else 'no'}")
    print(
        "Phases: "
        f"{summary.get('phase_count', 0)} total, "
        f"ready={len(summary.get('ready_now') or [])}, "
        f"future={len(summary.get('future_work') or [])}"
    )
    print("\nPhase overview:")
    for phase in report.get("phases") or []:
        print(f"- {phase['phase_id']}: {phase['status']} - {phase['title']}")
        for gate in (phase.get("required_gates") or [])[:3]:
            print(f"  gate: {gate}")
    print("\nNon-goals:")
    for item in report.get("non_goals") or []:
        print(f"- {item}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_runtime_activation_guard(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(f"Runtime activation guard: {'OK' if report['live_binding_allowed'] else 'BLOCKED'}")
    print(f"Status: {report['status']}")
    print(f"Live binding allowed: {'yes' if report.get('live_binding_allowed') else 'no'}")
    print("\nPassed gates:")
    passed = report.get("passed_gates") or []
    if not passed:
        print("- none")
    for gate in passed:
        print(f"- {gate}")
    print("\nBlockers:")
    blockers = report.get("blockers") or []
    if not blockers:
        print("- none")
    for blocker in blockers:
        print(f"- {blocker}")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if not warnings:
        print("- none")
    for warning in warnings:
        print(f"- {warning}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_runtime_isolation_contract(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(f"Runtime isolation contract: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Live runtime allowed: {'yes' if report.get('live_runtime_allowed') else 'no'}")
    print("\nNamespaces:")
    for namespace in report.get("namespaces") or []:
        shared = "shared" if namespace.get("shared_between_tenants") else "tenant-scoped"
        shadow_writes = "yes" if namespace.get("writes_allowed_in_shadow") else "no"
        print(
            f"- {namespace['namespace_id']}: {namespace['prefix']} "
            f"({shared}, shadow writes={shadow_writes})"
        )
    print("\nUploaded context sources:")
    uploaded = report.get("uploaded_context_sources") or []
    if not uploaded:
        print("- none")
    for source in uploaded:
        scoped = "yes" if source.get("runtime_scoped") else "no"
        print(f"- {source['source_id']}: {source['adapter']} runtime_scoped={scoped}")
    print("\nChecks:")
    for check in report.get("checks") or []:
        print(f"- {check['check_id']}: {'OK' if check.get('ok') else 'FAILED'} - {check.get('message')}")
    print("\nRequired before live runtime:")
    for item in report.get("required_before_live_runtime") or []:
        print(f"- {item}")
    print("\nForbidden in shadow:")
    for item in report.get("forbidden_in_shadow") or []:
        print(f"- {item}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_runtime_namespace_preview(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(f"Runtime namespace preview: {'OK' if report.get('ok') else 'FAILED'}")
    print("\nExpected prefixes:")
    for kind, prefix in (report.get("expected_prefixes") or {}).items():
        print(f"- {kind}: {prefix}")
    print("\nSample keys:")
    for item in report.get("sample_keys") or []:
        shared = "shared" if item.get("shared_between_tenants") else "tenant-scoped"
        print(f"- {item['kind']}: {item['key']} ({shared})")
    validation = report.get("validation") or {}
    print("\nValidation:")
    print(f"- ok: {'yes' if validation.get('ok') else 'no'}")
    errors = validation.get("errors") or []
    if errors:
        for error in errors:
            print(f"- error: {error}")
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


def _print_secrets_contract(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(f"Secret values allowed in package: {'yes' if report['secret_values_allowed_in_package'] else 'no'}")
    print(f"Smoke test allowed without LLM secret: {'yes' if report['smoke_test_allowed_without_llm_secret'] else 'no'}")
    print(f"Full answering requires LLM secret: {'yes' if report['full_answering_requires_llm_secret'] else 'no'}")
    print("\nSecret groups:")
    for group in report.get("groups") or []:
        keys = ", ".join(group.get("keys") or [])
        print(f"- {group['group_id']}: {group['mode']} [{keys}]")
    print("\nRequirements:")
    for requirement in report.get("requirements") or []:
        required_for = ", ".join(requirement.get("required_for") or [])
        print(f"- {requirement['key']}: {requirement['category']} ({required_for})")
    print("\nForbidden actions:")
    for item in report.get("forbidden_actions") or []:
        print(f"- {item}")
    print("\nNotes:")
    for note in report.get("notes") or []:
        print(f"- {note}")


def _print_pilot_secret_scaffold(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Pilot secret scaffold: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Mode: {report['mode']}")
    print(f"Include Slack: {'yes' if report.get('include_slack') else 'no'}")
    print(f"Output directory: {report['output_dir']}")
    print(f"Env file: {report['env_path']}")
    print(f"Manifest: {report['manifest_path']}")
    print("\nChecks:")
    for key, value in report.get("checks", {}).items():
        print(f"- {key}: {'yes' if value else 'no'}")
    print("\nFiles:")
    for path in report.get("files") or []:
        print(f"- {path}")
    print("\nNotes:")
    for note in report.get("notes") or []:
        print(f"- {note}")


def _print_secret_readiness(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Mode: {report['mode']}")
    print(f"Secret readiness: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Env source: {report['env_source']}")
    print(f"Include Slack: {'yes' if report.get('include_slack') else 'no'}")
    print("\nGroups:")
    for group in report.get("group_statuses") or []:
        status = "OK" if group.get("ok") else "FAILED"
        required = "required" if group.get("required") else "optional"
        present = ", ".join(group.get("present_keys") or []) or "-"
        print(f"- {group['group_id']}: {status} ({required}, mode={group['mode']}, present={present})")
    print("\nKeys:")
    for status in report.get("key_statuses") or []:
        required = "required" if status.get("required") else "optional"
        present = "present" if status.get("present") else "missing"
        non_empty = "non-empty" if status.get("non_empty") else "empty"
        placeholder = ", placeholder" if status.get("placeholder") else ""
        print(f"- {status['key']}: {required}, {present}, {non_empty}{placeholder}")
    for issue in report.get("errors") or []:
        scope = issue.get("key") or issue.get("group_id") or "-"
        print(f"ERROR {issue['code']} {scope}: {issue['message']}")
    for issue in report.get("warnings") or []:
        scope = issue.get("key") or issue.get("group_id") or "-"
        print(f"WARNING {issue['code']} {scope}: {issue['message']}")
    print("\nNotes:")
    for note in report.get("notes") or []:
        print(f"- {note}")


def _print_docker_plan(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(f"Single-instance env ready: {'yes' if report['single_instance_env_ready'] else 'no'}")
    print(f"Side-by-side Docker ready: {'yes' if report['side_by_side_ready'] else 'no'}")
    print(f"Live dynamic runtime ready: {'yes' if report['live_dynamic_runtime_ready'] else 'no'}")
    print(f"Suggested env file: {report['suggested_env_file']}")
    print("\nCompose files:")
    for path in report.get("compose_files", []):
        print(f"- {path}")
    print("\nBlockers:")
    blockers = report.get("blockers") or []
    if not blockers:
        print("- none")
    for issue in blockers:
        scope = issue.get("service") or issue.get("file") or "-"
        value = f" [{issue['value']}]" if issue.get("value") else ""
        print(f"- {issue['code']} {scope}{value}: {issue['message']}")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if not warnings:
        print("- none")
    for issue in warnings:
        scope = issue.get("service") or issue.get("file") or "-"
        value = f" [{issue['value']}]" if issue.get("value") else ""
        print(f"- {issue['code']} {scope}{value}: {issue['message']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")
    print("\nSuggested commands:")
    for command in report.get("suggested_commands", []):
        print(f"- {command}")


def _print_readiness(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Readiness: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Profile ready: {'yes' if report['profile_ready'] else 'no'}")
    print(f"Runtime env ready: {'yes' if report['runtime_env_ready'] else 'no'}")
    print(f"Docker single-instance ready: {'yes' if report['docker_single_instance_ready'] else 'no'}")
    print(f"Docker side-by-side ready: {'yes' if report['docker_side_by_side_ready'] else 'no'}")
    print(f"Live dynamic runtime ready: {'yes' if report['live_dynamic_runtime_ready'] else 'no'}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_bootstrap_plan(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Bootstrap plan: {'OK' if report['ok'] else 'NEEDS ATTENTION'}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(
        "Topology: "
        f"domain={summary.get('domain_pack')} "
        f"agent_pack={summary.get('agent_pack')} "
        f"source_catalog={summary.get('source_catalog')}"
    )
    print(
        "Coverage: "
        f"capabilities={summary.get('capability_count', 0)} "
        f"agents={summary.get('agent_count', 0)} "
        f"sources={summary.get('enabled_source_count', 0)}/{summary.get('source_count', 0)} "
        f"blockers={summary.get('blocker_count', 0)}"
    )
    print("\nSteps:")
    for step in report.get("steps") or []:
        print(f"- {step['step_id']}: {step['status']} - {step['title']}")
        for blocker in step.get("blockers") or []:
            print(f"  BLOCKER: {blocker}")
    print("\nSafe next commands:")
    for command in report.get("safe_next_commands") or []:
        print(f"- {command}")
    optional_smoke = report.get("optional_no_download_smoke_commands") or []
    if optional_smoke:
        print("\nOptional no-download smoke commands:")
        for command in optional_smoke:
            print(f"- {command}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_safety_audit(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Safety audit: {'OK' if report['ok'] else 'FAILED'}")
    print("\nChecks:")
    for key, value in report.get("checks", {}).items():
        print(f"- {key}: {'yes' if value else 'no'}")
    print("\nErrors:")
    errors = report.get("errors") or []
    if not errors:
        print("- none")
    for issue in errors:
        path = f" [{issue['path']}]" if issue.get("path") else ""
        print(f"- {issue['code']}{path}: {issue['message']}")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if not warnings:
        print("- none")
    for issue in warnings:
        path = f" [{issue['path']}]" if issue.get("path") else ""
        print(f"- {issue['code']}{path}: {issue['message']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_shadow_runtime(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime strategy: {report['runtime_strategy']}")
    print(f"Binding status: {report['runtime_binding_status']}")
    print(f"Match mode: {report['match_mode']}")
    print(f"Confidence: {report['confidence']}")
    print(f"Capabilities: {', '.join(report.get('selected_capabilities') or []) or '-'}")
    print(f"Agents: {', '.join(report.get('agents') or []) or '-'}")
    print(f"Specialists: {', '.join(report.get('specialists') or []) or '-'}")
    print(f"Sources: {', '.join(report.get('source_ids') or []) or '-'}")
    print(f"Final owner candidates: {', '.join(report.get('final_owner_candidates') or []) or '-'}")
    print("\nExecution plan:")
    if not report.get("execution_plan"):
        print("- none")
    for step in report.get("execution_plan") or []:
        suffix = " final-owner-candidate" if step.get("final_owner_candidate") else ""
        print(f"- step {step['step']}: {step['agent']} ({step['role']}){suffix}")
    print("\nWarnings:")
    if not report.get("warnings"):
        print("- none")
    for warning in report.get("warnings") or []:
        print(f"- {warning}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_shadow_runtime_replay(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Shadow runtime replay: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Match mode: {report['match_mode']}")
    print(f"Binding status: {report['runtime_binding_status']}")
    print(f"Fixture: {report['fixture_path']}")
    print(
        "Cases: "
        f"{summary.get('passed', 0)}/{summary.get('case_count', 0)} passed "
        f"({summary.get('failed', 0)} failed)"
    )
    for record in report.get("records") or []:
        status = "OK" if record.get("ok") else "FAILED"
        capabilities = ", ".join(record.get("selected_capabilities") or []) or "-"
        agents = ", ".join(record.get("agents") or []) or "-"
        print(f"- {record.get('case_id')}: {status} capabilities=[{capabilities}] agents=[{agents}]")
        for issue in record.get("issues") or []:
            print(f"  {issue['severity'].upper()} {issue['code']}: {issue['message']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_package(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Package directory: {report['output_dir']}")
    print("\nFiles:")
    for path in report.get("files", []):
        print(f"- {path}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_package_portfolio_audit(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant package portfolio audit: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Package root: {report.get('package_root')}")
    print(
        "Packages: "
        f"{summary.get('passed', 0)}/{summary.get('tenant_count', 0)} passed "
        f"({summary.get('failed', 0)} failed)"
    )
    print("\nTenant package records:")
    for record in report.get("records") or []:
        status = "OK" if record.get("ok") else "FAILED"
        print(f"- {record['tenant_key']}: {status} package={record.get('package_dir')}")
        if record.get("error"):
            print(f"  ERROR: {record['error']}")
        safety = record.get("safety_audit") or {}
        checks = safety.get("checks") or {}
        for key in (
            "package_manifest_hashes_ok",
            "package_config_snapshot_hashes_match",
            "package_handoff_index_offline_safe",
            "package_portability_audit_ok",
            "package_compose_manifest_draft",
            "package_compose_isolation_ok",
            "classic_runtime_import_isolated",
        ):
            if key in checks:
                print(f"  {key}: {'yes' if checks[key] else 'no'}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_creation_rehearsal(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Creation rehearsal: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Output directory: {report.get('output_dir')}")
    print(f"Rehearsal config root: {report.get('rehearsal_config_root')}")
    print(f"Package directory: {report.get('package_dir')}")
    print(
        "Topology: "
        f"domain={summary.get('domain_pack', '-')} "
        f"agent_pack={summary.get('agent_pack', '-')} "
        f"sources={summary.get('enabled_source_count', 0)}/{summary.get('source_count', 0)} "
        f"runtime={summary.get('runtime_strategy', '-')}"
    )
    print("\nChecks:")
    for key, value in report.get("checks", {}).items():
        print(f"- {key}: {'yes' if value else 'no'}")
    print("\nErrors:")
    errors = report.get("errors") or []
    if not errors:
        print("- none")
    for issue in errors:
        path = f" [{issue['path']}]" if issue.get("path") else ""
        print(f"- {issue['code']}{path}: {issue['message']}")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if not warnings:
        print("- none")
    for issue in warnings:
        path = f" [{issue['path']}]" if issue.get("path") else ""
        print(f"- {issue['code']}{path}: {issue['message']}")
    print("\nArtifacts:")
    for path in (report.get("artifacts") or [])[:12]:
        print(f"- {path}")
    if len(report.get("artifacts") or []) > 12:
        print(f"- ... {len(report.get('artifacts') or []) - 12} more")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_handoff_readiness(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Dynamic platform handoff readiness: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Package root: {report.get('package_root')}")
    print(
        "Checks: "
        f"registry={'OK' if summary.get('registry_ok') else 'FAILED'} "
        f"portfolio={'OK' if summary.get('portfolio_ok') else 'FAILED'} "
        f"portability={'OK' if summary.get('portability_ok') else 'FAILED'} "
        f"packages={'OK' if summary.get('package_audit_ok') else 'FAILED'} "
        f"compose_iso={'OK' if summary.get('package_compose_isolation_ok') else 'FAILED'} "
        f"adapter_smoke={summary.get('adapter_draft_smoke_passed', 0)}/"
        f"{summary.get('tenant_count', 0)}"
    )
    print("\nAdapter draft smoke:")
    for record in report.get("adapter_draft_smoke") or []:
        status = "OK" if record.get("ok") else "FAILED"
        caps = ", ".join(record.get("requested_capabilities") or []) or "-"
        preview = record.get("preview") or {}
        refusal = record.get("live_refusal") or {}
        print(
            f"- {record['tenant_key']}: {status} capabilities=[{caps}] "
            f"preview={preview.get('answer_status', '-')} "
            f"live={refusal.get('answer_status', '-')}"
        )
        if record.get("error"):
            print(f"  ERROR: {record['error']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_completion_report(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Dynamic platform completion: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Status: {report.get('status')}")
    print(f"Config root: {report.get('config_root')}")
    print(f"Package root: {report.get('package_root')}")
    print(f"Output root: {report.get('output_root')}")
    print(
        "Summary: "
        f"passed={summary.get('passed', 0)}/{summary.get('gate_count', 0)} "
        f"completion={summary.get('offline_completion_percent', 0)}% "
        f"tenants={summary.get('configured_tenant_count', 0)} "
        f"packages={summary.get('package_tenant_count', 0)} "
        f"live_authorized={'yes' if summary.get('live_runtime_authorized') else 'no'}"
    )
    print("\nGates:")
    for gate in report.get("gates") or []:
        print(f"- {gate['gate_id']}: {'OK' if gate.get('ok') else 'FAILED'} - {gate.get('message')}")
    print("\nBlocked live items:")
    for item in report.get("blocked_live_items") or []:
        print(f"- {item}")
    print("\nSafe next commands:")
    for command in report.get("safe_next_commands") or []:
        print(f"- {command}")
    optional_smoke = report.get("optional_no_download_smoke_commands") or []
    if optional_smoke:
        print("\nOptional no-download smoke commands:")
        for command in optional_smoke:
            print(f"- {command}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_preflight(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Dynamic platform preflight: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Status: {report.get('status')}")
    print(f"Config root: {report.get('config_root')}")
    print(f"Package root: {report.get('package_root')}")
    print(f"Output root: {report.get('output_root')}")
    print(
        "Summary: "
        f"tenants={summary.get('tenant_count', 0)} "
        f"compose_drafts={summary.get('compose_draft_passed', 0)}/"
        f"{summary.get('compose_draft_count', 0)} "
        f"completion={summary.get('completion_status', '-')} "
        f"live_authorized={'yes' if summary.get('live_runtime_authorized') else 'no'}"
    )
    print(f"Manual Docker config required: {'yes' if summary.get('manual_docker_config_required') else 'no'}")
    print(f"Docker started: {'yes' if summary.get('docker_started') else 'no'}")
    print(f"Build or pull run: {'yes' if summary.get('build_or_pull_run') else 'no'}")
    print(f"Live runtime authorized: {'yes' if summary.get('live_runtime_authorized') else 'no'}")
    print("\nGates:")
    for gate in report.get("gates") or []:
        print(f"- {gate['gate_id']}: {'OK' if gate.get('ok') else 'FAILED'} - {gate.get('message')}")
    print("\nCompose drafts:")
    for record in report.get("tenant_compose_drafts") or []:
        print(f"- {record['tenant_key']}: {'OK' if record.get('ok') else 'FAILED'}")
        if record.get("error"):
            print(f"  ERROR: {record['error']}")
    print("\nManual docker compose config checks:")
    for command in report.get("manual_docker_config_checks") or []:
        print(f"- {command}")
    print("\nArtifacts:")
    for artifact in report.get("artifacts") or []:
        print(f"- {artifact}")
    print("\nBlocked live items:")
    for item in report.get("blocked_live_items") or []:
        print(f"- {item}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_compose_config_audit(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Compose config audit: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Runtime strategy: {report.get('runtime_strategy')}")
    print(f"Package directory: {report.get('package_dir')}")
    print(f"Default services: {', '.join(report.get('default_services') or []) or '-'}")
    print(f"Dynamic-agent profile services: {', '.join(report.get('dynamic_agent_services') or []) or '-'}")
    print("\nChecks:")
    for key, value in sorted((report.get("checks") or {}).items()):
        print(f"- {key}: {'yes' if value else 'no'}")
    print("\nErrors:")
    errors = report.get("errors") or []
    if errors:
        for issue in errors:
            suffix = f" [{issue.get('service')}]" if issue.get("service") else ""
            value = f" value={issue.get('value')}" if issue.get("value") else ""
            print(f"- {issue.get('code')}{suffix}: {issue.get('message')}{value}")
    else:
        print("- none")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if warnings:
        for issue in warnings:
            suffix = f" [{issue.get('service')}]" if issue.get("service") else ""
            value = f" value={issue.get('value')}" if issue.get("value") else ""
            print(f"- {issue.get('code')}{suffix}: {issue.get('message')}{value}")
    else:
        print("- none")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_runtime_smoke_readiness(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime smoke readiness: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Status: {report.get('status')}")
    print(f"Package directory: {report.get('package_dir')}")
    print(f"Image ref: {report.get('image_ref')}")
    print("\nGates:")
    for gate in report.get("gates") or []:
        print(f"- {gate['gate_id']}: {'OK' if gate.get('ok') else 'FAILED'} - {gate.get('message')}")
    print("\nBlockers:")
    blockers = report.get("blockers") or []
    if blockers:
        for blocker in blockers:
            print(f"- {blocker}")
    else:
        print("- none")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if warnings:
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("- none")
    print("\nSuggested commands:")
    for command in report.get("suggested_commands") or []:
        print(f"- {command}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_runtime_container_audit(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime container audit: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Runtime strategy: {report.get('runtime_strategy')}")
    print(f"Package directory: {report.get('package_dir')}")
    print(f"Expected default services: {', '.join(report.get('expected_default_services') or []) or 'none'}")
    print(f"Expected dynamic-agent services: {', '.join(report.get('expected_dynamic_agent_services') or []) or 'none'}")
    print("\nContainers:")
    containers = report.get("containers") or []
    if containers:
        for container in containers:
            command = " ".join(container.get("command") or [])
            print(
                f"- {container.get('name')}: service={container.get('service')} "
                f"image={container.get('image')} status={container.get('status')} command={command}"
            )
    else:
        print("- none")
    print("\nErrors:")
    errors = report.get("errors") or []
    if errors:
        for error in errors:
            print(f"- [{error.get('code')}] {error.get('message')} service={error.get('service')} value={error.get('value')}")
    else:
        print("- none")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if warnings:
        for warning in warnings:
            print(f"- [{warning.get('code')}] {warning.get('message')} service={warning.get('service')} value={warning.get('value')}")
    else:
        print("- none")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_runtime_query_smoke(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Runtime query smoke: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Status: {report.get('status')}")
    print(f"Endpoint: {report.get('endpoint')}")
    print(f"HTTP status: {report.get('http_status') or '-'}")
    print(f"Latency: {report.get('latency_ms') or '-'} ms")
    print(f"Answer status: {report.get('answer_status') or '-'}")
    print(f"Final owner: {report.get('final_owner') or '-'}")
    print(f"Capabilities: {', '.join(report.get('selected_capabilities') or []) or '-'}")
    print(f"Agents: {', '.join(report.get('agents') or []) or '-'}")
    print(f"Sources: {', '.join(report.get('sources') or []) or '-'}")
    print(f"Query: {report.get('query')}")
    print("\nAnswer preview:")
    print(report.get("answer_preview") or "-")
    print("\nErrors:")
    errors = report.get("errors") or []
    if errors:
        for error in errors:
            print(f"- {error}")
    else:
        print("- none")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if warnings:
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("- none")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_pilot_readiness(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Mode: {report['mode']}")
    print(f"Pilot readiness: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Status: {report.get('status')}")
    print(f"Package root: {report.get('package_root')}")
    print(f"Secrets env source: {report.get('secrets_env_source')}")
    print(f"Live binding allowed: {'yes' if report.get('live_binding_allowed') else 'no'}")
    print(
        "Summary: "
        f"preflight={'OK' if summary.get('preflight_ok') else 'FAILED'} "
        f"secrets={'OK' if summary.get('secret_readiness_ok') else 'FAILED'} "
        f"adapter_live_now={'yes' if summary.get('adapter_live_binding_allowed_now') else 'no'} "
        f"docker_started={'yes' if summary.get('docker_started') else 'no'} "
        f"build_or_pull={'yes' if summary.get('build_or_pull_run') else 'no'}"
    )
    print("\nGates:")
    for gate in report.get("gates") or []:
        print(f"- {gate['gate_id']}: {'OK' if gate.get('ok') else 'FAILED'} - {gate.get('message')}")
    print("\nBlockers:")
    blockers = report.get("blockers") or []
    if not blockers:
        print("- none")
    for blocker in blockers:
        print(f"- {blocker}")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if not warnings:
        print("- none")
    for warning in warnings:
        print(f"- {warning}")
    print("\nArtifacts:")
    for artifact in report.get("artifacts") or []:
        print(f"- {artifact}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_activation_checklist(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Activation checklist: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Status: {report.get('status')}")
    print(f"Package root: {report.get('package_root')}")
    print(f"Runtime secrets dir: {report.get('runtime_secrets_dir')}")
    print(f"Live runtime authorized: {'yes' if report.get('live_runtime_authorized') else 'no'}")
    print(
        "Summary: "
        f"offline={summary.get('offline_preparation_percent', 0)}% "
        f"pilot_prereq={summary.get('dynamic_pilot_prerequisite_percent', 0)}% "
        f"pilot_status={summary.get('dynamic_pilot_status', '-')} "
        f"warnings={summary.get('warning_count', 0)} "
        f"docker_started={'yes' if summary.get('docker_started') else 'no'} "
        f"build_or_pull={'yes' if summary.get('build_or_pull_run') else 'no'}"
    )
    print("\nSteps:")
    for step in report.get("steps") or []:
        print(
            f"- {step['step_id']}: {'OK' if step.get('ok') else 'FAILED'} "
            f"({step.get('severity')}, {step.get('status')}) - {step.get('message')}"
        )
    print("\nRemaining work:")
    remaining = report.get("remaining_work") or []
    if not remaining:
        print("- none")
    for item in remaining:
        print(f"- {item}")
    print("\nSafe next commands:")
    for command in report.get("safe_next_commands") or []:
        print(f"- {command}")
    print("\nArtifacts:")
    for artifact in report.get("artifacts") or []:
        print(f"- {artifact}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_compose_template(report: dict[str, Any]) -> None:
    print(f"Tenant: {report['tenant_key']}")
    print(f"Compose template directory: {report['output_dir']}")
    print("\nFiles:")
    for path in report.get("files", []):
        print(f"- {path}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_compose_isolation_audit(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Compose isolation audit: {'OK' if report['ok'] else 'FAILED'}")
    print(f"Package directory: {report['package_dir']}")
    print(
        "Checked: "
        f"services={summary.get('service_count', 0)} "
        f"volumes={summary.get('volume_count', 0)} "
        f"networks={summary.get('network_count', 0)} "
        f"errors={summary.get('error_count', 0)} "
        f"warnings={summary.get('warning_count', 0)}"
    )
    print("\nChecks:")
    for key, value in report.get("checks", {}).items():
        print(f"- {key}: {'yes' if value else 'no'}")
    print("\nErrors:")
    errors = report.get("errors") or []
    if not errors:
        print("- none")
    for issue in errors:
        scope = issue.get("service") or issue.get("path") or "-"
        value = f" [{issue['value']}]" if issue.get("value") else ""
        print(f"- {issue['code']} {scope}{value}: {issue['message']}")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if not warnings:
        print("- none")
    for issue in warnings:
        scope = issue.get("service") or issue.get("path") or "-"
        value = f" [{issue['value']}]" if issue.get("value") else ""
        print(f"- {issue['code']} {scope}{value}: {issue['message']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_portability_audit(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant: {report['tenant_key']}")
    print(f"Portability audit: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Profile: "
        f"runtime={summary.get('runtime_strategy')} "
        f"domain={summary.get('domain_pack')} "
        f"agent_pack={summary.get('agent_pack')} "
        f"sources={summary.get('source_catalog')}"
    )
    print(f"Entity groups: {', '.join(summary.get('entity_groups') or []) or '-'}")
    print("\nChecks:")
    for key, value in report.get("checks", {}).items():
        print(f"- {key}: {'yes' if value else 'no'}")
    print("\nErrors:")
    errors = report.get("errors") or []
    if not errors:
        print("- none")
    for issue in errors:
        field = issue.get("field") or "-"
        value = f" [{issue['value']}]" if issue.get("value") else ""
        print(f"- {issue['code']} {field}{value}: {issue['message']}")
    print("\nWarnings:")
    warnings = report.get("warnings") or []
    if not warnings:
        print("- none")
    for issue in warnings:
        field = issue.get("field") or "-"
        value = f" [{issue['value']}]" if issue.get("value") else ""
        print(f"- {issue['code']} {field}{value}: {issue['message']}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


def _print_portability_portfolio_audit(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    print(f"Tenant portability portfolio audit: {'OK' if report['ok'] else 'FAILED'}")
    print(
        "Tenants: "
        f"{summary.get('passed', 0)}/{summary.get('tenant_count', 0)} passed "
        f"({summary.get('failed', 0)} failed)"
    )
    print("\nTenant records:")
    for record in report.get("records") or []:
        status = "OK" if record.get("ok") else "FAILED"
        print(
            f"- {record['tenant_key']}: {status} "
            f"runtime={record.get('runtime_strategy') or '-'} "
            f"domain={record.get('domain_pack') or '-'}"
        )
        if record.get("error"):
            print(f"  ERROR: {record['error']}")
        report_payload = record.get("report") or {}
        checks = report_payload.get("checks") or {}
        for key in (
            "profile_validation_ok",
            "no_cross_tenant_identifier_leakage",
            "identifiers_have_no_restricted_domain_terms",
            "source_locations_do_not_reference_other_tenants",
            "source_contracts_do_not_reference_other_tenant_sources",
        ):
            if key in checks:
                print(f"  {key}: {'yes' if checks[key] else 'no'}")
    print("\nNotes:")
    for note in report.get("notes", []):
        print(f"- {note}")


if __name__ == "__main__":
    raise SystemExit(main())
