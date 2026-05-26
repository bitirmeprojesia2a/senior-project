"""Shadow-only semantic value conflict checks.

The evidence-answer validator answers "did the final answer preserve required
values?". This module answers a narrower semantic question: for single-value
questions, did the answer present competing threshold values as if they were
the main answer?
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse

_VALUE_RE = re.compile(r"(?:%\s*\d+(?:[,.]\d+)?|\b\d+(?:[,.]\d+)?\b)")
_THRESHOLD_WINDOW_RE = re.compile(
    r"(?:en\s+az|en\s+cok|en\s+çok|en\s+fazla|asgari|azami|minimum|maksimum"
    r"|kadar\s+dusebilir|kadar\s+duser|kadar\s+duşebilir|kadar\s+düşer"
    r"|altina\s+dusemez|altına\s+düşemez|olmasi|olması|olmali|olmalidir"
    r"|gerekir|gerekmektedir|sarttir|şarttır|zorunludur)"
)
_SCALE_WINDOW_RE = re.compile(r"\b(?:uzerinden|üzerinden|puan\s+uzerinden|puan\s+üzerinden)\b")

_GPA_QUERY_MARKERS = (
    "not ortalamasi",
    "not ortalaması",
    "ortalama",
    "gano",
    "gno",
)
_SINGLE_VALUE_QUERY_MARKERS = (
    "kac",
    "kaç",
    "ne olmali",
    "ne olmalı",
    "kac olmali",
    "kaç olmalı",
    "sart",
    "şart",
    "kosul",
    "koşul",
)
_COMPARISON_MARKERS = (
    "yandal icin",
    "yan dal icin",
    "yandal için",
    "cap icin",
    "çap için",
    "cift anadal icin",
    "çift anadal için",
    "mezuniyet icin",
    "mezuniyet için",
    "ayri olarak",
    "ayrı olarak",
    "karsilastir",
    "karşılaştır",
)


@dataclass(frozen=True)
class AnswerValueRole:
    value: str
    canonical: str
    role: str
    aspect: str
    reason: str
    source: str = "answer"

    def to_dict(self) -> dict[str, str]:
        return {
            "value": self.value,
            "canonical": self.canonical,
            "role": self.role,
            "aspect": self.aspect,
            "reason": self.reason,
            "source": self.source,
        }


@dataclass(frozen=True)
class AnswerValueConflictResult:
    mode: str = "shadow"
    status: str = "skipped"  # skipped | pass | check
    reason: str = "not_applicable"
    aspect: str | None = None
    primary_answer_value: str | None = None
    competing_values: list[str] = field(default_factory=list)
    value_roles: list[AnswerValueRole] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "status": self.status,
            "reason": self.reason,
            "aspect": self.aspect,
            "primary_answer_value": self.primary_answer_value,
            "competing_values": list(self.competing_values),
            "value_roles": [role.to_dict() for role in self.value_roles],
        }


def validate_answer_value_conflicts(
    *,
    query: str,
    answer: str,
    responses: Iterable[DepartmentResponse] | None = None,
    mode: str = "shadow",
) -> AnswerValueConflictResult:
    """Detect competing answer values without calling an LLM."""

    if mode == "off":
        return AnswerValueConflictResult(mode=mode, reason="disabled")

    normalized_query = normalize_text(query or "")
    aspect = _query_value_aspect(normalized_query)
    if aspect is None:
        return AnswerValueConflictResult(mode=mode)
    if not _is_single_value_question(normalized_query):
        return AnswerValueConflictResult(
            mode=mode,
            status="pass",
            reason="query_not_single_value",
            aspect=aspect,
        )

    answer_text = normalize_text(answer or "")
    answer_roles = _classify_answer_values(answer_text, aspect=aspect)
    threshold_roles = [
        role for role in answer_roles
        if role.role in {"answer_threshold", "conflicting_threshold"}
    ]
    unique_thresholds = _dedupe_roles_by_canonical(threshold_roles)
    if not unique_thresholds:
        return AnswerValueConflictResult(
            mode=mode,
            status="pass",
            reason="no_answer_threshold_values",
            aspect=aspect,
            value_roles=answer_roles,
        )

    primary = unique_thresholds[0]
    competing = [
        role for role in unique_thresholds[1:]
        if role.canonical != primary.canonical
    ]
    explicit_comparison = _has_explicit_comparison_context(answer_text)
    evidence_primary = _evidence_primary_threshold_roles(
        query=query,
        answer=answer,
        responses=responses,
        aspect=aspect,
    )
    if evidence_primary and not explicit_comparison:
        expected_canonicals = {role.canonical for role in evidence_primary if role.canonical}
        if primary.canonical not in expected_canonicals:
            return AnswerValueConflictResult(
                mode=mode,
                status="check",
                reason="answer_primary_value_conflicts_with_evidence",
                aspect=aspect,
                primary_answer_value=primary.value,
                competing_values=[role.value for role in evidence_primary],
                value_roles=[
                    primary,
                    *[
                        AnswerValueRole(
                            value=role.value,
                            canonical=role.canonical,
                            role="conflicting_threshold",
                            aspect=role.aspect,
                            reason="expected_primary_evidence_threshold",
                            source=role.source,
                        )
                        for role in evidence_primary
                        if role.canonical != primary.canonical
                    ],
                    *[role for role in answer_roles if role.role not in {"answer_threshold", "conflicting_threshold"}],
                ],
            )
    if competing and not explicit_comparison:
        value_roles = [
            primary,
            *[
                AnswerValueRole(
                    value=role.value,
                    canonical=role.canonical,
                    role="conflicting_threshold",
                    aspect=role.aspect,
                    reason="competes_with_primary_threshold",
                    source=role.source,
                )
                for role in competing
            ],
            *[role for role in answer_roles if role.role not in {"answer_threshold", "conflicting_threshold"}],
        ]
        return AnswerValueConflictResult(
            mode=mode,
            status="check",
            reason="multiple_competing_threshold_values",
            aspect=aspect,
            primary_answer_value=primary.value,
            competing_values=[role.value for role in competing],
            value_roles=value_roles,
        )

    return AnswerValueConflictResult(
        mode=mode,
        status="pass",
        reason="single_primary_threshold",
        aspect=aspect,
        primary_answer_value=primary.value,
        value_roles=answer_roles,
    )


def _query_value_aspect(normalized_query: str) -> str | None:
    if any(marker in normalized_query for marker in _GPA_QUERY_MARKERS):
        return "gpa"
    return None


def _is_single_value_question(normalized_query: str) -> bool:
    return any(marker in normalized_query for marker in _SINGLE_VALUE_QUERY_MARKERS)


def _classify_answer_values(answer_text: str, *, aspect: str) -> list[AnswerValueRole]:
    roles: list[AnswerValueRole] = []
    for match in _VALUE_RE.finditer(answer_text):
        raw = match.group(0).strip()
        canonical = _canonicalize(raw)
        if not canonical:
            continue
        window_before = answer_text[max(0, match.start() - 55): match.start()]
        window_after = answer_text[match.end(): match.end() + 55]
        window = f"{window_before} {raw} {window_after}"
        if raw.startswith("%"):
            roles.append(
                AnswerValueRole(
                    value=raw,
                    canonical=canonical,
                    role="related_condition",
                    aspect="percentage",
                    reason="percent_condition",
                )
            )
            continue
        if _SCALE_WINDOW_RE.search(window_after[:30]):
            roles.append(
                AnswerValueRole(
                    value=raw,
                    canonical=canonical,
                    role="scale_value",
                    aspect=aspect,
                    reason="scale_context",
                )
            )
            continue
        if _THRESHOLD_WINDOW_RE.search(window):
            roles.append(
                AnswerValueRole(
                    value=raw,
                    canonical=canonical,
                    role="answer_threshold",
                    aspect=aspect,
                    reason="threshold_context",
                )
            )
            continue
        roles.append(
            AnswerValueRole(
                value=raw,
                canonical=canonical,
                role="supporting_value",
                aspect=aspect,
                reason="numeric_context",
            )
        )
    return roles


def _has_explicit_comparison_context(answer_text: str) -> bool:
    return sum(1 for marker in _COMPARISON_MARKERS if marker in answer_text) >= 2


def _evidence_primary_threshold_roles(
    *,
    query: str,
    answer: str,
    responses: Iterable[DepartmentResponse] | None,
    aspect: str,
) -> list[AnswerValueRole]:
    if not responses:
        return []
    try:
        from src.quality.evidence_answer_validator import validate_evidence_answer

        validation = validate_evidence_answer(query=query, answer=answer, responses=list(responses))
    except Exception:
        return []
    arbitration = validation.value_arbitration or {}
    primary_values = arbitration.get("primary_values") or []
    roles: list[AnswerValueRole] = []
    for value in primary_values:
        raw = str(value)
        canonical = _canonicalize(raw)
        if not canonical:
            continue
        roles.append(
            AnswerValueRole(
                value=raw,
                canonical=canonical,
                role="answer_threshold",
                aspect=aspect,
                reason="evidence_primary_threshold",
                source="evidence",
            )
        )
    return _dedupe_roles_by_canonical(roles)


def _canonicalize(value: str) -> str:
    cleaned = normalize_text(value).replace("%", "").replace(" ", "")
    if not cleaned:
        return ""
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        number = float(cleaned)
    except ValueError:
        return ""
    return f"{number:.4f}".rstrip("0").rstrip(".")


def _dedupe_roles_by_canonical(roles: list[AnswerValueRole]) -> list[AnswerValueRole]:
    seen: set[str] = set()
    result: list[AnswerValueRole] = []
    for role in roles:
        if role.canonical in seen:
            continue
        seen.add(role.canonical)
        result.append(role)
    return result
