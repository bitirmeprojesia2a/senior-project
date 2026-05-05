"""Retriever planning and source-relevance helpers."""

from typing import Any, Dict, List, Optional

import structlog

from src.core.config import settings
from src.core.constants import (
    ACADEMIC_SCHEDULE_QUERY_MARKERS,
    Department,
    collection_name_for_department,
    get_department_config,
    normalize_department_value,
)
from src.core.text_normalization import iter_alias_matches_longest_first, normalize_text

logger = structlog.get_logger()


OFF_TOPIC_PENALTY = 0.75
CAP_OFF_TOPIC_PENALTY = 0.55
_NO_SIGNAL_PRIMARY_DEPARTMENTS = [Department.STUDENT_AFFAIRS]
_NO_SIGNAL_FALLBACK_DEPARTMENTS = [Department.ACADEMIC_PROGRAMS, Department.FINANCE]
_CAP_PRIMARY_TOPICS = {
    normalize_text(topic)
    for topic in ("çap", "çift anadal", "çift ana dal", "ikinci lisans", "yan dal", "yandal", "ydp")
}


def _turkish_lower(text: str) -> str:
    """Normalize Turkish text into a lowercase ASCII-like representation."""
    return normalize_text(text)


_TOPIC_SOURCE_PATTERNS: Dict[str, List[str]] = {
    "çap": ["cift_anadal", "cift_ana_dal", "cift anadal", "cift ana dal", "cap"],
    "çift anadal": ["cift_anadal", "cift_ana_dal", "cift anadal", "cift ana dal", "cap"],
    "çift ana dal": ["cift_anadal", "cift_ana_dal", "cift anadal", "cift ana dal", "cap"],
    "ikinci lisans": ["cift_anadal", "cift_ana_dal", "cift anadal", "cift ana dal", "cap"],
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
    "intibak": ["muafiyet", "intibak"],
    "disiplin": ["disiplin", "kopya", "sinav_uygulama_kurallari", "ogrenci_isleri", "yonetmelik"],
    "kopya": ["disiplin", "kopya", "ogrenci_isleri", "yonetmelik", "on_lisans"],
    "denklik": ["denklik", "uluslararasi", "yabanci"],
    "ikamet": ["ikamet", "uluslararasi", "goc"],
    "notuma itiraz": ["ogrenci_isleri", "sik_sorulan", "yonetmelik", "on_lisans", "itiraz"],
    "itiraz": ["ogrenci_isleri", "sik_sorulan", "yonetmelik", "on_lisans", "itiraz"],
    "notlarimi sisteme": ["ogrenci_isleri", "sik_sorulan", "ogrenci_isleri_birimi", "oidb", "not", "duzeltme"],
    "not girmemis": ["ogrenci_isleri", "sik_sorulan", "ogrenci_isleri_birimi", "oidb", "not", "duzeltme"],
    "tomer": ["tomer", "uluslararasi", "turkce"],
    "yos": ["yos", "uluslararasi", "yabanci"],
    "transkript": ["sik_sorulan_sorular", "transkript", "ogrenci_isleri", "diploma"],
    "öğrenci belgesi": ["sik_sorulan_sorular", "ogrenci_belgesi", "ogrenci_isleri", "belge"],
    "burs": ["sik_sorulan_sorular", "burs", "scholarship", "idari_ve_mali", "ogrenci_isleri", "yemek_bursu"],
    "kayit dondurma": ["kayit", "dondurma", "donem_izni", "ogrenci_isleri"],
    "mezuniyet": ["mezuniyet", "diploma", "ogrenci_isleri", "ilisik_kesme", "kosul"],
    "azami sure": ["azami", "ogrenim_suresi", "yon_lisans"],
    "devam zorunlulugu": ["devam", "yoklama", "yonetmelik", "on_lisans"],
    "bagil degerlendirme": ["bagil_degerlendirme", "bagil degerlendirme", "yonerge_bagil_degerlendirme"],
    "mutlak degerlendirme": ["bagil_degerlendirme", "mutlak degerlendirme", "yonerge_bagil_degerlendirme"],
    "not sistemi": ["bagil_degerlendirme", "bagil degerlendirme", "yonerge_bagil_degerlendirme"],
    "ogrenci sayisi": ["bagil_degerlendirme", "bagil degerlendirme", "yonerge_bagil_degerlendirme"],
    "başarısız": ["sik_sorulan", "on_lisans", "lisans", "yonetmelik"],
    "seçmeli ders": ["on_lisans", "lisans", "mufredat", "sik_sorulan"],
    "ders programi": ["ders_programlari", "ders program", "program"],
    "ilisik kesme": ["ilisik_kesme", "kayit_sildirme", "ogrenci_isleri"],
    "ayrilmak": ["ilisik_kesme", "kayit_sildirme", "ogrenci_isleri"],
    "birakmak": ["ilisik_kesme", "kayit_sildirme", "ogrenci_isleri"],
}

