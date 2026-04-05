"""Scholarship ORM models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.model_base import Base, TimestampMixin


class AvailableScholarship(TimestampMixin, Base):
    """Scholarship program that students can apply to."""

    __tablename__ = "available_scholarships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    monthly_amount: Mapped[Optional[float]] = mapped_column(Float)
    min_gpa: Mapped[Optional[float]] = mapped_column(Float)
    deadline: Mapped[Optional[date]] = mapped_column(Date)
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
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    student: Mapped["Student"] = relationship(
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
    application_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
