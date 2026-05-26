"""add user profile contexts

Revision ID: b6f2d4c8e9a1
Revises: a3b7c9d1e2f4
Create Date: 2026-03-29 15:40:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b6f2d4c8e9a1"
down_revision = "a3b7c9d1e2f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profile_contexts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("context_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("student_number", sa.String(length=20), nullable=True),
        sa.Column("department", sa.String(length=120), nullable=False),
        sa.Column("faculty", sa.String(length=120), nullable=False),
        sa.Column("student_db_id", sa.Integer(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["student_db_id"], ["students.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("context_id"),
    )
    op.create_index(op.f("ix_user_profile_contexts_context_id"), "user_profile_contexts", ["context_id"], unique=True)
    op.create_index(op.f("ix_user_profile_contexts_student_db_id"), "user_profile_contexts", ["student_db_id"], unique=False)
    op.create_index(op.f("ix_user_profile_contexts_user_id"), "user_profile_contexts", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_profile_contexts_user_id"), table_name="user_profile_contexts")
    op.drop_index(op.f("ix_user_profile_contexts_student_db_id"), table_name="user_profile_contexts")
    op.drop_index(op.f("ix_user_profile_contexts_context_id"), table_name="user_profile_contexts")
    op.drop_table("user_profile_contexts")
