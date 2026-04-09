"""add office contacts table

Revision ID: e7b4f2a1c9d0
Revises: d2c9a8f14b3e
Create Date: 2026-04-06 17:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7b4f2a1c9d0"
down_revision = "d2c9a8f14b3e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "office_contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("unit_name", sa.String(length=150), nullable=False),
        sa.Column("department", sa.String(length=50), nullable=False),
        sa.Column("person_name", sa.String(length=120), nullable=True),
        sa.Column("title", sa.String(length=80), nullable=True),
        sa.Column("phone_ext", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("related_agents", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_office_contacts_department", "office_contacts", ["department"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_office_contacts_department", table_name="office_contacts")
    op.drop_table("office_contacts")
