"""add tuition fee catalog

Revision ID: f91c2b7d4e11
Revises: c4d8b91a7f22
Create Date: 2026-03-31 21:20:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f91c2b7d4e11"
down_revision: Union[str, None] = "c4d8b91a7f22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tuition_fee_catalog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("academic_year", sa.String(length=20), nullable=False),
        sa.Column("student_type", sa.String(length=20), nullable=False),
        sa.Column("unit_name", sa.String(length=160), nullable=False),
        sa.Column("normalized_unit_name", sa.String(length=160), nullable=False),
        sa.Column("annual_amount", sa.Float(), nullable=False),
        sa.Column("semester_amount", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="TRY"),
        sa.Column("source_document", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "academic_year",
            "student_type",
            "normalized_unit_name",
            name="uq_tuition_fee_catalog_year_type_unit",
        ),
    )
    op.create_index(op.f("ix_tuition_fee_catalog_academic_year"), "tuition_fee_catalog", ["academic_year"], unique=False)
    op.create_index(op.f("ix_tuition_fee_catalog_student_type"), "tuition_fee_catalog", ["student_type"], unique=False)
    op.create_index(
        op.f("ix_tuition_fee_catalog_normalized_unit_name"),
        "tuition_fee_catalog",
        ["normalized_unit_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tuition_fee_catalog_normalized_unit_name"), table_name="tuition_fee_catalog")
    op.drop_index(op.f("ix_tuition_fee_catalog_student_type"), table_name="tuition_fee_catalog")
    op.drop_index(op.f("ix_tuition_fee_catalog_academic_year"), table_name="tuition_fee_catalog")
    op.drop_table("tuition_fee_catalog")
