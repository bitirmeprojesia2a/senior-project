"""Optional LLM-backed query expansion for retrieval."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass

import structlog

from src.core.config import settings
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.prompt_templates import QUERY_EXPANSION_SYSTEM_PROMPT

logger = structlog.get_logger()


@dataclass(frozen=True)
class QueryExpansionResult:
    """Expanded query text and terms added by the LLM."""

    expanded_query: str
    added_terms: list[str]


class LLMQueryExpander:
    """Small sync facade around the async LLM service for retrieval threads."""

    def __init__(self, *, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or LLMService()

    def expand(self, query: str, *, rule_expanded_query: str | None = None) -> QueryExpansionResult | None:
        """Return an LLM-expanded query, or None when expansion is disabled/unsafe."""
        if not settings.rag.llm_query_expansion_enabled:
            return None

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            logger.warning("llm_query_expansion_skipped_running_event_loop")
            return None

        try:
            return asyncio.run(
                asyncio.wait_for(
                    self._expand_async(query, rule_expanded_query=rule_expanded_query),
                    timeout=settings.rag.llm_query_expansion_timeout_seconds,
                )
            )
        except (TimeoutError, LLMServiceError, ValueError, TypeError, json.JSONDecodeError) as exc:
            logger.warning("llm_query_expansion_failed", error=type(exc).__name__)
            return None

    async def _expand_async(
        self,
        query: str,
        *,
        rule_expanded_query: str | None,
    ) -> QueryExpansionResult | None:
        prompt = json.dumps(
            {
                "original_query": query,
                "rule_expanded_query": rule_expanded_query or query,
            },
            ensure_ascii=False,
        )
        raw = await self.llm_service.generate(
            prompt=prompt,
            system=QUERY_EXPANSION_SYSTEM_PROMPT,
            json_mode=True,
            model_role="query_expansion",
        )
        payload = json.loads(raw)
        expanded_query = self._clean_query(str(payload.get("expanded_query") or ""))
        if not expanded_query:
            return None

        max_chars = max(len(query), settings.rag.llm_query_expansion_max_chars)
        expanded_query = expanded_query[:max_chars].strip()
        if not self._contains_query_anchor(query, expanded_query):
            expanded_query = f"{query} {expanded_query}".strip()[:max_chars].strip()

        added_terms = payload.get("added_terms") or []
        if not isinstance(added_terms, list):
            added_terms = []
        cleaned_terms = [
            self._clean_query(str(term))[:80]
            for term in added_terms[:12]
            if self._clean_query(str(term))
        ]
        return QueryExpansionResult(expanded_query=expanded_query, added_terms=cleaned_terms)

    @staticmethod
    def _clean_query(text: str) -> str:
        text = re.sub(r"[\r\n\t]+", " ", text)
        return re.sub(r"\s+", " ", text).strip(" \t\r\n\"'")

    @staticmethod
    def _contains_query_anchor(original: str, expanded: str) -> bool:
        original_tokens = {token for token in re.findall(r"\w{4,}", original.lower())}
        if not original_tokens:
            return True
        expanded_lower = expanded.lower()
        return any(token in expanded_lower for token in original_tokens)


__all__ = ["LLMQueryExpander", "QueryExpansionResult"]
