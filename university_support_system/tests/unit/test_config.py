"""
Config ve Constants Unit Testleri

src/core/constants.py modülünün testleri.
"""

import pytest

from src.core.constants import (
    AgentRole,
    build_department_routing_descriptions,
    ConfidenceLevel,
    collection_name_for_department,
    Department,
    department_values,
    get_department_config,
    InternalTaskStatus,
    known_department_directory_names,
    normalize_department_value,
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
        assert Department.STUDENT_AFFAIRS.value == "student_affairs"
        assert Department.ACADEMIC_PROGRAMS.value == "academic_programs"

    def test_department_display_names(self):
        """Türkçe görüntüleme adları doğru."""
        assert Department.FINANCE.display_name == "Finans"
        assert Department.STUDENT_AFFAIRS.display_name == "Öğrenci İşleri"
        assert Department.ACADEMIC_PROGRAMS.display_name == "Akademik Programlar"

    def test_department_from_string(self):
        """String'den Department oluşturulabilir."""
        assert Department("finance") == Department.FINANCE
        assert Department("academic_programs") == Department.ACADEMIC_PROGRAMS

    def test_collection_name_for_department(self):
        """Departmandan koleksiyon adı üretilebilir."""
        assert collection_name_for_department(Department.STUDENT_AFFAIRS) == "student_affairs_docs"
        assert collection_name_for_department(Department.ACADEMIC_PROGRAMS) == "academic_programs_docs"
        assert collection_name_for_department("finance") == "finance_docs"

    def test_normalize_department_value(self):
        """Departman alias değeri normalize edilebilir."""
        assert normalize_department_value("finance") == "finance"
        assert normalize_department_value("student_affairs") == "student_affairs"

    def test_department_registry_helpers(self):
        """Merkezi departman yardımcıları tutarlı çalışır."""
        assert department_values() == [department.value for department in Department]
        assert "academic_programs" in known_department_directory_names()
        assert get_department_config(Department.FINANCE).display_name == "Finans"

    def test_routing_descriptions_are_generated_from_registry(self):
        """Prompt açıklamaları merkezden üretilir."""
        descriptions = build_department_routing_descriptions()
        assert any('"finance"' in line for line in descriptions)
        assert any('"academic_programs"' in line for line in descriptions)


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
