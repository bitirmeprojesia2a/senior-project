"""Retriever aday listeleri icin yardimci fonksiyonlar."""

from typing import Any, Dict, Iterable, List

from langchain_core.documents import Document


def sort_candidates_by_score(candidates: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Adaylari mevcut skorlarina gore yuksekten dusuge siralar."""
    return sorted(candidates, key=lambda item: item.get("score", 0.0), reverse=True)


def deduplicate_documents(raw_docs: List[Document]) -> List[Dict[str, Any]]:
    """Ayni icerige sahip Document adaylarini tekillestirir."""
    candidates: List[Dict[str, Any]] = []
    seen_contents: Dict[str, int] = {}

    for doc in raw_docs:
        content = doc.page_content
        content_key = content[:200]
        sim_score = doc.metadata.get("similarity_score", 0.0)

        if content_key in seen_contents:
            idx = seen_contents[content_key]
            if sim_score > candidates[idx]["score"]:
                candidates[idx]["score"] = sim_score
            continue

        seen_contents[content_key] = len(candidates)
        candidates.append(
            {
                "content": content,
                "source": doc.metadata.get("source", "bilinmiyor"),
                "category": doc.metadata.get("category", "genel"),
                "score": sim_score,
                "metadata": dict(doc.metadata),
            }
        )

    return candidates


def deduplicate_candidate_dicts(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ayni icerige sahip dict tabanli adaylari tekillestirir."""
    deduplicated: List[Dict[str, Any]] = []
    seen_contents: Dict[str, int] = {}

    for candidate in candidates:
        content = candidate.get("content", "")
        content_key = content[:200]
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
                "metadata": dict(candidate.get("metadata") or {}),
            }
        )

    return deduplicated
