"""add announcement sync tables

Revision ID: 1a2b3c4d5e6f
Revises: 9c31d7b6a8f4
Create Date: 2026-04-16 12:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1a2b3c4d5e6f"
down_revision: Union[str, None] = "9c31d7b6a8f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcement_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False, server_default="html_list"),
        sa.Column("parser_key", sa.String(length=50), nullable=False, server_default="generic_html"),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("list_url", sa.String(length=500), nullable=False),
        sa.Column("faculty", sa.String(length=80), nullable=True),
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
    op.create_index("ix_announcement_sources_department", "announcement_sources", ["department"], unique=False)

    op.add_column(
        "announcements",
        sa.Column("source_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "announcements",
        sa.Column("content_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "announcements",
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "announcements",
        sa.Column("inactive_reason", sa.String(length=80), nullable=True),
    )
    op.create_foreign_key(
        "fk_announcements_source_id_announcement_sources",
        "announcements",
        "announcement_sources",
        ["source_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_announcements_source_id", "announcements", ["source_id"], unique=False)
    op.create_index("ix_announcements_content_hash", "announcements", ["content_hash"], unique=False)

    op.create_table(
        "announcement_sync_runs",
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
        sa.ForeignKeyConstraint(["source_id"], ["announcement_sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_announcement_sync_runs_source_id", "announcement_sync_runs", ["source_id"], unique=False)
    op.create_index("ix_announcement_sync_runs_status", "announcement_sync_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_announcement_sync_runs_status", table_name="announcement_sync_runs")
    op.drop_index("ix_announcement_sync_runs_source_id", table_name="announcement_sync_runs")
    op.drop_table("announcement_sync_runs")

    op.drop_index("ix_announcements_content_hash", table_name="announcements")
    op.drop_index("ix_announcements_source_id", table_name="announcements")
    op.drop_constraint("fk_announcements_source_id_announcement_sources", "announcements", type_="foreignkey")
    op.drop_column("announcements", "inactive_reason")
    op.drop_column("announcements", "last_seen_at")
    op.drop_column("announcements", "content_hash")
    op.drop_column("announcements", "source_id")

    op.drop_index("ix_announcement_sources_department", table_name="announcement_sources")
    op.drop_table("announcement_sources")
