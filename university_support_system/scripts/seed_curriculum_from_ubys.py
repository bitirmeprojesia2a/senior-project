"""Fetch curriculum data from a UBYS page and seed it directly into the database."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.console import configure_utf8_stdio
from src.db import models as _db_models  # noqa: F401
from src.db.curriculum_seed import seed_curriculum_records
from src.db.ubys_curriculum import dump_payload, export_curriculum_from_ubys

configure_utf8_stdio()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch curriculum data from UBYS and seed it into the database"
    )
    parser.add_argument("url", help="UBYS curriculum page URL")
    parser.add_argument(
        "--department-name",
        help="Override department name in fetched payload",
        default=None,
    )
    parser.add_argument(
        "--skip-prerequisites",
        action="store_true",
        help="Skip course detail requests and seed courses only",
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
    parser.add_argument(
        "--output",
        help="Optional JSON output path for the fetched payload",
        default=None,
    )
    args = parser.parse_args()

    payload = export_curriculum_from_ubys(
        args.url,
        department_name=args.department_name,
        include_prerequisites=not args.skip_prerequisites,
        prerequisite_course_codes=set(args.prerequisite_course_code or []),
        max_prerequisite_courses=args.max_prerequisite_courses,
    )
    combined_courses = list(payload["courses"]) + list(payload.get("program_slots", []))

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = ROOT_DIR / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(dump_payload(payload), encoding="utf-8")
    else:
        output_path = None

    engine = create_engine(settings.postgres.sync_url, future=True)

    print(f"{payload['department']} UBYS mufredat verisi yukleniyor...")
    print(f"  {len(combined_courses)} ders/slot kaydi alindi.")
    print(f"  {len(payload['prerequisites'])} onkosul paketi alindi.")
    if not args.skip_prerequisites:
        print(f"  {len(payload.get('prerequisite_attempted_courses', []))} ders icin onkosul denendi.")
        print(f"  {len(payload.get('prerequisite_failed_courses', []))} ders onkosulunda hata alindi.")
    with Session(engine) as session:
        result = seed_curriculum_records(
            session,
            courses=combined_courses,
            prerequisites=payload["prerequisites"],
            managed_prerequisite_course_codes=payload.get("prerequisite_attempted_courses"),
        )
        session.commit()

    print(f"  {result.deleted_prerequisites} hedef onkosul kaydi temizlendi.")
    print(f"  {result.processed_courses} ders/slot islendi (insert/update).")
    print(f"  {result.inserted_prerequisites} onkosul iliskisi yazildi.")
    if result.missing_courses:
        print(f"  UYARI: Ders bulunamayan kayitlar: {', '.join(result.missing_courses)}")
    if result.missing_prerequisites:
        print(
            "  UYARI: Onkosul eslesmeyen kayitlar: "
            + ", ".join(result.missing_prerequisites)
        )
    if output_path:
        print(f"  JSON cikti: {output_path}")
    print("UBYS mufredat verisi basariyla yuklendi.")


if __name__ == "__main__":
    main()
