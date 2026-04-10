"""Reranker Kalite Benchmark Scripti.

ms-marco-MiniLM-L-6-v2 reranker'inin zaman kazancinin kalite kaybina
yol acip acmadigini olcmek icin tasarlanmis 25 soruluk LLM-sentez-odakli
benchmark seti.

Kullanim:
  cd university_support_system
  python scripts/run_quality_benchmark.py                          # Tum sorular
  python scripts/run_quality_benchmark.py --category A             # Tek kategori
  python scripts/run_quality_benchmark.py --question Q5             # Tek soru
  python scripts/run_quality_benchmark.py --question Q8 Q13 Q16    # Birden fazla soru
  python scripts/run_quality_benchmark.py --cold-start             # Cold-start (model yeniden yukle)
  python scripts/run_quality_benchmark.py --use-api                # API uzerinden
  python scripts/run_quality_benchmark.py --use-api --api-base-url http://localhost:8000
  python scripts/run_quality_benchmark.py -v                       # Verbose mod
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from statistics import mean, median

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.console import configure_utf8_stdio

configure_utf8_stdio()

_verbose_argv = any(a in ("-v", "--verbose") for a in sys.argv)
os.environ["SERVER_DEBUG"] = "true" if _verbose_argv else "false"

from src.db.conversation_context import ConversationContextService
from src.db.connection import init_engine
from src.orchestrators.main import MainOrchestrator
from src.core.profiling import QueryProfiler, activate_profiler
from src.api.main import app as api_app
from httpx import ASGITransport, AsyncClient

BENCHMARK_FILE = Path(__file__).resolve().with_name("reranker_quality_benchmark.json")
REPORT_DIR = _ROOT / "docs"
RESULTS_DIR = _ROOT / "tests"

BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
SEP = "\u2500" * 70

_SUSPICIOUS_QUALITY_PATTERNS = (
    "bilmedigim icin", "bilemedigim icin", "genellikle",
    "genel olarak bilinen", "genel bilgiler verilebilir",
    "genel bilgi birikimime", "genel bilgi birikimimden",
    "tahminim", "tahminimce", "tahminen",
    "internette arastirdiginizda", "genelde boyle bilinir",
)
_FOREIGN_LANGUAGE_PATTERNS = (
    "however", "therefore", "furthermore", "moreover",
    "please note", "in addition", "regarding",
)
_ROLE_RECITATION_PATTERNS = (
    "harc ve odeme uzmani olarak", "kayit uzmani olarak",
    "mevzuat uzmani olarak", "uzman asistan olarak",
)


def _configure_logging(*, verbose: bool) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)
        logging.getLogger("sqlalchemy").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING, force=True)
        logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
        try:
            import structlog
            structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            )
        except Exception:
            pass


def _load_benchmark() -> dict:
    if not BENCHMARK_FILE.exists():
        raise FileNotFoundError(f"Benchmark dosyasi bulunamadi: {BENCHMARK_FILE}")
    return json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))


def _extract_generation_mode(answer: str) -> str:
    """Yanit metninin sonundaki 'Uretim Turu:' satirindan mod bilgisini cikarir."""
    match = re.search(r"Uretim Turu:\s*\n(.*?)(?:\n\n|$)", answer, re.DOTALL)
    if not match:
        return "unknown"
    block = match.group(1).strip().lower()
    modes = set()
    for token in ("vt", "rag", "llm", "kural"):
        if token in block:
            modes.add(token)
    if not modes:
        return "unknown"
    priority = ["llm", "vt", "rag", "kural"]
    for m in priority:
        if m in modes:
            return m
    return "unknown"


def _extract_departments(answer: str, response_depts: list[str]) -> list[str]:
    """Yanit metninden veya response'dan departman listesini cikarir."""
    if response_depts:
        return response_depts
    return []


def _check_key_facts(answer: str, expected_facts: list[str]) -> dict:
    """Beklenen anahtar bilgilerin yanit icinde olup olmadigini kontrol eder."""
    lowered = answer.casefold()
    results = {}
    for fact in expected_facts:
        results[fact] = fact.casefold() in lowered
    return results


