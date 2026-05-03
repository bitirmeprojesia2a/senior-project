"""add event sync tables

Revision ID: 4e9d2c7b1a6f
Revises: 8b2f4d6c1a9e
Create Date: 2026-04-17 22:30:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4e9d2c7b1a6f"
down_revision: Union[str, None] = "8b2f4d6c1a9e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False, server_default="html_list"),
        sa.Column("parser_key", sa.String(length=50), nullable=False, server_default="generic_html"),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("list_url", sa.String(length=500), nullable=False),
        sa.Column("faculty", sa.String(length=80), nullable=True),
        sa.Column("unit_name", sa.String(length=120), nullable=True),
        sa.Column("department", sa.String(length=80), nullable=True),
        sa.Column("fetch_interval_minutes", sa.Integer(), nullable=False, server_default="360"),
        sa.Column("max_items_per_run", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("parser_options", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("list_url"),
    )
    op.create_index("ix_event_sources_department", "event_sources", ["department"], unique=False)
    op.create_index("ix_event_sources_unit_name", "event_sources", ["unit_name"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("display_summary", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("faculty", sa.String(length=80), nullable=True),
        sa.Column("unit_name", sa.String(length=120), nullable=True),
        sa.Column("department", sa.String(length=80), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=True),
        sa.Column("location", sa.String(length=300), nullable=True),
        sa.Column("organizer", sa.String(length=200), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("all_day", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("inactive_reason", sa.String(length=80), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["event_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_url"),
    )
    op.create_index("ix_events_source_id", "events", ["source_id"], unique=False)
    op.create_index("ix_events_content_hash", "events", ["content_hash"], unique=False)
    op.create_index("ix_events_unit_name", "events", ["unit_name"], unique=False)
    op.create_index("ix_events_event_type", "events", ["event_type"], unique=False)
    op.create_index("ix_events_starts_at", "events", ["starts_at"], unique=False)

    op.create_table(
        "event_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("link_type", sa.String(length=30), nullable=False, server_default="related"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "url", name="uq_event_links_event_url"),
    )
    op.create_index("ix_event_links_event_id", "event_links", ["event_id"], unique=False)

    op.create_table(
        "event_sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="started"),
        sa.Column("items_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_deactivated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["event_sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_sync_runs_source_id", "event_sync_runs", ["source_id"], unique=False)
    op.create_index("ix_event_sync_runs_status", "event_sync_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_event_sync_runs_status", table_name="event_sync_runs")
    op.drop_index("ix_event_sync_runs_source_id", table_name="event_sync_runs")
    op.drop_table("event_sync_runs")

    op.drop_index("ix_event_links_event_id", table_name="event_links")
    op.drop_table("event_links")

    op.drop_index("ix_events_starts_at", table_name="events")
    op.drop_index("ix_events_event_type", table_name="events")
    op.drop_index("ix_events_unit_name", table_name="events")
    op.drop_index("ix_events_content_hash", table_name="events")
    op.drop_index("ix_events_source_id", table_name="events")
    op.drop_table("events")

    op.drop_index("ix_event_sources_unit_name", table_name="event_sources")
    op.drop_index("ix_event_sources_department", table_name="event_sources")
    op.drop_table("event_sources")
