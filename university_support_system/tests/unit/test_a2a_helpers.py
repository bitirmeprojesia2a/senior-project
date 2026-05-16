"""A2A helper testleri."""

from a2a.types import Role, TaskState
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.a2a import (
    A2AQueryPayload,
    AgentResponse,
    agent_response_to_department_response,
    build_agent_card,
    build_agent_response_task,
    build_department_response_task,
    build_query_task,
    build_text_message,
    extract_agent_response,
    extract_department_response,
)
from src.a2a.transport import HttpA2ADepartmentTransport, ShadowDepartmentTransport
from src.a2a.capability_transport import HttpA2ACapabilityTransport
from src.a2a.specialist_transport import HttpA2ASpecialistTransport
from src.api.a2a_dispatch import CapabilityDispatchRequest
from src.core.constants import Capability, Department
from src.core.constants import TaskType
from src.db.schemas import DepartmentResponse
from src.orchestrators.task_builders import build_department_request_task


class _FakeSpecialistAgent:
    agent_id = "tuition_agent"
    department = Department.FINANCE
    definition = SimpleNamespace(
        name="Tuition Agent",
        description="Harc test ajani",
        task_types=[TaskType.TUITION_QUERY],
    )

    def __init__(self, answer: str = "Local specialist cevabi"):
        self.answer = answer
        self.handle_task = AsyncMock(side_effect=self._handle_task)

    async def _handle_task(self, task):
        return build_department_response_task(
            DepartmentResponse(
                department=Department.FINANCE,
                answer=self.answer,
                sources=[],
            ),
            request_task=task,
            emitter_id=self.agent_id,
            emitter_name=self.definition.name,
        )


@pytest.fixture(autouse=True)
def _reset_http_transport_circuit_state():
    HttpA2ADepartmentTransport.reset_runtime_state()
    HttpA2ASpecialistTransport.reset_circuit_state()
    yield
    HttpA2ADepartmentTransport.reset_runtime_state()
    HttpA2ASpecialistTransport.reset_circuit_state()


def test_agent_response_to_department_response_preserves_transport_diagnostics():
    response = AgentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Registration Agent agent servisine su anda ulasilamadi.",
        success=False,
        error="a2a_specialist_transport_timeout",
        metadata={
            "transport_error": "a2a_specialist_transport_timeout",
            "detail": "ReadTimeout",
            "endpoint": "http://student-registration-agent:8000/a2a",
            "attempt": 2,
            "timeout_seconds": 30,
            "http_status": 504,
            "ignored_internal_key": "not-for-legacy",
        },
    )

    mapped = agent_response_to_department_response(response)

    assert mapped is not None
    assert mapped.metadata["transport_error"] == "a2a_specialist_transport_timeout"
    assert mapped.metadata["endpoint"] == "http://student-registration-agent:8000/a2a"
    assert mapped.metadata["attempt"] == 2
    assert mapped.metadata["timeout_seconds"] == 30
    assert mapped.metadata["http_status"] == 504
    assert "ignored_internal_key" not in mapped.metadata


def test_agent_response_to_department_response_preserves_architectural_trace_metadata():
    response = AgentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="CAP icin en az 3,00 gerekir.",
        metadata={
            "source_owner": {"primary": "student_affairs_policy"},
            "decision_contract": {
                "schema": "omu.decision_contract.v1",
                "contract": {"source_owner": {"primary": "student_affairs_policy"}},
            },
            "resolved_decision": {
                "schema": "omu.resolved_decision.v1",
                "source_owner": "student_affairs_policy",
                "contract": {"id": "cap_eligibility"},
            },
            "branch_dispatch_gate": {"restored_primary_department": "student_affairs"},
            "specialist_selection": {"selected_agent_id": "registration_agent"},
            "capability_planner": {"action": {"capability": "student_affairs.policy_lookup"}},
            "final_answer_owner": "main_orchestrator",
            "specialist_response_mode": "evidence_packet",
            "evidence_packet": {
                "value_arbitration": {
                    "answer_threshold": ["3,00"],
                    "secondary_program_threshold": ["2,00"],
                }
            },
            "answer_validation": {"status": "pass"},
            "answer_coverage": {"status": "pass"},
            "answer_value_conflict": {"status": "pass", "primary_value": "3,00"},
            "llm_usage": [{"role": "routing", "key_fingerprint": "fp-test"}],
            "internal_scratchpad": "drop-me",
        },
    )

    mapped = agent_response_to_department_response(response)

    assert mapped is not None
    assert mapped.metadata["source_owner"]["primary"] == "student_affairs_policy"
    assert mapped.metadata["decision_contract"]["contract"]["source_owner"]["primary"] == "student_affairs_policy"
    assert mapped.metadata["resolved_decision"]["source_owner"] == "student_affairs_policy"
    assert mapped.metadata["branch_dispatch_gate"]["restored_primary_department"] == "student_affairs"
    assert mapped.metadata["specialist_selection"]["selected_agent_id"] == "registration_agent"
    assert mapped.metadata["evidence_packet"]["value_arbitration"]["answer_threshold"] == ["3,00"]
    assert mapped.metadata["answer_value_conflict"]["primary_value"] == "3,00"
    assert mapped.metadata["llm_usage"][0]["role"] == "routing"
    assert "internal_scratchpad" not in mapped.metadata


