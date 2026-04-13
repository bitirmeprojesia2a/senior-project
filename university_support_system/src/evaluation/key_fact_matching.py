"""Key-fact matching helpers for quality benchmarks."""

from __future__ import annotations

import re
import unicodedata

from src.core.text_normalization import collapse_whitespace, normalize_text

_NUMBER_WORDS = {
    "sifir": "0",
    "bir": "1",
    "iki": "2",
    "uc": "3",
    "dort": "4",
    "bes": "5",
    "alti": "6",
    "yedi": "7",
    "sekiz": "8",
    "dokuz": "9",
    "on": "10",
}

_ORDINAL_NUMBER_RE = re.compile(r"\b(\d+)\.(?=\s*[a-z])")
_DECIMAL_COMMA_RE = re.compile(r"(?<=\d),(?=\d)")
_NON_ALNUM_RE = re.compile(r"[^0-9a-z\.\s]+")


def _strip_diacritics(value: object | None) -> str:
    if value is None:
        return ""
    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_key_fact_text(value: object | None) -> str:
    """Normalize benchmark facts for tolerant matching."""
    text = normalize_text(_strip_diacritics(value))
    text = _DECIMAL_COMMA_RE.sub(".", text)
    text = _ORDINAL_NUMBER_RE.sub(r"\1", text)
    for word, digit in _NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", digit, text)
    text = _NON_ALNUM_RE.sub(" ", text)
    text = collapse_whitespace(text)
    return text


def key_fact_present(answer: str, fact: str) -> bool:
    """Return whether a normalized fact is present in the answer."""
    normalized_fact = normalize_key_fact_text(fact)
    if not normalized_fact:
        return False
    normalized_answer = normalize_key_fact_text(answer)
    return normalized_fact in normalized_answer


def check_key_facts(answer: str, expected_facts: list[str]) -> dict[str, bool]:
    """Check expected benchmark facts against an answer with tolerant matching."""
    return {fact: key_fact_present(answer, fact) for fact in expected_facts}
