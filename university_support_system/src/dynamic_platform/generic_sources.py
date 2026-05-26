"""Tenant-scoped local source loading for the dynamic pilot runtime.

The reader is intentionally small and offline-first. It only reads sources
declared in the tenant source catalog and does not reach out to the network.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from src.dynamic_platform.models import DynamicPlatformBundle, SourceCatalogEntry


@dataclass(frozen=True)
class SourceExcerpt:
    source_id: str
    source_family: str
    owner_agent: str
    authority_level: str
    text: str
    score: int

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "source_family": self.source_family,
            "owner_agent": self.owner_agent,
            "authority_level": self.authority_level,
            "text": self.text,
            "score": self.score,
        }


@dataclass(frozen=True)
class SourceReadResult:
    source: SourceCatalogEntry
    text: str
    warnings: list[str] = field(default_factory=list)


class TenantSourceReader:
    """Read tenant source catalog entries without cross-tenant fallback."""

    def __init__(self, bundle: DynamicPlatformBundle, *, project_root: str | Path = ".") -> None:
        self.bundle = bundle
        self.project_root = Path(project_root)

    def read(self, source: SourceCatalogEntry) -> SourceReadResult:
        if not source.enabled:
            return SourceReadResult(source=source, text="", warnings=["source_disabled"])
        if not source.path:
            return SourceReadResult(source=source, text="", warnings=["source_has_no_path"])
        path = Path(source.path)
        if not path.is_absolute():
            path = self.project_root / path
        try:
            if source.adapter == "structured_csv":
                return SourceReadResult(source=source, text=_read_csv(path))
            if path.suffix.lower() in {".txt", ".md", ".csv"}:
                return SourceReadResult(source=source, text=path.read_text(encoding="utf-8"))
            return SourceReadResult(source=source, text="", warnings=[f"unsupported_local_source_type:{path.suffix}"])
        except OSError as exc:
            return SourceReadResult(source=source, text="", warnings=[f"source_read_failed:{exc.__class__.__name__}"])

    def search(
        self,
        *,
        query: str,
        capabilities: list[str],
        source_families: list[str] | None = None,
        top_k: int = 4,
    ) -> tuple[list[SourceExcerpt], list[str]]:
        allowed_capabilities = set(capabilities)
        allowed_families = set(source_families or [])
        excerpts: list[SourceExcerpt] = []
        warnings: list[str] = []
        for source in self.bundle.source_catalog.sources:
            if allowed_capabilities and not (set(source.capabilities) & allowed_capabilities):
                continue
            if allowed_families and source.source_family not in allowed_families:
                continue
            result = self.read(source)
            warnings.extend(f"{source.source_id}:{warning}" for warning in result.warnings)
            for chunk in _chunks(result.text):
                score = _score(query, chunk)
                if score <= 0:
                    continue
                excerpts.append(
                    SourceExcerpt(
                        source_id=source.source_id,
                        source_family=source.source_family,
                        owner_agent=source.owner_agent,
                        authority_level=source.authority_level,
                        text=chunk,
                        score=score,
                    )
                )
        excerpts.sort(key=lambda item: (-item.score, item.source_id, item.text))
        return excerpts[:top_k], warnings


def _read_csv(path: Path) -> str:
    rows: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            rows.append(" | ".join(reader.fieldnames))
        for row in reader:
            rows.append(" | ".join(f"{key}: {value}" for key, value in row.items() if value))
    return "\n".join(rows)


def _chunks(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = [block.strip() for block in re.split(r"\n\s*\n", normalized) if block.strip()]
    if blocks:
        return blocks
    return [line.strip() for line in normalized.splitlines() if line.strip()]


def _score(query: str, text: str) -> int:
    query_tokens = set(_tokens(query))
    text_tokens = set(_tokens(text))
    if not query_tokens or not text_tokens:
        return 0
    return len(query_tokens & text_tokens)


def _tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.lower().replace("ı", "i").replace("İ", "i"))
    asciiish = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return [token for token in re.findall(r"[a-z0-9]+", asciiish) if len(token) > 1]
