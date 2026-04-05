"""Retrieval warm-up yardimcilari."""

from __future__ import annotations

import structlog

from src.core.config import settings
from src.rag.retriever import HybridRetriever

logger = structlog.get_logger()


def warm_retrieval_resources() -> None:
    """Opsiyonel retrieval warm-up akisini calistirir."""
    if not settings.server.warmup_enabled:
        return

    collections = settings.configured_warmup_collections()
    logger.info(
        "retrieval_warmup_start",
        collections=collections,
        include_reranker=settings.server.warmup_include_reranker,
        top_k=settings.rag.top_k,
    )
    try:
        HybridRetriever.prewarm(
            collections,
            k=settings.rag.top_k,
            include_reranker=settings.server.warmup_include_reranker,
        )
    except Exception:
        # Warm-up is a best-effort optimization and must never block server startup.
        logger.exception("retrieval_warmup_failed", collections=collections)
    else:
        logger.info(
            "retrieval_warmup_complete",
            collections=collections,
            include_reranker=settings.server.warmup_include_reranker,
        )