_LISANSUSTU_INDICATORS = (
    "lisansustu", "yuksek lisans", "master", "doktora", "tez savunma",
)
_LISANSUSTU_SOURCE_MARKERS = (
    "lisansustu", "yuksek_lisans", "lisans_ustu", "lisansustu_",
)
_LISANS_SOURCE_MARKERS = (
    "on_lisans", "onlisans", "lisans_yon", "yon_lisans",
)

_TOPIC_KEYS_BY_LENGTH = sorted(_TOPIC_SOURCE_PATTERNS.keys(), key=len, reverse=True)
_ACADEMIC_TOPIC_STUDENT_AFFAIRS_SOURCE_FALLBACKS = {
    "bagil degerlendirme",
    "mutlak degerlendirme",
}

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
_EXAM_DISCIPLINE_QUERY_MARKERS = (
    "kopya",
    "sinavda kopya",
    "disiplin sureci",
    "disiplin cezasi",
)
_EXAM_DISCIPLINE_NEGATIVE_SOURCE_PATTERNS = (
    "staj",
    "isyeri",
    "mesleki_uygulama",
    "intorn",
)
_RELATION_CUTTING_QUERY_MARKERS = (
    "ilisik kesme",
    "kayit sildirme",
    "kaydi sil",
    "kaydimi sil",
    "universiteyi birak",
    "universiteden ayril",
    "ayrilmak",
    "birakmak",
)
_RELATION_CUTTING_NEGATIVE_SOURCE_PATTERNS = (
    "staj",
    "isyeri",
    "topluluk",
    "kulup",
    "saglikli_yol",
)
_RELATION_CUTTING_POSITIVE_SOURCE_PATTERNS = (
    "ilisik_kesme",
    "kayit_sildirme",
    "ogrenci_isleri",
)
_ACADEMIC_CALENDAR_DATE_QUERY_MARKERS = (
    "akademik takvim",
    "final sinavlari",
    "final sinavlarinin",
    "yariyil sonu sinavlari",
    "yariyil sonu sinav sonuclari",
    "donem sonu sinavlari",
    "ara sinavlari",
    "butunleme sinavlari",
    "sinav sonuclarinin internetten girilmesi",
    "sinav sonuclarinin sisteme girilmesi",
    "not girislerinin son gunu",
    "sonuclarinin internetten girilmesinin son gunu",
)
_ACADEMIC_CALENDAR_DATE_INTENT_MARKERS = (
    "ne zaman",
    "tarih",
    "takvim",
    "son gun",
    "son tarih",
)
_ACADEMIC_CALENDAR_SOURCE_PATTERNS = (
    "akademik_takvim",
    "akademik takvim",
    "genel_akademik_takvim",
    "takvimler",
)
_STUDENT_AFFAIRS_QUERY_PROFILES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "grade_objection",
        (
            "sinav notuma itiraz",
            "sinav sonucuna itiraz",
            "sinav sonuclarina itiraz",
            "notuma itiraz",
            "itiraz etmek istiyorum",
        ),
    ),
    (
        "grade_entry",
        (
            "notlarimi sisteme girmemis",
            "notlarim sisteme girmemis",
            "notum sisteme girmemis",
            "notlarimi sisteme girilmemis",
            "notum sisteme girilmemis",
            "hocam not girmemis",
            "hocam benim ders notlarimi sisteme girmemis",
        ),
    ),
    (
        "grade_visibility",
        (
            "sinav notlarimi nereden",
            "sinav notlarim nereden",
            "sinav notlarimi nasil",
            "sinav notlarim nasil",
            "ders notlarimi nereden",
            "ders notlarim nereden",
            "notlarimi nereden",
            "notlarim nereden",
            "notlarimi gorebilirim",
            "notlarim gorebilirim",
            "notlarimi goruntuleyebilirim",
            "notlarim goruntuleyebilirim",
        ),
    ),
    (
        "withdrawal",
        (
            "universiteyi birak",
            "universiteden ayril",
            "ayrilmak istiyorum",
            "birakip ayril",
            "kayit sildirme",
            "kaydi sildirme",
            "kaydimi sildirme",
            "ilisik kesme",
        ),
    ),
    (
        "discipline",
        (
            "kopya",
            "disiplin",
            "disiplin sureci",
            "disiplin cezasi",
        ),
    ),
    (
        "muafiyet",
        (
            "muafiyet",
            "intibak",
        ),
    ),
    (
        "course_registration",
        (
            "ders kayd",
            "ders sec",
            "kayit yenile",
            "danisman onay",
            "ilk kez",
            "donuste",
        ),
    ),
    (
        "international_registration",
        (
            "uluslararasi ogrenci",
            "ikamet izni",
            "ikamet",
            "oturma izni",
        ),
    ),
)
_QUERY_PROFILE_POSITIVE_SOURCE_PATTERNS: Dict[str, tuple[str, ...]] = {
    "grade_objection": (
        "sik_sorulan",
        "ogrenci_isleri",
        "ogrenci_isleri_birimi",
        "yonetmelik_onlisans_lisans",
        "on_lisans_ve_lisans",
        "itiraz",
        "not_duzeltme",
    ),
    "grade_entry": (
        "sik_sorulan",
        "ogrenci_isleri",
        "ogrenci_isleri_birimi",
        "oidb",
        "not_duzeltme",
        "not_bildirim",
        "bolum",
        "dekan",
        "mudur",
    ),
    "grade_visibility": (
        "sik_sorulan",
        "ogrenci_isleri",
        "ogrenci_isleri_birimi",
        "ogrenci_bilgi",
        "otomasyon",
        "ubys",
        "not",
        "sinav",
        "yonetmelik",
        "on_lisans",
    ),
    "withdrawal": (
        "sik_sorulan",
        "ilisik_kesme",
        "kayit_sildirme",
        "kayit_sildirme_formu",
        "ilisik_kesme_formu",
        "ubys",
    ),
    "discipline": (
        "disiplin",
        "ogrenci_isleri",
        "yonetmelik",
        "on_lisans",
        "kopya",
        "sinav_uygulama_kurallari",
        "muhendislik_fakultesi_sinav_uygulama_kurallari",
    ),
    "muafiyet": (
        "muafiyet",
        "intibak",
        "ders_yeterlik",
        "ogrenci_isleri",
        "sik_sorulan",
        "yonetmelik",
        "on_lisans",
    ),
    "course_registration": (
        "sik_sorulan",
        "ogrenci_isleri",
        "ubys",
        "ogrenci_bilgi",
        "kayit",
        "ders_kaydi",
        "akademik_danismanlik",
    ),
    "international_registration": (
        "uluslararasi_ogrenci",
        "ikamet",
        "oturma_izni",
        "goc",
        "kayit_taahhut",
        "evrak_teslim",
        "yonerge_uluslararasi",
    ),
}
_QUERY_PROFILE_NEGATIVE_SOURCE_PATTERNS: Dict[str, tuple[str, ...]] = {
    "grade_objection": (
        "yuzde_on",
        "ders_yeterlilik",
        "staj_",
        "_staj",
        "staj_ilkeleri",
        "staj_yonergesi",
        "staj_esas",
        "sanayi_uygulama",
        "topluluk",
    ),
    "grade_entry": (
        "yatay_gecis",
        "muafiyet",
        "ders_yeterlilik",
        "staj_",
        "_staj",
        "staj_ilkeleri",
        "staj_yonergesi",
        "staj_esas",
        "topluluk",
    ),
    "grade_visibility": (
        "staj_",
        "_staj",
        "staj_ilkeleri",
        "staj_yonergesi",
        "staj_esas",
        "mesleki_uygulama",
        "sanayi_uygulama",
        "yatay_gecis",
        "muafiyet",
        "topluluk",
    ),
    "withdrawal": (
        "staj",
        "isyeri",
        "topluluk",
        "kulup",
        "kimlik_karti",
        "konukevi",
        "yatay_gecis",
        "disiplin",
        "uzaklastirma",
        "ceza",
    ),
    "discipline": (
        "staj",
        "isyeri",
        "mesleki_uygulama",
        "konukevi",
    ),
    "muafiyet": (
        "topluluk",
        "konukevi",
        "staj",
    ),
    "course_registration": (
        "staj",
        "topluluk",
        "yuzde_on",
    ),
    "international_registration": (
        "turk_ogrenci",
        "muhendislik_fakultesi",
        "yemek_bursu",
    ),
}


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
    return normalized == department.value


