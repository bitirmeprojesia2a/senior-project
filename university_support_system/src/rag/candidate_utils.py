"""Retriever aday listeleri icin yardimci fonksiyonlar."""

import re
from typing import Any, Dict, Iterable, List

from langchain_core.documents import Document

_SUB_CHUNK_RE = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s*$")
_BRACKETED_MADDE_HEADER_RE = re.compile(r"^\[(MADDE|Madde)[^\]]+\]\s*", re.DOTALL)
_MIN_OVERLAP_CHARS = 24
_MAX_OVERLAP_SCAN = 256


def sort_candidates_by_score(candidates: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Adaylari mevcut skorlarina gore yuksekten dusuge siralar."""
    return sorted(candidates, key=lambda item: item.get("score", 0.0), reverse=True)


def _candidate_dedup_key(content: str, metadata: Dict[str, Any]) -> str:
    """Build a stable dedup key that preserves distinct chunks from the same source."""
    source = (
        str(metadata.get("source") or "")
        or str(metadata.get("file_name") or "")
        or str(metadata.get("source_url") or "")
    )
    chunk_index = metadata.get("chunk_index")
    sub_chunk = metadata.get("sub_chunk")
    madde_no = metadata.get("madde_no")

    if metadata.get("context_expanded") and source and madde_no is not None:
        return f"{source}::{madde_no}::expanded"

    if any(value is not None and str(value) != "" for value in (chunk_index, sub_chunk, madde_no)):
        return f"{source}::{madde_no}::{chunk_index}::{sub_chunk}"

    return f"{source}::{content[:200]}"


def parse_sub_chunk_position(value: Any) -> tuple[int, int] | None:
    """'2/4' gibi alt parca konumunu sayisal ikiliye cevirir."""
    if not value:
        return None

    match = _SUB_CHUNK_RE.match(str(value))
    if not match:
        return None

    current = int(match.group(1))
    total = int(match.group(2))
    if current < 1 or total < 1 or current > total:
        return None
    return current, total


def merge_chunk_texts(chunks: Iterable[str]) -> str:
    """Ayni maddeye ait alt chunk'lari tekrarli kisimlari temizleyerek birlestirir."""
    merged = ""
    for index, raw_chunk in enumerate(chunks):
        piece = str(raw_chunk or "").strip()
        if not piece:
            continue

        if index > 0:
            piece = _BRACKETED_MADDE_HEADER_RE.sub("", piece, count=1).lstrip()

        if not merged:
            merged = piece
            continue

        if piece in merged:
            continue

        max_overlap = min(len(merged), len(piece), _MAX_OVERLAP_SCAN)
        overlap_found = False
        for size in range(max_overlap, _MIN_OVERLAP_CHARS - 1, -1):
            if merged.endswith(piece[:size]):
                merged = f"{merged}{piece[size:]}"
                overlap_found = True
                break

        if overlap_found:
            continue

        merged = f"{merged.rstrip()}\n{piece.lstrip()}"

    return merged


def deduplicate_documents(raw_docs: List[Document]) -> List[Dict[str, Any]]:
    """Ayni icerige sahip Document adaylarini tekillestirir."""
    candidates: List[Dict[str, Any]] = []
    seen_contents: Dict[str, int] = {}

    for doc in raw_docs:
        content = doc.page_content
        metadata = dict(doc.metadata)
        content_key = _candidate_dedup_key(content, metadata)
        sim_score = float(metadata.get("similarity_score", 0.0))
        metadata.setdefault(
            "score_type",
            "semantic_similarity" if "similarity_score" in metadata else "retrieval",
        )
        metadata.setdefault("retrieval_score", round(sim_score, 4))

        if content_key in seen_contents:
            idx = seen_contents[content_key]
            if sim_score > candidates[idx]["score"]:
                candidates[idx]["score"] = sim_score
                candidates[idx]["metadata"] = metadata
            continue

        seen_contents[content_key] = len(candidates)
        candidates.append(
            {
                "content": content,
                "source": metadata.get("source", "bilinmiyor"),
                "category": metadata.get("category", "genel"),
                "score": sim_score,
                "metadata": metadata,
            }
        )

    return candidates


def deduplicate_candidate_dicts(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ayni icerige sahip dict tabanli adaylari tekillestirir."""
    deduplicated: List[Dict[str, Any]] = []
    seen_contents: Dict[str, int] = {}

    for candidate in candidates:
        content = candidate.get("content", "")
        metadata = dict(candidate.get("metadata") or {})
        content_key = _candidate_dedup_key(content, metadata)
        score = float(candidate.get("score", 0.0))

        if content_key in seen_contents:
            idx = seen_contents[content_key]
            if score > float(deduplicated[idx].get("score", 0.0)):
                deduplicated[idx]["score"] = score
                deduplicated[idx]["source"] = candidate.get(
                    "source",
                    deduplicated[idx].get("source", "bilinmiyor"),
                )
                deduplicated[idx]["category"] = candidate.get(
                    "category",
                    deduplicated[idx].get("category", "genel"),
                )
                deduplicated[idx]["metadata"] = dict(
                    candidate.get("metadata") or deduplicated[idx].get("metadata") or {}
                )
            continue

        seen_contents[content_key] = len(deduplicated)
        deduplicated.append(
            {
                "content": content,
                "source": candidate.get("source", "bilinmiyor"),
                "category": candidate.get("category", "genel"),
                "score": score,
                "metadata": metadata,
            }
        )

    return deduplicated
