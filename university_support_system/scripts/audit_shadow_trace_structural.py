"""Offline structural audit for shadow decision trace golden outputs.

This script intentionally makes no LLM/API calls. It reuses the same structural
contract checks as the live golden runner so archived runs can be reclassified
after the contract becomes stricter.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.console import configure_utf8_stdio

configure_utf8_stdio()

from scripts import run_shadow_trace_golden as golden
from src.quality.answer_value_conflict import validate_answer_value_conflicts


def _load_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        records = [
            json.loads(line)
            for line in text.splitlines()
            if line.strip()
        ]
        return {
            "run_id": path.stem,
            "trace_path": str(path),
            "results": [_row_from_trace_record(record) for record in records],
        }
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("Audit input JSON must be an object.")
    return payload


def _row_from_trace_record(record: dict[str, Any]) -> dict[str, Any]:
    context_id = str(record.get("context_id") or "")
    row: dict[str, Any] = {
        "id": context_id or record.get("trace_id") or "trace-record",
        "family": "-",
        "query": ((record.get("shadow_decision_contract") or {}).get("query") or {}).get("original"),
        "context_id": context_id,
        "expected_owner": None,
        "expected_capability": None,
        "expected_primary_department": None,
        "expected_primary_specialist": None,
        "answer_preview": record.get("final_answer_preview") or "",
        "error": None,
    }
    return golden._hydrate_row_from_trace(row, record)


def _audit_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    case_by_id = {case.id: case for case in golden.GOLDEN_CASES}
    audited: list[dict[str, Any]] = []
    for raw_row in rows:
        row = dict(raw_row)
        case = case_by_id.get(str(row.get("id") or "").upper())
        if case is not None:
            row["expected_owner"] = row.get("expected_owner") or case.expected_owner
            row["expected_capability"] = row.get("expected_capability") or case.expected_capability
            row["expected_primary_department"] = (
                row.get("expected_primary_department") or case.expected_primary_department
            )
            row["expected_primary_specialist"] = (
                row.get("expected_primary_specialist") or case.expected_primary_specialist
            )
        if not row.get("answer_value_conflict"):
            value_conflict = validate_answer_value_conflicts(
                query=str(row.get("query") or ""),
                answer=str(row.get("answer_preview") or ""),
            ).to_dict()
            row["answer_value_conflict"] = value_conflict
            row["answer_value_conflict_summary"] = golden._format_answer_value_conflict_summary(
                value_conflict
            )
        issues = golden._structural_issues(row)
        row["structural_issues"] = issues
        row["structural_summary"] = "; ".join(issues) if issues else "-"
        row["structural_status"] = golden._row_status(row)
        audited.append(row)
    return audited


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_issue: dict[str, int] = {}
    for row in rows:
        status = str(row.get("structural_status") or "?")
        by_status[status] = by_status.get(status, 0) + 1
        for issue in row.get("structural_issues") or []:
            key = str(issue).split(" actual=", 1)[0]
            by_issue[key] = by_issue.get(key, 0) + 1
    return {
        "total": len(rows),
        "by_status": by_status,
        "by_issue": by_issue,
    }


def _print_report(*, input_path: Path, payload: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    summary = _summary(rows)
    print("Shadow Trace Structural Audit")
    print(f"Input: {input_path}")
    print(f"Run id: {payload.get('run_id') or '-'}")
    print(f"Rows: {summary['total']}")
    print("Status: " + (", ".join(f"{k}={v}" for k, v in sorted(summary["by_status"].items())) or "-"))
    if summary["by_issue"]:
        print("Issues: " + ", ".join(f"{k}={v}" for k, v in sorted(summary["by_issue"].items())))
    print("-" * 88)
    for row in rows:
        print(
            "[{id}] status={status} owner={owner}/{expected_owner} capability={capability}/{expected_capability} "
            "dept={dept} specialist={specialist} value_conflict={value_conflict} issues={issues}".format(
                id=row.get("id") or "-",
                status=row.get("structural_status") or "-",
                owner=row.get("trace_owner") or "-",
                expected_owner=row.get("expected_owner") or "-",
                capability=row.get("trace_capability") or "-",
                expected_capability=row.get("expected_capability") or "-",
                dept=", ".join(row.get("trace_departments") or row.get("departments") or []) or "-",
                specialist=", ".join(row.get("trace_selected_specialists") or []) or "-",
                value_conflict=row.get("answer_value_conflict_summary") or "-",
                issues=row.get("structural_summary") or "-",
            )
        )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline audit for shadow trace structural contract")
    parser.add_argument("--input", required=True, help="Golden results JSON or decision trace JSONL path")
    parser.add_argument("--output-json", default=None, help="Optional path for audited JSON summary")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = _ROOT / input_path
    payload = _load_payload(input_path)
    rows = _audit_rows(list(payload.get("results") or []))
    _print_report(input_path=input_path, payload=payload, rows=rows)
    if args.output_json:
        output_path = Path(args.output_json)
        if not output_path.is_absolute():
            output_path = _ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                {
                    "input": str(input_path),
                    "run_id": payload.get("run_id"),
                    "summary": _summary(rows),
                    "results": rows,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
