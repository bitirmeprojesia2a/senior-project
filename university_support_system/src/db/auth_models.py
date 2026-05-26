"""Authentication and user-context ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.model_base import Base, TimestampMixin, utcnow


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
    failed_attempts: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )


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
    """Persistent mapping between a Slack user and a student."""

    __tablename__ = "slack_student_mapping"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slack_user_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UserProfileContext(TimestampMixin, Base):
    """Stored user profile context used for personalized conversations."""

    __tablename__ = "user_profile_contexts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context_id: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    student_number: Mapped[Optional[str]] = mapped_column(String(20))
    department: Mapped[str] = mapped_column(String(120), nullable=False)
    faculty: Mapped[str] = mapped_column(String(120), nullable=False)
    student_type: Mapped[Optional[str]] = mapped_column(String(40))
    student_db_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="SET NULL"), index=True
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