def test_agent_response_task_roundtrip_preserves_evidence_contract_metadata():
    request_task = build_query_task(
        A2AQueryPayload(
            query_text="Peki not ortalamasi kac olmali?",
            context_id="ctx-a2a-parity",
            source_owner={"primary": "student_affairs_policy"},
            decision_contract={"contract": {"source_owner": {"primary": "student_affairs_policy"}}},
            resolved_decision={"schema": "omu.resolved_decision.v1", "source_owner": "student_affairs_policy"},
            branch_dispatch_gate={"kept_departments": ["student_affairs", "academic_programs"]},
            specialist_selection={"selected_agent_id": "registration_agent"},
        )
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="CAP icin ana dal not ortalamasi 4,00 uzerinden en az 3,00 olmalidir.",
        sources=[],
        metadata={
            "evidence_packet": {
                "source_owner": "student_affairs_policy",
                "specialist": "registration_agent",
                "value_arbitration": {
                    "answer_threshold": ["3,00"],
                    "scale_value": ["4,00"],
                    "related_condition": ["%20"],
                },
            },
            "answer_validation": {"status": "pass"},
            "answer_value_conflict": {"status": "pass", "primary_value": "3,00"},
        },
    )

    response_task = build_agent_response_task(
        response,
        request_task=request_task,
        emitter_id="registration_agent",
        emitter_name="Registration Agent",
        metadata={
            "agent_role": "specialist_agent",
            "source_owner": {"primary": "student_affairs_policy"},
            "decision_contract": {"contract": {"source_owner": {"primary": "student_affairs_policy"}}},
            "resolved_decision": {"schema": "omu.resolved_decision.v1", "source_owner": "student_affairs_policy"},
            "branch_dispatch_gate": {"restored_primary_department": "student_affairs"},
            "specialist_selection": {"selected_agent_id": "registration_agent"},
        },
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.metadata["source_owner"]["primary"] == "student_affairs_policy"
    assert extracted.metadata["resolved_decision"]["source_owner"] == "student_affairs_policy"
    assert extracted.metadata["specialist_selection"]["selected_agent_id"] == "registration_agent"
    assert extracted.metadata["evidence_packet"]["value_arbitration"]["answer_threshold"] == ["3,00"]
    assert extracted.metadata["answer_validation"]["status"] == "pass"
    assert extracted.metadata["answer_value_conflict"]["primary_value"] == "3,00"


def test_build_text_message_creates_user_message():
    message = build_text_message("Merhaba", context_id="ctx-1", role=Role.user)

    assert message.contextId == "ctx-1"
    assert message.role == Role.user
    assert message.parts[0].root.text == "Merhaba"


def test_build_query_task_sets_metadata_and_state():
    payload = A2AQueryPayload(
        query_text="Harc borcum var mi?",
        context_id="ctx-2",
        task_type="tuition_query",
        student_id=42,
        student_number="20210001",
        student_full_name="Ahmet Yilmaz",
        is_authenticated=True,
    )

    task = build_query_task(payload)

    assert task.contextId == "ctx-2"
    assert task.status.state == TaskState.submitted
    assert task.metadata["query_text"] == "Harc borcum var mi?"
    assert task.metadata["student_id"] == 42
    assert "student_number" not in task.metadata
    assert "student_full_name" not in task.metadata
    assert task.metadata["trace_id"]
    assert task.metadata["span_id"]
    assert task.metadata["state_transitions"][0]["state"] == "submitted"
    assert task.metadata["state_transitions"][0]["task_id"] == task.id
    assert task.metadata["state_transitions"][0]["message_id"] == task.status.message.messageId
    assert task.status.message.metadata["trace_id"] == task.metadata["trace_id"]
    assert task.status.message.metadata["span_id"] == task.metadata["span_id"]


def test_build_query_task_preserves_retrieval_execution_metadata():
    payload = A2AQueryPayload(
        query_text="Muafiyet basvurusu ne zaman yapilir?",
        context_id="ctx-retrieval-policy",
        branch_role="primary",
        retrieval_execution_policy={
            "schema": "omu.retrieval_execution_policy.v1",
            "branch_role": "primary",
            "reranker_candidate_limit": 8,
        },
    )

    task = build_query_task(payload)

    assert task.metadata["branch_role"] == "primary"
    assert task.metadata["retrieval_execution_policy"]["branch_role"] == "primary"
    assert task.metadata["retrieval_execution_policy"]["reranker_candidate_limit"] == 8


def test_build_agent_card_creates_skillful_card():
    card = build_agent_card(
        agent_id="registration_agent",
        name="Registration Agent",
        description="Kayit sureclerine bakar.",
        url="https://omu.edu.tr/agents/registration_agent",
        skills=[],
    )

    assert card.name == "Registration Agent"
    assert card.url.endswith("registration_agent")


def test_department_response_task_uses_data_artifact_and_can_be_extracted():
    request_task = build_query_task(
        A2AQueryPayload(
            query_text="Kayit yenileme ucreti ne kadar?",
            context_id="ctx-3",
            trace_id="trace-response-1",
            span_id="span-department-1",
            parent_span_id="span-main-1",
        )
    )
    response = DepartmentResponse(
        department=Department.FINANCE,
        answer="Yillik ucret 2.397,00 TL.",
        success=True,
        sources=[],
    )

    task = build_department_response_task(
        response,
        request_task=request_task,
        emitter_id="tuition_agent",
        emitter_name="Tuition Agent",
    )

    assert task.metadata["parent_task_id"] == request_task.id
    assert task.metadata["response_schema"] == "omu.agent_response.v1"
    assert task.metadata["legacy_response_schema"] == "omu.department_response.v1"
    assert task.metadata["trace_id"] == "trace-response-1"
    assert [item["state"] for item in task.metadata["state_transitions"]] == [
        "submitted",
        "working",
        "completed",
    ]
    assert task.metadata["state_transitions"][-1]["actor_id"] == "tuition_agent"
    assert task.metadata["state_transitions"][-1]["message_id"] == task.status.message.messageId
    assert task.status.message.metadata["trace_id"] == "trace-response-1"
    assert task.artifacts[0].metadata["trace_id"] == "trace-response-1"
    assert task.artifacts[1].metadata["trace_id"] == "trace-response-1"
    assert "department_response" not in (task.metadata or {})
    assert len(task.artifacts or []) == 2
    assert task.artifacts[1].metadata["schema"] == "omu.agent_response.v1"
    assert "omu.department_response.v1" in task.artifacts[1].extensions

    extracted = extract_department_response(task)
    agent_extracted = extract_agent_response(task)

    assert extracted is not None
    assert agent_extracted is not None
    assert extracted.department == Department.FINANCE
    assert extracted.answer == "Yillik ucret 2.397,00 TL."
    assert agent_extracted.answer == "Yillik ucret 2.397,00 TL."


def test_agent_response_artifact_uses_generic_contract_with_legacy_mapper():
    request_task = build_query_task(
        A2AQueryPayload(
            query_text="Ders programim var mi?",
            context_id="ctx-agent-contract",
        )
    )
    legacy_response = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Program bilgisi bulundu.",
        sources=[],
        generation_mode="vt",
    )

    task = build_agent_response_task(
        legacy_response,
        request_task=request_task,
        emitter_id="curriculum_agent",
        emitter_name="Curriculum Agent",
        metadata={"agent_role": "specialist_agent"},
    )

    data = task.artifacts[1].parts[0].root.data
    assert data["agent_id"] == "curriculum_agent"
    assert data["agent_name"] == "Curriculum Agent"
    assert data["agent_role"] == "specialist_agent"
    assert data["department"] == "academic_programs"
    assert data["metadata"]["legacy_department"] == "academic_programs"

    agent_response = extract_agent_response(task)
    legacy_mapped = extract_department_response(task)

    assert isinstance(agent_response, AgentResponse)
    assert not isinstance(agent_response, DepartmentResponse)
    assert agent_response.agent_id == "curriculum_agent"
    assert legacy_mapped == legacy_response


