"""Summarize quality benchmark results into general problem classes."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_FACT_THRESHOLD = 0.8
DEFAULT_SLOW_MS = 30_000.0

_A2A_FALLBACK_MARKERS = (
    "a2a_transport_fallback",
    "agent servisi zamaninda yanit veremedi",
    "agent servisine su anda ulasilamadi",
    "agent servisi gecici olarak korumaya alindi",
)

_RECOMMENDATIONS = {
    "infra_error": "Benchmark ortami/API/stack sagligini duzeltmeden kalite yorumu yapma.",
    "a2a_diagnostics_failures": "Kullanici cevabi basarili gorunse bile A2A diagnostics failure delta uretmis; timeout, cold-start ve branch concurrency nedenlerini incele.",
    "a2a_transport_fallback": "A2A diagnostics, specialist timeout, model/RAG cold-start ve concurrency sinirlarini incele.",
    "routing_mismatch": "Router policy, intent sinyali ve departman mapping kurallarini genel marker setleriyle iyilestir.",
    "generation_mode_mismatch": "VT/RAG/LLM karar politikasini ve force-LLM kosullarini gozden gecir.",
    "low_fact_coverage": "Retrieval/ranking ve LLM sentez promptlarini kaynakta bulunan gerekli resmi kosullari kesmeyecek sekilde iyilestir.",
    "no_sources": "Ilgili veri/dokuman kapsamı, koleksiyon secimi ve dusuk-guven kaynak filtrelerini kontrol et.",
    "quality_warning": "Kalite uyarisi tipine gore genel prompt, kaynak guveni veya transport davranisini incele.",
    "slow_response": "Yavas branch'leri diagnostics latency ve LLM/RAG sureleriyle eslestir; timeout artirmadan once maliyeti bul.",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fact_ratio(result: dict[str, Any]) -> float:
    total = int(result.get("key_facts_total") or 0)
    if total <= 0:
        return 1.0
    return float(result.get("key_facts_found") or 0) / total


def classify_result(
    result: dict[str, Any],
    *,
    fact_threshold: float,
    slow_ms: float,
) -> list[str]:
    labels: list[str] = []
    answer = str(result.get("answer") or "").casefold()
    warnings = [str(item) for item in result.get("quality_warnings") or []]

    if result.get("error"):
        labels.append("infra_error")
    if any(marker in answer or marker in warnings for marker in _A2A_FALLBACK_MARKERS):
        labels.append("a2a_transport_fallback")
    if not result.get("dept_match"):
        labels.append("routing_mismatch")
    if not result.get("mode_match"):
        labels.append("generation_mode_mismatch")
    if _fact_ratio(result) < fact_threshold:
        labels.append("low_fact_coverage")
    if int(result.get("source_count") or 0) == 0 and not result.get("error"):
        labels.append("no_sources")
    if warnings:
        labels.append("quality_warning")
    if float(result.get("elapsed_ms") or 0.0) >= slow_ms:
        labels.append("slow_response")
    return labels or ["clean_pass"]


def build_summary(
    payload: dict[str, Any],
    *,
    fact_threshold: float = DEFAULT_FACT_THRESHOLD,
    slow_ms: float = DEFAULT_SLOW_MS,
) -> dict[str, Any]:
    results = list(payload.get("results") or [])
    labels: dict[str, list[dict[str, Any]]] = defaultdict(list)
    categories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        result_labels = classify_result(
            result,
            fact_threshold=fact_threshold,
            slow_ms=slow_ms,
        )
        compact = {
            "id": result.get("id"),
            "category": result.get("category"),
            "elapsed_ms": result.get("elapsed_ms"),
            "facts": f"{result.get('key_facts_found')}/{result.get('key_facts_total')}",
            "mode": result.get("actual_generation_mode"),
            "departments": result.get("actual_departments"),
            "warnings": result.get("quality_warnings") or [],
            "error": result.get("error"),
        }
        for label in result_labels:
            labels[label].append(compact)
        categories[str(result.get("category") or "unknown")].append(
            {**compact, "labels": result_labels}
        )

    diagnostics = payload.get("diagnostics") or {}
    diagnostics_overview_delta = diagnostics.get("overview_delta") or {}
    run_level_signals: list[dict[str, Any]] = []
    agent_task_failure_delta = int(
        diagnostics_overview_delta.get("agent_task_failure_count") or 0
    )
    query_failure_delta = int(diagnostics_overview_delta.get("query_failure_count") or 0)
    if agent_task_failure_delta or query_failure_delta:
        run_level_signals.append(
            {
                "label": "a2a_diagnostics_failures",
                "count": agent_task_failure_delta + query_failure_delta,
                "query_failure_delta": query_failure_delta,
                "agent_task_failure_delta": agent_task_failure_delta,
                "recommendation": _RECOMMENDATIONS["a2a_diagnostics_failures"],
                "agent_deltas": diagnostics.get("agent_deltas") or [],
                "recent_failures": diagnostics.get("new_recent_failures") or [],
            }
        )

    return {
        "benchmark_version": payload.get("benchmark_version"),
        "run_timestamp": payload.get("run_timestamp"),
        "total_questions": len(results),
        "summary": payload.get("summary") or {},
        "run_level_signals": run_level_signals,
        "problem_classes": {
            label: {
                "count": len(items),
                "question_ids": [str(item["id"]) for item in items],
                "recommendation": _RECOMMENDATIONS.get(label, "Genel kalite analizinde ele al."),
                "items": items,
            }
            for label, items in sorted(labels.items(), key=lambda pair: (-len(pair[1]), pair[0]))
        },
        "categories": {
            category: {
                "count": len(items),
                "avg_elapsed_ms": round(mean(float(item.get("elapsed_ms") or 0.0) for item in items), 1),
                "items": items,
            }
            for category, items in sorted(categories.items())
        },
    }


def _markdown(summary: dict[str, Any], *, source_path: Path) -> str:
    lines = [
        "# Quality Benchmark Problem Summary",
        "",
        f"- Source: `{source_path}`",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Total questions: {summary['total_questions']}",
        "",
        "## Metrics",
        "",
    ]
    metrics = summary.get("summary") or {}
    for key, value in metrics.items():
        lines.append(f"- `{key}`: {value}")
    run_level_signals = summary.get("run_level_signals") or []
    if run_level_signals:
        lines.extend(["", "## Run-Level Signals", ""])
        for signal in run_level_signals:
            lines.append(f"### {signal['label']} ({signal['count']})")
            lines.append("")
            lines.append(f"- Recommendation: {signal['recommendation']}")
            lines.append(f"- Query failure delta: {signal.get('query_failure_delta', 0)}")
            lines.append(f"- Agent task failure delta: {signal.get('agent_task_failure_delta', 0)}")
            failed_agents = [
                agent for agent in signal.get("agent_deltas", [])
                if agent.get("failed_delta")
            ]
            if failed_agents:
                lines.append("- Failed agents: " + ", ".join(
                    f"{agent.get('agent_id')}={agent.get('failed_delta')}"
                    for agent in failed_agents
                ))
            recent = signal.get("recent_failures") or []
            if recent:
                lines.append("- Recent failure samples:")
                for item in recent[:5]:
                    lines.append(
                        f"  - {item.get('receiver_agent_id')}: "
                        f"{item.get('error')} - {item.get('query_preview')}"
                    )
            lines.append("")
    lines.extend(["", "## Problem Classes", ""])
    for label, data in summary["problem_classes"].items():
        lines.append(f"### {label} ({data['count']})")
        lines.append("")
        lines.append(f"- Recommendation: {data['recommendation']}")
        lines.append(f"- Questions: {', '.join(data['question_ids'])}")
        lines.append("")
    lines.extend(["## Category Details", ""])
    for category, data in summary["categories"].items():
        lines.append(f"### {category}")
        lines.append("")
        lines.append(f"- Count: {data['count']}")
        lines.append(f"- Avg elapsed ms: {data['avg_elapsed_ms']}")
        for item in data["items"]:
            labels = ", ".join(item["labels"])
            lines.append(
                f"- {item['id']}: labels={labels}; facts={item['facts']}; "
                f"mode={item['mode']}; elapsed={item['elapsed_ms']}ms"
            )
        lines.append("")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize quality benchmark problem classes")
    parser.add_argument("benchmark_json", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--fact-threshold", type=float, default=DEFAULT_FACT_THRESHOLD)
    parser.add_argument("--slow-ms", type=float, default=DEFAULT_SLOW_MS)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    payload = _load(args.benchmark_json)
    summary = build_summary(
        payload,
        fact_threshold=args.fact_threshold,
        slow_ms=args.slow_ms,
    )
    if args.format == "json":
        output = json.dumps(summary, ensure_ascii=False, indent=2)
    else:
        output = _markdown(summary, source_path=args.benchmark_json)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
