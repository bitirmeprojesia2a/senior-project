"""Finance ORM models."""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.model_base import Base, TimestampMixin


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
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    last_payment_date: Mapped[Optional[date]] = mapped_column(Date)

    student: Mapped["Student"] = relationship(
        "Student", back_populates="tuitions", lazy="selectin"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="tuition", lazy="selectin"
    )
    installments: Mapped[list["Installment"]] = relationship(
        "Installment", back_populates="tuition", lazy="selectin"
    )


class TuitionFeeCatalog(TimestampMixin, Base):
    """Structured tuition fee table keyed by student type and unit."""

    __tablename__ = "tuition_fee_catalog"
    __table_args__ = (
        UniqueConstraint(
            "academic_year",
            "student_type",
            "normalized_unit_name",
            name="uq_tuition_fee_catalog_year_type_unit",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    student_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    unit_name: Mapped[str] = mapped_column(String(160), nullable=False)
    normalized_unit_name: Mapped[str] = mapped_column(
        String(160), nullable=False, index=True
    )
    annual_amount: Mapped[float] = mapped_column(Float, nullable=False)
    semester_amount: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="TRY"
    )
    source_document: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Payment(TimestampMixin, Base):
    """Historical payment record for a tuition entry."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tuition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tuition.id", ondelete="RESTRICT"), index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
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
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )
    paid_at: Mapped[Optional[date]] = mapped_column(Date)

    tuition: Mapped[Tuition] = relationship(
        "Tuition", back_populates="installments", lazy="selectin"
    )
