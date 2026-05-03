"""Manual event synchronization entrypoint.

Usage examples:
    python -m scripts.sync_events --source-url "https://example.edu.tr/tr/etkinlikler"
    python -m scripts.sync_events --source-id 1
"""

from __future__ import annotations

import argparse
import asyncio
from copy import deepcopy
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.agents.event.sync import sync_event_source, sync_event_sources
from src.core.console import configure_utf8_stdio
from src.db import get_session
from src.db.event_sources import (
    EventSourceRecord,
    fetch_active_event_sources,
    get_or_create_event_source,
)

configure_utf8_stdio()

_SOURCE_PRESETS = {
    "omu_egitim": {
        "source_name": "OMU Egitim Fakultesi Etkinlikler",
        "source_url": "https://egitim.omu.edu.tr/tr/etkinlikler",
        "base_url": "https://egitim.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Egitim Fakultesi",
        "unit_name": None,
        "interval_minutes": 360,
        "max_items": 100,
    },
    "omu_fen_edebiyat": {
        "source_name": "OMU Fen Edebiyat Etkinlikler",
        "source_url": "https://fen.omu.edu.tr/tr/etkinlikler",
        "base_url": "https://fen.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Fen Edebiyat Fakultesi",
        "unit_name": None,
        "interval_minutes": 360,
        "max_items": 100,
    },
    "omu_muhendislik": {
        "source_name": "OMU Muhendislik Etkinlikler",
        "source_url": "https://muhendislik.omu.edu.tr/tr/etkinlikler",
        "base_url": "https://muhendislik.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Muhendislik Fakultesi",
        "unit_name": None,
        "interval_minutes": 360,
        "max_items": 100,
    },
    "omu_bil_muh": {
        "source_name": "OMU Bilgisayar Muhendisligi Etkinlikler",
        "source_url": "https://bil-muhendislik.omu.edu.tr/tr/etkinlikler",
        "base_url": "https://bil-muhendislik.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Muhendislik Fakultesi",
        "unit_name": "Bilgisayar Muhendisligi",
        "interval_minutes": 360,
        "max_items": 100,
    },
    "omu_mfbeb": {
        "source_name": "OMU Matematik ve Fen Bilimleri Egitimi Etkinlikler",
        "source_url": "https://mfbeb-egitim.omu.edu.tr/tr",
        "base_url": "https://mfbeb-egitim.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Egitim Fakultesi",
        "unit_name": "Matematik ve Fen Bilimleri Egitimi",
        "interval_minutes": 360,
        "max_items": 100,
    },
    "omu_guzel_sanatlar_egitim": {
        "source_name": "OMU Guzel Sanatlar Egitimi Etkinlikler",
        "source_url": "https://guzelsanatlar-egitim.omu.edu.tr/tr",
        "base_url": "https://guzelsanatlar-egitim.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Egitim Fakultesi",
        "unit_name": "Guzel Sanatlar Egitimi",
        "interval_minutes": 360,
        "max_items": 100,
    },
    "omu_eem": {
        "source_name": "OMU Elektrik Elektronik Muhendisligi Etkinlikler",
        "source_url": "https://eem-muhendislik.omu.edu.tr/tr/etkinlikler",
        "base_url": "https://eem-muhendislik.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Muhendislik Fakultesi",
        "unit_name": "Elektrik Elektronik Muhendisligi",
        "interval_minutes": 360,
        "max_items": 100,
    },
    "omu_fizik": {
        "source_name": "OMU Fizik Etkinlikler",
        "source_url": "https://fizik-fen.omu.edu.tr/tr/etkinlikler",
        "base_url": "https://fizik-fen.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Fen Edebiyat Fakultesi",
        "unit_name": "Fizik",
        "interval_minutes": 360,
        "max_items": 100,
    },
    "omu_istatistik": {
        "source_name": "OMU Istatistik Etkinlikler",
        "source_url": "https://ist-fen.omu.edu.tr/tr/etkinlikler",
        "base_url": "https://ist-fen.omu.edu.tr",
        "parser_key": "omu_faculty_home_events",
        "source_type": "html_list",
        "department": "academic_programs",
        "faculty": "Fen Edebiyat Fakultesi",
        "unit_name": "Istatistik",
        "interval_minutes": 360,
        "max_items": 100,
    },
}


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Etkinlik kaynaklarini senkronize eder.")
    parser.add_argument(
        "--preset",
        choices=sorted(_SOURCE_PRESETS),
        help="Hazir etkinlik kaynagi ayarlarini uygular.",
    )
    parser.add_argument("--source-id", type=int, help="Sadece belirli source kaydini calistir.")
    parser.add_argument("--source-name", help="Yeni source kaydi olustururken gosterim adi.")
    parser.add_argument("--source-url", help="Yeni source kaydi olustururken liste URL'i.")
    parser.add_argument("--base-url", help="Relative linkler icin temel URL.")
    parser.add_argument("--department", help="Source icin departman etiketi.")
    parser.add_argument("--faculty", help="Source icin fakulte etiketi.")
    parser.add_argument("--unit-name", help="Source icin bolum/birim etiketi.")
    parser.add_argument("--parser-key", default="generic_html", help="Parser anahtari.")
    parser.add_argument("--source-type", default="html_list", help="Source tipi.")
    parser.add_argument("--interval-minutes", type=int, default=360, help="Kaynak tarama araligi.")
    parser.add_argument("--max-items", type=int, help="Bir kosuda alinacak maksimum etkinlik sayisi.")
    parser.add_argument("--dry-run", action="store_true", help="DB kaydi yapmadan sonucu onizler.")
    parser.add_argument(
        "--no-deactivate",
        action="store_true",
        help="Bu kosuda kaynakta gorunmeyen eski etkinlikleri pasiflestirme.",
    )
    parser.add_argument(
        "--skip-details",
        action="store_true",
        help="Detay sayfalarini tek tek cekmeden liste bilgisinden aday olustur.",
    )
    return parser


