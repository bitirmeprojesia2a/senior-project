"""add student type to students

Revision ID: 6d8e4f2a9c10
Revises: 4e9d2c7b1a6f
Create Date: 2026-04-28 15:30:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6d8e4f2a9c10"
down_revision: Union[str, None] = "4e9d2c7b1a6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("students", sa.Column("student_type", sa.String(length=40), nullable=True))
    op.create_index(op.f("ix_students_student_type"), "students", ["student_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_students_student_type"), table_name="students")
    op.drop_column("students", "student_type")
