"""
RAG Değerlendirme Scripti

data/test/rag_test_questions.json dosyasındaki test soruları ile RAG pipeline'ını
değerlendirir. Precision@k, kaynak doğruluğu ve performans metrikleri hesaplar.

Kullanım:
    python scripts/evaluate_rag.py
    python scripts/evaluate_rag.py --top-k 3
    python scripts/evaluate_rag.py --output docs/archive/benchmarks/rag_evaluation_report.md
    python scripts/evaluate_rag.py --department academic_programs
"""

import argparse
import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.console import configure_utf8_stdio
from src.core.constants import department_values
from src.rag.retriever import HybridRetriever

configure_utf8_stdio()


def load_test_questions(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]


def filter_questions_by_department(questions: list, department: str | None) -> list:
    """Soru listesini departman alanına göre filtreler."""
    if not department:
        return questions
    return [q for q in questions if q.get("department") == department]


def check_source_match(results: list, expected_patterns: list) -> dict:
    """Sonuçların kaynak dosya adlarının beklenen kalıplarla eşleşip eşleşmediğini kontrol eder."""
    matches = []
    for i, result in enumerate(results):
        source = result.get("source", "").lower()
        matched = any(p.lower() in source for p in expected_patterns)
        matches.append({
            "rank": i + 1,
            "source": result.get("source", "?"),
            "score": round(result.get("score", 0.0), 4),
            "matched": matched,
        })
    return {
        "top1_match": matches[0]["matched"] if matches else False,
        "any_top3_match": any(m["matched"] for m in matches[:3]),
        "any_top5_match": any(m["matched"] for m in matches[:5]),
        "details": matches,
    }


def evaluate(
    questions: list,
    retriever: HybridRetriever,
    top_k: int,
    department: str | None = None,
) -> list:
    """Tüm soruları değerlendirir."""
    results = []
    total_time_ms = 0.0

    for q in questions:
        qid = q["id"]
        question = q["question"]
        expected = q["expected_source_patterns"]

        start = time.perf_counter()
        search_results = retriever.search(question, top_k=top_k, department=department)
        elapsed_ms = (time.perf_counter() - start) * 1000
        total_time_ms += elapsed_ms

        source_check = check_source_match(search_results, expected)

        entry = {
            "id": qid,
            "question": question,
            "expected_topic": q.get("expected_topic", ""),
            "difficulty": q.get("difficulty", ""),
            "category": q.get("category", ""),
            "top1_match": source_check["top1_match"],
            "any_top3_match": source_check["any_top3_match"],
            "any_top5_match": source_check["any_top5_match"],
            "result_count": len(search_results),
            "top1_score": search_results[0]["score"] if search_results else 0.0,
            "top1_source": search_results[0]["source"] if search_results else "N/A",
            "elapsed_ms": round(elapsed_ms, 1),
            "details": source_check["details"],
        }
        results.append(entry)

        status = "✅" if source_check["any_top3_match"] else "❌"
        print(f"  {status} [{qid:2d}] {question[:60]:<60} "
              f"top1={'✓' if source_check['top1_match'] else '✗'}  "
              f"top3={'✓' if source_check['any_top3_match'] else '✗'}  "
              f"{elapsed_ms:7.0f}ms")

    avg_ms = total_time_ms / len(questions) if questions else 0
    print(f"\n  Ortalama yanıt süresi: {avg_ms:.0f}ms")
    return results


def compute_metrics(results: list) -> dict:
    total = len(results)
    if total == 0:
        return {}

    top1_correct = sum(1 for r in results if r["top1_match"])
    top3_correct = sum(1 for r in results if r["any_top3_match"])
    top5_correct = sum(1 for r in results if r["any_top5_match"])

    avg_score = sum(r["top1_score"] for r in results) / total
    avg_ms = sum(r["elapsed_ms"] for r in results) / total

    by_difficulty = {}
    for diff in ["easy", "medium", "hard"]:
        subset = [r for r in results if r["difficulty"] == diff]
        if subset:
            by_difficulty[diff] = {
                "total": len(subset),
                "precision_at_3": sum(1 for r in subset if r["any_top3_match"]) / len(subset),
            }

    return {
        "total_questions": total,
        "precision_at_1": round(top1_correct / total, 3),
        "precision_at_3": round(top3_correct / total, 3),
        "precision_at_5": round(top5_correct / total, 3),
        "avg_top1_score": round(avg_score, 4),
        "avg_response_ms": round(avg_ms, 1),
        "by_difficulty": by_difficulty,
    }


