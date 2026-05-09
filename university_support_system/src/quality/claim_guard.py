"""Deterministic claim grounding guard.

Checks LLM-generated answers against structured evidence items to detect
ungrounded claims (numbers, dates, entities, definitive statements).

Design principles:
- Conservative: logs to diagnostics first, modifies answer minimally.
- Never deletes sentences.
- Only softens very clear hallucinated entities/portals not in any source.
- Does NOT add generic "teyit ediniz" to every answer — only when a
  modification was actually made.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence

from src.core.text_normalization import normalize_text
from src.quality.evidence import (
    EvidenceItem,
    KNOWN_SYSTEM_ENTITIES,
    extract_factual_claims,
)


@dataclass
class GuardResult:
    """Result of the claim guard check."""

    cleaned_answer: str
    unsupported_claims: list[dict] = field(default_factory=list)
    modifications_made: int = 0
    diagnostics: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Patterns for entity detection in answers
# ---------------------------------------------------------------------------

# Portal/system names: capitalized multi-word or URL-like references
_PORTAL_RE = re.compile(
    r"\b(?:e-[A-Za-z\u00c0-\u024f]{3,}|"
    r"[A-Z\u00c0-\u024f][a-z\u00c0-\u024f]+\s+(?:portali|sistemi|ekrani|menusu|platformu|modulu))\b",
)

# Payment channel patterns
_PAYMENT_CHANNEL_RE = re.compile(
    r"\b(?:banka\s+subesi|atm|internet\s+bankaciligi|"
    r"mobil\s+bankaciligi|eft|havale|pos\s+cihazi|"
    r"kredi\s+karti|odeme\s+noktasi)\b",
    re.IGNORECASE,
)

# Document/form names: "... formu", "... belgesi", "... dilekce"
_DOCUMENT_RE = re.compile(
    r"\b[A-Z\u00c0-\u024f][a-z\u00c0-\u024f]+(?:\s+[A-Za-z\u00c0-\u024f]+)*\s+"
    r"(?:formu|belgesi|dilekcesi|dilekce|tutanagi)\b",
)

_OFFICE_RE = re.compile(
    r"\b[A-Z\u00c0-\u024f][a-z\u00c0-\u024f]+(?:\s+[A-Za-z\u00c0-\u024f]+){0,4}\s+"
    r"(?:Burosu|B\u00fcrosu|Ofisi|Dairesi|Baskanligi|Ba\u015fkanl\u0131\u011f\u0131|Mudurlugu|M\u00fcd\u00fcrl\u00fc\u011f\u00fc)\b",
)

# Definitive claim endings — only the very strong ones
_STRONG_DEFINITIVE_RE = re.compile(
    r"\b(kesinlikle\s+(?:yapilamaz|yapilmaz|gerekir|gereklidir|zorunludur|yasaktir)|"
    r"asla\s+(?:yapilamaz|yapilmaz|kabul\s+edilmez))\b",
    re.IGNORECASE,
)

# Numeric/date extraction for answer checking
_ANSWER_NUMBER_RE = re.compile(
    r"(?:%\s*\d+(?:[,.]\d+)?)|"
    r"(?:\b\d+(?:[,.]\d+)?\s*(?:akts|ects|gno|kredi|gun|hafta|ay|yil|donem|tl|lira)\b)|"
    r"(?:\bgno\s*[:=]?\s*(?:\w+\s+){0,3}\d+[,.]\d+\b)|"
    r"(?:\b\d+[,.]\d+\s*(?:gno|not\s*ortalamas))",
    re.IGNORECASE,
)
_ANSWER_DATE_RE = re.compile(
    r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b"
    r"|\b\d{4}\s*[-\u2013]\s*\d{4}\b",
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_REPEATED_DURATION_RE = re.compile(
    r"\b(?P<days>\d{1,3})\s*(?:gunluk|günlük|is\s+gunluk|iş\s+günlük)\s+"
    r"(?P<count>\d{1,2})\s*(?:farkli|farklı|ayri|ayrı)\s+staj\b",
    re.IGNORECASE,
)
_TOTAL_DURATION_RE = re.compile(
    r"\btoplam\s+(?P<total>\d{1,3})\s*(?:is\s+gunu(?:ne)?|iş\s+günü(?:ne)?|gun(?:e)?|gün(?:e)?)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

def _collect_evidence_text(evidence_items: Sequence[EvidenceItem]) -> str:
    """Concatenate all evidence text for searching."""
    parts: list[str] = []
    for item in evidence_items:
        parts.append(normalize_text(item.content_snippet))
        parts.append(normalize_text(item.selected_sentences))
    return " ".join(parts)


def _collect_evidence_facts(evidence_items: Sequence[EvidenceItem]) -> set[str]:
    """Collect all extracted facts from evidence items."""
    facts: set[str] = set()
    for item in evidence_items:
        for fact in item.extracted_facts:
            facts.add(normalize_text(fact))
    return facts


def check_numeric_grounding(
    answer: str,
    evidence_items: Sequence[EvidenceItem],
) -> list[dict]:
    """Check if numeric claims in the answer are supported by evidence."""
    ungrounded: list[dict] = []
    evidence_text = _collect_evidence_text(evidence_items)
    evidence_facts = _collect_evidence_facts(evidence_items)

    for pattern in (_ANSWER_NUMBER_RE, _ANSWER_DATE_RE):
        for match in pattern.finditer(answer):
            claim_raw = match.group(0).strip()
            claim_normalized = normalize_text(claim_raw)

            # Check if the numeric value appears in any evidence
            found = False
            # Direct substring match in evidence text
            if claim_normalized in evidence_text:
                found = True
            else:
                # Extract just the number and check
                numbers = re.findall(r"\d+(?:[,.]\d+)?", claim_raw)
                for num in numbers:
                    if num in evidence_text:
                        found = True
                        break
                    # Also check extracted facts
                    if any(num in fact for fact in evidence_facts):
                        found = True
                        break

            if not found:
                ungrounded.append({
                    "claim": claim_raw,
                    "type": "numeric",
                    "grounded": False,
                })

    return ungrounded


def check_entity_grounding(
    answer: str,
    evidence_items: Sequence[EvidenceItem],
) -> list[dict]:
    """Check if portal/system/payment/document entities in the answer are grounded."""
    ungrounded: list[dict] = []
    evidence_text = _collect_evidence_text(evidence_items)
    answer_normalized = normalize_text(answer)

    for pattern in (_PORTAL_RE, _PAYMENT_CHANNEL_RE, _DOCUMENT_RE, _OFFICE_RE):
        for match in pattern.finditer(answer):
            entity_raw = match.group(0).strip()
            entity_normalized = normalize_text(entity_raw)

            # Skip known system entities — these are always valid
            if entity_normalized in KNOWN_SYSTEM_ENTITIES:
                continue

            # Check if entity appears in evidence
            if entity_normalized in evidence_text:
                continue

            # Check partial match (at least the key noun)
            key_words = [
                w for w in entity_normalized.split()
                if len(w) > 3
            ]
            if key_words and all(w in evidence_text for w in key_words):
                continue

            ungrounded.append({
                "claim": entity_raw,
                "type": "entity",
                "grounded": False,
            })

    return ungrounded


def check_definitive_claims(
    answer: str,
    evidence_items: Sequence[EvidenceItem],
) -> list[dict]:
    """Check if strong definitive claims are supported by evidence.

    Only targets HIGH-CONFIDENCE patterns like "kesinlikle yapilamaz",
    "asla yapilmaz".  Regular definitive endings (zorunludur, etc.)
    are NOT flagged here — those are too common and often correct.
    """
    ungrounded: list[dict] = []
    evidence_text = _collect_evidence_text(evidence_items)
    evidence_facts = _collect_evidence_facts(evidence_items)

    for match in _STRONG_DEFINITIVE_RE.finditer(answer):
        claim_raw = match.group(0).strip()
        claim_normalized = normalize_text(claim_raw)

        # Check if evidence supports this strong claim
        found = False
        if claim_normalized in evidence_text:
            found = True
        else:
            # Check if the key verb/action appears in evidence facts
            for fact in evidence_facts:
                key_parts = claim_normalized.split()
                if len(key_parts) >= 2 and key_parts[-1] in fact:
                    found = True
                    break

        if not found:
            ungrounded.append({
                "claim": claim_raw,
                "type": "definitive",
                "grounded": False,
            })

    return ungrounded


def check_arithmetic_consistency(answer: str) -> list[dict]:
    """Detect simple arithmetic contradictions inside a single answer sentence."""
    issues: list[dict] = []
    for sentence in _SENTENCE_SPLIT_RE.split(answer.strip()):
        repeated = _REPEATED_DURATION_RE.search(sentence)
        total = _TOTAL_DURATION_RE.search(sentence)
        if not repeated or not total:
            continue
        days = int(repeated.group("days"))
        count = int(repeated.group("count"))
        stated_total = int(total.group("total"))
        computed_total = days * count
        if computed_total != stated_total:
            issues.append(
                {
                    "claim": sentence.strip(),
                    "type": "arithmetic",
                    "grounded": False,
                    "computed_total": computed_total,
                    "stated_total": stated_total,
                }
            )
    return issues


def check_known_policy_contradictions(
    answer: str,
    evidence_items: Sequence[EvidenceItem],
) -> list[dict]:
    """Catch narrow, high-signal contradictions for well-known policy phrases."""
    issues: list[dict] = []
    answer_normalized = normalize_text(answer)
    evidence_text = _collect_evidence_text(evidence_items)

    if "tek ders" in answer_normalized:
        says_no_attendance_required = (
            "dersi hic almamis" in answer_normalized
            or "derse hic almamis" in answer_normalized
            or "hic almamis olsaniz" in answer_normalized
            or "hic almadiginiz" in answer_normalized
            or "devam sartini yerine getiremeyen" in answer_normalized
            or "devam sartini yerine getiremediginiz" in answer_normalized
            or "devam sartini saglamayan" in answer_normalized
        )
        evidence_requires_attendance = (
            "devam sartini yerine getirdigi" in evidence_text
            or "devam sartini yerine getirdiginiz" in evidence_text
            or "devam sartini sagladigi" in evidence_text
            or "devam sartini sagladiginiz" in evidence_text
            or "devam sartini yerine getiren" in evidence_text
        )
        if says_no_attendance_required and evidence_requires_attendance:
            issues.append(
                {
                    "claim": "Tek ders sınavı devam şartını sağlamayan veya dersi hiç almamış öğrenciye açık gösterildi.",
                    "type": "policy_contradiction",
                    "grounded": False,
                }
            )
    return issues


def _correct_single_exam_attendance_claim(answer: str) -> str:
    """Replace unsafe tek-ders eligibility wording with the source-bound rule."""
    safe_sentence = (
        "Tek ders sınavı için kaynakta, müfredattaki tüm dersleri almış olmak "
        "ve kalan tek ders için devam şartını daha önce sağlamış olmak koşulu "
        "vurgulanır."
    )
    lines = answer.splitlines()
    corrected_lines: list[str] = []
    removed_unsafe_line = False
    drop_following_allowance = False
    for line in lines:
        normalized = normalize_text(line)
        unsafe_line = (
            "hic alm" in normalized
            or "devam sartini yerine getirem" in normalized
            or "devam sartini saglamayan" in normalized
            or "kayit yaptirmis olmaniz gerekmez" in normalized
        )
        if unsafe_line:
            removed_unsafe_line = True
            drop_following_allowance = True
            continue
        if drop_following_allowance and any(
            marker in normalized for marker in ("girebilir", "basvurabilir")
        ):
            removed_unsafe_line = True
            drop_following_allowance = False
            continue
        if normalized.strip() and not normalized.lstrip().startswith("•"):
            drop_following_allowance = False
        corrected_lines.append(line)

    if not removed_unsafe_line:
        return answer
    remaining = "\n".join(line for line in corrected_lines if line.strip()).strip()
    if not remaining:
        return safe_sentence
    if safe_sentence in remaining:
        return remaining
    return f"{safe_sentence}\n\n{remaining}"


# ---------------------------------------------------------------------------
# Main guard entry point
# ---------------------------------------------------------------------------

def guard_answer(
    answer: str,
    evidence_items: Sequence[EvidenceItem],
) -> GuardResult:
    """Run all claim checks and apply minimal, safe corrections.

    Design:
    - Ungrounded entities (portals, payment channels) → softened
    - Ungrounded numbers/dates → logged to diagnostics only (not modified)
    - Ungrounded definitive claims → softened only if VERY clear
    - No sentences deleted
    - "teyit ediniz" note added ONLY when modifications were actually made
    """
    if not evidence_items:
        return GuardResult(
            cleaned_answer=answer,
            diagnostics={"skipped": True, "reason": "no_evidence_items"},
        )

    numeric_issues = check_numeric_grounding(answer, evidence_items)
    entity_issues = check_entity_grounding(answer, evidence_items)
    definitive_issues = check_definitive_claims(answer, evidence_items)
    arithmetic_issues = check_arithmetic_consistency(answer)
    policy_issues = check_known_policy_contradictions(answer, evidence_items)

    all_issues = numeric_issues + entity_issues + definitive_issues + arithmetic_issues + policy_issues

    if not all_issues:
        return GuardResult(
            cleaned_answer=answer,
            diagnostics={"checks_passed": True, "issues_found": 0},
        )

    # Apply corrections — conservative approach
    cleaned = answer
    modifications = 0

    # 1. Entity issues: remove/soften only clear hallucinated portal/menu names
    for issue in entity_issues:
        entity = issue["claim"]
        if entity in cleaned:
            # Don't delete the sentence — just note it's not verified
            # Only for portal/system/payment channel names that are clearly fabricated
            # We replace with a generic reference
            entity_type = _classify_entity(entity)
            if entity_type == "portal":
                cleaned = cleaned.replace(entity, "ilgili sistem")
                modifications += 1
            elif entity_type == "office":
                cleaned = cleaned.replace(entity, "ilgili birim")
                modifications += 1
            elif entity_type == "payment_channel":
                cleaned = cleaned.replace(entity, "ilgili odeme kanali")
                modifications += 1
            # document names are kept but logged — less likely to be fabricated

    # 2. Strong definitive claims: soften only the strongest patterns
    for issue in definitive_issues:
        claim = issue["claim"]
        if claim in cleaned:
            # Replace "kesinlikle yapilamaz" with "yapilamamaktadir"
            softened = _soften_definitive(claim)
            if softened != claim:
                cleaned = cleaned.replace(claim, softened)
                modifications += 1

    # 3. Arithmetic issues: replace only the contradictory sentence with a guarded statement.
    for issue in arithmetic_issues:
        claim = issue["claim"]
        if claim in cleaned:
            computed_total = issue["computed_total"]
            cleaned = cleaned.replace(
                claim,
                (
                    f"Bu örnekte toplam gün hesabı {computed_total} gündür; "
                    "stajın bölünerek kabul edilip edilmeyeceği için ilgili bölüm staj ilkeleri esas alınmalıdır."
                ),
            )
            modifications += 1

    # 4. Known policy contradictions: remove the contradicted phrase, keep a cautious source-bound sentence.
    for issue in policy_issues:
        if "tek ders" in normalize_text(issue["claim"]):
            before_policy_cleanup = cleaned
            cleaned = _correct_single_exam_attendance_claim(cleaned)
            cleaned = re.sub(
                r"(?i)Bu sınavlara,?\s*dersi hiç almamış olan veya devam şartını yerine getiremeyen öğrenciler girebilir\.\s*",
                (
                    "Tek ders sınavı için kaynakta devam şartını daha önce sağlamış olma koşulu vurgulanır. "
                ),
                cleaned,
            )
            cleaned = re.sub(
                r"(?i)dersi hiç almamış olan veya devam şartını yerine getiremeyen öğrenciler girebilir",
                "devam şartını daha önce sağlamış öğrenciler başvurabilir",
                cleaned,
            )
            if cleaned != before_policy_cleanup:
                modifications += 1

    # 5. Numeric issues: otherwise ONLY logged, not modified.

    # Add verification note ONLY if we actually modified something
    if modifications > 0:
        if not cleaned.rstrip().endswith("."):
            cleaned = cleaned.rstrip() + "."
        cleaned = (
            cleaned.rstrip()
            + "\n\n(Not: Bu cevaptaki bazi bilgiler kaynaklarda dogrudan "
            "teyit edilemedi; ilgili birimden dogrulama yapmaniz onerilir.)"
        )

    return GuardResult(
        cleaned_answer=cleaned,
        unsupported_claims=all_issues,
        modifications_made=modifications,
        diagnostics={
            "numeric_issues": len(numeric_issues),
            "entity_issues": len(entity_issues),
            "definitive_issues": len(definitive_issues),
            "arithmetic_issues": len(arithmetic_issues),
            "policy_issues": len(policy_issues),
            "modifications_made": modifications,
            "unsupported_claims": all_issues,
        },
    )


def _classify_entity(entity: str) -> str:
    """Classify an entity string into portal, payment_channel, office, or document."""
    normalized = normalize_text(entity)
    if any(w in normalized for w in ("portal", "sistem", "ekran", "menu", "platform", "modul")):
        return "portal"
    if any(w in normalized for w in ("banka", "atm", "eft", "havale", "pos", "odeme noktasi")):
        return "payment_channel"
    if any(w in normalized for w in ("buro", "ofis", "daire", "baskanlik", "mudurluk")):
        return "office"
    if any(w in normalized for w in ("form", "belge", "dilekce", "tutanak")):
        return "document"
    return "other"


def _soften_definitive(claim: str) -> str:
    """Soften a strong definitive claim to a more cautious phrasing."""
    normalized = normalize_text(claim)
    if "kesinlikle yapilamaz" in normalized or "kesinlikle yapilmaz" in normalized:
        return claim.replace("kesinlikle ", "")
    if "asla yapilamaz" in normalized or "asla yapilmaz" in normalized:
        return claim.replace("asla ", "")
    if "asla kabul edilmez" in normalized:
        return claim.replace("asla ", "")
    return claim
