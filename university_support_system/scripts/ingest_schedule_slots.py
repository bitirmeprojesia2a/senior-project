from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.config import settings
from src.db.schedule_ingest import (
    collect_schedule_slots_from_path,
    replace_schedule_slots_for_sources,
    summarize_schedule_slots,
)
from src.db.schedule_scrapling import collect_schedule_slots_from_scrapling_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest structured course schedule slots from local PDF timetable documents.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT_DIR / "data" / "raw" / "academic_programs" / "ders_programlari",
        help="PDF file or directory containing schedule documents.",
    )
    parser.add_argument(
        "--academic-year",
        type=str,
        default=None,
        help="Override inferred academic year for all parsed rows.",
    )
    parser.add_argument(
        "--term",
        type=str,
        default=None,
        help="Override inferred term for all parsed rows.",
    )
    parser.add_argument(
        "--department",
        type=str,
        default=None,
        help="Override inferred department for all parsed rows.",
    )
    parser.add_argument(
        "--source-url",
        type=str,
        default=None,
        help="Optional upstream source URL to attach to all ingested rows.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse documents and print a summary without writing to PostgreSQL.",
    )
    parser.add_argument(
        "--html-url",
        type=str,
        default=None,
        help="Optional HTML schedule URL to ingest via Scrapling.",
    )
    parser.add_argument(
        "--html-source-name",
        type=str,
        default=None,
        help="Optional source document name to use when ingesting from --html-url.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.html_url:
        source_name, rows = collect_schedule_slots_from_scrapling_url(
            args.html_url,
            source_name=args.html_source_name,
            academic_year=args.academic_year,
            term=args.term,
            department=args.department,
        )
        slots_by_source = {Path(source_name): rows}
    else:
        source_path: Path = args.source.resolve()
        if not source_path.exists():
            raise SystemExit(f"Kaynak bulunamadi: {source_path}")

        slots_by_source = collect_schedule_slots_from_path(
            source_path,
            academic_year=args.academic_year,
            term=args.term,
            department=args.department,
            source_url=args.source_url,
        )
    summary = summarize_schedule_slots(slots_by_source)

    print(f"Kaynak sayisi: {summary['sources']}")
    print(f"Bos olmayan kaynak: {summary['non_empty_sources']}")
    print(f"Cikarilan satir: {summary['rows']}")
    if summary["empty_sources"]:
        print("Slot cikarilamayan dosyalar:")
        for name in summary["empty_sources"]:
            print(f"  - {name}")

    if args.dry_run:
        return

    engine = create_engine(settings.postgres.sync_url, future=True)
    with Session(engine) as session:
        result = replace_schedule_slots_for_sources(session, slots_by_source)
        session.commit()

    print(f"PostgreSQL guncellendi: {result['sources']} kaynak, {result['rows']} satir")


if __name__ == "__main__":
    main()
