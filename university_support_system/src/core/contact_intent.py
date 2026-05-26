"""Contact intent helpers shared by routing and specialist agents."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from src.core.query_markers import CONTACT_QUERY_MARKERS
from src.core.text_normalization import contains_any_normalized, normalize_text

_DIRECT_CONTACT_QUERY_MARKERS = (
    "iletisim",
    "iletisim bilgisi",
    "telefon",
    "telefon numarasi",
    "dahili",
    "eposta",
    "e-posta",
    "email",
    "sekreter",
    "sekreterlik",
)
_LOCATION_CONTACT_QUERY_MARKERS = (
    "adres",
    "nerede",
    "kime basvurayim",
    "kimle gorusmeliyim",
)
_CONTACT_FUZZY_TARGETS = (
    "iletisim",
    "sekreter",
    "eposta",
    "dahili",
)
_PHONE_FUZZY_TARGETS = (
    "telefon",
)
_CONTACT_FUZZY_THRESHOLD = 0.82
_PERSONAL_PHONE_CONTEXT_MARKERS = (
    "telefonum",
    "telefonumu",
    "telefon numaram",
    "telefon numarami",
    "numaram degisti",
    "numarami degistir",
    "numarami guncelle",
    "numarami nasil",
    "gsm numaram",
    "cep telefonu",
)
_EXPLICIT_CONTACT_CONTEXT_MARKERS = (
    "iletisim",
    "iletisim bilgisi",
    "ogrenci isleri telefonu",
    "sekreter",
    "sekreterlik",
    "dahili",
    "eposta",
    "e-posta",
    "email",
    "ofis telefonu",
)
_OFFICE_CONTACT_CONTEXT_MARKERS = (
    "ogrenci isleri",
    "sekreter",
    "sekreterlik",
    "ofis",
    "birim",
    "danisman",
    "dekanlik",
    "mudurluk",
    "bolum",
    "fakulte",
)


def _contains_marker_word(normalized: str, marker: str) -> bool:
    escaped = re.escape(normalize_text(marker))
    return re.search(rf"(?<!\w){escaped}(?!\w)", normalized) is not None


def _contains_any_marker_word(normalized: str, markers: tuple[str, ...]) -> bool:
    return any(_contains_marker_word(normalized, marker) for marker in markers)


def _is_close_contact_token(token: str) -> bool:
    if len(token) < 5:
        return False
    # "dahil" gibi akademik kelimeler "dahili" ile cok yakin; fuzzy contact'a kaymasin.
    if token in {"dahil", "dahildir", "dahiliyeti"}:
        return False
    return any(
        SequenceMatcher(None, token, target).ratio() >= _CONTACT_FUZZY_THRESHOLD
        for target in _CONTACT_FUZZY_TARGETS
    )


def _is_close_phone_token(token: str) -> bool:
    if len(token) < 5:
        return False
    return any(
        SequenceMatcher(None, token, target).ratio() >= _CONTACT_FUZZY_THRESHOLD
        for target in _PHONE_FUZZY_TARGETS
    )


def looks_like_contact_intent(query: object | None) -> bool:
    """Return True for direct contact requests, including small typos."""
    normalized = normalize_text(query)
    if contains_any_normalized(normalized, _PERSONAL_PHONE_CONTEXT_MARKERS) and not contains_any_normalized(
        normalized,
        _EXPLICIT_CONTACT_CONTEXT_MARKERS,
    ):
        return False
    if _contains_any_marker_word(normalized, _DIRECT_CONTACT_QUERY_MARKERS):
        return True
    if _contains_any_marker_word(normalized, _LOCATION_CONTACT_QUERY_MARKERS):
        return contains_any_normalized(normalized, _OFFICE_CONTACT_CONTEXT_MARKERS)
    if contains_any_normalized(normalized, CONTACT_QUERY_MARKERS):
        return contains_any_normalized(normalized, _EXPLICIT_CONTACT_CONTEXT_MARKERS)
    if contains_any_normalized(normalized, _OFFICE_CONTACT_CONTEXT_MARKERS) and any(
        _is_close_phone_token(token) for token in normalized.split()
    ):
        return True
    return any(_is_close_contact_token(token) for token in normalized.split())
