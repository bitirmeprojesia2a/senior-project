"""Metin normalizasyonu ve eslesme yardimcilari."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from typing import TypeVar

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
_T = TypeVar("_T")


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


def normalized_length(value: object | None) -> int:
    """Return normalized text length for specificity-based matching."""
    return len(normalize_text(value))


def iter_alias_matches_longest_first(
    alias_groups: Iterable[tuple[_T, Sequence[str]]],
) -> Iterable[tuple[_T, str]]:
    """Yield ``(target, normalized_alias)`` pairs with specific aliases first.

    This prevents generic aliases such as "matematik" from shadowing more
    specific aliases such as "matematik ogretmenligi" in first-match logic.
    Input order is preserved as the tie-breaker.
    """
    candidates: list[tuple[int, int, int, _T, str]] = []
    for group_order, (target, aliases) in enumerate(alias_groups):
        for alias_order, alias in enumerate(aliases):
            normalized_alias = normalize_text(alias)
            if not normalized_alias:
                continue
            candidates.append(
                (len(normalized_alias), group_order, alias_order, target, normalized_alias)
            )

    for _length, _group_order, _alias_order, target, normalized_alias in sorted(
        candidates,
        key=lambda item: (-item[0], item[1], item[2]),
    ):
        yield target, normalized_alias
