"""Evidence policy derived from the central source ownership registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Sequence

from src.core.source_ownership import (
    OWNER_ACADEMIC_CALENDAR,
    OWNER_ANNOUNCEMENT_SEARCH,
    OWNER_CURRICULUM_CATALOG,
    OWNER_EVENT_SEARCH,
    OWNER_INTERNATIONAL_POLICY,
    OWNER_PERSONAL_STUDENT_DATA,
    OWNER_STUDENT_AFFAIRS_POLICY,
    OWNER_TUITION_FEE_CATALOG,
    OWNER_WEEKLY_SCHEDULE,
)
from src.core.text_normalization import normalize_text

SourceOwnerPolicyMode = Literal["off", "advisory", "balanced", "strict"]

SOURCE_OWNER_POLICY_SCHEMA = "omu.source_owner_policy.v1"
STRUCTURED_SOURCE_OWNERS = frozenset(
    {
        OWNER_ACADEMIC_CALENDAR,
        OWNER_CURRICULUM_CATALOG,
        OWNER_TUITION_FEE_CATALOG,
        OWNER_WEEKLY_SCHEDULE,
    }
)


@dataclass(frozen=True)
class SourceOwnerEvidencePolicy:
    owner: str
    preferred_markers: tuple[str, ...] = ()
    avoid_markers: tuple[str, ...] = ()
    structured_required: bool = False
    description: str | None = None


@dataclass(frozen=True)
class SourceOwnerPolicyApplication:
    results: list[dict[str, Any]]
    diagnostics: dict[str, Any]
    should_block: bool = False
    fallback_answer: str | None = None


SOURCE_OWNER_POLICIES: dict[str, SourceOwnerEvidencePolicy] = {
    OWNER_ACADEMIC_CALENDAR: SourceOwnerEvidencePolicy(
        owner=OWNER_ACADEMIC_CALENDAR,
        preferred_markers=(
            "akademik takvim",
            "genel akademik takvim",
            "calendar",
            "derslerin baslamasi",
            "derslerin bitimi",
            "final sinavlari",
            "butunleme",
            "not giris",
        ),
        avoid_markers=("duyuru", "etkinlik", "haber"),
        structured_required=True,
        description="Academic calendar dates should come from the calendar source family.",
    ),
    OWNER_TUITION_FEE_CATALOG: SourceOwnerEvidencePolicy(
        owner=OWNER_TUITION_FEE_CATALOG,
        preferred_markers=(
            "ogrenim ucreti",
            "harc",
            "ucret tablosu",
            "tuition",
            "katki payi",
            "fee",
        ),
        avoid_markers=("burs", "duyuru", "etkinlik"),
        structured_required=True,
        description="Tuition amounts should come from the fee catalog source family.",
    ),
    OWNER_CURRICULUM_CATALOG: SourceOwnerEvidencePolicy(
        owner=OWNER_CURRICULUM_CATALOG,
        preferred_markers=(
            "mufredat",
            "ders plani",
            "akts",
            "kredi",
            "course",
            "curriculum",
            "yariyil",
        ),
        avoid_markers=("duyuru", "etkinlik", "konukevi"),
        structured_required=True,
        description="Course and curriculum facts should come from curriculum records.",
    ),
    OWNER_WEEKLY_SCHEDULE: SourceOwnerEvidencePolicy(
        owner=OWNER_WEEKLY_SCHEDULE,
        preferred_markers=(
            "haftalik ders programi",
            "ders programi",
            "haftalik program",
            "schedule",
            "gun",
            "saat",
            "derslik",
        ),
        avoid_markers=("duyuru", "etkinlik"),
        structured_required=True,
        description="Weekly schedule facts should come from schedule records.",
    ),
    OWNER_STUDENT_AFFAIRS_POLICY: SourceOwnerEvidencePolicy(
        owner=OWNER_STUDENT_AFFAIRS_POLICY,
        preferred_markers=(
            "yonetmelik",
            "yonerge",
            "ogrenci isleri",
            "sik sorulan sorular",
            "sss",
            "kayit",
            "basvuru",
        ),
        avoid_markers=("konukevi", "etkinlik", "haber"),
        description="Student affairs policy answers should prefer official policy documents.",
    ),
    OWNER_INTERNATIONAL_POLICY: SourceOwnerEvidencePolicy(
        owner=OWNER_INTERNATIONAL_POLICY,
        preferred_markers=(
            "uluslararasi ogrenci",
            "yabanci ogrenci",
            "international",
            "yos",
            "tomer",
            "ikamet",
            "denklik",
            "kabul",
            "evrak",
        ),
        avoid_markers=("konukevi", "yemek bursu", "etkinlik", "spor"),
        description="International student policy answers should prefer international policy sources.",
    ),
    OWNER_ANNOUNCEMENT_SEARCH: SourceOwnerEvidencePolicy(
        owner=OWNER_ANNOUNCEMENT_SEARCH,
        preferred_markers=("announcement", "duyuru", "ilan", "haber"),
        description="Announcement questions should stay on announcement records.",
    ),
    OWNER_EVENT_SEARCH: SourceOwnerEvidencePolicy(
        owner=OWNER_EVENT_SEARCH,
        preferred_markers=("event", "etkinlik", "seminer", "konferans", "workshop"),
        description="Event questions should stay on event records.",
    ),
    OWNER_PERSONAL_STUDENT_DATA: SourceOwnerEvidencePolicy(
        owner=OWNER_PERSONAL_STUDENT_DATA,
        preferred_markers=("auth", "student data", "ogrenci verisi"),
        structured_required=True,
        description="Personal student data must not be answered from generic RAG evidence.",
    ),
}


def apply_source_owner_policy(
    results: Sequence[dict[str, Any]],
    source_owner: dict[str, Any] | None,
    *,
    mode: SourceOwnerPolicyMode = "advisory",
    min_compatible_score: float = 0.30,
) -> SourceOwnerPolicyApplication:
    """Apply owner-derived evidence bias and optional guard diagnostics."""
    original_results = [dict(item) for item in results]
    owner = _source_owner_primary(source_owner)
    if mode == "off" or not owner:
        return SourceOwnerPolicyApplication(
            results=original_results,
            diagnostics=_diagnostics(
                owner=owner,
                mode=mode,
                status="skipped",
                reason="disabled_or_missing_owner",
                result_count=len(original_results),
            ),
        )

    policy = SOURCE_OWNER_POLICIES.get(owner)
    if policy is None:
        return SourceOwnerPolicyApplication(
            results=original_results,
            diagnostics=_diagnostics(
                owner=owner,
                mode=mode,
                status="skipped",
                reason="unknown_owner",
                result_count=len(original_results),
            ),
        )

    preferred = _normalized_markers(policy.preferred_markers)
    avoid = _normalized_markers(policy.avoid_markers)
    adjusted: list[dict[str, Any]] = []
    compatible_count = 0
    compatible_best_score = 0.0
    avoided_count = 0
    changed = False

    for item in original_results:
        candidate = dict(item)
        metadata = dict(candidate.get("metadata") or {})
        haystack = _candidate_haystack(candidate)
        matched_preferred = bool(preferred and any(marker in haystack for marker in preferred))
        matched_avoid = bool(avoid and any(marker in haystack for marker in avoid))
        score = _score(candidate)
        updated_score = score

        if matched_preferred:
            compatible_count += 1
            compatible_best_score = max(compatible_best_score, score)
            updated_score += 0.18
        if matched_avoid:
            avoided_count += 1
            updated_score *= 0.40

        if updated_score != score:
            candidate["score"] = round(updated_score, 6)
            changed = True

        metadata["source_owner_policy_owner"] = owner
        metadata["source_owner_compatible"] = matched_preferred
        metadata["source_owner_avoid_match"] = matched_avoid
        metadata["source_owner_policy_mode"] = mode
        candidate["metadata"] = metadata
        adjusted.append(candidate)

    if changed:
        adjusted.sort(key=lambda item: _score(item), reverse=True)

    should_block = _should_block(
        mode=mode,
        policy=policy,
        result_count=len(original_results),
        compatible_count=compatible_count,
        compatible_best_score=compatible_best_score,
        min_compatible_score=min_compatible_score,
    )
    status = "blocked" if should_block else "applied"
    diagnostics = _diagnostics(
        owner=owner,
        mode=mode,
        status=status,
        reason=None,
        result_count=len(original_results),
        compatible_count=compatible_count,
        compatible_best_score=round(compatible_best_score, 4),
        avoided_count=avoided_count,
        structured_required=policy.structured_required,
        min_compatible_score=min_compatible_score,
        preferred_markers=list(policy.preferred_markers),
        avoid_markers=list(policy.avoid_markers),
    )
    return SourceOwnerPolicyApplication(
        results=adjusted,
        diagnostics=diagnostics,
        should_block=should_block,
        fallback_answer=_fallback_answer(owner, policy) if should_block else None,
    )


def _source_owner_primary(source_owner: dict[str, Any] | None) -> str | None:
    if not isinstance(source_owner, dict):
        return None
    owner = str(source_owner.get("primary") or "").strip().lower()
    return owner or None


def _should_block(
    *,
    mode: SourceOwnerPolicyMode,
    policy: SourceOwnerEvidencePolicy,
    result_count: int,
    compatible_count: int,
    compatible_best_score: float,
    min_compatible_score: float,
) -> bool:
    if mode == "advisory":
        return False
    if result_count <= 0:
        return False
    has_compatible = compatible_count > 0 and compatible_best_score >= min_compatible_score
    if mode == "strict":
        return not has_compatible
    if mode == "balanced":
        return bool(policy.structured_required and not has_compatible)
    return False


def _fallback_answer(owner: str, policy: SourceOwnerEvidencePolicy) -> str:
    if owner == OWNER_PERSONAL_STUDENT_DATA:
        return (
            "Bu soru kisisel ogrenci verisi gerektiriyor. Bu bilgi genel belgelerden "
            "yanitlanamaz; kimlik dogrulamasi olan resmi ogrenci kaynagi gerekir."
        )
    if policy.structured_required:
        return (
            "Bu soru icin beklenen resmi kaynak ailesinde yeterli ve uyumlu kanit "
            "bulunamadi. Yanlis kaynakla tahmin yapmak yerine ilgili resmi kaynagin "
            "guncel kaydini kontrol etmek gerekir."
        )
    return (
        "Bu soru icin beklenen kaynak ailesiyle uyumlu yeterli kanit bulunamadi. "
        "Soruyu biraz daha netlestirebilir veya ilgili birime basvurabilirsiniz."
    )


def _diagnostics(
    *,
    owner: str | None,
    mode: SourceOwnerPolicyMode,
    status: str,
    reason: str | None,
    result_count: int,
    compatible_count: int = 0,
    compatible_best_score: float = 0.0,
    avoided_count: int = 0,
    structured_required: bool = False,
    min_compatible_score: float = 0.30,
    preferred_markers: list[str] | None = None,
    avoid_markers: list[str] | None = None,
) -> dict[str, Any]:
    diagnostics = {
        "schema": SOURCE_OWNER_POLICY_SCHEMA,
        "mode": mode,
        "owner": owner,
        "status": status,
        "result_count": result_count,
        "compatible_count": compatible_count,
        "compatible_best_score": compatible_best_score,
        "avoided_count": avoided_count,
        "structured_required": structured_required,
        "min_compatible_score": min_compatible_score,
        "should_block": status == "blocked",
    }
    if reason:
        diagnostics["reason"] = reason
    if preferred_markers is not None:
        diagnostics["preferred_markers"] = preferred_markers
    if avoid_markers is not None:
        diagnostics["avoid_markers"] = avoid_markers
    return diagnostics


def _normalized_markers(markers: Sequence[str]) -> tuple[str, ...]:
    normalized = [normalize_text(marker).strip() for marker in markers]
    return tuple(dict.fromkeys(marker for marker in normalized if marker))


def _candidate_haystack(item: dict[str, Any]) -> str:
    metadata = item.get("metadata") or {}
    values = [
        item.get("source"),
        item.get("source_url"),
        metadata.get("source"),
        metadata.get("filename"),
        metadata.get("file_name"),
        metadata.get("display_source"),
        metadata.get("title"),
        metadata.get("relative_path"),
        metadata.get("source_url"),
        metadata.get("category"),
        metadata.get("subcategory"),
        metadata.get("record_type"),
        str(item.get("content") or "")[:1200],
    ]
    return " ".join(normalize_text(value) for value in values if value)


def _score(item: dict[str, Any]) -> float:
    try:
        return float(item.get("score", 0.0))
    except (TypeError, ValueError):
        return 0.0
