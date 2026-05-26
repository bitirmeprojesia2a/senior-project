"""
Reranker model comparison utility.

This script is a shadow benchmark helper. It compares the configured runtime
reranker with a candidate model without changing production defaults.

Usage:
    python scripts/compare_reranker_models.py
    python scripts/compare_reranker_models.py --compare
    python scripts/compare_reranker_models.py --compare --fp16
    python scripts/compare_reranker_models.py --compare --turkish-finetune
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.console import configure_utf8_stdio
from src.core.config import apply_model_cache_environment, settings

configure_utf8_stdio()
apply_model_cache_environment()

import torch  # noqa: E402
from sentence_transformers import CrossEncoder  # noqa: E402

from src.rag.candidate_utils import deduplicate_candidate_dicts  # noqa: E402
from src.rag.retriever import HybridRetriever  # noqa: E402

DEFAULT_BASELINE_MODEL = settings.reranker.model
DEFAULT_CANDIDATE_MODEL = "BAAI/bge-reranker-v2-m3"
DEFAULT_TURKISH_FINE_TUNE_MODEL = "seroe/bge-reranker-v2-m3-turkish-triplet"
DEFAULT_BASELINE_MAX_LENGTH = settings.reranker.max_length
DEFAULT_CANDIDATE_MAX_LENGTH = 1024

DIAGNOSTIC_QUERIES = [
    {
        "query": "Denklik belgesi ne zaman gerekir?",
        "department": "academic_programs",
        "expected_source_keywords": ["denklik"],
        "note": "Belge getirildi ama reranker dusuk skor verdi",
    },
    {
        "query": "YOS ID numarami nasil ogrenebilirim?",
        "department": "academic_programs",
        "expected_source_keywords": ["ogrenci_no", "uluslararasi_ogrenci"],
        "note": "Belge getirildi ama reranker dusuk skor verdi",
    },
    {
        "query": "Azami ogrenim suresi dolunca ne olur?",
        "department": "academic_programs",
        "expected_source_keywords": ["lisans", "yonetmelik", "egitim_ogretim"],
        "note": "academic_programs koleksiyonunda dusuk skor",
    },
    {
        "query": "TOMER ne is yapar?",
        "department": "academic_programs",
        "expected_source_keywords": ["tomer", "turkce"],
        "note": "Koleksiyonda ilgili belge olmayabilir",
    },
    {
        "query": "Basarisiz oldugum dersi tekrar almak icin ne yapmaliyim?",
        "department": "student_affairs",
        "expected_source_keywords": ["yonetmelik", "egitim_ogretim", "ders"],
        "note": "Basarili ama LLM sentez daginik cikti",
    },
    {
        "query": "Yaz okulunda en fazla kac ders alabilirim?",
        "department": "student_affairs",
        "expected_source_keywords": ["yaz_okulu", "yonerge"],
        "note": "Basarili - kontrol grubu",
    },
    {
        "query": "Mezuniyet icin GNO en az kac olmalidir?",
        "department": "student_affairs",
        "expected_source_keywords": ["lisans", "yonetmelik", "mezuniyet"],
        "note": "Basarili - kontrol grubu",
    },
    {
        "query": "Program suresini asarsam katki payi oder miyim?",
        "department": "finance",
        "expected_source_keywords": ["katki_payi", "ucret"],
        "note": "finance_docs kucuk koleksiyon, reranker skip",
    },
]

PREFIX_TEMPLATE = "Muhendislik Fakultesi / Bilgisayar Muhendisligi bolumu/programi icin: "


def _resolve_torch_dtype(*, use_fp16: bool) -> torch.dtype | None:
    """Return FP16 dtype only when CUDA is available."""
    if not use_fp16:
        return None
    if not torch.cuda.is_available():
        print("  FP16 istendi ama CUDA yok; model varsayilan dtype ile yuklenecek.", flush=True)
        return None
    return torch.float16


def load_model(model_name: str, max_length: int, *, use_fp16: bool = False) -> CrossEncoder:
    """Load a CrossEncoder model with the same cache/local-files policy as runtime."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = _resolve_torch_dtype(use_fp16=use_fp16)
    dtype_label = str(torch_dtype) if torch_dtype is not None else "default"
    print(
        f"  Model yukleniyor: {model_name} "
        f"(max_length={max_length}, device={device}, dtype={dtype_label})",
        flush=True,
    )
    t0 = time.perf_counter()
    kwargs: dict[str, Any] = {
        "max_length": max_length,
        "device": device,
        "local_files_only": settings.reranker.local_files_only,
    }
    if settings.model_cache.hf_hub_cache is not None:
        kwargs["cache_dir"] = str(settings.model_cache.hf_hub_cache)
    if torch_dtype is not None:
        kwargs["automodel_args"] = {"torch_dtype": torch_dtype}
    model = CrossEncoder(model_name, **kwargs)
    elapsed = time.perf_counter() - t0
    print(f"  Yuklendi: {elapsed:.1f}s", flush=True)
    return model


