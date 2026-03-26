"""Kisisel veri odakli ozet sorgular."""

from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select

from src.db.connection import get_session
from src.db.models import (
    AvailableScholarship,
    Course,
    Scholarship,
    ScholarshipApplication,
    Student,
    StudentCourse,
    Tuition,
)


async def fetch_student_tuition_snapshot(student_id: int) -> dict[str, Any] | None:
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


async def fetch_student_scholarship_snapshot(student_id: int) -> dict[str, Any] | None:
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


async def fetch_student_academic_snapshot(student_id: int) -> dict[str, Any] | None:
    """Ogrencinin akademik durum ozetini getirir."""

    async with get_session() as session:
        student = await session.get(Student, student_id)
        if student is None:
            return None

        courses_stmt = (
            select(StudentCourse, Course)
            .join(Course, StudentCourse.course_id == Course.id)
            .where(StudentCourse.student_id == student_id)
            .order_by(desc(StudentCourse.id))
            .limit(8)
        )
        course_rows = (await session.execute(courses_stmt)).all()

        return {
            "student_id": student.id,
            "student_name": student.full_name,
            "gpa": student.gpa,
            "completed_credits": student.completed_credits,
            "total_credits": student.total_credits,
            "registration_status": student.registration_status,
            "recent_courses": [
                {
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "semester": enrollment.semester,
                    "grade": enrollment.grade,
                    "status": enrollment.status,
                }
                for enrollment, course in course_rows
            ],
        }