def _looks_like_student_document_query(normalized_query: str) -> bool:
    """Return whether the query is about transcript/student document retrieval."""
    if any(marker in normalized_query for marker in _STUDENT_DOCUMENT_QUERY_MARKERS):
        return True
    return (
        "belge" in normalized_query
        and any(marker in normalized_query for marker in ("ogrenci", "transkript", "diploma"))
    )


def _looks_like_schedule_query(query: str) -> bool:
    """Return whether the query primarily asks for a timetable/course schedule."""
    normalized_query = normalize_text(query)
    if any(normalize_text(marker) in normalized_query for marker in ACADEMIC_SCHEDULE_QUERY_MARKERS):
        return True
    return (
        "ders" in normalized_query
        and any(marker in normalized_query for marker in ("hangi gun", "hangi gün", "hangi saatte", "saat kacta", "saat kaçta"))
    )


def _detect_query_topic(query: str) -> Optional[str]:
    """Detect the primary topic marker inside the query."""
    normalized_query = normalize_text(query)
    for topic in _TOPIC_KEYS_BY_LENGTH:
        if normalize_text(topic) in normalized_query:
            return topic
    return None


def _detect_student_affairs_query_profile(query: str) -> Optional[str]:
    """Detect high-value student-affairs procedure/query profiles."""
    normalized_query = normalize_text(query)
    if "itiraz" in normalized_query and any(marker in normalized_query for marker in ("not", "sinav", "sonuc")):
        return "grade_objection"
    if (
        "not" in normalized_query
        and "sistem" in normalized_query
        and any(marker in normalized_query for marker in ("girmemis", "girilmemis", "girilmey", "girmed"))
    ):
        return "grade_entry"
    if (
        "not" in normalized_query
        and any(
            marker in normalized_query
            for marker in ("nereden", "nerede", "nasil", "gorebilirim", "goruntuleyebilirim")
        )
    ):
        return "grade_visibility"
    for profile, marker in iter_alias_matches_longest_first(_STUDENT_AFFAIRS_QUERY_PROFILES):
        if marker in normalized_query:
            return profile
    return None