def get_candidates(retriever: HybridRetriever, query: str, department: str) -> list[dict[str, Any]]:
    """Collect raw pre-reranker candidates for a department."""
    from src.core.constants import Department, collection_name_for_department

    dept = Department(department)
    collection = collection_name_for_department(dept)
    expanded_query = retriever.query_preprocessor.preprocess(query)
    retriever._ensure_ensemble(collection)
    raw_docs = retriever._ensembles[collection].invoke(expanded_query)
    return deduplicate_candidate_dicts(
        [
            {
                "content": doc.page_content,
                "metadata": dict(doc.metadata or {}),
                "source": (doc.metadata or {}).get("source", "?"),
                "score": float((doc.metadata or {}).get("similarity_score", 0.0)),
            }
            for doc in raw_docs
        ]
    )


def score_with_model(model: CrossEncoder, query: str, candidates: list[dict[str, Any]]) -> list[tuple[float, str, str]]:
    """Score candidates and return sorted tuples of score/source/preview."""
    if not candidates:
        return []
    pairs = [(query, c["content"]) for c in candidates]
    scores = model.predict(pairs, batch_size=settings.reranker.batch_size, show_progress_bar=False)
    results = []
    for candidate, score in zip(candidates, scores):
        source = candidate.get("source", candidate.get("metadata", {}).get("source", "?"))
        preview = candidate["content"][:80].replace("\n", " ")
        results.append((round(float(score), 4), source, preview))
    results.sort(key=lambda item: item[0], reverse=True)
    return results


def source_matches_expected(source: str, keywords: list[str]) -> bool:
    """Check whether the source name contains one of the expected keywords."""
    source_lower = source.lower().replace(" ", "_")
    return any(keyword.lower() in source_lower for keyword in keywords)


def _best_expected_score(results: list[tuple[float, str, str]], keywords: list[str]) -> float | None:
    scores = [score for score, source, _ in results if source_matches_expected(source, keywords)]
    return max(scores) if scores else None


def print_block(label: str, results: list[tuple[float, str, str]], expected_keywords: list[str]) -> None:
    """Print top reranker results for one model."""
    print(f"\n  {label}:")
    print(f"  {'Rank':<5} {'Score':<10} {'Hit?':<6} {'Source':<50} Preview")
    print("  " + "-" * 90)
    for rank, (score, source, preview) in enumerate(results[:5], 1):
        match = "yes" if source_matches_expected(source, expected_keywords) else ""
        print(f"  {rank:<5} {score:<10.4f} {match:<6} {source[:50]:<50} {preview[:40]}")

    best = _best_expected_score(results, expected_keywords)
    if best is None:
        print("  >> Beklenen belge adaylar arasinda bulunamadi")
        return
    rank = next(
        idx
        for idx, (score, source, _preview) in enumerate(results, 1)
        if score == best and source_matches_expected(source, expected_keywords)
    )
    print(f"  >> Beklenen belge en iyi skoru: {best:.4f} (sira: {rank})")


