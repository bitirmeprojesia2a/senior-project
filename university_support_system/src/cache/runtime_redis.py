"""Best-effort Redis helpers for runtime cache layers."""

from __future__ import annotations

import logging

import redis

from src.core.config import settings

logger = logging.getLogger(__name__)

_runtime_redis: redis.Redis | None = None


def get_runtime_redis() -> redis.Redis | None:
    """Return a shared sync Redis client for low-latency runtime caches."""
    global _runtime_redis
    if not settings.redis.enabled:
        return None
    if _runtime_redis is None:
        try:
            _runtime_redis = redis.Redis.from_url(
                settings.redis.url,
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
            )
        except Exception as exc:
            logger.warning("runtime_cache_redis_init_failed reason=%s", exc)
            return None
    return _runtime_redis


def redis_get(key: str) -> str | None:
    client = get_runtime_redis()
    if client is None:
        return None
    try:
        return client.get(key)
    except Exception as exc:
        logger.warning("runtime_cache_redis_get_failed key=%s reason=%s", key, exc)
        return None


def redis_set(key: str, value: str, *, ttl_seconds: int) -> None:
    client = get_runtime_redis()
    if client is None:
        return
    try:
        client.set(key, value, ex=ttl_seconds)
    except Exception as exc:
        logger.warning("runtime_cache_redis_set_failed key=%s reason=%s", key, exc)


def redis_delete(key: str) -> None:
    client = get_runtime_redis()
    if client is None:
        return
    try:
        client.delete(key)
    except Exception as exc:
        logger.warning("runtime_cache_redis_delete_failed key=%s reason=%s", key, exc)


def redis_delete_prefix(prefix: str) -> None:
    client = get_runtime_redis()
    if client is None:
        return
    try:
        cursor = 0
        pattern = f"{prefix}*"
        while True:
            cursor, keys = client.scan(cursor=cursor, match=pattern, count=200)
            if keys:
                client.delete(*keys)
            if cursor == 0:
                break
    except Exception as exc:
        logger.warning("runtime_cache_redis_delete_prefix_failed prefix=%s reason=%s", prefix, exc)


def redis_count_prefix(prefix: str) -> int:
    client = get_runtime_redis()
    if client is None:
        return 0
    try:
        cursor = 0
        total = 0
        pattern = f"{prefix}*"
        while True:
            cursor, keys = client.scan(cursor=cursor, match=pattern, count=200)
            total += len(keys)
            if cursor == 0:
                break
        return total
    except Exception as exc:
        logger.warning("runtime_cache_redis_count_prefix_failed prefix=%s reason=%s", prefix, exc)
        return 0
