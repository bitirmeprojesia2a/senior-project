"""Standalone A2A agent service tests."""

from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

from a2a.types import Role
from fastapi.testclient import TestClient

from src.a2a import A2AQueryPayload, build_department_response_task, build_query_task, build_text_message
from src.a2a.service_identity import sign_a2a_request
from src.api.agent_service import (
    SpecialistTarget,
    build_agent_card_payload,
    build_standard_agent_card,
    create_agent_service_app,
    resolve_agent_department,
    resolve_agent_target,
)
from src.a2a.targets import agent_target_kind, resolve_agent_service_target
from src.core.config import settings
from src.core.constants import Capability, Department
from src.db.schemas import DepartmentResponse


class _FakeAgent:
    agent_id = "fake_registration_agent"
    definition = SimpleNamespace(
        name="Fake Registration Agent",
        description="Kayit test ajani",
        task_types=[],
    )


class _FakeCapabilityAgent:
    agent_id = "fake_capability_agent"
    definition = SimpleNamespace(
        name="Fake Capability Agent",
        description="Capability test ajani",
        task_types=[],
    )

    def __init__(self, response: DepartmentResponse):
        self._response = response
        self.handle_task = AsyncMock(side_effect=self._handle_task)

    async def _handle_task(self, task):
        request_task = build_query_task(
            A2AQueryPayload(
                query_text=str(task.metadata.get("query_text") or ""),
                context_id=task.contextId or "ctx-capability",
            )
        )
        return build_department_response_task(
            self._response,
            request_task=request_task,
            emitter_id=self.agent_id,
            emitter_name=self.definition.name,
        )


class _FakeSpecialistAgent:
    agent_id = "tuition_agent"
    department = Department.FINANCE
    definition = SimpleNamespace(
        name="Tuition Agent",
        description="Harc test ajani",
        task_types=[],
    )

    def __init__(self, response: DepartmentResponse):
        self._response = response
        self.handle_task = AsyncMock(side_effect=self._handle_task)

    async def _handle_task(self, task):
        return build_department_response_task(
            self._response,
            request_task=task,
            emitter_id=self.agent_id,
            emitter_name=self.definition.name,
        )


def test_resolve_agent_department_reads_setting(monkeypatch):
    monkeypatch.setattr(settings.agent, "department", "finance")

    assert resolve_agent_department() == Department.FINANCE


def test_resolve_agent_target_reads_capability_setting(monkeypatch):
    monkeypatch.setattr(settings.agent, "department", "announcement")

    assert resolve_agent_target() == Capability.ANNOUNCEMENT


def test_resolve_agent_target_reads_specialist_setting(monkeypatch):
    monkeypatch.setattr(settings.agent, "department", "finance")
    monkeypatch.setattr(settings.agent, "specialist_id", "tuition_agent")

    target = resolve_agent_target()

    assert isinstance(target, SpecialistTarget)
    assert target.department == Department.FINANCE
    assert target.agent_id == "tuition_agent"


def test_agent_service_target_resolver_is_independent_from_api_settings():
    target = resolve_agent_service_target(
        raw_target="academic_programs",
        specialist_id="international_agent",
    )

    assert isinstance(target, SpecialistTarget)
    assert target.department == Department.ACADEMIC_PROGRAMS
    assert target.value == "international_agent"
    assert agent_target_kind(target) == "specialist"


def test_specialist_agent_card_names_do_not_duplicate_agent_suffix(monkeypatch):
    monkeypatch.setattr(settings.agent, "service_id", "agent-finance-tuition")
    monkeypatch.setattr(settings.agent, "public_url", "http://agent-finance-tuition:8110")
    handler = _FakeSpecialistAgent(
        DepartmentResponse(
            department=Department.FINANCE,
            answer="ok",
            sources=[],
            generation_mode="vt",
        )
    )
    target = SpecialistTarget(
        department=Department.FINANCE,
        agent_id="tuition_agent",
    )

    standard_card = build_standard_agent_card(target=target, service_handler=handler)
    lightweight_card = build_agent_card_payload(target=target, service_handler=handler)

    assert standard_card.name == "OMU Tuition Agent"
    assert lightweight_card["name"] == "OMU Tuition Agent Service"


