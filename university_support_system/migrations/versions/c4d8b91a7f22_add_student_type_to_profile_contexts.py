"""add student_type to user profile contexts

Revision ID: c4d8b91a7f22
Revises: b6f2d4c8e9a1
Create Date: 2026-03-29 20:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4d8b91a7f22"
down_revision = "b6f2d4c8e9a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_profile_contexts",
        sa.Column("student_type", sa.String(length=40), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_profile_contexts", "student_type")