def test_build_department_response_task_stays_backward_compatible():
    request_task = build_query_task(
        A2AQueryPayload(
            query_text="Harc ucreti ne kadar?",
            context_id="ctx-agent-response-alias",
        )
    )
    response = DepartmentResponse(
        department=Department.FINANCE,
        answer="Agent response cevabi",
        sources=[],
    )

    generic_task = build_agent_response_task(
        response,
        request_task=request_task,
        emitter_id="finance_agent",
        emitter_name="Finance Agent",
    )
    legacy_task = build_department_response_task(
        response,
        request_task=request_task,
        emitter_id="finance_agent",
        emitter_name="Finance Agent",
    )

    assert generic_task.metadata["response_schema"] == "omu.agent_response.v1"
    assert legacy_task.metadata["response_schema"] == generic_task.metadata["response_schema"]
    assert extract_agent_response(generic_task).answer == "Agent response cevabi"
    assert extract_agent_response(legacy_task).answer == "Agent response cevabi"


def test_http_transport_payload_keeps_a2a_metadata_without_session_secret():
    payload = HttpA2ADepartmentTransport._build_dispatch_payload(
        department=Department.STUDENT_AFFAIRS,
        query="Ders kaydi nasil yapilir?",
        context_id="ctx-http-a2a",
        task_type=TaskType.REGISTRATION_QUERY,
        metadata={
            "user_id": "U123",
            "student_id": 42,
            "student_number": "22000001",
            "student_full_name": "Test Ogrenci",
            "student_department": "Bilgisayar Muhendisligi",
            "llm_profile": "fast",
            "is_authenticated": True,
            "session_token": "secret-session-token",
            "force_llm_synthesis": True,
            "is_personal_query": False,
            "source_owner": {
                "schema": "omu.source_owner.v1",
                "primary": "student_affairs_policy",
                "reasoning": "task_type",
            },
            "decision_contract": {
                "schema": "omu.decision_contract.v1",
                "mode": "read_only",
                "contract": {
                    "source_owner": {"primary": "student_affairs_policy"},
                },
            },
            "branch_dispatch_gate": {
                "schema": "omu.branch_dispatch_gate.v1",
                "restored_primary_department": "student_affairs",
            },
            "trace_id": "trace-http-1",
            "span_id": "span-http-1",
            "parent_span_id": "span-main-1",
        },
        disable_specialist_llm=True,
    )

    assert payload["department"] == "student_affairs"
    assert payload["task_type"] == "registration_query"
    assert payload["student_id"] == 42
    assert payload["force_llm_synthesis"] is True
    assert payload["source_owner"]["primary"] == "student_affairs_policy"
    assert payload["decision_contract"]["mode"] == "read_only"
    assert payload["decision_contract"]["contract"]["source_owner"]["primary"] == "student_affairs_policy"
    assert payload["branch_dispatch_gate"]["restored_primary_department"] == "student_affairs"
    assert payload["trace_id"] == "trace-http-1"
    assert payload["span_id"] == "span-http-1"
    assert payload["parent_span_id"] == "span-main-1"
    assert payload["disable_specialist_llm"] is True
    assert "session_token" not in payload


def test_specialist_transport_payload_keeps_specialist_metadata():
    task = build_query_task(
        A2AQueryPayload(
            query_text="Harc ucreti ne kadar?",
            context_id="ctx-specialist-payload",
            task_type="tuition_query",
            student_id=42,
            student_department="Bilgisayar Muhendisligi",
            student_faculty="Muhendislik Fakultesi",
            student_type="Turk",
            is_authenticated=True,
            final_answer_owner="main_orchestrator",
            specialist_response_mode="evidence_packet",
            capability_planner={
                "mode": "on",
                "apply": True,
                "action": {"capability": "finance.tuition_fee"},
            },
            source_owner={
                "schema": "omu.source_owner.v1",
                "primary": "tuition_fee_catalog",
                "reasoning": "capability_planner",
            },
            decision_contract={
                "schema": "omu.decision_contract.v1",
                "mode": "read_only",
                "contract": {
                    "capabilities": {"selected": "finance.tuition_fee"},
                    "source_owner": {"primary": "tuition_fee_catalog"},
                },
            },
            branch_dispatch_gate={
                "schema": "omu.branch_dispatch_gate.v1",
                "restored_primary_department": "finance",
            },
            specialist_selection={
                "selected_agent_id": "tuition_agent",
                "reason": "registry",
            },
            trace_id="trace-specialist-1",
            span_id="span-specialist-1",
            parent_span_id="span-department-1",
        )
    )
    task.metadata["disable_specialist_llm"] = True

    payload = HttpA2ASpecialistTransport._build_dispatch_payload(
        agent=_FakeSpecialistAgent(),
        task=task,
    )

    assert payload["department"] == "finance"
    assert payload["agent_id"] == "tuition_agent"
    assert payload["query"] == "Harc ucreti ne kadar?"
    assert payload["task_type"] == "tuition_query"
    assert payload["student_id"] == 42
    assert payload["student_faculty"] == "Muhendislik Fakultesi"
    assert payload["is_authenticated"] is True
    assert payload["final_answer_owner"] == "main_orchestrator"
    assert payload["specialist_response_mode"] == "evidence_packet"
    assert payload["capability_planner"]["action"]["capability"] == "finance.tuition_fee"
    assert payload["source_owner"]["primary"] == "tuition_fee_catalog"
    assert payload["decision_contract"]["contract"]["capabilities"]["selected"] == "finance.tuition_fee"
    assert payload["branch_dispatch_gate"]["restored_primary_department"] == "finance"
    assert payload["specialist_selection"]["selected_agent_id"] == "tuition_agent"
    assert payload["trace_id"] == "trace-specialist-1"
    assert payload["span_id"] == "span-specialist-1"
    assert payload["parent_span_id"] == "span-department-1"
    assert payload["disable_specialist_llm"] is True


