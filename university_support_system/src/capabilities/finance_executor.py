"""Deterministic finance capability executors."""

from __future__ import annotations

from typing import Any

from src.capabilities.models import ExecutionResult
from src.core.text_normalization import normalize_text
from src.db.finance_data import fetch_tuition_fee_catalog_entry


_AMOUNT_MARKERS = (
    "ne kadar",
    "kac tl",
    "kac lira",
    "tutar",
    "ucret",
    "ogrenim ucreti",
    "katki payi",
    "donem ucreti",
    "yillik ucret",
)
_NON_AMOUNT_MARKERS = (
    "basvur",
    "basvuru",
    "sart",
    "kosul",
    "nasil",
    "nereye",
    "hangi banka",
    "odeme yontemi",
    "olsaydi",
    "olsaydim",
    "olursa",
    "olursam",
    "gerekir mi",
    "odeyebilir miyim",
    "odenmezse",
    "iade",
    "muafiyet",
    "burs",
    "yaz okulu",
    "yaz donemi",
    "yaz ogretimi",
    "cap",
    "cift anadal",
    "cift ana dal",
    "yandal",
    "yan dal",
    "erasmus",
    "degisim programi",
    "fazla odeme",
    "ucret iadesi",
    "harc iadesi",
)


async def tuition_fee(params: dict[str, Any]) -> ExecutionResult:
    """Fetch the registered tuition fee for a student type and academic unit."""
    query = str(params.get("query") or "").strip()
    if query and not _is_explicit_fee_amount_query(query):
        return ExecutionResult(
            success=False,
            capability="finance.tuition_fee",
            params=params,
            error="not_fee_amount_query",
            fallback_allowed=True,
        )

    student_type = _normalize_student_type(params.get("student_type"))
    unit_name = str(params.get("unit_name") or "").strip()
    academic_year = str(params.get("academic_year") or "").strip() or None
    if student_type not in {"domestic", "international"} or not unit_name:
        return ExecutionResult(
            success=False,
            capability="finance.tuition_fee",
            params=params,
            error="missing_params",
            missing_params=[
                name
                for name, value in (
                    ("student_type", student_type),
                    ("unit_name", unit_name),
                )
                if not value
            ],
            fallback_allowed=False,
        )

    entry = await fetch_tuition_fee_catalog_entry(
        student_type=student_type,
        unit_name=unit_name,
        academic_year=academic_year,
    )
    if entry is None:
        return ExecutionResult(
            success=False,
            capability="finance.tuition_fee",
            params={
                **params,
                "student_type": student_type,
                "unit_name": unit_name,
                "academic_year": academic_year,
            },
            error="not_found",
            fallback_allowed=True,
        )

    return ExecutionResult(
        success=True,
        capability="finance.tuition_fee",
        params={
            **params,
            "student_type": student_type,
            "unit_name": unit_name,
            "academic_year": academic_year,
        },
        records=[entry],
        metadata={
            "student_type": student_type,
            "unit_name": unit_name,
            "academic_year": entry.get("academic_year") or academic_year,
            "source_document": entry.get("source_document"),
        },
        authoritative_no_records=False,
        fallback_allowed=False,
    )


def _normalize_student_type(value: object) -> str | None:
    if not value:
        return None
    lowered = normalize_text(str(value))
    if any(marker in lowered for marker in ("uluslararasi", "international", "yabanci", "foreign")):
        return "international"
    if any(marker in lowered for marker in ("turk", "domestic", "yerli", "turkiye")):
        return "domestic"
    return None


def _is_explicit_fee_amount_query(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    if any(marker in lowered for marker in _NON_AMOUNT_MARKERS):
        return False
    if "borc" in lowered and not any(
        marker in lowered for marker in ("ne kadar", "kac tl", "kac lira", "tutar")
    ):
        return False
    return any(marker in lowered for marker in _AMOUNT_MARKERS)
