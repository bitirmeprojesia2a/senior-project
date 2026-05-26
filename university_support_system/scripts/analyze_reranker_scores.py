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
    python scripts/analyze_reranker_scores.py --output docs/archive/benchmarks/reranker_score_analysis.md
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
from src.core.text_normalization import normalize_text
from src.rag.retriever import HybridRetriever
from src.rag.reranker import CrossEncoderReranker
from src.rag.candidate_utils import deduplicate_candidate_dicts
from src.quality.evidence_answer_validator import infer_source_family

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

_BENCHMARK_SOURCE_OWNER_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "tuition_fee_catalog",
        ("katki_payi", "katkı_payı", "ogrenim_ucreti", "öğrenim_ücreti", "harc", "ücretleri"),
    ),
    (
        "international_policy",
        ("uluslararasi", "uluslararası", "yabanci", "yabancı", "yos", "yös", "tomer", "tömer", "ikamet"),
    ),
    (
        "curriculum_catalog",
        ("mufredat", "müfredat", "ders_plani", "ders_planı", "akts", "curriculum"),
    ),
    (
        "student_affairs_policy",
        (
            "sik_sorulan_sorular",
            "sık_sorulan_sorular",
            "ogrenci_isleri",
            "öğrenci_işleri",
            "yonerge",
            "yönerge",
            "yonetmelik",
            "yönetmelik",
            "on_lisans",
            "ön_lisans",
            "onlisans",
            "önlisans",
            "yatay_gecis",
            "yatay_geçiş",
            "cift_anadal",
            "çift_anadal",
            "cift_ana_dal",
            "çift_ana_dal",
            "yandal",
            "yan_dal",
            "staj",
            "yaz_okulu",
            "muafiyet",
            "intibak",
            "kimlik_karti",
            "kimlik_kartı",
            "bagil_degerlendirme",
            "bağıl_değerlendirme",
        ),
    ),
)

_EXPECTED_DEPARTMENT_OWNER_MAP: dict[str, set[str]] = {
    "student_affairs": {"student_affairs_policy", "academic_calendar"},
    "finance": {"tuition_fee_catalog", "student_affairs_policy"},
    "academic_programs": {"curriculum_catalog", "international_policy", "student_affairs_policy"},
}


def infer_benchmark_source_owner(*, source: str | None = None, claim: str | None = None) -> str | None:
    """Infer a lightweight source owner for benchmark reports only."""
    haystack = normalize_text(f"{source or ''} {claim or ''}")
    for owner, markers in _BENCHMARK_SOURCE_OWNER_MARKERS:
        if any(marker in haystack for marker in markers):
            return owner
    return infer_source_family(source=source) or infer_source_family(claim=claim)


def expected_department_matches_owner(expected_department: str, owner: str | None) -> bool:
    """Map benchmark department labels to compatible source-owner families."""
    owner = (owner or "").strip()
    if not owner:
        return False
    expected_parts = [
        part.strip()
        for part in expected_department.split(",")
        if part.strip() and part.strip() not in {"?", "clarification", "announcement"}
    ]
    if not expected_parts:
        return False
    return any(owner in _EXPECTED_DEPARTMENT_OWNER_MAP.get(part, set()) for part in expected_parts)


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