def test_agent_service_health_and_card():
    previous_build_id = settings.server.build_id
    previous_runtime_label = settings.server.runtime_label
    settings.server.build_id = "agent-build"
    settings.server.runtime_label = "agent-test"
    orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={"fake_registration_agent": _FakeAgent()},
    )
    try:
        app = create_agent_service_app(
            department=Department.STUDENT_AFFAIRS,
            orchestrator=orchestrator,
        )
        client = TestClient(app)

        health = client.get("/health")
        card = client.get("/agent-card")
    finally:
        settings.server.build_id = previous_build_id
        settings.server.runtime_label = previous_runtime_label

    assert health.status_code == 200
    assert health.json()["department"] == "student_affairs"
    assert health.json()["build"]["version"] == settings.server.app_version
    assert health.json()["build"]["build_id"] == "agent-build"
    assert health.json()["runtime"]["label"] == "agent-test"
    assert card.status_code == 200
    assert card.json()["department"] == "student_affairs"
    assert card.json()["version"] == settings.server.app_version
    assert card.json()["build"]["build_id"] == "agent-build"
    assert card.json()["agents"][0]["agent_id"] == "fake_registration_agent"


def test_agent_service_exposes_standard_well_known_agent_card(monkeypatch):
    monkeypatch.setattr(settings.agent, "public_url", "http://localhost:8101")
    orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={"fake_registration_agent": _FakeAgent()},
    )
    app = create_agent_service_app(
        department=Department.STUDENT_AFFAIRS,
        orchestrator=orchestrator,
        telemetry_service=SimpleNamespace(ensure_agent=AsyncMock()),
    )
    client = TestClient(app)

    response = client.get("/.well-known/agent.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "OMU Öğrenci İşleri Agent"
    assert payload["url"] == "http://localhost:8101/a2a"
    assert payload["capabilities"]["streaming"] is False
    assert payload["skills"][0]["id"] == "fake_registration_agent"


def test_agent_service_registers_department_endpoint_on_startup(monkeypatch):
    monkeypatch.setattr(settings.agent, "public_url", "http://localhost:8102")
    monkeypatch.setattr(settings.server, "build_id", "registry-build")
    monkeypatch.setattr(settings.server, "runtime_label", "agent-student-affairs")
    telemetry_service = SimpleNamespace(ensure_agent=AsyncMock())
    orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={"fake_registration_agent": _FakeAgent()},
    )
    app = create_agent_service_app(
        department=Department.STUDENT_AFFAIRS,
        orchestrator=orchestrator,
        telemetry_service=telemetry_service,
    )

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert telemetry_service.ensure_agent.await_count == 2
    identity = telemetry_service.ensure_agent.await_args.args[0]
    assert identity.agent_id == "student_affairs_orchestrator"
    assert identity.endpoint == "http://localhost:8102"
    assert identity.capabilities["a2a_dispatch"] is True
    assert identity.capabilities["agent_response_schema"] == "omu.agent_response.v1"
    assert identity.capabilities["department_response_schema"] == "omu.department_response.v1"
    assert identity.capabilities["service_build"]["build_id"] == "registry-build"
    assert identity.capabilities["service_runtime_label"] == "agent-student-affairs"


def test_agent_service_agent_card_refreshes_registry_presence(monkeypatch):
    monkeypatch.setattr(settings.agent, "public_url", "http://localhost:8102")
    telemetry_service = SimpleNamespace(ensure_agent=AsyncMock())
    orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={"fake_registration_agent": _FakeAgent()},
    )
    app = create_agent_service_app(
        department=Department.STUDENT_AFFAIRS,
        orchestrator=orchestrator,
        telemetry_service=telemetry_service,
    )

    with TestClient(app) as client:
        response = client.get("/agent-card")

    assert response.status_code == 200
    assert telemetry_service.ensure_agent.await_count == 2


def test_agent_service_dispatch_rejects_wrong_department(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={},
        handle=AsyncMock(),
    )
    app = create_agent_service_app(
        department=Department.FINANCE,
        orchestrator=orchestrator,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "department": "student_affairs",
            "query": "Ders kaydi nasil yapilir?",
            "context_id": "ctx-agent-service-wrong",
        },
    )

    assert response.status_code == 404
    orchestrator.handle.assert_not_awaited()