def generate_report(results: list, metrics: dict, top_k: int) -> str:
    lines = [
        "# RAG Değerlendirme Raporu",
        "",
        f"**Tarih:** {time.strftime('%d %B %Y')}  ",
        f"**Test Sorusu Sayısı:** {metrics['total_questions']}  ",
        f"**Top-K:** {top_k}  ",
        "",
        "---",
        "",
        "## Özet Metrikler",
        "",
        "| Metrik | Değer |",
        "|--------|-------|",
        f"| Precision@1 | {metrics['precision_at_1']:.1%} |",
        f"| Precision@3 | {metrics['precision_at_3']:.1%} |",
        f"| Precision@5 | {metrics['precision_at_5']:.1%} |",
        f"| Ortalama Top-1 Skor | {metrics['avg_top1_score']:.4f} |",
        f"| Ortalama Yanıt Süresi | {metrics['avg_response_ms']:.0f} ms |",
        "",
    ]

    if metrics.get("by_difficulty"):
        lines.extend([
            "### Zorluk Seviyesine Göre",
            "",
            "| Zorluk | Soru Sayısı | Precision@3 |",
            "|--------|:-----------:|:-----------:|",
        ])
        for diff, data in metrics["by_difficulty"].items():
            lines.append(f"| {diff} | {data['total']} | {data['precision_at_3']:.1%} |")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Detaylı Sonuçlar",
        "",
        "| # | Soru | Top-1 Doğru | Top-3 Doğru | Skor | Kaynak | Süre |",
        "|:-:|------|:-----------:|:-----------:|:----:|--------|:----:|",
    ])

    for r in results:
        t1 = "✅" if r["top1_match"] else "❌"
        t3 = "✅" if r["any_top3_match"] else "❌"
        q_short = r["question"][:50] + ("..." if len(r["question"]) > 50 else "")
        lines.append(
            f"| {r['id']} | {q_short} | {t1} | {t3} | "
            f"{r['top1_score']:.3f} | {r['top1_source']} | {r['elapsed_ms']:.0f}ms |"
        )

    failed = [r for r in results if not r["any_top3_match"]]
    if failed:
        lines.extend([
            "",
            "---",
            "",
            "## Başarısız Sorgular Analizi",
            "",
        ])
        for r in failed:
            lines.append(f"### Soru {r['id']}: {r['question']}")
            lines.append(f"- **Beklenen konu:** {r['expected_topic']}")
            lines.append(f"- **Dönen kaynak:** {r['top1_source']}")
            lines.append(f"- **Skor:** {r['top1_score']:.4f}")
            lines.append("")

    lines.extend([
        "",
        "---",
        "",
        "*Bu rapor `scripts/evaluate_rag.py` tarafından otomatik üretilmiştir.*",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="RAG pipeline değerlendirmesi")
    parser.add_argument("--top-k", type=int, default=5, help="Sonuç sayısı (varsayılan: 5)")
    parser.add_argument(
        "--questions",
        type=str,
        default="data/test/rag_test_questions.json",
        help="Test soruları dosyası",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="docs/archive/benchmarks/rag_evaluation_report.md",
        help="Rapor çıktı dosyası",
    )
    parser.add_argument(
        "--department",
        type=str,
        choices=department_values(),
        default=None,
        help="Değerlendirmeyi belirli bir departmanla sınırla",
    )
    parser.add_argument("--no-cache", action="store_true", help="Sorgu cache'ini devre dışı bırak")
    args = parser.parse_args()

    questions_path = project_root / args.questions
    if not questions_path.exists():
        print(f"❌ Test soruları bulunamadı: {questions_path}")
        sys.exit(1)

    questions = load_test_questions(questions_path)
    questions = filter_questions_by_department(questions, args.department)
    if not questions:
        print("❌ Seçilen departman için soru bulunamadı.")
        sys.exit(1)

    print("=" * 70)
    print("  RAG Değerlendirme")
    print("=" * 70)
    if args.department:
        print(f"  Departman:   {args.department}")
    print(f"  Soru sayısı: {len(questions)}")
    print(f"  Top-K:       {args.top_k}")
    print("=" * 70)
    print()

    cache_ttl = 0 if args.no_cache else 300
    retriever = HybridRetriever(cache_ttl=cache_ttl)

    try:
        results = evaluate(
            questions,
            retriever,
            args.top_k,
            department=args.department,
        )
        metrics = compute_metrics(results)

        print("\n" + "=" * 70)
        print("  Sonuçlar")
        print("=" * 70)
        print(f"  Precision@1: {metrics['precision_at_1']:.1%}")
        print(f"  Precision@3: {metrics['precision_at_3']:.1%}")
        print(f"  Precision@5: {metrics['precision_at_5']:.1%}")
        print(f"  Ort. Skor:   {metrics['avg_top1_score']:.4f}")
        print(f"  Ort. Süre:   {metrics['avg_response_ms']:.0f}ms")
        print("=" * 70)

        report = generate_report(results, metrics, args.top_k)
        output_path = project_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\n📄 Rapor kaydedildi: {output_path}")

        json_path = output_path.with_suffix(".json")
        json_data = {"metrics": metrics, "results": results}
        json_path.write_text(
            json.dumps(json_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"📊 JSON rapor:      {json_path}")

    finally:
        retriever.close()


if __name__ == "__main__":
    main()
