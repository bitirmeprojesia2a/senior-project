"""Central retrieval/reranker service API."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.constants import Department
from src.db import dispose_engine
from src.rag.retriever import HybridRetriever
from src.rag.warmup import warm_retrieval_resources
from src.startup.warmup import cancel_application_warmup, schedule_application_warmup


class RetrievalSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=30)
    department: Department | None = None
    source_hints: list[str] = Field(default_factory=list)
    topic_hint: str | None = None
    student_department: str | None = None
    source_owner: str | None = None
    reranker_candidate_limit: int | None = Field(default=None, ge=1, le=30)


class RetrievalEnrichRequest(BaseModel):
    results: list[dict[str, Any]] = Field(default_factory=list)
    department: Department | None = None


class RetrievalResultsResponse(BaseModel):
    results: list[dict[str, Any]] = Field(default_factory=list)


@lru_cache
def get_retriever() -> HybridRetriever:
    return HybridRetriever()


async def _warm_retrieval_service() -> None:
    await asyncio.to_thread(
        warm_retrieval_resources,
        collections=settings.configured_warmup_collections(),
        include_reranker=settings.server.warmup_include_reranker,
    )


@asynccontextmanager
async def _retrieval_lifespan(app: FastAPI):
    warmup_task = schedule_application_warmup(
        _warm_retrieval_service,
        label="retrieval-service",
    )
    app.state.warmup_task = warmup_task
    try:
        yield
    finally:
        await cancel_application_warmup(warmup_task)
        get_retriever().close()
        await dispose_engine()


def create_retrieval_service_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.institution.short_name_ascii} Retrieval Service",
        version=settings.server.app_version,
        description="Centralized hybrid retrieval and reranking service.",
        lifespan=_retrieval_lifespan,
    )

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, Any]:
        warmup_task: asyncio.Task | None = getattr(app.state, "warmup_task", None)
        warmup_complete = warmup_task is None or warmup_task.done()
        return {
            "status": "healthy" if warmup_complete else "warming",
            "service": "retrieval-service",
            "build": settings.server.build_metadata(),
            "warmup": {
                "enabled": settings.server.warmup_enabled,
                "complete": warmup_complete,
            },
            "runtime": {
                "label": settings.server.runtime_label,
                "embedding_device": settings.embedding.device,
                "reranker_device": settings.reranker.device,
            },
        }

    @app.post("/search", response_model=RetrievalResultsResponse, tags=["retrieval"])
    async def search(payload: RetrievalSearchRequest) -> RetrievalResultsResponse:
        retriever = get_retriever()
        results = await asyncio.to_thread(
            retriever.search,
            payload.query,
            top_k=payload.top_k,
            department=payload.department,
            source_hints=payload.source_hints,
            topic_hint=payload.topic_hint,
            student_department=payload.student_department,
            source_owner=payload.source_owner,
            reranker_candidate_limit=payload.reranker_candidate_limit,
        )
        return RetrievalResultsResponse(results=results)

    @app.post("/enrich", response_model=RetrievalResultsResponse, tags=["retrieval"])
    async def enrich(payload: RetrievalEnrichRequest) -> RetrievalResultsResponse:
        retriever = get_retriever()
        results = await asyncio.to_thread(
            retriever.enrich_results,
            payload.results,
            department=payload.department,
        )
        return RetrievalResultsResponse(results=results)

    return app


app = create_retrieval_service_app()
