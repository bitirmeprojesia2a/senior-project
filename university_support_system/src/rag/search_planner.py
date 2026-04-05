"""Retriever planlama ve kaynak uyumlulugu yardimcilari."""

from typing import Any, Dict, List, Optional

import structlog

from src.core.constants import (
    Department,
    collection_name_for_department,
    get_department_config,
    normalize_department_value,
)

logger = structlog.get_logger()


OFF_TOPIC_PENALTY = 0.75


def _turkish_lower(text: str) -> str:
    """Python'un Turkish I davranisi icin daha guvenli lowercase."""
    return text.replace("İ", "i").replace("I", "ı").lower()


_TOPIC_SOURCE_PATTERNS: Dict[str, List[str]] = {
    "çap": ["cift_anadal", "çift ana dal", "çap"],
    "çift anadal": ["cift_anadal", "çift ana dal", "çap"],
    "çift ana dal": ["cift_anadal", "çift ana dal", "çap"],
    "ikinci lisans": ["cift_anadal", "çift ana dal", "çap"],
    "yan dal": ["cift_anadal", "yan dal", "yandal"],
    "yandal": ["cift_anadal", "yan dal", "yandal"],
    "ydp": ["cift_anadal", "yan dal", "yandal"],
    "yatay geçiş": ["yatay_gecis", "yatay geçiş"],
    "dikey geçiş": ["dikey_gecis", "dikey geçiş"],
    "staj": ["staj", "intörn"],
    "yaz okulu": ["yaz_okulu", "yaz okulu"],
    "erasmus": ["erasmus", "değişim", "uluslararası"],
    "mevlana": ["mevlana", "değişim"],
    "farabi": ["farabi", "değişim"],
    "muafiyet": ["muafiyet"],
    "disiplin": ["disiplin"],
}

_TOPIC_KEYS_BY_LENGTH = sorted(_TOPIC_SOURCE_PATTERNS.keys(), key=len, reverse=True)

_DEPARTMENT_KEYWORDS: Dict[Department, List[str]] = {
    department: list(get_department_config(department).keywords)
    for department in Department
}

_FINANCE_INTERNATIONAL_QUERY_MARKERS = (
    "uluslararasi",
    "uluslararası",
    "international",
    "yabanci",
    "yabancı",
    "foreign",
    "erasmus",
    "exchange",
)
_FINANCE_INTERNATIONAL_SOURCE_MARKERS = (
    "uluslararasi",
    "uluslararası",
    "international",
    "foreign",
    "yabanci",
    "yabancı",
)
_FINANCE_FEE_QUERY_MARKERS = (
    "ucret",
    "ücret",
    "harc",
    "harç",
    "odeme",
    "ödeme",
    "taksit",
    "kayit yenileme",
    "kayıt yenileme",
    "dekont",
)


def _detect_query_topic(query: str) -> Optional[str]:
    """Sorgudaki ana konu anahtar kelimesini tespit eder."""
    lowered_query = query.lower()
    for topic in _TOPIC_KEYS_BY_LENGTH:
        if topic in lowered_query:
            return topic
    return None


def _score_departments(query: str) -> Dict[Department, int]:
    """Sorgu icin departman bazli anahtar kelime skoru uretir."""
    lowered_query = _turkish_lower(query)
    scores: Dict[Department, int] = {}
    for department, keywords in _DEPARTMENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if _turkish_lower(keyword) in lowered_query)
        scores[department] = score
    return scores


def _plan_search_departments(
    query: str,
    explicit_department: Department | str | None = None,
) -> tuple[List[Department], List[Department]]:
    """Sorgu icin birincil ve fallback departman planini belirler."""
    if explicit_department is not None:
        normalized = (
            explicit_department
            if isinstance(explicit_department, Department)
            else normalize_department_value(explicit_department)
        )
        department = normalized if isinstance(normalized, Department) else Department(normalized)
        return [department], []

    scores = _score_departments(query)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_department, top_score = ranked[0]
    second_department, second_score = ranked[1]

    if top_score == 0:
        return [department for department, _ in ranked], []

    if second_score > 0 and second_score >= top_score - 1:
        primary = [top_department, second_department]
        fallback = [department for department, score in ranked[2:] if score > 0]
        return primary, fallback

    fallback = [second_department] if second_score > 0 else []
    return [top_department], fallback


def _apply_source_relevance(
    results: List[Dict[str, Any]],
    query: str,
    penalty: float = OFF_TOPIC_PENALTY,
) -> List[Dict[str, Any]]:
    """Konu-kaynak uyumsuzlugu olan sonuclara penalty uygular."""
    topic = _detect_query_topic(query)
    if not topic:
        return results

    expected = _TOPIC_SOURCE_PATTERNS.get(topic, [])
    if not expected:
        return results

    adjusted = False
    for result in results:
        source = _turkish_lower(result["source"])
        on_topic = any(pattern in source for pattern in expected)
        if not on_topic:
            result["score"] = round(result["score"] * penalty, 4)
            adjusted = True

    if adjusted:
        results.sort(key=lambda candidate: candidate["score"], reverse=True)
        logger.debug(
            "source_relevance_applied",
            topic=topic,
            adjusted_scores=[(result["source"], result["score"]) for result in results[:5]],
        )

    return results


def _apply_finance_source_penalty(
    results: List[Dict[str, Any]],
    query: str,
    collection_name: str,
) -> List[Dict[str, Any]]:
    """Genel finance sorgularinda uluslararasi ucret kaynaklarini geriye iter."""
    if collection_name != collection_name_for_department(Department.FINANCE):
        return results

    lowered_query = _turkish_lower(query)
    if any(marker in lowered_query for marker in _FINANCE_INTERNATIONAL_QUERY_MARKERS):
        return results
    if not any(marker in lowered_query for marker in _FINANCE_FEE_QUERY_MARKERS):
        return results

    adjusted = False
    for item in results:
        source = _turkish_lower(item.get("source", ""))
        content = _turkish_lower(item.get("content", "")[:400])
        if any(marker in source or marker in content for marker in _FINANCE_INTERNATIONAL_SOURCE_MARKERS):
            item["score"] = round(float(item.get("score", 0.0)) * 0.45, 4)
            adjusted = True

    if adjusted:
        results.sort(key=lambda item: item.get("score", 0.0), reverse=True)
        logger.debug(
            "finance_source_penalty_applied",
            query=query,
            top_sources=[(result.get("source", ""), result.get("score", 0.0)) for result in results[:5]],
        )

    return results
