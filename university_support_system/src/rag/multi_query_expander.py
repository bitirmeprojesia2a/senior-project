"""Deterministic multi-query expansion for improved RAG recall.

Generates multiple reformulations of a user query to capture synonyms,
paraphrases, and solution-oriented perspectives. Each variant is searched
independently and results are merged with deduplication.

This module does NOT use LLM calls — all expansions are rule-based and
deterministic, ensuring reproducibility and zero latency overhead beyond
the additional retrieval calls.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from src.core.text_normalization import normalize_text

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExpandedQueries:
    """Container for the original query and its deterministic variants."""

    original: str
    variants: tuple[str, ...] = ()
    profile: str | None = None

    @property
    def all_queries(self) -> tuple[str, ...]:
        """Return the original query followed by all variants."""
        return (self.original, *self.variants)


# ── Synonym-based paraphrase mappings ─────────────────────────────
# Each entry maps a normalized trigger phrase to a list of alternative
# phrasings. When the trigger is found in the query, a variant is
# produced by substituting each alternative.

_PARAPHRASE_MAP: dict[str, tuple[str, ...]] = {
    # Ders bitişi / son ders
    "son ders tarihi": ("derslerin bitimi", "ders bitis tarihi", "derslerin sonu"),
    "derslerin bitimi": ("son ders tarihi", "ders bitis tarihi", "derslerin sonu"),
    "ders bitis": ("derslerin bitimi", "son ders tarihi"),
    "derslerin sonu": ("derslerin bitimi", "son ders tarihi"),
    "dersler ne zaman bitiyor": ("derslerin bitimi ne zaman", "son ders tarihi nedir"),
    "dersler ne zaman biter": ("derslerin bitimi ne zaman", "son ders tarihi nedir"),
    # Ders başlangıcı
    "ders baslangic": ("derslerin baslamasi", "dersler ne zaman basliyor"),
    "derslerin baslamasi": ("ders baslangic tarihi", "dersler ne zaman basliyor"),
    "dersler ne zaman basliyor": ("derslerin baslamasi ne zaman", "ders baslangic tarihi"),
    "dersler ne zaman baslar": ("derslerin baslamasi ne zaman", "ders baslangic tarihi"),
    # Final / yarıyıl sonu
    "final sinav": ("yariyil sonu sinav", "donem sonu sinav"),
    "yariyil sonu sinav": ("final sinav", "donem sonu sinav"),
    "donem sonu sinav": ("final sinav", "yariyil sonu sinav"),
    # Bütünleme
    "butunleme sinav": ("ek sinav", "telafi sinav"),
    # Tek ders
    "tek ders sinavi": ("tek ders", "mezuniyet sinavi"),
    "tek ders": ("tek ders sinavi", "mezuniyet sinavi"),
    # Yaz okulu
    "yaz okulu": ("yaz donemi", "yaz ogretimi"),
    # Kayıt
    "kayit dondurma": ("donem dondurma", "donem izni"),
    "donem dondurma": ("kayit dondurma", "donem izni"),
    # Muafiyet
    "muafiyet": ("intibak", "ders muafiyeti"),
    "intibak": ("muafiyet", "ders muafiyeti"),
}

# ── Solution-oriented expansion profiles ──────────────────────────
# When a query matches a "problem profile", additional sub-queries are
# generated to search for solution alternatives.

_SOLUTION_PROFILES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    # profile_name: (trigger_markers, solution_sub_queries)
    "course_delay": (
        (
            "okulum uzuyor",
            "okul uzuyor",
            "donem uzuyor",
            "donemim uzuyor",
            "ders yuzunden",
            "dersimden kaldim",
            "dersten kaldim",
            "basarisiz oldugum",
            "basarisiz oldum",
            "hic almadigim",
            "eksik ders",
            "alt donem ders",
            "mezun olamiyorum",
            "uzatma",
        ),
        (
            "tek ders sinavi kosullari ve basvuru",
            "yaz okulu ders alma sartlari",
            "butunleme sinavi hakki ve kosullari",
            "azami ogrenim suresi ek sure hakki",
        ),
    ),
    "single_exam": (
        (
            "tek ders sinavi",
            "tek derse girebilir miyim",
            "tek ders",
        ),
        (
            "tek ders sinavi kosullari devam sarti",
            "tek ders sinavi basvuru sureci",
        ),
    ),
    "summer_school": (
        (
            "yaz okulu",
            "yaz okuluna",
            "yaz okulundan",
        ),
        (
            "yaz okulu ders alma kosullari",
            "yaz okulu ucret ve basvuru",
        ),
    ),
}


def expand_query(query: str) -> ExpandedQueries:
    """Generate deterministic query variants for multi-query retrieval.

    Returns an ``ExpandedQueries`` container with at most 3 variants
    (to keep retrieval cost bounded). The original query is always
    the primary search term.
    """
    normalized = normalize_text(query)
    variants: list[str] = []
    matched_profile: str | None = None

    # 1. Synonym/paraphrase variants
    for trigger, alternatives in sorted(
        _PARAPHRASE_MAP.items(), key=lambda kv: len(kv[0]), reverse=True
    ):
        if trigger not in normalized:
            continue
        for alt in alternatives:
            variant = normalized.replace(trigger, alt, 1)
            # Restore original non-normalized tokens where possible
            variant_clean = _restore_original_tokens(query, trigger, alt)
            if variant_clean and variant_clean != query:
                variants.append(variant_clean)
            elif variant != normalized:
                variants.append(variant)
            if len(variants) >= 2:
                break
        break  # Only apply the first (longest) matching trigger

    # 2. Solution-oriented sub-queries
    for profile, (triggers, sub_queries) in _SOLUTION_PROFILES.items():
        if not any(marker in normalized for marker in triggers):
            continue
        matched_profile = profile
        for sub_query in sub_queries:
            if sub_query not in variants and normalize_text(sub_query) != normalized:
                variants.append(sub_query)
        break  # Only apply the first matching profile

    # 3. Strip department/program names from academic calendar queries
    # "Bilgisayar muhendisligi bahar donemi son ders tarihi" ->
    # also search "bahar donemi son ders tarihi" (without program name)
    calendar_variant = _strip_program_name_for_calendar(query, normalized)
    if calendar_variant and calendar_variant not in variants:
        variants.insert(0, calendar_variant)

    # Cap at 3 variants to keep retrieval cost bounded
    unique_variants = _deduplicate_variants(query, variants[:5])[:3]

    if unique_variants:
        logger.info(
            "multi_query_expanded original=%s variants=%s profile=%s",
            query,
            unique_variants,
            matched_profile,
        )

    return ExpandedQueries(
        original=query,
        variants=tuple(unique_variants),
        profile=matched_profile,
    )


# ── Calendar-specific: strip program names ────────────────────────

_CALENDAR_SIGNAL_MARKERS = (
    "son ders",
    "ders bitis",
    "derslerin bitimi",
    "derslerin baslamasi",
    "ders baslangic",
    "final sinav",
    "yariyil sonu sinav",
    "donem sonu sinav",
    "butunleme sinav",
    "ara sinav",
    "akademik takvim",
    "sinav takvim",
    "not giris",
)

_PROGRAM_NAME_RE = re.compile(
    r"\b(?:bilgisayar|elektrik|elektronik|makine|insaat|gida|cevre|kimya|"
    r"fizik|matematik|biyoloji|tarih|edebiyat|hukuk|tip|eczacilik|"
    r"dis hekimligi|hemsirelik|isletme|iktisat|maliye|"
    r"muhendisligi?|fakultesi?|bolumu?|programi?|lisans|onlisans)\b",
    re.IGNORECASE,
)


def _strip_program_name_for_calendar(original: str, normalized: str) -> str | None:
    """If a query has strong calendar signals plus a program name, produce a
    variant without the program name so the calendar matcher can succeed."""
    has_calendar_signal = any(marker in normalized for marker in _CALENDAR_SIGNAL_MARKERS)
    if not has_calendar_signal:
        return None
    has_program = bool(_PROGRAM_NAME_RE.search(normalized))
    if not has_program:
        return None
    # Strip program name tokens
    cleaned = _PROGRAM_NAME_RE.sub("", normalize_text(original))
    # Also remove "icin", "deki", "nin" etc. that become orphaned
    cleaned = re.sub(r"\b(icin|deki|nin|daki|den|dan|nda|ndaki)\b", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned if cleaned and cleaned != normalized else None


def _restore_original_tokens(
    original: str, trigger: str, replacement: str
) -> str | None:
    """Try to produce a variant using the original query's casing/accents."""
    norm_original = normalize_text(original)
    idx = norm_original.find(trigger)
    if idx < 0:
        return None
    # Replace the matched span in the original query
    prefix = original[:idx]
    suffix = original[idx + len(trigger):]
    return f"{prefix}{replacement}{suffix}".strip() or None


def _deduplicate_variants(original: str, variants: list[str]) -> list[str]:
    """Remove variants that are identical to the original after normalization."""
    norm_original = normalize_text(original)
    seen = {norm_original}
    result: list[str] = []
    for variant in variants:
        norm_variant = normalize_text(variant)
        if norm_variant in seen or not norm_variant.strip():
            continue
        seen.add(norm_variant)
        result.append(variant)
    return result
