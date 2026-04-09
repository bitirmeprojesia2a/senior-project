"""Retriever planning and source-relevance helpers."""

from typing import Any, Dict, List, Optional

import structlog

from src.core.constants import (
    Department,
    collection_name_for_department,
    get_department_config,
    normalize_department_value,
)
from src.core.text_normalization import normalize_text

logger = structlog.get_logger()


OFF_TOPIC_PENALTY = 0.75


def _turkish_lower(text: str) -> str:
    """Normalize Turkish text into a lowercase ASCII-like representation."""
    return normalize_text(text)


_TOPIC_SOURCE_PATTERNS: Dict[str, List[str]] = {
    "çap": ["cift_anadal", "cift anadal", "cift ana dal", "cap"],
    "çift anadal": ["cift_anadal", "cift anadal", "cift ana dal", "cap"],
    "çift ana dal": ["cift_anadal", "cift anadal", "cift ana dal", "cap"],
    "ikinci lisans": ["cift_anadal", "cift anadal", "cift ana dal", "cap"],
    "yan dal": ["cift_anadal", "yan dal", "yandal"],
    "yandal": ["cift_anadal", "yan dal", "yandal"],
    "ydp": ["cift_anadal", "yan dal", "yandal"],
    "yatay geçiş": ["yatay_gecis", "yatay gecis", "yatay"],
    "dikey geçiş": ["dikey_gecis", "dikey gecis", "dikey"],
    "staj": ["staj", "intorn", "mesleki_uygulama"],
    "bitirme projesi": ["staj", "bitirme", "proje"],
    "yaz okulu": ["yaz_okulu", "yaz okulu"],
    "erasmus": ["erasmus", "degisim", "uluslararasi"],
    "mevlana": ["mevlana", "degisim"],
    "farabi": ["farabi", "degisim"],
    "muafiyet": ["muafiyet", "intibak"],
    "disiplin": ["disiplin"],
    "denklik": ["denklik", "uluslararasi", "yabanci"],
    "ikamet": ["ikamet", "uluslararasi", "goc"],
    "tomer": ["tomer", "uluslararasi", "turkce"],
    "yos": ["yos", "uluslararasi", "yabanci"],
    "transkript": ["sik_sorulan_sorular", "transkript", "ogrenci_isleri", "diploma"],
    "öğrenci belgesi": ["sik_sorulan_sorular", "ogrenci_belgesi", "ogrenci_isleri", "belge"],
    "burs": ["sik_sorulan_sorular", "burs", "scholarship", "idari_ve_mali", "ogrenci_isleri", "yemek_bursu"],
    "kayit dondurma": ["kayit", "dondurma", "donem_izni", "ogrenci_isleri"],
    "mezuniyet": ["mezuniyet", "diploma", "ogrenci_isleri"],
    "azami sure": ["azami", "ogrenim_suresi", "yon_lisans"],
    "devam zorunlulugu": ["devam", "yoklama", "yonetmelik"],
}

_TOPIC_KEYS_BY_LENGTH = sorted(_TOPIC_SOURCE_PATTERNS.keys(), key=len, reverse=True)

_DEPARTMENT_KEYWORDS: Dict[Department, List[str]] = {
    department: list(get_department_config(department).keywords)
    for department in Department
}

