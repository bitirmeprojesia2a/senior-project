"""Announcement, event, office-contact, and telemetry ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.model_base import Base, TimestampMixin, utcnow


class AnnouncementSource(TimestampMixin, Base):
    """Registry record for a tracked announcement source."""

    __tablename__ = "announcement_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False, default="html_list")
    parser_key: Mapped[str] = mapped_column(String(50), nullable=False, default="generic_html")
    base_url: Mapped[Optional[str]] = mapped_column(String(500))
    list_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    faculty: Mapped[Optional[str]] = mapped_column(String(80))
    unit_name: Mapped[Optional[str]] = mapped_column(String(120), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(80), index=True)
    fetch_interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=360)
    max_items_per_run: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    parser_options: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)


class Announcement(TimestampMixin, Base):
    """University announcements periodically fetched and summarized."""

    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("announcement_sources.id", ondelete="SET NULL"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    original_text: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    display_summary: Mapped[Optional[str]] = mapped_column(Text)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), unique=True)
    faculty: Mapped[Optional[str]] = mapped_column(String(80))
    unit_name: Mapped[Optional[str]] = mapped_column(String(120), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(80))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    inactive_reason: Mapped[Optional[str]] = mapped_column(String(80))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AnnouncementLink(TimestampMixin, Base):
    """Attachment or related link discovered on an announcement detail page."""

    __tablename__ = "announcement_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    announcement_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("announcements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(300), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    link_type: Mapped[str] = mapped_column(String(30), nullable=False, default="attachment")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AnnouncementSyncRun(TimestampMixin, Base):
    """Audit record for each per-source announcement synchronization run."""

    __tablename__ = "announcement_sync_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("announcement_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="started", index=True)
    items_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_deactivated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)


class EventSource(TimestampMixin, Base):
    """Registry record for a tracked event source."""

    __tablename__ = "event_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False, default="html_list")
    parser_key: Mapped[str] = mapped_column(String(50), nullable=False, default="generic_html")
    base_url: Mapped[Optional[str]] = mapped_column(String(500))
    list_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    faculty: Mapped[Optional[str]] = mapped_column(String(80))
    unit_name: Mapped[Optional[str]] = mapped_column(String(120), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(80), index=True)
    fetch_interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=360)
    max_items_per_run: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    parser_options: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)


class Event(TimestampMixin, Base):
    """University events periodically fetched and normalized."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("event_sources.id", ondelete="SET NULL"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    original_text: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    display_summary: Mapped[Optional[str]] = mapped_column(Text)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), unique=True)
    faculty: Mapped[Optional[str]] = mapped_column(String(80))
    unit_name: Mapped[Optional[str]] = mapped_column(String(120), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(80))
    event_type: Mapped[Optional[str]] = mapped_column(String(80), index=True)
    location: Mapped[Optional[str]] = mapped_column(String(300))
    organizer: Mapped[Optional[str]] = mapped_column(String(200))
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    all_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    inactive_reason: Mapped[Optional[str]] = mapped_column(String(80))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class EventLink(TimestampMixin, Base):
    """Attachment or related link discovered on an event detail page."""

    __tablename__ = "event_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(300), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    link_type: Mapped[str] = mapped_column(String(30), nullable=False, default="related")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class EventSyncRun(TimestampMixin, Base):
    """Audit record for each per-source event synchronization run."""

    __tablename__ = "event_sync_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("event_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="started", index=True)
    items_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_deactivated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)


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
