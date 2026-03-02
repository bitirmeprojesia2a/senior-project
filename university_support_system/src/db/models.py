"""
Veritabanı Modelleri (SQLAlchemy ORM)

PostgreSQL tablo şemaları.
Tablolar: students, courses, student_courses, tuition, payments,
          installments, scholarships, scholarship_applications,
          available_scholarships, user_accounts, it_tickets, known_issues,
          course_registration_periods, query_logs, agent_registry

Kullanım:
    from src.db.models import Student, Tuition, Payment
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    """Timezone-aware UTC zaman damgası üretir."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Tüm modeller için temel sınıf."""
    pass


# ── Ortak Mixin ──────────────────────────────────
class TimestampMixin:
    """created_at ve updated_at alanlarını otomatik ekler."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=_utcnow, nullable=False
    )


# ── Öğrenci ──────────────────────────────────────
class Student(TimestampMixin, Base):
    """Öğrenci tablosu."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    faculty: Mapped[Optional[str]] = mapped_column(String(100))
    grade: Mapped[Optional[int]] = mapped_column(Integer)
    enrollment_year: Mapped[Optional[int]] = mapped_column(Integer)
    registration_status: Mapped[str] = mapped_column(String(50), default="Aktif")
    gpa: Mapped[float] = mapped_column(Float, default=0.0)
    total_credits: Mapped[int] = mapped_column(Integer, default=0)
    completed_credits: Mapped[int] = mapped_column(Integer, default=0)
    current_semester: Mapped[int] = mapped_column(Integer, default=1)

    # İlişkiler
    courses = relationship("StudentCourse", back_populates="student", lazy="selectin")
    tuition = relationship("Tuition", back_populates="student", uselist=False, lazy="selectin")
    scholarships = relationship("Scholarship", back_populates="student", lazy="selectin")
    account = relationship("UserAccount", back_populates="student", uselist=False, lazy="selectin")

    def __repr__(self) -> str:
        return f"<Student(id={self.student_id}, name={self.full_name})>"


# ── Ders ─────────────────────────────────────────
class Course(TimestampMixin, Base):
    """Ders tablosu."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=3)
    department: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    semester: Mapped[Optional[int]] = mapped_column(Integer)
    instructor: Mapped[Optional[str]] = mapped_column(String(100))
    prerequisite: Mapped[Optional[str]] = mapped_column(String(20))

    # İlişkiler
    enrollments = relationship("StudentCourse", back_populates="course", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Course(code={self.course_code}, name={self.course_name})>"


# ── Öğrenci-Ders ─────────────────────────────────
class StudentCourse(TimestampMixin, Base):
    """Öğrenci-Ders ilişki tablosu."""

    __tablename__ = "student_courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), index=True)
    semester: Mapped[Optional[str]] = mapped_column(String(20))
    grade: Mapped[Optional[str]] = mapped_column(String(5))
    status: Mapped[str] = mapped_column(String(20), default="Devam")

    # İlişkiler
    student = relationship("Student", back_populates="courses")
    course = relationship("Course", back_populates="enrollments")


# ── Harç ─────────────────────────────────────────
class Tuition(TimestampMixin, Base):
    """Harç tablosu."""

    __tablename__ = "tuition"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)
    semester: Mapped[Optional[str]] = mapped_column(String(20))
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    paid_amount: Mapped[float] = mapped_column(Float, default=0.0)
    has_debt: Mapped[bool] = mapped_column(Boolean, default=False)
    debt_amount: Mapped[float] = mapped_column(Float, default=0.0)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # İlişkiler
    student = relationship("Student", back_populates="tuition")
    payments = relationship("Payment", back_populates="tuition", lazy="selectin")
    installments = relationship("Installment", back_populates="tuition", lazy="selectin")


# ── Ödeme Geçmişi ────────────────────────────────
class Payment(TimestampMixin, Base):
    """Ödeme geçmişi tablosu."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tuition_id: Mapped[int] = mapped_column(Integer, ForeignKey("tuition.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    receipt_no: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    # İlişkiler
    tuition = relationship("Tuition", back_populates="payments")


