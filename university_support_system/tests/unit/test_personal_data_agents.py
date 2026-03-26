"""Kisisel veri kullanan uzman ajan testleri."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.agents.finance.agents import ScholarshipAgent, TuitionAgent
from src.agents.student.agents import GraduationAgent
from src.core.constants import Department


def _build_task(query_text: str, *, student_id: int | None, is_authenticated: bool):
    return SimpleNamespace(
        metadata={
            "query_text": query_text,
            "student_id": student_id,
            "is_authenticated": is_authenticated,
        },
        status=SimpleNamespace(message=None),
    )


@pytest.mark.asyncio
async def test_tuition_agent_uses_db_snapshot_for_authenticated_personal_query():
    fetcher = AsyncMock(
        return_value={
            "student_id": 7,
            "student_name": "Ahmet Yilmaz",
            "tuition": {
                "semester": "2025-Guz",
                "total_amount": 15000.0,
                "paid_amount": 10000.0,
                "has_debt": True,
                "debt_amount": 5000.0,
                "due_date": "2026-03-31",
                "last_payment_date": None,
            },
        }
    )
    agent = TuitionAgent(tuition_fetcher=fetcher)

    response = await agent.handle_task(
        _build_task("Harc borcum ne kadar?", student_id=7, is_authenticated=True)
    )

    assert response.success is True
    assert response.db_data["student_id"] == 7
    assert "5000.00 TL borc" in response.answer
    fetcher.assert_awaited_once_with(7)


@pytest.mark.asyncio
async def test_tuition_agent_requires_authentication_for_personal_query():
    fetcher = AsyncMock()
    agent = TuitionAgent(tuition_fetcher=fetcher)

    response = await agent.handle_task(
        _build_task("Odeme gecmisim nedir?", student_id=7, is_authenticated=False)
    )

    assert response.success is False
    assert response.error == "authentication_required"
    fetcher.assert_not_awaited()


@pytest.mark.asyncio
async def test_scholarship_agent_uses_db_snapshot_for_authenticated_personal_query():
    fetcher = AsyncMock(
        return_value={
            "student_id": 8,
            "student_name": "Ayse Demir",
            "gpa": 3.4,
            "scholarship": {
                "program_name": "Yemek Bursu",
                "monthly_amount": 1250.0,
                "status": "active",
                "start_date": "2025-10-01",
                "end_date": None,
            },
            "latest_application": {
                "program_name": "Yemek Bursu",
                "status": "approved",
                "application_date": "2025-09-15",
            },
        }
    )
    agent = ScholarshipAgent(scholarship_fetcher=fetcher)

    response = await agent.handle_task(
        _build_task("Burs durumum ne?", student_id=8, is_authenticated=True)
    )

    assert response.success is True
    assert "Yemek Bursu" in response.answer
    assert "Guncel GNO: 3.40" in response.answer
    fetcher.assert_awaited_once_with(8)


@pytest.mark.asyncio
async def test_graduation_agent_uses_db_snapshot_for_authenticated_personal_query():
    fetcher = AsyncMock(
        return_value={
            "student_id": 9,
            "student_name": "Mehmet Kaya",
            "gpa": 3.1,
            "completed_credits": 140,
            "total_credits": 240,
            "registration_status": "active",
            "recent_courses": [
                {
                    "course_code": "BLM401",
                    "course_name": "Bitirme Projesi",
                    "semester": "2025-Guz",
                    "grade": "AA",
                    "status": "completed",
                }
            ],
        }
    )
    agent = GraduationAgent(academic_fetcher=fetcher)

    response = await agent.handle_task(
        _build_task("GNO'm ve notlarim nasil?", student_id=9, is_authenticated=True)
    )

    assert response.success is True
    assert response.department == Department.STUDENT_AFFAIRS
    assert "GNO: 3.10" in response.answer
    assert "BLM401" in response.answer
    fetcher.assert_awaited_once_with(9)
