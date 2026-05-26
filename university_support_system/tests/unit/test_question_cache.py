"""Question cache unit testleri."""

import time
from fnmatch import fnmatch

from src.core.config import settings
from src.cache.question_cache import QuestionCache, build_question_cache_key
from src.db.schemas import UserQueryResponse


def _response(answer: str = "Test cevabi") -> UserQueryResponse:
    return UserQueryResponse(
        answer=answer,
        departments_involved=["student_affairs"],
        generation_modes=["rag"],
        sources=[],
        response_time_ms=12.5,
        query_id="ctx-1",
    )


class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        _ = ex
        self.store[key] = value

    def delete(self, *keys: str) -> None:
        for key in keys:
            self.store.pop(key, None)

    def scan(self, cursor: int = 0, match: str | None = None, count: int = 200):
        _ = count
        keys = [
            key
            for key in self.store
            if match is None or fnmatch(key, match)
        ]
        return 0, keys


def test_question_cache_put_and_get_returns_copy():
    cache = QuestionCache(ttl_seconds=300, enabled=True)
    cache.put("q1", _response())

    first = cache.get("q1")
    first.answer = "Degisti"

    second = cache.get("q1")
    assert second.answer == "Test cevabi"


def test_question_cache_disabled_returns_none():
    cache = QuestionCache(ttl_seconds=300, enabled=False)
    cache.put("q1", _response())

    assert cache.get("q1") is None
    assert cache.size == 0


def test_question_cache_expiry():
    cache = QuestionCache(ttl_seconds=0, enabled=True)
    cache.put("q1", _response())
    time.sleep(0.01)

    assert cache.get("q1") is None


def test_question_cache_invalidate_single_key():
    cache = QuestionCache(ttl_seconds=300, enabled=True)
    cache.put("q1", _response("A"))
    cache.put("q2", _response("B"))

    cache.invalidate("q1")

    assert cache.get("q1") is None
    assert cache.get("q2").answer == "B"


def test_question_cache_evicts_oldest_when_max_entries_exceeded(monkeypatch):
    monkeypatch.setattr(settings.cache, "redis_question_cache_enabled", False)
    cache = QuestionCache(ttl_seconds=300, enabled=True, max_entries=2)

    cache.put("q1", _response("A"))
    cache.put("q2", _response("B"))
    cache.put("q3", _response("C"))

    assert cache.get("q1") is None
    assert cache.get("q2").answer == "B"
    assert cache.get("q3").answer == "C"
    assert cache.size == 2


def test_question_cache_get_marks_entry_recently_used(monkeypatch):
    monkeypatch.setattr(settings.cache, "redis_question_cache_enabled", False)
    cache = QuestionCache(ttl_seconds=300, enabled=True, max_entries=2)
    cache.put("q1", _response("A"))
    cache.put("q2", _response("B"))

    assert cache.get("q1").answer == "A"
    cache.put("q3", _response("C"))

    assert cache.get("q1").answer == "A"
    assert cache.get("q2") is None
    assert cache.get("q3").answer == "C"


def test_build_question_cache_key_includes_context_dimensions():
    key1 = build_question_cache_key(
        query="Ders kaydi ne zaman basliyor?",
        llm_profile="fast",
        student_department=None,
        student_faculty=None,
        student_type=None,
        is_authenticated=False,
    )
    key2 = build_question_cache_key(
        query="Ders kaydi ne zaman basliyor?",
        llm_profile="quality",
        student_department=None,
        student_faculty=None,
        student_type=None,
        is_authenticated=False,
    )

    assert key1 != key2
    assert key1.endswith("||v2")


def test_question_cache_reads_back_from_redis_when_local_entry_missing(monkeypatch):
    fake_redis = _FakeRedis()
    monkeypatch.setattr("src.cache.runtime_redis.get_runtime_redis", lambda: fake_redis)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)
    monkeypatch.setattr(settings.cache, "redis_question_cache_enabled", True)
    monkeypatch.setattr(settings.redis, "enabled", True)

    writer = QuestionCache(ttl_seconds=300, enabled=True)
    reader = QuestionCache(ttl_seconds=300, enabled=True)

    writer.put("q-redis", _response("Redis cevabi"))

    restored = reader.get("q-redis")

    assert restored is not None
    assert restored.answer == "Redis cevabi"
    assert reader.hits == 1
    assert reader.size == 1


def test_question_cache_clear_removes_redis_entries(monkeypatch):
    fake_redis = _FakeRedis()
    monkeypatch.setattr("src.cache.runtime_redis.get_runtime_redis", lambda: fake_redis)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)
    monkeypatch.setattr(settings.cache, "redis_question_cache_enabled", True)
    monkeypatch.setattr(settings.redis, "enabled", True)

    cache = QuestionCache(ttl_seconds=300, enabled=True)
    cache.put("q1", _response("A"))
    cache.put("q2", _response("B"))

    assert cache.distributed_size() == 2

    cache.clear()

    assert cache.distributed_size() == 0
    assert cache.size == 0
