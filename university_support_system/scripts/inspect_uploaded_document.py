"""Inspect uploaded document extraction without starting Slack.

Usage:
    python -m scripts.inspect_uploaded_document --file path/to/document.pdf
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.transcripts.service import TranscriptProcessingError, TranscriptProcessor


def _print(text: object = "") -> None:
    output = str(text)
    try:
        print(output)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(output.encode("utf-8", errors="replace") + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect uploaded document extraction.")
    parser.add_argument("--file", required=True, help="Path to the document to inspect.")
    parser.add_argument("--mimetype", default=None, help="Optional MIME type override.")
    parser.add_argument("--preview-chars", type=int, default=1200, help="Raw text preview length.")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        _print(f"File not found: {path}")
        return 2

    processor = TranscriptProcessor()
    try:
        document = processor.process_bytes(
            filename=path.name,
            content=path.read_bytes(),
            mimetype=args.mimetype,
        )
    except TranscriptProcessingError as exc:
        _print(f"Document could not be processed: {exc}")
        return 1

    _print("== Document ==")
    _print(f"filename: {document.filename}")
    _print(f"document_type: {document.document_type}")
    _print(f"extraction_mode: {document.extraction_mode}")
    _print(f"parse_confidence: {document.parse_confidence}")
    _print(f"warnings: {list(document.warnings)}")
    _print()

    _print("== Extraction Debug ==")
    _print(json.dumps(document.extraction_debug, ensure_ascii=False, indent=2))
    _print()

    _print("== Fields ==")
    if not document.fields:
        _print("(none)")
    for field in document.fields:
        value = field.value if field.value.strip() else "<empty>"
        _print(
            f"- key={field.key!r} label={field.label!r} "
            f"state={field.state} confidence={field.confidence} source={field.source} value={value!r}"
        )
    _print()

    if document.courses:
        _print("== Courses ==")
        for course in document.courses[:40]:
            _print(
                f"- {course.code} {course.name} "
                f"akts={course.akts} credit={course.credit} grade={course.grade} status={course.status}"
            )
        if len(document.courses) > 40:
            _print(f"... {len(document.courses) - 40} more")
        _print()

    preview = " ".join(document.text.split())[: max(args.preview_chars, 0)]
    _print("== Text Preview ==")
    _print(preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
