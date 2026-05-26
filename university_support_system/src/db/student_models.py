"""Student affairs ORM models."""

from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, SmallInteger, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.model_base import Base, TimestampMixin


class Student(TimestampMixin, Base):
    """Core student record used by all departments."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    faculty: Mapped[str] = mapped_column(String(80), nullable=False)
    student_type: Mapped[Optional[str]] = mapped_column(String(40), index=True)
    class_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    enrollment_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    registration_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
    )
    gpa: Mapped[Optional[float]] = mapped_column(Float)
    total_credits: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    completed_credits: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    current_semester: Mapped[Optional[str]] = mapped_column(String(20))

    courses: Mapped[list["StudentCourse"]] = relationship(
        "StudentCourse", back_populates="student", lazy="selectin"
    )
    tuitions: Mapped[list["Tuition"]] = relationship(
        "Tuition", back_populates="student", lazy="selectin"
    )
    scholarships: Mapped[list["Scholarship"]] = relationship(
        "Scholarship", back_populates="student", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Student(student_id={self.student_id}, name={self.full_name})>"


class Course(TimestampMixin, Base):
    """Course catalog entry."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    credits: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=3)
    department: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    semester: Mapped[Optional[str]] = mapped_column(String(20))
    instructor: Mapped[Optional[str]] = mapped_column(String(120))
    theory_hours: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0"
    )
    practice_hours: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0"
    )
    lab_hours: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0"
    )
    akts: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0"
    )
    curriculum_semester: Mapped[Optional[int]] = mapped_column(SmallInteger)
    course_type: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="zorunlu"
    )
    elective_group: Mapped[Optional[str]] = mapped_column(String(20))

    enrollments: Mapped[list["StudentCourse"]] = relationship(
        "StudentCourse", back_populates="course", lazy="selectin"
    )
    prerequisites: Mapped[list["CoursePrerequisite"]] = relationship(
        "CoursePrerequisite",
        foreign_keys="CoursePrerequisite.course_id",
        back_populates="course",
        lazy="selectin",
    )
    required_for: Mapped[list["CoursePrerequisite"]] = relationship(
        "CoursePrerequisite",
        foreign_keys="CoursePrerequisite.prerequisite_id",
        back_populates="prerequisite_course",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Course(code={self.course_code}, name={self.course_name})>"


class CoursePrerequisite(Base):
    """Many-to-many mapping for course prerequisites."""

    __tablename__ = "course_prerequisites"

    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )
    prerequisite_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )
    prerequisite_group: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="1"
    )

    course: Mapped[Course] = relationship(
        "Course",
        foreign_keys=[course_id],
        back_populates="prerequisites",
    )
    prerequisite_course: Mapped[Course] = relationship(
        "Course",
        foreign_keys=[prerequisite_id],
        back_populates="required_for",
    )


class StudentCourse(TimestampMixin, Base):
    """Enrollment and grade information for a student in a course."""

    __tablename__ = "student_courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="RESTRICT"), index=True
    )
    semester: Mapped[str] = mapped_column(String(20), nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(5))
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="enrolled",
    )

    student: Mapped[Student] = relationship(
        "Student", back_populates="courses", lazy="selectin"
    )
    course: Mapped[Course] = relationship(
        "Course", back_populates="enrollments", lazy="selectin"
    )


class CourseRegistrationPeriod(TimestampMixin, Base):
    """Registration window for a given academic semester."""

    __tablename__ = "course_registration_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    semester: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class CourseScheduleSlot(TimestampMixin, Base):
    """Structured department timetable rows for future hybrid schedule answers."""

    __tablename__ = "course_schedule_slots"
    __table_args__ = (
        UniqueConstraint(
            "academic_year",
            "term",
            "department",
            "course_key",
            "schedule_group",
            "section",
            "day_of_week",
            "start_time",
            "classroom",
            name="uq_course_schedule_slot_identity",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    term: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    course_code: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    course_key: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    course_name: Mapped[Optional[str]] = mapped_column(String(200))
    schedule_group: Mapped[str] = mapped_column(String(40), nullable=False, default="", index=True)
    section: Mapped[str] = mapped_column(String(20), nullable=False, default="", index=True)
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time(), nullable=False)
    end_time: Mapped[Optional[time]] = mapped_column(Time())
    classroom: Mapped[Optional[str]] = mapped_column(String(100))
    instructor: Mapped[Optional[str]] = mapped_column(String(120))
    source_document: Mapped[Optional[str]] = mapped_column(String(255))
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
