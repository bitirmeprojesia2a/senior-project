"""Kullanici sorgulari icin TTL tabanli in-memory cache."""

from __future__ import annotations

import time

from src.cache.runtime_redis import (
    redis_count_prefix,
    redis_delete,
    redis_delete_prefix,
    redis_get,
    redis_set,
)
from src.core.config import settings
from src.db.schemas import UserQueryResponse


class QuestionCache:
    """Best-effort soru cache'i."""

    _REDIS_KEY_PREFIX = "runtime:question:"

    def __init__(
        self,
        ttl_seconds: int = 300,
        enabled: bool = True,
        max_entries: int | None = None,
    ) -> None:
        self._ttl_seconds = ttl_seconds
        self._enabled = enabled
        self._max_entries = (
            settings.cache.question_cache_max_entries
            if max_entries is None
            else max_entries
        )
        self._store: dict[str, tuple[float, UserQueryResponse]] = {}
        self._hits = 0
        self._misses = 0

    @property
    def enabled(self) -> bool:
        return self._enabled and settings.cache.enabled and settings.cache.question_cache_enabled

    @property
    def redis_enabled(self) -> bool:
        return self.enabled and settings.cache.redis_question_cache_enabled and settings.redis.enabled

    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds

    @property
    def size(self) -> int:
        return len(self._store)

    @property
    def max_entries(self) -> int:
        return self._max_entries

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    def configure(
        self,
        *,
        ttl_seconds: int | None = None,
        enabled: bool | None = None,
        max_entries: int | None = None,
    ) -> None:
        if ttl_seconds is not None:
            self._ttl_seconds = ttl_seconds
        if enabled is not None:
            self._enabled = enabled
        if max_entries is not None:
            self._max_entries = max_entries
            self._evict_lru_if_needed()

    def get(self, key: str) -> UserQueryResponse | None:
        if not self.enabled:
            return None
        try:
            cached_at, response = self._store.pop(key)
        except KeyError:
            return self._get_from_redis_or_miss(key)
        if time.time() - cached_at >= self._ttl_seconds:
            return self._get_from_redis_or_miss(key)
        self._store[key] = (cached_at, response)
        self._hits += 1
        return response.model_copy(deep=True)

    def put(self, key: str, response: UserQueryResponse) -> None:
        if not self.enabled:
            return
        stored = response.model_copy(deep=True)
        self._store[key] = (time.time(), stored)
        self._evict_lru_if_needed()
        if self.redis_enabled and self._ttl_seconds > 0:
            redis_set(
                self._redis_key(key),
                stored.model_dump_json(),
                ttl_seconds=self._ttl_seconds,
            )

    def invalidate(self, key: str | None = None) -> None:
        if key is None:
            self._store.clear()
            if self.redis_enabled:
                redis_delete_prefix(self._REDIS_KEY_PREFIX)
            return
        self._store.pop(key, None)
        if self.redis_enabled:
            redis_delete(self._redis_key(key))

    def clear(self) -> None:
        self.invalidate()

    def reset_stats(self) -> None:
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict[str, int]:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": self.size,
        }

    def distributed_size(self) -> int:
        if not self.redis_enabled:
            return 0
        return redis_count_prefix(self._REDIS_KEY_PREFIX)

    @classmethod
    def _redis_key(cls, key: str) -> str:
        return f"{cls._REDIS_KEY_PREFIX}{key}"

    def _get_from_redis_or_miss(self, key: str) -> UserQueryResponse | None:
        if self._ttl_seconds <= 0:
            self._misses += 1
            return None
        if self.redis_enabled:
            raw = redis_get(self._redis_key(key))
            if raw:
                try:
                    response = UserQueryResponse.model_validate_json(raw)
                    self._store[key] = (time.time(), response.model_copy(deep=True))
                    self._evict_lru_if_needed()
                    self._hits += 1
                    return response.model_copy(deep=True)
                except Exception:
                    redis_delete(self._redis_key(key))
        self._misses += 1
        return None

    def _evict_lru_if_needed(self) -> None:
        if self._max_entries <= 0:
            self._store.clear()
            return
        while len(self._store) > self._max_entries:
            oldest_key = next(iter(self._store))
            self._store.pop(oldest_key, None)


def build_question_cache_key(
    *,
    query: str,
    llm_profile: str | None,
    student_department: str | None,
    student_faculty: str | None,
    student_type: str | None,
    is_authenticated: bool,
) -> str:
    """Sorgu cache anahtarini olusturur."""
    return "||".join(
        [
            query.strip().casefold(),
            (llm_profile or "").strip().casefold(),
            (student_department or "").strip().casefold(),
            (student_faculty or "").strip().casefold(),
            (student_type or "").strip().casefold(),
            "auth" if is_authenticated else "anon",
            "v2",
        ]
    )


question_cache = QuestionCache(
    ttl_seconds=settings.cache.question_cache_ttl_seconds,
    enabled=settings.cache.question_cache_enabled,
    max_entries=settings.cache.question_cache_max_entries,
)


__all__ = [
    "QuestionCache",
    "build_question_cache_key",
    "question_cache",
]
