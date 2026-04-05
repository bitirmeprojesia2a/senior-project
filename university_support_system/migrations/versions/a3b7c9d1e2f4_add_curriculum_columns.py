"""add curriculum columns to courses and course_prerequisites

Revision ID: a3b7c9d1e2f4
Revises: e1f257054c4e
Create Date: 2026-03-28 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3b7c9d1e2f4"
down_revision: Union[str, None] = "e1f257054c4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "courses",
        sa.Column("theory_hours", sa.SmallInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "courses",
        sa.Column("practice_hours", sa.SmallInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "courses",
        sa.Column("lab_hours", sa.SmallInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "courses",
        sa.Column("akts", sa.SmallInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "courses",
        sa.Column("curriculum_semester", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "courses",
        sa.Column("course_type", sa.String(30), nullable=False, server_default="zorunlu"),
    )
    op.add_column(
        "courses",
        sa.Column("elective_group", sa.String(20), nullable=True),
    )

    op.alter_column("courses", "course_name", type_=sa.String(200), existing_nullable=False)

    op.add_column(
        "course_prerequisites",
        sa.Column("prerequisite_group", sa.SmallInteger(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_column("course_prerequisites", "prerequisite_group")
    op.drop_column("courses", "elective_group")
    op.drop_column("courses", "course_type")
    op.drop_column("courses", "curriculum_semester")
    op.drop_column("courses", "akts")
    op.drop_column("courses", "lab_hours")
    op.drop_column("courses", "practice_hours")
    op.drop_column("courses", "theory_hours")
    op.alter_column("courses", "course_name", type_=sa.String(120), existing_nullable=False)
