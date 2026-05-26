"""LLM-assisted evidence selection for specialist RAG synthesis.

The deterministic retriever/reranker still produces the candidate pool.  This
module only decides which candidates should be placed into the final synthesis
context, with safe fallback to the original ranking on every failure mode.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Sequence

from src.core.config import settings
from src.quality.evidence import EvidenceItem

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvidenceSelectionDecision:
    """Diagnostics for the optional LLM evidence selector."""

    used_llm: bool
    status: str
    selected_ids: list[str] = field(default_factory=list)
    ranking: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""
    candidate_count: int = 0

    def to_diagnostics_dict(self) -> dict[str, Any]:
        """Return JSON-safe selector diagnostics."""
        return {
            "used_llm": self.used_llm,
            "status": self.status,
            "selected_ids": self.selected_ids,
            "ranking": self.ranking,
            "reason": self.reason,
            "candidate_count": self.candidate_count,
        }


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _candidate_payload(evidence_items: Sequence[EvidenceItem]) -> list[dict[str, Any]]:
    """Compact candidate representation for the selector prompt."""
    payload: list[dict[str, Any]] = []
    for index, item in enumerate(evidence_items, start=1):
        payload.append(
            {
                "id": item.source_id,
                "rank": index,
                "source": item.source_name,
                "department": item.department,
                "score": round(float(item.score), 4),
                "score_type": item.score_type,
                "relevance_score": round(float(item.relevance_score), 4),
                "low_confidence": item.is_low_confidence,
                "potentially_off_topic": item.is_potentially_off_topic,
                "matched_terms": item.matched_query_terms[:12],
                "supported_aspects": item.supported_aspects[:8],
                "facts": item.extracted_facts[:8],
                "evidence_text": _truncate(
                    item.selected_sentences or item.content_snippet,
                    900,
                ),
            }
        )
    return payload


def _build_selector_prompt(
    query: str,
    evidence_items: Sequence[EvidenceItem],
    *,
    max_selected: int,
) -> tuple[str, str]:
    system = (
        "You are an evidence selector for a Turkish university support RAG system. "
        "Your job is not to answer the user. Select only the candidate evidence "
        "that directly supports answering the user's question."
    )
    payload = {
        "user_question": query,
        "max_selected": max_selected,
        "selection_rules": [
            "Prefer candidates that directly answer the exact question.",
            "Prefer specific dates, numbers, deadlines, forms, units, conditions, and exceptions.",
            "Use multiple candidates only when they answer different required parts.",
            "Do not select off-topic candidates just because their retrieval score is high.",
            "Do not invent source ids. Return ids only from candidates.",
            "If no candidate directly supports the answer, set insufficient_evidence to true and select no ids.",
        ],
        "candidates": _candidate_payload(evidence_items),
        "required_json_schema": {
            "insufficient_evidence": False,
            "selected_ids": ["source_id_1", "source_id_2"],
            "ranking": [
                {
                    "source_id": "source_id",
                    "answer_usefulness": 0.0,
                    "reason": "short reason",
                }
            ],
            "reason": "short overall reason",
        },
    }
    prompt = (
        "Select the best evidence for final answer synthesis. "
        "Return ONLY valid JSON matching required_json_schema.\n\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    return prompt, system


def _parse_selector_json(raw_text: str) -> dict[str, Any]:
    text = (raw_text or "").strip()
    fenced_match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        text = fenced_match.group(1).strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for match in re.finditer(r"\{", text):
            try:
                payload, _ = decoder.raw_decode(text[match.start():])
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                return payload
        raise
    if not isinstance(payload, dict):
        raise ValueError("selector_json_not_object")
    return payload


def _apply_selection(
    evidence_items: Sequence[EvidenceItem],
    selected_ids: Sequence[str],
    *,
    max_selected: int,
) -> tuple[list[EvidenceItem], int]:
    by_id = {item.source_id: item for item in evidence_items}
    selected: list[EvidenceItem] = []
    seen: set[str] = set()
    valid_llm_selection_count = 0

    for source_id in selected_ids:
        normalized = str(source_id).strip()
        item = by_id.get(normalized)
        if item is None or normalized in seen:
            continue
        selected.append(item)
        seen.add(normalized)
        valid_llm_selection_count += 1
        if len(selected) >= max_selected:
            return selected, valid_llm_selection_count

    # Keep context robust: if the selector was too narrow, backfill from the
    # deterministic ranking so final synthesis still has enough grounding.
    min_keep = min(2, len(evidence_items), max_selected)
    for item in evidence_items:
        if len(selected) >= min_keep:
            break
        if item.source_id in seen:
            continue
        selected.append(item)
        seen.add(item.source_id)

    return selected, valid_llm_selection_count


async def select_evidence_with_llm(
    query: str,
    evidence_items: Sequence[EvidenceItem],
    llm_service: Any,
    *,
    llm_profile: str | None = None,
    max_selected: int | None = None,
) -> tuple[list[EvidenceItem], EvidenceSelectionDecision]:
    """Select final synthesis evidence with an LLM, falling back safely."""
    items = list(evidence_items)
    max_selected = max(1, int(max_selected or settings.rag.llm_evidence_selection_max_selected))
    min_candidates = max(1, int(settings.rag.llm_evidence_selection_min_candidates))

    if not settings.rag.llm_evidence_selection_enabled:
        return items, EvidenceSelectionDecision(
            used_llm=False,
            status="disabled",
            candidate_count=len(items),
        )
    if len(items) < min_candidates:
        return items, EvidenceSelectionDecision(
            used_llm=False,
            status="too_few_candidates",
            candidate_count=len(items),
        )

    candidate_limit = max(min_candidates, int(settings.rag.llm_evidence_selection_max_candidates))
    candidates = items[:candidate_limit]
    prompt, system = _build_selector_prompt(query, candidates, max_selected=max_selected)

    try:
        raw = await asyncio.wait_for(
            llm_service.generate(
                prompt=prompt,
                system=system,
                json_mode=True,
                model_role="evidence_selection",
                llm_profile=llm_profile,
            ),
            timeout=max(1, int(settings.rag.llm_evidence_selection_timeout_seconds)),
        )
        parsed = _parse_selector_json(raw)
    except Exception as exc:
        logger.warning("evidence_selector_fallback reason=%s", type(exc).__name__)
        return items, EvidenceSelectionDecision(
            used_llm=False,
            status="fallback_error",
            reason=type(exc).__name__,
            candidate_count=len(candidates),
        )

    if parsed.get("insufficient_evidence") is True:
        return [], EvidenceSelectionDecision(
            used_llm=True,
            status="insufficient_evidence",
            reason=str(parsed.get("reason", ""))[:500],
            candidate_count=len(candidates),
        )

    raw_ids = parsed.get("selected_ids", [])
    if not isinstance(raw_ids, list):
        raw_ids = []
    selected_ids = [str(value).strip() for value in raw_ids if str(value).strip()]
    selected, valid_selection_count = _apply_selection(
        candidates,
        selected_ids,
        max_selected=max_selected,
    )
    if valid_selection_count == 0:
        return items, EvidenceSelectionDecision(
            used_llm=False,
            status="fallback_empty_selection",
            selected_ids=selected_ids,
            candidate_count=len(candidates),
        )

    ranking = parsed.get("ranking", [])
    if not isinstance(ranking, list):
        ranking = []
    reason = parsed.get("reason", "")
    return selected, EvidenceSelectionDecision(
        used_llm=True,
        status="selected",
        selected_ids=[item.source_id for item in selected],
        ranking=[entry for entry in ranking if isinstance(entry, dict)][:max_selected],
        reason=str(reason)[:500],
        candidate_count=len(candidates),
    )
