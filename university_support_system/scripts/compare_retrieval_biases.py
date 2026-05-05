"""Compare retrieval ranking with and without heuristic score shaping.

This script is intentionally retrieval-only: it does not call final answer LLMs.
It helps inspect whether source penalties / boosts improve or hurt the top
RAG evidence returned to specialist agents.

Usage:
    python -m scripts.compare_retrieval_biases --limit 12
    python -m scripts.compare_retrieval_biases --queries custom --top-k 5
"""

from __future__ import annotations

import argparse
import json
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from src.core.config import settings
from src.core.constants import Department
from src.rag.retriever import HybridRetriever


@dataclass(frozen=True)
class QueryCase:
    query: str
    department: Department | None = None
    note: str = ""


CUSTOM_CASES: list[QueryCase] = [
    QueryCase("Önlisans öğrencisiyim ÇAP'a başvurabilir miyim?", Department.ACADEMIC_PROGRAMS, "CAP / onlisans"),
    QueryCase("Yaz okulunda sınıf kapasitesi kaç kişi olur?", Department.STUDENT_AFFAIRS, "yaz okulu kapasite"),
    QueryCase("Öğrenci kimlik kartım kayıp ne yapacağım?", Department.STUDENT_AFFAIRS, "kimlik karti"),
    QueryCase("ÇAP başvurusu nasıl yapılır?", Department.ACADEMIC_PROGRAMS, "CAP basvuru"),
    QueryCase("ÇAP not ortalaması kaç olmalı?", Department.ACADEMIC_PROGRAMS, "CAP not ortalamasi"),
    QueryCase("Ders kaydı ne zaman başlıyor?", Department.STUDENT_AFFAIRS, "ders kaydi tarih"),
    QueryCase("Devam zorunluluğu var mı?", Department.ACADEMIC_PROGRAMS, "devam"),
    QueryCase("Başarısız olduğum seçmeli ders yerine başka seçmeli ders alabilir miyim?", Department.STUDENT_AFFAIRS, "secmeli ders"),
    QueryCase("Kayıt dondurma başvurusu nasıl yapılır?", Department.STUDENT_AFFAIRS, "kayit dondurma"),
    QueryCase("Not itirazı başvurusu nasıl yapılır?", Department.STUDENT_AFFAIRS, "not itirazi"),
    QueryCase("Mezuniyet için kaç AKTS gerekir?", Department.STUDENT_AFFAIRS, "mezuniyet akts"),
    QueryCase("Burs başvurusu nereden yapılır?", Department.FINANCE, "burs"),
    QueryCase("Türk öğrenciler için diş hekimliği ücreti ne kadar?", Department.FINANCE, "domestic fee"),
    QueryCase("Uluslararası öğrenciler için tıp ücreti ne kadar?", Department.FINANCE, "international fee"),
    QueryCase("Erasmus başvurusu nasıl yapılır?", Department.ACADEMIC_PROGRAMS, "erasmus"),
    QueryCase("BIL104 dersinin ön koşulu nedir?", Department.ACADEMIC_PROGRAMS, "ders on kosul"),
    QueryCase("Staj başvurusu için hangi belgeler gerekli?", Department.STUDENT_AFFAIRS, "staj belge"),
    QueryCase("Disiplin soruşturmasında sınav hakkım etkilenir mi?", Department.STUDENT_AFFAIRS, "disiplin"),
    QueryCase("Muafiyet dilekçesi nereye verilir?", Department.STUDENT_AFFAIRS, "muafiyet"),
    QueryCase("Yatay geçiş şartları nelerdir?", Department.ACADEMIC_PROGRAMS, "yatay gecis"),
]


BIAS_FLAGS = (
    "source_relevance_penalty_enabled",
    "query_profile_source_bias_enabled",
    "education_level_penalty_enabled",
    "finance_source_penalty_enabled",
    "student_affairs_faq_bias_enabled",
)


