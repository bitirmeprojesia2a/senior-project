"""Audit academic announcement/curriculum/schedule source coverage.

This script is intentionally read-only. It answers one operational question:
for announcement sources we track, do we also have structured curriculum and
course schedule data?
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any

from sqlalchemy import create_engine, text

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.sync_announcements import _SOURCE_PRESETS
from src.core.config import settings
from src.core.console import configure_utf8_stdio
from src.core.text_normalization import normalize_text

configure_utf8_stdio()

FACULTY_LEVEL_PRESETS = {"omu_main", "omu_muhendislik", "omu_egitim", "omu_fen"}
UNIT_DEPARTMENT_ALIASES = {
    "bilgisayar muhendisligi": ["bilgisayar muhendisligi"],
    "elektrik elektronik muhendisligi": [
        "elektrik elektronik muhendisligi",
        "elektrik-elektronik muhendisligi",
    ],
    "fizik": ["fizik"],
    "istatistik": ["istatistik"],
    "matematik ve fen bilimleri egitimi": [
        "fen bilgisi ogretmenligi",
        "matematik ogretmenligi",
    ],
    "guzel sanatlar egitimi": [
        "muzik ogretmenligi",
        "resim is ogretmenligi",
    ],
}


@dataclass(slots=True)
class CurriculumSeedCoverage:
    path: Path
    department: str
    courses: int
    program_slots: int


@dataclass(slots=True)
class ScheduleCoverage:
    department: str
    term_counts: dict[str, int]


def _load_curriculum_seed_coverage(curriculum_dir: Path) -> list[CurriculumSeedCoverage]:
    coverage: list[CurriculumSeedCoverage] = []
    for path in sorted(curriculum_dir.glob("*_seed.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        coverage.append(
            CurriculumSeedCoverage(
                path=path,
                department=str(payload.get("department") or "").strip(),
                courses=len(payload.get("courses") or []),
                program_slots=len(payload.get("program_slots") or []),
            )
        )
    return coverage


def _load_schedule_coverage_from_db() -> list[ScheduleCoverage]:
    engine = create_engine(settings.postgres.sync_url, future=True)
    grouped: dict[str, dict[str, int]] = defaultdict(dict)
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                """
                select department, term, count(*)
                from course_schedule_slots
                where is_active is true
                group by department, term
                order by department, term
                """
            )
        )
        for department, term, count in rows:
            grouped[str(department)][str(term)] = int(count)
    return [
        ScheduleCoverage(department=department, term_counts=term_counts)
        for department, term_counts in sorted(grouped.items())
    ]


def _matches_department(candidate: str, expected_aliases: list[str]) -> bool:
    normalized_candidate = normalize_text(candidate)
    compact_candidate = re.sub(r"[^a-z0-9]", "", normalized_candidate)
    return any(
        alias in normalized_candidate
        or re.sub(r"[^a-z0-9]", "", normalize_text(alias)) in compact_candidate
        for alias in expected_aliases
    )


def _find_curriculum_matches(
    coverage: list[CurriculumSeedCoverage],
    expected_aliases: list[str],
) -> list[CurriculumSeedCoverage]:
    return [
        item
        for item in coverage
        if _matches_department(item.department, expected_aliases)
    ]


def _find_schedule_matches(
    coverage: list[ScheduleCoverage],
    expected_aliases: list[str],
) -> list[ScheduleCoverage]:
    return [
        item
        for item in coverage
        if _matches_department(item.department, expected_aliases)
    ]


def _format_terms(matches: list[ScheduleCoverage]) -> str:
    if not matches:
        return "-"
    parts: list[str] = []
    for match in matches:
        term_text = ", ".join(
            f"{term}:{count}" for term, count in sorted(match.term_counts.items())
        )
        parts.append(f"{match.department} ({term_text})")
    return "; ".join(parts)


def build_coverage_rows(
    *,
    curriculum_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    curriculum_coverage = _load_curriculum_seed_coverage(curriculum_dir)
    schedule_coverage = _load_schedule_coverage_from_db()

    tracked_rows: list[dict[str, Any]] = []
    faculty_rows: list[dict[str, Any]] = []

    for preset_key, preset in sorted(_SOURCE_PRESETS.items()):
        unit_name = preset.get("unit_name")
        if preset_key in FACULTY_LEVEL_PRESETS or not unit_name:
            faculty_rows.append(
                {
                    "preset": preset_key,
                    "name": preset["source_name"],
                    "faculty": preset.get("faculty") or "-",
                    "url": preset["source_url"],
                    "note": "faculty_or_main_source",
                }
            )
            continue

        aliases = UNIT_DEPARTMENT_ALIASES.get(
            normalize_text(unit_name),
            [normalize_text(unit_name)],
        )
        curriculum_matches = _find_curriculum_matches(curriculum_coverage, aliases)
        schedule_matches = _find_schedule_matches(schedule_coverage, aliases)
        tracked_rows.append(
            {
                "preset": preset_key,
                "unit": unit_name,
                "aliases": aliases,
                "announcement_url": preset["source_url"],
                "curriculum": curriculum_matches,
                "schedule": schedule_matches,
                "has_curriculum": bool(curriculum_matches),
                "has_schedule": bool(schedule_matches),
            }
        )

    return tracked_rows, faculty_rows


def print_markdown_report(rows: list[dict[str, Any]], faculty_rows: list[dict[str, Any]]) -> None:
    print("# Academic Source Coverage")
    print()
    print("| Preset | Unit | Curriculum | Schedule slots | Status |")
    print("| --- | --- | --- | --- | --- |")
    for row in rows:
        curriculum_text = "-"
        if row["curriculum"]:
            curriculum_text = "; ".join(
                f"{item.department} ({item.courses} ders)"
                for item in row["curriculum"]
            )
        schedule_text = _format_terms(row["schedule"])
        status_parts = []
        if not row["has_curriculum"]:
            status_parts.append("missing_curriculum")
        if not row["has_schedule"]:
            status_parts.append("missing_schedule")
        status = ", ".join(status_parts) if status_parts else "ok"
        print(
            f"| {row['preset']} | {row['unit']} | {curriculum_text} | "
            f"{schedule_text} | {status} |"
        )

    print()
    print("## Faculty/Main Announcement Sources")
    print()
    print("| Preset | Faculty | Note |")
    print("| --- | --- | --- |")
    for row in faculty_rows:
        print(f"| {row['preset']} | {row['faculty']} | {row['note']} |")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit structured academic source coverage for tracked announcement units.",
    )
    parser.add_argument(
        "--curriculum-dir",
        type=Path,
        default=ROOT_DIR / "data" / "curriculum",
        help="Directory containing *_seed.json curriculum payloads.",
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit with status 2 when any tracked unit is missing curriculum or schedule coverage.",
    )
    args = parser.parse_args()

    rows, faculty_rows = build_coverage_rows(curriculum_dir=args.curriculum_dir)
    print_markdown_report(rows, faculty_rows)
    missing = [
        row for row in rows
        if not row["has_curriculum"] or not row["has_schedule"]
    ]
    return 2 if args.fail_on_missing and missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
