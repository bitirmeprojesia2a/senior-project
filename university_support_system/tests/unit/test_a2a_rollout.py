"""Tests for the standardized A2A rollout helper."""

from __future__ import annotations

import pytest

from scripts.a2a_rollout import (
    _compose_files,
    _compose_up_args,
    _health_build_id,
    _health_matches_build,
    _health_targets,
    _select_legacy_image_refs,
    _service_names,
)


def test_health_targets_defaults_to_api_and_finance():
    assert _health_targets(
        include_student=False,
        include_academic=False,
        include_announcement=False,
        include_event=False,
        include_finance_specialists=False,
    ) == [
        ("retrieval-service", "http://localhost:8140/health"),
        ("api", "http://localhost:8000/health"),
        ("agent-finance", "http://localhost:8103/health"),
    ]


def test_health_targets_include_optional_agents():
    assert _health_targets(
        include_student=True,
        include_academic=True,
        include_announcement=True,
        include_event=True,
        include_finance_specialists=True,
    ) == [
        ("retrieval-service", "http://localhost:8140/health"),
        ("api", "http://localhost:8000/health"),
        ("agent-finance", "http://localhost:8103/health"),
        ("agent-student-affairs", "http://localhost:8101/health"),
        ("agent-academic", "http://localhost:8102/health"),
        ("agent-announcement", "http://localhost:8104/health"),
        ("agent-event", "http://localhost:8105/health"),
        ("agent-finance-tuition", "http://localhost:8110/health"),
        ("agent-finance-scholarship", "http://localhost:8111/health"),
    ]


def test_compose_files_include_specialist_overlays_for_existing_infra():
    assert _compose_files(
        existing_infra=True,
        include_student=True,
        include_academic=True,
        include_announcement=True,
        include_event=True,
        include_finance_specialists=True,
        include_student_specialists=True,
        include_academic_specialists=True,
    ) == [
        "docker-compose.a2a-existing-infra.yml",
        "docker-compose.a2a-existing-infra-student.yml",
        "docker-compose.a2a-existing-infra-academic.yml",
        "docker-compose.a2a-existing-infra-capabilities.yml",
        "docker-compose.a2a-existing-infra-finance-specialists.yml",
        "docker-compose.a2a-existing-infra-student-specialists.yml",
        "docker-compose.a2a-existing-infra-academic-specialists.yml",
    ]


def test_service_names_include_department_and_specialist_agents():
    assert _service_names(
        include_student=True,
        include_academic=True,
        include_announcement=True,
        include_event=True,
        include_finance_specialists=True,
        include_student_specialists=True,
        include_academic_specialists=True,
    ) == [
        "retrieval-service",
        "api",
        "agent-finance",
        "agent-finance-tuition",
        "agent-finance-scholarship",
        "agent-student-affairs",
        "agent-student-registration",
        "agent-student-graduation",
        "agent-student-internship",
        "agent-student-life",
        "agent-academic",
        "agent-academic-curriculum",
        "agent-academic-regulation",
        "agent-academic-international",
        "agent-announcement",
        "agent-event",
    ]


def test_compose_up_args_force_recreates_services_for_fresh_build_metadata():
    assert _compose_up_args(
        ["docker", "compose", "-f", "docker-compose.a2a-existing-infra.yml"],
        ["api", "agent-finance"],
    ) == [
        "docker",
        "compose",
        "-f",
        "docker-compose.a2a-existing-infra.yml",
        "up",
        "--no-build",
        "--force-recreate",
        "-d",
        "api",
        "agent-finance",
    ]


def test_health_targets_include_department_and_specialist_agents():
    assert _health_targets(
        include_student=True,
        include_academic=True,
        include_announcement=True,
        include_event=True,
        include_finance_specialists=True,
        include_student_specialists=True,
        include_academic_specialists=True,
    ) == [
        ("retrieval-service", "http://localhost:8140/health"),
        ("api", "http://localhost:8000/health"),
        ("agent-finance", "http://localhost:8103/health"),
        ("agent-student-affairs", "http://localhost:8101/health"),
        ("agent-student-registration", "http://localhost:8120/health"),
        ("agent-student-graduation", "http://localhost:8121/health"),
        ("agent-student-internship", "http://localhost:8122/health"),
        ("agent-student-life", "http://localhost:8123/health"),
        ("agent-academic", "http://localhost:8102/health"),
        ("agent-academic-curriculum", "http://localhost:8130/health"),
        ("agent-academic-regulation", "http://localhost:8131/health"),
        ("agent-academic-international", "http://localhost:8132/health"),
        ("agent-announcement", "http://localhost:8104/health"),
        ("agent-event", "http://localhost:8105/health"),
        ("agent-finance-tuition", "http://localhost:8110/health"),
        ("agent-finance-scholarship", "http://localhost:8111/health"),
    ]


def test_select_legacy_image_refs_filters_only_known_candidates():
    image_refs = [
        "university_support_system-app:latest",
        "university_support_system-api:latest",
        "university_support_system-agent-finance:latest",
        "postgres:15-alpine",
    ]

    assert _select_legacy_image_refs(image_refs) == [
        "university_support_system-api:latest",
        "university_support_system-agent-finance:latest",
    ]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {
                "status": "healthy",
                "app": {"build": {"build_id": "codex-build"}},
            },
            True,
        ),
        (
            {
                "status": "ok",
                "build": {"build_id": "codex-build"},
            },
            True,
        ),
        (
            {
                "status": "warming",
                "build": {"build_id": "codex-build"},
                "warmup": {"complete": False},
            },
            True,
        ),
        (
            {
                "status": "healthy",
                "app": {"build": {"build_id": "different-build"}},
            },
            False,
        ),
        (
            {
                "status": "down",
                "build": {"build_id": "codex-build"},
            },
            False,
        ),
    ],
)
def test_health_matches_build(payload, expected):
    assert _health_matches_build(payload, expected_build_id="codex-build") is expected


def test_health_build_id_reads_api_and_agent_payload_shapes():
    assert (
        _health_build_id(
            {
                "status": "healthy",
                "app": {"build": {"build_id": "api-build"}},
            }
        )
        == "api-build"
    )
    assert (
        _health_build_id(
            {
                "status": "ok",
                "build": {"build_id": "agent-build"},
            }
        )
        == "agent-build"
    )
