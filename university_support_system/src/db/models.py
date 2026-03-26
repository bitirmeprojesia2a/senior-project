"""
Database models (SQLAlchemy ORM)

This module defines the relational schema for the university support
system. Tables are grouped conceptually as:

1. Student Affairs   -> students, courses, course_prerequisites,
                        student_courses, course_registration_periods
2. Finance           -> tuition, payments, installments
3. Scholarships      -> available_scholarships, scholarships,
                        scholarship_applications
4. Authentication    -> otp_codes, verification_sessions,
                        slack_student_mapping
5. Announcements     -> announcements
6. Agent / Telemetry -> agent_registry, query_logs, agent_tasks

Some tables are actively used by the current RAG/LLM core, while others
prepare planned or partial integration layers.

The actual DDL is applied via Alembic migrations; this file is the
single source of truth for application code and migration generation.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class TimestampMixin:
    """Common mixin that adds created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=_utcnow,
        nullable=False,
    )


# ============================================================
# 1. STUDENT AFFAIRS
# ============================================================


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

    # Relationships
    courses: Mapped[list["StudentCourse"]] = relationship(
        "StudentCourse", back_populates="student", lazy="selectin"
    )
    tuitions: Mapped[list["Tuition"]] = relationship(
        "Tuition", back_populates="student", lazy="selectin"
    )
    scholarships: Mapped[list["Scholarship"]] = relationship(
        "Scholarship", back_populates="student", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover - repr convenience
        return f"<Student(student_id={self.student_id}, name={self.full_name})>"


class Course(TimestampMixin, Base):
    """Course catalog entry."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    course_name: Mapped[str] = mapped_column(String(120), nullable=False)
    credits: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=3
    )
    department: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    semester: Mapped[Optional[str]] = mapped_column(String(20))
    instructor: Mapped[Optional[str]] = mapped_column(String(120))

    # Relationships
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

    def __repr__(self) -> str:  # pragma: no cover - repr convenience
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


# ============================================================
# 2. FINANCE
# ============================================================


class Tuition(TimestampMixin, Base):
    """Per-semester tuition information for a student."""

    __tablename__ = "tuition"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    semester: Mapped[str] = mapped_column(String(20), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    has_debt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    debt_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    due_date: Mapped[Optional[Date]] = mapped_column(Date)
    last_payment_date: Mapped[Optional[Date]] = mapped_column(Date)

    student: Mapped[Student] = relationship(
        "Student", back_populates="tuitions", lazy="selectin"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="tuition", lazy="selectin"
    )
    installments: Mapped[list["Installment"]] = relationship(
        "Installment", back_populates="tuition", lazy="selectin"
    )


class Payment(TimestampMixin, Base):
    """Historical payment record for a tuition entry."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tuition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tuition.id", ondelete="RESTRICT"), index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[Date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)
    receipt_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    tuition: Mapped[Tuition] = relationship(
        "Tuition", back_populates="payments", lazy="selectin"
    )


class Installment(TimestampMixin, Base):
    """Installment plan entries for a tuition record."""

    __tablename__ = "installments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tuition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tuition.id", ondelete="RESTRICT"), index=True
    )
    installment_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    due_date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )
    paid_at: Mapped[Optional[Date]] = mapped_column(Date)

    tuition: Mapped[Tuition] = relationship(
        "Tuition", back_populates="installments", lazy="selectin"
    )


# ============================================================
# 3. SCHOLARSHIPS
# ============================================================


class AvailableScholarship(TimestampMixin, Base):
    """Scholarship program that students can apply to."""

    __tablename__ = "available_scholarships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    monthly_amount: Mapped[Optional[float]] = mapped_column(Float)
    min_gpa: Mapped[Optional[float]] = mapped_column(Float)
    deadline: Mapped[Optional[Date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Scholarship(TimestampMixin, Base):
    """Scholarship assigned to a particular student."""

    __tablename__ = "scholarships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    available_scholarship_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("available_scholarships.id", ondelete="RESTRICT")
    )
    monthly_amount: Mapped[Optional[float]] = mapped_column(Float)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[Date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    student: Mapped[Student] = relationship(
        "Student", back_populates="scholarships", lazy="selectin"
    )
    program: Mapped[AvailableScholarship] = relationship(
        "AvailableScholarship", lazy="selectin"
    )


class ScholarshipApplication(TimestampMixin, Base):
    """History of scholarship applications made by students."""

    __tablename__ = "scholarship_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    available_scholarship_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("available_scholarships.id", ondelete="RESTRICT")
    )
    application_date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


# ============================================================
# 4. AUTHENTICATION (OTP + SESSIONS + SLACK MAPPING)
# ============================================================


class OTPCode(TimestampMixin, Base):
    """One-time password entry associated with a student."""

    __tablename__ = "otp_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    failed_attempts: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)


class VerificationSession(TimestampMixin, Base):
    """Active verification session after a successful OTP challenge."""

    __tablename__ = "verification_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    slack_user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    session_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class SlackStudentMapping(TimestampMixin, Base):
    """Slack kullanıcısı ile öğrenci arasında kalıcı eşleme."""

    __tablename__ = "slack_student_mapping"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slack_user_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# ============================================================
# 5. ANNOUNCEMENTS
# ============================================================


class Announcement(TimestampMixin, Base):
    """University announcements periodically fetched and summarized by LLM."""

    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    original_text: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), unique=True)
    faculty: Mapped[Optional[str]] = mapped_column(String(80))
    department: Mapped[Optional[str]] = mapped_column(String(80))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# ============================================================
# 6. OFFICE CONTACTS
# ============================================================


class OfficeContact(TimestampMixin, Base):
    """Contact record that can be suggested by specialist agents."""

    __tablename__ = "office_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_name: Mapped[str] = mapped_column(String(150), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    person_name: Mapped[Optional[str]] = mapped_column(String(120))
    title: Mapped[Optional[str]] = mapped_column(String(80))
    phone_ext: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(120))
    related_agents: Mapped[Optional[list[str]]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# ============================================================
# 7. AGENTS / TELEMETRY
# ============================================================


class AgentRegistry(TimestampMixin, Base):
    """Planlı veya kısmi ajan kayıtları için saklama tablosu."""

    __tablename__ = "agent_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    endpoint: Mapped[Optional[str]] = mapped_column(String(255))
    capabilities: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class QueryLog(TimestampMixin, Base):
    """Telemetry for each user query processed by the system."""

    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="SET NULL"), index=True
    )
    agent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("agent_registry.id", ondelete="SET NULL"), index=True
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    departments: Mapped[Optional[dict]] = mapped_column(JSON)
    routing_strategy: Mapped[Optional[str]] = mapped_column(String(20))
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    response_text: Mapped[Optional[str]] = mapped_column(Text)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    error: Mapped[Optional[str]] = mapped_column(Text)
    # Column name is "metadata" in the database; attribute uses a safer name.
    query_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON)


class AgentTask(TimestampMixin, Base):
    """Planlı veya kısmi ajan görev yaşam döngüsü kaydı."""

    __tablename__ = "agent_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    query_log_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("query_logs.id", ondelete="SET NULL"), index=True
    )
    sender_agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agent_registry.id", ondelete="CASCADE"), index=True
    )
    receiver_agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agent_registry.id", ondelete="CASCADE"), index=True
    )
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="submitted")
    payload: Mapped[Optional[dict]] = mapped_column(JSON)
    result: Mapped[Optional[dict]] = mapped_column(JSON)
    error_msg: Mapped[Optional[str]] = mapped_column(Text)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
