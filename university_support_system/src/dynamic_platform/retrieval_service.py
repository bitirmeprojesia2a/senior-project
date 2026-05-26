"""Tenant-scoped retrieval service boundary for dynamic runtimes.

The first implementation is intentionally offline-first: it reads only the
tenant source catalog and local demo files. The interface exists so later
Chroma/BM25/vector adapters can be wired without changing agent orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from src.dynamic_platform.generic_sources import SourceExcerpt, TenantSourceReader
from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class RetrievalQuery:
    tenant_key: str
    query: str
    capabilities: list[str]
    source_families: list[str] = field(default_factory=list)
    top_k: int = 4


@dataclass(frozen=True)
class RetrievalResult:
    excerpts: list[SourceExcerpt]
    warnings: list[str] = field(default_factory=list)
    telemetry: dict[str, object] = field(default_factory=dict)


class DynamicRetrievalService(Protocol):
    """Contract all dynamic retrieval implementations must satisfy."""

    def search(self, request: RetrievalQuery) -> RetrievalResult:
        """Return tenant-scoped source excerpts for a capability-scoped query."""


class LocalSourceRetrievalService:
    """No-download retrieval service for offline demo and smoke runs."""

    mode = "local_source_retrieval_service_no_download_smoke"

    def __init__(self, bundle: DynamicPlatformBundle, *, project_root: str | Path = ".") -> None:
        self.bundle = bundle
        self.reader = TenantSourceReader(bundle, project_root=project_root)

    def search(self, request: RetrievalQuery) -> RetrievalResult:
        if request.tenant_key != self.bundle.tenant.tenant_key:
            return RetrievalResult(
                excerpts=[],
                warnings=["retrieval_tenant_mismatch"],
                telemetry={
                    "retrieval_mode": self.mode,
                    "tenant_key": self.bundle.tenant.tenant_key,
                    "requested_tenant": request.tenant_key,
                },
            )
        excerpts, warnings = self.reader.search(
            query=request.query,
            capabilities=request.capabilities,
            source_families=request.source_families,
            top_k=request.top_k,
        )
        collections = sorted(
            {
                source.collection
                for source in self.bundle.source_catalog.sources
                if source.enabled and source.collection
            }
        )
        return RetrievalResult(
            excerpts=excerpts,
            warnings=warnings,
            telemetry={
                "retrieval_mode": self.mode,
                "tenant_key": self.bundle.tenant.tenant_key,
                "source_catalog": self.bundle.source_catalog.source_catalog,
                "tenant_collections": collections,
                "capabilities": request.capabilities,
                "source_families": request.source_families,
                "top_k": request.top_k,
                "excerpt_count": len(excerpts),
            },
        )
