"""Client for the central retrieval/reranker service."""

from __future__ import annotations

from typing import Any

import httpx
import structlog

from src.core.config import settings
from src.core.constants import Department

logger = structlog.get_logger()


def _department_value(department: Department | str | None) -> str | None:
    if isinstance(department, Department):
        return department.value
    if department is None:
        return None
    return str(department)


class RemoteHybridRetriever:
    """HybridRetriever-compatible facade backed by the retrieval service."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.base_url = (base_url or settings.retrieval_service.normalized_url).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.retrieval_service.timeout_seconds
        self._client = httpx.Client(timeout=self.timeout_seconds)

    def search(
        self,
        query: str,
        top_k: int | None = None,
        department: Department | str | None = None,
        *,
        source_hints: list[str] | None = None,
        topic_hint: str | None = None,
        student_department: str | None = None,
    ) -> list[dict[str, Any]]:
        payload = {
            "query": query,
            "top_k": top_k,
            "department": _department_value(department),
            "source_hints": source_hints or [],
            "topic_hint": topic_hint,
            "student_department": student_department,
        }
        response = self._client.post(f"{self.base_url}/search", json=payload)
        response.raise_for_status()
        data = response.json()
        return list(data.get("results") or [])

    def enrich_results(
        self,
        results: list[dict[str, Any]],
        *,
        department: Department | str | None = None,
    ) -> list[dict[str, Any]]:
        if not results:
            return []
        payload = {
            "results": results,
            "department": _department_value(department),
        }
        response = self._client.post(f"{self.base_url}/enrich", json=payload)
        response.raise_for_status()
        data = response.json()
        return list(data.get("results") or [])

    def close(self) -> None:
        self._client.close()

