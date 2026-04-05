"""A2A helper testleri."""

from a2a.types import Role, TaskState

from src.a2a import (
    A2AQueryPayload,
    build_agent_card,
    build_department_response_task,
    build_query_task,
    build_text_message,
    extract_department_response,
)
from src.core.constants import Department
from src.db.schemas import DepartmentResponse


def test_build_text_message_creates_user_message():
    message = build_text_message("Merhaba", context_id="ctx-1", role=Role.user)

    assert message.contextId == "ctx-1"
    assert message.role == Role.user
    assert message.parts[0].root.text == "Merhaba"


def test_build_query_task_sets_metadata_and_state():
    payload = A2AQueryPayload(
        query_text="Harç borcum var mı?",
        context_id="ctx-2",
        task_type="tuition_query",
        student_id=42,
        is_authenticated=True,
    )

    task = build_query_task(payload)

    assert task.contextId == "ctx-2"
    assert task.status.state == TaskState.submitted
    assert task.metadata["query_text"] == "Harç borcum var mı?"
    assert task.metadata["student_id"] == 42


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
    assert "department_response" not in (task.metadata or {})
    assert len(task.artifacts or []) == 2

    extracted = extract_department_response(task)

    assert extracted is not None
    assert extracted.department == Department.FINANCE
    assert extracted.answer == "Yillik ucret 2.397,00 TL."
