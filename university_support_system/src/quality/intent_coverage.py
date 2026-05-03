"""Marker-based intent coverage for multi-part questions.

Detects sub-intents in a query and checks whether the evidence set
covers them.  When coverage is low, the caller can widen retrieval
before generating an answer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.core.text_normalization import normalize_text


# ── Sub-intent marker groups ──────────────────────────────────────
# Each tuple: (intent_label, marker_patterns)
# marker_patterns are checked against the normalized query text.
_INTENT_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("time_date", (
        "ne zaman", "hangi tarihte", "tarih", "takvim", "son gun",
        "son tarih", "donem tarihi", "sinav tarihi", "baslangic",
        "bitis", "sure", "deadline",
    )),
    ("eligibility", (
        "kimler katil", "kimler basvur", "kimler alinir", "kimler yapabilir",
        "kimler girebilir", "hangi ogrenci", "hangi bolum", "sinav hakki",
        "hakki var mi", "uygun mu", "kosul", "sart", "on kosul",
        "on sart", "eligib", "girebilir", "alabilir",
    )),
    ("application_process", (
        "nasil basvur", "basvuru nasil", "basvuru yapilir", "nasil yapilir",
        "basvuru adim", "basvuru sureci", "nereden basvur", "basvuru yeri",
        "basvuru sekli", "nasil kaydol",
    )),
    ("fee_cost", (
        "ucret", "ne kadar", "kac tl", "kac para", "ucretli mi",
        "ucretsiz mi", "odeme", "katki payi", "harc", "fiyat",
        "taksit", "odeyebilir",
    )),
    ("required_documents", (
        "hangi belge", "gerekli belge", "belgeler", "evrak",
        "form", "dilekce", "dekont", "basvuru belge",
    )),
    ("conditions_requirements", (
        "sartlar", "kosullar", "gerekli mi", "zorunlu mu",
        "kac akts", "gano", "not ortalamasi", "sinir",
        "esik", "minimum", "azami", "maximum",
    )),
    ("location", (
        "hangi derslik", "hangi sinif", "nere", "nerede",
        "hangis", "derslik", "sinif", "bina", "kampus",
    )),
)


def _detect_sub_intents(query: str) -> list[str]:
    """Return list of sub-intent labels detected in the query."""
    normalized = normalize_text(query)
    detected: list[str] = []
    for label, markers in _INTENT_GROUPS:
        if any(marker in normalized for marker in markers):
            detected.append(label)
    return detected


def _evidence_covers_intent(
    evidence_texts: list[str],
    intent_label: str,
) -> bool:
    """Check if any evidence text contains markers for the given intent."""
    markers_for_intent = dict(_INTENT_GROUPS).get(intent_label, ())
    if not markers_for_intent:
        return False
    for text in evidence_texts:
        normalized_ev = normalize_text(text)
        if any(marker in normalized_ev for marker in markers_for_intent):
            return True
    return False


@dataclass(frozen=True)
class IntentCoverageResult:
    """Result of intent coverage analysis."""

    sub_intents: list[str]
    covered_intents: list[str]
    missing_intents: list[str]
    coverage_ratio: float  # 0.0 – 1.0
    is_low: bool  # True when coverage < 0.5 and >=2 sub-intents


def compute_intent_coverage(
    query: str,
    evidence_texts: list[str],
    *,
    low_threshold: float = 0.5,
) -> IntentCoverageResult:
    """Compute how well the evidence set covers the query's sub-intents.

    Returns an IntentCoverageResult with detected sub-intents, which are
    covered/missing, and whether coverage is too low.
    """
    sub_intents = _detect_sub_intents(query)

    # Single-intent or no-intent queries: coverage is always sufficient
    if len(sub_intents) <= 1:
        return IntentCoverageResult(
            sub_intents=sub_intents,
            covered_intents=sub_intents,
            missing_intents=[],
            coverage_ratio=1.0 if sub_intents else 1.0,
            is_low=False,
        )

    covered: list[str] = []
    missing: list[str] = []
    for intent in sub_intents:
        if _evidence_covers_intent(evidence_texts, intent):
            covered.append(intent)
        else:
            missing.append(intent)

    ratio = len(covered) / len(sub_intents) if sub_intents else 1.0
    return IntentCoverageResult(
        sub_intents=sub_intents,
        covered_intents=covered,
        missing_intents=missing,
        coverage_ratio=ratio,
        is_low=ratio < low_threshold and len(sub_intents) >= 2,
    )


def should_widen_retrieval(
    query: str,
    evidence_texts: list[str],
) -> bool:
    """Quick check: should retrieval be widened before answer generation?

    True when the query has multiple sub-intents and evidence covers
    less than half of them.
    """
    result = compute_intent_coverage(query, evidence_texts)
    return result.is_low
