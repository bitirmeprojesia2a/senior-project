"""Ogrenci akademik ozet sorgulari."""

from __future__ import annotations

from sqlalchemy import desc, select

from src.db.connection import get_session
from src.db.student_models import Course, Student, StudentCourse


async def fetch_student_academic_snapshot(student_id: int) -> dict[str, object] | None:
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
            "department": student.department,
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
