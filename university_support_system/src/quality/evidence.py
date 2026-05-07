"""Structured evidence extraction and topic coherence utilities.

This module provides the EvidenceItem model and deterministic extraction
pipeline for converting raw RAG results into structured, scored evidence
for LLM synthesis.  It is intentionally free of imports from
``src.agents.base`` to avoid circular dependencies.

Shared constants (stopwords, sentence regex, thresholds) are defined
here so that both ``src.agents.base`` and ``src.orchestrators.*`` can
import them cleanly.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Sequence

from src.core.text_normalization import normalize_text

# ---------------------------------------------------------------------------
# Shared constants (imported by base.py and synthesis_utils.py)
# ---------------------------------------------------------------------------

EVIDENCE_SENTENCE_RE = re.compile(r"(?<=[\.\?\!])\s+|\n+")

EVIDENCE_STOPWORDS: frozenset[str] = frozenset({
    "bir", "bu", "su", "o", "ve", "ile", "icin", "ne", "mi", "mu",
    "da", "de", "nasil", "nedir", "var", "yok", "hangi", "kac",
    "olarak", "olan", "olur", "gerekir", "gereken", "dair", "ilgili",
    "ogrenci", "universite", "soru", "cevap", "bilgi",
})

_CAPACITY_QUERY_TERMS: frozenset[str] = frozenset({
    "kapasite", "kapasiteleri", "kontenjan", "kontenjanlari",
    "sinif", "mevcut", "mevcudu", "sube", "subeler", "kisi",
    "ogrenci", "sayisi", "acilabilmesi", "bolunebilir", "belirlenir",
})

EVIDENCE_MAX_SENTENCES = 7
EVIDENCE_MIN_SCORE = 0.35

# Specificity patterns for scoring sentences
_SPECIFICITY_RE = re.compile(
    r"\b(?:madde|fikra|bent|oran|yuzde|akts|gno|not|tarih|sure"
    r"|kontenjan|ogrenci\s+sayisi|kisi|sube)\b",
)
_NUMERIC_RE = re.compile(r"(?:%|\b\d+(?:[,.]\d+)?\b)")
_NUMERIC_RANGE_RE = re.compile(
    r"\b\d+(?:[,.]\d+)?\s*"
    r"(?:[-\u2013]\s*\d+(?:[,.]\d+)?"
    r"|(?:ve\s+)?(?:uzeri|uzerinde|ustu|ustunde|alti|altinda)"
    r"|(?:arasi|arasinda))\b",
    re.IGNORECASE,
)
_RANGE_BLOCK_QUERY_TERMS: frozenset[str] = frozenset({
    "akts", "ects", "gano", "gno", "kredi", "not", "ortalama",
    "puan", "oran", "yuzde", "ucret", "tl", "tutar",
})
_RANGE_BLOCK_CONTENT_TERMS: frozenset[str] = frozenset({
    "akts", "ects", "gano", "gno", "kredi", "not", "ortalama",
    "puan", "oran", "yuzde", "ucret", "tl", "tutar", "ogrenci",
})

# Factual claim extraction patterns
_PERCENTAGE_RE = re.compile(
    r"(?:%\s*\d+(?:[,.]\d+)?|\byuzde\s+\d+(?:[,.]\d+)?)",
)
_DATE_RE = re.compile(
    r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b"
    r"|\b\d{4}\s*[-\u2013]\s*\d{4}\b",
)
_ACADEMIC_TERM_RE = re.compile(
    r"\b(?:guz|bahar|yaz)\s+(?:donemi|yariyili)\b",
)
_NUMERIC_FACT_RE = re.compile(
    r"\b\d+(?:[,.]\d+)?\s*"
    r"(?:akts|ects|gno|kredi|gun|hafta|ay|yil|donem|tl|lira|kisi\w*|ogrenci\w*|sube\w*)\b",
    re.IGNORECASE,
)
_GNO_RE = re.compile(
    r"\b(?:gno|genel\s*not\s*ortalamas[iı])\s*[:=]?\s*(?:\w+\s+){0,3}\d+[,.]\d+\b",
    re.IGNORECASE,
)
_CONDITION_TAIL_RE = re.compile(
    r"\b(zorunludur|yapilamaz|yapilamayacaktir|yapilmaz"
    r"|gerekir|gereklidir|yapilabilir|odenir|odenmez"
    r"|muaf|muaftir|kesilir|kesilmez|ekleme yapilamaz"
    r"|kabul edilmez|kabul edilir|verilir|verilmez"
    r"|iptal edilir|gecersiz sayilir|bolunebilir|belirlenir)\b",
)

# Reference pronouns that signal context window should expand
_REFERENCE_WORDS = frozenset({
    "bu", "bunun", "bunu", "bunlar", "bunlarin",
    "soz konusu", "yukaridaki", "asagidaki",
    "o", "onun", "onu",
})

# Known system/portal names for entity grounding
KNOWN_SYSTEM_ENTITIES: frozenset[str] = frozenset({
    "ubys", "obs", "ubys.omu.edu.tr",
    "ogrenci bilgi sistemi", "ogrenci bilgi yonetim sistemi",
    "e-devlet", "kyk", "turkiye burs",
})


def _query_needs_numeric_range_block(normalized_query: str) -> bool:
    """Return true when the user is asking about a numeric bracket/table."""
    if not any(term in normalized_query for term in _RANGE_BLOCK_QUERY_TERMS):
        return False
    return bool(
        _NUMERIC_RE.search(normalized_query)
        or "kac" in normalized_query
        or "hangi" in normalized_query
    )


def _looks_like_numeric_range_part(part: str) -> bool:
    normalized_part = normalize_text(part)
    if not _NUMERIC_RANGE_RE.search(normalized_part):
        return False
    return any(term in normalized_part for term in _RANGE_BLOCK_CONTENT_TERMS)


def _numeric_range_context_indices(parts: Sequence[str], selected_indices: set[int]) -> set[int]:
    """Keep adjacent rows of a numeric range list together.

    Range tables in PDFs are often split by line breaks. If only the first
    matching line reaches the prompt, the LLM sees values such as 6/10/12/15
    without the full bracket mapping. This helper preserves the local list as
    one evidence unit without changing retrieval or routing.
    """
    range_indices = {
        index
        for index, part in enumerate(parts)
        if _looks_like_numeric_range_part(part)
    }
    if len(range_indices) < 2:
        return set()
    if not selected_indices & range_indices:
        return set()

    expanded = set(range_indices)
    for index in range_indices:
        if index > 0:
            previous = normalize_text(parts[index - 1])
            if any(term in previous for term in _RANGE_BLOCK_CONTENT_TERMS):
                expanded.add(index - 1)
        if index + 1 < len(parts):
            following = normalize_text(parts[index + 1])
            if (
                any(term in following for term in _RANGE_BLOCK_CONTENT_TERMS)
                or _CONDITION_TAIL_RE.search(following)
            ):
                expanded.add(index + 1)
    return expanded


def _expand_query_terms_for_evidence(query_terms: set[str], normalized_query: str) -> set[str]:
    """Add deterministic concept aliases used in policy documents."""
    expanded = set(query_terms)
    if expanded & _CAPACITY_QUERY_TERMS or "ogrenci sayisi" in normalized_query:
        expanded.update(_CAPACITY_QUERY_TERMS)
        expanded.update({
            "yaz", "okulu", "dersin", "ders", "acilabilmesi",
            "bolunebilir", "bolunur", "belirlenir", "mevcut",
        })
    return expanded


# ---------------------------------------------------------------------------
# EvidenceItem data model
# ---------------------------------------------------------------------------

@dataclass
class EvidenceItem:
    """Structured representation of a single RAG source with annotations."""

    source_name: str
    source_id: str
    department: str
    score: float
    score_type: str
    content_snippet: str
    selected_sentences: str
    matched_query_terms: list[str]
    relevance_score: float
    extracted_facts: list[str]
    supported_aspects: list[str] = field(default_factory=list)
    is_low_confidence: bool = False
    is_potentially_off_topic: bool = False
    source_rank: int = 0

    def to_diagnostics_dict(self) -> dict:
        """JSON-serializable diagnostics representation."""
        return {
            "source_name": self.source_name,
            "source_id": self.source_id,
            "department": self.department,
            "score": round(self.score, 4),
            "score_type": self.score_type,
            "relevance_score": round(self.relevance_score, 4),
            "matched_query_terms": self.matched_query_terms,
            "extracted_facts": self.extracted_facts,
            "supported_aspects": self.supported_aspects,
            "is_low_confidence": self.is_low_confidence,
            "is_potentially_off_topic": self.is_potentially_off_topic,
            "source_rank": self.source_rank,
        }


# ---------------------------------------------------------------------------
# Core extraction functions
# ---------------------------------------------------------------------------

def _stable_source_id(source_name: str, content: str) -> str:
    """Deterministic hash for deduplication (cross-process stable)."""
    raw = f"{source_name}|{content[:200]}"
    return hashlib.sha1(raw.encode("utf-8", errors="replace")).hexdigest()[:12]


def _source_identity(metadata: dict | None, source_name: str) -> str:
    """Prefer path-level identity when available, while keeping display names separate."""
    metadata = metadata or {}
    return str(
        metadata.get("relative_path")
        or metadata.get("file_path")
        or metadata.get("source_url")
        or source_name
    )


def extract_factual_claims(text: str) -> list[str]:
    """Extract verifiable factual claims (numbers, dates, conditions) from text."""
    normalized = normalize_text(text)
    facts: list[str] = []
    seen: set[str] = set()

    for pattern in (
        _PERCENTAGE_RE, _DATE_RE, _ACADEMIC_TERM_RE,
        _NUMERIC_FACT_RE, _GNO_RE,
    ):
        for match in pattern.finditer(normalized):
            value = match.group(0).strip()
            if value and value not in seen:
                facts.append(value)
                seen.add(value)

    for match in _CONDITION_TAIL_RE.finditer(normalized):
        # Capture the sentence fragment ending with the condition word
        start = max(0, match.start() - 60)
        fragment = normalized[start:match.end()].strip()
        # Take from last sentence boundary
        for sep in (".", "?", "!"):
            idx = fragment.rfind(sep)
            if idx >= 0:
                fragment = fragment[idx + 1:].strip()
                break
        if fragment and fragment not in seen:
            facts.append(fragment)
            seen.add(fragment)

    return facts


def _detect_supported_aspects(
    query_terms: set[str],
    content_normalized: str,
) -> list[str]:
    """Detect which question aspects a source covers."""
    aspects: list[str] = []
    aspect_definitions = (
        ("timing", ("ne zaman", "tarih", "takvim", "son basvuru", "donem")),
        ("condition", ("kosul", "sart", "gerekli", "kriter", "ortalama")),
        ("fee", ("ucret", "harc", "odeme", "katki payi", "tl")),
        ("document", ("belge", "evrak", "form", "dokuman")),
        ("process", ("nasil", "surec", "basvuru", "adim", "islem")),
        ("capacity", ("kapasite", "kontenjan", "ogrenci sayisi", "kisi", "sube", "mevcut", "bolunebilir", "acilabilmesi")),
    )
    for aspect_name, markers in aspect_definitions:
        if any(m in content_normalized for m in markers):
            aspects.append(aspect_name)
    return aspects


def compute_topic_coherence(
    query_terms: set[str],
    source_content: str,
    source_metadata: dict | None = None,
    *,
    expected_department: str = "",
    source_score: float = 0.0,
    score_type: str = "retrieval",
) -> float:
    """Compute topic coherence between query and source — 100% deterministic.

    Uses term overlap, metadata/department match, and retriever score.
    No LLM or embedding calls.
    """
    if not query_terms:
        return 0.0

    content_normalized = normalize_text(source_content[:600])
    content_terms = {
        t for t in content_normalized.split()
        if len(t) > 2 and t not in EVIDENCE_STOPWORDS
    }

    # Base: term overlap
    intersection = query_terms & content_terms
    base_score = len(intersection) / max(len(query_terms), 1)

    # Department match bonus
    dept_bonus = 0.0
    if expected_department and source_metadata:
        source_dept = normalize_text(
            source_metadata.get("department", "")
            or source_metadata.get("collection", "")
        )
        if expected_department in source_dept or source_dept in expected_department:
            dept_bonus = 0.10

    # Reranker trust bonus: if reranker gave high score, trust it
    reranker_bonus = 0.0
    if score_type == "reranker" and source_score >= 0.60:
        reranker_bonus = 0.15
    elif score_type == "reranker" and source_score >= 0.50:
        reranker_bonus = 0.08

    # Fact overlap: if source has facts relevant to query domain
    fact_bonus = 0.0
    source_facts = extract_factual_claims(source_content[:500])
    if source_facts:
        fact_bonus = 0.05

    coherence = min(base_score + dept_bonus + reranker_bonus + fact_bonus, 1.0)
    return round(coherence, 4)


def select_evidence_sentences(
    query_text: str,
    content: str,
    *,
    max_sentences: int = EVIDENCE_MAX_SENTENCES,
    min_score: float = EVIDENCE_MIN_SCORE,
) -> str:
    """Select the most query-relevant sentences from content.

    Enhanced version of the extraction logic previously in
    ``BaseSpecialistAgent._extract_evidence_content``.
    Improvements:
    - Context window: keeps neighbor sentence if it has references
    - Heading preservation: numbered list items keep their heading
    - Stronger numeric/date bonus
    - Position bonus for first sentence
    - Fallback to first 2 sentences if nothing scores high enough
    """
    normalized_query = normalize_text(query_text)
    query_terms = {
        token
        for token in normalized_query.split()
        if len(token) > 2 and token not in EVIDENCE_STOPWORDS
    }
    query_terms = _expand_query_terms_for_evidence(query_terms, normalized_query)
    if not query_terms:
        return content

    parts = [
        part.strip()
        for part in EVIDENCE_SENTENCE_RE.split(content)
        if part and part.strip()
    ]
    if len(parts) <= max_sentences:
        return content

    scored: list[tuple[float, int, str]] = []
    for index, part in enumerate(parts):
        normalized_part = normalize_text(part)
        part_terms = {
            token
            for token in normalized_part.split()
            if len(token) > 2 and token not in EVIDENCE_STOPWORDS
        }
        if not part_terms:
            continue
        overlap = len(query_terms & part_terms) / max(len(query_terms), 1)

        specificity_bonus = 0.0
        if _SPECIFICITY_RE.search(normalized_part):
            specificity_bonus += 0.22
        if _NUMERIC_RE.search(part):
            specificity_bonus += 0.22
        if any(term in normalized_part for term in query_terms):
            specificity_bonus += 0.08

        # Position bonus: first sentence often has core definition
        if index == 0:
            specificity_bonus += 0.05

        score = overlap + specificity_bonus
        if score >= min_score:
            scored.append((score, index, part))

    if not scored:
        # Keep a small fallback instead of passing the whole chunk. Full-content
        # fallback lets unrelated page boilerplate leak into the LLM context.
        return " ".join(parts[: min(2, max_sentences)]).strip() or content

    scored.sort(key=lambda item: (-item[0], item[1]))
    selected_indices: set[int] = set()
    for _score, idx, _part in scored[:max_sentences]:
        selected_indices.add(idx)

        # Context window: include neighbor if it has a reference word
        if idx + 1 < len(parts):
            neighbor_normalized = normalize_text(parts[idx + 1])
            neighbor_tokens = set(neighbor_normalized.split()[:4])
            if neighbor_tokens & _REFERENCE_WORDS:
                selected_indices.add(idx + 1)

        # Heading preservation: if part starts with numbered item,
        # include preceding line that might be the heading
        if idx > 0 and re.match(r"^\s*\d+[.\)]\s", parts[idx]):
            prev_normalized = normalize_text(parts[idx - 1])
            # Preceding short line is likely a heading
            if len(prev_normalized.split()) <= 8:
                selected_indices.add(idx - 1)

    if _query_needs_numeric_range_block(normalized_query):
        selected_indices.update(
            _numeric_range_context_indices(parts, selected_indices),
        )

    # Respect max_sentences limit even with context additions
    ordered_indices = sorted(selected_indices)[:max_sentences + 2]
    excerpt = " ".join(parts[i] for i in ordered_indices).strip()
    return excerpt or content


def extract_evidence_items(
    query: str,
    results: Sequence[dict],
    department: str,
    *,
    analysis_query: str | None = None,
    low_confidence_reranker_threshold: float = 0.35,
    low_confidence_retrieval_threshold: float = 0.15,
    off_topic_coherence_threshold: float = 0.15,
) -> list[EvidenceItem]:
    """Convert raw RAG result dicts to a list of EvidenceItem.

    Parameters
    ----------
    query : str
        The user question.
    results : list[dict]
        RAG results with keys: content, source, score, metadata.
    department : str
        Expected department identifier.

    Returns
    -------
    list[EvidenceItem]
        Sorted by relevance_score descending.
    """
    effective_query = analysis_query or query
    normalized_query = normalize_text(effective_query)
    query_terms = {
        t for t in normalized_query.split()
        if len(t) > 2 and t not in EVIDENCE_STOPWORDS
    }
    query_terms = _expand_query_terms_for_evidence(query_terms, normalized_query)

    items: list[EvidenceItem] = []
    for index, result in enumerate(results):
        raw_content = str(result.get("content", ""))
        source_name = str(result.get("source", "bilinmiyor"))
        score = float(result.get("score", 0.0))
        metadata = result.get("metadata") or {}
        score_type = str(metadata.get("score_type", "retrieval")).strip().lower()

        source_id = _stable_source_id(_source_identity(metadata, source_name), raw_content)

        # Match query terms
        content_normalized = normalize_text(raw_content[:600])
        content_terms = {
            t for t in content_normalized.split()
            if len(t) > 2 and t not in EVIDENCE_STOPWORDS
        }
        matched = sorted(query_terms & content_terms)

        # Topic coherence
        relevance = compute_topic_coherence(
            query_terms,
            raw_content,
            metadata,
            expected_department=department,
            source_score=score,
            score_type=score_type,
        )

        # Select sentences
        selected = select_evidence_sentences(effective_query, raw_content)

        # Extract facts
        facts = extract_factual_claims(raw_content)

        # Aspects
        aspects = _detect_supported_aspects(query_terms, content_normalized)

        # Low confidence
        if score_type == "reranker":
            is_low = score < low_confidence_reranker_threshold
        else:
            is_low = score < low_confidence_retrieval_threshold

        # Off-topic: use BASE term overlap (without reranker/dept bonuses)
        # to avoid high reranker score masking zero-overlap sources.
        base_overlap = len(matched) / max(len(query_terms), 1)
        is_off_topic = (
            score >= 0.50
            and base_overlap < off_topic_coherence_threshold
            and len(matched) == 0
        )

        items.append(EvidenceItem(
            source_name=source_name,
            source_id=source_id,
            department=department,
            score=score,
            score_type=score_type,
            content_snippet=raw_content,
            selected_sentences=selected,
            matched_query_terms=matched,
            relevance_score=relevance,
            extracted_facts=facts,
            supported_aspects=aspects,
            is_low_confidence=is_low,
            is_potentially_off_topic=is_off_topic,
            source_rank=index,
        ))

    # Sort by relevance descending
    items.sort(key=lambda item: (-item.relevance_score, item.source_rank))
    return items


def build_evidence_context_chunks(
    evidence_items: list[EvidenceItem],
    query: str,
    *,
    max_items: int = 5,
    max_content_len: int = 2000,
) -> list[str]:
    """Build annotated context chunks for LLM prompt from evidence items.

    Off-topic items are excluded ONLY when enough safe items exist;
    otherwise they are included as low-confidence fallback.
    """
    safe_items = [e for e in evidence_items if not e.is_potentially_off_topic]
    strong_safe_items = [e for e in safe_items if not e.is_low_confidence]
    off_topic_items = [e for e in evidence_items if e.is_potentially_off_topic]

    # Prefer strong safe evidence. Low-confidence chunks are used only as a
    # fallback so the LLM does not anchor on weakly related FAQ/page fragments.
    if len(strong_safe_items) >= 2:
        selected = strong_safe_items[:max_items]
    elif strong_safe_items:
        selected = strong_safe_items + [
            item for item in safe_items if item.is_low_confidence
        ][:max_items - len(strong_safe_items)]
        if len(selected) < max_items:
            selected += off_topic_items[:max_items - len(selected)]
    # If enough safe evidence, use only safe items
    elif len(safe_items) >= 2:
        selected = safe_items[:max_items]
    elif safe_items:
        # Few safe items: supplement with off-topic as fallback
        selected = safe_items + off_topic_items[:max_items - len(safe_items)]
    else:
        # All off-topic: use them but the caller should consider a
        # "kaynaklarda net bilgi yok" fallback
        selected = off_topic_items[:max_items]

    chunks: list[str] = []
    for index, item in enumerate(selected, start=1):
        header = f"Belge parcasi {index} ({item.source_name}):"

        # Use selected sentences, compact to max length
        body = item.selected_sentences
        if len(body) > max_content_len:
            body = body[:max_content_len - 3].rstrip() + "..."

        # Append extracted facts if any
        facts_section = ""
        if item.extracted_facts:
            facts_str = "; ".join(item.extracted_facts[:8])
            facts_section = f"\nOnemli bilgiler: {facts_str}"

        chunks.append(f"{header}\n{body}{facts_section}")

    return chunks


def all_evidence_off_topic(evidence_items: list[EvidenceItem]) -> bool:
    """Check if ALL evidence items are off-topic or low confidence.

    When true, the caller should consider falling back to a
    'kaynaklarda net bilgi bulunamadi' response instead of risking
    hallucination.
    """
    if not evidence_items:
        return True
    # If any item has a strong reranker score, the retriever found
    # semantic relevance — trust it even if term overlap is low.
    has_retriever_confidence = any(
        item.score >= 0.45
        and item.score_type == "reranker"
        and not item.is_low_confidence
        and not item.is_potentially_off_topic
        for item in evidence_items
    )
    if has_retriever_confidence:
        return False
    return all(
        item.is_potentially_off_topic or item.is_low_confidence
        for item in evidence_items
    )


def build_evidence_diagnostics(evidence_items: list[EvidenceItem]) -> dict:
    """Build a diagnostics summary dict for profiler attributes."""
    safe = [e for e in evidence_items if not e.is_potentially_off_topic]
    off_topic = [e for e in evidence_items if e.is_potentially_off_topic]
    all_facts: list[str] = []
    for item in evidence_items:
        all_facts.extend(item.extracted_facts)

    return {
        "evidence_item_count": len(evidence_items),
        "sources_in_context": len(safe),
        "sources_off_topic": len(off_topic),
        "facts_extracted": len(set(all_facts)),
        "items": [item.to_diagnostics_dict() for item in evidence_items],
    }
