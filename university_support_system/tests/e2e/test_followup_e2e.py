"""
Follow-up Mekanizmasi E2E Test Script
=====================================
Dogrudan MainOrchestrator uzerinden test eder.

Kullanim:
    python tests/e2e/test_followup_e2e.py
"""

import asyncio
import json
import logging
import sys
import time

# Loglari gostermek icin
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# conversation_resolution loglarini mutlaka goster
logging.getLogger("src.db.conversation_context").setLevel(logging.INFO)


async def run_tests():
    # ------------------------------------------------------------------
    # Lazy import: modüller yüklenirken embedding model vb. indirilmez,
    # sadece kullanılacaklari ana oluşturulur.
    # ------------------------------------------------------------------
    from src.db.conversation_context import ConversationContextService
    from src.orchestrators.main import MainOrchestrator
    from src.rag.warmup import warm_retrieval_resources

    print("\n" + "=" * 60)
    print("  RAG Warmup Baslatiliyor...")
    print("=" * 60)
    warm_retrieval_resources()
    print("  Warmup tamamlandi.\n")

    orchestrator = MainOrchestrator(
        conversation_service=ConversationContextService(),
    )

    # ------------------------------------------------------------------
    # Test gruplari
    # ------------------------------------------------------------------
    test_groups = [
        {
            "name": "GRUP A: Temel Follow-up Algilama",
            "context_id": f"test-A-{int(time.time())}",
            "turns": [
                {
                    "query": "CAP basvurusu nasil yapilir?",
                    "expected": "is_follow_up=false, topic=CAP, dept=student_affairs+academic_programs",
                },
                {
                    "query": "Peki not ortalamasi kac olmali?",
                    "expected": "is_follow_up=true, effective_query ~= CAP icin not ortalamasi",
                },
                {
                    "query": "Bunun icin hangi belge gerekli?",
                    "expected": "is_follow_up=true, bunun zamiri cozulmeli",
                },
                {
                    "query": "Erasmus basvurusu nasil yapilir?",
                    "expected": "is_follow_up=false, yeni konu, topic degismeli",
                },
            ],
        },
        {
            "name": "GRUP B: Suffix/Marker Bug Fix Dogrulama",
            "context_id": f"test-B-{int(time.time())}",
            "turns": [
                {
                    "query": "Kayit dondurma islemi nasil yapilir?",
                    "expected": "is_follow_up=false, topic=Kayit Dondurma",
                },
                {
                    "query": "Ucreti nedir?",
                    "expected": "is_follow_up=true, nedir marker ile yakalanmali",
                },
                {
                    "query": "Ne zaman yapilir?",
                    "expected": "is_follow_up=true, ne zaman marker",
                },
                {
                    "query": "Kosullari nelerdir?",
                    "expected": "is_follow_up=true, nelerdir marker",
                },
            ],
        },
        {
            "name": "GRUP C: Kisa / Anlamsiz Soru Filtresi",
            "context_id": f"test-C-{int(time.time())}",
            "turns": [
                {
                    "query": "Yaz okulu hakkinda bilgi verir misin?",
                    "expected": "Normal soru, is_follow_up=false",
                },
                {
                    "query": "Evet",
                    "expected": "Turbo kelime, is_follow_up=false",
                },
                {
                    "query": "Tesekkurler",
                    "expected": "Turbo kelime, is_follow_up=false",
                },
            ],
        },
        {
            "name": "GRUP D: Konu Degisimi",
            "context_id": f"test-D-{int(time.time())}",
            "turns": [
                {
                    "query": "Harc ucreti ne kadar?",
                    "expected": "topic=Harc, dept=finance",
                },
                {
                    "query": "Taksitle odeyebilir miyim?",
                    "expected": "is_follow_up=true, ayni konu, dept=finance",
                },
                {
                    "query": "Burs basvurusu ne zaman?",
                    "expected": "is_follow_up=false, yeni konu",
                },
                {
                    "query": "Peki GNO sarti var mi?",
                    "expected": "is_follow_up=true, burs baglaminda GNO",
                },
            ],
        },
        {
            "name": "GRUP E: Cok Departmanli Gecis",
            "context_id": f"test-E-{int(time.time())}",
            "turns": [
                {
                    "query": "Kayit dondurma nasil yapilir?",
                    "expected": "dept=student_affairs",
                },
                {
                    "query": "Bu durumda harc odenir mi?",
                    "expected": "is_follow_up=true, kayit dondurma + harc",
                },
                {
                    "query": "Peki ne kadar odenir?",
                    "expected": "is_follow_up=true, dept=finance",
                },
            ],
        },
        {
            "name": "GRUP F: Belirsiz Zamir Cozumleme",
            "context_id": f"test-F-{int(time.time())}",
            "turns": [
                {
                    "query": "Staj basvurusu icin hangi belgeler gerekli?",
                    "expected": "dept=student_affairs",
                },
                {
                    "query": "Onlari nereden alirim?",
                    "expected": "is_follow_up=true, onlari -> staj belgeleri",
                },
                {
                    "query": "Suresi ne kadar?",
                    "expected": "is_follow_up=true, suresi -> staj suresi",
                },
            ],
        },
        {
            "name": "GRUP G: LLM Rewrite Dogrulama",
            "context_id": f"test-G-{int(time.time())}",
            "turns": [
                {
                    "query": "Yatay gecis basvurusu nasil yapilir?",
                    "expected": "Normal soru",
                },
                {
                    "query": "Not ortalamasi kac olmali?",
                    "expected": "LLM rewrite: Yatay gecis icin not ortalamasi",
                },
                {
                    "query": "Peki kontenjan var mi?",
                    "expected": "LLM rewrite: Yatay gecis icin kontenjan",
                },
            ],
        },
    ]

    total_turns = 0
    for group in test_groups:
        print("\n" + "=" * 60)
        print(f"  {group['name']}")
        print("=" * 60)

        ctx = group["context_id"]

        for i, turn in enumerate(group["turns"], 1):
            total_turns += 1
            query = turn["query"]
            expected = turn["expected"]

            print(f"\n{'─' * 55}")
            print(f"  Tur {i}: {query}")
            print(f"  Beklenen: {expected}")
            print(f"{'─' * 55}")

            start = time.perf_counter()
            try:
                response = await orchestrator.handle_query(
                    query,
                    context_id=ctx,
                    student_number="21060731",
                    student_full_name="Test Kullanici",
                    student_department="Bilgisayar Muhendisligi",
                    student_faculty="Muhendislik Fakultesi",
                )
                elapsed = time.perf_counter() - start

                # Sonuclari goster
                print(f"\n  ⏱  Yanit suresi: {elapsed:.2f}s")
                print(f"  📋 Departmanlar: {response.departments_involved}")
                print(f"  🎯 Strateji:     {response.strategy}")
                print(f"  📊 Guven:        {response.confidence}")

                # Cevap metnini kisalt
                answer_preview = response.answer[:200] if response.answer else "(bos)"
                if len(response.answer or "") > 200:
                    answer_preview += "..."
                print(f"  💬 Cevap:        {answer_preview}")

                # Kaynak sayisi
                total_sources = sum(
                    len(dept_resp.sources) for dept_resp in (response.department_responses or [])
                )
                print(f"  📎 Kaynak:       {total_sources} adet")

            except Exception as exc:
                elapsed = time.perf_counter() - start
                print(f"\n  ❌ HATA ({elapsed:.2f}s): {type(exc).__name__}: {exc}")

            # Turlar arasi bekleme (LLM ve DB islemlerinin tamamlanmasi icin)
            await asyncio.sleep(1)

    print("\n" + "=" * 60)
    print(f"  TUM TESTLER TAMAMLANDI ({total_turns} tur)")
    print("=" * 60)
    print("\n  Loglardaki 'conversation_resolution' satirlarini inceleyin.")
    print("  Ozellikle is_follow_up, rewrite_method ve effective_query degerlerine bakin.\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