def calibrated_sigmoid(raw_logit: float, *, shift: float, scale: float) -> float:
    """reranker.py ile ayni kalibre sigmoid: sigmoid((logit - shift) / scale)."""
    adjusted = (raw_logit - shift) / scale
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
        source = candidate.get("source", "?")
        content = candidate.get("content", "")
        source_family = infer_benchmark_source_owner(source=source, claim=content[:420])
        results.append({
            "source": source,
            "collection": candidate.get("collection") or candidate.get("metadata", {}).get("collection"),
            "source_owner": candidate.get("metadata", {}).get("source_owner") or source_family,
            "source_family": source_family,
            "score_type": candidate.get("metadata", {}).get("score_type"),
            "content_preview": content[:120].replace("\n", " "),
            "pre_rerank_score": float(candidate.get("metadata", {}).get("pre_rerank_score", 0.0)),
            "raw_reranker_score": raw_float,
            "sigmoid_score": sig_score,
            "calibrated_score": round(
                calibrated_sigmoid(
                    raw_float,
                    shift=reranker.calibration_shift,
                    scale=reranker.calibration_scale,
                ),
                6,
            ),
            "content_length": len(content),
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


def compute_top1_source_owner_summary(query_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Return lightweight top-1 source-owner distribution and expected dept match."""
    counts: dict[str, int] = {}
    checked = 0
    matched = 0
    for item in query_results:
        results = item.get("results") or []
        if not results:
            continue
        top1 = results[0]
        owner = str(top1.get("source_owner") or top1.get("collection") or "-")
        counts[owner] = counts.get(owner, 0) + 1
        expected = str(item.get("department") or "").strip().lower()
        if not expected or expected in {"?", "clarification", "announcement"}:
            continue
        checked += 1
        owner = str(top1.get("source_owner") or top1.get("source_family") or "").strip()
        if expected_department_matches_owner(expected, owner):
            matched += 1
    return {
        "top1_source_owner_counts": counts,
        "expected_department_checked": checked,
        "expected_department_matched": matched,
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
    reranker_device: str = "?",
    reranker_torch_dtype: str = "?",
    calibration_shift: float = 0.0,
    calibration_scale: float = 1.0,
    elapsed_seconds: float = 0.0,
) -> str:
    """Markdown formatinda rapor uretir."""
    raw_stats = compute_statistics(all_raw_scores)
    sig_stats = compute_statistics(all_sigmoid_scores)
    cal_stats = compute_statistics(all_calibrated_scores)
    top1_raw_stats = compute_statistics(top1_raw_scores)
    top1_sig_stats = compute_statistics(top1_sigmoid_scores)
    top1_cal_stats = compute_statistics(top1_calibrated_scores)
    source_owner_summary = compute_top1_source_owner_summary(query_results)
    suggestion = suggest_sigmoid_params(raw_stats)

    lines = [
        "# Reranker Skor Dagilim Analizi",
        "",
        f"**Tarih:** {time.strftime('%Y-%m-%d %H:%M')}",
        f"**Model:** {reranker_model_name}",
        f"**Device:** {reranker_device}",
        f"**Torch dtype:** {reranker_torch_dtype}",
        f"**Kalibrasyon:** shift={calibration_shift}, scale={calibration_scale}",
        f"**Toplam Soru:** {len(query_results)}",
        f"**Toplam Skor Ornegi:** {len(all_raw_scores)}",
        f"**Toplam sure:** {elapsed_seconds:.1f}s",
        "**Kapsam:** Candidate pool + reranker analizi; final threshold/filtering adimlari buna dahil degildir.",
        "",
        "---",
        "",
        "## Top-1 Source Owner Ozeti",
        "",
        f"- Expected department match: {source_owner_summary['expected_department_matched']}/{source_owner_summary['expected_department_checked']}",
        "- Top-1 source owner dagilimi: "
        + (
            ", ".join(
                f"{owner}={count}"
                for owner, count in sorted(source_owner_summary["top1_source_owner_counts"].items())
            )
            or "-"
        ),
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
        lines.append("| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |")
        lines.append("|:-:|:--------:|:-------:|:-------:|--------------|--------|")
        for i, r in enumerate(results, 1):
            lines.append(
                f"| {i} | {r['raw_reranker_score']:.4f} | {r['calibrated_score']:.4f} | "
                f"{r['sigmoid_score']:.4f} | {r.get('source_owner') or '-'} | {r['source']} |"
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
        "--model",
        type=str,
        default=None,
        help=(
            "Reranker modeli. Bos birakilirsa RERANKER_MODEL kullanilir; "
            "Turkish shadow icin: seroe/bge-reranker-v2-m3-turkish-triplet"
        ),
    )
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default=None,
        help="Reranker cihazi. Bos birakilirsa RERANKER_DEVICE kullanilir.",
    )
    parser.add_argument(
        "--torch-dtype",
        choices=["auto", "float32", "float16", "bfloat16"],
        default=None,
        help="Model agirlik dtype'i. float16 yalniz CUDA'da uygulanir; CPU'da FP32 varsayilir.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Markdown rapor cikti dosyasi (ornegin: docs/archive/benchmarks/reranker_score_analysis.md)",
    )
    parser.add_argument(
        "--calibration-output",
        type=str,
        default=None,
        help="Sadece model ve onerilen kalibrasyon ozeti icin JSON cikti dosyasi.",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("  RERANKER SKOR DAGILIM ANALIZI")
    print("=" * 80)

    print("\nModeller yukleniyor...")
    retriever = HybridRetriever(cache_ttl=0)
    reranker = CrossEncoderReranker(
        model_name=args.model,
        device=args.device,
        torch_dtype=args.torch_dtype,
    )
    _ = reranker.model
    print(f"  Reranker: {reranker.model_name}")
    print(f"  Max Length: {reranker.max_length}")
    print(f"  Device: {reranker.resolved_device}")
    print(f"  Torch dtype: {reranker.torch_dtype_name} -> {reranker.torch_dtype}")
    print(f"  Calibration: shift={reranker.calibration_shift} scale={reranker.calibration_scale}")

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
    source_owner_summary = compute_top1_source_owner_summary(query_results)

    print_statistics(raw_stats, "Ham Reranker Skorlari (tum adaylar):")
    print_statistics(sig_stats, "Sigmoid Skorlar (tum adaylar):")
    print_statistics(cal_stats, "Kalibre Skorlar (tum adaylar):")
    print_statistics(top1_raw_stats, "Ham Top-1 Skorlar (her sorunun en iyisi):")
    print_statistics(top1_sig_stats, "Sigmoid Top-1 Skorlar (her sorunun en iyisi):")
    print_statistics(top1_cal_stats, "Kalibre Top-1 Skorlar (her sorunun en iyisi):")
    print("\nTop-1 Source Owner Dagilimi:")
    for owner, count in sorted(source_owner_summary["top1_source_owner_counts"].items()):
        print(f"  {owner}: {count}")
    print(
        "Expected department match: "
        f"{source_owner_summary['expected_department_matched']}/"
        f"{source_owner_summary['expected_department_checked']}"
    )

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
            reranker_device=reranker.resolved_device,
            reranker_torch_dtype=f"{reranker.torch_dtype_name}->{reranker.torch_dtype}",
            calibration_shift=reranker.calibration_shift,
            calibration_scale=reranker.calibration_scale,
            elapsed_seconds=elapsed,
        )
        output_path = project_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nRapor kaydedildi: {output_path}")

        json_path = output_path.with_suffix(".json")
        json_data = {
            "model": reranker.model_name,
            "device": {
                "requested": reranker.device,
                "resolved": reranker.resolved_device,
            },
            "torch_dtype": {
                "requested": reranker.torch_dtype_name,
                "resolved": str(reranker.torch_dtype),
            },
            "elapsed_seconds": round(elapsed, 3),
            "calibration": {
                "shift": reranker.calibration_shift,
                "scale": reranker.calibration_scale,
            },
            "raw_stats": raw_stats,
            "sigmoid_stats": sig_stats,
            "calibrated_stats": cal_stats,
            "top1_raw_stats": top1_raw_stats,
            "top1_sigmoid_stats": top1_sig_stats,
            "top1_calibrated_stats": top1_cal_stats,
            "source_owner_summary": source_owner_summary,
            "suggestion": suggestion,
            "queries": query_results,
        }
        json_path.write_text(
            json.dumps(json_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"JSON rapor: {json_path}")

    if args.calibration_output:
        calibration_path = project_root / args.calibration_output
        calibration_path.parent.mkdir(parents=True, exist_ok=True)
        calibration_payload = {
            "model": reranker.model_name,
            "device": reranker.resolved_device,
            "torch_dtype": {
                "requested": reranker.torch_dtype_name,
                "resolved": str(reranker.torch_dtype),
            },
            "runtime_calibration": {
                "shift": reranker.calibration_shift,
                "scale": reranker.calibration_scale,
            },
            "suggested_calibration": suggestion,
            "raw_stats": raw_stats,
            "top1_raw_stats": top1_raw_stats,
            "source_owner_summary": source_owner_summary,
            "elapsed_seconds": round(elapsed, 3),
        }
        calibration_path.write_text(
            json.dumps(calibration_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Kalibrasyon ozeti: {calibration_path}")

    retriever.close()


if __name__ == "__main__":
    main()
