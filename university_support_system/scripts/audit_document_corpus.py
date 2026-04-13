"""
Belge korpusunu hizlica denetleyen yardimci script.

Amaç:
    - Desteklenen / desteklenmeyen uzanti dagilimini gormek
    - Unsupported dosyalari tek listede toplamak
    - Registry dosyalarinin guncel mi yoksa legacy mi oldugunu anlamak
    - Akademik koleksiyondaki olasi gurultu kaynaklarini isaretlemek

Kullanim:
    python scripts/audit_document_corpus.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.document_loader import DocumentLoader
from src.db.schedule_ingest import classify_schedule_document
from src.core.console import configure_utf8_stdio


LEGACY_REGISTRY_NAME = "doc_registry.json"
EXPECTED_REGISTRY_FILES = {
    "doc_registry_student_affairs_docs.json",
    "doc_registry_academic_programs_docs.json",
    "doc_registry_academic_schedules_docs.json",
    "doc_registry_finance_docs.json",
}
NOISY_PATH_MARKERS = {
    "ders_programlari": "ders_programlari klasoru",
    "lisansustu": "lisansustu dosyalari",
    "yuksek_lisans": "yuksek lisans dosyalari",
    "yüksek_lisans": "yuksek lisans dosyalari",
    "doktora": "doktora dosyalari",
}
MOJIBAKE_MARKERS = ("Ã", "Ä", "Å")


def _relative(path: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _collect_files(raw_dir: Path) -> list[Path]:
    return sorted(path for path in raw_dir.rglob("*") if path.is_file())


def _print_extension_summary(files: list[Path], supported_extensions: set[str]) -> None:
    extension_counts = Counter(path.suffix.lower() or "[no_extension]" for path in files)
    supported_count = sum(
        count for extension, count in extension_counts.items()
        if extension in supported_extensions
    )
    unsupported_count = len(files) - supported_count

    print("=== Uzanti Dagilimi ===")
    for extension, count in extension_counts.most_common():
        support_label = "supported" if extension in supported_extensions else "unsupported"
        print(f"- {extension}: {count} ({support_label})")
    print(f"- toplam: {len(files)}")
    print(f"- supported: {supported_count}")
    print(f"- unsupported: {unsupported_count}")
    print()


def _print_unsupported_files(files: list[Path], supported_extensions: set[str]) -> None:
    unsupported_files = [path for path in files if path.suffix.lower() not in supported_extensions]
    print("=== Unsupported Dosyalar ===")
    if not unsupported_files:
        print("- unsupported dosya yok")
        print()
        return

    grouped = Counter(path.suffix.lower() or "[no_extension]" for path in unsupported_files)
    for extension, count in grouped.most_common():
        print(f"- {extension}: {count}")

    for path in unsupported_files:
        print(f"  - {_relative(path)}")
    print()


def _print_noise_markers(files: list[Path]) -> None:
    print("=== Olasi Gurultu Alanlari ===")
    hits: Counter[str] = Counter()
    for path in files:
        normalized = path.as_posix().lower()
        for marker, label in NOISY_PATH_MARKERS.items():
            if marker in normalized:
                hits[label] += 1

    if not hits:
        print("- belirgin gurultu marker'i bulunmadi")
        print()
        return

    for label, count in hits.most_common():
        print(f"- {label}: {count}")
    print()


def _load_registry_preview(path: Path) -> dict[str, object]:
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"path": _relative(path), "status": f"okunamadi: {exc}"}

    has_mojibake = any(marker in content for marker in MOJIBAKE_MARKERS)
    return {
        "path": _relative(path),
        "status": "ok",
        "total_documents": data.get("total_documents"),
        "collection_name": data.get("collection_name"),
        "has_mojibake_markers": has_mojibake,
    }


def _print_registry_status(metadata_dir: Path) -> None:
    print("=== Registry Durumu ===")
    registry_files = sorted(metadata_dir.glob("doc_registry*.json"))
    if not registry_files:
        print("- registry dosyasi bulunamadi")
        print()
        return

    found_names = {path.name for path in registry_files}
    missing_expected = sorted(EXPECTED_REGISTRY_FILES - found_names)
    has_legacy = LEGACY_REGISTRY_NAME in found_names

    for path in registry_files:
        preview = _load_registry_preview(path)
        print(
            "- {path} | status={status} | collection={collection_name} | total_documents={total_documents} | mojibake={has_mojibake_markers}".format(
                **preview
            )
        )

    if has_legacy and missing_expected:
        print("- uyari: legacy doc_registry.json var, ama collection-bazli registry'ler eksik gorunuyor")
    elif has_legacy:
        print("- not: legacy doc_registry.json hala mevcut")

    if missing_expected:
        print("- eksik beklenen registry dosyalari:")
        for name in missing_expected:
            print(f"  - {name}")
    print()


def _print_schedule_source_classification(raw_dir: Path) -> None:
    print("=== Schedule Kaynak Siniflandirmasi ===")
    schedule_dir = raw_dir / "academic_programs" / "ders_programlari"
    if not schedule_dir.exists():
        print("- schedule klasoru bulunamadi")
        print()
        return

    buckets: dict[str, list[str]] = {
        "weekly_schedule": [],
        "non_weekly_program": [],
        "unknown": [],
    }

    loader = DocumentLoader(min_content_length=1)
    for path in sorted(schedule_dir.glob("*.pdf")):
        doc = loader.load_file(path, category="ders_programlari")
        preview = (doc.content[:4000] if doc else "")
        classification = classify_schedule_document(path.name, preview)
        buckets[classification].append(path.name)

    for key, label in (
        ("weekly_schedule", "haftalik program"),
        ("non_weekly_program", "haftalik olmayan program/katalog"),
        ("unknown", "kararsiz"),
    ):
        print(f"- {label}: {len(buckets[key])}")
        for name in buckets[key]:
            print(f"  - {name}")
    print()


def main() -> None:
    configure_utf8_stdio()

    raw_dir = project_root / "data" / "raw"
    metadata_dir = project_root / "data" / "metadata"

    if not raw_dir.exists():
        raise SystemExit(f"Kaynak klasor bulunamadi: {raw_dir}")

    files = _collect_files(raw_dir)
    supported_extensions = set(DocumentLoader.SUPPORTED_EXTENSIONS)

    print("Belge Korpus Audit")
    print(f"- raw_dir: {_relative(raw_dir)}")
    print(f"- supported_extensions: {sorted(supported_extensions)}")
    print()

    _print_extension_summary(files, supported_extensions)
    _print_unsupported_files(files, supported_extensions)
    _print_noise_markers(files)
    _print_registry_status(metadata_dir)
    _print_schedule_source_classification(raw_dir)


if __name__ == "__main__":
    main()
