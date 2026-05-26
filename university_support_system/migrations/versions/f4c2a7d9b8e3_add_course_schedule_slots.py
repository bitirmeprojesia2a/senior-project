"""add course schedule slots

Revision ID: f4c2a7d9b8e3
Revises: e7b4f2a1c9d0
Create Date: 2026-04-12 20:30:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f4c2a7d9b8e3"
down_revision: Union[str, None] = "e7b4f2a1c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_schedule_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("academic_year", sa.String(length=20), nullable=False),
        sa.Column("term", sa.String(length=20), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=False),
        sa.Column("course_code", sa.String(length=20), nullable=False),
        sa.Column("course_name", sa.String(length=200), nullable=True),
        sa.Column("section", sa.String(length=20), nullable=True),
        sa.Column("day_of_week", sa.String(length=20), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("classroom", sa.String(length=100), nullable=True),
        sa.Column("instructor", sa.String(length=120), nullable=True),
        sa.Column("source_document", sa.String(length=255), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "academic_year",
            "term",
            "department",
            "course_code",
            "section",
            "day_of_week",
            "start_time",
            "classroom",
            name="uq_course_schedule_slot_identity",
        ),
    )
    op.create_index(op.f("ix_course_schedule_slots_academic_year"), "course_schedule_slots", ["academic_year"], unique=False)
    op.create_index(op.f("ix_course_schedule_slots_term"), "course_schedule_slots", ["term"], unique=False)
    op.create_index(op.f("ix_course_schedule_slots_department"), "course_schedule_slots", ["department"], unique=False)
    op.create_index(op.f("ix_course_schedule_slots_course_code"), "course_schedule_slots", ["course_code"], unique=False)
    op.create_index(op.f("ix_course_schedule_slots_section"), "course_schedule_slots", ["section"], unique=False)
    op.create_index(op.f("ix_course_schedule_slots_day_of_week"), "course_schedule_slots", ["day_of_week"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_course_schedule_slots_day_of_week"), table_name="course_schedule_slots")
    op.drop_index(op.f("ix_course_schedule_slots_section"), table_name="course_schedule_slots")
    op.drop_index(op.f("ix_course_schedule_slots_course_code"), table_name="course_schedule_slots")
    op.drop_index(op.f("ix_course_schedule_slots_department"), table_name="course_schedule_slots")
    op.drop_index(op.f("ix_course_schedule_slots_term"), table_name="course_schedule_slots")
    op.drop_index(op.f("ix_course_schedule_slots_academic_year"), table_name="course_schedule_slots")
    op.drop_table("course_schedule_slots")