def test_agent_service_dispatch_returns_department_response(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="Finans cevabi",
        sources=[],
        generation_mode="vt",
    )
    orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={},
        handle=AsyncMock(return_value=expected),
    )
    app = create_agent_service_app(
        department=Department.FINANCE,
        orchestrator=orchestrator,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "department": "finance",
            "query": "Harc odemesi nasil yapilir?",
            "context_id": "ctx-agent-service-ok",
            "task_type": "tuition_query",
            "student_department": "Bilgisayar Muhendisligi",
        },
    )

    assert response.status_code == 200
    assert response.json()["department"] == "finance"
    assert response.json()["answer"] == "Finans cevabi"
    assert client.get("/metrics").json()["request_count"] == 1
    orchestrator.handle.assert_awaited_once()


def test_agent_service_can_require_a2a_caller_identity(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(settings.agent, "service_id", "agent-finance")
    monkeypatch.setattr(settings.a2a, "require_service_identity", True)
    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="Finans cevabi",
        sources=[],
        generation_mode="vt",
    )
    orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={},
        handle=AsyncMock(return_value=expected),
    )
    app = create_agent_service_app(
        department=Department.FINANCE,
        orchestrator=orchestrator,
    )
    client = TestClient(app)
    body = {
        "department": "finance",
        "query": "Harc odemesi nasil yapilir?",
        "context_id": "ctx-agent-service-identity",
    }

    missing_caller = client.post(
        "/a2a/dispatch",
        headers={
            "X-Internal-API-Key": "test-key",
            "X-A2A-Target-ID": "agent-finance",
        },
        json=body,
    )
    accepted = client.post(
        "/a2a/dispatch",
        headers={
            "X-Internal-API-Key": "test-key",
            "X-A2A-Caller-ID": "main_orchestrator",
            "X-A2A-Target-ID": "agent-finance",
        },
        json=body,
    )

    assert missing_caller.status_code == 403
    assert accepted.status_code == 200
    assert orchestrator.handle.await_count == 1


def test_agent_service_can_require_signed_a2a_request(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(settings.agent, "service_id", "agent-finance")
    monkeypatch.setattr(settings.a2a, "require_request_signature", True)
    monkeypatch.setattr(settings.a2a, "request_signature_secret", "signing-secret")
    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="Finans cevabi",
        sources=[],
        generation_mode="vt",
    )
    orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={},
        handle=AsyncMock(return_value=expected),
    )
    app = create_agent_service_app(
        department=Department.FINANCE,
        orchestrator=orchestrator,
    )
    client = TestClient(app)
    body = {
        "department": "finance",
        "query": "Harc odemesi nasil yapilir?",
        "context_id": "ctx-agent-service-signature",
        "user_id": None,
        "full_name": None,
        "student_number": None,
        "student_id": None,
        "student_department": None,
        "student_faculty": None,
        "student_type": None,
        "llm_profile": None,
        "is_authenticated": False,
        "session_token": None,
        "slack_user_id": None,
        "task_type": None,
        "original_query": None,
        "resolved_query": None,
        "conversation_is_follow_up": False,
        "conversation_topic": None,
        "conversation_source_refs": [],
        "force_llm_synthesis": False,
        "query_complexity": None,
        "is_personal_query": False,
        "disable_specialist_llm": False,
        "trace_id": None,
        "span_id": None,
        "parent_span_id": None,
    }
    signature_headers = sign_a2a_request(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp=str(int(time.time())),
        nonce="nonce-1",
    )
    headers = {
        "X-Internal-API-Key": "test-key",
        "X-A2A-Caller-ID": "main_orchestrator",
        "X-A2A-Target-ID": "agent-finance",
        **signature_headers,
    }

    missing_signature = client.post(
        "/a2a/dispatch",
        headers={
            "X-Internal-API-Key": "test-key",
            "X-A2A-Caller-ID": "main_orchestrator",
            "X-A2A-Target-ID": "agent-finance",
        },
        json=body,
    )
    accepted = client.post(
        "/a2a/dispatch",
        headers=headers,
        json=body,
    )
    tampered = client.post(
        "/a2a/dispatch",
        headers=headers,
        json={**body, "query": "Degistirilmis soru"},
    )

    assert missing_signature.status_code == 403
    assert accepted.status_code == 200
    assert tampered.status_code == 403
    assert orchestrator.handle.await_count == 1