_FINANCE_INTERNATIONAL_QUERY_MARKERS = (
    "uluslararasi",
    "international",
    "yabanci",
    "foreign",
    "erasmus",
    "exchange",
    "mevlana",
    "farabi",
    "degisim",
)
_FINANCE_INTERNATIONAL_SOURCE_MARKERS = (
    "uluslararasi",
    "international",
    "foreign",
    "yabanci",
    "erasmus",
    "degisim",
)
_FINANCE_FEE_QUERY_MARKERS = (
    "ucret",
    "harc",
    "odeme",
    "taksit",
    "kayit yenileme",
    "dekont",
    "katki payi",
    "ogrenim ucreti",
    "borc",
    "tahsilat",
)
_STUDENT_DOCUMENT_QUERY_MARKERS = (
    "transkript",
    "ogrenci belgesi",
    "diploma eki",
    "transkript belgesi",
    "not dokumu",
    "kayit belgesi",
    "ogrenci durum belgesi",
    "tecil belgesi",
    "askerlik belgesi",
)
_STUDENT_DOCUMENT_REQUEST_MARKERS = (
    "belge nasil al",
    "belgemi nasil al",
    "belgeyi nasil al",
    "nereden alabilirim",
    "belge almak istiyorum",
    "belge basvurusu",
)
_STUDENT_AFFAIRS_FAQ_SOURCE_PATTERNS = (
    "sik_sorulan_sorular",
    "ogrenci_isleri_birimi",
    "ogrenci_isleri",
)
_FINANCE_BURS_SOURCE_PATTERNS = (
    "burs",
    "scholarship",
    "idari_ve_mali",
    "mali_isler",
    "yemek_bursu",
    "kismi_zamanli",
)
_INTERNATIONAL_BURS_SOURCE_PATTERNS = (
    "erasmus",
    "uluslararasi",
    "degisim",
    "exchange",
    "mevlana",
    "farabi",
)


def _candidate_targets_department(
    item: Dict[str, Any],
    department: Department,
    collection_name: str,
) -> bool:
    """Return whether a candidate belongs to the target department in single or multi-collection mode."""
    target_collection = collection_name_for_department(department)
    if collection_name == target_collection:
        return True

    metadata = item.get("metadata") or {}
    candidate_department = metadata.get("department")
    if not candidate_department:
        return False

    normalized = normalize_department_value(str(candidate_department))
    if isinstance(normalized, Department):
        return normalized == department
    return False


def _looks_like_student_document_query(normalized_query: str) -> bool:
    """Return whether the query is about transcript/student document retrieval."""
    if any(marker in normalized_query for marker in _STUDENT_DOCUMENT_QUERY_MARKERS):
        return True
    return (
        "belge" in normalized_query
        and any(marker in normalized_query for marker in ("ogrenci", "transkript", "diploma"))
    )


def _detect_query_topic(query: str) -> Optional[str]:
    """Detect the primary topic marker inside the query."""
    normalized_query = normalize_text(query)
    for topic in _TOPIC_KEYS_BY_LENGTH:
        if normalize_text(topic) in normalized_query:
            return topic
    return None


def _score_departments(query: str) -> Dict[Department, int]:
    """Compute keyword scores per department for a query."""
    normalized_query = normalize_text(query)
    scores: Dict[Department, int] = {}
    for department, keywords in _DEPARTMENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if normalize_text(keyword) in normalized_query)
        scores[department] = score
    return scores


def _plan_search_departments(
    query: str,
    explicit_department: Department | str | None = None,
) -> tuple[List[Department], List[Department]]:
    """Decide primary and fallback department collections for the query."""
    if explicit_department is not None:
        normalized = (
            explicit_department
            if isinstance(explicit_department, Department)
            else normalize_department_value(explicit_department)
        )
        department = normalized if isinstance(normalized, Department) else Department(normalized)
        return [department], []

    normalized_query = normalize_text(query)
    if _looks_like_student_document_query(normalized_query):
        return [Department.STUDENT_AFFAIRS], [Department.FINANCE]

    if "burs" in normalized_query:
        if any(marker in normalized_query for marker in _FINANCE_INTERNATIONAL_QUERY_MARKERS):
            return [Department.ACADEMIC_PROGRAMS, Department.FINANCE], [Department.STUDENT_AFFAIRS]
        if any(marker in normalized_query for marker in ("basvuru", "ne zaman", "tarih", "son tarih", "surec")):
            return [Department.FINANCE, Department.STUDENT_AFFAIRS], []
        return [Department.FINANCE], [Department.STUDENT_AFFAIRS]

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
    """Apply a penalty to results whose source looks off-topic for the query."""
    topic = _detect_query_topic(query)
    if not topic:
        return results

    expected = _TOPIC_SOURCE_PATTERNS.get(topic, [])
    if not expected:
        return results

    adjusted = False
    for result in results:
        source = normalize_text(result.get("source", ""))
        on_topic = any(pattern in source for pattern in expected)
        if not on_topic:
            result["score"] = round(result["score"] * penalty, 4)
            adjusted = True

    if adjusted:
        results.sort(key=lambda candidate: candidate["score"], reverse=True)
        logger.debug(
            "source_relevance_applied",
            topic=topic,
            adjusted_scores=[(result.get("source", ""), result["score"]) for result in results[:5]],
        )

    return results


