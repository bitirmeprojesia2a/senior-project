"""Helpers for student affairs registration agent."""

from __future__ import annotations

from collections.abc import Sequence

from src.core.text_normalization import normalize_text

REGISTRATION_TIMING_KEYWORDS: tuple[str, ...] = (
    "ne zaman",
    "tarih",
    "donem",
    "dönem",
    "takvim",
    "baslangic",
    "başlangıç",
    "bitis",
    "bitiş",
    "acik mi",
    "açık mı",
    "aktif",
    "son gun",
    "son tarih",
    "son basvuru",
    "kayit donemi",
)

REGISTRATION_SOURCE_ONLY_KEYWORDS: tuple[str, ...] = (
    "basvuru",
    "nasil yapilir",
    "gerekli belge",
    "evrak",
    "sart",
    "kosul",
    "muafiyet",
    "intibak",
    "yatay gecis",
    "dikey gecis",
    "cap",
    "cift anadal",
    "yan dal",
    "kayit dondurma",
    "donem dondurma",
    "kayit sildirme",
    "ilisik kesme",
    "ders ekleme",
    "ders birakma",
)

REGISTRATION_TOPIC_MARKERS: dict[str, tuple[str, ...]] = {
    "cap": ("cap", "cift anadal", "cift ana dal", "ikinci lisans"),
    "yandal": ("yandal", "yan dal"),
    "yatay": ("yatay gecis", "yatay", "kurum ici yatay"),
    "dikey": ("dikey gecis", "dikey", "dgs"),
    "muafiyet": ("muafiyet", "intibak"),
    "dondurma": ("kayit dondurma", "donem dondurma", "donem izni"),
    "silme": ("kayit sildirme", "ilisik kesme", "ayrilma"),
    "staj": ("staj", "zorunlu staj", "mustahaklik", "provizyon"),
}

REGISTRATION_QUERY_ASPECTS: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "document",
        ("belge", "evrak", "form", "dokuman"),
        ("belge", "evrak", "form", "dokuman", "nufus", "mustahaklik", "provizyon"),
    ),
    (
        "timing",
        ("ne zaman", "tarih", "takvim", "son basvuru", "son tarih", "donem"),
        ("ne zaman", "tarih", "takvim", "son basvuru", "son tarih", "baslangic", "bitis"),
    ),
    (
        "condition",
        ("kosul", "kosullari", "sart", "sartlari", "gerekli", "gerekiyor", "kriter"),
        ("kosul", "sart", "gerekli", "gerekir", "kriter", "ortalama", "yuzde", "basari", "kabul"),
    ),
    (
        "quota",
        ("kontenjan",),
        ("kontenjan",),
    ),
    (
        "fee",
        ("ucret", "harc", "odeme"),
        ("ucret", "harc", "odeme", "katki payi"),
    ),
    (
        "process",
        ("nasil", "surec", "basvuru", "basvurusu", "adim"),
        ("nasil", "surec", "basvuru", "elektronik", "online", "link", "adim"),
    ),
)

_FAQ_SOURCE_MARKERS: tuple[str, ...] = ("sss", "faq", "sik sorulan")


def normalize_registration_text(text: str) -> str:
    return normalize_text(text)


_VT_EXCLUDE_TOPICS: tuple[str, ...] = (
    "kayit dondurma",
    "donem dondurma",
    "kayit sildirme",
    "ilisik kesme",
    "muafiyet",
    "intibak",
    "yatay",
    "dikey",
    "cap",
    "cift anadal",
    "yan dal",
    "staj",
    "mezuniyet",
    "burs",
    "harc",
    "ucret",
    "katki payi",
    "ek sure",
    "devamsizlik",
    "butunleme",
    "sinav",
    "ders secimi",
    "ders ekleme",
    "ders birakma",
)

_PROCESS_NOT_TIMING: tuple[str, ...] = (
    "nasil yapilir",
    "nasil yapacagim",
    "nasil isliyor",
    "sureci nasil",
    "adim adim",
    "ne yapmaliyim",
    "danismanin onayi",
    "danismanin onay",
)

_REGISTRATION_CONTEXT: tuple[str, ...] = (
    "kayit",
    "ders kaydi",
)


def is_registration_timing_query(query_text: str) -> bool:
    lowered = normalize_registration_text(query_text)

    if any(kw in lowered for kw in _VT_EXCLUDE_TOPICS):
        return False

    if any(kw in lowered for kw in _PROCESS_NOT_TIMING):
        return False

    if "kayit donemi" in lowered:
        return True

    has_timing = any(
        normalize_registration_text(kw) in lowered
        for kw in REGISTRATION_TIMING_KEYWORDS
    )
    if not has_timing:
        return False

    return any(kw in lowered for kw in _REGISTRATION_CONTEXT)