@pytest.mark.asyncio
async def test_capability_http_transport_dispatches_rest_payload(monkeypatch):
    import src.a2a.capability_transport as capability_transport_module
    from src.core.config import settings

    expected = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="HTTP duyuru cevabi",
        sources=[],
    )
    calls = []

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return expected.model_dump(mode="json")

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": self.timeout})
            return _FakeResponse()

    monkeypatch.setattr(settings.a2a, "announcement_url", "http://agent-announcement:8104")
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(capability_transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    response = await HttpA2ACapabilityTransport(timeout_seconds=3).dispatch(
        capability=Capability.ANNOUNCEMENT,
        payload=CapabilityDispatchRequest(
            capability=Capability.ANNOUNCEMENT,
            query="Guncel duyurular neler?",
            context_id="ctx-capability-rest",
            departments=["student_affairs"],
            allow_latest_fallback=False,
        ),
    )

    assert response is not None
    assert response.answer == "HTTP duyuru cevabi"
    assert calls[0]["url"] == "http://agent-announcement:8104/a2a/dispatch"
    assert calls[0]["headers"]["X-Internal-API-Key"] == "test-key"
    assert calls[0]["headers"]["X-A2A-Caller-ID"] == "main_orchestrator"
    assert calls[0]["headers"]["X-A2A-Target-ID"] == "agent-announcement"
    assert calls[0]["json"]["capability"] == "announcement"
    assert calls[0]["json"]["allow_latest_fallback"] is False


@pytest.mark.asyncio
async def test_capability_http_transport_can_use_jsonrpc_message_send(monkeypatch):
    import src.a2a.capability_transport as capability_transport_module
    from src.core.config import settings

    expected = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="JSON-RPC duyuru cevabi",
        sources=[],
    )
    calls = []

    class _FakeResponse:
        def __init__(self, request_id):
            request_task = build_query_task(
                A2AQueryPayload(
                    query_text="Guncel duyurular neler?",
                    context_id="ctx-capability-jsonrpc",
                )
            )
            response_task = build_department_response_task(
                expected,
                request_task=request_task,
                emitter_id="announcement_agent",
                emitter_name="Duyurular Agent",
            )
            self._payload = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response_task.model_dump(mode="json", exclude_none=True),
            }

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": self.timeout})
            return _FakeResponse(json["id"])

    monkeypatch.setattr(settings.a2a, "announcement_url", "http://agent-announcement:8104")
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(capability_transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    response = await HttpA2ACapabilityTransport(
        timeout_seconds=3,
        transport_protocol="jsonrpc",
    ).dispatch(
        capability=Capability.ANNOUNCEMENT,
        payload=CapabilityDispatchRequest(
            capability=Capability.ANNOUNCEMENT,
            query="Guncel duyurular neler?",
            context_id="ctx-capability-jsonrpc",
            departments=["student_affairs"],
            allow_latest_fallback=False,
        ),
    )

    assert response is not None
    assert response.answer == "JSON-RPC duyuru cevabi"
    assert calls[0]["url"] == "http://agent-announcement:8104/a2a"
    assert calls[0]["headers"]["X-Internal-API-Key"] == "test-key"
    assert calls[0]["headers"]["X-A2A-Caller-ID"] == "main_orchestrator"
    assert calls[0]["headers"]["X-A2A-Target-ID"] == "agent-announcement"
    assert calls[0]["json"]["method"] == "message/send"
    assert calls[0]["json"]["params"]["message"]["parts"][0]["text"] == "Guncel duyurular neler?"
    assert calls[0]["json"]["params"]["metadata"]["capability"] == "announcement"
    assert calls[0]["json"]["params"]["metadata"]["allow_latest_fallback"] is False


@pytest.mark.asyncio
async def test_http_transport_dispatch_wraps_department_response(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.transport as transport_module
    from src.core.config import settings

    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="HTTP finans cevabi",
        sources=[],
    )
    calls = []

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return expected.model_dump(mode="json")

    class _FakeHealthResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "ok"}

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            calls.append({"url": url, "kind": "health", "timeout": self.timeout})
            return _FakeHealthResponse()

        async def post(self, url, *, json, headers):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": self.timeout, "kind": "dispatch"})
            return _FakeResponse()

    monkeypatch.setattr(settings.a2a, "finance_url", "http://agent-finance:8103")
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    transport = HttpA2ADepartmentTransport(timeout_seconds=3, retry_count=0)
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc odemesi nasil yapilir?",
        context_id="ctx-http-transport",
        task_type=None,
        metadata={"student_department": "Bilgisayar Muhendisligi"},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.answer == "HTTP finans cevabi"
    assert calls[0]["url"] == "http://agent-finance:8103/a2a/dispatch"
    assert calls[0]["headers"]["X-Internal-API-Key"] == "test-key"
    assert calls[0]["headers"]["X-A2A-Caller-ID"] == "main_orchestrator"
    assert calls[0]["headers"]["X-A2A-Target-ID"] == "agent-finance"
    assert calls[0]["json"]["department"] == "finance"


@pytest.mark.asyncio
async def test_http_transport_can_use_jsonrpc_message_send(monkeypatch):
    from src.core.config import settings
    import src.a2a.transport as transport_module

    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="JSON-RPC finans cevabi",
        sources=[],
    )
    calls = []

    class _FakeResponse:
        def __init__(self, request_id):
            request_task = build_query_task(
                A2AQueryPayload(
                    query_text="Harc ucreti ne kadar?",
                    context_id="ctx-jsonrpc-transport",
                    task_type="tuition_query",
                )
            )
            response_task = build_department_response_task(
                expected,
                request_task=request_task,
                emitter_id="finance_orchestrator",
                emitter_name="Finance Orchestrator",
            )
            self._payload = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response_task.model_dump(mode="json", exclude_none=True),
            }

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            calls.append({"url": url, "kind": "health", "timeout": self.timeout})
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"status": "ok"},
            )

        async def post(self, url, *, json, headers):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": self.timeout, "kind": "dispatch"})
            return _FakeResponse(json["id"])

    monkeypatch.setattr(settings.a2a, "finance_url", "http://agent-finance:8103")
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    transport = HttpA2ADepartmentTransport(
        timeout_seconds=3,
        retry_count=0,
        transport_protocol="jsonrpc",
    )
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc ucreti ne kadar?",
        context_id="ctx-jsonrpc-transport",
        task_type=TaskType.TUITION_QUERY,
        metadata={"student_type": "Turk"},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.answer == "JSON-RPC finans cevabi"
    assert calls[0]["url"] == "http://agent-finance:8103/a2a"
    assert calls[0]["json"]["method"] == "message/send"
    assert calls[0]["json"]["params"]["metadata"]["student_type"] == "Turk"
    assert calls[0]["headers"]["X-Internal-API-Key"] == "test-key"
    assert calls[0]["headers"]["X-A2A-Caller-ID"] == "main_orchestrator"
    assert calls[0]["headers"]["X-A2A-Target-ID"] == "agent-finance"


