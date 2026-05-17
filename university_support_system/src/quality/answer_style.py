"""Shared final-answer style helpers."""

from __future__ import annotations

import re
from typing import Any

from src.core.profiling import get_current_profiler


_LENGTH_EXEMPT_MARKERS = (
    "ders program",
    "haftalik program",
    "haftalık program",
    "akademik takvim",
    "sinav takvimi",
    "sınav takvimi",
    "gunler",
    "günler",
    "guncel duyur",
    "güncel duyur",
    "duyurular",
    "hangi dersler",
    "acilan ders",
    "açılan ders",
    "transkript",
    "belgeyi incele",
    "derslerimi",
    "geçtiğim",
    "gectigim",
    "kaldığım",
    "kaldigim",
)

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.MULTILINE)
_NORMAL_SENTENCE_WARNING_THRESHOLD = 6
_NORMAL_BULLET_WARNING_THRESHOLD = 5
_NORMAL_CHAR_WARNING_THRESHOLD = 1200


def is_length_exempt_query(query: str) -> bool:
    """Return true for naturally long list/calendar/transcript answers."""
    lowered = (query or "").casefold()
    return any(marker in lowered for marker in _LENGTH_EXEMPT_MARKERS)


def build_answer_length_instruction(query: str) -> str:
    """Return a prompt-level length instruction for the current query."""
    if is_length_exempt_query(query):
        return (
            "- Cevap uzunlugu: Bu soru liste, takvim, ders programi, duyuru veya transkript gibi "
            "dogal olarak uzun olabilir. Gerekli satirlari kesme; sadece ilgisiz kaynak metnini ve "
            "tekrarlari tasima."
        )
    return (
        "- Cevap uzunlugu: Tekil sorularda 1-3 cumle, normal cevaplarda en fazla 4 cumle kullan. "
        "Madde gerekiyorsa en fazla 3 kisa madde kullan; kritik resmi kosul, tarih, tutar ve sayilari kesme."
    )


def _count_sentences(answer: str) -> int:
    """Return a lightweight sentence estimate without changing the answer."""
    text = " ".join((answer or "").split())
    if not text:
        return 0
    parts = [part.strip() for part in _SENTENCE_RE.split(text) if part.strip()]
    return max(1, len(parts))


def analyze_answer_length(query: str, answer: str) -> dict[str, Any]:
    """Return soft answer length telemetry.

    This deliberately does not enforce or truncate. It only marks likely
    overlong normal answers so replay/diagnostics can tell us where token
    pressure is coming from.
    """
    answer_text = answer or ""
    exempt = is_length_exempt_query(query)
    sentence_count = _count_sentences(answer_text)
    bullet_count = len(_BULLET_RE.findall(answer_text))
    char_count = len(answer_text)

    warnings: list[str] = []
    if not exempt:
        if sentence_count > _NORMAL_SENTENCE_WARNING_THRESHOLD:
            warnings.append("normal_answer_sentence_count_high")
        if bullet_count > _NORMAL_BULLET_WARNING_THRESHOLD:
            warnings.append("normal_answer_bullet_count_high")
        if char_count > _NORMAL_CHAR_WARNING_THRESHOLD:
            warnings.append("normal_answer_char_count_high")

    return {
        "schema": "omu.answer_length.v1",
        "policy": "exempt" if exempt else "normal",
        "char_count": char_count,
        "sentence_count": sentence_count,
        "bullet_count": bullet_count,
        "warning": bool(warnings),
        "warnings": warnings,
    }


def record_answer_length_telemetry(*, answer: str, query: str | None = None) -> dict[str, Any]:
    """Attach answer length telemetry to the active profiler and return it."""
    profiler = get_current_profiler()
    effective_query = query
    if effective_query is None and profiler is not None:
        effective_query = str(profiler.get_attribute("query", "") or "")
    telemetry = analyze_answer_length(effective_query or "", answer)
    if profiler is not None:
        profiler.set_attribute("answer_length", telemetry)
    return telemetry
