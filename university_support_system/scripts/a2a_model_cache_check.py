"""Check whether Docker/A2A services can load local RAG model artifacts.

This script is intentionally separate from health checks. `/health` should stay
cheap; this command is a deployment preflight for embedding/reranker caches.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.core.config import settings
from src.rag.embedder import Embedder
from src.rag.reranker import CrossEncoderReranker


def _check_embedding(device: str | None) -> dict[str, Any]:
    started = time.perf_counter()
    embedder = Embedder(device=device or settings.embedding.device)
    dimension = embedder.dimension
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "ok": True,
        "model": embedder.model_name,
        "device": embedder.resolved_device,
        "dimension": dimension,
        "local_files_only": settings.embedding.local_files_only,
        "elapsed_ms": elapsed_ms,
    }


def _check_reranker(device: str | None) -> dict[str, Any]:
    started = time.perf_counter()
    reranker = CrossEncoderReranker(device=device or settings.reranker.device)
    _ = reranker.model
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "ok": True,
        "model": reranker.model_name,
        "device": reranker.resolved_device,
        "local_files_only": settings.reranker.local_files_only,
        "elapsed_ms": elapsed_ms,
    }


def _run_check(func, device: str | None) -> dict[str, Any]:
    try:
        return func(device)
    except Exception as exc:  # pragma: no cover - deployment diagnostic path
        return {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate local model cache for A2A Docker services.")
    parser.add_argument("--device", choices=["cpu", "cuda", "auto"], default=None)
    parser.add_argument("--skip-reranker", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    checks = {
        "embedding": _run_check(_check_embedding, args.device),
    }
    if not args.skip_reranker:
        checks["reranker"] = _run_check(_check_reranker, args.device)

    payload = {
        "ok": all(result.get("ok") for result in checks.values()),
        "cache_env": {
            "HF_HOME": os.getenv("HF_HOME"),
            "SENTENCE_TRANSFORMERS_HOME": os.getenv("SENTENCE_TRANSFORMERS_HOME"),
            "MODEL_CACHE_HOST_DIR": os.getenv("MODEL_CACHE_HOST_DIR"),
        },
        "configured_cache": {
            "host_dir": str(settings.model_cache.resolved_host_dir)
            if settings.model_cache.resolved_host_dir is not None
            else None,
            "hf_home": str(settings.model_cache.hf_home)
            if settings.model_cache.hf_home is not None
            else None,
            "hf_hub_cache": str(settings.model_cache.hf_hub_cache)
            if settings.model_cache.hf_hub_cache is not None
            else None,
        },
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