@pytest.mark.asyncio
async def test_specialist_http_transport_dispatch_wraps_department_response(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.specialist_transport as specialist_transport_module
    from src.core.config import settings

    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="HTTP uzman harc cevabi",
        sources=[],
    )
    calls = []

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return expected.model_dump(mode="json")

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": self.timeout})
            return _FakeResponse()

    monkeypatch.setattr(
        settings.a2a,
        "specialist_endpoints",
        "tuition_agent=http://agent-finance-tuition:8110",
    )
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(specialist_transport_module.httpx, "AsyncClient", _FakeAsyncClient)
    task = build_query_task(
        A2AQueryPayload(
            query_text="Harc ucreti ne kadar?",
            context_id="ctx-specialist-http",
            task_type="tuition_query",
        )
    )

    transport = HttpA2ASpecialistTransport(timeout_seconds=3)
    response_task = await transport.dispatch(
        agent=_FakeSpecialistAgent(),
        task=task,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.answer == "HTTP uzman harc cevabi"
    assert calls[0]["url"] == "http://agent-finance-tuition:8110/a2a/dispatch"
    assert calls[0]["headers"]["X-Internal-API-Key"] == "test-key"
    assert calls[0]["headers"]["X-A2A-Caller-ID"] == "agent-finance"
    assert calls[0]["headers"]["X-A2A-Target-ID"] == "agent-finance-tuition"
    assert calls[0]["json"]["agent_id"] == "tuition_agent"


@pytest.mark.asyncio
async def test_specialist_http_transport_can_use_jsonrpc_message_send(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.specialist_transport as specialist_transport_module
    from src.core.config import settings

    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="JSON-RPC uzman cevabi",
        sources=[],
    )
    calls = []

    class _FakeResponse:
        def __init__(self, request_id):
            request_task = build_query_task(
                A2AQueryPayload(
                    query_text="Harc ucreti ne kadar?",
                    context_id="ctx-specialist-jsonrpc",
                    task_type="tuition_query",
                )
            )
            response_task = build_department_response_task(
                expected,
                request_task=request_task,
                emitter_id="tuition_agent",
                emitter_name="Tuition Agent",
            )
            self._payload = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response_task.model_dump(mode="json", exclude_none=True),
            }

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": self.timeout})
            return _FakeResponse(json["id"])

    monkeypatch.setattr(
        settings.a2a,
        "specialist_endpoints",
        "tuition_agent=http://agent-finance-tuition:8110",
    )
    monkeypatch.setattr(settings.server, "internal_api_key", "test-key")
    monkeypatch.setattr(specialist_transport_module.httpx, "AsyncClient", _FakeAsyncClient)
    task = build_query_task(
        A2AQueryPayload(
            query_text="Harc ucreti ne kadar?",
            context_id="ctx-specialist-jsonrpc",
            task_type="tuition_query",
        )
    )

    transport = HttpA2ASpecialistTransport(
        timeout_seconds=3,
        transport_protocol="jsonrpc",
    )
    response_task = await transport.dispatch(
        agent=_FakeSpecialistAgent(),
        task=task,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.answer == "JSON-RPC uzman cevabi"
    assert calls[0]["url"] == "http://agent-finance-tuition:8110/a2a"
    assert calls[0]["headers"]["X-A2A-Caller-ID"] == "agent-finance"
    assert calls[0]["headers"]["X-A2A-Target-ID"] == "agent-finance-tuition"
    assert calls[0]["json"]["method"] == "message/send"
    assert calls[0]["json"]["params"]["metadata"]["task_type"] == "tuition_query"


def test_specialist_http_transport_uses_specialist_timeout_setting(monkeypatch):
    from src.core.config import settings

    monkeypatch.setattr(settings.a2a, "timeout_seconds", 10.0)
    monkeypatch.setattr(settings.a2a, "specialist_timeout_seconds", 45.0)

    transport = HttpA2ASpecialistTransport()

    assert transport.timeout_seconds == 45.0


def test_specialist_http_transport_uses_a2a_timeout_when_specialist_timeout_unset(monkeypatch):
    from src.core.config import settings

    monkeypatch.setattr(settings.a2a, "timeout_seconds", 12.0)
    monkeypatch.setattr(settings.a2a, "specialist_timeout_seconds", None)

    transport = HttpA2ASpecialistTransport()

    assert transport.timeout_seconds == 12.0


def test_department_http_transport_uses_department_timeout_setting(monkeypatch):
    from src.core.config import settings

    monkeypatch.setattr(settings.a2a, "timeout_seconds", 10.0)
    monkeypatch.setattr(settings.a2a, "department_timeout_seconds", 75.0)

    transport = HttpA2ADepartmentTransport(retry_count=0)

    assert transport.timeout_seconds == 75.0


def test_department_http_transport_falls_back_to_generic_a2a_timeout(monkeypatch):
    from src.core.config import settings

    monkeypatch.setattr(settings.a2a, "timeout_seconds", 12.0)
    monkeypatch.setattr(settings.a2a, "department_timeout_seconds", None)

    transport = HttpA2ADepartmentTransport(retry_count=0)

    assert transport.timeout_seconds == 12.0


@pytest.mark.asyncio
async def test_capability_http_transport_returns_failed_response_when_endpoint_missing(monkeypatch):
    from src.core.config import settings

    monkeypatch.setattr(settings.a2a, "announcement_url", None)
    endpoint_resolver = SimpleNamespace(resolve_service_endpoint=AsyncMock(return_value=None))

    response = await HttpA2ACapabilityTransport(
        timeout_seconds=3,
        endpoint_resolver=endpoint_resolver,
    ).dispatch(
        capability=Capability.ANNOUNCEMENT,
        payload=CapabilityDispatchRequest(
            capability=Capability.ANNOUNCEMENT,
            query="Guncel duyurular neler?",
            context_id="ctx-capability-missing",
        ),
    )

    assert response.success is False
    assert response.error == "a2a_capability_endpoint_missing"
    assert "A2A HTTP" in response.answer
    endpoint_resolver.resolve_service_endpoint.assert_awaited_once_with(
        "announcement",
        role="capability_agent",
    )


@pytest.mark.asyncio
async def test_capability_http_transport_returns_failed_response_on_remote_error(monkeypatch):
    import src.a2a.capability_transport as capability_transport_module
    from src.core.config import settings

    class _FailingAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            raise capability_transport_module.httpx.ConnectError("connection refused")

    monkeypatch.setattr(settings.a2a, "announcement_url", "http://agent-announcement:8104")
    monkeypatch.setattr(capability_transport_module.httpx, "AsyncClient", _FailingAsyncClient)

    response = await HttpA2ACapabilityTransport(timeout_seconds=3).dispatch(
        capability=Capability.ANNOUNCEMENT,
        payload=CapabilityDispatchRequest(
            capability=Capability.ANNOUNCEMENT,
            query="Guncel duyurular neler?",
            context_id="ctx-capability-remote-error",
        ),
    )

    assert response.success is False
    assert response.error == "a2a_capability_transport_failed"
    assert response.db_data["capability"] == "announcement"


@pytest.mark.asyncio
async def test_specialist_http_transport_returns_failed_response_when_endpoint_missing(monkeypatch):
    from src.a2a import extract_department_response
    from src.core.config import settings

    monkeypatch.setattr(settings.a2a, "specialist_endpoints", "")
    endpoint_resolver = SimpleNamespace(resolve_agent_endpoint=AsyncMock(return_value=None))
    agent = _FakeSpecialistAgent(answer="Local specialist cevabi")
    task = build_query_task(
        A2AQueryPayload(
            query_text="Harc ucreti ne kadar?",
            context_id="ctx-specialist-missing",
            task_type="tuition_query",
        )
    )

    transport = HttpA2ASpecialistTransport(
        timeout_seconds=3,
        endpoint_resolver=endpoint_resolver,
    )
    response_task = await transport.dispatch(agent=agent, task=task)

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_specialist_endpoint_missing"
    assert "A2A HTTP" in extracted.answer
    agent.handle_task.assert_not_awaited()
    endpoint_resolver.resolve_agent_endpoint.assert_awaited_once_with(
        "tuition_agent",
        role="specialist_agent",
    )


@pytest.mark.asyncio
async def test_specialist_http_transport_returns_failed_response_on_remote_error(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.specialist_transport as specialist_transport_module
    from src.core.config import settings

    class _FailingAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            raise specialist_transport_module.httpx.ConnectError("connection refused")

    monkeypatch.setattr(
        settings.a2a,
        "specialist_endpoints",
        "tuition_agent=http://agent-finance-tuition:8110",
    )
    monkeypatch.setattr(specialist_transport_module.httpx, "AsyncClient", _FailingAsyncClient)
    agent = _FakeSpecialistAgent(answer="Local specialist cevabi")
    task = build_query_task(
        A2AQueryPayload(
            query_text="Harc ucreti ne kadar?",
            context_id="ctx-specialist-remote-error",
            task_type="tuition_query",
        )
    )

    response_task = await HttpA2ASpecialistTransport(timeout_seconds=3).dispatch(
        agent=agent,
        task=task,
    )
    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_specialist_transport_failed"
    agent.handle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_specialist_http_transport_retries_read_timeout(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.specialist_transport as specialist_transport_module
    from src.core.config import settings

    attempts = {"count": 0}
    header_nonces: list[str] = []

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            attempts["count"] += 1
            header_nonces.append(headers["X-A2A-Nonce"])
            raise specialist_transport_module.httpx.ReadTimeout("timed out")

    auth_calls = {"count": 0}

    def _fake_auth_headers(**kwargs):
        auth_calls["count"] += 1
        return {"X-A2A-Nonce": f"nonce-{auth_calls['count']}"}

    monkeypatch.setattr(
        settings.a2a,
        "specialist_endpoints",
        "tuition_agent=http://agent-finance-tuition:8110",
    )
    monkeypatch.setattr(
        specialist_transport_module,
        "build_a2a_auth_headers",
        _fake_auth_headers,
    )
    monkeypatch.setattr(specialist_transport_module.httpx, "AsyncClient", _FakeAsyncClient)
    task = build_query_task(
        A2AQueryPayload(
            query_text="Harc ucreti ne kadar?",
            context_id="ctx-specialist-timeout",
            task_type="tuition_query",
        )
    )

    response_task = await HttpA2ASpecialistTransport(
        timeout_seconds=3,
        retry_count=1,
        retry_backoff_seconds=0,
    ).dispatch(
        agent=_FakeSpecialistAgent(),
        task=task,
    )
    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_specialist_transport_timeout"
    assert extracted.metadata["attempt"] == 2
    assert attempts["count"] == 2
    assert header_nonces == ["nonce-1", "nonce-2"]


@pytest.mark.asyncio
async def test_specialist_http_transport_opens_circuit_after_repeated_failures(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.specialist_transport as specialist_transport_module
    from src.core.config import settings

    attempts = {"count": 0}

    class _FailingAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            attempts["count"] += 1
            raise specialist_transport_module.httpx.ConnectError("connection refused")

    monkeypatch.setattr(
        settings.a2a,
        "specialist_endpoints",
        "tuition_agent=http://agent-finance-tuition:8110",
    )
    monkeypatch.setattr(specialist_transport_module.httpx, "AsyncClient", _FailingAsyncClient)
    agent = _FakeSpecialistAgent()

    def _task(context_id: str):
        return build_query_task(
            A2AQueryPayload(
                query_text="Harc ucreti ne kadar?",
                context_id=context_id,
                task_type="tuition_query",
            )
        )

    transport = HttpA2ASpecialistTransport(
        timeout_seconds=3,
        retry_count=0,
        circuit_breaker_threshold=2,
        circuit_breaker_cooldown_seconds=60,
    )
    first_task = await transport.dispatch(agent=agent, task=_task("ctx-specialist-circuit-1"))
    second_task = await transport.dispatch(agent=agent, task=_task("ctx-specialist-circuit-2"))
    third_task = await transport.dispatch(agent=agent, task=_task("ctx-specialist-circuit-3"))

    first = extract_department_response(first_task)
    second = extract_department_response(second_task)
    third = extract_department_response(third_task)

    assert first is not None
    assert second is not None
    assert third is not None
    assert first.error == "a2a_specialist_transport_failed"
    assert second.error == "a2a_specialist_transport_failed"
    assert third.error == "a2a_specialist_circuit_open"
    assert attempts["count"] == 2


@pytest.mark.asyncio
async def test_http_transport_returns_failed_response_when_endpoint_missing(monkeypatch):
    from src.a2a import extract_department_response
    from src.core.config import settings

    monkeypatch.setattr(settings.a2a, "finance_url", None)
    endpoint_resolver = SimpleNamespace(resolve_department_endpoint=AsyncMock(return_value=None))

    transport = HttpA2ADepartmentTransport(
        timeout_seconds=3,
        retry_count=0,
        endpoint_resolver=endpoint_resolver,
    )
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc borcum ne kadar?",
        context_id="ctx-http-missing",
        task_type=TaskType.TUITION_QUERY,
        metadata={"is_personal_query": True},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_endpoint_missing"
    assert "agent servisine" in extracted.answer
    endpoint_resolver.resolve_department_endpoint.assert_awaited_once_with(Department.FINANCE)


@pytest.mark.asyncio
async def test_http_transport_resolves_endpoint_from_registry_when_env_missing(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.transport as transport_module
    from src.core.config import settings

    expected = DepartmentResponse(
        department=Department.FINANCE,
        answer="Registry uzerinden finans cevabi",
        sources=[],
    )
    calls = []

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return expected.model_dump(mode="json")

    class _FakeHealthResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "ok"}

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            calls.append({"url": url, "kind": "health", "timeout": self.timeout})
            return _FakeHealthResponse()

        async def post(self, url, *, json, headers):
            calls.append(
                {
                    "url": url,
                    "json": json,
                    "headers": headers,
                    "timeout": self.timeout,
                    "kind": "dispatch",
                }
            )
            return _FakeResponse()

    monkeypatch.setattr(settings.a2a, "finance_url", None)
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)
    endpoint_resolver = SimpleNamespace(
        resolve_department_endpoint=AsyncMock(return_value="http://registry-finance:8103")
    )

    transport = HttpA2ADepartmentTransport(
        timeout_seconds=3,
        retry_count=0,
        endpoint_resolver=endpoint_resolver,
    )
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc odemesi nasil yapilir?",
        context_id="ctx-http-registry-endpoint",
        task_type=None,
        metadata={},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is True
    assert extracted.answer == "Registry uzerinden finans cevabi"
    assert calls[0]["url"] == "http://registry-finance:8103/health"
    assert calls[1]["url"] == "http://registry-finance:8103/a2a/dispatch"
    endpoint_resolver.resolve_department_endpoint.assert_awaited_once_with(Department.FINANCE)


@pytest.mark.asyncio
async def test_http_transport_skips_unhealthy_discovered_endpoint(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.transport as transport_module
    from src.core.config import settings

    calls = {"get": 0, "post": 0}

    class _HealthResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "down"}

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            calls["get"] += 1
            return _HealthResponse()

        async def post(self, url, *, json, headers):
            calls["post"] += 1
            raise AssertionError("dispatch should not be attempted for unhealthy endpoint")

    monkeypatch.setattr(settings.a2a, "finance_url", None)
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)
    endpoint_resolver = SimpleNamespace(
        resolve_department_endpoint=AsyncMock(return_value="http://registry-finance:8103")
    )

    transport = HttpA2ADepartmentTransport(
        timeout_seconds=3,
        retry_count=0,
        endpoint_resolver=endpoint_resolver,
        discovery_healthcheck_cache_seconds=0,
    )
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc odemesi nasil yapilir?",
        context_id="ctx-http-registry-unhealthy",
        task_type=None,
        metadata={},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_endpoint_missing"
    assert calls["get"] == 1
    assert calls["post"] == 0


@pytest.mark.asyncio
async def test_http_transport_caches_discovery_healthcheck(monkeypatch):
    import src.a2a.transport as transport_module
    from src.core.config import settings

    calls = {"get": 0}

    class _HealthResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "ok"}

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            calls["get"] += 1
            return _HealthResponse()

    monkeypatch.setattr(settings.a2a, "finance_url", None)
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)
    endpoint_resolver = SimpleNamespace(
        resolve_department_endpoint=AsyncMock(return_value="http://registry-finance:8103")
    )

    transport = HttpA2ADepartmentTransport(
        timeout_seconds=3,
        retry_count=0,
        endpoint_resolver=endpoint_resolver,
        discovery_healthcheck_cache_seconds=30,
    )

    first = await transport._is_endpoint_healthy("http://registry-finance:8103")
    second = await transport._is_endpoint_healthy("http://registry-finance:8103")

    assert first is True
    assert second is True
    assert calls["get"] == 1


