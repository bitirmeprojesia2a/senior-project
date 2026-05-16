"""FastAPI giris noktasi testleri."""

import pytest
from a2a.types import Role
from fastapi.testclient import TestClient

from src.a2a import build_text_message
from src.api.main import (
    A2AAgentStatus,
    AgentCardSummary,
    app,
    get_agent_card_summaries,
    get_auth_service,
    get_llm_service,
    get_main_orchestrator,
    get_profile_context_service,
    get_telemetry_service,
)
from src.core.config import settings
from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse, RAGSource, UserQueryResponse

pytestmark = pytest.mark.api


class _FakeLLMService:
    async def get_health(self):
        return {
            "status": "healthy",
            "primary": {"name": "groq", "status": "healthy", "model_loaded": True},
            "fallback": {"name": "openai", "available": False},
        }


class _FakeAuthService:
    async def request_otp(self, *, student_number: str, slack_user_id: str | None = None):
        if student_number != "20210001":
            return None
        return {
            "success": True,
            "student_number": "20210001",
            "masked_email": "20******@stu.omu.edu.tr",
            "expires_at": __import__("datetime").datetime(2026, 3, 26, 12, 0, 0),
            "delivery_channel": "email_smtp",
            "otp_preview_code": None,
        }

    async def verify_otp(self, *, student_number: str, otp_code: str, slack_user_id: str | None = None):
        if student_number != "20210001":
            return None
        if otp_code != "123456":
            return {
                "success": False,
                "message": "OTP kodu gecersiz.",
            }
        return {
            "success": True,
            "student_db_id": 42,
            "student_number": "20210001",
            "full_name": "Ahmet Yilmaz",
            "student_department": "bilgisayar_muhendisligi",
            "student_faculty": "Muhendislik Fakultesi",
            "student_type": "domestic",
            "session_token": "session-xyz",
            "expires_at": __import__("datetime").datetime(2026, 3, 26, 20, 0, 0),
        }

    async def resolve_auth_context(self, *, session_token: str | None = None, slack_user_id: str | None = None):
        if session_token == "session-xyz" or slack_user_id == "U123":
            return type(
                "ResolvedContext",
                (),
                {
                    "student_db_id": 42,
                    "student_number": "20210001",
                    "full_name": "Ahmet Yilmaz",
                    "student_department": "bilgisayar_muhendisligi",
                    "student_faculty": "Muhendislik Fakultesi",
                    "student_type": "domestic",
                    "slack_user_id": "U123",
                    "session_token": session_token,
                    "expires_at": None,
                },
            )()
        return None

    async def invalidate_session(self, session_token: str):
        return session_token == "session-xyz"


class _FakeDepartmentOrchestrator:
    def __init__(self, department: Department):
        self.department = department

    async def handle(self, *, query_text: str, context_id: str, task_type=None, metadata=None):
        return DepartmentResponse(
            department=self.department,
            answer=f"{self.department.value} cevabi: {query_text}",
            sources=[
                RAGSource(
                    content="ornek kaynak",
                    score=0.9,
                    metadata={
                        "context_id": context_id,
                        "task_type": task_type.value if task_type else None,
                        "student_id": (metadata or {}).get("student_id"),
                        "is_authenticated": (metadata or {}).get("is_authenticated"),
                    },
                )
            ],
        )


