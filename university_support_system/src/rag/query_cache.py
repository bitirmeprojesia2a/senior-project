"""Retriever icin TTL tabanli sorgu cache'i."""

import json
import time
from typing import Any, Dict, List

from copy import deepcopy

from src.cache.runtime_redis import (
    redis_count_prefix,
    redis_delete,
    redis_delete_prefix,
    redis_get,
    redis_set,
)
from src.core.config import settings


class _QueryCache:
    """TTL tabanli in-memory sorgu cache'i."""

    _REDIS_KEY_PREFIX = "runtime:retriever:"

    def __init__(self, ttl: int = 300, enabled: bool = True, max_entries: int | None = None):
        self._store: Dict[str, tuple[float, List[Dict[str, Any]]]] = {}
        self._ttl = ttl
        self._enabled = enabled
        self._max_entries = (
            settings.cache.retriever_query_cache_max_entries
            if max_entries is None
            else max_entries
        )

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def redis_enabled(self) -> bool:
        return (
            self._enabled
            and settings.cache.enabled
            and settings.cache.retriever_query_cache_enabled
            and settings.cache.redis_retriever_query_cache_enabled
            and settings.redis.enabled
        )

    @property
    def max_entries(self) -> int:
        return self._max_entries

    def configure(
        self,
        *,
        ttl: int | None = None,
        enabled: bool | None = None,
        max_entries: int | None = None,
    ) -> None:
        if ttl is not None:
            self._ttl = ttl
        if enabled is not None:
            self._enabled = enabled
        if max_entries is not None:
            self._max_entries = max_entries
            self._evict_lru_if_needed()

    def get(self, key: str) -> List[Dict[str, Any]] | None:
        if not self._enabled:
            return None
        try:
            timestamp, results = self._store.pop(key)
        except KeyError:
            return self._get_from_redis(key)
        if time.time() - timestamp < self._ttl:
            self._store[key] = (timestamp, results)
            return deepcopy(results)
        return self._get_from_redis(key)

    def put(self, key: str, results: List[Dict[str, Any]]) -> None:
        if not self._enabled:
            return
        stored = deepcopy(results)
        self._store[key] = (time.time(), stored)
        self._evict_lru_if_needed()
        if self.redis_enabled and self._ttl > 0:
            redis_set(
                self._redis_key(key),
                json.dumps(stored, ensure_ascii=False),
                ttl_seconds=self._ttl,
            )

    def invalidate(self) -> None:
        self._store.clear()
        if self.redis_enabled:
            redis_delete_prefix(self._REDIS_KEY_PREFIX)

    @property
    def size(self) -> int:
        return len(self._store)

    @classmethod
    def distributed_size(cls) -> int:
        if not (
            settings.cache.enabled
            and settings.cache.retriever_query_cache_enabled
            and settings.cache.redis_retriever_query_cache_enabled
            and settings.redis.enabled
        ):
            return 0
        return redis_count_prefix(cls._REDIS_KEY_PREFIX)

    @classmethod
    def _redis_key(cls, key: str) -> str:
        return f"{cls._REDIS_KEY_PREFIX}{key}"

    def _get_from_redis(self, key: str) -> List[Dict[str, Any]] | None:
        if self._ttl <= 0:
            return None
        if not self.redis_enabled:
            return None
        raw = redis_get(self._redis_key(key))
        if not raw:
            return None
        try:
            results = json.loads(raw)
        except Exception:
            redis_delete(self._redis_key(key))
            return None
        self._store[key] = (time.time(), deepcopy(results))
        self._evict_lru_if_needed()
        return deepcopy(results)

    def _evict_lru_if_needed(self) -> None:
        if self._max_entries <= 0:
            self._store.clear()
            return
        while len(self._store) > self._max_entries:
            oldest_key = next(iter(self._store))
            self._store.pop(oldest_key, None)


def clear_shared_query_cache() -> None:
    _QueryCache(enabled=True).invalidate()


def shared_query_cache_size() -> int:
    return _QueryCache.distributed_size()