@pytest.mark.asyncio
async def test_http_transport_returns_failed_response_on_http_error(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.transport as transport_module
    from src.core.config import settings

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            raise transport_module.httpx.ConnectError("connection refused")

    monkeypatch.setattr(settings.a2a, "finance_url", "http://agent-finance:8103")
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    transport = HttpA2ADepartmentTransport(timeout_seconds=3, retry_count=0)
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc borcum ne kadar?",
        context_id="ctx-http-error",
        task_type=TaskType.TUITION_QUERY,
        metadata={"is_personal_query": True},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_transport_failed"
    assert extracted.db_data == {"transport_error": "connection refused"}


@pytest.mark.asyncio
async def test_http_transport_returns_timeout_response_on_http_timeout(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.transport as transport_module
    from src.core.config import settings

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            raise transport_module.httpx.ReadTimeout("timed out")

    monkeypatch.setattr(settings.a2a, "finance_url", "http://agent-finance:8103")
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    transport = HttpA2ADepartmentTransport(timeout_seconds=3, retry_count=0)
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc borcum ne kadar?",
        context_id="ctx-http-timeout",
        task_type=TaskType.TUITION_QUERY,
        metadata={"is_personal_query": True},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_transport_timeout"
    assert extracted.db_data == {"transport_error": "timed out"}


@pytest.mark.asyncio
async def test_http_transport_retries_read_timeout(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.transport as transport_module
    from src.core.config import settings

    attempts = {"count": 0}
    header_nonces: list[str] = []

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            attempts["count"] += 1
            header_nonces.append(headers["X-A2A-Nonce"])
            raise transport_module.httpx.ReadTimeout("timed out")

    auth_calls = {"count": 0}

    def _fake_auth_headers(**kwargs):
        auth_calls["count"] += 1
        return {"X-A2A-Nonce": f"nonce-{auth_calls['count']}"}

    monkeypatch.setattr(settings.a2a, "finance_url", "http://agent-finance:8103")
    monkeypatch.setattr(transport_module, "build_a2a_auth_headers", _fake_auth_headers)
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    transport = HttpA2ADepartmentTransport(
        timeout_seconds=3,
        retry_count=1,
        retry_backoff_seconds=0,
    )
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc odemesi nasil yapilir?",
        context_id="ctx-http-timeout-no-retry",
        task_type=None,
        metadata={},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_transport_timeout"
    assert extracted.metadata["attempt"] == 2
    assert attempts["count"] == 2
    assert header_nonces == ["nonce-1", "nonce-2"]


@pytest.mark.asyncio
async def test_http_transport_does_not_retry_non_retryable_http_status(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.transport as transport_module
    from src.core.config import settings

    attempts = {"count": 0}

    class _FakeResponse:
        def __init__(self, url: str):
            self.status_code = 403
            self.text = '{"detail":"forbidden"}'
            self.request = transport_module.httpx.Request("POST", url)

        def raise_for_status(self):
            raise transport_module.httpx.HTTPStatusError(
                "403 forbidden",
                request=self.request,
                response=self,
            )

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            attempts["count"] += 1
            return _FakeResponse(url)

    monkeypatch.setattr(settings.a2a, "finance_url", "http://agent-finance:8103")
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    transport = HttpA2ADepartmentTransport(
        timeout_seconds=3,
        retry_count=2,
        retry_backoff_seconds=0,
    )
    response_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc borcum ne kadar?",
        context_id="ctx-http-403",
        task_type=TaskType.TUITION_QUERY,
        metadata={"is_personal_query": True},
        disable_specialist_llm=False,
    )

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.success is False
    assert extracted.error == "a2a_transport_failed"
    assert extracted.db_data == {"transport_error": 'HTTP 403: {"detail":"forbidden"}'}
    assert attempts["count"] == 1


@pytest.mark.asyncio
async def test_http_transport_opens_circuit_after_repeated_request_failures(monkeypatch):
    from src.a2a import extract_department_response
    import src.a2a.transport as transport_module
    from src.core.config import settings

    attempts = {"count": 0}

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, json, headers):
            attempts["count"] += 1
            raise transport_module.httpx.ConnectError("connection refused")

    monkeypatch.setattr(settings.a2a, "finance_url", "http://agent-finance:8103")
    monkeypatch.setattr(transport_module.httpx, "AsyncClient", _FakeAsyncClient)

    transport = HttpA2ADepartmentTransport(
        timeout_seconds=3,
        retry_count=0,
        circuit_breaker_threshold=2,
        circuit_breaker_cooldown_seconds=60,
    )

    first_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc borcum ne kadar?",
        context_id="ctx-http-circuit-1",
        task_type=TaskType.TUITION_QUERY,
        metadata={"is_personal_query": True},
        disable_specialist_llm=False,
    )
    second_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc borcum ne kadar?",
        context_id="ctx-http-circuit-2",
        task_type=TaskType.TUITION_QUERY,
        metadata={"is_personal_query": True},
        disable_specialist_llm=False,
    )
    third_task = await transport.dispatch(
        department=Department.FINANCE,
        orchestrator=None,
        query="Harc borcum ne kadar?",
        context_id="ctx-http-circuit-3",
        task_type=TaskType.TUITION_QUERY,
        metadata={"is_personal_query": True},
        disable_specialist_llm=False,
    )

    first = extract_department_response(first_task)
    second = extract_department_response(second_task)
    third = extract_department_response(third_task)

    assert first is not None
    assert second is not None
    assert third is not None
    assert first.error == "a2a_transport_failed"
    assert second.error == "a2a_transport_failed"
    assert third.error == "a2a_circuit_open"
    assert third.metadata["transport_error"]
    assert third.metadata["circuit_failures"] == 2
    assert attempts["count"] == 2


