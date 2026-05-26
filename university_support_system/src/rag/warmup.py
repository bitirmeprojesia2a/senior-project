"""Retrieval warm-up yardimcilari."""

from __future__ import annotations

import structlog

from src.core.config import settings
from src.rag.retriever import HybridRetriever

logger = structlog.get_logger()


def warm_retrieval_resources(
    *,
    collections: list[str] | None = None,
    include_reranker: bool | None = None,
) -> None:
    """Opsiyonel retrieval warm-up akisini calistirir."""
    if not settings.server.warmup_enabled:
        return

    effective_collections = collections or settings.configured_warmup_collections()
    effective_include_reranker = (
        settings.server.warmup_include_reranker
        if include_reranker is None
        else include_reranker
    )
    logger.info(
        "retrieval_warmup_start",
        collections=effective_collections,
        include_reranker=effective_include_reranker,
        top_k=settings.rag.top_k,
    )
    try:
        HybridRetriever.prewarm(
            effective_collections,
            k=settings.rag.top_k,
            include_reranker=effective_include_reranker,
        )
    except Exception:
        # Warm-up is a best-effort optimization and must never block server startup.
        logger.exception("retrieval_warmup_failed", collections=effective_collections)
    else:
        logger.info(
            "retrieval_warmup_complete",
            collections=effective_collections,
            include_reranker=effective_include_reranker,
        )
