"""ORM models for multi-turn conversation context."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.model_base import Base, TimestampMixin


class ConversationTurn(TimestampMixin, Base):
    """Persisted user/assistant turn used for follow-up handling."""

    __tablename__ = "conversation_turns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_query: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_summary: Mapped[Optional[str]] = mapped_column(Text)
    active_topic: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    task_type: Mapped[Optional[str]] = mapped_column(String(50))
    is_follow_up: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    departments: Mapped[Optional[list[str]]] = mapped_column(JSON)
    source_refs: Mapped[Optional[list[str]]] = mapped_column(JSON)
    turn_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON)


class ConversationState(TimestampMixin, Base):
    """Rolling state optimized for resolving follow-up questions."""

    __tablename__ = "conversation_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    active_topic: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    rolling_summary: Mapped[Optional[str]] = mapped_column(Text)
    active_entities: Mapped[Optional[list[str]]] = mapped_column(JSON)
    last_departments: Mapped[Optional[list[str]]] = mapped_column(JSON)
    last_source_refs: Mapped[Optional[list[str]]] = mapped_column(JSON)
    last_task_type: Mapped[Optional[str]] = mapped_column(String(50))
    last_turn_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("conversation_turns.id", ondelete="SET NULL"),
        index=True,
    )
    last_user_query: Mapped[Optional[str]] = mapped_column(Text)
    last_resolved_query: Mapped[Optional[str]] = mapped_column(Text)
    last_assistant_answer: Mapped[Optional[str]] = mapped_column(Text)
    turn_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
