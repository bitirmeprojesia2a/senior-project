"""Retriever icin TTL tabanli sorgu cache'i."""

from copy import deepcopy
import time
from typing import Any, Dict, List


class _QueryCache:
    """TTL tabanli in-memory sorgu cache'i."""

    def __init__(self, ttl: int = 300):
        self._store: Dict[str, tuple[float, List[Dict[str, Any]]]] = {}
        self._ttl = ttl

    def get(self, key: str) -> List[Dict[str, Any]] | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        timestamp, results = entry
        if time.time() - timestamp < self._ttl:
            return deepcopy(results)
        del self._store[key]
        return None

    def put(self, key: str, results: List[Dict[str, Any]]) -> None:
        self._store[key] = (time.time(), deepcopy(results))

    def invalidate(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)
