"""add conversation context tables

Revision ID: d2c9a8f14b3e
Revises: f91c2b7d4e11
Create Date: 2026-04-05 18:45:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d2c9a8f14b3e"
down_revision = "f91c2b7d4e11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation_turns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("context_id", sa.String(length=100), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("user_query", sa.Text(), nullable=False),
        sa.Column("resolved_query", sa.Text(), nullable=False),
        sa.Column("assistant_answer", sa.Text(), nullable=False),
        sa.Column("answer_summary", sa.Text(), nullable=True),
        sa.Column("active_topic", sa.String(length=200), nullable=True),
        sa.Column("task_type", sa.String(length=50), nullable=True),
        sa.Column("is_follow_up", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("departments", sa.JSON(), nullable=True),
        sa.Column("source_refs", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_conversation_turns_context_id", "conversation_turns", ["context_id"])
    op.create_index("ix_conversation_turns_active_topic", "conversation_turns", ["active_topic"])

    op.create_table(
        "conversation_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("context_id", sa.String(length=100), nullable=False),
        sa.Column("active_topic", sa.String(length=200), nullable=True),
        sa.Column("rolling_summary", sa.Text(), nullable=True),
        sa.Column("active_entities", sa.JSON(), nullable=True),
        sa.Column("last_departments", sa.JSON(), nullable=True),
        sa.Column("last_source_refs", sa.JSON(), nullable=True),
        sa.Column("last_task_type", sa.String(length=50), nullable=True),
        sa.Column(
            "last_turn_id",
            sa.Integer(),
            sa.ForeignKey("conversation_turns.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("last_user_query", sa.Text(), nullable=True),
        sa.Column("last_resolved_query", sa.Text(), nullable=True),
        sa.Column("last_assistant_answer", sa.Text(), nullable=True),
        sa.Column("turn_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_conversation_states_context_id", "conversation_states", ["context_id"], unique=True)
    op.create_index("ix_conversation_states_active_topic", "conversation_states", ["active_topic"])
    op.create_index("ix_conversation_states_last_turn_id", "conversation_states", ["last_turn_id"])


def downgrade() -> None:
    op.drop_index("ix_conversation_states_last_turn_id", table_name="conversation_states")
    op.drop_index("ix_conversation_states_active_topic", table_name="conversation_states")
    op.drop_index("ix_conversation_states_context_id", table_name="conversation_states")
    op.drop_table("conversation_states")

    op.drop_index("ix_conversation_turns_active_topic", table_name="conversation_turns")
    op.drop_index("ix_conversation_turns_context_id", table_name="conversation_turns")
    op.drop_table("conversation_turns")
