"""
Config ve Constants Unit Testleri

src/core/constants.py modülünün testleri.
"""

import pytest

from src.core.constants import (
    AgentRole,
    ConfidenceLevel,
    Department,
    InternalTaskStatus,
    Priority,
    RoutingStrategy,
    TaskType,
    ROUTING_HIGH_CONFIDENCE_THRESHOLD,
    ROUTING_LOW_CONFIDENCE_THRESHOLD,
)


class TestDepartmentEnum:
    """Department enum testleri."""

    def test_department_values(self):
        """Tüm departman değerleri doğru tanımlı."""
        assert Department.FINANCE.value == "finance"
        assert Department.IT.value == "it"
        assert Department.STUDENT_AFFAIRS.value == "student_affairs"

    def test_department_display_names(self):
        """Türkçe görüntüleme adları doğru."""
        assert Department.FINANCE.display_name == "Finans"
        assert Department.IT.display_name == "Bilgi İşlem"
        assert Department.STUDENT_AFFAIRS.display_name == "Öğrenci İşleri"

    def test_department_from_string(self):
        """String'den Department oluşturulabilir."""
        assert Department("finance") == Department.FINANCE


class TestInternalTaskStatusEnum:
    """InternalTaskStatus enum testleri."""

    def test_all_statuses_exist(self):
        """Tüm iç görev durumları tanımlı."""
        statuses = [s.value for s in InternalTaskStatus]
        assert "routing" in statuses
        assert "queued" in statuses
        assert "retrying" in statuses
        assert "timeout" in statuses


class TestTaskTypeEnum:
    """TaskType enum testleri."""

    def test_finance_task_types(self):
        """Finans görev tipleri tanımlı."""
        assert TaskType.TUITION_QUERY.value == "tuition_query"
        assert TaskType.SCHOLARSHIP_QUERY.value == "scholarship_query"

    def test_it_task_types(self):
        """IT görev tipleri tanımlı."""
        assert TaskType.TECH_SUPPORT.value == "tech_support"
        assert TaskType.EMAIL_SUPPORT.value == "email_support"

    def test_student_task_types(self):
        """Öğrenci işleri görev tipleri tanımlı."""
        assert TaskType.COURSE_QUERY.value == "course_query"
        assert TaskType.REGISTRATION_QUERY.value == "registration_query"


class TestPriorityEnum:
    """Priority enum testleri."""

    def test_priority_ordering(self):
        """Öncelik sıralaması doğru."""
        assert Priority.LOW < Priority.NORMAL < Priority.HIGH < Priority.URGENT < Priority.CRITICAL


class TestRoutingConstants:
    """Yönlendirme sabit değerleri testleri."""

    def test_confidence_thresholds(self):
        """Güven eşik değerleri mantıklı."""
        assert 0 < ROUTING_LOW_CONFIDENCE_THRESHOLD < ROUTING_HIGH_CONFIDENCE_THRESHOLD < 1

    def test_threshold_values(self):
        """Eşik değerleri doğru."""
        assert ROUTING_HIGH_CONFIDENCE_THRESHOLD == 0.7
        assert ROUTING_LOW_CONFIDENCE_THRESHOLD == 0.4