class _FakeMainOrchestrator:
    def __init__(self):
        self.department_orchestrators = {
            Department.FINANCE: _FakeDepartmentOrchestrator(Department.FINANCE),
            Department.STUDENT_AFFAIRS: _FakeDepartmentOrchestrator(Department.STUDENT_AFFAIRS),
            Department.ACADEMIC_PROGRAMS: _FakeDepartmentOrchestrator(Department.ACADEMIC_PROGRAMS),
        }

    async def handle_query(
        self,
        query: str,
        *,
        context_id: str | None = None,
        user_id: str | None = None,
        student_id: int | None = None,
        student_number: str | None = None,
        student_full_name: str | None = None,
        student_department: str | None = None,
        student_faculty: str | None = None,
        student_type: str | None = None,
        llm_profile: str | None = None,
        is_authenticated: bool = False,
        trace_id: str | None = None,
        span_id: str | None = None,
        parent_span_id: str | None = None,
        disable_cache: bool = False,
    ):
        return UserQueryResponse(
            answer=f"yanit: {query}",
            departments_involved=[Department.STUDENT_AFFAIRS.value],
            sources=[
                RAGSource(
                    content="kaynak",
                    score=0.8,
                    metadata={
                        "context_id": context_id,
                        "user_id": user_id,
                        "student_id": student_id,
                        "student_number": student_number,
                        "student_full_name": student_full_name,
                        "student_department": student_department,
                        "student_faculty": student_faculty,
                        "student_type": student_type,
                        "llm_profile": llm_profile,
                        "is_authenticated": is_authenticated,
                        "trace_id": trace_id,
                        "span_id": span_id,
                        "parent_span_id": parent_span_id,
                        "disable_cache": disable_cache,
                    },
                )
            ],
            response_time_ms=12.5,
            query_id=context_id or "generated-context",
        )


class _FakeProfileContextService:
    def __init__(self):
        self.store = {}

    async def get_context(self, *, context_id: str):
        return self.store.get(context_id)

    async def upsert_profile(
        self,
        *,
        context_id: str,
        user_id: str | None,
        full_name: str,
        student_number: str | None,
        department: str,
        faculty: str,
        student_type: str | None = None,
        is_verified: bool = False,
        student_db_id: int | None = None,
    ):
        data = type(
            "ProfileContext",
            (),
            {
                "context_id": context_id,
                "user_id": user_id,
                "full_name": full_name,
                "student_number": student_number,
                "department": department,
                "faculty": faculty,
                "student_type": student_type,
                "student_db_id": student_db_id,
                "is_verified": is_verified,
                "first_name": (full_name.split() or [full_name])[0],
            },
        )()
        self.store[context_id] = data
        return data


class _FakeTelemetryService:
    async def list_registered_agents(self, *, include_internal: bool = False):
        rows = [
            {
                "agent_id": "student_affairs_orchestrator",
                "name": "Student Affairs Orchestrator",
                "department": "student_affairs",
                "role": "department_orchestrator",
                "description": "Student affairs service",
                "endpoint": "http://agent-student-affairs:8101",
                "is_active": True,
                "last_heartbeat": "2026-04-21T16:00:00+00:00",
                "is_stale": False,
                "capabilities": {
                    "service_build": {"build_id": "codex-build"},
                    "service_runtime_label": "agent-student-affairs",
                },
                "service_build": {"build_id": "codex-build"},
                "service_runtime_label": "agent-student-affairs",
                "is_published_service": True,
            },
            {
                "agent_id": "announcement_agent",
                "name": "Announcement Capability",
                "department": "announcement",
                "role": "capability_agent",
                "description": "Announcement capability service",
                "endpoint": "http://agent-announcement:8104",
                "is_active": True,
                "last_heartbeat": "2026-04-21T15:00:00+00:00",
                "is_stale": True,
                "capabilities": {
                    "service_build": {"build_id": "codex-build"},
                    "service_runtime_label": "agent-announcement",
                },
                "service_build": {"build_id": "codex-build"},
                "service_runtime_label": "agent-announcement",
                "is_published_service": True,
            },
            {
                "agent_id": "registration_agent",
                "name": "Registration Agent",
                "department": "student_affairs",
                "role": "specialist_agent",
                "description": "Internal specialist",
                "endpoint": None,
                "is_active": True,
                "last_heartbeat": "2026-04-20T15:00:00+00:00",
                "is_stale": True,
                "capabilities": {},
                "service_build": None,
                "service_runtime_label": None,
                "is_published_service": False,
            },
        ]
        if include_internal:
            return rows
        return [row for row in rows if row["is_published_service"]]

    async def get_a2a_diagnostics(self, *, window_minutes: int = 60, recent_limit: int = 10):
        return {
            "status": "ok",
            "overview": {
                "generated_at": "2026-04-23T00:00:00+00:00",
                "window_minutes": window_minutes,
                "window_started_at": "2026-04-22T23:00:00+00:00",
                "query_count": 3,
                "query_failure_count": 1,
                "agent_task_count": 4,
                "agent_task_failure_count": 1,
                "avg_response_time_ms": 125.5,
                "max_response_time_ms": 300,
            },
            "agents": [
                {
                    "agent_id": "event_agent",
                    "name": "Event Agent",
                    "department": "event",
                    "role": "capability_agent",
                    "total_tasks": 2,
                    "completed_tasks": 1,
                    "failed_tasks": 1,
                    "failure_rate": 0.5,
                    "latency_sample_count": 2,
                    "avg_latency_ms": 81.2,
                    "max_latency_ms": 120.0,
                    "last_error": "timeout",
                    "last_completed_at": "2026-04-23T00:00:00+00:00",
                }
            ],
            "recent_failures": [
                {
                    "task_id": "task-1",
                    "sender_agent_id": "main_orchestrator",
                    "receiver_agent_id": "event_agent",
                    "status": "failed",
                    "error": "timeout",
                    "completed_at": "2026-04-23T00:00:00+00:00",
                    "trace_id": "trace-1",
                    "query_preview": "Bu hafta etkinlik var mi?",
                }
            ][:recent_limit],
        }


