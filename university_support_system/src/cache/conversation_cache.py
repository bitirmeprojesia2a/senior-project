"""Redis-backed conversation state cache.

Write-through cache: PostgreSQL remains the source of truth.
Redis is used to avoid DB reads on the hot path (every ``resolve_query``).

When Redis is disabled or unavailable the service degrades gracefully
— callers never see an error, they just hit the database directly.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as aioredis

from src.core.config import settings

logger = logging.getLogger(__name__)

_KEY_PREFIX = "conv:state:"
_DEFAULT_TTL_SECONDS = settings.conversation.ttl_minutes * 60
_CACHE_QUERY_MAX_CHARS = 280
_CACHE_ANSWER_MAX_CHARS = 360
_CACHE_SOURCE_REF_MAX_CHARS = 80

_redis_pool: aioredis.Redis | None = None


def _get_redis() -> aioredis.Redis | None:
    """Return a shared async Redis connection (lazy singleton)."""
    global _redis_pool
    if not settings.redis.enabled:
        return None
    if _redis_pool is None:
        try:
            _redis_pool = aioredis.from_url(
                settings.redis.url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
        except Exception as exc:
            logger.warning("conversation_cache_redis_init_failed reason=%s", exc)
            return None
    return _redis_pool


def _cache_key(context_id: str) -> str:
    return f"{_KEY_PREFIX}{context_id}"


def _compact_text(value: object, *, max_len: int) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    compacted = " ".join(text.split())
    if len(compacted) <= max_len:
        return compacted
    return compacted[: max_len - 3].rstrip() + "..."


def _serialize_state(state_data: Any) -> str:
    """Serialize a ConversationStateData to a JSON string."""
    data = {
        "context_id": state_data.context_id,
        "active_topic": state_data.active_topic,
        "rolling_summary": _compact_text(
            state_data.rolling_summary,
            max_len=settings.conversation.max_rolling_summary_chars,
        ),
        "active_entities": list(state_data.active_entities or []),
        "last_departments": list(state_data.last_departments or []),
        "last_source_refs": [
            ref
            for ref in (
                _compact_text(item, max_len=_CACHE_SOURCE_REF_MAX_CHARS)
                for item in list(state_data.last_source_refs or [])
            )
            if ref
        ][: settings.conversation.max_source_refs],
        "last_task_type": state_data.last_task_type,
        "last_turn_id": state_data.last_turn_id,
        "last_user_query": _compact_text(
            state_data.last_user_query,
            max_len=_CACHE_QUERY_MAX_CHARS,
        ),
        "last_resolved_query": _compact_text(
            state_data.last_resolved_query,
            max_len=_CACHE_QUERY_MAX_CHARS,
        ),
        "last_assistant_answer": _compact_text(
            state_data.last_assistant_answer,
            max_len=_CACHE_ANSWER_MAX_CHARS,
        ),
        "turn_count": state_data.turn_count,
        "updated_at": state_data.updated_at.isoformat(),
    }
    return json.dumps(data, ensure_ascii=False)


def _deserialize_state(raw: str) -> Any:
    """Deserialize a JSON string back to ConversationStateData."""
    from src.db.conversation_context import ConversationStateData

    data = json.loads(raw)
    updated_at_raw = data.get("updated_at", "")
    if updated_at_raw:
        updated_at = datetime.fromisoformat(updated_at_raw)
    else:
        updated_at = datetime.now(timezone.utc)

    return ConversationStateData(
        context_id=data["context_id"],
        active_topic=data.get("active_topic"),
        rolling_summary=data.get("rolling_summary"),
        active_entities=list(data.get("active_entities") or []),
        last_departments=list(data.get("last_departments") or []),
        last_source_refs=list(data.get("last_source_refs") or []),
        last_task_type=data.get("last_task_type"),
        last_turn_id=data.get("last_turn_id"),
        last_user_query=data.get("last_user_query"),
        last_resolved_query=data.get("last_resolved_query"),
        last_assistant_answer=data.get("last_assistant_answer"),
        turn_count=data.get("turn_count", 0),
        updated_at=updated_at,
    )


async def get_cached_state(context_id: str) -> Any | None:
    """Try to read conversation state from Redis.

    Returns ``ConversationStateData`` on hit, ``None`` on miss or error.
    """
    client = _get_redis()
    if client is None:
        return None
    try:
        raw = await client.get(_cache_key(context_id))
        if raw is None:
            return None
        return _deserialize_state(raw)
    except Exception as exc:
        logger.warning("conversation_cache_get_failed context_id=%s reason=%s", context_id, exc)
        return None


async def set_cached_state(state_data: Any, *, ttl_seconds: int | None = None) -> None:
    """Write conversation state to Redis with TTL.

    Failures are logged but never propagated — cache is best-effort.
    """
    client = _get_redis()
    if client is None:
        return
    try:
        key = _cache_key(state_data.context_id)
        value = _serialize_state(state_data)
        await client.set(key, value, ex=ttl_seconds or _DEFAULT_TTL_SECONDS)
    except Exception as exc:
        logger.warning(
            "conversation_cache_set_failed context_id=%s reason=%s",
            state_data.context_id,
            exc,
        )


async def invalidate_cached_state(context_id: str) -> None:
    """Remove a conversation state from Redis cache."""
    client = _get_redis()
    if client is None:
        return
    try:
        await client.delete(_cache_key(context_id))
    except Exception as exc:
        logger.warning(
            "conversation_cache_invalidate_failed context_id=%s reason=%s",
            context_id,
            exc,
        )
