"""Compare two golden trace JSON reports.

This script is intentionally lightweight: it does not call models or services.
It only compares archived replay outputs so reranker/LLM profile experiments can
be reviewed without rerunning the expensive path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


COMPARE_FIELDS: tuple[tuple[str, str], ...] = (
    ("status", "status"),
    ("owner", "trace_owner"),
    ("capability", "trace_capability"),
    ("final_owner", "trace_final_owner"),
    ("departments", "trace_departments"),
    ("validation", "answer_validation.status"),
    ("quality", "answer_quality.status"),
    ("value_conflict", "answer_value_conflict.status"),
    ("source_count", "source_count"),
    ("llm_call_count", "llm_call_count"),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested_get(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _status_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in results:
        status = str(item.get("status") or "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _short(text: str | None, limit: int = 260) -> str:
    if not text:
        return "-"
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def build_report(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    baseline_label: str,
    candidate_label: str,
) -> str:
    baseline_results = baseline.get("results") or []
    candidate_results = candidate.get("results") or []
    baseline_by_id = {str(item.get("id")): item for item in baseline_results}
    candidate_by_id = {str(item.get("id")): item for item in candidate_results}
    all_ids = sorted(set(baseline_by_id) | set(candidate_by_id))

    lines: list[str] = []
    lines.append("# Golden Trace Comparison")
    lines.append("")
    lines.append(f"- Baseline: `{baseline_label}` / `{baseline.get('run_id', '-')}`")
    lines.append(f"- Candidate: `{candidate_label}` / `{candidate.get('run_id', '-')}`")
    lines.append(f"- Baseline statuses: `{_status_counts(baseline_results)}`")
    lines.append(f"- Candidate statuses: `{_status_counts(candidate_results)}`")
    lines.append(
        f"- Baseline validation: `{baseline.get('answer_validation_stats', {})}`"
    )
    lines.append(
        f"- Candidate validation: `{candidate.get('answer_validation_stats', {})}`"
    )
    lines.append(
        f"- Baseline provider errors: `{baseline.get('provider_error_stats', {})}`"
    )
    lines.append(
        f"- Candidate provider errors: `{candidate.get('provider_error_stats', {})}`"
    )
    lines.append("")
    lines.append("## Case Diffs")
    lines.append("")

    changed_count = 0
    for case_id in all_ids:
        b_item = baseline_by_id.get(case_id, {})
        c_item = candidate_by_id.get(case_id, {})
        query = b_item.get("query") or c_item.get("query") or "-"
        changes: list[tuple[str, Any, Any]] = []
        for label, field_path in COMPARE_FIELDS:
            b_value = _nested_get(b_item, field_path)
            c_value = _nested_get(c_item, field_path)
            if b_value != c_value:
                changes.append((label, b_value, c_value))

        if not changes:
            lines.append(f"### {case_id} same")
            lines.append("")
            lines.append(f"- Query: {_short(query)}")
            lines.append("")
            continue

        changed_count += 1
        lines.append(f"### {case_id} changed")
        lines.append("")
        lines.append(f"- Query: {_short(query)}")
        for label, b_value, c_value in changes:
            lines.append(f"- {label}: `{b_value}` -> `{c_value}`")

        if b_item.get("answer_validation_summary") != c_item.get(
            "answer_validation_summary"
        ):
            lines.append(
                f"- baseline validation summary: `{b_item.get('answer_validation_summary')}`"
            )
            lines.append(
                f"- candidate validation summary: `{c_item.get('answer_validation_summary')}`"
            )
        if b_item.get("answer_preview") != c_item.get("answer_preview"):
            lines.append(f"- baseline preview: {_short(b_item.get('answer_preview'))}")
            lines.append(f"- candidate preview: {_short(c_item.get('answer_preview'))}")
        lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Changed cases: `{changed_count}/{len(all_ids)}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_report(
        _load(args.baseline),
        _load(args.candidate),
        baseline_label=args.baseline_label,
        candidate_label=args.candidate_label,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
