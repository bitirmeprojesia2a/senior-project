"""
Config ve Constants Unit Testleri

src/core/constants.py modülünün testleri.
"""

import os

import pytest

from src.core import config as config_module
from src.core.config import ModelCacheSettings, Settings
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
        monkeypatch.setenv("OPENAI_ROUTING_MODEL", "")
        monkeypatch.setenv("OPENAI_CONVERSATION_MODEL", "")

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
        monkeypatch.setenv("GOOGLE_AI_ROUTING_MODEL", "")
        monkeypatch.setenv("GOOGLE_AI_GLOBAL_SYNTHESIS_MODEL", "")
        monkeypatch.setenv("OPENAI_ROUTING_MODEL", "")

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

    def test_high_value_provider_lane_applies_only_to_configured_roles(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "balanced")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("LLM_HIGH_VALUE_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_HIGH_VALUE_ROLES", "global_synthesis,specialist_synthesis")

        test_settings = Settings()

        assert test_settings.resolve_llm_provider(role="routing") == "openai_compatible"
        assert test_settings.resolve_llm_provider(role="final_refinement") == "openai_compatible"
        assert test_settings.resolve_llm_provider(role="global_synthesis") == "anthropic"
        assert test_settings.resolve_llm_provider(role="specialist_synthesis") == "anthropic"
        assert test_settings.configured_llm_models()["high_value_provider"] == "anthropic"
        assert test_settings.configured_llm_models()["high_value_roles"] == "global_synthesis,specialist_synthesis"

    def test_groq_only_profile_keeps_primary_provider_even_with_high_value_lane(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "groq_only")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("LLM_HIGH_VALUE_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_HIGH_VALUE_ROLES", "global_synthesis,specialist_synthesis")

        test_settings = Settings()

        assert test_settings.normalize_llm_profile(test_settings.llm.profile) == "balanced"
        assert test_settings.normalize_llm_operating_profile(test_settings.llm.profile) == "groq_only"
        assert test_settings.resolve_llm_provider(role="global_synthesis") == "openai_compatible"
        assert test_settings.configured_llm_models()["operating_profile"] == "groq_only"

    def test_hybrid_quality_profile_uses_high_value_lane_when_configured(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "hybrid_quality")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("LLM_HIGH_VALUE_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_HIGH_VALUE_ROLES", "global_synthesis")

        test_settings = Settings()

        assert test_settings.normalize_llm_profile(test_settings.llm.profile) == "quality"
        assert test_settings.normalize_llm_operating_profile(test_settings.llm.profile) == "hybrid_quality"
        assert test_settings.resolve_llm_provider(role="routing") == "openai_compatible"
        assert test_settings.resolve_llm_provider(role="global_synthesis") == "anthropic"

    def test_hybrid_shadow_profile_does_not_change_answer_provider(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "hybrid_shadow")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("LLM_HIGH_VALUE_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_HIGH_VALUE_ROLES", "global_synthesis")

        test_settings = Settings()

        assert test_settings.normalize_llm_operating_profile(test_settings.llm.profile) == "hybrid_shadow"
        assert test_settings.resolve_llm_provider(role="global_synthesis") == "openai_compatible"

    def test_role_specific_provider_override_wins_over_high_value_lane(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "balanced")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "openai_compatible")
        monkeypatch.setenv("LLM_HIGH_VALUE_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_HIGH_VALUE_ROLES", "global_synthesis")
        monkeypatch.setenv("LLM_GLOBAL_SYNTHESIS_PROVIDER", "google_ai")

        test_settings = Settings()

        assert test_settings.resolve_llm_provider(role="global_synthesis") == "google_ai"

    def test_anthropic_provider_model_resolution(self, monkeypatch):
        monkeypatch.setenv("LLM_PROFILE", "balanced")
        monkeypatch.setenv("LLM_PRIMARY_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "none")
        monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        monkeypatch.setenv("ANTHROPIC_SECONDARY_MODEL", "claude-3-5-haiku-20241022")
        monkeypatch.setenv("ANTHROPIC_ROUTING_MODEL", "claude-3-5-haiku-20241022")
        monkeypatch.setenv("ANTHROPIC_VERSION", "2023-06-01")

        test_settings = Settings()

        assert test_settings.anthropic.anthropic_version == "2023-06-01"
        assert test_settings.resolve_llm_provider(role="routing") == "anthropic"
        assert test_settings.resolve_llm_model(role="routing", provider="anthropic") == "claude-3-5-haiku-20241022"
        assert test_settings.resolve_llm_model(role="global_synthesis", provider="anthropic") == "claude-sonnet-4-20250514"
        assert test_settings.configured_llm_models()["provider"] == "anthropic"


class TestInstitutionSettings:
    """Kurum kimligi ayarlari."""

    def test_institution_defaults_are_omu(self):
        test_settings = Settings()

        assert test_settings.institution.short_name_ascii == "OMU"
        assert test_settings.institution.homepage_url == "https://www.omu.edu.tr"
        assert test_settings.institution.switchboard_phone == "0 (362) 312 19 19"

    def test_institution_can_be_overridden(self, monkeypatch):
        monkeypatch.setenv("INSTITUTION_SHORT_NAME_ASCII", "ABC")
        monkeypatch.setenv("INSTITUTION_NAME_ASCII", "ABC University")
        monkeypatch.setenv("INSTITUTION_HOMEPAGE_URL", "https://abc.example.edu")
        monkeypatch.setenv("INSTITUTION_SUPPORT_BOT_NAME", "ABC Destek Botu")
        monkeypatch.setenv("INSTITUTION_SWITCHBOARD_PHONE", "0 (555) 000 00 00")

        test_settings = Settings()

        assert test_settings.institution.short_name_ascii == "ABC"
        assert test_settings.institution.name_ascii == "ABC University"
        assert test_settings.institution.homepage_url == "https://abc.example.edu"
        assert test_settings.institution.support_bot_name == "ABC Destek Botu"
        assert test_settings.institution.switchboard_phone == "0 (555) 000 00 00"


class TestModelCacheSettings:
    """Local model cache path helpers."""

    def test_model_cache_host_dir_resolves_against_project_root(self, monkeypatch):
        monkeypatch.setenv("MODEL_CACHE_HOST_DIR", "./data/models")

        test_settings = Settings()

        assert test_settings.model_cache.hf_home == test_settings.base_dir / "data" / "models" / "huggingface"
        assert test_settings.model_cache.hf_hub_cache == (
            test_settings.base_dir / "data" / "models" / "huggingface" / "hub"
        )

    def test_apply_model_cache_environment_sets_missing_hf_env(self, monkeypatch):
        monkeypatch.delenv("HF_HOME", raising=False)
        monkeypatch.delenv("HF_HUB_CACHE", raising=False)
        monkeypatch.delenv("SENTENCE_TRANSFORMERS_HOME", raising=False)
        cache_root = Settings().base_dir / "tmp" / "model-cache-test"
        cache = ModelCacheSettings.model_validate(
            {
                "MODEL_CACHE_HOST_DIR": str(cache_root),
                "MODEL_CACHE_SET_HF_ENV": True,
            }
        )
        monkeypatch.setattr(config_module.settings, "model_cache", cache)

        applied = config_module.apply_model_cache_environment()

        assert applied == {
            "HF_HOME": str(cache_root / "huggingface"),
            "HF_HUB_CACHE": str(cache_root / "huggingface" / "hub"),
            "SENTENCE_TRANSFORMERS_HOME": str(cache_root / "huggingface" / "hub"),
        }
        assert os.environ["HF_HOME"] == str(cache_root / "huggingface")


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
        monkeypatch.setenv("A2A_DEPARTMENT_TIMEOUT_SECONDS", "")

        test_settings = Settings()

        assert test_settings.a2a.effective_department_timeout_seconds() == 12
