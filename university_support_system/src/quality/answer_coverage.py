"""Shadow-only answer coverage checks for contract/facet drift.

The evidence answer validator guards concrete values. This module catches a
different class of issue: the answer may preserve values but respond to the
wrong facet of the evidence, for example answering a CAP process question with
only GPA/graduation conditions. It is diagnostic-only and never enforces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse


@dataclass(frozen=True)
class AnswerCoverageResult:
    mode: str = "shadow"
    status: str = "skipped"
    expected_facet: str | None = None
    reason: str = "not_applicable"
    positive_markers: list[str] = field(default_factory=list)
    drift_markers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "status": self.status,
            "expected_facet": self.expected_facet,
            "reason": self.reason,
            "positive_markers": list(self.positive_markers),
            "drift_markers": list(self.drift_markers),
        }


_APPLICATION_PROCESS_QUERY_MARKERS = (
    "basvurusu nasil yapilir",
    "basvuru nasil yapilir",
    "nasil basvur",
    "basvuru sureci",
    "basvuru islemi",
    "nasil yapilir",
)
_APPLICATION_PROCESS_ANSWER_MARKERS = (
    "basvur",
    "basvuru",
    "dilekce",
    "form",
    "belge",
    "evrak",
    "ogrenci isleri",
    "fakulte",
    "dekanlik",
    "sistem",
    "tarih",
    "duyuru",
    "takvim",
)
_ELIGIBILITY_VALUE_MARKERS = (
    "gano",
    "gno",
    "not ortalamasi",
    "ortalama",
    "3,00",
    "3.00",
    "2,75",
    "2.75",
    "mezuniyet",
    "akts",
    "kredi",
    "sart",
    "kosul",
)
_ELIGIBILITY_QUERY_MARKERS = (
    "not ortalamasi kac",
    "gano kac",
    "gno kac",
    "kac olmali",
    "ortalama kac",
)


def validate_answer_coverage(
    *,
    query: str,
    answer: str,
    responses: Iterable[DepartmentResponse] | None = None,
) -> AnswerCoverageResult:
    expected_facet = _expected_facet(query)
    if expected_facet is None:
        return AnswerCoverageResult()

    answer_text = normalize_text(answer or "")
    evidence_text = normalize_text(_evidence_text(responses or []))

    if expected_facet == "application_process":
        positive = _matched(answer_text, _APPLICATION_PROCESS_ANSWER_MARKERS)
        drift = _matched(answer_text, _ELIGIBILITY_VALUE_MARKERS)
        evidence_positive = _matched(evidence_text, _APPLICATION_PROCESS_ANSWER_MARKERS)
        if positive:
            return AnswerCoverageResult(
                status="pass",
                expected_facet=expected_facet,
                reason="answer_contains_process_markers",
                positive_markers=positive,
                drift_markers=drift,
            )
        if drift and evidence_positive:
            return AnswerCoverageResult(
                status="check",
                expected_facet=expected_facet,
                reason="answer_drifted_to_eligibility_while_process_evidence_exists",
                positive_markers=evidence_positive,
                drift_markers=drift,
            )
        return AnswerCoverageResult(
            status="check",
            expected_facet=expected_facet,
            reason="answer_missing_process_markers",
            positive_markers=evidence_positive,
            drift_markers=drift,
        )

    if expected_facet == "eligibility_value":
        positive = _matched(answer_text, _ELIGIBILITY_VALUE_MARKERS)
        return AnswerCoverageResult(
            status="pass" if positive else "check",
            expected_facet=expected_facet,
            reason="answer_contains_eligibility_markers" if positive else "answer_missing_eligibility_markers",
            positive_markers=positive,
        )

    return AnswerCoverageResult(expected_facet=expected_facet)


def _expected_facet(query: str) -> str | None:
    normalized = normalize_text(query or "")
    if any(marker in normalized for marker in _APPLICATION_PROCESS_QUERY_MARKERS):
        return "application_process"
    if any(marker in normalized for marker in _ELIGIBILITY_QUERY_MARKERS):
        return "eligibility_value"
    return None


def _matched(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if normalize_text(marker) in text]


def _evidence_text(responses: Iterable[DepartmentResponse]) -> str:
    parts: list[str] = []
    for response in responses:
        metadata = response.metadata or {}
        evidence_packet = metadata.get("evidence_packet")
        if isinstance(evidence_packet, dict):
            _collect(evidence_packet.get("supporting_claims"), parts)
            _collect(evidence_packet.get("required_values"), parts)
        for source in response.sources[:5]:
            _collect((source.metadata or {}).get("supporting_claims"), parts)
            _collect((source.metadata or {}).get("required_values"), parts)
    return " ".join(parts)


def _collect(value: Any, parts: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, dict):
        for nested in value.values():
            _collect(nested, parts)
        return
    if isinstance(value, (list, tuple, set)):
        for item in value:
            _collect(item, parts)
        return
    text = str(value).strip()
    if text:
        parts.append(text)
