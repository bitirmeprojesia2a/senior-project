"""Intent classification for uploaded document questions.

This module intentionally classifies *what kind* of document question was
asked before any answer path runs. It keeps field lookup from becoming the
default route for generic document questions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum
from typing import Any

from src.core.text_normalization import normalize_text


class DocumentQuestionIntent(str, Enum):
    DOCUMENT_SUMMARY = "document_summary"
    DOCUMENT_PROCEDURE = "document_procedure"
    DOCUMENT_FIELD_LOOKUP = "document_field_lookup"
    TRANSCRIPT_METRIC = "transcript_metric"
    INSTITUTIONAL_RAG = "institutional_rag"
    HYBRID_DOCUMENT_RAG = "hybrid_document_rag"
    CLARIFY = "clarify"


@dataclass(frozen=True)
class DocumentQuestionClassification:
    intent: DocumentQuestionIntent
    confidence: float
    reason: str
    field_confidence: float | None = None


_GRADE_QUERY_RE = re.compile(r"\b(AA|BA|BB|CB|CC|DC|DD|FD|FF|YT|YZ|G|K|P|F)\b", re.IGNORECASE)
_WORD_RE = re.compile(r"[a-z0-9]+")

_DOCUMENT_REFERENCE_MARKERS = (
    "belgeye gore",
    "belgede",
    "belgedeki",
    "belgenin",
    "belge ne",
    "bu belge",
    "bu belgede",
    "yukledigim belge",
    "yuklenen belge",
    "dosyaya gore",
    "transkripte gore",
    "transkriptime gore",
    "bu transkript",
    "inceleyip",
)

_TRANSCRIPT_METRIC_MARKERS = (
    "akts",
    "kredi",
    "gno",
    "agno",
    "gano",
    "ortalama",
    "not dagilimi",
    "harf notu",
    "basarisiz",
    "basarili",
    "kaldigim",
    "gectigim",
    "aldigim",
    "aldigi",
    "aldiklarim",
    "aldiklari",
    "almis",
    "almisim",
    "aldim",
    "dersim",
    "derslerim",
    "notum",
    "notlarim",
)

_COUNT_OR_LIST_MARKERS = (
    "kac",
    "kac tane",
    "sayisi",
    "say",
    "hangi",
    "hangileri",
    "neler",
    "liste",
    "listele",
    "digerleri",
    "bos",
)

_GRADUATION_PROGRESS_MARKERS = (
    "mezun",
    "mezuniyet",
    "kac kaldi",
    "tamamlamam",
)

_INSTITUTIONAL_MARKERS = (
    "harc",
    "borc",
    "ders kaydi",
    "kayit yenileme",
    "cap",
    "capa",
    "cift anadal",
    "yandal",
    "duyuru",
    "takvim",
    "basvuru tarih",
    "iletisim",
    "santral",
    "yonetmelik",
    "mezun",
    "mezuniyet",
    "lisans",
    "onlisans",
    "akts",
    "tek ders",
    "kaldim",
    "yaz okulu",
    "staj tarih",
    "staj ne zaman",
    "sinav",
    "butunleme",
    "ubys",
    "obs",
    "ogrenci bilgi sistemi",
    "yatay gecis",
    "erasmus",
)

_SUMMARY_MARKERS = (
    "ozet",
    "ozetle",
    "yorumla",
    "yorumlar misin",
    "incele",
    "ne diyor",
    "neler var",
    "hangi alanlar",
    "alanlar var",
    "alanlari",
    "ne hakkinda",
    "bu belge ne",
    "belge ne",
    "nedir bu",
    "bu nedir",
    "ne ise yariyor",
    "ise yariyor",
    "neye yarar",
    "ne icin",
    "amaci",
    "amac",
)

_PROCEDURE_MARKERS = (
    "teslim",
    "nereye",
    "nereden",
    "basvur",
    "basvuru",
    "doldur",
    "imza",
    "imzalat",
    "onay",
    "sonra ne",
    "ne yap",
    "nasil",
    "yeterli mi",
)

_FIELD_QUESTION_MARKERS = (
    "ne olarak geciyor",
    "ne yaziyor",
    "neymis",
    "nedir",
    "hangi",
    "yaziyor",
    "geciyor",
)

_FIELD_STOP_WORDS = {
    "bu",
    "belge",
    "belgede",
    "belgedeki",
    "belgenin",
    "ne",
    "nedir",
    "neymis",
    "hangi",
    "olarak",
    "geciyor",
    "yaziyor",
    "var",
    "mi",
}

_FIELD_LABEL_ALIASES = (
    ("tc kimlik no", ("tc kimlik", "tc kimlik no", "kimlik no", "tc kimlik numarasi", "t c kimlik no", "t c kimlik numarasi")),
    ("adi soyadi", ("adi soyadi", "adi ve soyadi", "ad soyad", "ad soyadi", "kisinin adi", "adi kisinin")),
    ("e posta adresi", ("e posta", "eposta", "e posta adresi", "eposta adresi", "email", "e mail")),
    ("telefon no", ("telefon", "telefon no", "telefon numarasi")),
)

_AMBIGUOUS_SHORT_FOLLOWUP_TOKENS = {
    "peki",
    "kac",
    "kacti",
    "hangileri",
    "neler",
    "listele",
}

_DOCUMENT_CONTINUATION_MARKERS = (
    "biraz daha",
    "daha detayli",
    "detayli acikla",
    "detaylandir",
    "aciklar misin",
    "ayrintili",
    "devam et",
)

_PERSONAL_DOCUMENT_FIELD_MARKERS = (
    "anne",
    "baba",
    "kimlik",
    "tc",
    "dogum",
    "dogr",
    "adres",
    "telefon",
    "eposta",
    "mail",
)

_FIELD_REPAIR_MARKERS = (
    "var ya",
    "var iste",
    "belgede var",
    "orada var",
    "yaziyor ya",
    "gosteriyor",
)


def classify_document_question(
    *,
    query: str,
    document: Any,
    last_query: str | None = None,
) -> DocumentQuestionClassification:
    normalized = normalize_text(query)
    if not normalized:
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.CLARIFY,
            confidence=0.7,
            reason="empty_query_with_active_document",
        )

    document_type = str(getattr(document, "document_type", "") or "")
    has_document_reference = _has_document_reference(normalized)

    if _is_short_institutional_followup(normalized, last_query):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.INSTITUTIONAL_RAG,
            confidence=0.78,
            reason="short_followup_after_institutional_query",
        )

    if document_type == "schedule_document":
        if _looks_like_schedule_detail_question(normalized):
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.HYBRID_DOCUMENT_RAG,
                confidence=0.84,
                reason="schedule_document_detail_question",
            )
        if _is_summary_question(normalized) or has_document_reference:
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.DOCUMENT_SUMMARY,
                confidence=0.86,
                reason="schedule_document_summary_question",
            )
        if _is_short_vague_followup(normalized, last_query):
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.HYBRID_DOCUMENT_RAG,
                confidence=0.72,
                reason="schedule_document_short_followup",
            )

    if document_type == "transcript":
        if _has_grade_query(query, normalized) and (_has_count_or_list(normalized) or _has_transcript_metric(normalized)):
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.TRANSCRIPT_METRIC,
                confidence=0.93,
                reason="transcript_grade_metric",
            )
        if _has_transcript_metric(normalized):
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.TRANSCRIPT_METRIC,
                confidence=0.9,
                reason="transcript_metric_marker",
            )
        if _has_graduation_progress(normalized) and _has_count_or_list(normalized):
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.TRANSCRIPT_METRIC,
                confidence=0.82,
                reason="graduation_progress_with_active_transcript",
            )
        if _is_institutional_query(normalized) and not has_document_reference:
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.INSTITUTIONAL_RAG,
                confidence=0.86,
                reason="institutional_marker_without_document_reference",
            )
        if has_document_reference or _is_summary_question(normalized):
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.DOCUMENT_SUMMARY,
                confidence=0.82,
                reason="transcript_document_summary_question",
            )
        if _is_short_vague_followup(normalized, last_query):
            return DocumentQuestionClassification(
                intent=DocumentQuestionIntent.TRANSCRIPT_METRIC,
                confidence=0.75,
                reason="short_followup_after_document_query",
            )
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.CLARIFY,
            confidence=0.58,
            reason="ambiguous_active_document_query",
        )

    if _is_field_repair_followup(normalized, last_query):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP,
            confidence=0.78,
            reason="field_lookup_repair_followup",
        )

    if _is_field_inventory_followup(normalized, last_query):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_SUMMARY,
            confidence=0.78,
            reason="field_inventory_followup",
        )

    field_confidence = document_field_match_confidence(document=document, normalized_query=normalized)
    if field_confidence >= 0.72:
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP,
            confidence=0.9,
            reason="generic_document_field_inventory_match",
            field_confidence=field_confidence,
        )

    if _is_institutional_query(normalized) and not has_document_reference:
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.INSTITUTIONAL_RAG,
            confidence=0.86,
            reason="institutional_marker_without_document_reference",
        )

    if _looks_like_personal_document_field_query(normalized):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP,
            confidence=0.74,
            reason="generic_document_personal_field_shape",
            field_confidence=field_confidence,
        )

    if _is_hybrid_question(normalized, document=document):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.HYBRID_DOCUMENT_RAG,
            confidence=0.82,
            reason="generic_document_hybrid_procedure",
        )

    if _is_summary_question(normalized) or has_document_reference:
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_SUMMARY,
            confidence=0.84,
            reason="generic_document_summary_question",
        )

    if _is_procedure_question(normalized):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_PROCEDURE,
            confidence=0.76,
            reason="generic_document_procedure_question",
        )

    if _looks_like_field_lookup(normalized):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP,
            confidence=0.68,
            reason="generic_document_field_lookup_shape",
            field_confidence=field_confidence,
        )

    if _is_short_vague_followup(normalized, last_query):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_SUMMARY,
            confidence=0.7,
            reason="short_followup_after_document_query",
        )

    if _is_document_continuation_question(normalized, last_query):
        return DocumentQuestionClassification(
            intent=DocumentQuestionIntent.DOCUMENT_SUMMARY,
            confidence=0.76,
            reason="document_continuation_followup",
        )

    return DocumentQuestionClassification(
        intent=DocumentQuestionIntent.INSTITUTIONAL_RAG,
        confidence=0.78,
        reason="generic_document_no_document_reference",
    )


def document_field_match_confidence(*, document: Any, normalized_query: str) -> float:
    facts = getattr(document, "facts", None)
    fields = tuple(getattr(facts, "fields", ()) or getattr(document, "fields", ()) or ())
    if not fields:
        return 0.0
    query_words = [word for word in _WORD_RE.findall(normalized_query) if word not in _FIELD_STOP_WORDS]
    query_tokens = set(query_words)
    query_label = " ".join(query_words)
    best = 0.0
    for field in fields:
        key = str(getattr(field, "key", "") or "")
        field_tokens = set(_WORD_RE.findall(key))
        if not field_tokens:
            continue
        if key and key in normalized_query:
            best = max(best, 0.7 if len(field_tokens) == 1 and len(query_tokens) > 1 else 1.0)
            continue
        overlap = len(query_tokens & field_tokens)
        if overlap == 0:
            score = _field_fuzzy_score(key, query_label)
            if score < 0.72:
                continue
        else:
            score = max(
                _field_fuzzy_score(key, query_label),
                overlap / max(min(len(field_tokens), max(len(query_tokens), 1)), 1),
            )
        if len(field_tokens) == 1 and overlap == 1:
            score = max(score, 0.86)
        best = max(best, score)
    return best


def _field_fuzzy_score(field_key: str, query_label: str) -> float:
    if not query_label:
        return 0.0
    candidates = [field_key]
    for canonical, aliases in _FIELD_LABEL_ALIASES:
        if field_key == canonical:
            candidates.extend(aliases)
            for alias in aliases:
                if alias and alias in query_label:
                    return 0.96
    return max(SequenceMatcher(None, candidate, query_label).ratio() for candidate in candidates)


def _has_document_reference(normalized: str) -> bool:
    return any(marker in normalized for marker in _DOCUMENT_REFERENCE_MARKERS)


def _has_grade_query(raw_query: str, normalized: str) -> bool:
    if _GRADE_QUERY_RE.search(raw_query):
        return True
    tokens = set(_WORD_RE.findall(normalized))
    return bool(tokens & {"aa", "ba", "bb", "cb", "cc", "dc", "dd", "fd", "ff", "yt", "yz"})


def _has_transcript_metric(normalized: str) -> bool:
    return any(marker in normalized for marker in _TRANSCRIPT_METRIC_MARKERS)


def _has_count_or_list(normalized: str) -> bool:
    return any(marker in normalized for marker in _COUNT_OR_LIST_MARKERS)


def _has_graduation_progress(normalized: str) -> bool:
    return any(marker in normalized for marker in _GRADUATION_PROGRESS_MARKERS)


def _is_institutional_query(normalized: str) -> bool:
    return any(marker in normalized for marker in _INSTITUTIONAL_MARKERS)


def _is_summary_question(normalized: str) -> bool:
    return any(marker in normalized for marker in _SUMMARY_MARKERS)


def _is_procedure_question(normalized: str) -> bool:
    return any(marker in normalized for marker in _PROCEDURE_MARKERS)


def _is_hybrid_question(normalized: str, *, document: Any) -> bool:
    if not _is_procedure_question(normalized):
        if _document_topic_hint(document) == "schedule" and _looks_like_schedule_detail_question(normalized):
            return True
        return False
    doc_hint = _document_topic_hint(document)
    if any(marker in normalized for marker in ("nasil", "basvur", "sonra ne", "yeterli mi", "teslim")):
        return bool(doc_hint)
    return False


def _document_topic_hint(document: Any) -> str | None:
    haystack = normalize_text(f"{getattr(document, 'filename', '')}\n{getattr(document, 'text', '')[:1600]}")
    if "staj" in haystack:
        return "internship"
    if "ogrenci belgesi" in haystack or "ogrencilik" in haystack:
        return "student_status"
    if "transkript" in haystack or "not dokum" in haystack:
        return "transcript"
    if getattr(document, "document_type", "") == "schedule_document" or "ders program" in haystack:
        return "schedule"
    if "mufredat" in haystack or "ders icer" in haystack:
        return "curriculum"
    return None


def _looks_like_schedule_detail_question(normalized: str) -> bool:
    if not normalized:
        return False
    schedule_markers = (
        "ders",
        "dersi",
        "dersler",
        "program",
        "cuma",
        "sali",
        "pazartesi",
        "carsamba",
        "persembe",
        "sinif",
        "saat",
        "gunu",
        "hangi",
    )
    return any(marker in normalized for marker in schedule_markers)


def _looks_like_field_lookup(normalized: str) -> bool:
    if not normalized:
        return False
    if _is_summary_question(normalized) or _is_procedure_question(normalized):
        return False
    if any(marker in normalized for marker in _FIELD_QUESTION_MARKERS):
        return True
    return re.search(r"\bne\b", normalized) is not None


def _is_short_vague_followup(normalized: str, last_query: str | None) -> bool:
    if not last_query:
        return False
    tokens = set(_WORD_RE.findall(normalized))
    if len(tokens) > 5:
        return False
    return bool(tokens & _AMBIGUOUS_SHORT_FOLLOWUP_TOKENS)


def _is_document_continuation_question(normalized: str, last_query: str | None) -> bool:
    if not last_query:
        return False
    if _is_institutional_query(normalized):
        return False
    return any(marker in normalized for marker in _DOCUMENT_CONTINUATION_MARKERS)


def _is_field_inventory_followup(normalized: str, last_query: str | None) -> bool:
    if not last_query:
        return False
    last_normalized = normalize_text(last_query)
    if not _asks_field_inventory(last_normalized):
        return False
    return any(marker in normalized for marker in ("digerleri", "bos mu", "bosta", "boş mu", "degerleri", "degeri"))


def _asks_field_inventory(normalized: str) -> bool:
    return any(marker in normalized for marker in ("hangi alanlar", "alanlar var", "alanlari", "degerleri"))


def _is_short_institutional_followup(normalized: str, last_query: str | None) -> bool:
    if not last_query:
        return False
    tokens = set(_WORD_RE.findall(normalized))
    if len(tokens) > 4:
        return False
    if not (tokens & {"tarih", "tarihleri", "neler", "ne", "peki"}):
        return False
    return _is_institutional_query(normalize_text(last_query))


def _looks_like_personal_document_field_query(normalized: str) -> bool:
    if not normalized:
        return False
    if any(marker in normalized for marker in _PERSONAL_DOCUMENT_FIELD_MARKERS):
        if "tarih" in normalized or any(marker in normalized for marker in ("ne", "nedir", "neymis", "var mi", "sordum")):
            return True
    return False


def _is_field_repair_followup(normalized: str, last_query: str | None) -> bool:
    if not last_query:
        return False
    if not any(marker in normalized for marker in _FIELD_REPAIR_MARKERS):
        return False
    return _looks_like_field_lookup(normalize_text(last_query))
