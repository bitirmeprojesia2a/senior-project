"""add announcement display summary

Revision ID: 7c4e2d9a1b3f
Revises: 2f8a6b1c4d7e
Create Date: 2026-04-16 22:10:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c4e2d9a1b3f"
down_revision: Union[str, None] = "2f8a6b1c4d7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "announcements",
        sa.Column("display_summary", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("announcements", "display_summary")
