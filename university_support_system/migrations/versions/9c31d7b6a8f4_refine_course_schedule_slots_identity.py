"""refine course schedule slot identity

Revision ID: 9c31d7b6a8f4
Revises: f4c2a7d9b8e3
Create Date: 2026-04-12 22:25:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c31d7b6a8f4"
down_revision: Union[str, None] = "f4c2a7d9b8e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "course_schedule_slots",
        sa.Column("course_key", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "course_schedule_slots",
        sa.Column("schedule_group", sa.String(length=40), nullable=True),
    )
    op.create_index(
        op.f("ix_course_schedule_slots_course_key"),
        "course_schedule_slots",
        ["course_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_course_schedule_slots_schedule_group"),
        "course_schedule_slots",
        ["schedule_group"],
        unique=False,
    )
    op.alter_column(
        "course_schedule_slots",
        "course_code",
        existing_type=sa.String(length=20),
        nullable=True,
    )
    op.execute("UPDATE course_schedule_slots SET course_key = course_code WHERE course_key IS NULL")
    op.alter_column(
        "course_schedule_slots",
        "course_key",
        existing_type=sa.String(length=200),
        nullable=False,
    )
    op.execute("UPDATE course_schedule_slots SET schedule_group = '' WHERE schedule_group IS NULL")
    op.execute("UPDATE course_schedule_slots SET section = '' WHERE section IS NULL")
    op.alter_column(
        "course_schedule_slots",
        "schedule_group",
        existing_type=sa.String(length=40),
        nullable=False,
        server_default="",
    )
    op.alter_column(
        "course_schedule_slots",
        "section",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default="",
    )
    op.drop_constraint(
        "uq_course_schedule_slot_identity",
        "course_schedule_slots",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_course_schedule_slot_identity",
        "course_schedule_slots",
        [
            "academic_year",
            "term",
            "department",
            "course_key",
            "schedule_group",
            "section",
            "day_of_week",
            "start_time",
            "classroom",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_course_schedule_slot_identity",
        "course_schedule_slots",
        type_="unique",
    )
    op.execute("UPDATE course_schedule_slots SET course_code = COALESCE(course_code, course_key)")
    op.alter_column(
        "course_schedule_slots",
        "course_code",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.alter_column(
        "course_schedule_slots",
        "section",
        existing_type=sa.String(length=20),
        nullable=True,
        server_default=None,
    )
    op.alter_column(
        "course_schedule_slots",
        "schedule_group",
        existing_type=sa.String(length=40),
        nullable=True,
        server_default=None,
    )
    op.create_unique_constraint(
        "uq_course_schedule_slot_identity",
        "course_schedule_slots",
        [
            "academic_year",
            "term",
            "department",
            "course_code",
            "section",
            "day_of_week",
            "start_time",
            "classroom",
        ],
    )
    op.drop_index(op.f("ix_course_schedule_slots_schedule_group"), table_name="course_schedule_slots")
    op.drop_index(op.f("ix_course_schedule_slots_course_key"), table_name="course_schedule_slots")
    op.drop_column("course_schedule_slots", "schedule_group")
    op.drop_column("course_schedule_slots", "course_key")
