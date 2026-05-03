"""Seed curriculum and prerequisite data from a JSON payload."""

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
from src.db.curriculum_seed import load_curriculum_payload, seed_curriculum_records

configure_utf8_stdio()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed curriculum data from JSON")
    parser.add_argument("input", help="Path to curriculum JSON file")
    parser.add_argument(
        "--courses-only",
        action="store_true",
        help="Insert/update courses without deleting or inserting prerequisite rows.",
    )
    args = parser.parse_args()

    payload = load_curriculum_payload(args.input)
    engine = create_engine(settings.postgres.sync_url, future=True)

    print(f"{payload['department']} mufredat verisi yukleniyor...")
    with Session(engine) as session:
        result = seed_curriculum_records(
            session,
            courses=payload["courses"],
            prerequisites=[] if args.courses_only else payload["prerequisites"],
            managed_prerequisite_course_codes=[] if args.courses_only else None,
        )
        session.commit()

    print(f"  {result.deleted_prerequisites} hedef onkosul kaydi temizlendi.")
    print(f"  {result.processed_courses} ders islendi (insert/update).")
    print(f"  {result.inserted_prerequisites} onkosul iliskisi yazildi.")
    if result.missing_courses:
        print(f"  UYARI: Ders bulunamayan kayitlar: {', '.join(result.missing_courses)}")
    if result.missing_prerequisites:
        print(
            "  UYARI: Onkosul eslesmeyen kayitlar: "
            + ", ".join(result.missing_prerequisites)
        )
    print("Mufredat verisi basariyla yuklendi.")


if __name__ == "__main__":
    main()