def _load_profile_cases(profile: str) -> list[QueryCase]:
    path = Path(__file__).with_name("profile_benchmarks.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data.get(profile, {}).get("questions") or []
    return [QueryCase(str(item.get("soru") or "").strip(), None, profile) for item in questions if item.get("soru")]


@contextmanager
def _bias_config(enabled: bool) -> Iterator[None]:
    old = {name: getattr(settings.rag, name) for name in BIAS_FLAGS}
    old_cache_enabled = settings.cache.retriever_query_cache_enabled
    try:
        for name in BIAS_FLAGS:
            setattr(settings.rag, name, enabled)
        settings.cache.retriever_query_cache_enabled = False
        yield
    finally:
        for name, value in old.items():
            setattr(settings.rag, name, value)
        settings.cache.retriever_query_cache_enabled = old_cache_enabled


def _source_name(item: dict[str, Any]) -> str:
    meta = item.get("metadata") or {}
    return str(
        item.get("source")
        or meta.get("source")
        or meta.get("filename")
        or meta.get("file_name")
        or meta.get("relative_path")
        or "?"
    )


def _run_search(
    case: QueryCase,
    *,
    top_k: int,
    biases_enabled: bool,
    force_reranker: bool = False,
) -> tuple[list[dict[str, Any]], float]:
    with _bias_config(biases_enabled):
        retriever = HybridRetriever(cache_ttl=0, enable_query_expansion=False)
        if force_reranker:
            retriever._should_skip_reranker = lambda *args, **kwargs: False  # type: ignore[method-assign]
        start = time.perf_counter()
        try:
            results = retriever.search(case.query, top_k=top_k, department=case.department)
        finally:
            retriever.close()
        elapsed_ms = (time.perf_counter() - start) * 1000
    return results, elapsed_ms


def _summarize(results: list[dict[str, Any]], *, top_n: int) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for item in results[:top_n]:
        meta = item.get("metadata") or {}
        summary.append(
            {
                "source": _source_name(item),
                "score": round(float(item.get("score", 0.0)), 4),
                "score_type": str(meta.get("score_type") or ""),
                "reranker_score": meta.get("reranker_score"),
                "pre_rerank_score": meta.get("pre_rerank_score"),
            }
        )
    return summary


def _compare_case(case: QueryCase, *, top_k: int, top_n: int, force_reranker: bool) -> dict[str, Any]:
    current_results, current_ms = _run_search(
        case,
        top_k=top_k,
        biases_enabled=True,
        force_reranker=force_reranker,
    )
    plain_results, plain_ms = _run_search(
        case,
        top_k=top_k,
        biases_enabled=False,
        force_reranker=force_reranker,
    )
    current_sources = [_source_name(item) for item in current_results[:top_n]]
    plain_sources = [_source_name(item) for item in plain_results[:top_n]]
    return {
        "query": case.query,
        "department": case.department.value if case.department else None,
        "note": case.note,
        "top1_changed": (current_sources[:1] != plain_sources[:1]),
        "top3_same_set": set(current_sources[:3]) == set(plain_sources[:3]),
        "current_elapsed_ms": round(current_ms, 1),
        "no_bias_elapsed_ms": round(plain_ms, 1),
        "current": _summarize(current_results, top_n=top_n),
        "no_bias": _summarize(plain_results, top_n=top_n),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieval score-shaping A/B benchmark")
    parser.add_argument("--queries", default="custom", choices=("custom", "core", "all"))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument("--force-reranker", action="store_true")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    if args.queries == "custom":
        cases = CUSTOM_CASES
    elif args.queries == "core":
        cases = _load_profile_cases("core")
    else:
        cases = [*CUSTOM_CASES, *_load_profile_cases("core")]

    if args.limit > 0:
        cases = cases[: args.limit]

    print("Retrieval bias/penalty comparison")
    print(f"Questions: {len(cases)} | top_k={args.top_k} | top_n={args.top_n}")
    print(f"Flags compared: {', '.join(BIAS_FLAGS)}")
    print()

    results = []
    top1_changed = 0
    top3_changed = 0
    for index, case in enumerate(cases, start=1):
        item = _compare_case(
            case,
            top_k=args.top_k,
            top_n=args.top_n,
            force_reranker=args.force_reranker,
        )
        results.append(item)
        if item["top1_changed"]:
            top1_changed += 1
        if not item["top3_same_set"]:
            top3_changed += 1

        print(f"{index:02d}. {case.query}")
        print(f"    current : {item['current'][0]['source'] if item['current'] else '-'}")
        print(f"    no_bias : {item['no_bias'][0]['source'] if item['no_bias'] else '-'}")
        marker = "TOP1_CHANGED" if item["top1_changed"] else "same"
        print(f"    result  : {marker} | current={item['current_elapsed_ms']}ms no_bias={item['no_bias_elapsed_ms']}ms")

    print()
    print("Summary")
    print(f"- Top-1 changed: {top1_changed}/{len(cases)}")
    print(f"- Top-3 set changed: {top3_changed}/{len(cases)}")

    payload = {"summary": {"top1_changed": top1_changed, "top3_changed": top3_changed, "count": len(cases)}, "results": results}
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"- JSON written: {args.json_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