def _apply_preset(args: argparse.Namespace) -> argparse.Namespace:
    if not args.preset:
        if args.max_items is None:
            args.max_items = 20
        return args

    preset = deepcopy(_SOURCE_PRESETS[args.preset])
    if args.source_name is None:
        args.source_name = preset["source_name"]
    if args.source_url is None:
        args.source_url = preset["source_url"]
    if args.base_url is None:
        args.base_url = preset["base_url"]
    if args.parser_key == "generic_html":
        args.parser_key = preset["parser_key"]
    if args.source_type == "html_list":
        args.source_type = preset["source_type"]
    if args.department is None:
        args.department = preset["department"]
    if args.faculty is None:
        args.faculty = preset["faculty"]
    if args.unit_name is None:
        args.unit_name = preset["unit_name"]
    if args.interval_minutes == 360:
        args.interval_minutes = preset["interval_minutes"]
    if args.max_items is None:
        args.max_items = preset["max_items"]
    return args


async def _resolve_sources(args: argparse.Namespace) -> list[EventSourceRecord]:
    if args.source_url:
        source_name = args.source_name or args.source_url
        if args.dry_run:
            return [
                EventSourceRecord(
                    id=0,
                    name=source_name,
                    source_type=args.source_type,
                    parser_key=args.parser_key,
                    base_url=args.base_url,
                    list_url=args.source_url,
                    faculty=args.faculty,
                    unit_name=args.unit_name,
                    department=args.department,
                    fetch_interval_minutes=args.interval_minutes,
                    max_items_per_run=args.max_items,
                    parser_options={},
                    is_active=True,
                    last_success_at=None,
                    last_error=None,
                )
            ]
        async with get_session() as session:
            source = await get_or_create_event_source(
                session,
                name=source_name,
                list_url=args.source_url,
                source_type=args.source_type,
                parser_key=args.parser_key,
                base_url=args.base_url,
                faculty=args.faculty,
                unit_name=args.unit_name,
                department=args.department,
                fetch_interval_minutes=args.interval_minutes,
                max_items_per_run=args.max_items,
                is_active=True,
            )
        return [source]

    return await fetch_active_event_sources(source_id=args.source_id)


def _print_result(result) -> None:
    label = f"[{result.status.upper()}] {result.source.name}"
    print(label)
    print(f"  Kaynak URL : {result.source.list_url}")
    print(f"  Bulunan    : {result.stats.items_found}")
    print(f"  Yeni       : {result.stats.items_inserted}")
    print(f"  Guncellenen: {result.stats.items_updated}")
    print(f"  Pasiflesen : {result.stats.items_deactivated}")
    if result.error_message:
        print(f"  Hata       : {result.error_message}")


async def _main_async(args: argparse.Namespace) -> int:
    sources = await _resolve_sources(args)
    if not sources:
        print("Aktif etkinlik kaynagi bulunamadi. --source-url ile yeni bir kaynak ekleyebilirsiniz.")
        return 1

    if len(sources) == 1:
        results = [
            await sync_event_source(
                sources[0],
                dry_run=args.dry_run,
                allow_deactivation=not args.no_deactivate,
                fetch_details=not args.skip_details,
            )
        ]
    else:
        results = await sync_event_sources(
            sources,
            dry_run=args.dry_run,
            allow_deactivation=not args.no_deactivate,
            fetch_details=not args.skip_details,
        )

    had_failure = False
    for result in results:
        _print_result(result)
        had_failure = had_failure or result.status == "failed"

    return 2 if had_failure else 0


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()
    args = _apply_preset(args)
    return asyncio.run(_main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
