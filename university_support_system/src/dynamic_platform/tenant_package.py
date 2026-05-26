"""Offline tenant preparation package writer.

The package is a handoff artifact: it writes env/readiness/plan files for a
tenant without building images, downloading models, or starting Docker
services.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.bootstrap_plan import build_tenant_bootstrap_plan
from src.dynamic_platform.compose_isolation_audit import run_compose_isolation_audit
from src.dynamic_platform.compose_template import LAUNCH_MANIFEST_NAME, build_compose_launch_template_files
from src.dynamic_platform.contract_matrix import build_capability_contract_matrix
from src.dynamic_platform.decision_shadow import default_shadow_fixture_path
from src.dynamic_platform.docker_plan import build_docker_deployment_plan
from src.dynamic_platform.genericity_audit import run_genericity_audit
from src.dynamic_platform.loader import DynamicPlatformPaths
from src.dynamic_platform.model_runtime_contract import build_model_runtime_contract
from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.onboarding import build_onboarding_preview
from src.dynamic_platform.portability_audit import collect_portability_restrictions, run_tenant_portability_audit
from src.dynamic_platform.readiness import build_tenant_readiness_report
from src.dynamic_platform.registry_catalog import build_registry_catalog
from src.dynamic_platform.retrieval_contract import build_retrieval_contract
from src.dynamic_platform.runtime_adapter_contract import build_runtime_adapter_contract
from src.dynamic_platform.runtime_adapter_draft import DynamicRuntimeAdapterDraft, DynamicRuntimeRequest
from src.dynamic_platform.runtime_adapter_implementation_plan import build_runtime_adapter_implementation_plan
from src.dynamic_platform.runtime_isolation_contract import build_runtime_isolation_contract
from src.dynamic_platform.runtime_namespace import build_runtime_namespace_preview
from src.dynamic_platform.runtime_plan import build_runtime_launch_plan
from src.dynamic_platform.secrets_contract import build_tenant_secrets_contract
from src.dynamic_platform.shadow_runtime_replay import run_shadow_runtime_replay
from src.dynamic_platform.source_audit import audit_source_adapters
from src.dynamic_platform.source_ingestion_plan import build_source_ingestion_plan
from src.dynamic_platform.validator import build_execution_plan, validate_bundle

PACKAGE_MANIFEST_NAME = "package_manifest.json"


@dataclass(frozen=True)
class TenantPackageResult:
    tenant_key: str
    output_dir: str
    files: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "output_dir": self.output_dir,
            "files": self.files,
            "notes": self.notes,
        }


def build_tenant_package_files(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    require_quality_gates: bool = True,
    package_dir: str | Path | None = None,
) -> dict[str, str]:
    runtime_plan = build_runtime_launch_plan(
        bundle,
        config_root=config_root,
        require_quality_gates=require_quality_gates,
    )
    docker_plan = build_docker_deployment_plan(
        bundle,
        config_root=config_root,
        require_quality_gates=require_quality_gates,
    )
    readiness = build_tenant_readiness_report(
        bundle,
        config_root=config_root,
        env_file=None,
        require_quality_gates=require_quality_gates,
    )
    bootstrap_plan = build_tenant_bootstrap_plan(bundle)
    validation = validate_bundle(bundle)
    execution_plan = build_execution_plan(bundle)
    contract_matrix = build_capability_contract_matrix(bundle)
    source_audit = audit_source_adapters(bundle)
    source_ingestion_plan = build_source_ingestion_plan(bundle)
    retrieval_contract = build_retrieval_contract(bundle)
    model_runtime_contract = build_model_runtime_contract(bundle)
    runtime_adapter_contract = build_runtime_adapter_contract(bundle)
    runtime_adapter_preview = _runtime_adapter_draft_preview(bundle)
    runtime_isolation_contract = build_runtime_isolation_contract(bundle)
    runtime_namespace_preview = build_runtime_namespace_preview(bundle)
    secrets_contract = build_tenant_secrets_contract(bundle)
    adapter_handoff_checklist = _adapter_handoff_checklist(
        bundle,
        runtime_adapter_contract.to_dict(),
        runtime_adapter_preview,
    )
    runtime_adapter_implementation_plan = build_runtime_adapter_implementation_plan(bundle)
    restricted_terms, restricted_groups = collect_portability_restrictions(
        config_root=config_root,
        current_domain_pack=bundle.domain_pack.domain_pack,
    )
    portability_audit = run_tenant_portability_audit(
        bundle,
        restricted_identifier_terms=restricted_terms,
        restricted_entity_groups=restricted_groups,
    )
    genericity_audit = run_genericity_audit()
    registry_snapshot = build_registry_catalog(config_root=config_root)
    config_snapshot = _config_snapshot(bundle, config_root=config_root)
    package_path = Path(package_dir) if package_dir else Path("tmp/tenant_packages") / bundle.tenant.tenant_key
    compose_template_files = build_compose_launch_template_files(
        bundle,
        config_root=config_root,
        package_dir=package_path,
    )
    tenant_env_text = _tenant_env_text(runtime_plan.to_env_text(), compose_template_files)
    compose_isolation_audit = run_compose_isolation_audit(
        bundle,
        package_dir=package_path,
        draft_files=compose_template_files,
    )

    payloads: dict[str, str] = {
        "tenant.env": tenant_env_text,
        "runtime_plan.json": _json(runtime_plan.to_dict()),
        "docker_plan.json": _json(docker_plan.to_dict()),
        "readiness.json": _json(readiness.to_dict()),
        "bootstrap_plan.json": _json(bootstrap_plan.to_dict()),
        "validation.json": _json(validation.to_dict()),
        "execution_plan.json": _json(execution_plan),
        "capability_contract_matrix.json": _json(contract_matrix.to_dict()),
        "source_audit.json": _json(source_audit.to_dict()),
        "source_ingestion_plan.json": _json(source_ingestion_plan.to_dict()),
        "retrieval_contract.json": _json(retrieval_contract.to_dict()),
        "model_runtime_contract.json": _json(model_runtime_contract.to_dict()),
        "runtime_adapter_contract.json": _json(runtime_adapter_contract.to_dict()),
        "runtime_adapter_draft_preview.json": _json(runtime_adapter_preview),
        "runtime_adapter_implementation_plan.json": _json(runtime_adapter_implementation_plan.to_dict()),
        "runtime_isolation_contract.json": _json(runtime_isolation_contract.to_dict()),
        "runtime_namespace_preview.json": _json(runtime_namespace_preview),
        "secrets_contract.json": _json(secrets_contract.to_dict()),
        "tenant.secrets.example.env": secrets_contract.to_example_env(),
        "adapter_handoff_checklist.json": _json(adapter_handoff_checklist),
        "cache_strategy.json": _json(_cache_strategy(bundle)),
        "compose_isolation_audit.json": _json(compose_isolation_audit.to_dict()),
        "portability_audit.json": _json(portability_audit.to_dict()),
        "genericity_audit.json": _json(genericity_audit.to_dict()),
        "registry_snapshot.json": _json(registry_snapshot.to_dict()),
        "config_snapshot.json": _json(config_snapshot),
        "onboarding_preview.md": build_onboarding_preview(bundle),
        "README.md": _readme(bundle, docker_plan.to_dict(), package_path=package_path),
    }
    replay_path = default_shadow_fixture_path(bundle.tenant.tenant_key)
    if replay_path.exists():
        replay = run_shadow_runtime_replay(bundle, fixture_path=replay_path, match_mode="contract")
        payloads["shadow_runtime_replay.json"] = _json(replay.to_dict())
    payloads.update(compose_template_files)
    payloads["handoff_index.json"] = _json(_handoff_index(bundle, payloads, package_path=package_path))
    payloads[PACKAGE_MANIFEST_NAME] = _json(_package_manifest(bundle, runtime_plan.to_dict(), payloads))
    return payloads


def write_tenant_package(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    output_dir: str | Path | None = None,
    require_quality_gates: bool = True,
    force: bool = False,
) -> TenantPackageResult:
    target_dir = Path(output_dir) if output_dir else Path("tmp/tenant_packages") / bundle.tenant.tenant_key
    files = build_tenant_package_files(
        bundle,
        config_root=config_root,
        require_quality_gates=require_quality_gates,
        package_dir=target_dir,
    )

    existing = [target_dir / name for name in files if (target_dir / name).exists()]
    if existing and not force:
        names = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"Tenant package files already exist. Use --force to overwrite: {names}")

    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for relative_name, content in files.items():
        path = target_dir / relative_name
        path.write_text(content, encoding="utf-8")
        written.append(str(path))

    notes = [
        "Package creation is offline; no Docker service was started and no model/download command was run.",
        "tenant.env is a prepared env artifact. Do not replace production .env without runtime-env-check and replay.",
        "package_manifest.json records offline safety status and file hashes for handoff verification.",
        "docker_plan.json reports current side-by-side blockers; this package does not solve compose isolation by itself.",
        "compose launch files are draft handoff artifacts; validate them before any Docker run.",
    ]
    return TenantPackageResult(
        tenant_key=bundle.tenant.tenant_key,
        output_dir=str(target_dir),
        files=written,
        notes=notes,
    )


def _json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _tenant_env_text(base_env: str, compose_template_files: dict[str, str]) -> str:
    overrides = _compose_suggested_env_overrides(compose_template_files)
    if not overrides:
        return base_env
    existing = _env_keys(base_env)
    lines = [base_env.rstrip(), "", "# Compose draft defaults"]
    for key, value in sorted(overrides.items()):
        if key not in existing:
            lines.append(f"{key}={value}")
    return "\n".join(lines).rstrip() + "\n"


def _compose_suggested_env_overrides(compose_template_files: dict[str, str]) -> dict[str, str]:
    manifest_text = compose_template_files.get(LAUNCH_MANIFEST_NAME)
    if not manifest_text:
        return {}
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return {}
    overrides = manifest.get("suggested_env_overrides")
    if not isinstance(overrides, dict):
        return {}
    return {str(key): str(value) for key, value in overrides.items()}


def _env_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        keys.add(stripped.split("=", 1)[0])
    return keys


def _package_manifest(
    bundle: DynamicPlatformBundle,
    runtime_plan: dict[str, Any],
    payloads: dict[str, str],
) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for name, content in sorted(payloads.items()):
        raw = content.encode("utf-8")
        files.append(
            {
                "path": name,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return {
        "tenant_key": bundle.tenant.tenant_key,
        "display_name": bundle.tenant.display_name,
        "runtime_strategy": bundle.tenant.runtime_strategy,
        "runtime_binding_status": runtime_plan.get("runtime_binding_status"),
        "safety_status": "offline_handoff_only",
        "dynamic_live_binding_allowed": False,
        "file_count": len(files),
        "files": files,
        "required_checks_before_runtime_use": [
            "runtime-env-check",
            "readiness",
            "safety-audit",
            "docker compose config for draft override",
            "golden replay and narrow live replay before any runtime adapter wiring",
        ],
        "notes": [
            "This manifest is generated offline.",
            "It does not authorize Docker run, Slack/API wiring, model downloads, or dynamic live routing.",
            "File hashes cover generated UTF-8 text payloads except this manifest itself; audit normalizes platform line endings.",
        ],
    }


def _config_snapshot(bundle: DynamicPlatformBundle, *, config_root: str | Path) -> dict[str, Any]:
    paths = DynamicPlatformPaths.from_root(config_root)
    records = [
        ("tenant_profile", paths.tenant_path(bundle.tenant.tenant_key)),
        ("domain_pack", paths.domain_pack_path(bundle.domain_pack.domain_pack)),
        ("agent_pack", paths.agent_pack_path(bundle.agent_pack.agent_pack)),
        ("source_catalog", paths.source_catalog_path(bundle.source_catalog.source_catalog)),
    ]
    files: list[dict[str, Any]] = []
    for role, path in records:
        raw = path.read_bytes()
        files.append(
            {
                "role": role,
                "path": str(path),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return {
        "tenant_key": bundle.tenant.tenant_key,
        "config_root": str(paths.root),
        "safety_status": "offline_handoff_only",
        "file_count": len(files),
        "files": files,
        "notes": [
            "This snapshot records config file hashes only.",
            "It does not copy source documents, start services, or authorize live runtime binding.",
        ],
    }


def _runtime_adapter_draft_preview(bundle: DynamicPlatformBundle) -> dict[str, Any]:
    query = "Tenant destek sorusu"
    requested_capabilities: list[str] = []
    replay_path = default_shadow_fixture_path(bundle.tenant.tenant_key)
    if replay_path.exists():
        try:
            replay_payload = json.loads(replay_path.read_text(encoding="utf-8"))
            raw_cases = replay_payload.get("cases") if isinstance(replay_payload, dict) else replay_payload
            if isinstance(raw_cases, list) and raw_cases:
                first_case = raw_cases[0]
                query = str(first_case.get("query") or query)
                requested_capabilities = list(first_case.get("expected_capabilities") or [])
        except (OSError, ValueError, TypeError):
            requested_capabilities = []
    if not requested_capabilities and bundle.domain_pack.capabilities:
        first_capability = bundle.domain_pack.capabilities[0]
        requested_capabilities = [first_capability.capability_id]
        query = first_capability.display_name or first_capability.capability_id

    request = DynamicRuntimeRequest(
        tenant_key=bundle.tenant.tenant_key,
        conversation_id="tenant-package-shadow-preview",
        user_id="offline-package",
        query=query,
        locale=bundle.tenant.locale,
        timezone=bundle.tenant.timezone,
        requested_capabilities=requested_capabilities,
    )
    preview = DynamicRuntimeAdapterDraft(bundle).preview(request)
    payload = preview.to_dict()
    payload["safety_status"] = "shadow_only_not_user_facing"
    payload["request"] = request.to_dict()
    return payload


def _adapter_handoff_checklist(
    bundle: DynamicPlatformBundle,
    adapter_contract: dict[str, Any],
    adapter_preview: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tenant_key": bundle.tenant.tenant_key,
        "runtime_strategy": bundle.tenant.runtime_strategy,
        "handoff_status": "prepared_not_wired",
        "dynamic_live_binding_allowed": False,
        "adapter_status": adapter_contract.get("adapter_status"),
        "preview_answer_status": adapter_preview.get("answer_status"),
        "preview_user_facing_answer_empty": adapter_preview.get("answer") == "",
        "forbidden_now": [
            "Do not import src.dynamic_platform from classic Slack/API/router/agent runtime.",
            "Do not post dynamic shadow preview as a user-facing answer.",
            "Do not start Docker services from draft compose artifacts.",
            "Do not write cache or conversation state from the draft adapter.",
            "Do not download models or touch live RAG/DB from package generation.",
        ],
        "required_before_live_runtime": [
            "Implement an explicit adapter layer approved for live routing.",
            "Keep OMU classic_protected runtime as owner unless a separate rollout decision changes it.",
            "Run handoff-readiness and package-audit-all against fresh packages.",
            "Run golden replay and a narrow live Slack replay.",
            "Validate side-by-side Docker compose with docker compose config before any run.",
            "Add cache, conversation-state, uploaded-file, and tenant isolation tests for live adapter behavior.",
        ],
        "safe_offline_commands": [
            f"python -m scripts.tenant runtime-adapter-draft --tenant {bundle.tenant.tenant_key} --query \"...\"",
            f"python -m scripts.tenant safety-audit --tenant {bundle.tenant.tenant_key}",
            f"python -m scripts.tenant readiness --tenant {bundle.tenant.tenant_key}",
        ],
        "notes": [
            "This checklist is an offline handoff artifact.",
            "Passing this checklist does not authorize live dynamic runtime.",
        ],
    }


def _cache_strategy(bundle: DynamicPlatformBundle) -> dict[str, Any]:
    return {
        "tenant_key": bundle.tenant.tenant_key,
        "safety_status": "offline_cache_plan_only",
        "docker_image": {
            "default_ref": "university_support_system-app:latest",
            "reuse_existing_image": True,
            "pull_policy": "do_not_pull_during_package_generation",
        },
        "model_cache": {
            "host_dir_env": "MODEL_CACHE_HOST_DIR",
            "default_host_dir": "./data/models",
            "container_root": "/models",
            "hf_home": "/models/huggingface",
            "sentence_transformers_home": "/models/huggingface/hub",
            "shared_between_tenants_by_default": True,
        },
        "ocr_runtime": {
            "installed_in_app_image": True,
            "requires_rebuild_only_if_base_image_or_dockerfile_changes": True,
        },
        "offline_package_generation": {
            "starts_docker": False,
            "builds_images": False,
            "pulls_images": False,
            "downloads_models": False,
            "writes_runtime_cache": False,
        },
        "before_any_future_live_run": [
            "Confirm university_support_system-app:latest exists locally with docker images.",
            "Prefer --skip-build or an already-built image when the Dockerfile has not changed.",
            "Keep MODEL_CACHE_HOST_DIR pointing at the shared local model cache unless tenant isolation requires a separate cache.",
            "Run docker compose config against the draft override before any build/up.",
            "Do not enable dynamic_pilot/dynamic_on until replay, cache, state, upload, and DB isolation gates pass.",
        ],
        "notes": [
            "This cache strategy is a handoff artifact only; it does not inspect Docker or download anything.",
            "Sharing the model cache reduces internet use, but live runtime must still isolate tenant data/state.",
        ],
    }


def _readme(bundle: DynamicPlatformBundle, docker_plan: dict[str, Any], *, package_path: Path) -> str:
    tenant = bundle.tenant
    lines = [
        f"# {tenant.display_name} Tenant Preparation Package",
        "",
        "Bu klasor offline hazirlik paketidir. Docker build/pull yapmaz, servis baslatmaz, model indirmez.",
        "",
        "## Icerik",
        "",
        "- `tenant.env`: tenant runtime environment sozlesmesi.",
        "- `runtime_plan.json`: runtime/env plani.",
        "- `docker_plan.json`: compose/Docker hazirlik ve blocker raporu.",
        "- `readiness.json`: toplu offline readiness raporu.",
        "- `bootstrap_plan.json`: tenant kurulum/adaptasyon adimlari ve eksik/hazir alanlar.",
        "- `validation.json`: tenant profil dogrulama raporu.",
        "- `execution_plan.json`: agent/capability/source dry-run plani.",
        "- `capability_contract_matrix.json`: capability -> agent/specialist/source/final-owner matrisi.",
        "- `source_audit.json`: source adapter/authority/owner denetimi.",
        "- `source_ingestion_plan.json`: source sync/index hazirlik plani; dosya/web/DB acmaz.",
        "- `retrieval_contract.json`: demo local retrieval service ve gelecekteki indexed/vector retrieval siniri.",
        "- `model_runtime_contract.json`: model cache, reranker adayi ve FP16 kurallari.",
        "- `runtime_adapter_contract.json`: live dynamic runtime baglanmadan onceki adapter siniri.",
        "- `runtime_adapter_draft_preview.json`: shadow-only adapter onizlemesi; kullanici cevabi uretmez.",
        "- `runtime_adapter_implementation_plan.json`: live adapter fazlari, gate'ler ve rollback kurallari.",
        "- `runtime_isolation_contract.json`: tenant cache/state/upload izolasyon sozlesmesi.",
        "- `runtime_namespace_preview.json`: tenant cache/state/upload key onizlemesi; runtime store'a yazmaz.",
        "- `secrets_contract.json`: secret isimleri ve guvenli enjeksiyon sozlesmesi; gercek secret degeri icermez.",
        "- `tenant.secrets.example.env`: bos degerli ornek secret env dosyasi; doldurulup commit edilmemelidir.",
        "- `adapter_handoff_checklist.json`: live adapter fazi oncesi tamamlanacak guvenlik listesi.",
        "- `cache_strategy.json`: image/model/OCR cache kullanimi ve internetsiz deneme notlari.",
        "- `compose_isolation_audit.json`: draft compose dosyalarinin tenant izolasyon denetimi.",
        "- `portability_audit.json`: tenant'in baska kurum/tenant varsayimi sizdirmadigini denetler.",
        "- `handoff_index.json`: paketteki artifact, gate ve guvenli komut sirasi.",
        "- `genericity_audit.json`: dynamic core'un kurum/domain ozel davranis sizdirmadigini denetler.",
        "- `registry_snapshot.json`: paketin uretildigi dynamic domain/agent/source/tenant katalog gorunumu.",
        "- `config_snapshot.json`: pakete kaynak olan tenant/domain/agent/source YAML hashleri.",
        "- `shadow_runtime_replay.json`: decision fixture uzerinden offline shadow runtime replay raporu.",
        "- `onboarding_preview.md`: Slack/onboarding metni icin offline tenant onizlemesi.",
        "- `package_manifest.json`: offline safety status ve dosya hash dogrulama manifesti.",
        "- `compose_launch_manifest.json`: side-by-side Docker taslak manifesti.",
        "- `docker-compose.tenant.override.draft.yml`: calistirmadan once validate edilmesi gereken override taslagi.",
        "- `COMPOSE_NOTES.md`: compose taslaginin riskleri ve validasyon notlari.",
        "- `compose-config-audit` pakete otomatik yazilmaz; Docker compose config calistirdigi icin manuel onayli validasyon komutu olarak kosulur.",
        "",
        "## Guvenli Kontrol Komutlari",
        "",
        "```powershell",
        f".\\venv\\Scripts\\python.exe -m scripts.tenant runtime-env-check --tenant {tenant.tenant_key} --env-file {package_path / 'tenant.env'}",
        f".\\venv\\Scripts\\python.exe -m scripts.tenant runtime-isolation-contract --tenant {tenant.tenant_key}",
        f".\\venv\\Scripts\\python.exe -m scripts.tenant runtime-namespace-preview --tenant {tenant.tenant_key}",
        f".\\venv\\Scripts\\python.exe -m scripts.tenant readiness --tenant {tenant.tenant_key} --env-file {package_path / 'tenant.env'}",
        f".\\venv\\Scripts\\python.exe -m scripts.tenant docker-plan --tenant {tenant.tenant_key}",
        "```",
        "",
        "## Durum",
        "",
        f"- Runtime strategy: `{tenant.runtime_strategy}`",
        f"- Domain pack: `{tenant.domain_pack}`",
        f"- Agent pack: `{tenant.agent_pack}`",
        f"- Source catalog: `{tenant.source_catalog}`",
        f"- Docker single-instance ready: `{docker_plan.get('single_instance_env_ready')}`",
        f"- Docker side-by-side ready: `{docker_plan.get('side_by_side_ready')}`",
        "",
        "Not: Side-by-side Docker ready `false` ise bu beklenen olabilir. Mevcut OMU compose dosyalari korunur. Paket icindeki compose override dosyasi yalniz taslaktir; `docker compose config` ve replay gecmeden calistirilmaz.",
        "",
    ]
    return "\n".join(lines)


def _handoff_index(
    bundle: DynamicPlatformBundle,
    payloads: dict[str, str],
    *,
    package_path: Path,
) -> dict[str, Any]:
    tenant = bundle.tenant
    files = sorted(set(payloads) | {PACKAGE_MANIFEST_NAME})
    return {
        "tenant_key": tenant.tenant_key,
        "display_name": tenant.display_name,
        "runtime_strategy": tenant.runtime_strategy,
        "domain_pack": tenant.domain_pack,
        "agent_pack": tenant.agent_pack,
        "source_catalog": tenant.source_catalog,
        "handoff_status": "offline_prepared_not_wired",
        "live_runtime_authorized": False,
        "artifact_count": len(files),
        "artifacts": files,
        "required_artifacts_before_handoff": [
            "tenant.env",
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
            "compose_launch_manifest.json",
            "docker-compose.tenant.override.draft.yml",
            "package_manifest.json",
        ],
        "safe_verification_order": [
            f"python -m scripts.tenant validate --tenant {tenant.tenant_key}",
            f"python -m scripts.tenant source-audit --tenant {tenant.tenant_key}",
            f"python -m scripts.tenant portability-audit --tenant {tenant.tenant_key}",
            f"python -m scripts.tenant runtime-isolation-contract --tenant {tenant.tenant_key}",
            f"python -m scripts.tenant runtime-namespace-preview --tenant {tenant.tenant_key}",
            f"python -m scripts.tenant retrieval-contract --tenant {tenant.tenant_key}",
            f"python -m scripts.tenant model-runtime-contract --tenant {tenant.tenant_key}",
            f"python -m scripts.tenant runtime-env-check --tenant {tenant.tenant_key} --env-file {package_path / 'tenant.env'}",
            f"python -m scripts.tenant safety-audit --tenant {tenant.tenant_key} --env-file {package_path / 'tenant.env'} --package-dir {package_path}",
            f"python -m scripts.tenant compose-isolation-audit --tenant {tenant.tenant_key} --package-dir {package_path}",
            f"python -m scripts.tenant compose-config-audit --tenant {tenant.tenant_key} --package-dir {package_path}",
            f"python -m scripts.tenant runtime-smoke-readiness --tenant {tenant.tenant_key} --package-dir {package_path}",
            f"python -m scripts.tenant runtime-query-smoke --tenant {tenant.tenant_key}",
            "python -m scripts.tenant package-audit-all --package-root tmp/tenant_packages --allow-missing-shadow",
            "python -m scripts.tenant handoff-readiness --package-root tmp/tenant_packages --allow-missing-shadow",
        ],
        "manual_approval_required_before": [
            "docker compose config against the draft override",
            "Docker build/up or any container start",
            "Slack/API/router live binding",
            "dynamic_pilot or dynamic_on runtime strategy",
            "cache, conversation-state, uploaded-file, or DB writes from dynamic runtime",
        ],
        "classic_runtime_guardrails": [
            "Do not import src.dynamic_platform from src/orchestrators, src/routing, src/agents, src/slack, or src/api.",
            "Keep OMU classic_protected unless a separate rollout decision changes it.",
            "Treat dynamic_shadow tenants as planning artifacts until live adapter gates pass.",
        ],
        "notes": [
            "This index is generated offline and does not authorize runtime use.",
            "It is intended as a compact handoff map for humans and future automation.",
        ],
    }