def _looks_like_academic_calendar_date_query(normalized_query: str) -> bool:
    """Return whether the query asks for general academic-calendar dates."""
    return (
        any(marker in normalized_query for marker in _ACADEMIC_CALENDAR_DATE_QUERY_MARKERS)
        and any(marker in normalized_query for marker in _ACADEMIC_CALENDAR_DATE_INTENT_MARKERS)
    )


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
        topic = _detect_query_topic(query)
        if (
            department == Department.ACADEMIC_PROGRAMS
            and topic in _ACADEMIC_TOPIC_STUDENT_AFFAIRS_SOURCE_FALLBACKS
        ):
            return [Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS], []
        return [department], []

    normalized_query = normalize_text(query)
    if _looks_like_student_document_query(normalized_query):
        return [Department.STUDENT_AFFAIRS], [Department.FINANCE]

    topic = _detect_query_topic(query)
    if topic and normalize_text(topic) in _CAP_PRIMARY_TOPICS:
        return [Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS], [Department.FINANCE]

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
        return _NO_SIGNAL_PRIMARY_DEPARTMENTS, _NO_SIGNAL_FALLBACK_DEPARTMENTS

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
    if not settings.rag.source_relevance_penalty_enabled:
        return results

    normalized_query = normalize_text(query)
    if _looks_like_academic_calendar_date_query(normalized_query):
        adjusted = False
        for result in results:
            metadata = result.get("metadata") or {}
            source_text = " ".join(
                normalize_text(str(value or ""))
                for value in (
                    result.get("source"),
                    result.get("category"),
                    metadata.get("source"),
                    metadata.get("file_name"),
                    metadata.get("relative_path"),
                    metadata.get("category"),
                    metadata.get("subcategory"),
                )
            )
            score = float(result.get("score", 0.0))
            if any(pattern in source_text for pattern in _ACADEMIC_CALENDAR_SOURCE_PATTERNS):
                result["score"] = round(score + 0.18, 4)
                adjusted = True
            elif "sik_sorulan" in source_text or "faq" in source_text:
                result["score"] = round(score * 0.75, 4)
                adjusted = True
        if adjusted:
            results.sort(key=lambda candidate: candidate["score"], reverse=True)
            logger.debug(
                "academic_calendar_source_relevance_applied",
                query=query,
                adjusted_scores=[(result.get("source", ""), result["score"]) for result in results[:5]],
            )

    profile = _detect_student_affairs_query_profile(query)
    topic = _detect_query_topic(query)
    if not topic or profile in {
        "grade_objection",
        "grade_entry",
        "withdrawal",
        "discipline",
        "muafiyet",
    }:
        return results

    expected = _TOPIC_SOURCE_PATTERNS.get(topic, [])
    if not expected:
        return results
    effective_penalty = (
        min(penalty, CAP_OFF_TOPIC_PENALTY)
        if normalize_text(topic) in _CAP_PRIMARY_TOPICS
        else penalty
    )

    adjusted = False
    for result in results:
        source = normalize_text(result.get("source", ""))
        on_topic = any(pattern in source for pattern in expected)
        if not on_topic:
            result["score"] = round(result["score"] * effective_penalty, 4)
            adjusted = True

    if adjusted:
        results.sort(key=lambda candidate: candidate["score"], reverse=True)
        logger.debug(
            "source_relevance_applied",
            topic=topic,
            adjusted_scores=[(result.get("source", ""), result["score"]) for result in results[:5]],
        )

    query_specific_adjusted = False
    for result in results:
        source = normalize_text(result.get("source", ""))
        score = float(result.get("score", 0.0))
        updated_score = score

        if (
            any(marker in normalized_query for marker in _EXAM_DISCIPLINE_QUERY_MARKERS)
            and "staj" not in normalized_query
            and any(pattern in source for pattern in _EXAM_DISCIPLINE_NEGATIVE_SOURCE_PATTERNS)
        ):
            updated_score *= 0.2

        if any(marker in normalized_query for marker in _RELATION_CUTTING_QUERY_MARKERS):
            if not any(marker in normalized_query for marker in ("staj", "topluluk", "kulup")):
                if any(pattern in source for pattern in _RELATION_CUTTING_NEGATIVE_SOURCE_PATTERNS):
                    updated_score *= 0.3
            if any(pattern in source for pattern in _RELATION_CUTTING_POSITIVE_SOURCE_PATTERNS):
                updated_score += 0.18

        if updated_score != score:
            result["score"] = round(updated_score, 4)
            query_specific_adjusted = True

    if query_specific_adjusted:
        results.sort(key=lambda candidate: candidate["score"], reverse=True)
        logger.debug(
            "query_specific_source_relevance_applied",
            query=query,
            adjusted_scores=[(result.get("source", ""), result["score"]) for result in results[:5]],
        )

    return results


