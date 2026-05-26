"""add announcement links table

Revision ID: 2f8a6b1c4d7e
Revises: 1a2b3c4d5e6f
Create Date: 2026-04-16 18:20:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f8a6b1c4d7e"
down_revision: Union[str, None] = "1a2b3c4d5e6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcement_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("announcement_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("link_type", sa.String(length=30), nullable=False, server_default="attachment"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["announcement_id"], ["announcements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("announcement_id", "url", name="uq_announcement_links_announcement_url"),
    )
    op.create_index(
        "ix_announcement_links_announcement_id",
        "announcement_links",
        ["announcement_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_announcement_links_announcement_id", table_name="announcement_links")
    op.drop_table("announcement_links")