@pytest.mark.asyncio
async def test_shadow_transport_returns_primary_and_logs_shadow_comparison(caplog):
    class _FakeTransport:
        def __init__(self, answer: str, generation_mode: str):
            self.answer = answer
            self.generation_mode = generation_mode

        async def dispatch(
            self,
            *,
            department,
            orchestrator,
            query,
            context_id,
            task_type,
            metadata,
            disable_specialist_llm,
        ):
            request_task = build_department_request_task(
                department=department,
                query=query,
                context_id=context_id,
                task_type=task_type,
                metadata=metadata,
                disable_specialist_llm=disable_specialist_llm,
            )
            return build_department_response_task(
                DepartmentResponse(
                    department=department,
                    answer=self.answer,
                    generation_mode=self.generation_mode,
                    sources=[],
                ),
                request_task=request_task,
                emitter_id=f"{department.value}_{self.generation_mode}",
                emitter_name=self.generation_mode,
            )

    class _FakeOrchestrator:
        department = Department.FINANCE

    ShadowDepartmentTransport._pending_tasks.clear()
    transport = ShadowDepartmentTransport()
    transport.primary = _FakeTransport("primary answer", "primary")
    transport.shadow = _FakeTransport("shadow answer", "shadow")

    with caplog.at_level("INFO", logger="src.a2a.transport"):
        response_task = await transport.dispatch(
            department=Department.FINANCE,
            orchestrator=_FakeOrchestrator(),
            query="Harc borcum ne kadar?",
            context_id="ctx-shadow",
            task_type=TaskType.TUITION_QUERY,
            metadata={},
            disable_specialist_llm=False,
        )
        await ShadowDepartmentTransport.wait_for_pending(timeout_seconds=3)

    extracted = extract_department_response(response_task)

    assert extracted is not None
    assert extracted.answer == "primary answer"
    assert any(
        "a2a_shadow_complete department=finance context_id=ctx-shadow" in message
        and "same_answer=False" in message
        for message in caplog.messages
    )