def print_comparison(
    query: str,
    expected_keywords: list[str],
    baseline_results: list[tuple[float, str, str]],
    candidate_results: list[tuple[float, str, str]],
    prefixed_baseline: list[tuple[float, str, str]] | None = None,
    prefixed_candidate: list[tuple[float, str, str]] | None = None,
) -> None:
    """Print per-query comparison."""
    print("\n  " + "-" * 90)
    print(f"  SORGU: {query}")
    print(f"  Beklenen kaynak anahtar kelimeleri: {expected_keywords}")
    print_block("[A] baseline", baseline_results, expected_keywords)
    print_block("[B] candidate", candidate_results, expected_keywords)
    if prefixed_baseline and prefixed_candidate:
        print(f"\n  --- PREFIX ETKISI ({PREFIX_TEMPLATE[:30]}...) ---")
        print_block("[A+prefix] baseline", prefixed_baseline, expected_keywords)
        print_block("[B+prefix] candidate", prefixed_candidate, expected_keywords)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare runtime reranker with a candidate model.")
    parser.add_argument("--compare", action="store_true", help="Load and compare the candidate model too.")
    parser.add_argument("--fp16", action="store_true", help="Use FP16 on CUDA for loaded models.")
    parser.add_argument("--baseline-model", default=DEFAULT_BASELINE_MODEL)
    parser.add_argument("--candidate-model", default=DEFAULT_CANDIDATE_MODEL)
    parser.add_argument("--baseline-max-length", type=int, default=DEFAULT_BASELINE_MAX_LENGTH)
    parser.add_argument("--candidate-max-length", type=int, default=DEFAULT_CANDIDATE_MAX_LENGTH)
    parser.add_argument(
        "--turkish-finetune",
        action="store_true",
        help="Use seroe/bge-reranker-v2-m3-turkish-triplet as candidate.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidate_model_name = DEFAULT_TURKISH_FINE_TUNE_MODEL if args.turkish_finetune else args.candidate_model

    print("=" * 95, flush=True)
    print("RERANKER TANI TESTI", flush=True)
    print("=" * 95, flush=True)
    print(f"\nBaseline model: {args.baseline_model} (max_length={args.baseline_max_length})", flush=True)
    if args.compare:
        print(f"Candidate model: {candidate_model_name} (max_length={args.candidate_max_length})", flush=True)
    print(f"FP16: {'acik' if args.fp16 else 'kapali'}", flush=True)
    print(f"Tani sorgusu sayisi: {len(DIAGNOSTIC_QUERIES)}", flush=True)

    print("\n--- Model Yukleme ---", flush=True)
    baseline_model = load_model(args.baseline_model, args.baseline_max_length, use_fp16=args.fp16)
    candidate_model = (
        load_model(candidate_model_name, args.candidate_max_length, use_fp16=args.fp16)
        if args.compare
        else None
    )

    print("\n--- Retriever Hazirlama ---", flush=True)
    retriever = HybridRetriever()
    summary_rows: list[dict[str, Any]] = []

    for index, test_case in enumerate(DIAGNOSTIC_QUERIES, 1):
        query = test_case["query"]
        department = test_case["department"]
        expected_keywords = test_case["expected_source_keywords"]
        note = test_case["note"]

        print(f"\n{'=' * 95}", flush=True)
        print(f"SORGU {index}/{len(DIAGNOSTIC_QUERIES)}: {query}", flush=True)
        print(f"Departman: {department} | Not: {note}", flush=True)

        candidates = get_candidates(retriever, query, department)
        if not candidates:
            print("  ADAY BULUNAMADI - atlaniyor", flush=True)
            continue
        print(f"  Aday sayisi: {len(candidates)}", flush=True)

        baseline_results = score_with_model(baseline_model, query, candidates)
        candidate_results = score_with_model(candidate_model, query, candidates) if candidate_model else baseline_results

        prefixed_query = PREFIX_TEMPLATE + query
        prefixed_baseline = score_with_model(baseline_model, prefixed_query, candidates)
        prefixed_candidate = score_with_model(candidate_model, prefixed_query, candidates) if candidate_model else prefixed_baseline

        print_comparison(
            query,
            expected_keywords,
            baseline_results,
            candidate_results,
            prefixed_baseline,
            prefixed_candidate,
        )

        summary_rows.append(
            {
                "query": query,
                "baseline_best": _best_expected_score(baseline_results, expected_keywords),
                "candidate_best": _best_expected_score(candidate_results, expected_keywords) if candidate_model else None,
                "prefix_baseline_best": _best_expected_score(prefixed_baseline, expected_keywords),
                "prefix_candidate_best": (
                    _best_expected_score(prefixed_candidate, expected_keywords) if candidate_model else None
                ),
                "candidate_count": len(candidates),
            }
        )

    print(f"\n\n{'=' * 95}", flush=True)
    print("GENEL OZET", flush=True)
    print(f"{'=' * 95}", flush=True)

    if args.compare:
        print(f"\n{'Sorgu':<55} {'Base':<10} {'Aday':<10} {'Base+Pfx':<10} {'Aday+Pfx':<10}", flush=True)
    else:
        print(f"\n{'Sorgu':<55} {'Skor':<10} {'Prefix+Skor':<12}", flush=True)
    print("-" * 95, flush=True)

    baseline_wins = 0
    candidate_wins = 0
    for row in summary_rows:
        query_label = row["query"][:53]
        base = f"{row['baseline_best']:.4f}" if row["baseline_best"] is not None else "N/A"
        prefix_base = (
            f"{row['prefix_baseline_best']:.4f}" if row["prefix_baseline_best"] is not None else "N/A"
        )

        if args.compare:
            candidate = f"{row['candidate_best']:.4f}" if row["candidate_best"] is not None else "N/A"
            prefix_candidate = (
                f"{row['prefix_candidate_best']:.4f}" if row["prefix_candidate_best"] is not None else "N/A"
            )
            print(
                f"{query_label:<55} {base:<10} {candidate:<10} {prefix_base:<10} {prefix_candidate:<10}",
                flush=True,
            )
            base_score = row["baseline_best"] or 0.0
            candidate_score = row["candidate_best"] or 0.0
            if base_score > candidate_score:
                baseline_wins += 1
            elif candidate_score > base_score:
                candidate_wins += 1
        else:
            print(f"{query_label:<55} {base:<10} {prefix_base:<12}", flush=True)

    if args.compare:
        print(f"\n{'-' * 95}", flush=True)
        print(f"Baseline daha iyi: {baseline_wins} sorgu", flush=True)
        print(f"Aday daha iyi:     {candidate_wins} sorgu", flush=True)
        print(f"Esit/N/A:          {len(summary_rows) - baseline_wins - candidate_wins} sorgu", flush=True)

    retriever.close()
    print("\nBitti.", flush=True)


if __name__ == "__main__":
    main()
