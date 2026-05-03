"""Export curriculum and prerequisite data from a UBYS program page to JSON."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.console import configure_utf8_stdio
from src.db.ubys_curriculum import dump_payload, export_curriculum_from_ubys

configure_utf8_stdio()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export curriculum data from a UBYS curriculum page")
    parser.add_argument("url", help="UBYS curriculum page URL")
    parser.add_argument(
        "--output",
        help="Output JSON path",
        default=None,
    )
    parser.add_argument(
        "--department-name",
        help="Override department name in exported payload",
        default=None,
    )
    parser.add_argument(
        "--skip-prerequisites",
        action="store_true",
        help="Skip course detail requests and export courses only",
    )
    parser.add_argument(
        "--max-prerequisite-courses",
        type=int,
        default=None,
        help="Fetch prerequisites for at most N courses",
    )
    parser.add_argument(
        "--prerequisite-course-code",
        action="append",
        default=None,
        help="Limit prerequisite fetch to specific course codes (repeatable)",
    )
    args = parser.parse_args()

    payload = export_curriculum_from_ubys(
        args.url,
        department_name=args.department_name,
        include_prerequisites=not args.skip_prerequisites,
        prerequisite_course_codes=set(args.prerequisite_course_code or []),
        max_prerequisite_courses=args.max_prerequisite_courses,
    )

    output_path = Path(args.output) if args.output else Path("data/curriculum/ubys_export.json")
    if not output_path.is_absolute():
        output_path = ROOT_DIR / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dump_payload(payload), encoding="utf-8")

    print(f"Bolum       : {payload['department']}")
    print(f"Ders sayisi : {len(payload['courses'])}")
    print(f"Slot sayisi : {len(payload.get('program_slots', []))}")
    print(f"Onkosul     : {len(payload['prerequisites'])}")
    if not args.skip_prerequisites:
        print(f"Denenen     : {len(payload.get('prerequisite_attempted_courses', []))}")
        print(f"Basarisiz   : {len(payload.get('prerequisite_failed_courses', []))}")
    print(f"Cikti       : {output_path}")


if __name__ == "__main__":
    main()