def _override_cards():
    return [
        AgentCardSummary(
            agent_id="registration_agent",
            name="Kayit Ajani",
            department=Department.STUDENT_AFFAIRS.value,
            description="Kayit islemleri icin uzman ajan",
            task_types=[TaskType.REGISTRATION_QUERY.value],
        )
    ]


def setup_function():
    app.dependency_overrides.clear()


def teardown_function():
    app.dependency_overrides.clear()


def test_health_endpoint_returns_llm_status():
    app.dependency_overrides[get_llm_service] = lambda: _FakeLLMService()
    client = TestClient(app)
    previous_build_id = settings.server.build_id
    previous_git_sha = settings.server.git_sha
    settings.server.build_id = "test-build"
    settings.server.git_sha = "abc123"

    try:
        response = client.get("/health")
    finally:
        settings.server.build_id = previous_build_id
        settings.server.git_sha = previous_git_sha

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["llm"]["primary"]["status"] == "healthy"
    assert payload["llm"]["primary"]["name"] == "groq"
    assert payload["app"]["build"]["version"] == settings.server.app_version
    assert payload["app"]["build"]["build_id"] == "test-build"
    assert payload["app"]["build"]["git_sha"] == "abc123"
    assert payload["app"]["a2a_mode"] == settings.a2a.mode
    assert payload["app"]["auth_mode"] == "otp_session"


