"""Follow-up Mekanizmasi E2E Test Scripti.

Dogrudan MainOrchestrator uzerinden coklu tur sohbet testi yapar.

Kullanim:
  cd university_support_system
  python scripts/test_followup.py                   # Tum gruplar
  python scripts/test_followup.py --group A          # Tek grup
  python scripts/test_followup.py --group A B        # Birden fazla grup
  python scripts/test_followup.py -v                 # Verbose mod
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

_verbose_argv = any(a in ("-v", "--verbose") for a in sys.argv)
os.environ["SERVER_DEBUG"] = "true" if _verbose_argv else "false"

from src.db.conversation_context import ConversationContextService
from src.db.connection import init_engine
from src.orchestrators.main import MainOrchestrator

# ── Renkler ──────────────────────────────────────────────────────────
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
SEP = "\u2500" * 65

# ── Test Gruplari ────────────────────────────────────────────────────
TEST_GROUPS: dict[str, dict] = {
    "A": {
        "name": "Temel Follow-up Algilama",
        "turns": [
            ("CAP basvurusu nasil yapilir?",
             "is_follow_up=false, topic=CAP, dept=student_affairs+academic_programs"),
            ("Peki not ortalamasi kac olmali?",
             "is_follow_up=true, effective_query ~= CAP icin not ortalamasi"),
            ("Bunun icin hangi belge gerekli?",
             "is_follow_up=true, 'bunun' zamiri cozulmeli"),
            ("Erasmus basvurusu nasil yapilir?",
             "is_follow_up=false, yeni konu, topic degismeli"),
        ],
    },
    "B": {
        "name": "Suffix/Marker Bug Fix Dogrulama",
        "turns": [
            ("Kayit dondurma islemi nasil yapilir?",
             "is_follow_up=false"),
            ("Ucreti nedir?",
             "is_follow_up=true, 'nedir' marker ile yakalanmali"),
            ("Ne zaman yapilir?",
             "is_follow_up=true, 'ne zaman' marker"),
            ("Kosullari nelerdir?",
             "is_follow_up=true, 'nelerdir' marker"),
        ],
    },
    "C": {
        "name": "Kisa / Anlamsiz Soru Filtresi",
        "turns": [
            ("Yaz okulu hakkinda bilgi verir misin?",
             "is_follow_up=false"),
            ("Evet",
             "Turbo kelime -> is_follow_up=false"),
            ("Tesekkurler",
             "Turbo kelime -> is_follow_up=false"),
        ],
    },
    "D": {
        "name": "Konu Degisimi",
        "turns": [
            ("Harc ucreti ne kadar?",
             "topic=Harc, dept=finance"),
            ("Taksitle odeyebilir miyim?",
             "is_follow_up=true, ayni konu, dept=finance"),
            ("Burs basvurusu ne zaman?",
             "is_follow_up=false, yeni konu"),
            ("Peki GNO sarti var mi?",
             "is_follow_up=true, burs baglaminda GNO"),
        ],
    },
    "E": {
        "name": "Cok Departmanli Gecis",
        "turns": [
            ("Kayit dondurma nasil yapilir?",
             "dept=student_affairs"),
            ("Bu durumda harc odenir mi?",
             "is_follow_up=true, kayit dondurma + harc"),
            ("Peki ne kadar odenir?",
             "is_follow_up=true, dept beklenen=finance"),
        ],
    },
    "F": {
        "name": "Belirsiz Zamir Cozumleme",
        "turns": [
            ("Staj basvurusu icin hangi belgeler gerekli?",
             "dept=student_affairs"),
            ("Onlari nereden alirim?",
             "is_follow_up=true, 'onlari' -> staj belgeleri"),
            ("Suresi ne kadar?",
             "is_follow_up=true, 'suresi' -> staj suresi"),
        ],
    },
    "G": {
        "name": "LLM Rewrite Dogrulama",
        "turns": [
            ("Yatay gecis basvurusu nasil yapilir?",
             "Normal soru"),
            ("Not ortalamasi kac olmali?",
             "LLM rewrite: Yatay gecis icin not ortalamasi"),
            ("Peki kontenjan var mi?",
             "LLM rewrite: Yatay gecis icin kontenjan"),
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
    # conversation_resolution loglarini her zaman goster
    logging.getLogger("src.db.conversation_context").setLevel(logging.INFO)


async def run_group(
    orchestrator: MainOrchestrator,
    group_key: str,
    group: dict,
) -> list[dict]:
    ctx = f"followup-{group_key}-{int(time.time())}"
    results: list[dict] = []

    print(f"\n{'=' * 65}")
    print(f"  {BOLD}GRUP {group_key}: {group['name']}{RESET}")
    print(f"  context_id = {ctx}")
    print(f"{'=' * 65}")

    for i, (query, expected) in enumerate(group["turns"], 1):
        print(f"\n{SEP}")
        print(f"  {CYAN}Tur {i}:{RESET} {query}")
        print(f"  {DIM}Beklenen: {expected}{RESET}")
        print(SEP)

        start = time.perf_counter()
        try:
            response = await orchestrator.handle_query(
                query,
                context_id=ctx,
                student_number="21060731",
                student_full_name="Test Kullanici",
                student_department="Bilgisayar Muhendisligi",
                student_faculty="Muhendislik Fakultesi",
                is_authenticated=False,
            )
            elapsed = time.perf_counter() - start

            answer_text = response.answer or ""
            answer_preview = answer_text[:200]
            if len(answer_text) > 200:
                answer_preview += "..."

            print(f"\n  {BOLD}Sure:{RESET}        {elapsed:.2f}s")
            print(f"  {BOLD}Departman:{RESET}   {list(response.departments_involved)}")
            print(f"  {BOLD}Strateji:{RESET}    {response.strategy}")
            print(f"  {BOLD}Guven:{RESET}       {response.confidence}")
            print(f"  {BOLD}Yanit:{RESET}")
            for line in answer_preview.splitlines()[:6]:
                print(f"    {line}")

            results.append({
                "group": group_key,
                "turn": i,
                "query": query,
                "expected": expected,
                "departments": list(response.departments_involved),
                "strategy": str(response.strategy),
                "confidence": response.confidence,
                "elapsed_s": round(elapsed, 2),
                "answer_preview": answer_preview,
                "error": None,
            })
        except Exception as exc:
            elapsed = time.perf_counter() - start
            print(f"\n  {RED}HATA ({elapsed:.2f}s): {type(exc).__name__}: {exc}{RESET}")
            results.append({
                "group": group_key,
                "turn": i,
                "query": query,
                "expected": expected,
                "departments": [],
                "strategy": "error",
                "confidence": 0.0,
                "elapsed_s": round(elapsed, 2),
                "answer_preview": "",
                "error": str(exc),
            })

        # Turlar arasi bekleme
        if i < len(group["turns"]):
            await asyncio.sleep(2)

    return results


async def main():
    parser = argparse.ArgumentParser(description="Follow-up Mekanizmasi E2E Testi")
    parser.add_argument("--group", type=str, nargs="+", default=[],
                        help="Calistirilacak grup(lar): A B C D E F G")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose mod")
    args = parser.parse_args()

    _configure_logging(verbose=args.verbose)
    init_engine(echo=args.verbose)

    # Grup filtresi
    if args.group:
        keys = [k.upper() for k in args.group]
        groups = {k: v for k, v in TEST_GROUPS.items() if k in keys}
        if not groups:
            print(f"{RED}Grup bulunamadi: {', '.join(args.group)}{RESET}")
            print(f"Gecerli gruplar: {', '.join(TEST_GROUPS.keys())}")
            return
    else:
        groups = TEST_GROUPS

    print(f"\n{BOLD}Follow-up Mekanizmasi E2E Testi{RESET}")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Grup Sayisi: {len(groups)}")
    total_turns = sum(len(g["turns"]) for g in groups.values())
    print(f"Toplam Tur: {total_turns}")
    print(SEP)

    print("Orchestrator baslatiliyor...")
    orchestrator = MainOrchestrator(
        conversation_service=ConversationContextService(),
    )
    print("Hazir.\n")

    # Warmup
    print("Warm-up sorgusu gonderiliyor...")
    warmup_start = time.perf_counter()
    try:
        await orchestrator.handle_query(
            "Test sorgusu",
            context_id="warmup-followup",
            is_authenticated=False,
        )
    except Exception:
        pass
    warmup_ms = round((time.perf_counter() - warmup_start) * 1000)
    print(f"Warm-up tamamlandi ({warmup_ms} ms).")

    # Testleri calistir
    all_results: list[dict] = []
    for group_key, group in groups.items():
        group_results = await run_group(orchestrator, group_key, group)
        all_results.extend(group_results)

        # Gruplar arasi bekleme
        await asyncio.sleep(3)

    # Ozet
    print(f"\n{'=' * 65}")
    print(f"{BOLD}OZET{RESET}")
    print(f"{'=' * 65}")

    errors = sum(1 for r in all_results if r["error"])
    times = [r["elapsed_s"] for r in all_results]
    avg_time = sum(times) / len(times) if times else 0

    print(f"  Toplam Tur:    {len(all_results)}")
    print(f"  Basarili:      {len(all_results) - errors}")
    print(f"  Hatali:        {errors}")
    print(f"  Ort. Sure:     {avg_time:.2f}s")

    print(f"\n  {BOLD}Loglardaki 'conversation_resolution' satirlarini inceleyin.{RESET}")
    print(f"  {DIM}is_follow_up, rewrite_method ve effective_query degerlerine bakin.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
