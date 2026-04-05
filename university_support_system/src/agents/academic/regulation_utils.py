"""Helpers for regulation and international academic agents."""

from __future__ import annotations

from src.core.text_normalization import normalize_text

REGULATION_SOURCE_ONLY_MARKERS: tuple[str, ...] = (
    "cap",
    "cift anadal",
    "cift ana dal",
    "yandal",
    "yan dal",
    "erasmus",
    "degisim programi",
    "basvuru",
    "sart",
    "kosul",
)

REGULATION_TOPIC_MARKERS: dict[str, tuple[str, ...]] = {
    "cap": ("cap", "cift anadal", "cift ana dal"),
    "yandal": ("yandal", "yan dal"),
    "erasmus": ("erasmus", "degisim programi", "degisim"),
}

INTL_TUITION_KEYWORDS: tuple[str, ...] = (
    "harc",
    "harç",
    "ucret",
    "ücret",
    "odeme",
    "ödeme",
    "taksit",
)


def should_skip_regulation_llm_synthesis(
    query_text: str,
    results: list[dict] | tuple[dict, ...],
) -> bool:
    lowered = normalize_text(query_text)
    return bool(results) and any(marker in lowered for marker in REGULATION_SOURCE_ONLY_MARKERS)


def build_regulation_intro(query_text: str) -> str:
    lowered = normalize_text(query_text)
    if "cap" in lowered or "cift anadal" in lowered:
        return "CAP mevzuatinda one cikan kosullar soyledir:"
    if "yandal" in lowered or "yan dal" in lowered:
        return "Yandal mevzuatinda one cikan kosullar soyledir:"
    if "erasmus" in lowered or "degisim programi" in lowered:
        return "Degisim programi kurallarinda one cikan bilgi soyledir:"
    return "Akademik mevzuatta en ilgili bilgi su sekildedir:"


def pick_preferred_regulation_result(
    query_text: str,
    results: list[dict] | tuple[dict, ...],
) -> dict | None:
    if not results:
        return None

    lowered = normalize_text(query_text)
    expected_markers: tuple[str, ...] = ()
    for marker, topic_markers in REGULATION_TOPIC_MARKERS.items():
        if marker in lowered:
            expected_markers = topic_markers
            break

    ranked = sorted(
        results,
        key=lambda item: (
            0 if matches_regulation_topic(item, expected_markers) else 1,
            -float(item.get("score", 0.0)),
        ),
    )
    return dict(ranked[0])


def matches_regulation_topic(item: dict, expected_markers: tuple[str, ...]) -> bool:
    if not expected_markers:
        return True
    source = normalize_text(item.get("source", ""))
    content = normalize_text(item.get("content", "")[:600])
    return any(marker in source or marker in content for marker in expected_markers)


def needs_international_finance_reference(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    has_intl = any(
        kw in lowered for kw in ("uluslararasi", "uluslararası", "yabanci", "yabancı", "erasmus")
    )
    has_finance = any(kw in lowered for kw in INTL_TUITION_KEYWORDS)
    return has_intl and has_finance
