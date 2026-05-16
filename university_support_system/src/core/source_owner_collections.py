"""Collection bridge rules for source-owner based evidence retrieval.

Source ownership answers "which authority owns the final answer"; corpus
placement answers "which indexed collection currently contains the evidence".
These two are intentionally separate because some student-affairs policies are
stored under academic-program policy directories in the raw corpus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.constants import Department, collection_name_for_department
from src.core.source_ownership import (
    OWNER_INTERNATIONAL_POLICY,
    OWNER_STUDENT_AFFAIRS_POLICY,
)
from src.core.text_normalization import normalize_text


@dataclass(frozen=True)
class SourceOwnerCollectionBridge:
    """Evidence collection expansion derived from source ownership."""

    source_owner: str | None = None
    support_collections: tuple[str, ...] = ()
    reason: str | None = None
    activated_by: tuple[str, ...] = field(default_factory=tuple)

    @property
    def active(self) -> bool:
        return bool(self.support_collections)

    def as_metadata(self) -> dict[str, Any]:
        return {
            "source_owner": self.source_owner,
            "support_collections": list(self.support_collections),
            "reason": self.reason,
            "activated_by": list(self.activated_by),
        }


_STUDENT_POLICY_ACADEMIC_CORPUS_MARKERS = (
    "cap",
    "cift ana dal",
    "cift anadal",
    "cift_ana_dal",
    "çift ana dal",
    "çift anadal",
    "yandal",
    "yan dal",
    "gano",
    "gno",
    "not ortalamasi",
    "not ortalaması",
    "ozel ogrenci",
    "özel öğrenci",
    "uzaktan egitim",
    "uzaktan eğitim",
    "karma egitim",
    "karma eğitim",
    "pedagojik formasyon",
)

_INTERNATIONAL_POLICY_ACADEMIC_CORPUS_MARKERS = (
    "uluslararasi ogrenci",
    "uluslararası öğrenci",
    "yabanci ogrenci",
    "yabancı öğrenci",
    "ikamet",
    "oturma izni",
    "yos",
    "tomer",
    "denklik",
)


def resolve_source_owner_collection_bridge(
    *,
    source_owner: str | None,
    query: str,
    department: Department | str | None = None,
    source_hints: list[str] | None = None,
    topic_hint: str | None = None,
) -> SourceOwnerCollectionBridge:
    """Return support collections that may contain evidence for an owner.

    The bridge only expands evidence search. It does not change final answer
    ownership, router decisions, or selected specialist identity.
    """
    owner = str(source_owner or "").strip()
    if not owner:
        return SourceOwnerCollectionBridge()

    haystack = _normalized_haystack(query=query, source_hints=source_hints, topic_hint=topic_hint)
    support: list[str] = []
    activated_by: list[str] = []
    reason: str | None = None

    if owner == OWNER_STUDENT_AFFAIRS_POLICY:
        activated_by = _matching_markers(haystack, _STUDENT_POLICY_ACADEMIC_CORPUS_MARKERS)
        if activated_by:
            support.append(collection_name_for_department(Department.ACADEMIC_PROGRAMS))
            reason = "student_affairs_policy_cross_corpus"

    elif owner == OWNER_INTERNATIONAL_POLICY:
        activated_by = _matching_markers(haystack, _INTERNATIONAL_POLICY_ACADEMIC_CORPUS_MARKERS)
        if activated_by:
            support.append(collection_name_for_department(Department.ACADEMIC_PROGRAMS))
            reason = "international_policy_academic_corpus"

    primary_collection = _department_collection_or_none(department)
    support_tuple = tuple(
        collection
        for collection in dict.fromkeys(support)
        if collection and collection != primary_collection
    )
    return SourceOwnerCollectionBridge(
        source_owner=owner,
        support_collections=support_tuple,
        reason=reason if support_tuple else None,
        activated_by=tuple(activated_by if support_tuple else ()),
    )


def _normalized_haystack(
    *,
    query: str,
    source_hints: list[str] | None,
    topic_hint: str | None,
) -> str:
    parts = [query or "", topic_hint or "", *(source_hints or [])]
    normalized_parts: list[str] = []
    for part in parts:
        text = str(part or "").strip()
        if not text:
            continue
        normalized_parts.append(normalize_text(text))
        normalized_parts.append(normalize_text(text.replace("_", " ").replace("-", " ")))
    return " ".join(part for part in normalized_parts if part)


def _matching_markers(haystack: str, markers: tuple[str, ...]) -> list[str]:
    return [
        marker
        for marker in markers
        if normalize_text(marker) in haystack
    ]


def _department_collection_or_none(department: Department | str | None) -> str | None:
    if department is None:
        return None
    try:
        normalized = department if isinstance(department, Department) else Department(str(department))
    except ValueError:
        return None
    return collection_name_for_department(normalized)
