"""Metin normalizasyonu ve eslesme yardimcilari."""

from __future__ import annotations

import re
from typing import Sequence

_NORMALIZE_CHAR_MAP = str.maketrans(
    {
        "\u00e7": "c",
        "\u00c7": "c",
        "\u011f": "g",
        "\u011e": "g",
        "\u0131": "i",
        "\u0130": "i",
        "\u00f6": "o",
        "\u00d6": "o",
        "\u015f": "s",
        "\u015e": "s",
        "\u00fc": "u",
        "\u00dc": "u",
    }
)
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: object | None) -> str:
    """Turkce karakterleri ASCII-benzeri forma indirger ve kucultur."""
    if value is None:
        return ""
    return str(value).translate(_NORMALIZE_CHAR_MAP).casefold()


def collapse_whitespace(value: object | None) -> str:
    """Metni tek bosluklu satira indirger."""
    if value is None:
        return ""
    return _WHITESPACE_RE.sub(" ", str(value)).strip()


def contains_any_normalized(text: object | None, markers: Sequence[str]) -> bool:
    """Normalizasyondan sonra marker eslesmesi yapar."""
    normalized = normalize_text(text)
    return any(normalize_text(marker) in normalized for marker in markers)
