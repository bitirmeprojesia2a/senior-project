"""Question cache policy helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core.config import settings
from src.core.constants import RoutingStrategy
from src.db.schemas import UserQueryResponse
from src.orchestrators.query_policy import (
    looks_like_announcement_query,
    looks_like_contact_query,
    looks_like_event_query,
    should_fetch_related_announcements,
)

if TYPE_CHECKING:
    from src.db.conversation_context import ConversationResolution


@dataclass(frozen=True)
class QuestionCacheDecision:
    """Question cache karari ve gerekcesi."""

    allowed: bool
    reason: str


def evaluate_question_cache_lookup(
    *,
    query: str,
    conversation_resolution: ConversationResolution,
    is_authenticated: bool,
    disable_cache: bool = False,
) -> QuestionCacheDecision:
    """Sorgu icin question cache lookup yapilip yapilmayacagini degerlendir."""
    if disable_cache:
        return QuestionCacheDecision(False, "request_disabled")
    if not settings.cache.enabled or not settings.cache.question_cache_enabled:
        return QuestionCacheDecision(False, "cache_disabled")
    if is_authenticated:
        return QuestionCacheDecision(False, "authenticated_query")
    if conversation_resolution.is_follow_up or conversation_resolution.used_context:
        return QuestionCacheDecision(False, "contextual_follow_up")
    if conversation_resolution.announcement_context:
        return QuestionCacheDecision(False, "announcement_follow_up")
    if looks_like_announcement_query(query):
        return QuestionCacheDecision(False, "announcement_query")
    if looks_like_event_query(query):
        return QuestionCacheDecision(False, "event_query")
    if should_fetch_related_announcements(query):
        return QuestionCacheDecision(False, "announcement_related_query")
    if looks_like_contact_query(query):
        return QuestionCacheDecision(False, "contact_query")
    if settings.capability_planner.enabled:
        return QuestionCacheDecision(False, "capability_planner_enabled")
    return QuestionCacheDecision(True, "eligible")


def evaluate_question_cache_storage(
    *,
    question_cache_key: str | None,
    routing,
    final_response: UserQueryResponse,
    used_global_synthesis: bool,
) -> QuestionCacheDecision:
    """Cevabin question cache'e yazilip yazilmayacagini degerlendir."""
    if question_cache_key is None:
        return QuestionCacheDecision(False, "lookup_not_attempted")
    if routing.strategy != RoutingStrategy.DIRECT:
        return QuestionCacheDecision(False, "non_direct_strategy")
    if len(routing.departments) != 1:
        return QuestionCacheDecision(False, "multi_department_routing")
    if used_global_synthesis:
        return QuestionCacheDecision(False, "global_synthesis")
    if len(final_response.departments_involved) != 1:
        return QuestionCacheDecision(False, "multi_department_response")
    if "llm" in final_response.generation_modes:
        return QuestionCacheDecision(False, "llm_generated_response")
    if any(
        (source.metadata or {}).get("record_type") == "announcement"
        for source in final_response.sources
    ):
        return QuestionCacheDecision(False, "announcement_source")
    if any(
        (source.metadata or {}).get("record_type") == "event"
        for source in final_response.sources
    ):
        return QuestionCacheDecision(False, "event_source")
    return QuestionCacheDecision(True, "eligible")