def _apply_query_profile_source_bias(
    results: List[Dict[str, Any]],
    query: str,
    collection_name: str,
) -> List[Dict[str, Any]]:
    """Apply student-affairs procedure/profile source shaping before reranking."""
    if not settings.rag.query_profile_source_bias_enabled:
        return results

    profile = _detect_student_affairs_query_profile(query)
    if not profile:
        return results

    positive_patterns = _QUERY_PROFILE_POSITIVE_SOURCE_PATTERNS.get(profile, ())
    negative_patterns = _QUERY_PROFILE_NEGATIVE_SOURCE_PATTERNS.get(profile, ())
    adjusted = False

    for item in results:
        source = normalize_text(item.get("source", ""))
        metadata = item.get("metadata") or {}
        metadata_text = " ".join(
            normalize_text(str(value or ""))
            for value in (
                metadata.get("file_name"),
                metadata.get("source"),
                metadata.get("title"),
            )
        )
        content = normalize_text(str(item.get("content") or "")[:700])
        haystack = f"{source} {metadata_text} {content}"
        score = float(item.get("score", 0.0))
        updated_score = score

        matches_positive = any(pattern in haystack for pattern in positive_patterns)
        matches_negative = any(pattern in haystack for pattern in negative_patterns)

        if matches_positive:
            updated_score += 0.22
            if _candidate_targets_department(item, Department.STUDENT_AFFAIRS, collection_name):
                updated_score += 0.08
            # Some high-value FAQ/admin chunks are weak on dense+BM25 score but
            # still exact matches for query-profile slots (e.g. OIDB contact,
            # not itirazi, muafiyet dilekcesi). Give them a small floor so they
            # are not dropped before reranking.
            if profile in {"grade_objection", "grade_entry", "withdrawal", "muafiyet"}:
                updated_score = max(updated_score, 0.30)

        if matches_negative:
            updated_score *= 0.25 if profile == "discipline" else 0.35

        if updated_score != score:
            item["score"] = round(updated_score, 4)
            adjusted = True

    if adjusted:
        results.sort(key=lambda item: item.get("score", 0.0), reverse=True)
        logger.debug(
            "query_profile_source_bias_applied",
            query=query,
            profile=profile,
            top_sources=[(result.get("source", ""), result.get("score", 0.0)) for result in results[:5]],
        )

    return results


