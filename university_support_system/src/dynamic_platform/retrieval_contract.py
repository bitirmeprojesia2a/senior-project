"""Tenant retrieval contract for dynamic platform runtimes.

Demo tenants currently use a local source retrieval service for no-download
smoke tests. This contract makes that limitation explicit and defines the
production-grade tenant retrieval service boundary that must exist before broad
live rollout.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class DynamicRetrievalContract:
    tenant_key: str
    ok: bool
    current_mode: str
    dedicated_retrieval_service_wired: bool
    tenant_collections: list[str]
    source_count: int
    enabled_source_count: int
    required_live_capabilities: list[str]
    required_runtime_guards: list[str]
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "current_mode": self.current_mode,
            "dedicated_retrieval_service_wired": self.dedicated_retrieval_service_wired,
            "tenant_collections": self.tenant_collections,
            "source_count": self.source_count,
            "enabled_source_count": self.enabled_source_count,
            "required_live_capabilities": self.required_live_capabilities,
            "required_runtime_guards": self.required_runtime_guards,
            "warnings": self.warnings,
            "notes": self.notes,
        }


def build_retrieval_contract(bundle: DynamicPlatformBundle) -> DynamicRetrievalContract:
    sources = list(bundle.source_catalog.sources)
    enabled_sources = [source for source in sources if source.enabled]
    collections = sorted({source.collection for source in enabled_sources if source.collection})
    warnings: list[str] = []
    dedicated_retrieval_service_wired = False
    if enabled_sources and not dedicated_retrieval_service_wired:
        warnings.append("dynamic_demo_uses_local_retrieval_service: no indexed/vector retrieval service is wired yet")

    return DynamicRetrievalContract(
        tenant_key=bundle.tenant.tenant_key,
        ok=True,
        current_mode="local_source_retrieval_service_no_download_smoke",
        dedicated_retrieval_service_wired=dedicated_retrieval_service_wired,
        tenant_collections=collections,
        source_count=len(sources),
        enabled_source_count=len(enabled_sources),
        required_live_capabilities=[
            "tenant-scoped collection selection",
            "source-family and capability scoped retrieval",
            "cross-tenant collection isolation",
            "retrieval cache namespaced by tenant",
            "chunk/source telemetry returned with every answer",
            "no fallback to protected classic collections for unrelated tenants",
        ],
        required_runtime_guards=[
            "retrieval_contract_present_in_package",
            "retrieval_cache_namespace_checked",
            "tenant_collections_do_not_reference_other_tenants",
            "retrieval_quality_replay_passed",
            "manual rollout approval before broad live retrieval",
        ],
        warnings=warnings,
        notes=[
            "Local source retrieval service is acceptable for offline/no-download smoke tests.",
            "Production-grade dynamic tenants should use a tenant-scoped indexed retrieval adapter or service.",
            "Existing source catalog collection fields are metadata until an index/retrieval adapter is wired.",
        ],
    )
