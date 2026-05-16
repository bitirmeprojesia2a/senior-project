"""
Reranker Model Karsilastirma Testi

Sorunlu sorgularda mevcut Turkish fine-tune model ile base modeli
kafa kafaya karsilastirir. Ayrica sorgu prefix etkisini olcer.

Kullanim:
    python scripts/compare_reranker_models.py
"""

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

from sentence_transformers import CrossEncoder  # noqa: E402

from src.rag.retriever import HybridRetriever
from src.rag.candidate_utils import deduplicate_candidate_dicts

CURRENT_MODEL = "seroe/bge-reranker-v2-m3-turkish-triplet"
BASE_MODEL = "BAAI/bge-reranker-v2-m3"

CURRENT_MAX_LENGTH = 512
BASE_MAX_LENGTH = 1024

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


def load_model(model_name: str, max_length: int) -> CrossEncoder:
    """CrossEncoder modelini yukler."""
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Model yukleniyor: {model_name} (max_length={max_length}, device={device})")
    t0 = time.perf_counter()
    model = CrossEncoder(
        model_name,
        max_length=max_length,
        device=device,
        cache_dir=str(settings.model_cache.hf_hub_cache)
        if settings.model_cache.hf_hub_cache is not None
        else None,
        local_files_only=settings.reranker.local_files_only,
    )
    elapsed = time.perf_counter() - t0
    print(f"  Yuklendi: {elapsed:.1f}s")
    return model


