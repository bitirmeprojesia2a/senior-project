"""Process-wide API key rotation helpers.

Clients may be created in several parts of the runtime. A per-client cycle
starts from the first key every time, which can burn the first keys faster than
the rest. This module keeps provider key rotation process-wide while exposing
only non-secret fingerprints to diagnostics.
"""

from __future__ import annotations

import hashlib
import re
import threading
import time
from dataclasses import dataclass


_ORG_RE = re.compile(r"\b(org_[A-Za-z0-9_]+)\b")
_POOLS: dict[tuple[str, str], "ApiKeyPool"] = {}
_POOLS_LOCK = threading.Lock()


@dataclass(frozen=True)
class ApiKeyLease:
    key: str
    fingerprint: str
    index: int
    cooldown_until: float = 0.0
    provider_org_fingerprint: str | None = None


@dataclass
class _ApiKeyEntry:
    key: str
    fingerprint: str
    index: int
    cooldown_until: float = 0.0
    provider_org_fingerprint: str | None = None
    use_count: int = 0
    error_count: int = 0
    last_error_reason: str | None = None


def split_api_keys(raw_keys: str | None) -> list[str]:
    """Parse comma/newline separated keys while preserving order."""
    if not raw_keys:
        return []
    normalized = raw_keys.replace("\n", ",").replace(";", ",")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def api_key_fingerprint(key: str) -> str:
    """Return a non-secret stable fingerprint for diagnostics."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def org_fingerprint_from_message(message: str) -> str | None:
    match = _ORG_RE.search(message or "")
    if not match:
        return None
    return hashlib.sha256(match.group(1).encode("utf-8")).hexdigest()[:12]


def _raw_keys_digest(keys: list[str]) -> str:
    joined = "\n".join(keys)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def get_api_key_pool(pool_id: str, raw_keys: str | None) -> "ApiKeyPool":
    keys = split_api_keys(raw_keys)
    digest = _raw_keys_digest(keys)
    registry_key = (pool_id, digest)
    with _POOLS_LOCK:
        pool = _POOLS.get(registry_key)
        if pool is None:
            pool = ApiKeyPool(pool_id=pool_id, keys=keys)
            _POOLS[registry_key] = pool
        return pool


def reset_api_key_pools() -> None:
    """Test helper: clear process-wide key pools."""
    with _POOLS_LOCK:
        _POOLS.clear()


class ApiKeyPool:
    """Round-robin pool with simple per-key cooldown on provider 429s."""

    def __init__(self, *, pool_id: str, keys: list[str]) -> None:
        self.pool_id = pool_id
        self._entries = [
            _ApiKeyEntry(
                key=key,
                fingerprint=api_key_fingerprint(key),
                index=index,
            )
            for index, key in enumerate(keys)
        ]
        self._cursor = 0
        self._org_cooldowns: dict[str, float] = {}
        self._lock = threading.Lock()

    @property
    def key_count(self) -> int:
        return len(self._entries)

    @property
    def is_available(self) -> bool:
        return bool(self._entries)

    def next_key(self) -> ApiKeyLease:
        if not self._entries:
            raise ValueError("api_key_pool_empty")
        with self._lock:
            now = time.monotonic()
            chosen: _ApiKeyEntry | None = None
            for offset in range(len(self._entries)):
                index = (self._cursor + offset) % len(self._entries)
                candidate = self._entries[index]
                if self._effective_cooldown_until(candidate) <= now:
                    chosen = candidate
                    self._cursor = (index + 1) % len(self._entries)
                    break
            if chosen is None:
                chosen = min(self._entries, key=self._effective_cooldown_until)
                self._cursor = (chosen.index + 1) % len(self._entries)

            chosen.use_count += 1
            return ApiKeyLease(
                key=chosen.key,
                fingerprint=chosen.fingerprint,
                index=chosen.index,
                cooldown_until=self._effective_cooldown_until(chosen),
                provider_org_fingerprint=chosen.provider_org_fingerprint,
            )

    def _effective_cooldown_until(self, entry: _ApiKeyEntry) -> float:
        org_cooldown = (
            self._org_cooldowns.get(entry.provider_org_fingerprint or "", 0.0)
            if entry.provider_org_fingerprint
            else 0.0
        )
        return max(entry.cooldown_until, org_cooldown)

    def mark_error(
        self,
        *,
        fingerprint: str | None,
        reason: str,
        cooldown_seconds: float = 0.0,
        provider_org_fingerprint: str | None = None,
    ) -> None:
        if not fingerprint:
            return
        with self._lock:
            for entry in self._entries:
                if entry.fingerprint != fingerprint:
                    continue
                entry.error_count += 1
                entry.last_error_reason = reason
                if provider_org_fingerprint:
                    entry.provider_org_fingerprint = provider_org_fingerprint
                if cooldown_seconds > 0:
                    entry.cooldown_until = max(
                        entry.cooldown_until,
                        time.monotonic() + cooldown_seconds,
                    )
                    if provider_org_fingerprint:
                        self._org_cooldowns[provider_org_fingerprint] = max(
                            self._org_cooldowns.get(provider_org_fingerprint, 0.0),
                            time.monotonic() + cooldown_seconds,
                        )
                return

    def diagnostics(self) -> dict[str, object]:
        with self._lock:
            return {
                "pool_id": self.pool_id,
                "key_count": len(self._entries),
                "entries": [
                    {
                        "fingerprint": entry.fingerprint,
                        "index": entry.index,
                        "use_count": entry.use_count,
                        "error_count": entry.error_count,
                        "cooldown_active": self._effective_cooldown_until(entry) > time.monotonic(),
                        "provider_org_fingerprint": entry.provider_org_fingerprint,
                        "org_cooldown_active": bool(
                            entry.provider_org_fingerprint
                            and self._org_cooldowns.get(entry.provider_org_fingerprint, 0.0) > time.monotonic()
                        ),
                        "last_error_reason": entry.last_error_reason,
                    }
                    for entry in self._entries
                ],
                "org_cooldowns": {
                    org: until > time.monotonic()
                    for org, until in self._org_cooldowns.items()
                },
            }
