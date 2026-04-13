"""
Reranker Skor Dagilim Analizi

Benchmark sorularini calistirarak candidate pool + reranker skor dagilimini olcer.
Bu script final retrieval pipeline'inin tum post-processing adimlarini tekrar etmez;
ama reranker kalibrasyonu ve aday havuzu kalitesi icin guclu bir inceleme aracidir.
Bu verilerle sigmoid kalibrasyon parametreleri ve esik degerleri belirlenir.

Kullanim:
    python scripts/analyze_reranker_scores.py
    python scripts/analyze_reranker_scores.py --profile core
    python scripts/analyze_reranker_scores.py --query "Erasmus basvurusu nasil yapilir"
    python scripts/analyze_reranker_scores.py --all-profiles
    python scripts/analyze_reranker_scores.py --output docs/reranker_score_analysis.md
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.console import configure_utf8_stdio
from src.rag.retriever import HybridRetriever
from src.rag.reranker import CrossEncoderReranker, _CALIBRATION_SHIFT, _CALIBRATION_SCALE
from src.rag.candidate_utils import deduplicate_candidate_dicts

configure_utf8_stdio()

BENCHMARKS_PATH = project_root / "scripts" / "profile_benchmarks.json"

EXPLORE_PROFILES = [
    "explore_student_documents_turk",
    "explore_transfer_and_special_status_turk",
    "explore_international_procedures_turk",
    "explore_formasyon_turk",
    "explore_finance_edge_turk",
    "explore_exam_and_attendance_turk",
    "explore_graduation_gpa_turk",
    "explore_internship_project_turk",
]


def load_benchmark_questions(profile_name: str | None) -> list[dict[str, Any]]:
    """Benchmark dosyasindan sorulari yukler."""
    if not BENCHMARKS_PATH.exists():
        print(f"Benchmark dosyasi bulunamadi: {BENCHMARKS_PATH}")
        sys.exit(1)

    with open(BENCHMARKS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if profile_name:
        if profile_name not in data:
            print(f"Profil bulunamadi: {profile_name}")
            print(f"Mevcut profiller: {', '.join(data.keys())}")
            sys.exit(1)
        questions = data[profile_name]["questions"]
        for q in questions:
            q["_profile"] = profile_name
        return questions

    all_questions: list[dict[str, Any]] = []
    for name in EXPLORE_PROFILES:
        if name in data:
            for q in data[name]["questions"]:
                q["_profile"] = name
                all_questions.append(q)
    return all_questions


def sigmoid(x: float) -> float:
    """Standart sigmoid fonksiyonu."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    ez = math.exp(x)
    return ez / (1.0 + ez)


def calibrated_sigmoid(raw_logit: float) -> float:
    """reranker.py ile ayni kalibre sigmoid: sigmoid((logit - shift) / scale)."""
    adjusted = (raw_logit - _CALIBRATION_SHIFT) / _CALIBRATION_SCALE
    return sigmoid(adjusted)


def percentile(values: list[float], p: float) -> float:
    """Basit percentile hesaplama."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_vals):
        return sorted_vals[-1]
    return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])


def analyze_single_query(
    query: str,
    retriever: HybridRetriever,
    reranker: CrossEncoderReranker,
    department: str | None = None,
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Tek bir sorgu icin candidate pool + reranking skorlarini toplar."""
    primary_collections, fallback_collections = retriever._resolve_search_collections(
        query=query,
        department=department,
    )
    expanded_query = retriever.query_preprocessor.preprocess(query)

    candidates = retriever._collect_candidates(
        query=query,
        expanded_query=expanded_query,
        primary_collections=primary_collections,
        fallback_collections=fallback_collections,
    )
    if not candidates:
        return []

    candidates = deduplicate_candidate_dicts(candidates)

    for c in candidates:
        meta = c.setdefault("metadata", {})
        meta["pre_rerank_score"] = round(float(c.get("score", 0.0)), 4)

    pairs = [(query, c["content"]) for c in candidates]
    try:
        raw_scores = reranker.model.predict(
            pairs,
            batch_size=reranker.batch_size,
            show_progress_bar=False,
        )
    except Exception as exc:
        print(f"  Reranker hatasi: {exc}")
        return []

    results = []
    for candidate, raw_score in zip(candidates, raw_scores):
        raw_float = round(float(raw_score), 6)
        sig_score = round(sigmoid(raw_float), 6)
        cal_score = round(calibrated_sigmoid(raw_float), 6)
        results.append({
            "source": candidate.get("source", "?"),
            "content_preview": candidate.get("content", "")[:120].replace("\n", " "),
            "pre_rerank_score": float(candidate.get("metadata", {}).get("pre_rerank_score", 0.0)),
            "raw_reranker_score": raw_float,
            "sigmoid_score": sig_score,
            "calibrated_score": cal_score,
            "content_length": len(candidate.get("content", "")),
        })

    results.sort(key=lambda r: r["raw_reranker_score"], reverse=True)
    return results[:top_k]


