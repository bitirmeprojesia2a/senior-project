"""Compare warm in-process and HTTP A2A latency for the same questions.

This is a measurement aid, not a quality benchmark. It answers one specific
operational question: how much of the observed latency is transport/topology
overhead versus the underlying RAG/LLM work.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.console import configure_utf8_stdio
from src.db.connection import init_engine
from src.db.conversation_context import ConversationContextService
from src.orchestrators.main import MainOrchestrator

from scripts.run_quality_benchmark import (
    DEFAULT_BENCHMARK_PROFILE,
    _diagnostics_delta,
    _format_llm_usage_summary,
    _fetch_a2a_diagnostics,
    _load_benchmark,
    _response_diagnostics_payload,
    _summarize_llm_usage,
    _verify_api_ready,
)

configure_utf8_stdio()

REPORT_DIR = _ROOT / "docs" / "archive" / "benchmarks"
RESULTS_DIR = _ROOT / "tests" / "archive" / "benchmarks"


def _select_questions(question_ids: list[str]) -> list[dict[str, Any]]:
    benchmark = _load_benchmark()
    questions = list(benchmark.get("questions") or [])
    if not question_ids:
        return [question for question in questions if question.get("id") in {"Q5"}]
    wanted = {item.upper() for item in question_ids}
    selected = [question for question in questions if str(question.get("id", "")).upper() in wanted]
    missing = wanted - {str(question.get("id", "")).upper() for question in selected}
    if missing:
        raise SystemExit(f"Soru bulunamadi: {', '.join(sorted(missing))}")
    return selected


def _profile_payload() -> dict[str, str]:
    return dict(DEFAULT_BENCHMARK_PROFILE)


def _llm_usage_summary_from_diagnostics(diagnostics: Any) -> dict[str, list[str]]:
    if hasattr(diagnostics, "model_dump"):
        diagnostics = diagnostics.model_dump()
    if not isinstance(diagnostics, dict):
        return {}
    llm_usage = diagnostics.get("llm_usage") or []
    if not isinstance(llm_usage, list):
        return {}
    return _summarize_llm_usage(
        [dict(item) for item in llm_usage if isinstance(item, dict)]
    )


async def _run_api_once(
    client: httpx.AsyncClient,
    question: dict[str, Any],
    *,
    llm_profile: str | None,
    disable_cache: bool,
    run_label: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    response = await client.post(
        "/query",
        json={
            "query": question["question"],
            "context_id": f"latcmp-{question['id']}-{run_label}",
            "llm_profile": llm_profile,
            "disable_cache": disable_cache,
            **_profile_payload(),
        },
    )
    response.raise_for_status()
    body = response.json()
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    return {
        "elapsed_ms": elapsed_ms,
        "response_time_ms": body.get("response_time_ms"),
        "departments": body.get("departments_involved") or [],
        "generation_modes": body.get("generation_modes") or [],
        "source_count": len(body.get("sources") or []),
        "diagnostics": body.get("diagnostics") or {},
        "llm_usage_summary": _llm_usage_summary_from_diagnostics(body.get("diagnostics") or {}),
        "answer_preview": str(body.get("answer") or "")[:280],
    }


async def _run_inprocess_once(
    orchestrator: MainOrchestrator,
    question: dict[str, Any],
    *,
    llm_profile: str | None,
    disable_cache: bool,
    run_label: str,
) -> dict[str, Any]:
    profile = _profile_payload()
    started = time.perf_counter()
    response = await orchestrator.handle_query(
        question["question"],
        context_id=f"latcmp-{question['id']}-{run_label}",
        llm_profile=llm_profile,
        is_authenticated=False,
        student_id=None,
        student_number=profile.get("student_number"),
        student_full_name=profile.get("full_name"),
        student_department=profile.get("student_department"),
        student_faculty=profile.get("student_faculty"),
        student_type=profile.get("student_type"),
        disable_cache=disable_cache,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    return {
        "elapsed_ms": elapsed_ms,
        "response_time_ms": response.response_time_ms,
        "departments": response.departments_involved,
        "generation_modes": response.generation_modes,
        "source_count": len(response.sources),
        "diagnostics": _response_diagnostics_payload(response),
        "llm_usage_summary": _llm_usage_summary_from_diagnostics(response.diagnostics),
        "answer_preview": response.answer[:280],
    }


async def _measure_api(
    questions: list[dict[str, Any]],
    *,
    api_base_url: str,
    api_timeout: float,
    llm_profile: str | None,
    disable_cache: bool,
    warmups: int,
    repeats: int,
) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=api_base_url.rstrip("/"), timeout=api_timeout) as client:
        health = await _verify_api_ready(client)
        diagnostics_before = await _fetch_a2a_diagnostics(client)
        runs: list[dict[str, Any]] = []
        for question in questions:
            for index in range(warmups):
                await _run_api_once(
                    client,
                    question,
                    llm_profile=llm_profile,
                    disable_cache=disable_cache,
                    run_label=f"api-warmup-{index}",
                )
            for index in range(repeats):
                runs.append(
                    {
                        "question_id": question["id"],
                        **await _run_api_once(
                            client,
                            question,
                            llm_profile=llm_profile,
                            disable_cache=disable_cache,
                            run_label=f"api-measured-{index}",
                        ),
                    }
                )
        diagnostics_after = await _fetch_a2a_diagnostics(client)
    return {
        "mode": "http_a2a",
        "health": health,
        "runs": runs,
        "diagnostics": _diagnostics_delta(diagnostics_before, diagnostics_after),
    }


async def _measure_inprocess(
    questions: list[dict[str, Any]],
    *,
    llm_profile: str | None,
    disable_cache: bool,
    warmups: int,
    repeats: int,
) -> dict[str, Any]:
    orchestrator = MainOrchestrator(
        conversation_service=ConversationContextService(),
    )
    runs: list[dict[str, Any]] = []
    for question in questions:
        for index in range(warmups):
            await _run_inprocess_once(
                orchestrator,
                question,
                llm_profile=llm_profile,
                disable_cache=disable_cache,
                run_label=f"inprocess-warmup-{index}",
            )
        for index in range(repeats):
            runs.append(
                {
                    "question_id": question["id"],
                    **await _run_inprocess_once(
                        orchestrator,
                        question,
                        llm_profile=llm_profile,
                        disable_cache=disable_cache,
                        run_label=f"inprocess-measured-{index}",
                    ),
                }
            )
    return {
        "mode": "inprocess",
        "runs": runs,
    }


def _summarize_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    values = [float(run["elapsed_ms"]) for run in runs]
    if not values:
        return {
            "count": 0,
            "avg_ms": None,
            "median_ms": None,
            "min_ms": None,
            "max_ms": None,
        }
    return {
        "count": len(values),
        "avg_ms": round(statistics.mean(values), 1),
        "median_ms": round(statistics.median(values), 1),
        "min_ms": round(min(values), 1),
        "max_ms": round(max(values), 1),
    }


def _build_payload(args: argparse.Namespace, results: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode = {result["mode"]: result for result in results}
    summaries = {
        mode: _summarize_runs(result.get("runs") or [])
        for mode, result in by_mode.items()
    }
    api_summary = summaries.get("http_a2a") or {}
    inprocess_summary = summaries.get("inprocess") or {}
    ratio = None
    if api_summary.get("median_ms") and inprocess_summary.get("median_ms"):
        ratio = round(float(api_summary["median_ms"]) / float(inprocess_summary["median_ms"]), 3)
    return {
        "run_timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "questions": args.question,
        "llm_profile": args.llm_profile or None,
        "warmups": args.warmups,
        "repeats": args.repeats,
        "disable_cache": not args.allow_cache,
        "summaries": summaries,
        "http_to_inprocess_median_ratio": ratio,
        "results": results,
    }


def _write_outputs(payload: dict[str, Any]) -> tuple[Path, Path]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = payload["run_timestamp"]
    json_path = RESULTS_DIR / f"a2a_latency_compare_{timestamp}.json"
    md_path = REPORT_DIR / f"a2a_latency_compare_{timestamp}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# A2A Latency Compare",
        "",
        f"- Timestamp: `{timestamp}`",
        f"- Questions: `{', '.join(payload.get('questions') or ['Q5'])}`",
        f"- Warmups: `{payload['warmups']}`",
        f"- Repeats: `{payload['repeats']}`",
        f"- Disable cache: `{payload['disable_cache']}`",
        f"- HTTP/In-process median ratio: `{payload.get('http_to_inprocess_median_ratio')}`",
        "",
        "## Summary",
        "",
        "| Mode | Count | Avg ms | Median ms | Min ms | Max ms |",
        "|------|-------|--------|-----------|--------|--------|",
    ]
    for mode, summary in payload["summaries"].items():
        lines.append(
            f"| {mode} | {summary['count']} | {summary['avg_ms']} | "
            f"{summary['median_ms']} | {summary['min_ms']} | {summary['max_ms']} |"
        )
    lines.extend(["", "## Runs", ""])
    for result in payload["results"]:
        lines.append(f"### {result['mode']}")
        lines.append("")
        diagnostics = result.get("diagnostics")
        if diagnostics and diagnostics.get("overview_delta"):
            delta = diagnostics["overview_delta"]
            lines.append(
                "- A2A diagnostics delta: "
                f"queries={delta.get('query_count')}, "
                f"agent_tasks={delta.get('agent_task_count')}, "
                f"agent_task_failures={delta.get('agent_task_failure_count')}"
            )
            lines.append("")
        for run in result.get("runs") or []:
            llm_usage = _format_llm_usage_summary(run.get("llm_usage_summary") or {})
            lines.append(
                f"- {run['question_id']}: {run['elapsed_ms']} ms; "
                f"departments={run['departments']}; modes={run['generation_modes']}; "
                f"sources={run['source_count']}; "
                f"llm={llm_usage or '-'}"
            )
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare in-process and HTTP A2A latency")
    parser.add_argument("--question", nargs="+", default=["Q5"], help="Benchmark question IDs")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--api-timeout", type=float, default=120.0)
    parser.add_argument("--llm-profile", default="fast")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--allow-cache", action="store_true")
    parser.add_argument("--skip-api", action="store_true")
    parser.add_argument("--skip-inprocess", action="store_true")
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    init_engine(echo=False)
    questions = _select_questions(args.question)
    results: list[dict[str, Any]] = []
    if not args.skip_api:
        print("HTTP A2A olcumu basliyor...")
        results.append(
            await _measure_api(
                questions,
                api_base_url=args.api_base_url,
                api_timeout=args.api_timeout,
                llm_profile=args.llm_profile or None,
                disable_cache=not args.allow_cache,
                warmups=max(0, args.warmups),
                repeats=max(1, args.repeats),
            )
        )
    if not args.skip_inprocess:
        print("In-process olcumu basliyor...")
        results.append(
            await _measure_inprocess(
                questions,
                llm_profile=args.llm_profile or None,
                disable_cache=not args.allow_cache,
                warmups=max(0, args.warmups),
                repeats=max(1, args.repeats),
            )
        )
    payload = _build_payload(args, results)
    json_path, md_path = _write_outputs(payload)
    print(json.dumps(payload["summaries"], ensure_ascii=False, indent=2))
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


if __name__ == "__main__":
    asyncio.run(main())
