from __future__ import annotations

from pathlib import Path

from scripts import audit_slack_replay


def test_slack_replay_fixture_is_clean() -> None:
    rows = audit_slack_replay._load_rows(Path("tests/fixtures/slack_diagnostic_cases.json"))

    results = audit_slack_replay.audit_rows(rows)

    assert {row["status"] for row in results} == {"OK"}


def test_slack_replay_audit_catches_context_drift() -> None:
    row = {
        "id": "bad-course-context",
        "query": "BIL104 dersinin on kosulu var mi?",
        "effective_query": "BIL203 dersinin on kosulu var mi?",
        "answer": "BIL203 dersinin on kosulu BIL104 dersidir.",
        "departments": ["academic_programs"],
        "expected": {
            "effective_contains": ["BIL104"],
            "effective_forbidden": ["BIL203"],
        },
    }

    result = audit_slack_replay.audit_row(row)

    assert result["status"] == "CHECK"
    assert result["context_ok"] is False


def test_slack_replay_audit_catches_bad_tokens_and_footer() -> None:
    row = {
        "id": "bad-quality",
        "query": "Topluluklar kapanir mi?",
        "effective_query": "Topluluklar kapanir mi?",
        "answer": (
            "Topluluklar znajabilir.\n\n---\n"
            "Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz. "
            "İletişim bilgisi yazarak ulaşabilirsiniz."
        ),
        "departments": ["student_affairs"],
        "expected": {},
    }

    result = audit_slack_replay.audit_row(row)

    assert result["status"] == "CHECK"
    assert result["quality_ok"] is False
