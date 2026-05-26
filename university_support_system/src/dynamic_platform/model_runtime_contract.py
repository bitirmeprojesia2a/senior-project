"""Offline model/cache/precision contract for dynamic tenant packages.

This module is intentionally declarative. It must not import heavy model
libraries, inspect Hugging Face, start Docker, or download artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.config import settings
from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class DynamicModelRuntimeContract:
    tenant_key: str
    ok: bool
    safety_status: str
    model_cache: dict[str, Any]
    reranker_policy: dict[str, Any]
    precision_policy: dict[str, Any]
    offline_generation: dict[str, bool]
    required_before_model_switch: list[str]
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "safety_status": self.safety_status,
            "model_cache": self.model_cache,
            "reranker_policy": self.reranker_policy,
            "precision_policy": self.precision_policy,
            "offline_generation": self.offline_generation,
            "required_before_model_switch": self.required_before_model_switch,
            "warnings": self.warnings,
            "notes": self.notes,
        }


def build_model_runtime_contract(bundle: DynamicPlatformBundle) -> DynamicModelRuntimeContract:
    """Build a tenant package contract for model caches, rerankers, and FP16."""

    configured_model = settings.reranker.model
    configured_dtype = settings.reranker.torch_dtype
    configured_device = settings.reranker.device
    return DynamicModelRuntimeContract(
        tenant_key=bundle.tenant.tenant_key,
        ok=True,
        safety_status="offline_contract_only_no_model_load",
        model_cache={
            "host_dir_env": "MODEL_CACHE_HOST_DIR",
            "default_host_dir": "./data/models",
            "container_root": "/models",
            "hf_home": "/models/huggingface",
            "sentence_transformers_home": "/models/huggingface/hub",
            "shared_model_artifacts_allowed": True,
            "tenant_data_cache_shared": False,
            "package_generation_reads_or_writes_cache": False,
        },
        reranker_policy={
            "current_configured_model": configured_model,
            "current_configured_device": configured_device,
            "current_configured_torch_dtype": configured_dtype,
            "rollback_baseline": "nreimers/mmarco-mMiniLMv2-L6-H384-v1",
            "primary_bge_candidate": "BAAI/bge-reranker-v2-m3",
            "turkish_shadow_candidate": "seroe/bge-reranker-v2-m3-turkish-triplet",
            "turkish_candidate_default_enabled": False,
            "model_switch_requires_shadow_benchmark": True,
            "model_switch_requires_final_replay": True,
            "calibration_is_model_specific": True,
        },
        precision_policy={
            "configured_torch_dtype": configured_dtype,
            "fp16_allowed_only_on_cuda": True,
            "cpu_uses_fp32": True,
            "turkish_shadow_fp16_allowed_on_cuda": True,
            "do_not_force_fp16_without_device_check": True,
        },
        offline_generation={
            "loads_models": False,
            "downloads_models": False,
            "starts_docker": False,
            "builds_images": False,
            "pulls_images": False,
            "writes_runtime_cache": False,
        },
        required_before_model_switch=[
            "Confirm model artifacts are already present in MODEL_CACHE_HOST_DIR or approve a separate download phase.",
            "Run reranker benchmark with explicit --model, --device, --torch-dtype, --profile, and --output.",
            "Keep the current configured reranker unless replay proves the candidate is better.",
            "Recompute or verify calibration shift/scale for the selected model.",
            "Run golden replay and narrow live Slack replay before changing production defaults.",
        ],
        warnings=[
            "This contract does not validate that model files exist locally.",
            "Dynamic tenant package generation must not trigger model downloads.",
            "Turkish reranker remains shadow/benchmark-only unless a later rollout explicitly enables it.",
        ],
        notes=[
            "Model artifact cache may be shared to reduce internet use; tenant data/state caches remain isolated.",
            "FP16 is a runtime optimization, not a package-generation behavior.",
        ],
    )
