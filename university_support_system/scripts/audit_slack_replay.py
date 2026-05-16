"""Offline audit for Slack diagnostic replay rows.

The audit is intentionally lightweight and LLM-free.  It checks whether a
captured Slack row kept the expected context, owner/departments, answer
constraints, source constraints, and text quality.
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
from src.core.text_normalization import normalize_text
from src.quality.answer_filter import check_answer_quality

configure_utf8_stdio()


DEFAULT_FIXTURE = _ROOT / "tests" / "fixtures" / "slack_diagnostic_cases.json"


def _load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("cases") or payload.get("rows") or []
    if not isinstance(payload, list):
        raise ValueError("Slack replay audit input must be a JSON list or an object with cases.")
    return [dict(item) for item in payload if isinstance(item, dict)]


def _contains_all(text: str, markers: list[str]) -> bool:
    normalized = normalize_text(text)
    return all(normalize_text(marker) in normalized for marker in markers)


def _contains_none(text: str, markers: list[str]) -> bool:
    normalized = normalize_text(text)
    return all(normalize_text(marker) not in normalized for marker in markers)


def audit_row(row: dict[str, Any]) -> dict[str, Any]:
    query = str(row.get("query") or "")
    effective_query = str(row.get("effective_query") or row.get("resolved_query") or query)
    answer = str(row.get("answer") or "")
    departments = [str(item) for item in row.get("departments") or row.get("pipeline") or []]
    sources = [str(item) for item in row.get("sources") or []]
    expected = dict(row.get("expected") or {})

    context_ok = _contains_all(effective_query, list(expected.get("effective_contains") or []))
    context_ok = context_ok and _contains_none(
        effective_query,
        list(expected.get("effective_forbidden") or []),
    )

    owner_ok = True
    if expected.get("departments_include"):
        owner_ok = all(item in departments for item in expected["departments_include"])
    if expected.get("departments_forbid"):
        owner_ok = owner_ok and all(item not in departments for item in expected["departments_forbid"])

    answer_ok = _contains_all(answer, list(expected.get("answer_contains") or []))
    answer_ok = answer_ok and _contains_none(answer, list(expected.get("answer_forbidden") or []))

    source_text = "\n".join(sources)
    source_ok = _contains_all(source_text, list(expected.get("source_contains") or []))
    source_ok = source_ok and _contains_none(source_text, list(expected.get("source_forbidden") or []))

    quality = check_answer_quality(answer)
    normalized_answer = normalize_text(answer)
    has_footer = "daha iyi yard" in normalized_answer and "iletisim bilgisi" in normalized_answer
    quality_ok = not quality.needs_rewrite and not has_footer

    checks = {
        "context_ok": context_ok,
        "owner_ok": owner_ok,
        "answer_ok": answer_ok,
        "source_ok": source_ok,
        "quality_ok": quality_ok,
    }
    status = "OK" if all(checks.values()) else "CHECK"
    return {
        "id": row.get("id") or row.get("case_id") or "-",
        "query": query,
        "status": status,
        **checks,
        "bad_tokens": quality.bad_tokens,
    }


def audit_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [audit_row(row) for row in rows]


def _summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_check: dict[str, int] = {}
    for row in results:
        status = str(row.get("status") or "?")
        by_status[status] = by_status.get(status, 0) + 1
        for key in ("context_ok", "owner_ok", "answer_ok", "source_ok", "quality_ok"):
            if row.get(key) is False:
                by_check[key] = by_check.get(key, 0) + 1
    return {"total": len(results), "by_status": by_status, "by_check": by_check}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline audit for Slack diagnostic replay rows")
    parser.add_argument("--input", default=str(DEFAULT_FIXTURE), help="Slack replay JSON fixture")
    parser.add_argument("--output-json", default=None, help="Optional path for audited JSON output")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = _ROOT / input_path
    rows = _load_rows(input_path)
    results = audit_rows(rows)
    summary = _summary(results)
    print("Slack Replay Audit")
    print(f"Input: {input_path}")
    print(f"Rows: {summary['total']}")
    print("Status: " + (", ".join(f"{k}={v}" for k, v in sorted(summary["by_status"].items())) or "-"))
    if summary["by_check"]:
        print("Checks: " + ", ".join(f"{k}={v}" for k, v in sorted(summary["by_check"].items())))
    print("-" * 88)
    for row in results:
        print(
            "[{id}] status={status} context={context_ok} owner={owner_ok} "
            "answer={answer_ok} source={source_ok} quality={quality_ok}".format(**row)
        )
    if args.output_json:
        output_path = Path(args.output_json)
        if not output_path.is_absolute():
            output_path = _ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