def compute_statistics(all_scores: list[float]) -> dict[str, float]:
    """Skor listesi icin istatistiksel ozet."""
    if not all_scores:
        return {}
    n = len(all_scores)
    mean = sum(all_scores) / n
    variance = sum((x - mean) ** 2 for x in all_scores) / n
    std = math.sqrt(variance)
    sorted_scores = sorted(all_scores)

    return {
        "count": n,
        "min": round(sorted_scores[0], 4),
        "max": round(sorted_scores[-1], 4),
        "mean": round(mean, 4),
        "std": round(std, 4),
        "median": round(percentile(all_scores, 50), 4),
        "p10": round(percentile(all_scores, 10), 4),
        "p25": round(percentile(all_scores, 25), 4),
        "p75": round(percentile(all_scores, 75), 4),
        "p90": round(percentile(all_scores, 90), 4),
    }


def print_query_results(query: str, results: list[dict[str, Any]], index: int) -> None:
    """Tek sorgu icin sonuclari yazdirir."""
    print(f"\n{'='*80}")
    print(f"[{index}] {query}")
    print(f"{'='*80}")
    if not results:
        print("  Sonuc bulunamadi.")
        return

    print(f"  {'#':>3}  {'Ham Skor':>10}  {'Kalibre':>8}  {'Sigmoid':>8}  {'Uzunluk':>8}  Kaynak")
    print(f"  {'---':>3}  {'--------':>10}  {'-------':>8}  {'-------':>8}  {'-------':>8}  {'------'}")
    for i, r in enumerate(results, 1):
        print(
            f"  {i:3d}  {r['raw_reranker_score']:10.4f}  {r['calibrated_score']:8.4f}  "
            f"{r['sigmoid_score']:8.4f}  {r['content_length']:8d}  {r['source']}"
        )


def print_statistics(stats: dict[str, float], label: str) -> None:
    """Istatistik tablosu yazdirir."""
    if not stats:
        return
    print(f"\n{label}")
    print(f"  Adet    : {stats['count']}")
    print(f"  Min     : {stats['min']:.4f}")
    print(f"  P10     : {stats['p10']:.4f}")
    print(f"  P25     : {stats['p25']:.4f}")
    print(f"  Median  : {stats['median']:.4f}")
    print(f"  Mean    : {stats['mean']:.4f}")
    print(f"  P75     : {stats['p75']:.4f}")
    print(f"  P90     : {stats['p90']:.4f}")
    print(f"  Max     : {stats['max']:.4f}")
    print(f"  Std     : {stats['std']:.4f}")


def suggest_sigmoid_params(raw_stats: dict[str, float]) -> dict[str, Any]:
    """Ham skor istatistiklerine dayanarak sigmoid kalibrasyon onerisi yapar."""
    if not raw_stats:
        return {}
    median = raw_stats["median"]
    p25 = raw_stats["p25"]
    p75 = raw_stats["p75"]
    iqr = p75 - p25
    scale = max(iqr, 0.5)
    shift = median

    return {
        "shift": round(shift, 4),
        "scale": round(scale, 4),
        "formula": f"sigmoid((score - {shift:.4f}) / {scale:.4f})",
        "suggested_direct_rag_threshold": round(sigmoid((p75 - shift) / scale), 3),
        "suggested_min_source_threshold": round(sigmoid((p25 - shift) / scale), 3),
    }