def test_request_otp_endpoint_returns_masked_email_and_preview_code():
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)

    response = client.post(
        "/auth/request-otp",
        json={"student_number": "20210001", "slack_user_id": "U123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["student_number"] is None
    assert payload["otp_preview_code"] is None
    assert "dogruysa" in normalize_text(payload["message"])


def test_verify_otp_endpoint_returns_session_token():
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)

    response = client.post(
        "/auth/verify-otp",
        json={"student_number": "20210001", "otp_code": "123456", "slack_user_id": "U123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["student_id"] == 42
    assert payload["student_department"] == "bilgisayar_muhendisligi"
    assert payload["student_faculty"] == "Muhendislik Fakultesi"
    assert payload["session_token"] == "session-xyz"


def test_auth_resolve_requires_internal_key_for_slack_only_resolution():
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)
    previous_key = settings.server.internal_api_key
    settings.server.internal_api_key = "test-internal-key"

    try:
        response = client.post(
            "/auth/resolve",
            json={"slack_user_id": "U123"},
        )
    finally:
        settings.server.internal_api_key = previous_key

    assert response.status_code == 403


def test_query_endpoint_resolves_session_token_before_orchestration():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: _FakeProfileContextService()
    client = TestClient(app)

    response = client.post(
        "/query",
        json={
            "query": "Cap basvurusu nasil yapilir?",
            "context_id": "ctx-api-1",
            "session_token": "session-xyz",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "yanit: Cap basvurusu nasil yapilir?"
    assert payload["generation_modes"] == []
    assert payload["sources"][0]["metadata"]["student_id"] == 42
    assert payload["sources"][0]["metadata"]["student_department"] == "bilgisayar_muhendisligi"
    assert payload["sources"][0]["metadata"]["student_faculty"] == "Muhendislik Fakultesi"
    assert payload["sources"][0]["metadata"]["is_authenticated"] is True
    assert payload["sources"][0]["metadata"]["user_id"] == "U123"


def test_query_endpoint_verified_session_uses_verified_student_type_not_payload_override():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: _FakeProfileContextService()
    client = TestClient(app)

    response = client.post(
        "/query",
        json={
            "query": "Cap basvurusu nasil yapilir?",
            "context_id": "ctx-api-verified-type",
            "session_token": "session-xyz",
            "student_type": "uluslararasi ogrenci",
            "is_authenticated": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"][0]["metadata"]["is_authenticated"] is True
    assert payload["sources"][0]["metadata"]["student_type"] == "domestic"


def test_a2a_dispatch_endpoint_routes_to_department_orchestrator_with_auth_resolution():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)
    previous_key = settings.server.internal_api_key
    settings.server.internal_api_key = "test-internal-key"

    try:
        response = client.post(
            "/a2a/dispatch",
            json={
                "department": "finance",
                "query": "Harc dekontu nasil alinir?",
                "context_id": "ctx-a2a-1",
                "task_type": "tuition_query",
                "session_token": "session-xyz",
            },
            headers={"X-Internal-API-Key": "test-internal-key"},
        )
    finally:
        settings.server.internal_api_key = previous_key

    assert response.status_code == 200
    payload = response.json()
    assert payload["department"] == "finance"
    assert "finance cevabi" in payload["answer"]
    assert payload["sources"][0]["metadata"]["student_id"] == 42


def test_a2a_dispatch_endpoint_generates_context_id_when_missing():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)
    previous_key = settings.server.internal_api_key
    settings.server.internal_api_key = "test-internal-key"

    try:
        first = client.post(
            "/a2a/dispatch",
            json={
                "department": "finance",
                "query": "Harc dekontu nasil alinir?",
                "task_type": "tuition_query",
                "session_token": "session-xyz",
            },
            headers={"X-Internal-API-Key": "test-internal-key"},
        )
        second = client.post(
            "/a2a/dispatch",
            json={
                "department": "finance",
                "query": "Harc dekontu nasil alinir?",
                "task_type": "tuition_query",
                "session_token": "session-xyz",
            },
            headers={"X-Internal-API-Key": "test-internal-key"},
        )
    finally:
        settings.server.internal_api_key = previous_key

    assert first.status_code == 200
    assert second.status_code == 200
    first_context_id = first.json()["sources"][0]["metadata"]["context_id"]
    second_context_id = second.json()["sources"][0]["metadata"]["context_id"]
    assert first_context_id != "api-a2a-context"
    assert second_context_id != "api-a2a-context"
    assert first_context_id != second_context_id


def test_a2a_dispatch_endpoint_rejects_requests_without_internal_key():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)
    previous_key = settings.server.internal_api_key
    settings.server.internal_api_key = "test-internal-key"

    try:
        response = client.post(
            "/a2a/dispatch",
            json={
                "department": "finance",
                "query": "Harc dekontu nasil alinir?",
                "context_id": "ctx-a2a-2",
                "task_type": "tuition_query",
                "session_token": "session-xyz",
            },
        )
    finally:
        settings.server.internal_api_key = previous_key

    assert response.status_code == 403


def test_query_endpoint_requests_profile_before_answering():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: _FakeProfileContextService()
    client = TestClient(app)

    response = client.post(
        "/query",
        json={
            "query": "Merhaba",
            "context_id": "ctx-profile-1",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "ad soyad" in payload["answer"].lower()
    assert payload["departments_involved"] == []


def test_query_endpoint_saves_profile_and_personalizes_answer():
    profile_service = _FakeProfileContextService()
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: profile_service
    client = TestClient(app)

    save_response = client.post(
        "/query",
        json={
            "query": "Ad Soyad: Ahmet Yilmaz\nOgrenci Numarasi: 20210001\nBolum: Bilgisayar Muhendisligi\nFakulte: Muhendislik Fakultesi",
            "context_id": "ctx-profile-2",
        },
    )
    assert save_response.status_code == 200
    assert "Bilgisayar Muhendisligi" in save_response.json()["answer"]

    response = client.post(
        "/query",
        json={
            "query": "Mufredat hakkinda bilgi ver",
            "context_id": "ctx-profile-2",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"][0]["metadata"]["student_full_name"] == "Ahmet Yilmaz"
    assert payload["sources"][0]["metadata"]["student_department"] == "Bilgisayar Muhendisligi"


def test_query_endpoint_does_not_trust_client_authenticated_flags_without_session():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: _FakeProfileContextService()
    client = TestClient(app)

    response = client.post(
        "/query",
        json={
            "query": "Not ortalamam kac?",
            "context_id": "ctx-auth-spoof",
            "full_name": "Test Ogrenci",
            "student_number": "22060388",
            "student_department": "Bilgisayar Muhendisligi",
            "student_faculty": "Muhendislik Fakultesi",
            "student_id": 999,
            "is_authenticated": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"][0]["metadata"]["student_id"] is None
    assert payload["sources"][0]["metadata"]["is_authenticated"] is False


def test_query_endpoint_forwards_disable_cache_to_orchestrator():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: _FakeProfileContextService()
    client = TestClient(app)

    response = client.post(
        "/query",
        json={
            "query": "Ders kaydi ne zaman basliyor?",
            "context_id": "ctx-disable-cache",
            "full_name": "Test Ogrenci",
            "student_number": "22060388",
            "student_department": "Bilgisayar Muhendisligi",
            "student_faculty": "Muhendislik Fakultesi",
            "disable_cache": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"][0]["metadata"]["disable_cache"] is True


def test_query_endpoint_attaches_local_profile_diagnostics():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: _FakeProfileContextService()
    client = TestClient(app)

    response = client.post(
        "/query",
        json={
            "query": "Ders kaydi nasil yapilir?",
            "context_id": "ctx-local-profile",
            "full_name": "Test Ogrenci",
            "student_number": "22060388",
            "student_department": "Bilgisayar Muhendisligi",
            "student_faculty": "Muhendislik Fakultesi",
        },
    )

    assert response.status_code == 200
    diagnostics = response.json()["diagnostics"]
    assert diagnostics["local_profile"]["label"] == "api.query:ctx-local-profile"
    assert any(
        event["name"] == "api.query"
        for event in diagnostics["local_profile"]["events"]
    )


def test_agents_endpoint_lists_active_agent_cards():
    app.dependency_overrides[get_agent_card_summaries] = _override_cards
    client = TestClient(app)

    response = client.get("/agents")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["agent_id"] == "registration_agent"


def test_main_agent_card_endpoint_exposes_a2a_discovery():
    client = TestClient(app)

    response = client.get("/.well-known/agent.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "OMU Main Orchestrator"
    assert payload["url"].endswith("/a2a")
    assert payload["capabilities"]["stateTransitionHistory"] is True
    assert payload["skills"][0]["id"] == "university_support_query"
    assert "announcement" in payload["skills"][0]["tags"]


def test_main_a2a_jsonrpc_message_send_handles_user_query():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: _FakeProfileContextService()
    client = TestClient(app)
    previous_key = settings.server.internal_api_key
    settings.server.internal_api_key = "test-internal-key"
    message = build_text_message(
        "Ders kaydi nasil yapilir?",
        context_id="ctx-main-a2a",
        role=Role.user,
        metadata={
            "full_name": "Test Ogrenci",
            "student_number": "22000001",
            "student_department": "Bilgisayar Muhendisligi",
            "student_faculty": "Muhendislik Fakultesi",
            "student_type": "Turk ogrenci",
            "llm_profile": "fast",
            "trace_id": "trace-main-a2a-test",
            "span_id": "span-main-a2a-test",
        },
    )

    try:
        response = client.post(
            "/a2a",
            json={
                "jsonrpc": "2.0",
                "id": "main-a2a-req-1",
                "method": "message/send",
                "params": {
                    "message": message.model_dump(mode="json", exclude_none=True),
                },
            },
            headers={"X-Internal-API-Key": "test-internal-key"},
        )
    finally:
        settings.server.internal_api_key = previous_key

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "main-a2a-req-1"
    assert payload["result"]["status"]["state"] == "completed"
    assert payload["result"]["metadata"]["trace_id"] == "trace-main-a2a-test"
    assert payload["result"]["metadata"]["span_id"] == "span-main-a2a-test"
    assert [item["state"] for item in payload["result"]["metadata"]["state_transitions"]] == [
        "submitted",
        "working",
        "completed",
    ]
    assert payload["result"]["metadata"]["state_transitions"][-1]["actor_id"] == "main_orchestrator"
    artifacts = payload["result"]["artifacts"]
    data_artifact = next(
        artifact
        for artifact in artifacts
        if artifact["metadata"]["schema"] == "omu.user_query_response.v1"
    )
    data = data_artifact["parts"][0]["data"]
    assert data["answer"] == "yanit: Ders kaydi nasil yapilir?"
    assert data["query_id"] == "ctx-main-a2a"
    assert data["sources"][0]["metadata"]["student_department"] == "Bilgisayar Muhendisligi"
    assert data["sources"][0]["metadata"]["llm_profile"] == "fast"


def test_main_a2a_jsonrpc_rejects_requests_without_internal_key():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    app.dependency_overrides[get_profile_context_service] = lambda: _FakeProfileContextService()
    client = TestClient(app)
    previous_key = settings.server.internal_api_key
    settings.server.internal_api_key = "test-internal-key"
    message = build_text_message(
        "Ders kaydi nasil yapilir?",
        context_id="ctx-main-a2a-forbidden",
        role=Role.user,
    )

    try:
        response = client.post(
            "/a2a",
            json={
                "jsonrpc": "2.0",
                "id": "main-a2a-req-forbidden",
                "method": "message/send",
                "params": {
                    "message": message.model_dump(mode="json", exclude_none=True),
                },
            },
        )
    finally:
        settings.server.internal_api_key = previous_key

    assert response.status_code == 403


def test_a2a_topology_endpoint_lists_registry_agents():
    app.dependency_overrides[get_telemetry_service] = lambda: _FakeTelemetryService()
    client = TestClient(app)

    response = client.get("/a2a/topology")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["include_internal"] is False
    assert payload["agent_count"] == 3
    assert payload["active_count"] == 3
    assert payload["stale_count"] == 1
    assert payload["agents"][0]["agent_id"] == "main_orchestrator"
    assert payload["agents"][0]["is_published_service"] is True
    assert payload["agents"][0]["capabilities"]["response_schema"] == "omu.user_query_response.v1"
    assert payload["agents"][1]["agent_id"] == "student_affairs_orchestrator"
    assert payload["agents"][1]["service_runtime_label"] == "agent-student-affairs"
    assert payload["agents"][2]["agent_id"] == "announcement_agent"
    assert payload["agents"][2]["is_stale"] is True


def test_a2a_topology_endpoint_can_include_internal_registry_agents():
    app.dependency_overrides[get_telemetry_service] = lambda: _FakeTelemetryService()
    client = TestClient(app)

    response = client.get("/a2a/topology?include_internal=true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["include_internal"] is True
    assert payload["agent_count"] == 4
    assert payload["stale_count"] == 2
    assert payload["agents"][3]["agent_id"] == "registration_agent"
    assert payload["agents"][3]["is_published_service"] is False


def test_a2a_diagnostics_endpoint_returns_recent_agent_health():
    app.dependency_overrides[get_telemetry_service] = lambda: _FakeTelemetryService()
    client = TestClient(app)

    response = client.get("/a2a/diagnostics?window_minutes=30&recent_limit=1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["overview"]["window_minutes"] == 30
    assert payload["overview"]["agent_task_failure_count"] == 1
    assert payload["agents"][0]["agent_id"] == "event_agent"
    assert payload["agents"][0]["failure_rate"] == 0.5
    assert payload["recent_failures"][0]["trace_id"] == "trace-1"


def test_logout_endpoint_invalidates_session():
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)

    response = client.post("/auth/logout", json={"session_token": "session-xyz"})

    assert response.status_code == 200
    assert response.json()["success"] is True