def test_agent_service_rejects_a2a_target_identity_mismatch(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(settings.agent, "service_id", "agent-finance")
    orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={},
        handle=AsyncMock(),
    )
    app = create_agent_service_app(
        department=Department.FINANCE,
        orchestrator=orchestrator,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        headers={
            "X-Internal-API-Key": "test-key",
            "X-A2A-Caller-ID": "main_orchestrator",
            "X-A2A-Target-ID": "agent-student-affairs",
        },
        json={
            "department": "finance",
            "query": "Harc odemesi nasil yapilir?",
            "context_id": "ctx-agent-service-target-mismatch",
        },
    )

    assert response.status_code == 403
    orchestrator.handle.assert_not_awaited()


def test_agent_service_jsonrpc_message_send_returns_a2a_task(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="Finans JSON-RPC cevabi",
        sources=[],
        generation_mode="vt",
    )
    orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={},
        handle=AsyncMock(return_value=expected),
    )
    app = create_agent_service_app(
        department=Department.FINANCE,
        orchestrator=orchestrator,
    )
    client = TestClient(app)
    message = build_text_message(
        "Harc odemesi nasil yapilir?",
        context_id="ctx-jsonrpc-service-ok",
        role=Role.user,
        metadata={
            "task_type": "tuition_query",
            "student_department": "Bilgisayar Muhendisligi",
            "final_answer_owner": "main_orchestrator",
            "specialist_response_mode": "evidence_packet",
            "capability_planner": {"action": {"capability": "finance.tuition_fee"}},
            "source_owner": {"primary": "tuition_fee_catalog"},
            "decision_contract": {"contract": {"source_owner": {"primary": "tuition_fee_catalog"}}},
            "branch_dispatch_gate": {"restored_primary_department": "finance"},
        },
    )

    response = client.post(
        "/a2a",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "jsonrpc": "2.0",
            "id": "req-1",
            "method": "message/send",
            "params": {
                "message": message.model_dump(mode="json", exclude_none=True),
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == "req-1"
    assert payload["result"]["status"]["state"] == "completed"
    assert payload["result"]["metadata"]["response_schema"] == "omu.agent_response.v1"
    assert payload["result"]["metadata"]["legacy_response_schema"] == "omu.department_response.v1"
    assert payload["result"]["artifacts"][1]["metadata"]["schema"] == "omu.agent_response.v1"
    assert "omu.department_response.v1" in payload["result"]["artifacts"][1]["extensions"]
    assert payload["result"]["artifacts"][1]["parts"][0]["data"]["answer"] == "Finans JSON-RPC cevabi"
    orchestrator.handle.assert_awaited_once()
    metadata = orchestrator.handle.await_args.kwargs["metadata"]
    assert metadata["final_answer_owner"] == "main_orchestrator"
    assert metadata["specialist_response_mode"] == "evidence_packet"
    assert metadata["capability_planner"]["action"]["capability"] == "finance.tuition_fee"
    assert metadata["source_owner"]["primary"] == "tuition_fee_catalog"
    assert metadata["decision_contract"]["contract"]["source_owner"]["primary"] == "tuition_fee_catalog"
    assert metadata["branch_dispatch_gate"]["restored_primary_department"] == "finance"


def test_agent_service_jsonrpc_rejects_unsupported_method(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={},
        handle=AsyncMock(),
    )
    app = create_agent_service_app(
        department=Department.FINANCE,
        orchestrator=orchestrator,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "jsonrpc": "2.0",
            "id": "req-unsupported",
            "method": "tasks/get",
            "params": {},
        },
    )

    assert response.status_code == 200
    assert response.json()["error"]["code"] == -32601
    orchestrator.handle.assert_not_awaited()


def test_agent_service_dispatch_trusts_internal_authenticated_identity(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="Finans cevabi",
        sources=[],
        generation_mode="vt",
    )
    orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        agents={},
        fallback_agent=_FakeAgent(),
        agents_by_id={},
        handle=AsyncMock(return_value=expected),
    )
    app = create_agent_service_app(
        department=Department.FINANCE,
        orchestrator=orchestrator,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "department": "finance",
            "query": "Harc borcum ne kadar?",
            "context_id": "ctx-agent-service-auth",
            "task_type": "tuition_query",
            "student_id": 10,
            "student_number": "22060388",
            "full_name": "Test Ogrenci",
            "student_department": "Bilgisayar Muhendisligi",
            "student_faculty": "Muhendislik Fakultesi",
            "is_authenticated": True,
        },
    )

    assert response.status_code == 200
    orchestrator.handle.assert_awaited_once()
    metadata = orchestrator.handle.await_args.kwargs["metadata"]
    assert metadata["student_id"] == 10
    assert metadata["student_number"] == "22060388"
    assert metadata["is_authenticated"] is True


