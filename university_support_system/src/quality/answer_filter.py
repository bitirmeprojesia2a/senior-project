"""Post-generation answer quality filter.

Detects foreign/broken tokens in generated answers and triggers
rewrite-only retry when quality issues are found.  Maximum 1 retry.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass

from src.core.text_normalization import normalize_text

logger = logging.getLogger(__name__)

# ── Detection patterns ─────────────────────────────────────────────

# Non-Latin script blocks that should never appear in Turkish text
_NON_LATIN_SCRIPT_RE = re.compile(
    "[\u0400-\u04ff"   # Cyrillic
    "\u0900-\u097f"    # Devanagari
    "\u4e00-\u9fff"    # CJK Unified
    "\u3040-\u309f"    # Hiragana
    "\u30a0-\u30ff"    # Katakana
    "\uac00-\ud7af"    # Hangul syllables
    "\u1100-\u11ff"    # Hangul Jamo
    "\u0600-\u06ff"    # Arabic
    "\u0590-\u05ff"    # Hebrew
    "]+"
)

# Common misrecognized / broken tokens
_BROKEN_TOKEN_RE = re.compile(
    r"\b(tonabilir|dentroslar|possibilite|konkret|bekannt|verificar|"
    r"información|requerido|puede|deber|espec\w+|además|además|también|"
    r"por favor|necessario|podria|siguientes|continuation|"
    r"appropriate|necesario|enen|bailikli|bailik|odense)\b",
    re.IGNORECASE,
)

# Mixed-script word: Turkish sentence with embedded English/foreign word
# that is NOT a common loanword (like "online", "test", "kampüs")
_ENGLISH_WORD_RE = re.compile(r"\b[a-z]{4,}\b", re.IGNORECASE)
_TURKISH_LOANWORDS = frozenset({
    "online", "test", "kampus", "kampüs", "form", "sistem", "portal",
    "program", "kod", "mail", "e posta", "web", "link", "pdf", "excel",
    "word", "ubys", "obs", "akts", "gno", "cap", "yks", "lys", "dgs",
    "kpss", "ales", "yds", "yok", "omü", "omu", "sks", "mfb",
    "lab", "labaratuvar", "laboratuvar", "bilgi", "sayisal",
})
_ENGLISH_ONLY_HINTS = frozenset({
    "the", "and", "for", "with", "that", "this", "from", "after",
    "before", "during", "will", "would", "should", "could", "must",
    "however", "therefore", "furthermore", "moreover", "nevertheless",
    "accordingly", "consequently", "specifically", "approximately",
    "respectively", "regarding", "additionally", "including", "excluding",
    "contribution", "however", "therefore", "necessary", "required",
    "information", "application", "process", "condition", "requirement",
    "document", "student", "university", "education", "academic",
    "registration", "renewal", "semester", "fee", "fees", "refund",
    "cancel", "graduate", "doctoral", "master", "language", "following",
    "several", "different", "same", "overview", "timeline", "approval",
    "approved", "certain", "details", "detail", "success",
})

# Corrupted suffix patterns: Turkish root + foreign suffix
_CORRUPT_SUFFIX_RE = re.compile(
    r"\w+(?:tion|ment|ness|able|ible|ous|ive|ful|less|ing|ally)\b",
    re.IGNORECASE,
)
_TURKISH_WORDS_WITH_EN_SUFFIXES = frozenset({
    "yapilandirilmis", "yapilandirilmalar", "desteklenmektedir",
})


@dataclass(frozen=True)
class QualityCheckResult:
    """Result of post-generation quality check."""

    has_foreign_script: bool
    has_broken_tokens: bool
    has_suspicious_english: bool
    has_corrupt_suffixes: bool
    needs_rewrite: bool
    detected_issues: list[str]
    bad_tokens: list[str]


def check_answer_quality(answer: str) -> QualityCheckResult:
    """Check an answer for foreign/broken token quality issues.

    Returns a QualityCheckResult with detected issues and whether
    a rewrite-only retry should be attempted.
    """
    issues: list[str] = []
    bad_tokens: list[str] = []

    # 1) Non-Latin script detection
    non_latin_matches = _NON_LATIN_SCRIPT_RE.findall(answer)
    if non_latin_matches:
        issues.append("non_latin_script")
        bad_tokens.extend(non_latin_matches[:5])

    # 2) Broken / misrecognized tokens
    broken_matches = _BROKEN_TOKEN_RE.findall(answer)
    if broken_matches:
        issues.append("broken_tokens")
        bad_tokens.extend(broken_matches[:5])

    # 3) Suspicious English words in Turkish text
    normalized = normalize_text(answer)
    en_words = _ENGLISH_WORD_RE.findall(normalized)
    suspicious = [
        w for w in en_words
        if w.lower() in _ENGLISH_ONLY_HINTS
        and w.lower() not in _TURKISH_LOANWORDS
    ]
    if len(suspicious) >= 2:
        issues.append("suspicious_english")
        bad_tokens.extend(suspicious[:5])

    # 4) Corrupted suffix patterns
    corrupt_matches = [
        m.group(0)
        for m in _CORRUPT_SUFFIX_RE.finditer(answer)
        if m.group(0).lower() not in _TURKISH_WORDS_WITH_EN_SUFFIXES
    ]
    if corrupt_matches:
        issues.append("corrupt_suffixes")
        bad_tokens.extend(corrupt_matches[:3])

    needs_rewrite = len(issues) > 0

    return QualityCheckResult(
        has_foreign_script="non_latin_script" in issues,
        has_broken_tokens="broken_tokens" in issues,
        has_suspicious_english="suspicious_english" in issues,
        has_corrupt_suffixes="corrupt_suffixes" in issues,
        needs_rewrite=needs_rewrite,
        detected_issues=issues,
        bad_tokens=bad_tokens,
    )


REWRITE_ONLY_SYSTEM_SUFFIX = (
    "\n\nEK KAL\u0130TE KURALI: Cevab\u0131 ayn\u0131 anlam\u0131 koruyarak do\u011fal T\u00fcrk\u00e7e yaz. "
    "Yabanc\u0131 kelime, bozuk token, uydurma ifade kullanma. "
    "Kaynak d\u0131\u015f\u0131 bilgi ekleme. \u00d6nceki cevaptaki anlam ve bilgiyi koru ama "
    "t\u00fcm kelimeleri do\u011fal T\u00fcrk\u00e7e ile ifade et."
)
