"""Finans ve burs odakli veri sorgulari."""

from __future__ import annotations

from sqlalchemy import desc, select

from src.core.text_normalization import collapse_whitespace, normalize_text
from src.db.connection import get_session
from src.db.finance_models import Tuition, TuitionFeeCatalog
from src.db.scholarship_models import (
    AvailableScholarship,
    Scholarship,
    ScholarshipApplication,
)
from src.db.student_models import Student


def _normalize_text(value: str | None) -> str:
    return normalize_text(value)


def _normalize_unit_name(value: str | None) -> str:
    normalized = _normalize_text(collapse_whitespace(value))
    replacements = {
        "fak.": "fakultesi",
        "fak ": "fakultesi ",
        "fakultesi̇": "fakultesi",
        "meslekyuksekokulu": "meslek yuksekokulu",
        "yuksekokulu": "yuksekokulu",
        "yuksek okulu": "yuksekokulu",
        "universitesi": "universitesi",
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return " ".join(normalized.split())


async def fetch_student_tuition_snapshot(student_id: int) -> dict[str, object] | None:
    """Ogrencinin en guncel harc ozetini getirir."""
    async with get_session() as session:
        student = await session.get(Student, student_id)
        if student is None:
            return None

        tuition_stmt = (
            select(Tuition)
            .where(Tuition.student_id == student_id)
            .order_by(desc(Tuition.id))
            .limit(1)
        )
        tuition = (await session.execute(tuition_stmt)).scalar_one_or_none()
        if tuition is None:
            return {
                "student_id": student.id,
                "student_name": student.full_name,
                "tuition": None,
            }

        return {
            "student_id": student.id,
            "student_name": student.full_name,
            "tuition": {
                "semester": tuition.semester,
                "total_amount": tuition.total_amount,
                "paid_amount": tuition.paid_amount,
                "has_debt": tuition.has_debt,
                "debt_amount": tuition.debt_amount,
                "due_date": tuition.due_date.isoformat() if tuition.due_date else None,
                "last_payment_date": tuition.last_payment_date.isoformat() if tuition.last_payment_date else None,
            },
        }


async def fetch_tuition_fee_catalog_entry(
    *,
    student_type: str,
    unit_name: str,
    academic_year: str | None = None,
) -> dict[str, object] | None:
    """Ogrenci tipi ve birime gore kayitli ogrenim ucretini getirir."""
    normalized_type = _normalize_text(student_type)
    normalized_unit = _normalize_unit_name(unit_name)
    if normalized_type not in {"domestic", "international"} or not normalized_unit:
        return None

    async with get_session() as session:
        stmt = select(TuitionFeeCatalog).where(
            TuitionFeeCatalog.student_type == normalized_type,
            TuitionFeeCatalog.normalized_unit_name == normalized_unit,
            TuitionFeeCatalog.is_active.is_(True),
        )
        if academic_year:
            stmt = stmt.where(TuitionFeeCatalog.academic_year == academic_year)
        stmt = stmt.order_by(desc(TuitionFeeCatalog.academic_year), desc(TuitionFeeCatalog.id)).limit(1)
        entry = (await session.execute(stmt)).scalar_one_or_none()
        if entry is None:
            return None

        return {
            "academic_year": entry.academic_year,
            "student_type": entry.student_type,
            "unit_name": entry.unit_name,
            "normalized_unit_name": entry.normalized_unit_name,
            "annual_amount": entry.annual_amount,
            "semester_amount": entry.semester_amount,
            "currency": entry.currency,
            "source_document": entry.source_document,
            "notes": entry.notes,
        }


async def fetch_student_scholarship_snapshot(student_id: int) -> dict[str, object] | None:
    """Ogrencinin burs ve basvuru ozetini getirir."""
    async with get_session() as session:
        student = await session.get(Student, student_id)
        if student is None:
            return None

        scholarship_stmt = (
            select(Scholarship, AvailableScholarship)
            .join(
                AvailableScholarship,
                Scholarship.available_scholarship_id == AvailableScholarship.id,
            )
            .where(Scholarship.student_id == student_id)
            .order_by(desc(Scholarship.id))
            .limit(1)
        )
        scholarship_row = (await session.execute(scholarship_stmt)).first()

        application_stmt = (
            select(ScholarshipApplication, AvailableScholarship)
            .join(
                AvailableScholarship,
                ScholarshipApplication.available_scholarship_id == AvailableScholarship.id,
            )
            .where(ScholarshipApplication.student_id == student_id)
            .order_by(desc(ScholarshipApplication.id))
            .limit(1)
        )
        application_row = (await session.execute(application_stmt)).first()

        scholarship_payload = None
        if scholarship_row is not None:
            scholarship, program = scholarship_row
            scholarship_payload = {
                "program_name": program.name,
                "monthly_amount": scholarship.monthly_amount,
                "status": scholarship.status,
                "start_date": scholarship.start_date.isoformat(),
                "end_date": scholarship.end_date.isoformat() if scholarship.end_date else None,
            }

        application_payload = None
        if application_row is not None:
            application, program = application_row
            application_payload = {
                "program_name": program.name,
                "status": application.status,
                "application_date": application.application_date.isoformat(),
            }

        return {
            "student_id": student.id,
            "student_name": student.full_name,
            "gpa": student.gpa,
            "scholarship": scholarship_payload,
            "latest_application": application_payload,
        }


async def fetch_eligible_scholarships(gpa: float) -> list[dict[str, object]]:
    """Ogrencinin GNO'suna gore basvurulabilecek aktif burslari getirir."""
    async with get_session() as session:
        stmt = (
            select(AvailableScholarship)
            .where(
                AvailableScholarship.is_active.is_(True),
                AvailableScholarship.min_gpa <= gpa,
            )
            .order_by(AvailableScholarship.deadline.asc())
        )
        scholarships = (await session.execute(stmt)).scalars().all()

        return [
            {
                "name": scholarship.name,
                "description": scholarship.description,
                "monthly_amount": scholarship.monthly_amount,
                "min_gpa": scholarship.min_gpa,
                "deadline": scholarship.deadline.isoformat() if scholarship.deadline else None,
            }
            for scholarship in scholarships
        ]
