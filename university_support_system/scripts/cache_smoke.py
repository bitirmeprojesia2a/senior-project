"""Cache acik/kapali smoke benchmark scripti."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
_VERBOSE_ARGV = any(arg in ("-v", "--verbose") for arg in sys.argv)
os.environ["SERVER_DEBUG"] = "true" if _VERBOSE_ARGV else "false"

if not _VERBOSE_ARGV:
    import structlog

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.ERROR),
    )

from src.cache import question_cache
from src.core.config import settings
from src.core.console import configure_utf8_stdio
from src.orchestrators.main import MainOrchestrator
from src.rag.query_cache import clear_shared_query_cache
from src.rag.embedder import Embedder
from src.rag.reranker import CrossEncoderReranker
from src.rag.retriever import HybridRetriever

configure_utf8_stdio()


@dataclass(frozen=True)
class SmokeQuestion:
    text: str
    expectation: str = "full-response"


DEFAULT_QUESTIONS = [
    SmokeQuestion("Ders kaydi ne zaman basliyor?", "full-response"),
    SmokeQuestion("Harc ucreti ne kadar?", "full-response"),
    SmokeQuestion("BIL104 dersinin on kosulu nedir?", "full-response"),
    SmokeQuestion(
        "Kayit yenileme ucreti ne kadar ve ne zaman yapilir?",
        "lookup-only",
    ),
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cache acik/kapali smoke benchmark")
    parser.add_argument("--question", nargs="*", help="Tek veya birden fazla soru")
    parser.add_argument("--repeat", type=int, default=3, help="Her soru icin tekrar sayisi")
    parser.add_argument("--llm-profile", default=None, help="LLM profili")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detayli loglari ac")
    return parser.parse_args()


def _configure_logging(*, verbose: bool) -> None:
    if verbose:
        logging.basicConfig(level=logging.INFO, force=True)
        return

    logging.basicConfig(level=logging.WARNING, force=True)
    logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)
    logging.getLogger("src.db.connection").setLevel(logging.ERROR)
    logging.getLogger("src.db.telemetry").setLevel(logging.ERROR)
    logging.getLogger("src.db.conversation_context").setLevel(logging.ERROR)
    logging.getLogger("src.rag.retriever").setLevel(logging.ERROR)
    logging.getLogger("src.rag.embedder").setLevel(logging.ERROR)
    logging.getLogger("src.rag.reranker").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)


def _resolve_questions(raw_questions: list[str] | None) -> list[SmokeQuestion]:
    if not raw_questions:
        return DEFAULT_QUESTIONS
    return [SmokeQuestion(question, "custom") for question in raw_questions]


def _evaluate_expectation(
    *,
    scenario_enabled: bool,
    expectation: str,
    repeat: int,
    hits: int,
    misses: int,
    bypasses: int,
) -> str:
    if not scenario_enabled:
        return "OK" if bypasses == repeat else "DIKKAT"
    if expectation == "full-response":
        if repeat == 1:
            return "OK" if misses == 1 and hits == 0 and bypasses == 0 else "DIKKAT"
        return "OK" if misses >= 1 and hits >= 1 and bypasses == 0 else "DIKKAT"
    if expectation == "lookup-only":
        return "OK" if hits == 0 and misses >= 1 and bypasses == 0 else "DIKKAT"
    return "-"


def _clear_runtime_caches() -> None:
    question_cache.clear()
    question_cache.reset_stats()
    clear_shared_query_cache()
    HybridRetriever.clear_resource_cache()
    Embedder.clear_model_cache()
    CrossEncoderReranker.clear_model_cache()


@contextmanager
def _cache_mode(enabled: bool):
    old_values = {
        "enabled": settings.cache.enabled,
        "question_cache_enabled": settings.cache.question_cache_enabled,
        "retriever_query_cache_enabled": settings.cache.retriever_query_cache_enabled,
        "embedding_model_cache_enabled": settings.cache.embedding_model_cache_enabled,
        "reranker_model_cache_enabled": settings.cache.reranker_model_cache_enabled,
        "bm25_resource_cache_enabled": settings.cache.bm25_resource_cache_enabled,
    }
    settings.cache.enabled = enabled
    settings.cache.question_cache_enabled = enabled
    settings.cache.retriever_query_cache_enabled = enabled
    settings.cache.embedding_model_cache_enabled = enabled
    settings.cache.reranker_model_cache_enabled = enabled
    settings.cache.bm25_resource_cache_enabled = enabled
    question_cache.configure(enabled=enabled)
    try:
        yield
    finally:
        settings.cache.enabled = old_values["enabled"]
        settings.cache.question_cache_enabled = old_values["question_cache_enabled"]
        settings.cache.retriever_query_cache_enabled = old_values["retriever_query_cache_enabled"]
        settings.cache.embedding_model_cache_enabled = old_values["embedding_model_cache_enabled"]
        settings.cache.reranker_model_cache_enabled = old_values["reranker_model_cache_enabled"]
        settings.cache.bm25_resource_cache_enabled = old_values["bm25_resource_cache_enabled"]
        question_cache.configure(enabled=old_values["question_cache_enabled"])


async def _run_scenario(
    *,
    enabled: bool,
    questions: list[SmokeQuestion],
    repeat: int,
    llm_profile: str | None,
) -> None:
    scenario = "CACHE ON" if enabled else "CACHE OFF"
    print(f"\n{'=' * 72}\n{scenario}\n{'=' * 72}")
    _clear_runtime_caches()
    scenario_hits = 0
    scenario_misses = 0
    scenario_bypasses = 0
    with _cache_mode(enabled):
        orchestrator = MainOrchestrator()
        for question in questions:
            durations: list[float] = []
            question_hits = 0
            question_misses = 0
            question_bypasses = 0
            print(f"\nSoru: {question.text}")
            print(f"  Beklenti: {question.expectation}")
            for turn in range(1, repeat + 1):
                before_stats = question_cache.stats()
                started = time.perf_counter()
                response = await orchestrator.handle_query(
                    question.text,
                    context_id=f"cache-smoke-{scenario}-{turn}",
                    llm_profile=llm_profile,
                    is_authenticated=False,
                )
                elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
                after_stats = question_cache.stats()
                hit_delta = after_stats["hits"] - before_stats["hits"]
                miss_delta = after_stats["misses"] - before_stats["misses"]
                if hit_delta > 0:
                    cache_state = "hit"
                    question_hits += 1
                    scenario_hits += 1
                elif miss_delta > 0:
                    cache_state = "miss"
                    question_misses += 1
                    scenario_misses += 1
                else:
                    cache_state = "bypass"
                    question_bypasses += 1
                    scenario_bypasses += 1
                durations.append(elapsed_ms)
                dept = ", ".join(response.departments_involved) or "-"
                preview = " ".join(response.answer.split())[:140]
                print(
                    f"  Tur {turn}: {elapsed_ms:8.2f} ms | cache={cache_state:<6} | dept={dept} | cevap={preview}"
                )
            print(f"  Ortalama: {mean(durations):.2f} ms")
            print(
                f"  Cache Ozeti: hit={question_hits}, miss={question_misses}, bypass={question_bypasses}"
            )
            expectation_result = _evaluate_expectation(
                scenario_enabled=enabled,
                expectation=question.expectation,
                repeat=repeat,
                hits=question_hits,
                misses=question_misses,
                bypasses=question_bypasses,
            )
            print(f"  Beklenti Sonucu: {expectation_result}")
    print(
        f"\n{scenario} toplam cache ozeti: hit={scenario_hits}, miss={scenario_misses}, bypass={scenario_bypasses}"
    )


async def _main() -> int:
    args = _parse_args()
    _configure_logging(verbose=args.verbose)
    questions = _resolve_questions(args.question)
    await _run_scenario(
        enabled=False,
        questions=questions,
        repeat=args.repeat,
        llm_profile=args.llm_profile,
    )
    await _run_scenario(
        enabled=True,
        questions=questions,
        repeat=args.repeat,
        llm_profile=args.llm_profile,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
