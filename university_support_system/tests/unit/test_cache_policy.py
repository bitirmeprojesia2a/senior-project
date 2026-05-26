"""Question cache policy testleri."""

from src.cache.policy import (
    evaluate_question_cache_lookup,
    evaluate_question_cache_storage,
)
from src.core.config import CapabilityPlannerSettings, settings
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.db.conversation_context import ConversationResolution
from src.db.schemas import RAGSource, RoutingResult, UserQueryResponse


def _resolution(query: str, **overrides) -> ConversationResolution:
    payload = {
        "original_query": query,
        "effective_query": query,
        "is_follow_up": False,
        "used_context": False,
        "active_topic": None,
        "department_hints": [],
        "source_hints": [],
    }
    payload.update(overrides)
    return ConversationResolution(**payload)


def _routing(*, departments: list[Department], strategy: RoutingStrategy = RoutingStrategy.DIRECT):
    return RoutingResult(
        departments=departments,
        confidence=0.9,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=strategy,
        reasoning="test",
        task_type=TaskType.REGISTRATION_QUERY,
    )


def _response(*, departments: list[str], generation_modes: list[str], sources=None) -> UserQueryResponse:
    return UserQueryResponse(
        answer="Test cevap",
        departments_involved=departments,
        generation_modes=generation_modes,
        sources=sources or [],
        response_time_ms=10.0,
        query_id="ctx-1",
    )


def test_evaluate_question_cache_lookup_allows_simple_anonymous_query(monkeypatch):
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)
    monkeypatch.setattr(settings, "capability_planner", CapabilityPlannerSettings(mode="off"))

    decision = evaluate_question_cache_lookup(
        query="Ders kaydi ne zaman basliyor?",
        conversation_resolution=_resolution("Ders kaydi ne zaman basliyor?"),
        is_authenticated=False,
    )

    assert decision.allowed is True
    assert decision.reason == "eligible"


def test_evaluate_question_cache_lookup_blocks_when_capability_planner_enabled(monkeypatch):
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)
    monkeypatch.setattr(settings, "capability_planner", CapabilityPlannerSettings(mode="on"))

    decision = evaluate_question_cache_lookup(
        query="Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?",
        conversation_resolution=_resolution(
            "Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?"
        ),
        is_authenticated=False,
    )

    assert decision.allowed is False
    assert decision.reason == "capability_planner_enabled"


def test_evaluate_question_cache_lookup_blocks_request_disabled(monkeypatch):
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)

    decision = evaluate_question_cache_lookup(
        query="Ders kaydi ne zaman basliyor?",
        conversation_resolution=_resolution("Ders kaydi ne zaman basliyor?"),
        is_authenticated=False,
        disable_cache=True,
    )

    assert decision.allowed is False
    assert decision.reason == "request_disabled"


def test_evaluate_question_cache_lookup_blocks_follow_up(monkeypatch):
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)

    decision = evaluate_question_cache_lookup(
        query="Peki ne zaman?",
        conversation_resolution=_resolution(
            "Peki ne zaman?",
            is_follow_up=True,
            used_context=True,
        ),
        is_authenticated=False,
    )

    assert decision.allowed is False
    assert decision.reason == "contextual_follow_up"


def test_evaluate_question_cache_lookup_blocks_event_query(monkeypatch):
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)

    decision = evaluate_question_cache_lookup(
        query="Muhendislik fakultesindeki etkinlikler neler?",
        conversation_resolution=_resolution("Muhendislik fakultesindeki etkinlikler neler?"),
        is_authenticated=False,
    )

    assert decision.allowed is False
    assert decision.reason == "event_query"


def test_evaluate_question_cache_storage_blocks_parallel_response():
    decision = evaluate_question_cache_storage(
        question_cache_key="k1",
        routing=_routing(
            departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
            strategy=RoutingStrategy.PARALLEL,
        ),
        final_response=_response(
            departments=["student_affairs", "finance"],
            generation_modes=["rag"],
        ),
        used_global_synthesis=False,
    )

    assert decision.allowed is False
    assert decision.reason == "non_direct_strategy"


def test_evaluate_question_cache_storage_blocks_llm_response():
    decision = evaluate_question_cache_storage(
        question_cache_key="k1",
        routing=_routing(departments=[Department.ACADEMIC_PROGRAMS]),
        final_response=_response(
            departments=["academic_programs"],
            generation_modes=["llm"],
        ),
        used_global_synthesis=False,
    )

    assert decision.allowed is False
    assert decision.reason == "llm_generated_response"


def test_evaluate_question_cache_storage_allows_simple_direct_response():
    decision = evaluate_question_cache_storage(
        question_cache_key="k1",
        routing=_routing(departments=[Department.STUDENT_AFFAIRS]),
        final_response=_response(
            departments=["student_affairs"],
            generation_modes=["vt"],
        ),
        used_global_synthesis=False,
    )

    assert decision.allowed is True
    assert decision.reason == "eligible"


def test_evaluate_question_cache_storage_blocks_announcement_sources():
    decision = evaluate_question_cache_storage(
        question_cache_key="k1",
        routing=_routing(departments=[Department.STUDENT_AFFAIRS]),
        final_response=_response(
            departments=["student_affairs"],
            generation_modes=["vt"],
            sources=[
                RAGSource(
                    content="duyuru",
                    score=1.0,
                    metadata={"record_type": "announcement"},
                )
            ],
        ),
        used_global_synthesis=False,
    )

    assert decision.allowed is False
    assert decision.reason == "announcement_source"


def test_evaluate_question_cache_storage_blocks_event_sources():
    decision = evaluate_question_cache_storage(
        question_cache_key="k1",
        routing=_routing(departments=[Department.ACADEMIC_PROGRAMS]),
        final_response=_response(
            departments=["event"],
            generation_modes=["vt"],
            sources=[
                RAGSource(
                    content="Etkinlik",
                    score=1.0,
                    metadata={"record_type": "event"},
                )
            ],
        ),
        used_global_synthesis=False,
    )

    assert decision.allowed is False
    assert decision.reason == "event_source"