def generate_markdown_report(
    query_results: list[dict[str, Any]],
    all_raw_scores: list[float],
    all_sigmoid_scores: list[float],
    all_calibrated_scores: list[float],
    top1_raw_scores: list[float],
    top1_sigmoid_scores: list[float],
    top1_calibrated_scores: list[float],
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
) -> str:
    """Markdown formatinda rapor uretir."""
    raw_stats = compute_statistics(all_raw_scores)
    sig_stats = compute_statistics(all_sigmoid_scores)
    cal_stats = compute_statistics(all_calibrated_scores)
    top1_raw_stats = compute_statistics(top1_raw_scores)
    top1_sig_stats = compute_statistics(top1_sigmoid_scores)
    top1_cal_stats = compute_statistics(top1_calibrated_scores)
    suggestion = suggest_sigmoid_params(raw_stats)

    lines = [
        "# Reranker Skor Dagilim Analizi",
        "",
        f"**Tarih:** {time.strftime('%Y-%m-%d %H:%M')}",
        f"**Model:** {reranker_model_name}",
        f"**Kalibrasyon:** shift={_CALIBRATION_SHIFT}, scale={_CALIBRATION_SCALE}",
        f"**Toplam Soru:** {len(query_results)}",
        f"**Toplam Skor Ornegi:** {len(all_raw_scores)}",
        "**Kapsam:** Candidate pool + reranker analizi; final threshold/filtering adimlari buna dahil degildir.",
        "",
        "---",
        "",
        "## Tum Skorlar (Tum Adaylar)",
        "",
        "### Ham Reranker Skorlari (Logit)",
        "",
        "| Metrik | Deger |",
        "|--------|-------|",
    ]
    for key in ["count", "min", "p10", "p25", "median", "mean", "p75", "p90", "max", "std"]:
        lines.append(f"| {key} | {raw_stats.get(key, 'N/A')} |")

    lines.extend([
        "",
        "### Kalibre Edilmis Skorlar (Runtime)",
        "",
        "| Metrik | Deger |",
        "|--------|-------|",
    ])
    for key in ["count", "min", "p10", "p25", "median", "mean", "p75", "p90", "max", "std"]:
        lines.append(f"| {key} | {cal_stats.get(key, 'N/A')} |")

    lines.extend([
        "",
        "### Duz Sigmoid Skorlar (Referans)",
        "",
        "| Metrik | Deger |",
        "|--------|-------|",
    ])
    for key in ["count", "min", "p10", "p25", "median", "mean", "p75", "p90", "max", "std"]:
        lines.append(f"| {key} | {sig_stats.get(key, 'N/A')} |")

    lines.extend([
        "",
        "---",
        "",
        "## Top-1 Skorlar (Her Sorunun En Iyi Adayi)",
        "",
        "### Ham Top-1 Skorlari (Logit)",
        "",
        "| Metrik | Deger |",
        "|--------|-------|",
    ])
    for key in ["count", "min", "p10", "p25", "median", "mean", "p75", "p90", "max", "std"]:
        lines.append(f"| {key} | {top1_raw_stats.get(key, 'N/A')} |")

    lines.extend([
        "",
        "### Kalibre Top-1 Skorlari (Runtime)",
        "",
        "| Metrik | Deger |",
        "|--------|-------|",
    ])
    for key in ["count", "min", "p10", "p25", "median", "mean", "p75", "p90", "max", "std"]:
        lines.append(f"| {key} | {top1_cal_stats.get(key, 'N/A')} |")

    lines.extend([
        "",
        "### Duz Sigmoid Top-1 Skorlari (Referans)",
        "",
        "| Metrik | Deger |",
        "|--------|-------|",
    ])
    for key in ["count", "min", "p10", "p25", "median", "mean", "p75", "p90", "max", "std"]:
        lines.append(f"| {key} | {top1_sig_stats.get(key, 'N/A')} |")

    if suggestion:
        lines.extend([
            "",
            "---",
            "",
            "## Sigmoid Kalibrasyon Onerisi",
            "",
            f"- **Formul:** `{suggestion['formula']}`",
            f"- **Shift (median):** {suggestion['shift']}",
            f"- **Scale (IQR):** {suggestion['scale']}",
            f"- **Onerilen direct-RAG esigi:** {suggestion['suggested_direct_rag_threshold']}",
            f"- **Onerilen min-source esigi:** {suggestion['suggested_min_source_threshold']}",
        ])

    lines.extend([
        "",
        "---",
        "",
        "## Soru Bazli Detaylar",
        "",
    ])
    for qr in query_results:
        query = qr["query"]
        results = qr["results"]
        lines.append(f"### {query}")
        if not results:
            lines.append("Sonuc bulunamadi.")
            lines.append("")
            continue
        lines.append("")
        lines.append("| # | Ham Skor | Kalibre | Sigmoid | Kaynak |")
        lines.append("|:-:|:--------:|:-------:|:-------:|--------|")
        for i, r in enumerate(results, 1):
            lines.append(
                f"| {i} | {r['raw_reranker_score']:.4f} | {r['calibrated_score']:.4f} | "
                f"{r['sigmoid_score']:.4f} | {r['source']} |"
            )
        lines.append("")

    lines.extend([
        "---",
        "",
        "*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Candidate pool + reranker skor dagilim analizi"
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=None,
        help="Belirli bir benchmark profili (ornegin: core, explore_finance_edge_turk)",
    )
    parser.add_argument(
        "--all-profiles",
        action="store_true",
        help="Tum explore_* profillerini calistir",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Tek bir sorgu analizi",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Her sorgu icin kaydedilecek aday sayisi (varsayilan: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Markdown rapor cikti dosyasi (ornegin: docs/reranker_score_analysis.md)",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("  RERANKER SKOR DAGILIM ANALIZI")
    print("=" * 80)

    print("\nModeller yukleniyor...")
    retriever = HybridRetriever(cache_ttl=0)
    reranker = CrossEncoderReranker()
    _ = reranker.model
    print(f"  Reranker: {reranker.model_name}")
    print(f"  Max Length: {reranker.max_length}")
    print(f"  Device: {reranker.resolved_device}")

    queries: list[dict[str, Any]] = []
    if args.query:
        queries = [{"soru": args.query, "beklenen_dept": "?", "_profile": "manual"}]
    elif args.profile:
        queries = load_benchmark_questions(args.profile)
    else:
        queries = load_benchmark_questions(None)

    if not queries:
        print("Analiz edilecek soru bulunamadi.")
        sys.exit(1)

    print(f"\nToplam {len(queries)} soru analiz edilecek...")

    all_raw_scores: list[float] = []
    all_sigmoid_scores: list[float] = []
    all_calibrated_scores: list[float] = []
    top1_raw_scores: list[float] = []
    top1_sigmoid_scores: list[float] = []
    top1_calibrated_scores: list[float] = []
    query_results: list[dict[str, Any]] = []

    start_time = time.perf_counter()

    for idx, q in enumerate(queries, 1):
        query_text = q["soru"]
        dept = q.get("beklenen_dept", "")
        dept_for_search = None
        if dept and dept not in ("clarification", "announcement", "?") and "," not in dept:
            dept_for_search = dept

        results = analyze_single_query(
            query=query_text,
            retriever=retriever,
            reranker=reranker,
            department=dept_for_search,
            top_k=args.top_k,
        )

        print_query_results(query_text, results, idx)

        for r in results:
            all_raw_scores.append(r["raw_reranker_score"])
            all_sigmoid_scores.append(r["sigmoid_score"])
            all_calibrated_scores.append(r["calibrated_score"])

        if results:
            top1_raw_scores.append(results[0]["raw_reranker_score"])
            top1_sigmoid_scores.append(results[0]["sigmoid_score"])
            top1_calibrated_scores.append(results[0]["calibrated_score"])

        query_results.append({
            "query": query_text,
            "department": dept,
            "profile": q.get("_profile", ""),
            "results": results,
        })

    elapsed = time.perf_counter() - start_time

    print("\n" + "=" * 80)
    print("  ISTATISTIKLER")
    print("=" * 80)

    raw_stats = compute_statistics(all_raw_scores)
    sig_stats = compute_statistics(all_sigmoid_scores)
    cal_stats = compute_statistics(all_calibrated_scores)
    top1_raw_stats = compute_statistics(top1_raw_scores)
    top1_sig_stats = compute_statistics(top1_sigmoid_scores)
    top1_cal_stats = compute_statistics(top1_calibrated_scores)

    print_statistics(raw_stats, "Ham Reranker Skorlari (tum adaylar):")
    print_statistics(sig_stats, "Sigmoid Skorlar (tum adaylar):")
    print_statistics(cal_stats, "Kalibre Skorlar (tum adaylar):")
    print_statistics(top1_raw_stats, "Ham Top-1 Skorlar (her sorunun en iyisi):")
    print_statistics(top1_sig_stats, "Sigmoid Top-1 Skorlar (her sorunun en iyisi):")
    print_statistics(top1_cal_stats, "Kalibre Top-1 Skorlar (her sorunun en iyisi):")

    suggestion = suggest_sigmoid_params(raw_stats)
    if suggestion:
        print(f"\n{'='*80}")
        print("  SIGMOID KALIBRASYON ONERISI")
        print(f"{'='*80}")
        print(f"  Formul          : {suggestion['formula']}")
        print(f"  Shift (median)  : {suggestion['shift']}")
        print(f"  Scale (IQR)     : {suggestion['scale']}")
        print(f"  Direct-RAG esik : {suggestion['suggested_direct_rag_threshold']}")
        print(f"  Min-source esik : {suggestion['suggested_min_source_threshold']}")

    print(f"\nToplam sure: {elapsed:.1f}s")

    if args.output:
        report = generate_markdown_report(
            query_results, all_raw_scores, all_sigmoid_scores,
            all_calibrated_scores,
            top1_raw_scores, top1_sigmoid_scores, top1_calibrated_scores,
            reranker_model_name=reranker.model_name,
        )
        output_path = project_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nRapor kaydedildi: {output_path}")

        json_path = output_path.with_suffix(".json")
        json_data = {
            "model": reranker.model_name,
            "calibration": {
                "shift": _CALIBRATION_SHIFT,
                "scale": _CALIBRATION_SCALE,
            },
            "raw_stats": raw_stats,
            "sigmoid_stats": sig_stats,
            "calibrated_stats": cal_stats,
            "top1_raw_stats": top1_raw_stats,
            "top1_sigmoid_stats": top1_sig_stats,
            "top1_calibrated_stats": top1_cal_stats,
            "suggestion": suggestion,
            "queries": query_results,
        }
        json_path.write_text(
            json.dumps(json_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"JSON rapor: {json_path}")

    retriever.close()


if __name__ == "__main__":
    main()