def _apply_finance_source_penalty(
    results: List[Dict[str, Any]],
    query: str,
    collection_name: str,
) -> List[Dict[str, Any]]:
    """Push international-fee sources down for general finance fee queries."""
    finance_collection = collection_name_for_department(Department.FINANCE)
    if collection_name != finance_collection and collection_name != "__multi__":
        return results

    normalized_query = normalize_text(query)
    if any(marker in normalized_query for marker in _FINANCE_INTERNATIONAL_QUERY_MARKERS):
        return results
    if not any(marker in normalized_query for marker in _FINANCE_FEE_QUERY_MARKERS):
        return results

    adjusted = False
    for item in results:
        if not _candidate_targets_department(item, Department.FINANCE, collection_name):
            continue
        source = normalize_text(item.get("source", ""))
        content = normalize_text(item.get("content", "")[:400])
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


def _apply_student_affairs_faq_bias(
    results: List[Dict[str, Any]],
    query: str,
    collection_name: str,
) -> List[Dict[str, Any]]:
    """Boost Student Affairs FAQ-like sources for transcript/document/burs questions."""
    normalized_query = normalize_text(query)
    student_document_query = _looks_like_student_document_query(normalized_query)
    burs_query = "burs" in normalized_query
    document_request_query = any(marker in normalized_query for marker in _STUDENT_DOCUMENT_REQUEST_MARKERS)

    if not student_document_query and not burs_query and not document_request_query:
        return results

    adjusted = False
    for item in results:
        item_adjusted = False
        is_student_affairs_candidate = _candidate_targets_department(
            item,
            Department.STUDENT_AFFAIRS,
            collection_name,
        )
        metadata = item.get("metadata") or {}
        source_text = " ".join(
            normalize_text(str(value or ""))
            for value in (
                metadata.get("file_name"),
                metadata.get("source"),
                metadata.get("title"),
                item.get("source"),
            )
        )
        content_text = normalize_text(str(item.get("content") or "")[:500])
        score = float(item.get("score", 0.0))
        boost = 0.0

        if student_document_query or document_request_query:
            if any(pattern in source_text for pattern in _STUDENT_AFFAIRS_FAQ_SOURCE_PATTERNS):
                boost = max(boost, 0.2)
            elif is_student_affairs_candidate:
                score *= 0.7
                item_adjusted = True

        if burs_query:
            if any(pattern in source_text for pattern in _STUDENT_AFFAIRS_FAQ_SOURCE_PATTERNS):
                boost = max(boost, 0.12)
            if any(pattern in source_text or pattern in content_text for pattern in _FINANCE_BURS_SOURCE_PATTERNS):
                boost = max(boost, 0.14)

            if not any(marker in normalized_query for marker in _FINANCE_INTERNATIONAL_QUERY_MARKERS):
                if any(pattern in source_text or pattern in content_text for pattern in _INTERNATIONAL_BURS_SOURCE_PATTERNS):
                    score *= 0.55
                    item_adjusted = True

        if boost > 0:
            score += boost
            item_adjusted = True

        if item_adjusted:
            adjusted = True
            item["score"] = round(score, 4)

    if adjusted:
        results.sort(key=lambda item: item.get("score", 0.0), reverse=True)
        logger.debug(
            "student_affairs_faq_bias_applied",
            query=query,
            top_sources=[(result.get("source", ""), result.get("score", 0.0)) for result in results[:5]],
        )

    return results