def test_capability_agent_service_dispatch_returns_department_response(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    capability_agent = _FakeCapabilityAgent(
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Duyuru capability cevabi",
            sources=[],
            generation_mode="vt",
        )
    )
    app = create_agent_service_app(
        target=Capability.ANNOUNCEMENT,
        service_handler=capability_agent,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "capability": "announcement",
            "query": "Guncel duyurular neler?",
            "context_id": "ctx-announcement-service",
            "allow_latest_fallback": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["department"] == "student_affairs"
    assert response.json()["answer"] == "Duyuru capability cevabi"
    assert client.get("/health").json()["capability"] == "announcement"
    capability_agent.handle_task.assert_awaited_once()


def test_event_capability_agent_service_rejects_wrong_capability(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    capability_agent = _FakeCapabilityAgent(
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Etkinlik capability cevabi",
            sources=[],
            generation_mode="vt",
        )
    )
    app = create_agent_service_app(
        target=Capability.EVENT,
        service_handler=capability_agent,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "capability": "announcement",
            "query": "Bu hafta etkinlik var mi?",
            "context_id": "ctx-event-service-wrong",
        },
    )

    assert response.status_code == 404
    capability_agent.handle_task.assert_not_awaited()


def test_specialist_agent_service_dispatch_returns_department_response(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    specialist_agent = _FakeSpecialistAgent(
        DepartmentResponse(
            department=Department.FINANCE,
            answer="Uzman harc cevabi",
            sources=[],
            generation_mode="vt",
        )
    )
    app = create_agent_service_app(
        target=SpecialistTarget(
            department=Department.FINANCE,
            agent_id="tuition_agent",
        ),
        service_handler=specialist_agent,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "department": "finance",
            "agent_id": "tuition_agent",
            "query": "Harc ucreti ne kadar?",
            "context_id": "ctx-specialist-service",
            "task_type": "tuition_query",
            "student_faculty": "Muhendislik Fakultesi",
            "student_type": "Turk",
        },
    )

    assert response.status_code == 200
    assert response.json()["department"] == "finance"
    assert response.json()["answer"] == "Uzman harc cevabi"
    assert client.get("/health").json()["specialist_id"] == "tuition_agent"
    assert client.get("/agent-card").json()["specialist_id"] == "tuition_agent"
    specialist_agent.handle_task.assert_awaited_once()
    task = specialist_agent.handle_task.await_args.args[0]
    assert task.metadata["student_faculty"] == "Muhendislik Fakultesi"
    assert task.metadata["student_type"] == "Turk"


def test_specialist_agent_service_rejects_wrong_agent(monkeypatch):
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    specialist_agent = _FakeSpecialistAgent(
        DepartmentResponse(
            department=Department.FINANCE,
            answer="Uzman harc cevabi",
            sources=[],
            generation_mode="vt",
        )
    )
    app = create_agent_service_app(
        target=SpecialistTarget(
            department=Department.FINANCE,
            agent_id="tuition_agent",
        ),
        service_handler=specialist_agent,
    )
    client = TestClient(app)

    response = client.post(
        "/a2a/dispatch",
        headers={"X-Internal-API-Key": "test-key"},
        json={
            "department": "finance",
            "agent_id": "scholarship_agent",
            "query": "Burs basvurusu ne zaman?",
            "context_id": "ctx-specialist-service-wrong",
        },
    )

    assert response.status_code == 404
    specialist_agent.handle_task.assert_not_awaited()
