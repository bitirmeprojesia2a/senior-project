"""
Veritabanı Modelleri Unit Testleri

SQLAlchemy modellerinin oluşturulma, ilişki ve temel operasyonlarının testleri.
"""

import pytest
from datetime import datetime

from sqlalchemy import select

from src.db.models import (
    Student,
    Course,
    StudentCourse,
    Tuition,
    Payment,
    Scholarship,
    UserAccount,
    QueryLog,
    AgentRegistry,
)


class TestStudentModel:
    """Student model testleri."""

    async def test_create_student(self, db_session, sample_student_data):
        """Öğrenci oluşturulabilir."""
        student = Student(**sample_student_data)
        db_session.add(student)
        await db_session.flush()

        assert student.id is not None
        assert student.student_id == "20210001"
        assert student.full_name == "Ahmet Yılmaz"
        assert student.gpa == 3.45

    async def test_student_default_values(self, db_session):
        """Öğrenci varsayılan değerleri doğru."""
        student = Student(
            student_id="20210002",
            full_name="Ayşe Demir",
        )
        db_session.add(student)
        await db_session.flush()

        assert student.registration_status == "Aktif"
        assert student.gpa == 0.0
        assert student.total_credits == 0
        assert student.current_semester == 1

    async def test_student_repr(self, db_session, sample_student_data):
        """Student __repr__ doğru çalışıyor."""
        student = Student(**sample_student_data)
        assert "20210001" in repr(student)
        assert "Ahmet Yılmaz" in repr(student)


class TestTuitionModel:
    """Tuition (harç) model testleri."""

    async def test_create_tuition(self, db_session, sample_student_data):
        """Harç kaydı oluşturulabilir."""
        student = Student(**sample_student_data)
        db_session.add(student)
        await db_session.flush()

        tuition = Tuition(
            student_id=student.id,
            semester="2024-Güz",
            total_amount=15000.0,
            paid_amount=10000.0,
            has_debt=True,
            debt_amount=5000.0,
        )
        db_session.add(tuition)
        await db_session.flush()

        assert tuition.id is not None
        assert tuition.debt_amount == 5000.0
        assert tuition.has_debt is True


class TestQueryLogModel:
    """QueryLog model testleri."""

    async def test_create_query_log(self, db_session):
        """Sorgu logu oluşturulabilir."""
        log = QueryLog(
            user_id="user_123",
            query_text="Harç borcum ne kadar?",
            departments={"departments": ["finance"]},
            routing_strategy="direct",
            confidence_score=0.92,
            response_text="Harç borcunuz 5000 TL'dir.",
            response_time_ms=1250.5,
            status="completed",
        )
        db_session.add(log)
        await db_session.flush()

        assert log.id is not None
        assert log.departments == {"departments": ["finance"]}

    async def test_query_log_jsonb(self, db_session):
        """JSONB query_metadata alanı çalışıyor."""
        log = QueryLog(
            query_text="Test sorgusu",
            query_metadata={"source": "slack", "channel": "#general"},
        )
        db_session.add(log)
        await db_session.flush()

        assert log.query_metadata["source"] == "slack"


class TestAgentRegistryModel:
    """AgentRegistry model testleri."""

    async def test_create_agent_registry(self, db_session):
        """Ajan kaydı oluşturulabilir."""
        agent = AgentRegistry(
            agent_id="finance_orchestrator",
            name="Finans Orkestratörü",
            department="finance",
            role="department_orchestrator",
            description="Finans departmanı görevlerini yönetir.",
            capabilities={"task_types": ["tuition_query", "scholarship_query"]},
            is_active=True,
        )
        db_session.add(agent)
        await db_session.flush()

        assert agent.id is not None
        assert agent.capabilities["task_types"][0] == "tuition_query"
