"""Structured conversation context for capability planning."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.core.constants import Department, TaskType

_COURSE_CODE_RE = re.compile(r"\b[A-ZÇĞİÖŞÜ]{2,6}\s?\d{3,4}\b", re.IGNORECASE)
_SEMESTER_RE = re.compile(r"\b(\d{1,2})\s*\.\s*(?:yariyil|yarıyıl|donem|dönem)\b", re.IGNORECASE)
_CLASS_YEAR_RE = re.compile(r"\b(\d)\s*\.\s*sinif\b", re.IGNORECASE)

_KNOWN_COURSE_PREFIXES = {
    "bil", "eem", "end", "mak", "ins", "muh", "mat", "fiz", "kim",
    "bio", "ist", "ikt", "huk", "tip", "dis", "ecz", "ssd", "ydl",
    "tur", "ata", "ing", "alm", "frn", "egf",
}
_INVALID_COURSE_PREFIXES = {
    "icin", "mayis", "eylul", "ekim", "kasim", "aralik", "ocak",
    "subat", "mart", "nisan", "haziran", "temmuz", "agustos",
}


@dataclass(frozen=True)
class ConversationFrame:
    """Small, explicit frame passed to the capability planner."""

    original_query: str
    effective_query: str
    standalone_query: str | None = None
    is_follow_up: bool = False
    used_context: bool = False
    active_topic: str | None = None
    department_hints: tuple[str, ...] = field(default_factory=tuple)
    source_hints: tuple[str, ...] = field(default_factory=tuple)
    task_type_hint: str | None = None
    announcement_context: bool = False
    rewrite_method: str = "none"
    active_course_code: str | None = None
    active_semester: int | None = None
    active_class_year: int | None = None
    operation: str = "new_topic"
    topic_id: str | None = None
    source_owner: str | None = None
    capability: str | None = None
    policy_facet: str | None = None
    question_type: str | None = None
    entities: dict[str, Any] = field(default_factory=dict)
    temporal_scope: dict[str, Any] = field(default_factory=dict)
    base_turn_index: int | None = None
    confidence: float | None = None
    expires_after_turns: int | None = None

    @classmethod
    def from_resolution_parts(
        cls,
        *,
        original_query: str,
        effective_query: str,
        standalone_query: str | None,
        is_follow_up: bool,
        used_context: bool,
        active_topic: str | None,
        department_hints: list[Department] | tuple[Department, ...],
        source_hints: list[str] | tuple[str, ...],
        task_type_hint: TaskType | None,
        announcement_context: bool,
        rewrite_method: str,
        operation: str = "new_topic",
        topic_id: str | None = None,
        source_owner: str | None = None,
        capability: str | None = None,
        policy_facet: str | None = None,
        question_type: str | None = None,
        entities: dict[str, Any] | None = None,
        temporal_scope: dict[str, Any] | None = None,
        base_turn_index: int | None = None,
        confidence: float | None = None,
        expires_after_turns: int | None = None,
    ) -> "ConversationFrame":
        query_for_inference = standalone_query or effective_query or original_query
        inferred_entities = dict(entities or {})
        active_course_code = _extract_course_code(query_for_inference)
        if active_course_code:
            inferred_entities.setdefault("course_code", active_course_code)
        return cls(
            original_query=original_query,
            effective_query=effective_query,
            standalone_query=standalone_query,
            is_follow_up=is_follow_up,
            used_context=used_context,
            active_topic=active_topic,
            department_hints=tuple(_enum_value(item) for item in department_hints),
            source_hints=tuple(str(item) for item in source_hints if str(item).strip()),
            task_type_hint=_enum_value(task_type_hint) if task_type_hint else None,
            announcement_context=announcement_context,
            rewrite_method=rewrite_method,
            active_course_code=active_course_code,
            active_semester=_extract_int(_SEMESTER_RE, query_for_inference),
            active_class_year=_extract_int(_CLASS_YEAR_RE, query_for_inference),
            operation=operation,
            topic_id=topic_id,
            source_owner=source_owner,
            capability=capability,
            policy_facet=policy_facet,
            question_type=question_type,
            entities=inferred_entities,
            temporal_scope=dict(temporal_scope or {}),
            base_turn_index=base_turn_index,
            confidence=confidence,
            expires_after_turns=expires_after_turns,
        )

    def to_prompt_context(self) -> dict[str, Any]:
        """Return a compact JSON-safe representation for planner prompts."""
        payload = {
            "original_query": self.original_query,
            "effective_query": self.effective_query,
            "standalone_query": self.standalone_query,
            "is_follow_up": self.is_follow_up,
            "used_context": self.used_context,
            "active_topic": self.active_topic,
            "department_hints": list(self.department_hints),
            "source_hints": list(self.source_hints),
            "task_type_hint": self.task_type_hint,
            "announcement_context": self.announcement_context,
            "rewrite_method": self.rewrite_method,
            "active_course_code": self.active_course_code,
            "active_semester": self.active_semester,
            "active_class_year": self.active_class_year,
            "operation": self.operation,
            "topic_id": self.topic_id,
            "source_owner": self.source_owner,
            "capability": self.capability,
            "policy_facet": self.policy_facet,
            "question_type": self.question_type,
            "entities": self.entities,
            "temporal_scope": self.temporal_scope,
            "base_turn_index": self.base_turn_index,
            "confidence": self.confidence,
            "expires_after_turns": self.expires_after_turns,
        }
        return {
            key: value
            for key, value in payload.items()
            if value not in (None, "", [], (), {})
        }


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _extract_course_code(text: str | None) -> str | None:
    if not text:
        return None
    match = _first_valid_course_match(text)
    if match is None:
        return None
    return match.group(0).upper().replace(" ", "")


def _first_valid_course_match(text: str) -> re.Match[str] | None:
    for match in _COURSE_CODE_RE.finditer(text):
        if _is_valid_course_code_match(match):
            return match
    return None


def _is_valid_course_code_match(match: re.Match[str]) -> bool:
    raw = match.group(0).replace(" ", "")
    prefix = re.sub(r"\d+", "", raw)
    normalized_prefix = _normalize_ascii(prefix)
    if normalized_prefix in _INVALID_COURSE_PREFIXES:
        return False
    if normalized_prefix in _KNOWN_COURSE_PREFIXES:
        return True
    return prefix == prefix.upper() and len(prefix) <= 5


def _normalize_ascii(text: str) -> str:
    table = str.maketrans({
        "Ç": "c", "Ğ": "g", "İ": "i", "I": "i", "Ö": "o", "Ş": "s", "Ü": "u",
        "ç": "c", "ğ": "g", "ı": "i", "i": "i", "ö": "o", "ş": "s", "ü": "u",
    })
    return text.translate(table).lower()


def _extract_int(pattern: re.Pattern[str], text: str | None) -> int | None:
    if not text:
        return None
    match = pattern.search(text)
    if match is None:
        return None
    try:
        return int(match.group(1))
    except (TypeError, ValueError):
        return None
