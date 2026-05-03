"""Duyuru sistemi icin kalite benchmark scripti.

Tek tek unit test yerine, gercek orchestrator akisindan gecen duyuru
senaryolarini grup halinde calistirir ve kalite sinyallerini ozetler.

Kullanim:
  cd university_support_system
  python scripts/announcement_benchmark.py
  python scripts/announcement_benchmark.py --group A C
  python scripts/announcement_benchmark.py -v
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.console import configure_utf8_stdio

configure_utf8_stdio()

_verbose_argv = any(arg in ("-v", "--verbose") for arg in sys.argv)
os.environ["SERVER_DEBUG"] = "true" if _verbose_argv else "false"

from src.db.conversation_context import ConversationContextService
from src.db.connection import init_engine
from src.orchestrators.main import MainOrchestrator

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
SEP = "\u2500" * 70

_SUSPICIOUS_QUALITY_PATTERNS = (
    "bilmedigim icin",
    "bilemedigim icin",
    "genellikle",
    "genel olarak",
    "yardimci olabilmem icin",
    "daha detayli aciklayabilirsiniz",
)
_FOREIGN_LANGUAGE_PATTERNS = (
    "however",
    "therefore",
    "furthermore",
    "por favor",
    "please note",
)

BENCHMARK_GROUPS: dict[str, dict] = {
    "A": {
        "name": "Dogrudan Duyuru Sorgulari",
        "shared_context": False,
        "turns": [
            {
                "query": "Son duyurular neler?",
                "expected_departments_exact": ["announcement"],
                "required_terms": [],
                "require_detail_link": True,
            },
            {
                "query": "Muhendislik fakultesindeki son duyurular neler?",
                "expected_departments_exact": ["announcement"],
                "required_terms": ["muhendislik"],
                "require_detail_link": True,
            },
            {
                "query": "Bilgisayar muhendisligindeki son duyurular neler?",
                "expected_departments_exact": ["announcement"],
                "required_terms": ["bilgisayar", "muhendisligi"],
                "require_detail_link": True,
            },
        ],
    },
    "B": {
        "name": "Ek Baglanti / Dosya Linki",
        "shared_context": False,
        "turns": [
            {
                "query": "Bilgisayar muhendisligi ara sinav programi duyurusu var mi?",
                "expected_departments_contains": ["announcement"],
                "required_terms": ["sinav", "program"],
                "require_detail_link": True,
                "require_attachment_link": True,
            },
            {
                "query": "Bilgisayar muhendisligi haftalik ders programi duyurusu var mi?",
                "expected_departments_contains": ["announcement"],
                "required_terms": ["ders", "program"],
                "require_detail_link": True,
                "require_attachment_link": True,
            },
        ],
    },
    "C": {
        "name": "Follow-up Duyuru Akisi",
        "shared_context": True,
        "turns": [
            {
                "query": "Bilgisayar muhendisligindeki son duyurular neler?",
                "expected_departments_exact": ["announcement"],
                "required_terms": ["bilgisayar", "muhendisligi"],
                "require_detail_link": True,
            },
            {
                "query": "Peki sinav programi ile ilgili olan var mi?",
                "expected_departments_contains": ["announcement"],
                "required_terms": ["sinav", "program"],
                "require_detail_link": True,
                "require_attachment_link": True,
            },
            {
                "query": "Bir de ders programi linki olan var mi?",
                "expected_departments_contains": ["announcement"],
                "required_terms": ["ders", "program"],
                "require_detail_link": True,
                "require_attachment_link": True,
            },
        ],
    },
    "D": {
        "name": "Akademik Cevaba Ilgili Duyuru Ekleme",
        "shared_context": False,
        "turns": [
            {
                "query": "Bilgisayar muhendisligi ara sinav programi nereden takip edilir?",
                "expected_departments_contains": ["announcement"],
                "required_terms": ["sinav", "program"],
                "require_detail_link": True,
                "prefer_related_announcements": True,
            },
            {
                "query": "Bilgisayar muhendisligi tek ders sinavi duyurusu var mi?",
                "expected_departments_contains": ["announcement"],
                "required_terms": ["tek ders", "sinav"],
                "require_detail_link": True,
            },
        ],
    },
}


def _configure_logging(*, verbose: bool) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)
    else:
        logging.basicConfig(level=logging.WARNING, force=True)
        logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
        try:
            import structlog

            structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING),
            )
        except Exception:
            pass
    logging.getLogger("src.db.conversation_context").setLevel(logging.INFO)


def _normalize_for_match(text: str) -> str:
    return (
        text.casefold()
        .replace("ı", "i")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ş", "s")
        .replace("ö", "o")
        .replace("ç", "c")
    )


def _quality_warnings(answer: str, *, source_count: int) -> list[str]:
    lowered = _normalize_for_match(answer)
    warnings: list[str] = []
    if source_count == 0:
        warnings.append("kaynak_yok")
    if any(pattern in lowered for pattern in _SUSPICIOUS_QUALITY_PATTERNS):
        warnings.append("zayif_netlik")
    if any(pattern in lowered for pattern in _FOREIGN_LANGUAGE_PATTERNS):
        warnings.append("yabanci_dil")
    if len(answer.strip()) < 40:
        warnings.append("cok_kisa")
    return warnings


def _departments_match(actual: list[str], turn: dict) -> bool:
    exact = turn.get("expected_departments_exact")
    if exact is not None:
        return list(actual) == list(exact)

    contains = turn.get("expected_departments_contains") or []
    return set(contains).issubset(set(actual))


def _terms_match(answer: str, required_terms: list[str]) -> bool:
    lowered = _normalize_for_match(answer)
    return all(_normalize_for_match(term) in lowered for term in required_terms)


def _has_detail_link(answer: str) -> bool:
    return "Detay: http" in answer


def _has_attachment_link(answer: str) -> bool:
    return "Ek baglanti:" in answer


def _has_related_announcements_block(answer: str) -> bool:
    return "Ilgili duyurular" in answer


def _format_preview(answer: str, *, max_lines: int = 8, max_chars: int = 360) -> str:
    clipped = answer[:max_chars]
    if len(answer) > max_chars:
        clipped += "..."
    lines = clipped.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append("...")
    return "\n".join(lines)


async def run_group(orchestrator: MainOrchestrator, group_key: str, group: dict) -> list[dict]:
    shared_context = bool(group.get("shared_context"))
    context_id = f"announcement-bench-{group_key}-{int(time.time())}"
    results: list[dict] = []

    print(f"\n{'=' * 70}")
    print(f"  {BOLD}GRUP {group_key}: {group['name']}{RESET}")
    print(f"  context_id = {context_id if shared_context else '(turn-bazli)'}")
    print(f"{'=' * 70}")

    for index, turn in enumerate(group["turns"], start=1):
        query = turn["query"]
        turn_context_id = context_id if shared_context else f"{context_id}-t{index}"

        print(f"\n{SEP}")
        print(f"  {CYAN}Tur {index}:{RESET} {query}")
        print(SEP)

        start = time.perf_counter()
        try:
            response = await orchestrator.handle_query(
                query,
                context_id=turn_context_id,
                student_number="21060731",
                student_full_name="Test Kullanici",
                student_department="Bilgisayar Muhendisligi",
                student_faculty="Muhendislik Fakultesi",
                is_authenticated=False,
            )
            elapsed = round(time.perf_counter() - start, 2)

            answer = response.answer or ""
            departments = list(response.departments_involved)
            source_count = len(response.sources)
            dept_ok = _departments_match(departments, turn)
            terms_ok = _terms_match(answer, turn.get("required_terms", []))
            detail_ok = (not turn.get("require_detail_link")) or _has_detail_link(answer)
            attachment_ok = (not turn.get("require_attachment_link")) or _has_attachment_link(answer)
            related_ok = (not turn.get("prefer_related_announcements")) or _has_related_announcements_block(answer)
            warnings = _quality_warnings(answer, source_count=source_count)
            passed = dept_ok and terms_ok and detail_ok and attachment_ok and related_ok

            status_color = GREEN if passed else RED
            print(f"  {BOLD}Durum:{RESET}      {status_color}{'GECTI' if passed else 'KALDI'}{RESET}")
            print(f"  {BOLD}Sure:{RESET}       {elapsed:.2f}s")
            print(f"  {BOLD}Departman:{RESET}  {departments}")
            print(f"  {BOLD}Kaynak:{RESET}     {source_count}")
            print(f"  {BOLD}Kontroller:{RESET}")
            print(f"    Dept:        {'OK' if dept_ok else 'HATA'}")
            print(f"    Anahtar Soz: {'OK' if terms_ok else 'HATA'}")
            print(f"    Detay Link:  {'OK' if detail_ok else 'HATA'}")
            if turn.get('require_attachment_link'):
                print(f"    Ek Baglanti: {'OK' if attachment_ok else 'HATA'}")
            if turn.get('prefer_related_announcements'):
                print(f"    Ilgili Blok: {'OK' if related_ok else 'HATA'}")
            print(f"  {BOLD}Kalite:{RESET}     {', '.join(warnings) if warnings else 'temiz'}")
            print(f"  {BOLD}Yanit:{RESET}")
            for line in _format_preview(answer).splitlines():
                print(f"    {line}")

            results.append(
                {
                    "group": group_key,
                    "turn": index,
                    "query": query,
                    "context_id": turn_context_id,
                    "passed": passed,
                    "elapsed_s": elapsed,
                    "departments": departments,
                    "source_count": source_count,
                    "warnings": warnings,
                    "error": None,
                }
            )
        except Exception as exc:
            elapsed = round(time.perf_counter() - start, 2)
            print(f"  {RED}HATA ({elapsed:.2f}s): {type(exc).__name__}: {exc}{RESET}")
            results.append(
                {
                    "group": group_key,
                    "turn": index,
                    "query": query,
                    "context_id": turn_context_id,
                    "passed": False,
                    "elapsed_s": elapsed,
                    "departments": [],
                    "source_count": 0,
                    "warnings": ["exception"],
                    "error": str(exc),
                }
            )

        if index < len(group["turns"]):
            await asyncio.sleep(2)

    return results


async def main() -> None:
    parser = argparse.ArgumentParser(description="Duyuru kalite benchmark testi")
    parser.add_argument("--group", type=str, nargs="+", default=[], help="Calistirilacak gruplar: A B C D")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mod")
    args = parser.parse_args()

    _configure_logging(verbose=args.verbose)
    init_engine(echo=args.verbose)

    if args.group:
        selected = {key: value for key, value in BENCHMARK_GROUPS.items() if key in {item.upper() for item in args.group}}
        if not selected:
            print(f"{RED}Grup bulunamadi: {', '.join(args.group)}{RESET}")
            print(f"Gecerli gruplar: {', '.join(BENCHMARK_GROUPS.keys())}")
            return
    else:
        selected = BENCHMARK_GROUPS

    print(f"\n{BOLD}Duyuru Kalite Benchmark{RESET}")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Grup Sayisi: {len(selected)}")
    total_turns = sum(len(group["turns"]) for group in selected.values())
    print(f"Toplam Tur: {total_turns}")
    print(SEP)

    print("Orchestrator baslatiliyor...")
    orchestrator = MainOrchestrator(
        conversation_service=ConversationContextService(),
    )
    print("Hazir.\n")

    print("Warm-up sorgusu gonderiliyor...")
    warmup_start = time.perf_counter()
    try:
        await orchestrator.handle_query(
            "Test duyuru sorgusu",
            context_id="warmup-announcement-benchmark",
            is_authenticated=False,
        )
    except Exception:
        pass
    warmup_ms = round((time.perf_counter() - warmup_start) * 1000)
    print(f"Warm-up tamamlandi ({warmup_ms} ms).")

    all_results: list[dict] = []
    for group_key, group in selected.items():
        group_results = await run_group(orchestrator, group_key, group)
        all_results.extend(group_results)
        await asyncio.sleep(3)

    print(f"\n{'=' * 70}")
    print(f"{BOLD}OZET{RESET}")
    print(f"{'=' * 70}")

    total = len(all_results)
    passed = sum(1 for result in all_results if result["passed"])
    errors = sum(1 for result in all_results if result["error"])
    avg_time = sum(result["elapsed_s"] for result in all_results) / total if total else 0.0
    clean = sum(1 for result in all_results if not result["warnings"])

    print(f"  Toplam Tur:    {total}")
    print(f"  Basarili:      {passed}")
    print(f"  Hatali:        {errors}")
    print(f"  Temiz Kalite:  {clean}/{total}")
    print(f"  Ort. Sure:     {avg_time:.2f}s")
    print(f"\n  {BOLD}Not:{RESET} Bu benchmark gercek DB + gercek orchestrator akisi ile calisir.")
    print(f"  {DIM}Ozellikle departman, detay linki, ek baglanti ve follow-up davranisina bakin.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