def get_candidates(retriever: HybridRetriever, query: str, department: str) -> list[dict[str, Any]]:
    """Reranker oncesi ham adaylari toplar."""
    from src.core.constants import Department, collection_name_for_department

    dept = Department(department)
    collection = collection_name_for_department(dept)
    expanded_query = retriever.query_preprocessor.preprocess(query)
    retriever._ensure_ensemble(collection)
    raw_docs = retriever._ensembles[collection].invoke(expanded_query)
    candidates = deduplicate_candidate_dicts(
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
    return candidates


def score_with_model(model: CrossEncoder, query: str, candidates: list[dict]) -> list[tuple[float, str, str]]:
    """Model ile adaylari skorlar, (skor, kaynak, icerik_preview) dondurur."""
    if not candidates:
        return []
    pairs = [(query, c["content"]) for c in candidates]
    scores = model.predict(pairs, batch_size=16, show_progress_bar=False)
    results = []
    for c, s in zip(candidates, scores):
        source = c.get("source", c.get("metadata", {}).get("source", "?"))
        preview = c["content"][:80].replace("\n", " ")
        results.append((round(float(s), 4), source, preview))
    results.sort(key=lambda x: x[0], reverse=True)
    return results


def source_matches_expected(source: str, keywords: list[str]) -> bool:
    """Kaynak adinin beklenen anahtar kelimelerden birini icerip icerdigini kontrol eder."""
    source_lower = source.lower().replace(" ", "_")
    return any(kw.lower() in source_lower for kw in keywords)


def print_comparison(
    query: str,
    expected_keywords: list[str],
    current_results: list[tuple[float, str, str]],
    base_results: list[tuple[float, str, str]],
    prefixed_current: list[tuple[float, str, str]] | None = None,
    prefixed_base: list[tuple[float, str, str]] | None = None,
):
    """Karsilastirma tablosunu yazdirir."""
    top_n = 5

    print(f"\n  {'─' * 90}")
    print(f"  SORGU: {query}")
    print(f"  Beklenen kaynak anahtar kelimeleri: {expected_keywords}")

    def _print_block(label: str, results: list[tuple[float, str, str]]):
        print(f"\n  {label}:")
        print(f"  {'Sira':<5} {'Skor':<10} {'Ilgili?':<9} {'Kaynak':<50} {'Icerik'}")
        print(f"  {'─' * 90}")
        for i, (score, source, preview) in enumerate(results[:top_n], 1):
            match = "***" if source_matches_expected(source, expected_keywords) else ""
            print(f"  {i:<5} {score:<10.4f} {match:<9} {source[:50]:<50} {preview[:40]}")

        expected_scores = [s for s, src, _ in results if source_matches_expected(src, expected_keywords)]
        if expected_scores:
            best = max(expected_scores)
            rank = next(i for i, (s, _, _) in enumerate(results, 1) if s == best and source_matches_expected(results[i-1][1], expected_keywords))
            print(f"  >> Beklenen belge en iyi skoru: {best:.4f} (sira: {rank})")
        else:
            print(f"  >> Beklenen belge BULUNAMADI adaylar arasinda")

    _print_block(f"[A] {CURRENT_MODEL} (max_len={CURRENT_MAX_LENGTH})", current_results)
    _print_block(f"[B] {BASE_MODEL} (max_len={BASE_MAX_LENGTH})", base_results)

    if prefixed_current and prefixed_base:
        print(f"\n  --- PREFIX ETKISI (sorguya '{PREFIX_TEMPLATE[:30]}...' eklendi) ---")
        _print_block(f"[A+prefix] {CURRENT_MODEL}", prefixed_current)
        _print_block(f"[B+prefix] {BASE_MODEL}", prefixed_base)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare", action="store_true", help="Base model ile karsilastir (indirilmesi gerekir)")
    args = parser.parse_args()

    run_comparison = args.compare

    print("=" * 95, flush=True)
    print("RERANKER TANI TESTI", flush=True)
    print("=" * 95, flush=True)
    print(f"\nMevcut model: {CURRENT_MODEL} (max_length={CURRENT_MAX_LENGTH})", flush=True)
    if run_comparison:
        print(f"Base model:   {BASE_MODEL} (max_length={BASE_MAX_LENGTH})", flush=True)
    print(f"Tani sorgusu sayisi: {len(DIAGNOSTIC_QUERIES)}", flush=True)

    print("\n--- Model Yukleme ---", flush=True)
    current_model = load_model(CURRENT_MODEL, CURRENT_MAX_LENGTH)
    base_model = None
    if run_comparison:
        base_model = load_model(BASE_MODEL, BASE_MAX_LENGTH)

    print("\n--- Retriever Hazirlama ---", flush=True)
    retriever = HybridRetriever()

    summary_rows: list[dict] = []

    for idx, test_case in enumerate(DIAGNOSTIC_QUERIES, 1):
        query = test_case["query"]
        department = test_case["department"]
        expected_kw = test_case["expected_source_keywords"]
        note = test_case["note"]

        print(f"\n{'═' * 95}", flush=True)
        print(f"SORGU {idx}/{len(DIAGNOSTIC_QUERIES)}: {query}", flush=True)
        print(f"Departman: {department} | Not: {note}", flush=True)

        candidates = get_candidates(retriever, query, department)
        if not candidates:
            print("  ADAY BULUNAMADI - atlaniyor", flush=True)
            continue

        print(f"  Aday sayisi: {len(candidates)}", flush=True)

        current_results = score_with_model(current_model, query, candidates)
        base_results = score_with_model(base_model, query, candidates) if base_model else []

        prefixed_query = PREFIX_TEMPLATE + query
        prefixed_current = score_with_model(current_model, prefixed_query, candidates)
        prefixed_base = score_with_model(base_model, prefixed_query, candidates) if base_model else []

        if run_comparison and base_results:
            print_comparison(query, expected_kw, current_results, base_results, prefixed_current, prefixed_base)
        else:
            print_comparison(query, expected_kw, current_results, current_results, prefixed_current, prefixed_current)

        def _best_expected_score(results):
            scores = [s for s, src, _ in results if source_matches_expected(src, expected_kw)]
            return max(scores) if scores else None

        summary_rows.append({
            "query": query,
            "current_best": _best_expected_score(current_results),
            "base_best": _best_expected_score(base_results) if base_results else None,
            "prefix_current_best": _best_expected_score(prefixed_current),
            "prefix_base_best": _best_expected_score(prefixed_base) if prefixed_base else None,
            "candidate_count": len(candidates),
        })

    print(f"\n\n{'═' * 95}", flush=True)
    print("GENEL OZET", flush=True)
    print(f"{'═' * 95}", flush=True)

    if run_comparison:
        print(f"\n{'Sorgu':<55} {'TR-FT':<10} {'Base':<10} {'TR+Pfx':<10} {'Base+Pfx':<10}", flush=True)
    else:
        print(f"\n{'Sorgu':<55} {'Skor':<10} {'Prefix+Skor':<12}", flush=True)
    print(f"{'─' * 95}", flush=True)

    current_wins = 0
    base_wins = 0
    for row in summary_rows:
        q = row["query"][:53]
        c = f"{row['current_best']:.4f}" if row["current_best"] is not None else "N/A"
        pc = f"{row['prefix_current_best']:.4f}" if row["prefix_current_best"] is not None else "N/A"

        if run_comparison:
            b = f"{row['base_best']:.4f}" if row["base_best"] is not None else "N/A"
            pb = f"{row['prefix_base_best']:.4f}" if row["prefix_base_best"] is not None else "N/A"
            print(f"{q:<55} {c:<10} {b:<10} {pc:<10} {pb:<10}", flush=True)
            cs = row["current_best"] or 0
            bs = row["base_best"] or 0
            if cs > bs:
                current_wins += 1
            elif bs > cs:
                base_wins += 1
        else:
            print(f"{q:<55} {c:<10} {pc:<12}", flush=True)

    if run_comparison:
        print(f"\n{'─' * 95}", flush=True)
        print(f"Turkish fine-tune daha iyi: {current_wins} sorgu", flush=True)
        print(f"Base model daha iyi:        {base_wins} sorgu", flush=True)
        print(f"Esit/N/A:                   {len(summary_rows) - current_wins - base_wins} sorgu", flush=True)

    retriever.close()
    print("\nBitti.", flush=True)


if __name__ == "__main__":
    main()
