"""LLM-backed query normalization before routing."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Literal

from src.core.config import settings
from src.core.text_normalization import normalize_text
from src.llm.llm_service import LLMService
from src.llm.prompt_templates import QUERY_NORMALIZATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

TargetCapability = Literal["announcement", "event", "none"]


@dataclass(frozen=True)
class QueryNormalizationResult:
    """Canonical query metadata produced by the LLM normalizer."""

    original_query: str
    canonical_query: str
    is_rewritten: bool
    is_personal: bool
    primary_intent: str
    target_capability: TargetCapability
    confidence: float
    reasoning: str | None = None


def unchanged_query(query: str) -> QueryNormalizationResult:
    """Return a no-op normalization result."""
    return QueryNormalizationResult(
        original_query=query,
        canonical_query=query,
        is_rewritten=False,
        is_personal=False,
        primary_intent="unknown",
        target_capability="none",
        confidence=0.0,
        reasoning=None,
    )


def _extract_json_object(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return None


def _safe_capability(value: object) -> TargetCapability:
    text = str(value or "none").strip().lower()
    if text in {"announcement", "event"}:
        return text  # type: ignore[return-value]
    return "none"


def _safe_confidence(value: object) -> float:
    try:
        return max(0.0, min(float(value), 1.0))
    except (TypeError, ValueError):
        return 0.0


def _rewrite_is_safe(original: str, canonical: str) -> bool:
    """Reject rewrites that are too large for standalone normalization."""
    original_norm = normalize_text(original)
    canonical_norm = normalize_text(canonical)
    if not canonical_norm:
        return False
    if canonical_norm == original_norm:
        return True
    # Preserve high-impact academic-calendar qualifiers. Dropping "sisteme
    # girilmesi/not girisi/sonuc" changes a grade-entry deadline question into
    # a generic exam-date question.
    grade_entry_deadline_markers = (
        "sisteme gir",
        "internetten gir",
        "not gir",
        "notlarin gir",
        "sonuclarin gir",
        "sonuclarinin gir",
        "sinav sonuclari",
        "sinav sonuclarinin",
    )
    if any(marker in original_norm for marker in grade_entry_deadline_markers):
        if not any(marker in canonical_norm for marker in grade_entry_deadline_markers):
            return False
    original_tokens = set(original_norm.split())
    canonical_tokens = set(canonical_norm.split())
    if not original_tokens:
        return False
    overlap_ratio = len(original_tokens & canonical_tokens) / len(original_tokens)
    if overlap_ratio >= 0.45:
        return True
    # Allow short typo/completion cases such as "guncel duyur" -> "guncel duyurular nelerdir".
    if len(original_tokens) <= 3:
        return any(
            len(token) >= 4 and any(candidate.startswith(token) for candidate in canonical_tokens)
            for token in original_tokens
        )
    return False


def rewrite_is_safe(original: str, canonical: str) -> bool:
    """Public guard for canonical queries produced by routing LLM."""
    return _rewrite_is_safe(original, canonical)


def should_pre_normalize_for_capability(query: str) -> bool:
    """Limit the extra normalizer call to short capability-like fragments."""
    normalized = normalize_text(query).strip(" \t\r\n?.!,;:")
    tokens = normalized.split()
    if not settings.llm.query_normalization_enabled or not (1 <= len(tokens) <= 4):
        return False
    capability_markers = (
        "duyur",
        "haber",
        "ilan",
        "etkinlik",
        "seminer",
        "konferans",
    )
    return any(marker in normalized for marker in capability_markers)


async def normalize_query_with_llm(
    *,
    query: str,
    llm_service: LLMService,
    llm_profile: str | None = None,
) -> QueryNormalizationResult:
    """Normalize a standalone query with an LLM, falling back to the original query."""
    if not settings.llm.query_normalization_enabled:
        return unchanged_query(query)

    prompt = json.dumps(
        {
            "query": query,
            "output_schema": {
                "canonical_query": "string",
                "is_personal": False,
                "primary_intent": "string",
                "target_capability": "announcement|event|none",
                "confidence": 0.0,
                "reasoning": "string",
            },
        },
        ensure_ascii=False,
    )
    try:
        raw = await asyncio.wait_for(
            llm_service.generate(
                prompt=prompt,
                system=QUERY_NORMALIZATION_SYSTEM_PROMPT,
                json_mode=True,
                model_role="query_expansion",
                llm_profile=llm_profile,
            ),
            timeout=settings.llm.query_normalization_timeout_seconds,
        )
    except Exception as exc:
        logger.warning("query_normalization_skipped reason=%s", type(exc).__name__)
        return unchanged_query(query)

    payload = _extract_json_object(raw)
    if payload is None:
        logger.warning("query_normalization_invalid_json")
        return unchanged_query(query)

    canonical_query = str(payload.get("canonical_query") or query).strip() or query
    if not _rewrite_is_safe(query, canonical_query):
        logger.warning(
            "query_normalization_rejected original=%r canonical=%r",
            query,
            canonical_query,
        )
        canonical_query = query

    target_capability = _safe_capability(payload.get("target_capability"))
    confidence = _safe_confidence(payload.get("confidence"))
    return QueryNormalizationResult(
        original_query=query,
        canonical_query=canonical_query,
        is_rewritten=normalize_text(canonical_query) != normalize_text(query),
        is_personal=bool(payload.get("is_personal", False)),
        primary_intent=str(payload.get("primary_intent") or "unknown").strip().lower() or "unknown",
        target_capability=target_capability,
        confidence=confidence,
        reasoning=str(payload.get("reasoning") or "").strip() or None,
    )
