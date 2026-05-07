"""
Config ve Constants Unit Testleri

src/core/constants.py modülünün testleri.
"""

import pytest

from src.core.config import Settings
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


class TestLLMModelResolution:
    """Rol bazli model cozumleme kurallari."""

    def test_fast_profile_prefers_secondary_model_for_all_roles(self, monkeypatch):
        monkeypatch.setenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
        monkeypatch.setenv("OPENAI_SECONDARY_MODEL", "llama-3.1-8b-instant")
        monkeypatch.setenv("LLM_PROFILE", "fast")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")

        test_settings = Settings()

        assert test_settings.resolve_llm_model(role="routing") == "llama-3.1-8b-instant"
        assert test_settings.resolve_llm_model(role="conversation") == "llama-3.1-8b-instant"
        assert test_settings.resolve_llm_model(role="query_expansion") == "llama-3.1-8b-instant"
        assert test_settings.resolve_llm_model(role="global_synthesis") == "llama-3.1-8b-instant"

    def test_balanced_profile_uses_role_overrides_before_primary_model(self, monkeypatch):
        monkeypatch.setenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
        monkeypatch.setenv("OPENAI_SECONDARY_MODEL", "llama-3.1-8b-instant")
        monkeypatch.setenv("LLM_PROFILE", "balanced")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("LLM_ROUTING_MODEL", "llama-3.1-8b-instant")
        monkeypatch.setenv("LLM_CONVERSATION_MODEL", "llama-3.1-8b-instant")
        monkeypatch.setenv("LLM_QUERY_EXPANSION_MODEL", "llama-3.3-70b-versatile")
        monkeypatch.setenv("LLM_SPECIALIST_SYNTHESIS_MODEL", "")
        monkeypatch.setenv("LLM_GLOBAL_SYNTHESIS_MODEL", "")

        test_settings = Settings()

        assert test_settings.resolve_llm_model(role="routing") == "llama-3.1-8b-instant"
        assert test_settings.resolve_llm_model(role="conversation") == "llama-3.1-8b-instant"
        assert test_settings.resolve_llm_model(role="query_expansion") == "llama-3.3-70b-versatile"
        assert test_settings.resolve_llm_model(role="specialist_synthesis") == "llama-3.3-70b-versatile"
        assert test_settings.resolve_llm_model(role="global_synthesis") == "llama-3.3-70b-versatile"

    def test_google_ai_provider_uses_its_own_model_namespace(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "balanced")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "google_ai")
        monkeypatch.setenv("LLM_ROUTING_MODEL", "llama-3.1-8b-instant")
        monkeypatch.setenv("OPENAI_MODEL", "llama-3.1-70b-versatile")
        monkeypatch.setenv("OPENAI_SECONDARY_MODEL", "llama-3.1-8b-instant")
        monkeypatch.setenv("GOOGLE_AI_MODEL", "gemini-2.5-flash")
        monkeypatch.setenv("GOOGLE_AI_SECONDARY_MODEL", "gemini-2.5-flash-lite")
        monkeypatch.delenv("GOOGLE_AI_ROUTING_MODEL", raising=False)

        test_settings = Settings()

        assert (
            test_settings.resolve_llm_model(role="routing", provider="openai_compatible")
            == "llama-3.1-8b-instant"
        )
        assert (
            test_settings.resolve_llm_model(role="routing", provider="google_ai")
            == "gemini-2.5-flash-lite"
        )
        assert (
            test_settings.resolve_llm_model(role="global_synthesis", provider="google_ai")
            == "gemini-2.5-flash"
        )

    def test_provider_specific_query_expansion_override_wins(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "balanced")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
        monkeypatch.setenv("OPENAI_SECONDARY_MODEL", "llama-3.1-8b-instant")
        monkeypatch.setenv("OPENAI_QUERY_EXPANSION_MODEL", "llama-3.3-70b-versatile")

        test_settings = Settings()

        assert (
            test_settings.resolve_llm_model(role="query_expansion", provider="openai_compatible")
            == "llama-3.3-70b-versatile"
        )

    def test_google_ai_provider_specific_role_override_wins(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "balanced")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("GOOGLE_AI_MODEL", "gemini-2.5-flash")
        monkeypatch.setenv("GOOGLE_AI_SECONDARY_MODEL", "gemini-2.5-flash-lite")
        monkeypatch.setenv("GOOGLE_AI_ROUTING_MODEL", "gemini-2.5-flash")

        test_settings = Settings()

        assert (
            test_settings.resolve_llm_model(role="routing", provider="google_ai")
            == "gemini-2.5-flash"
        )

    def test_role_specific_provider_override_wins(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "balanced")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("LLM_GLOBAL_SYNTHESIS_PROVIDER", "google_ai")
        monkeypatch.setenv("LLM_JUDGE_PROVIDER", "google_ai")
        monkeypatch.setenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
        monkeypatch.setenv("OPENAI_SECONDARY_MODEL", "llama-3.3-70b-versatile")
        monkeypatch.setenv("GOOGLE_AI_MODEL", "gemini-3-flash-preview")
        monkeypatch.setenv("GOOGLE_AI_GLOBAL_SYNTHESIS_MODEL", "gemini-3-flash-preview")

        test_settings = Settings()

        assert test_settings.resolve_llm_provider(role="routing") == "openai_compatible"
        assert test_settings.resolve_llm_provider(role="global_synthesis") == "google_ai"
        assert (
            test_settings.resolve_llm_model(
                role="global_synthesis",
                provider=test_settings.resolve_llm_provider(role="global_synthesis"),
            )
            == "gemini-3-flash-preview"
        )
        assert test_settings.configured_llm_models()["global_synthesis_provider"] == "google_ai"


