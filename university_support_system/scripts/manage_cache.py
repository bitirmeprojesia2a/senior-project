"""Yerel runtime cache yonetim komutu."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SERVER_DEBUG", "false")

from src.cache import invalidate_cached_state, question_cache
from src.core.console import configure_utf8_stdio
from src.rag.embedder import Embedder
from src.rag.query_cache import clear_shared_query_cache, shared_query_cache_size
from src.rag.reranker import CrossEncoderReranker
from src.rag.retriever import HybridRetriever

configure_utf8_stdio()
logging.basicConfig(level=logging.WARNING, force=True)
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Yerel runtime cache yonetimi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("show", help="Yerel cache ozetini goster")
    subparsers.add_parser("clear-runtime", help="Soru/model/retriever cache'lerini temizle")

    invalidate_conv = subparsers.add_parser(
        "invalidate-conversation",
        help="Belirli bir conversation cache girdisini Redis'ten sil",
    )
    invalidate_conv.add_argument("--context-id", required=True)

    return parser.parse_args()


def _show() -> int:
    stats = question_cache.stats()
    print("Yerel cache ozeti")
    print("Not: Bu degerler sadece mevcut Python sureci icin gecerlidir.")
    print("Not: Bu komut yeni bir surecte calistigi icin, onceki bir scriptin bellek ici cache'lerini goremez.")
    print("Not: Redis-backed dagitik runtime cache sayaclari asagida ayrica gosterilir.")
    print("Not: Conversation cache bu ozetin parcasi degildir; onun icin invalidate-conversation kullanilir.")
    print(f"- Question cache size : {stats['size']}")
    print(f"- Question cache hits : {stats['hits']}")
    print(f"- Question cache miss : {stats['misses']}")
    print(f"- Redis question size : {question_cache.distributed_size()}")
    print(f"- BM25 doc cache size : {len(HybridRetriever._BM25_DOCUMENT_CACHE)}")
    print(f"- BM25 retr cache size: {len(HybridRetriever._BM25_RETRIEVER_CACHE)}")
    print(f"- Redis retr cache size: {shared_query_cache_size()}")
    print(f"- Embedder model cache: {len(Embedder._MODEL_CACHE)}")
    print(f"- Reranker model cache: {len(CrossEncoderReranker._MODEL_CACHE)}")
    return 0


def _clear_runtime() -> int:
    question_cache.clear()
    question_cache.reset_stats()
    clear_shared_query_cache()
    HybridRetriever.clear_resource_cache()
    Embedder.clear_model_cache()
    CrossEncoderReranker.clear_model_cache()
    print("Yerel runtime cache'leri temizlendi.")
    return 0


async def _invalidate_conversation(context_id: str) -> int:
    await invalidate_cached_state(context_id)
    print(f"Conversation cache girdisi gecersiz kilindi: {context_id}")
    return 0


async def _main() -> int:
    args = _parse_args()
    if args.command == "show":
        return _show()
    if args.command == "clear-runtime":
        return _clear_runtime()
    if args.command == "invalidate-conversation":
        return await _invalidate_conversation(args.context_id)
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