def _apply_education_level_penalty(
    results: List[Dict[str, Any]],
    query: str,
) -> List[Dict[str, Any]]:
    """Penalize lisansustu sources when query is about lisans, and vice versa."""
    if not settings.rag.education_level_penalty_enabled:
        return results

    normalized_query = normalize_text(query)
    query_is_lisansustu = any(
        marker in normalized_query for marker in _LISANSUSTU_INDICATORS
    )

    adjusted = False
    for item in results:
        source = normalize_text(item.get("source", ""))
        metadata = item.get("metadata") or {}
        file_name = normalize_text(str(metadata.get("file_name", "")))
        combined = f"{source} {file_name}"

        if not query_is_lisansustu:
            if any(marker in combined for marker in _LISANSUSTU_SOURCE_MARKERS):
                item["score"] = round(float(item.get("score", 0.0)) * 0.35, 4)
                adjusted = True
        else:
            is_lisans_only = (
                any(marker in combined for marker in _LISANS_SOURCE_MARKERS)
                and not any(marker in combined for marker in _LISANSUSTU_SOURCE_MARKERS)
            )
            if is_lisans_only:
                item["score"] = round(float(item.get("score", 0.0)) * 0.6, 4)
                adjusted = True

    if adjusted:
        results.sort(key=lambda item: item.get("score", 0.0), reverse=True)
        logger.debug(
            "education_level_penalty_applied",
            query=query,
            query_is_lisansustu=query_is_lisansustu,
            top_sources=[(r.get("source", ""), r.get("score", 0.0)) for r in results[:5]],
        )

    return results


def _apply_finance_source_penalty(
    results: List[Dict[str, Any]],
    query: str,
    collection_name: str,
) -> List[Dict[str, Any]]:
    """Push international-fee sources down for general finance fee queries."""
    if not settings.rag.finance_source_penalty_enabled:
        return results

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
    if not settings.rag.student_affairs_faq_bias_enabled:
        return results

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