class TestSlackSettings:
    """Slack config yardimcilari."""

    def test_socket_mode_requires_all_three_tokens(self, monkeypatch):
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
        monkeypatch.setenv("SLACK_SIGNING_SECRET", "secret")
        monkeypatch.setenv("SLACK_APP_TOKEN", "")

        assert Settings().slack.is_configured is True
        assert Settings().slack.socket_mode_configured is False

        monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-test")

        assert Settings().slack.socket_mode_configured is True


class TestA2ASettings:
    """A2A transport config yardimcilari."""

    def test_a2a_defaults_to_inprocess(self):
        test_settings = Settings()

        assert test_settings.a2a.mode == "inprocess"

    def test_a2a_endpoint_for_department_trims_trailing_slash(self, monkeypatch):
        monkeypatch.setenv("A2A_MODE", "http")
        monkeypatch.setenv("A2A_STUDENT_AFFAIRS_URL", "http://localhost:8101/")

        test_settings = Settings()

        assert test_settings.a2a.mode == "http"
        assert test_settings.a2a.endpoint_for("student_affairs") == "http://localhost:8101"
        assert test_settings.a2a.endpoint_for("unknown") is None

    def test_a2a_department_timeout_can_be_configured_independently(self, monkeypatch):
        monkeypatch.setenv("A2A_TIMEOUT_SECONDS", "10")
        monkeypatch.setenv("A2A_DEPARTMENT_TIMEOUT_SECONDS", "75")

        test_settings = Settings()

        assert test_settings.a2a.timeout_seconds == 10
        assert test_settings.a2a.effective_department_timeout_seconds() == 75

    def test_a2a_department_timeout_falls_back_to_generic_timeout(self, monkeypatch):
        monkeypatch.setenv("A2A_TIMEOUT_SECONDS", "12")
        monkeypatch.delenv("A2A_DEPARTMENT_TIMEOUT_SECONDS", raising=False)

        test_settings = Settings()

        assert test_settings.a2a.effective_department_timeout_seconds() == 12
