"""FastAPI giris noktasi testleri."""

from fastapi.testclient import TestClient

from src.api.main import (
    AgentCardSummary,
    app,
    get_agent_card_summaries,
    get_auth_service,
    get_llm_service,
    get_main_orchestrator,
)
from src.core.constants import Department, TaskType
from src.db.schemas import DepartmentResponse, RAGSource, UserQueryResponse


class _FakeLLMService:
    async def get_health(self):
        return {
            "status": "healthy",
            "primary": {"name": "ollama", "status": "healthy", "model_loaded": True},
            "fallback": {"name": "openai", "available": False},
        }


class _FakeAuthService:
    async def request_otp(self, *, student_number: str, slack_user_id: str | None = None):
        if student_number != "20210001":
            return None
        return {
            "student_number": "20210001",
            "masked_email": "ah*****@uni.edu.tr",
            "expires_at": __import__("datetime").datetime(2026, 3, 26, 12, 0, 0),
            "delivery_channel": "email_stub",
            "otp_preview_code": "123456",
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
        is_authenticated: bool = False,
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
                        "is_authenticated": is_authenticated,
                    },
                )
            ],
            response_time_ms=12.5,
            query_id=context_id or "generated-context",
        )


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

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["llm"]["primary"]["status"] == "healthy"
    assert payload["app"]["a2a_mode"] == "internal"
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
    assert payload["student_number"] == "20210001"
    assert payload["otp_preview_code"] == "123456"


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
    assert payload["session_token"] == "session-xyz"


def test_query_endpoint_resolves_session_token_before_orchestration():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
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
    assert payload["sources"][0]["metadata"]["student_id"] == 42
    assert payload["sources"][0]["metadata"]["is_authenticated"] is True
    assert payload["sources"][0]["metadata"]["user_id"] == "U123"


def test_a2a_dispatch_endpoint_routes_to_department_orchestrator_with_auth_resolution():
    app.dependency_overrides[get_main_orchestrator] = lambda: _FakeMainOrchestrator()
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        json={
            "department": "finance",
            "query": "Harc dekontu nasil alinir?",
            "context_id": "ctx-a2a-1",
            "task_type": "tuition_query",
            "session_token": "session-xyz",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["department"] == "finance"
    assert "finance cevabi" in payload["answer"]
    assert payload["sources"][0]["metadata"]["student_id"] == 42


def test_agents_endpoint_lists_active_agent_cards():
    app.dependency_overrides[get_agent_card_summaries] = _override_cards
    client = TestClient(app)

    response = client.get("/agents")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["agent_id"] == "registration_agent"


def test_logout_endpoint_invalidates_session():
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService()
    client = TestClient(app)

    response = client.post("/auth/logout", json={"session_token": "session-xyz"})

    assert response.status_code == 200
    assert response.json()["success"] is True
