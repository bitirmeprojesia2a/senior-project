"""Small intent guards shared by routing, clarification, and follow-up code."""

from __future__ import annotations

from src.core.text_normalization import normalize_text

_FEE_MARKERS = (
    "ucret",
    "ucreti",
    "harc",
    "ogrenim ucreti",
    "katki payi",
)

_FEE_AMOUNT_MARKERS = (
    "ne kadar",
    "kac tl",
    "kac lira",
    "tutar",
    "tutari",
    "donemlik",
    "yillik",
    "ucret tablosu",
)

_EXPLICIT_FEE_AMOUNT_NOUNS = (
    "ucreti",
    "ucretleri",
    "harc ucreti",
    "ogrenim ucreti",
)

_NON_AMOUNT_FEE_CONTEXT_MARKERS = (
    "ne zaman",
    "tarih",
    "son odeme",
    "nasil odenir",
    "nasil yatirilir",
    "odeme",
    "yatirma",
    "yatir",
)

_PAYMENT_CONDITION_MARKERS = (
    "borc",
    "borcum",
    "borcu",
    "borclu",
    "odemezsem",
    "odemeden",
    "odenmezse",
    "yatirmazsam",
    "yatirmadan",
    "odemem gerekir mi",
    "odeyebilir miyim",
    "taksit",
    "taksitle",
)

_CONDITIONAL_MARKERS = (
    "olsaydi",
    "olsaydim",
    "olursa",
    "olursam",
    "diyelim ki",
    "varsayalim",
    "farz edelim",
)

_ACTION_ELIGIBILITY_MARKERS = (
    "basvurabilir",
    "basvurabilir miyim",
    "basvurabilir miydim",
    "katilabilir",
    "yapabilir",
    "girebilir",
    "alabilir",
    "mezun olabilir",
    "kabul edilir",
    "engel",
    "sorun olur",
    "etkiler mi",
    "etkilenir mi",
    "yararlanabilir",
    "hakki",
    "haklarindan",
    "zorunda miyim",
    "gerekir mi",
)


def looks_like_fee_catalog_amount_query(query: str | None) -> bool:
    """Return whether the query asks for a tuition/fee amount table value."""
    if not query:
        return False
    normalized = normalize_text(query)
    if not any(marker in normalized for marker in _FEE_MARKERS):
        return False
    if any(marker in normalized for marker in _PAYMENT_CONDITION_MARKERS):
        return False
    if any(marker in normalized for marker in _CONDITIONAL_MARKERS):
        return False
    if any(marker in normalized for marker in _ACTION_ELIGIBILITY_MARKERS):
        return False
    if any(marker in normalized for marker in _FEE_AMOUNT_MARKERS):
        return True
    return (
        any(marker in normalized for marker in _EXPLICIT_FEE_AMOUNT_NOUNS)
        and not any(marker in normalized for marker in _NON_AMOUNT_FEE_CONTEXT_MARKERS)
    )


def looks_like_payment_condition_or_eligibility_query(query: str | None) -> bool:
    """Return whether payment is a condition/facet of an action, not an amount request."""
    if not query:
        return False
    normalized = normalize_text(query)
    if not any(marker in normalized for marker in _FEE_MARKERS + _PAYMENT_CONDITION_MARKERS):
        return False
    has_condition = any(marker in normalized for marker in _PAYMENT_CONDITION_MARKERS + _CONDITIONAL_MARKERS)
    has_action = any(marker in normalized for marker in _ACTION_ELIGIBILITY_MARKERS)
    return has_condition and has_action
