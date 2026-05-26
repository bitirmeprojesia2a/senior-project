"""Cache package exports.

Keep package import side effects minimal so runtime cache helpers can be
imported without pulling policy/orchestrator modules into startup.
"""

from __future__ import annotations

from importlib import import_module

from src.cache.policy import (
    QuestionCacheDecision,
    evaluate_question_cache_lookup,
    evaluate_question_cache_storage,
)
from src.cache.question_cache import QuestionCache, build_question_cache_key, question_cache

__all__ = [
    "get_cached_state",
    "invalidate_cached_state",
    "set_cached_state",
    "QuestionCache",
    "QuestionCacheDecision",
    "build_question_cache_key",
    "evaluate_question_cache_lookup",
    "evaluate_question_cache_storage",
    "question_cache",
]

_EXPORT_MAP = {
    "get_cached_state": ("src.cache.conversation_cache", "get_cached_state"),
    "invalidate_cached_state": ("src.cache.conversation_cache", "invalidate_cached_state"),
    "set_cached_state": ("src.cache.conversation_cache", "set_cached_state"),
}


def __getattr__(name: str):
    try:
        module_name, attr_name = _EXPORT_MAP[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)