def should_skip_registration_llm_synthesis(
    query_text: str,
    results: Sequence[dict],
) -> bool:
    lowered = normalize_registration_text(query_text)
    if any(
        marker in lowered
        for markers in REGISTRATION_TOPIC_MARKERS.values()
        for marker in markers
    ):
        return bool(results)
    return bool(results) and any(keyword in lowered for keyword in REGISTRATION_SOURCE_ONLY_KEYWORDS)


def build_registration_intro(query_text: str) -> str:
    lowered = normalize_registration_text(query_text)
    if "cap" in lowered or "cift anadal" in lowered:
        return "CAP basvurusu icin en ilgili kaynakta su bilgi yer aliyor:"
    if "yandal" in lowered or "yan dal" in lowered:
        return "Yandal basvurusu icin en ilgili kaynakta su bilgi yer aliyor:"
    if "yatay" in lowered:
        return "Yatay gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:"
    if "dikey" in lowered:
        return "Dikey gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:"
    return "En ilgili ogrenci isleri kaynaginda su bilgi yer aliyor:"


def pick_preferred_registration_result(query_text: str, results: Sequence[dict]) -> dict | None:
    if not results:
        return None

    normalized_query = normalize_registration_text(query_text)
    expected_topic_key: str | None = None
    expected_markers: tuple[str, ...] = ()
    expected_aspect = detect_registration_query_aspect(normalized_query)
    best_marker_len = 0
    for topic_key, topic_markers in REGISTRATION_TOPIC_MARKERS.items():
        for marker in topic_markers:
            if marker in normalized_query and len(marker) > best_marker_len:
                expected_topic_key = topic_key
                expected_markers = topic_markers
                best_marker_len = len(marker)
        if topic_key in normalized_query and len(topic_key) > best_marker_len:
            expected_topic_key = topic_key
            expected_markers = topic_markers
            best_marker_len = len(topic_key)

    ranked = sorted(
        results,
        key=lambda item: (
            0 if matches_registration_topic(item, expected_markers) else 1,
            1 if has_conflicting_registration_topic(item, expected_topic_key) else 0,
            0 if matches_registration_aspect(item, expected_aspect) else 1,
            1 if should_penalize_registration_qa(item, expected_aspect) else 0,
            -float(item.get("score", 0.0)),
        ),
    )
    return dict(ranked[0])


def matches_registration_topic(item: dict, expected_markers: tuple[str, ...]) -> bool:
    if not expected_markers:
        return True
    source = normalize_registration_text(item.get("source", ""))
    content = normalize_registration_text(item.get("content", "")[:600])
    return any(marker in source or marker in content for marker in expected_markers)


def has_conflicting_registration_topic(item: dict, expected_topic_key: str | None) -> bool:
    if not expected_topic_key:
        return False

    source = normalize_registration_text(item.get("source", ""))
    content = normalize_registration_text(item.get("content", "")[:600])
    matched_topics = {
        topic_key
        for topic_key, topic_markers in REGISTRATION_TOPIC_MARKERS.items()
        if any(marker in source or marker in content for marker in topic_markers)
    }

    matched_topics.discard(expected_topic_key)
    if expected_topic_key == "dondurma":
        matched_topics.discard("silme")
    if expected_topic_key == "silme":
        matched_topics.discard("dondurma")
    return bool(matched_topics)


def detect_registration_query_aspect(normalized_query: str) -> str | None:
    for aspect, query_markers, _content_markers in REGISTRATION_QUERY_ASPECTS:
        if any(marker in normalized_query for marker in query_markers):
            return aspect
    return None


def matches_registration_aspect(item: dict, expected_aspect: str | None) -> bool:
    if not expected_aspect:
        return True

    aspect_markers = next(
        (
            content_markers
            for aspect, _query_markers, content_markers in REGISTRATION_QUERY_ASPECTS
            if aspect == expected_aspect
        ),
        (),
    )
    if not aspect_markers:
        return True

    source = normalize_registration_text(item.get("source", ""))
    content = normalize_registration_text(item.get("content", "")[:900])
    return any(marker in source or marker in content for marker in aspect_markers)


def should_penalize_registration_qa(item: dict, expected_aspect: str | None) -> bool:
    if expected_aspect not in {"document", "timing", "condition", "quota"}:
        return False

    source = normalize_registration_text(item.get("source", ""))
    metadata = normalize_registration_text((item.get("metadata") or {}).get("file_name", ""))
    content = str(item.get("content", "")[:240])
    normalized_content = normalize_registration_text(content)

    if any(marker in source or marker in metadata for marker in _FAQ_SOURCE_MARKERS):
        return True

    return (
        "?" in content
        and any(marker in normalized_content for marker in ("ogrencisiyim", "miyim", "miyiz", "zorunda miyim"))
    )


def should_reject_registration_source_only_result(query_text: str, item: dict) -> bool:
    normalized_query = normalize_registration_text(query_text)
    expected_aspect = detect_registration_query_aspect(normalized_query)
    if expected_aspect not in {"document", "timing", "condition", "quota"}:
        return False
    if not matches_registration_aspect(item, expected_aspect):
        return True
    return should_penalize_registration_qa(item, expected_aspect)