def _quality_warnings(answer: str) -> list[str]:
    warnings: list[str] = []
    lowered = answer.casefold()
    if any(p in lowered for p in _SUSPICIOUS_QUALITY_PATTERNS):
        warnings.append("uydurma_riski")
    if any(p in lowered for p in _FOREIGN_LANGUAGE_PATTERNS):
        warnings.append("yabanci_dil")
    if any(p in lowered for p in _ROLE_RECITATION_PATTERNS):
        warnings.append("rol_tekrari")
    if len(answer.strip()) < 30:
        warnings.append("cok_kisa_yanit")
    return warnings


def _dept_match(actual: list[str], expected: list[str]) -> bool:
    return set(actual) == set(expected)


def _generation_mode_match(actual: str, expected: str) -> bool:
    if expected == "kural":
        return actual == "kural"
    if expected == "llm":
        return actual in ("llm",)
    return actual == expected


def _create_api_client(api_base_url: str | None = None) -> AsyncClient:
    if api_base_url:
        return AsyncClient(base_url=api_base_url.rstrip("/"))
    transport = ASGITransport(app=api_app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def run_single_question(
    orchestrator: MainOrchestrator,
    q: dict,
    *,
    api_client: AsyncClient | None = None,
    llm_profile: str | None = None,
) -> dict:
    qid = q["id"]
    question = q["question"]
    expected_depts = q["expected_departments"]
    expected_mode = q["expected_generation_mode"]
    expected_facts = q.get("expected_key_facts", [])
    category = q["category"]
    difficulty = q.get("difficulty", "medium")

    context_id = f"qbench-{qid}-{datetime.now().strftime('%H%M%S')}"

    print(f"\n  {CYAN}[{qid}]{RESET} {question}")
    print(f"  Kategori: {category} | Zorluk: {difficulty}")

    start = time.perf_counter()
    profiler = QueryProfiler(label=f"qbench_{qid}")
    try:
        with activate_profiler(profiler):
            if api_client is None:
                response = await orchestrator.handle_query(
                    question,
                    context_id=context_id,
                    llm_profile=llm_profile,
                    is_authenticated=False,
                    student_id=None,
                )
            else:
                api_response = await api_client.post(
                    "/query",
                    json={
                        "query": question,
                        "context_id": context_id,
                        "llm_profile": llm_profile,
                    },
                )
                api_response.raise_for_status()
                body = api_response.json()
                from types import SimpleNamespace
                response = SimpleNamespace(
                    answer=body.get("answer", ""),
                    departments_involved=body.get("departments_involved", []),
                    sources=body.get("sources", []),
                    response_time_ms=body.get("response_time_ms", 0.0),
                    query_id=body.get("query_id", context_id),
                )

        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        profile_snapshot = profiler.snapshot()

        answer_text = response.answer
        actual_depts = list(response.departments_involved)
        actual_mode = _extract_generation_mode(answer_text)
        fact_check = _check_key_facts(answer_text, expected_facts)
        facts_found = sum(1 for v in fact_check.values() if v)
        facts_total = len(expected_facts)
        warnings = _quality_warnings(answer_text)

        dept_ok = _dept_match(actual_depts, expected_depts)
        mode_ok = _generation_mode_match(actual_mode, expected_mode)

        routing_attrs = profile_snapshot.get("attributes", {}).get("routing", {})
        intent_data = routing_attrs.get("intent")

        dept_color = GREEN if dept_ok else RED
        mode_color = GREEN if mode_ok else RED
        facts_color = GREEN if facts_found == facts_total else (YELLOW if facts_found > 0 else RED)
        warn_color = GREEN if not warnings else MAGENTA

        print(f"  {BOLD}Departman:{RESET}  {dept_color}{actual_depts}{RESET}  (beklenen: {expected_depts})  {'OK' if dept_ok else 'YANLIS'}")
        print(f"  {BOLD}Uretim:{RESET}     {mode_color}{actual_mode}{RESET}  (beklenen: {expected_mode})  {'OK' if mode_ok else 'YANLIS'}")
        if intent_data:
            print(
                f"  {BOLD}Intent:{RESET}     "
                f"complexity={intent_data.get('complexity', '?')} "
                f"force_llm={intent_data.get('force_llm_synthesis', '?')} "
                f"is_personal={intent_data.get('is_personal', '?')} "
                f"query_type={intent_data.get('query_type', '?')}"
            )
        print(f"  {BOLD}Key Facts:{RESET}  {facts_color}{facts_found}/{facts_total}{RESET}")
        if expected_facts:
            for fact, found in fact_check.items():
                mark = f"{GREEN}+{RESET}" if found else f"{RED}-{RESET}"
                print(f"    {mark} {fact}")
        print(f"  {BOLD}Sure:{RESET}       {elapsed_ms} ms")
        print(f"  {BOLD}Kaynak:{RESET}     {len(response.sources)} adet")
        print(f"  {BOLD}Kalite:{RESET}     {warn_color}{'OK' if not warnings else ', '.join(warnings)}{RESET}")
        print(f"  {BOLD}Yanit:{RESET}")
        for line in answer_text.splitlines()[:15]:
            print(f"    {line}")
        if len(answer_text.splitlines()) > 15:
            print(f"    ... ({len(answer_text.splitlines()) - 15} satir daha)")

        return {
            "id": qid,
            "category": category,
            "question": question,
            "difficulty": difficulty,
            "expected_departments": expected_depts,
            "actual_departments": actual_depts,
            "dept_match": dept_ok,
            "expected_generation_mode": expected_mode,
            "actual_generation_mode": actual_mode,
            "mode_match": mode_ok,
            "expected_key_facts": expected_facts,
            "key_fact_results": fact_check,
            "key_facts_found": facts_found,
            "key_facts_total": facts_total,
            "elapsed_ms": elapsed_ms,
            "source_count": len(response.sources),
            "quality_warnings": warnings,
            "intent_analysis": intent_data,
            "answer": answer_text,
            "profiling": {
                "total_ms": round(profile_snapshot["total_ms"], 3),
                "events": profile_snapshot.get("events", []),
            },
            "error": None,
        }
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        print(f"  {RED}HATA:{RESET} {e}")
        return {
            "id": qid,
            "category": category,
            "question": question,
            "difficulty": difficulty,
            "expected_departments": expected_depts,
            "actual_departments": [],
            "dept_match": False,
            "expected_generation_mode": expected_mode,
            "actual_generation_mode": "error",
            "mode_match": False,
            "expected_key_facts": expected_facts,
            "key_fact_results": {},
            "key_facts_found": 0,
            "key_facts_total": len(expected_facts),
            "elapsed_ms": elapsed_ms,
            "source_count": 0,
            "quality_warnings": ["exception"],
            "answer": "",
            "profiling": {},
            "error": str(e),
        }


def print_summary(results: list[dict], categories: dict) -> None:
    print(f"\n{'=' * 70}")
    print(f"{BOLD}KALITE BENCHMARK OZETI{RESET}")
    print(f"{'=' * 70}")

    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    total_dept_ok = 0
    total_mode_ok = 0
    total_facts_found = 0
    total_facts_total = 0
    total_quality_ok = 0
    all_times: list[float] = []
    total = len(results)
    errors = sum(1 for r in results if r["error"])

    for cat_key in sorted(by_cat.keys()):
        cat_results = by_cat[cat_key]
        cat_display = categories.get(cat_key, {}).get("display_name", cat_key)
        cat_dept = sum(1 for r in cat_results if r["dept_match"])
        cat_mode = sum(1 for r in cat_results if r["mode_match"])
        cat_ff = sum(r["key_facts_found"] for r in cat_results)
        cat_ft = sum(r["key_facts_total"] for r in cat_results)
        cat_qok = sum(1 for r in cat_results if not r["quality_warnings"])
        cat_times = [r["elapsed_ms"] for r in cat_results]

        total_dept_ok += cat_dept
        total_mode_ok += cat_mode
        total_facts_found += cat_ff
        total_facts_total += cat_ft
        total_quality_ok += cat_qok
        all_times.extend(cat_times)

        n = len(cat_results)
        fact_pct = round(cat_ff / cat_ft * 100) if cat_ft > 0 else 100

        dept_c = GREEN if cat_dept == n else (YELLOW if cat_dept > 0 else RED)
        mode_c = GREEN if cat_mode == n else (YELLOW if cat_mode > 0 else RED)
        fact_c = GREEN if fact_pct >= 80 else (YELLOW if fact_pct >= 50 else RED)

        print(
            f"\n  {BOLD}{cat_display}{RESET} ({n} soru)"
        )
        print(
            f"    Dept: {dept_c}{cat_dept}/{n}{RESET}"
            f"  |  Mod: {mode_c}{cat_mode}/{n}{RESET}"
            f"  |  Facts: {fact_c}{cat_ff}/{cat_ft} ({fact_pct}%){RESET}"
            f"  |  Kalite: {cat_qok}/{n}"
            f"  |  Ort: {round(mean(cat_times))}ms"
        )

    fact_total_pct = round(total_facts_found / total_facts_total * 100) if total_facts_total > 0 else 100

    intent_used = sum(1 for r in results if r.get("intent_analysis"))
    force_llm_count = sum(
        1 for r in results
        if (r.get("intent_analysis") or {}).get("force_llm_synthesis")
    )

    print(f"\n{'=' * 70}")
    print(f"  {BOLD}TOPLAM ({total} soru):{RESET}")
    print(f"    Departman Dogrulugu:   {total_dept_ok}/{total} ({round(total_dept_ok/total*100)}%)")
    print(f"    Uretim Modu Dogrulugu: {total_mode_ok}/{total} ({round(total_mode_ok/total*100)}%)")
    print(f"    Anahtar Bilgi Kapsami: {total_facts_found}/{total_facts_total} ({fact_total_pct}%)")
    print(f"    Temiz Kalite:          {total_quality_ok}/{total} ({round(total_quality_ok/total*100)}%)")
    print(f"    Intent Analizi:        {intent_used}/{total} soru icin aktif")
    print(f"    Force LLM Sentez:      {force_llm_count}/{total} soruda zorlanmis")
    print(f"    Hatalar:               {errors}")
    print(f"    Ortalama Sure:         {round(mean(all_times))} ms")
    print(f"    Medyan Sure:           {round(median(all_times))} ms")
    print(f"    Min / Max Sure:        {round(min(all_times))} / {round(max(all_times))} ms")


def save_results(results: list[dict], benchmark_meta: dict) -> tuple[Path, Path]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = RESULTS_DIR / f"quality_benchmark_{timestamp}.json"
    payload = {
        "benchmark_version": benchmark_meta.get("version", "?"),
        "reranker_model": benchmark_meta.get("reranker_model", "?"),
        "run_timestamp": timestamp,
        "total_questions": len(results),
        "summary": {
            "dept_accuracy": round(
                sum(1 for r in results if r["dept_match"]) / len(results) * 100, 1
            ),
            "mode_accuracy": round(
                sum(1 for r in results if r["mode_match"]) / len(results) * 100, 1
            ),
            "key_fact_coverage": round(
                sum(r["key_facts_found"] for r in results)
                / max(sum(r["key_facts_total"] for r in results), 1)
                * 100,
                1,
            ),
            "clean_quality_pct": round(
                sum(1 for r in results if not r["quality_warnings"]) / len(results) * 100, 1
            ),
            "avg_time_ms": round(mean(r["elapsed_ms"] for r in results), 1),
            "median_time_ms": round(median(r["elapsed_ms"] for r in results), 1),
        },
        "results": results,
    }
    intent_used = sum(1 for r in results if r.get("intent_analysis"))
    force_llm_count = sum(
        1 for r in results
        if (r.get("intent_analysis") or {}).get("force_llm_synthesis")
    )
    payload["summary"]["intent_analysis_active"] = intent_used
    payload["summary"]["force_llm_synthesis_count"] = force_llm_count
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = REPORT_DIR / f"quality_benchmark_report_{timestamp}.md"
    md_lines = _generate_markdown_report(results, benchmark_meta, payload["summary"])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\n  JSON sonuclari: {json_path}")
    print(f"  Markdown rapor: {md_path}")
    return json_path, md_path


def _generate_markdown_report(
    results: list[dict], meta: dict, summary: dict
) -> list[str]:
    lines = [
        "# Reranker Kalite Benchmark Raporu",
        "",
        f"- **Tarih**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Reranker Modeli**: {meta.get('reranker_model', '?')}",
        f"- **Toplam Soru**: {len(results)}",
        "",
        "## Ozet Metrikler",
        "",
        "| Metrik | Deger |",
        "|--------|-------|",
        f"| Departman Dogrulugu | {summary['dept_accuracy']}% |",
        f"| Uretim Modu Dogrulugu | {summary['mode_accuracy']}% |",
        f"| Anahtar Bilgi Kapsami | {summary['key_fact_coverage']}% |",
        f"| Temiz Kalite Orani | {summary['clean_quality_pct']}% |",
        f"| Ortalama Sure | {summary['avg_time_ms']} ms |",
        f"| Medyan Sure | {summary['median_time_ms']} ms |",
        f"| Intent Analizi Aktif | {summary.get('intent_analysis_active', 0)}/{len(results)} |",
        f"| Force LLM Sentez | {summary.get('force_llm_synthesis_count', 0)}/{len(results)} |",
        "",
    ]

    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    for cat_key in sorted(by_cat.keys()):
        cat_results = by_cat[cat_key]
        cat_name = meta.get("categories", {}).get(cat_key, {}).get("display_name", cat_key)
        lines.append(f"## {cat_name}")
        lines.append("")
        lines.append("| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |")
        lines.append("|---|------|------|-----|-------|-----------|----------|")

        for r in cat_results:
            dept_mark = "OK" if r["dept_match"] else "YANLIS"
            mode_mark = "OK" if r["mode_match"] else f"YANLIS ({r['actual_generation_mode']})"
            facts_mark = f"{r['key_facts_found']}/{r['key_facts_total']}"
            warns = ", ".join(r["quality_warnings"]) if r["quality_warnings"] else "-"
            q_short = r["question"][:60] + ("..." if len(r["question"]) > 60 else "")
            lines.append(
                f"| {r['id']} | {q_short} | {dept_mark} | {mode_mark} | {facts_mark} | {r['elapsed_ms']} | {warns} |"
            )
        lines.append("")

    lines.append("## Soru Detaylari")
    lines.append("")
    for r in results:
        lines.append(f"### {r['id']}: {r['question']}")
        lines.append("")
        lines.append(f"- **Kategori**: {r['category']}")
        lines.append(f"- **Zorluk**: {r['difficulty']}")
        lines.append(f"- **Departman**: {r['actual_departments']} (beklenen: {r['expected_departments']}) - {'OK' if r['dept_match'] else 'YANLIS'}")
        lines.append(f"- **Uretim Modu**: {r['actual_generation_mode']} (beklenen: {r['expected_generation_mode']}) - {'OK' if r['mode_match'] else 'YANLIS'}")
        lines.append(f"- **Key Facts**: {r['key_facts_found']}/{r['key_facts_total']}")
        if r["expected_key_facts"]:
            for fact, found in r["key_fact_results"].items():
                lines.append(f"  - {'[x]' if found else '[ ]'} {fact}")
        intent = r.get("intent_analysis")
        if intent:
            lines.append(
                f"- **Intent Analizi**: complexity={intent.get('complexity', '?')}, "
                f"force_llm={intent.get('force_llm_synthesis', '?')}, "
                f"is_personal={intent.get('is_personal', '?')}, "
                f"query_type={intent.get('query_type', '?')}"
            )
        lines.append(f"- **Sure**: {r['elapsed_ms']} ms")
        lines.append(f"- **Kaynak Sayisi**: {r['source_count']}")
        if r["quality_warnings"]:
            lines.append(f"- **Uyarilar**: {', '.join(r['quality_warnings'])}")
        if r["error"]:
            lines.append(f"- **Hata**: {r['error']}")
        lines.append("")
        lines.append("**Yanit:**")
        lines.append("```")
        lines.append(r["answer"][:2000])
        if len(r["answer"]) > 2000:
            lines.append(f"... ({len(r['answer']) - 2000} karakter daha)")
        lines.append("```")
        lines.append("")

    return lines


async def main():
    parser = argparse.ArgumentParser(description="Reranker Kalite Benchmark")
    parser.add_argument("--category", type=str, default="",
                        help="Sadece belirli kategoriyi calistir (or. A, B_cross)")
    parser.add_argument("--question", type=str, nargs="+", default=[],
                        help="Bir veya birden fazla soruyu calistir (or. Q5 veya Q8 Q13 Q16)")
    parser.add_argument("--cold-start", action="store_true",
                        help="Cold-start testi (varsayilan: warm)")
    parser.add_argument("--use-api", action="store_true",
                        help="Sorgulari /query API uzerinden kos")
    parser.add_argument("--api-base-url", type=str, default="",
                        help="Gercek HTTP API taban URL'si")
    parser.add_argument("--llm-profile", type=str, default="",
                        help="LLM profil tercihi: fast | balanced | quality")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose mod")
    args = parser.parse_args()

    _configure_logging(verbose=args.verbose)
    init_engine(echo=args.verbose)

    benchmark = _load_benchmark()
    questions = benchmark["questions"]
    categories = benchmark.get("categories", {})

    if args.question:
        q_ids = {qid.upper() for qid in args.question}
        questions = [q for q in questions if q["id"].upper() in q_ids]
        if not questions:
            print(f"{RED}Soru bulunamadi: {', '.join(args.question)}{RESET}")
            return

    if args.category:
        cat_filter = args.category.upper()
        questions = [
            q for q in questions
            if q["category"].upper().startswith(cat_filter)
        ]
        if not questions:
            print(f"{RED}Kategori bulunamadi: {args.category}{RESET}")
            return

    print(f"{BOLD}Reranker Kalite Benchmark{RESET}")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {benchmark.get('reranker_model', '?')}")
    print(f"Soru Sayisi: {len(questions)}")
    if args.cold_start:
        print(f"{YELLOW}Cold-start modu aktif{RESET}")
    print(SEP)

    print("Orchestrator baslatiliyor...")
    orchestrator = MainOrchestrator(
        conversation_service=ConversationContextService(),
    )
    print("Hazir.")

    if not args.cold_start:
        print("Warm-up sorgusu gonderiliyor...")
        warmup_start = time.perf_counter()
        try:
            await orchestrator.handle_query(
                "Test sorgusu",
                context_id="warmup-benchmark",
                is_authenticated=False,
            )
        except Exception:
            pass
        warmup_ms = round((time.perf_counter() - warmup_start) * 1000)
        print(f"Warm-up tamamlandi ({warmup_ms} ms).")

    results: list[dict] = []
    api_client: AsyncClient | None = None

    if args.use_api:
        api_client = _create_api_client(args.api_base_url or None)

    try:
        for i, q in enumerate(questions, 1):
            cat_display = categories.get(q["category"], {}).get("display_name", q["category"])
            if i == 1 or (i > 1 and questions[i - 2]["category"] != q["category"]):
                print(f"\n{SEP}")
                print(f"{BOLD}{cat_display}{RESET}")
                print(SEP)

            result = await run_single_question(
                orchestrator,
                q,
                api_client=api_client,
                llm_profile=args.llm_profile or None,
            )
            results.append(result)
    finally:
        if api_client is not None:
            await api_client.aclose()

    print_summary(results, categories)
    save_results(results, benchmark)


if __name__ == "__main__":
    asyncio.run(main())
