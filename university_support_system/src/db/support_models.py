"""Announcement, office-contact, and telemetry ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.model_base import Base, TimestampMixin, utcnow


class Announcement(TimestampMixin, Base):
    """University announcements periodically fetched and summarized."""

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
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


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


class AgentRegistry(TimestampMixin, Base):
    """Registry table for configured internal agents."""

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
    query_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON)


class AgentTask(TimestampMixin, Base):
    """Lifecycle record for internal agent-to-agent tasks."""

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
