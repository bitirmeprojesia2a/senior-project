"""Deactivate demo announcement rows that are not tied to a crawl source.

Usage:
    python -m scripts.cleanup_synthetic_announcements --dry-run
    python -m scripts.cleanup_synthetic_announcements
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.console import configure_utf8_stdio
from src.core.config import settings
from src.db.models import Announcement


configure_utf8_stdio()


DEMO_SOURCE_URLS = {
    "https://omu.edu.tr/duyuru/2026-bahar-ders-kayit-takvimi",
    "https://omu.edu.tr/duyuru/cap-basvurulari-2026",
    "https://omu.edu.tr/duyuru/yemek-bursu-basvurulari-2026",
}
DEMO_TITLES = {
    "2026 Bahar Ders Kayit Takvimi Guncellendi",
    "CAP Basvurulari Acildi",
    "Yemek Bursu Basvurulari Basladi",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deactivate source-less demo announcement rows.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching rows without updating the database.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    engine = create_engine(settings.postgres.sync_url, future=True)

    with Session(engine) as session:
        rows = list(
            session.scalars(
                select(Announcement)
                .where(Announcement.source_id.is_(None))
                .where(Announcement.is_active.is_(True))
            ).all()
        )
        matches = [
            row
            for row in rows
            if row.source_url in DEMO_SOURCE_URLS or row.title in DEMO_TITLES
        ]

        if not matches:
            print("No active source-less demo announcements found.")
            return 0

        print(f"Matched {len(matches)} demo announcement row(s):")
        for row in matches:
            print(f"- id={row.id} title={row.title!r} url={row.source_url!r}")

        if args.dry_run:
            print("Dry run only; database was not changed.")
            return 0

        for row in matches:
            row.is_active = False
            row.inactive_reason = "deactivated_source_less_demo_row"
        session.commit()
        print(f"Deactivated {len(matches)} demo announcement row(s).")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