# ── Taksit ───────────────────────────────────────
class Installment(TimestampMixin, Base):
    """Taksit tablosu."""

    __tablename__ = "installments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tuition_id: Mapped[int] = mapped_column(Integer, ForeignKey("tuition.id"), index=True)
    installment_number: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Float)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="Bekliyor")

    # İlişkiler
    tuition = relationship("Tuition", back_populates="installments")


# ── Burs ─────────────────────────────────────────
class Scholarship(TimestampMixin, Base):
    """Burs tablosu."""

    __tablename__ = "scholarships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)
    scholarship_name: Mapped[Optional[str]] = mapped_column(String(100))
    scholarship_type: Mapped[Optional[str]] = mapped_column(String(50))
    monthly_amount: Mapped[float] = mapped_column(Float, default=0.0)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="Aktif")

    # İlişkiler
    student = relationship("Student", back_populates="scholarships")


# ── Burs Başvuru ─────────────────────────────────
class ScholarshipApplication(TimestampMixin, Base):
    """Burs başvuru tablosu."""

    __tablename__ = "scholarship_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)
    scholarship_name: Mapped[Optional[str]] = mapped_column(String(100))
    application_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="Beklemede")
    notes: Mapped[Optional[str]] = mapped_column(Text)


# ── Başvuruya Açık Burslar ───────────────────────
class AvailableScholarship(TimestampMixin, Base):
    """Başvuruya açık burslar."""

    __tablename__ = "available_scholarships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    monthly_amount: Mapped[float] = mapped_column(Float, default=0.0)
    min_gpa: Mapped[float] = mapped_column(Float, default=0.0)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# ── Kullanıcı Hesabı (IT) ───────────────────────
class UserAccount(TimestampMixin, Base):
    """Kullanıcı hesap tablosu (IT departmanı)."""

    __tablename__ = "user_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="Aktif")
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    password_last_changed: Mapped[Optional[datetime]] = mapped_column(DateTime)
    password_expired: Mapped[bool] = mapped_column(Boolean, default=False)

    # İlişkiler
    student = relationship("Student", back_populates="account")


# ── IT Destek Talepleri ──────────────────────────
class ITTicket(TimestampMixin, Base):
    """IT destek talepleri."""

    __tablename__ = "it_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)
    ticket_no: Mapped[str] = mapped_column(String(20), unique=True)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    subject: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="Açık", index=True)
    priority: Mapped[str] = mapped_column(String(20), default="Normal")


# ── Bilinen Sorunlar ─────────────────────────────
class KnownIssue(TimestampMixin, Base):
    """Bilinen sorunlar (IT)."""

    __tablename__ = "known_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    solution: Mapped[Optional[str]] = mapped_column(Text)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)


# ── Ders Kayıt Dönemi ────────────────────────────
class CourseRegistrationPeriod(TimestampMixin, Base):
    """Ders kayıt dönemi."""

    __tablename__ = "course_registration_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    semester: Mapped[Optional[str]] = mapped_column(String(20))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)


# ── Sorgu Logları ────────────────────────────────
class QueryLog(TimestampMixin, Base):
    """Kullanıcı sorgu logları — izlenebilirlik ve analiz için."""

    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    departments: Mapped[Optional[dict]] = mapped_column(JSON)
    routing_strategy: Mapped[Optional[str]] = mapped_column(String(50))
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    response_text: Mapped[Optional[str]] = mapped_column(Text)
    response_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    error: Mapped[Optional[str]] = mapped_column(Text)
    query_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON)

    __table_args__ = (
        Index("ix_query_logs_created_at", "created_at"),
    )


# ── Ajan Registry ───────────────────────────────
class AgentRegistry(TimestampMixin, Base):
    """Ajan kayıt tablosu — dinamik ajan keşfi için."""

    __tablename__ = "agent_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    role: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    endpoint: Mapped[Optional[str]] = mapped_column(String(500))
    capabilities: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime)
