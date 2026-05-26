"""Sorgu bazli performans profilleme yardimcilari."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Iterator


_CURRENT_PROFILER: ContextVar["QueryProfiler | None"] = ContextVar(
    "current_query_profiler",
    default=None,
)


@dataclass
class ProfileEvent:
    """Tek bir zamanlanmis asama kaydi."""

    name: str
    started_at_ms: float
    ended_at_ms: float | None = None
    duration_ms: float | None = None
    parent: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "name": self.name,
            "started_at_ms": round(self.started_at_ms, 3),
            "ended_at_ms": round(self.ended_at_ms or 0.0, 3),
            "duration_ms": round(self.duration_ms or 0.0, 3),
            "parent": self.parent,
        }
        if self.meta:
            payload["meta"] = self.meta
        return payload


class QueryProfiler:
    """Bir sorgu akisindaki asamalari toplar."""

    def __init__(self, *, label: str | None = None) -> None:
        self.label = label
        self._origin = perf_counter()
        self._stack: list[int] = []
        self._events: list[ProfileEvent] = []
        self._attributes: dict[str, Any] = {}

    def _now_ms(self) -> float:
        return (perf_counter() - self._origin) * 1000

    def set_attribute(self, key: str, value: Any) -> None:
        self._attributes[key] = value

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self._attributes.get(key, default)

    def append_attribute_list(self, key: str, value: Any) -> None:
        current = self._attributes.get(key)
        if current is None:
            self._attributes[key] = [value]
            return
        if not isinstance(current, list):
            current = [current]
            self._attributes[key] = current
        current.append(value)

    def start(self, name: str, **meta: Any) -> int:
        parent = None
        if self._stack:
            parent = self._events[self._stack[-1]].name
        event = ProfileEvent(
            name=name,
            started_at_ms=self._now_ms(),
            parent=parent,
            meta={k: v for k, v in meta.items() if v is not None},
        )
        self._events.append(event)
        index = len(self._events) - 1
        self._stack.append(index)
        return index

    def finish(self, index: int, **meta: Any) -> None:
        event = self._events[index]
        event.ended_at_ms = self._now_ms()
        event.duration_ms = event.ended_at_ms - event.started_at_ms
        if meta:
            event.meta.update({k: v for k, v in meta.items() if v is not None})
        if self._stack and self._stack[-1] == index:
            self._stack.pop()
        elif index in self._stack:
            self._stack.remove(index)

    @contextmanager
    def stage(self, name: str, **meta: Any) -> Iterator[None]:
        index = self.start(name, **meta)
        try:
            yield
        finally:
            self.finish(index)

    def note(self, name: str, **meta: Any) -> None:
        index = self.start(name, **meta)
        self.finish(index)

    def snapshot(self) -> dict[str, Any]:
        total_ms = self._now_ms()
        return {
            "label": self.label,
            "total_ms": round(total_ms, 3),
            "attributes": dict(self._attributes),
            "events": [event.to_dict() for event in self._events],
        }


def get_current_profiler() -> QueryProfiler | None:
    """Aktif profili dondurur."""
    return _CURRENT_PROFILER.get()


@contextmanager
def activate_profiler(profiler: QueryProfiler) -> Iterator[QueryProfiler]:
    """Bir profili mevcut context'e baglar."""
    token: Token = _CURRENT_PROFILER.set(profiler)
    try:
        yield profiler
    finally:
        _CURRENT_PROFILER.reset(token)


@contextmanager
def profile_stage(name: str, **meta: Any) -> Iterator[None]:
    """Aktif profiler varsa asamayi zamanlar, yoksa no-op davranir."""
    profiler = get_current_profiler()
    if profiler is None:
        yield
        return
    with profiler.stage(name, **meta):
        yield
