"""Contact intent helpers shared by routing and specialist agents."""

from __future__ import annotations

from difflib import SequenceMatcher

from src.core.query_markers import CONTACT_QUERY_MARKERS
from src.core.text_normalization import contains_any_normalized, normalize_text

_CONTACT_FUZZY_TARGETS = (
    "iletisim",
    "telefon",
    "sekreter",
    "eposta",
    "dahili",
)
_CONTACT_FUZZY_THRESHOLD = 0.82


def _is_close_contact_token(token: str) -> bool:
    if len(token) < 5:
        return False
    return any(
        SequenceMatcher(None, token, target).ratio() >= _CONTACT_FUZZY_THRESHOLD
        for target in _CONTACT_FUZZY_TARGETS
    )


def looks_like_contact_intent(query: object | None) -> bool:
    """Return True for direct contact requests, including small typos."""
    normalized = normalize_text(query)
    if contains_any_normalized(normalized, CONTACT_QUERY_MARKERS):
        return True
    return any(_is_close_contact_token(token) for token in normalized.split())
