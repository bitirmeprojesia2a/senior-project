"""Audit that dynamic platform core stays institution/domain neutral."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GenericityFinding:
    severity: str
    code: str
    path: str
    term: str
    line: int
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "term": self.term,
            "line": self.line,
            "message": self.message,
        }


@dataclass
class GenericityAuditReport:
    ok: bool = True
    scanned_files: list[str] = field(default_factory=list)
    errors: list[GenericityFinding] = field(default_factory=list)
    warnings: list[GenericityFinding] = field(default_factory=list)
    allowed_mentions: list[GenericityFinding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_error(self, path: Path, term: str, line: int, message: str) -> None:
        self.ok = False
        self.errors.append(
            GenericityFinding("error", "domain_specific_core_term", str(path), term, line, message)
        )

    def add_allowed(self, path: Path, term: str, line: int, message: str) -> None:
        self.allowed_mentions.append(
            GenericityFinding("info", "allowed_classic_protection_reference", str(path), term, line, message)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "summary": {
                "scanned_file_count": len(self.scanned_files),
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
                "allowed_mention_count": len(self.allowed_mentions),
            },
            "scanned_files": self.scanned_files,
            "errors": [finding.to_dict() for finding in self.errors],
            "warnings": [finding.to_dict() for finding in self.warnings],
            "allowed_mentions": [finding.to_dict() for finding in self.allowed_mentions],
            "notes": self.notes,
        }


_DOMAIN_TERMS = [
    "akts",
    "harc",
    "harç",
    "çap",
    "cift anadal",
    "çift anadal",
    "ders kaydi",
    "ders kaydı",
    "yatay gecis",
    "yatay geçiş",
]

_CLASSIC_PROTECTION_TERMS = ["omu", "ondokuz mayis", "ondokuz mayıs"]

_ALLOWED_CLASSIC_PROTECTION_FILES = {
    "__init__.py",
    "classic_compare.py",
    "compose_template.py",
    "docker_plan.py",
    "genericity_audit.py",
    "models.py",
    "quality_gates.py",
    "readiness.py",
    "runtime_adapter_contract.py",
    "runtime_plan.py",
    "safety_audit.py",
    "shadow_runtime.py",
    "source_ingestion_plan.py",
    "tenant_package.py",
}

_DOMAIN_TERM_DEFINITION_FILES = {"genericity_audit.py"}


def run_genericity_audit(root: str | Path = "src/dynamic_platform") -> GenericityAuditReport:
    root_path = Path(root)
    report = GenericityAuditReport(
        notes=[
            "This audit scans dynamic platform Python core files only.",
            "Education-specific behavior belongs in domain packs/configs, not hardcoded core modules.",
            "OMU mentions are allowed only where they protect the current classic runtime boundary.",
        ]
    )
    for path in sorted(root_path.glob("*.py")):
        report.scanned_files.append(str(path))
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        _scan_file(path, text, report)
    return report


def _scan_file(path: Path, text: str, report: GenericityAuditReport) -> None:
    lower_lines = text.lower().splitlines()
    for line_number, line in enumerate(lower_lines, start=1):
        if path.name not in _DOMAIN_TERM_DEFINITION_FILES:
            for term in _DOMAIN_TERMS:
                if term in line:
                    report.add_error(
                        path,
                        term,
                        line_number,
                        (
                            "Domain-specific education term found in dynamic platform core. "
                            "Move it to a domain pack, tenant profile, or fixture."
                        ),
                    )
        for term in _CLASSIC_PROTECTION_TERMS:
            if term in line:
                if path.name in _ALLOWED_CLASSIC_PROTECTION_FILES:
                    report.add_allowed(
                        path,
                        term,
                        line_number,
                        "Allowed reference used to protect or compare the current classic OMU runtime.",
                    )
                else:
                    report.add_error(
                        path,
                        term,
                        line_number,
                        "OMU-specific reference is not allowed in this dynamic platform core file.",
                    )
