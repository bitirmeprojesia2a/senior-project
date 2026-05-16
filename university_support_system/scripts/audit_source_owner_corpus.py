"""Offline corpus placement audit for source-owner hardening.

The audit reads document registry metadata only. It does not query Chroma or
call an LLM; the goal is to make source-owner strict-mode readiness visible.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.console import configure_utf8_stdio

configure_utf8_stdio()

from src.core.source_owner_collections import resolve_source_owner_collection_bridge
from src.core.source_ownership import source_owner_routing_policies


_REGISTRY_GLOB = "doc_registry*_docs.json"


def _load_registries(metadata_dir: Path) -> list[dict[str, Any]]:
    registries: list[dict[str, Any]] = []
    for path in sorted(metadata_dir.glob(_REGISTRY_GLOB)):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            registries.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})
            continue
        payload["_path"] = str(path)
        registries.append(payload)
    return registries


def _owner_probe_queries() -> dict[str, list[str]]:
    return {
        "student_affairs_policy": [
            "CAP basvurusu icin GANO kosulu",
            "yatay gecis muafiyet basvurusu",
            "yaz okulu tek ders mazeret",
        ],
        "international_policy": [
            "yabanci ogrenci kayit belgeleri ikamet izni",
            "uluslararasi ogrenci kabul denklik",
        ],
        "tuition_fee_catalog": ["harc ucreti ikinci ogretim"],
        "academic_calendar": ["final sinavlari akademik takvim"],
        "curriculum_catalog": ["BIL203 AKTS on kosul"],
    }


def _audit(metadata_dir: Path) -> dict[str, Any]:
    registries = _load_registries(metadata_dir)
    collections = []
    for registry in registries:
        documents = registry.get("documents") or []
        collections.append(
            {
                "registry": registry.get("_path") or registry.get("path"),
                "collection_name": registry.get("collection_name"),
                "total_documents": registry.get("total_documents") or len(documents),
                "total_chunks": registry.get("total_chunks"),
                "categories": sorted(
                    {
                        str(document.get("category"))
                        for document in documents
                        if isinstance(document, dict) and document.get("category")
                    }
                ),
            }
        )

    bridge_samples: list[dict[str, Any]] = []
    for owner, queries in _owner_probe_queries().items():
        for query in queries:
            bridge = resolve_source_owner_collection_bridge(
                source_owner=owner,
                query=query,
                department=None,
            )
            bridge_samples.append(
                {
                    "source_owner": owner,
                    "query": query,
                    "active": bridge.active,
                    "support_collections": list(bridge.support_collections),
                    "reason": bridge.reason,
                    "activated_by": list(bridge.activated_by),
                }
            )

    return {
        "metadata_dir": str(metadata_dir),
        "collections": collections,
        "source_owner_routing_policies": [
            policy.to_metadata() for policy in source_owner_routing_policies()
        ],
        "bridge_samples": bridge_samples,
        "strict_mode_readiness": {
            "status": "advisory_only",
            "reason": "registry metadata does not yet prove every owner has compatible source_owner metadata in indexed chunks",
        },
    }


def _print_report(payload: dict[str, Any]) -> None:
    print("Source Owner Corpus Audit")
    print(f"Metadata dir: {payload['metadata_dir']}")
    print("-" * 88)
    for collection in payload["collections"]:
        print(
            "{collection}: docs={docs} chunks={chunks} categories={categories}".format(
                collection=collection.get("collection_name") or collection.get("registry"),
                docs=collection.get("total_documents"),
                chunks=collection.get("total_chunks") or "-",
                categories=", ".join(collection.get("categories") or []) or "-",
            )
        )
    print("-" * 88)
    for sample in payload["bridge_samples"]:
        print(
            "owner={owner} active={active} support={support} reason={reason} markers={markers}".format(
                owner=sample["source_owner"],
                active=sample["active"],
                support=", ".join(sample["support_collections"]) or "-",
                reason=sample["reason"] or "-",
                markers=", ".join(sample["activated_by"]) or "-",
            )
        )
    print(f"Strict mode: {payload['strict_mode_readiness']['status']}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit source-owner corpus placement")
    parser.add_argument("--metadata-dir", default="data/metadata")
    parser.add_argument("--output-json", default=None)
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    metadata_dir = Path(args.metadata_dir)
    if not metadata_dir.is_absolute():
        metadata_dir = _ROOT / metadata_dir
    payload = _audit(metadata_dir)
    _print_report(payload)
    if args.output_json:
        output_path = Path(args.output_json)
        if not output_path.is_absolute():
            output_path = _ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
