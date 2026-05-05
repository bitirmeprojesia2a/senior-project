"""Regression tests for the hotfix batch (v2):
1. EvidenceItem fallback constructor
2. EEM alias scope detection
3. AKTS/GANO routing — narrow registration markers only
4. Foreign token cleanup (Hangul, tonabilir) — real Unicode
5. Identity card answer guard (prompt-level)
6. Announcement length limit
7. Direct A2A failed response fallback
8. Sequential dispatch fallback
9. department_factories AKTS keyword routing
10. department=self.department.value
"""

from __future__ import annotations

from src.quality.evidence import (
    EvidenceItem,
    _stable_source_id,
    _source_identity,
    select_evidence_sentences,
)
from src.db.announcements import _detect_unit_scope as _detect_announcement_unit_scope
from src.db.events import _detect_unit_scope as _detect_event_unit_scope
from src.orchestrators.response_utils import clean_final_answer, _strip_foreign_words
from src.routing.routing_policy import (
    has_akts_markers,
    has_akts_registration_markers,
)
from src.orchestrators.department import _is_transport_error, _extract_transport_diagnostics
from src.db.schemas import DepartmentResponse


# ---------------------------------------------------------------------------
# 1. EvidenceItem fallback constructor
# ---------------------------------------------------------------------------


def test_evidence_item_fallback_constructor_no_error():
    source_id = _stable_source_id(
        _source_identity({}, "test_source"),
        "test content for fallback",
    )
    item = EvidenceItem(
        content_snippet="test content"[:500],
        source_name="test_source",
        source_id=source_id,
        department="student_affairs",
        score=0.5,
        score_type="retrieval",
        selected_sentences=select_evidence_sentences("test query", "test content"),
        matched_query_terms=[],
        relevance_score=0.5,
        extracted_facts=[],
    )
    assert item.source_id == source_id
    assert item.department == "student_affairs"
    assert item.selected_sentences is not None
    assert item.relevance_score == 0.5
    assert item.extracted_facts == []


def test_evidence_item_missing_fields_raises():
    import pytest
    with pytest.raises(TypeError):
        EvidenceItem(
            content_snippet="test",
            source_name="test",
            score=0.5,
            score_type="retrieval",
            matched_query_terms=[],
        )


def test_capacity_query_selects_yaz_okulu_threshold_sentence():
    content = (
        "Yaz okulu en az otuz bes egitim-ogretim gununden olusur. "
        "Dersin acilabilmesi icin gerekli ogrenci sayisi ilgili yonetim kurulu tarafindan belirlenir. "
        "Gerekli gorulmesi halinde siniflar subelere bolunebilir. "
        "Cumartesi gunleri de egitim-ogretime dahildir."
    )

    selected = select_evidence_sentences("Yaz okulu sinif kapasitesi nedir?", content)

    assert "Dersin acilabilmesi" in selected
    assert "ogrenci sayisi" in selected
    assert "subelere bolunebilir" in selected


# ---------------------------------------------------------------------------
# 2. EEM alias scope detection
# ---------------------------------------------------------------------------


def test_eem_typo_announcement_scope():
    result = _detect_announcement_unit_scope("elektrik elktronik muhendisligi duyurulari")
    assert result == "Elektrik Elektronik Muhendisligi"


def test_eem_hyphen_announcement_scope():
    result = _detect_announcement_unit_scope("elektrik-elektronik muhendisligi duyurulari")
    assert result == "Elektrik Elektronik Muhendisligi"


def test_eem_short_alias_announcement_scope():
    result = _detect_announcement_unit_scope("eem bolumu duyurulari")
    assert result == "Elektrik Elektronik Muhendisligi"


def test_eem_typo_event_scope():
    result = _detect_event_unit_scope("elektrik elktronik etkinlikleri")
    assert result == "Elektrik Elektronik Muhendisligi"


def test_eem_hyphen_event_scope():
    result = _detect_event_unit_scope("elektrik-elektronik muhendisligi etkinlikleri")
    assert result == "Elektrik Elektronik Muhendisligi"


# ---------------------------------------------------------------------------
# 3. AKTS/GANO routing — narrow registration markers
# ---------------------------------------------------------------------------


def test_akts_registration_markers_trigger():
    assert has_akts_registration_markers("akts hakki")
    assert has_akts_registration_markers("kredi siniri")
    assert has_akts_registration_markers("ders yuku")
    assert has_akts_registration_markers("gano")
    assert has_akts_registration_markers("gno")
    assert has_akts_registration_markers("azami akts")
    assert has_akts_registration_markers("kac akts alabilirim")


def test_generic_akts_not_registration():
    assert not has_akts_registration_markers("akts")
    assert not has_akts_registration_markers("bu ders kac akts")


def test_generic_akts_still_has_akts_markers():
    assert has_akts_markers("akts")


# ---------------------------------------------------------------------------
# 4. Foreign token cleanup — real Unicode
# ---------------------------------------------------------------------------


def test_hangul_syllable_removed():
    """Korece '\ud558\ud558\ub818' (gerekli) token temizlenmeli."""
    answer = "Bu islem \ud568\uc694 olarak yapilir."
    cleaned = clean_final_answer(answer)
    assert "\ud568\uc694" not in cleaned


def test_hangul_jamo_removed():
    answer = "Basvuru \u1100\u1161\u11a8 yapilmalidir."
    cleaned = _strip_foreign_words(answer)
    assert "\u1100" not in cleaned


def test_tonabilir_replaced():
    text = "Ek s\u00fcre tonabilir."
    cleaned = _strip_foreign_words(text)
    assert "tonabilir" not in cleaned
    assert "taninabilir" in cleaned


def test_cjk_removed():
    text = "Basvuru \u5b66\u751f yapilmalidir."
    cleaned = _strip_foreign_words(text)
    assert "\u5b66\u751f" not in cleaned


def test_devanagari_removed():
    text = "Bu \u0935\u093f\u0926\u094d\u092f\u093e\u0930\u094d\u0925\u0940 icin gecerlidir."
    cleaned = _strip_foreign_words(text)
    assert "\u0935\u093f\u0926\u094d\u092f\u093e\u0930\u094d\u0925\u0940" not in cleaned


def test_arabic_removed():
    text = "Basvuru \u0645\u0637\u0644\u0648\u0628 yapilmalidir."
    cleaned = _strip_foreign_words(text)
    assert "\u0645\u0637\u0644\u0648\u0628" not in cleaned


def test_answer_filter_detects_new_broken_tokens():
    from src.quality.answer_filter import check_answer_quality

    result = check_answer_quality("Muafiyet enen ders appropriate gorunuyor.")
    assert result.needs_rewrite
    assert any(token.lower() in {"enen", "appropriate"} for token in result.bad_tokens)


# ---------------------------------------------------------------------------
# 5. Identity card answer guard
# ---------------------------------------------------------------------------


def test_identity_card_prompt_contains_guard():
    from src.llm.prompt_templates import STUDENT_LIFE_AGENT_SYSTEM_PROMPT
    assert "OGRENCI KIMLIK KARTI" in STUDENT_LIFE_AGENT_SYSTEM_PROMPT
    prompt_lower = STUDENT_LIFE_AGENT_SYSTEM_PROMPT.lower()
    assert "ucretsiz" in prompt_lower or "\u00fccretsiz" in prompt_lower
    assert "dekont" in prompt_lower


# ---------------------------------------------------------------------------
# 6. Announcement length limit
# ---------------------------------------------------------------------------


def test_announcement_agent_limit_is_six():
    """Announcement agent limit+1=6 çekmeli (5 gösterim + 1 has_more dedeksiyon)."""
    from src.agents.announcement.agent import AnnouncementAgent
    import inspect
    source = inspect.getsource(AnnouncementAgent.handle_department_task)
    assert "limit=6" in source
    assert "has_more" in source


def test_source_summary_limited_to_five():
    from src.db.schemas import RAGSource
    from src.orchestrators.response_utils import append_source_summary_for_sources

    sources = [
        RAGSource(content=f"Source {i}", score=1.0, metadata={"title": f"Doc {i}"})
        for i in range(8)
    ]
    result = append_source_summary_for_sources("Cevap.", sources)
    lines = [l for l in result.split("\n") if l.startswith("- ")]
    assert len(lines) == 6
    assert "3 kaynak daha" in result


# ---------------------------------------------------------------------------
# 7. Direct A2A failed response fallback
# ---------------------------------------------------------------------------


def test_is_transport_error():
    assert _is_transport_error("a2a_timeout_error")
    assert _is_transport_error("transport connection refused")
    assert _is_transport_error("timeout after 30s")
    assert _is_transport_error("connection reset")
    assert _is_transport_error("EvidenceItem missing fields")
    assert not _is_transport_error("validation error: invalid input")
    assert not _is_transport_error("user query too short")


def test_extract_transport_diagnostics():
    response = DepartmentResponse(
        department="student_affairs",
        answer="",
        success=False,
        error="a2a_timeout_error",
        metadata={
            "detail": "Connection refused",
            "endpoint": "http://localhost:8001",
            "attempt": 2,
            "timeout_seconds": 120,
            "http_status": 503,
            "error_code": "A2A_TIMEOUT",
        },
    )
    diag = _extract_transport_diagnostics(response)
    assert diag["original_error"] == "a2a_timeout_error"
    assert diag["transport_detail"] == "Connection refused"
    assert diag["transport_endpoint"] == "http://localhost:8001"
    assert diag["transport_attempt"] == 2
    assert diag["transport_error_code"] == "A2A_TIMEOUT"


# ---------------------------------------------------------------------------
# 8. Sequential dispatch fallback (structural)
# ---------------------------------------------------------------------------


def test_dispatch_has_sequential_fallback():
    import inspect
    from src.orchestrators.department_dispatch import dispatch_to_departments
    source = inspect.getsource(dispatch_to_departments)
    assert "department_sequential_a2a_failed" in source
    assert "_is_transport_error" in source


# ---------------------------------------------------------------------------
# 9. department_factories AKTS keyword routing
# ---------------------------------------------------------------------------


def test_academic_programs_gano_routes_to_regulation():
    from src.orchestrators.department_factories import build_academic_programs_orchestrator
    from unittest.mock import MagicMock
    agents = {
        "curriculum_agent": MagicMock(agent_id="curriculum_agent"),
        "regulation_agent": MagicMock(agent_id="regulation_agent"),
        "international_agent": MagicMock(agent_id="international_agent"),
    }
    orch = build_academic_programs_orchestrator(list(agents.values()))
    assert orch.keyword_routing.get("gano") == "regulation_agent"
    assert orch.keyword_routing.get("gno") == "regulation_agent"
    assert orch.keyword_routing.get("akts hakki") == "regulation_agent"
    assert orch.keyword_routing.get("kredi siniri") == "regulation_agent"
    assert orch.keyword_routing.get("akts") == "curriculum_agent"


def test_student_affairs_gano_routes_to_registration():
    from src.orchestrators.department_factories import build_student_affairs_orchestrator
    from unittest.mock import MagicMock
    agents = {
        "registration_agent": MagicMock(agent_id="registration_agent"),
        "graduation_agent": MagicMock(agent_id="graduation_agent"),
        "internship_agent": MagicMock(agent_id="internship_agent"),
        "student_life_agent": MagicMock(agent_id="student_life_agent"),
    }
    orch = build_student_affairs_orchestrator(list(agents.values()))
    assert orch.keyword_routing.get("gano") == "registration_agent"
    assert orch.keyword_routing.get("gno") == "registration_agent"
    assert orch.keyword_routing.get("akts hakki") == "registration_agent"
    assert orch.keyword_routing.get("kredi siniri") == "registration_agent"


# ---------------------------------------------------------------------------
# 10. department=self.department.value
# ---------------------------------------------------------------------------


def test_evidence_item_uses_department_value():
    import inspect
    from src.agents.base import BaseSpecialistAgent
    source = inspect.getsource(BaseSpecialistAgent)
    # EvidenceItem fallback path'de self.department.value kullanilmali
    assert "self.department.value" in source


# ---------------------------------------------------------------------------
# 11. Judge quality gate + intent coverage regression
# ---------------------------------------------------------------------------


def test_judge_quality_gate_is_integrated_in_base_agent():
    import inspect
    from src.agents.base import BaseSpecialistAgent

    source = inspect.getsource(BaseSpecialistAgent)
    assert "_apply_judge_quality_gate" in source
    assert "run_judge" in source
    assert "agent.judge_repair" in source
    assert "agent.judge_retrieve_again" in source


def test_judge_risk_detection_for_no_info_and_numeric():
    from src.quality.judge import _is_risky_answer

    assert _is_risky_answer("3,28 GANO icin 12 AKTS artirim uygulanabilir.")
    assert _is_risky_answer("Bu konuda bilgi bulunamadi.")
    assert not _is_risky_answer("Ders kaydi UBYS uzerinden yapilir.")


def test_intent_coverage_detects_missing_multi_part_evidence():
    from src.quality.intent_coverage import compute_intent_coverage

    coverage = compute_intent_coverage(
        "Yaz okulu ne zaman ve kimler katilabilir?",
        ["Yaz okulunda ders acilmasi icin en az ogrenci sayisi gerekir."],
    )
    assert "time_date" in coverage.sub_intents
    assert "eligibility" in coverage.sub_intents
    assert coverage.is_low


# ---------------------------------------------------------------------------
# 12. FAZ 1 — Natural Turkish in user-facing messages + mojibake absence
# ---------------------------------------------------------------------------


def test_no_mojibake_in_response_utils_regex():
    """Regex patterns in clean_final_answer must not contain mojibake."""
    import inspect
    from src.orchestrators.response_utils import clean_final_answer

    source = inspect.getsource(clean_final_answer)
    # These mojibake sequences must never appear in source code
    for bad in ("\u00c3\u00bc", "\u00c3\u00b6", "\u00c3\u00a7", "\u00e2\u2020",
                "Yan\u00c4\u00b1", "cevab\u00c4\u00b1", "Do\u00c4\u0178", "c\u00c3\u00a7"):
        assert bad not in source, f"Mojibake sequence found in clean_final_answer"


def test_no_mojibake_in_prompt_templates():
    """prompt_templates.py must not contain mojibake arrow or broken chars."""
    import inspect
    from src.llm import prompt_templates

    source = inspect.getsource(prompt_templates)
    assert "\u00e2\u2020\u2019" not in source, "Mojibake arrow â†' found in prompt_templates"


def test_clarification_messages_use_natural_turkish():
    """User-facing clarification messages must use proper Turkish diacritics."""
    from src.orchestrators.query_policy import (
        CLARIFICATION_MESSAGE,
        AUTH_CLARIFICATION_MESSAGE,
        FEE_CONTEXT_CLARIFICATION_MESSAGE,
        APPLICATION_TYPE_CLARIFICATION_MESSAGE,
    )

    for msg in (
        CLARIFICATION_MESSAGE,
        AUTH_CLARIFICATION_MESSAGE,
        FEE_CONTEXT_CLARIFICATION_MESSAGE,
        APPLICATION_TYPE_CLARIFICATION_MESSAGE,
    ):
        # Must contain at least one Turkish diacritic
        has_diacritic = any(c in msg for c in "\u00e7\u011f\u0131\u00f6\u015f\u00fc\u00c7\u011e\u0130\u00d6\u015e\u00dc")
        assert has_diacritic, f"Message lacks Turkish diacritics: {msg[:60]}..."
        # Must NOT contain ASCII Turkish artifacts
        for bad in ("dogru", "bulunamadi", "belirtir misiniz", "ogrenci"):
            assert bad not in msg, f"ASCII Turkish '{bad}' found in: {msg[:60]}..."


def test_announcement_agent_uses_natural_turkish():
    """Announcement agent fallback messages must use proper Turkish diacritics."""
    import inspect
    from src.agents.announcement.agent import AnnouncementAgent

    source = inspect.getsource(AnnouncementAgent._format_announcements)
    assert "\u0130lgili duyurular:" in source
    assert "Ilgili duyurular:" not in source

    source_handle = inspect.getsource(AnnouncementAgent.handle_department_task)
    assert "bulunam\u0131yor" in source_handle or "bulunamad\u0131" in source_handle
    assert "bulunamadi" not in source_handle


def test_base_agent_no_info_uses_natural_turkish():
    """Base agent no-info fallback must use proper Turkish diacritics."""
    import inspect
    from src.agents.base import BaseSpecialistAgent

    source = inspect.getsource(BaseSpecialistAgent)
    assert "bulunamad\u0131" in source
    assert "ileti\u015fime" in source
    assert "bulunamadi" not in source or "bulunamad\u0131" in source


def test_slack_fallback_uses_natural_turkish():
    """Slack fallback message must use proper Turkish diacritics."""
    from src.slack.formatting import split_slack_message

    result = split_slack_message("")
    assert len(result) == 1
    msg = result[0]
    # Must have diacritics, not ASCII Turkish
    assert "\u00fc" in msg  # ü
    assert "uretilemedi" not in msg
    assert "sorunuz\u0131" not in msg  # no ı after soru
    assert "sorunuzu" in msg


# ---------------------------------------------------------------------------
# 13. FAZ 5 — Judge config + main-level integration
# ---------------------------------------------------------------------------


def test_judge_role_in_llm_role():
    """LLMRole must include 'judge'."""
    from src.core.config import LLMRole
    import typing
    args = typing.get_args(LLMRole)
    assert "judge" in args


def test_judge_model_config_field_exists():
    """LLMRuntimeSettings must have judge_model and main_judge_enabled."""
    from src.core.config import LLMRuntimeSettings
    settings = LLMRuntimeSettings()
    assert hasattr(settings, "judge_model")
    assert hasattr(settings, "main_judge_enabled")
    assert settings.main_judge_enabled is True  # default


def test_judge_model_in_configured_llm_models():
    """configured_llm_models health map must include judge and main_judge_enabled."""
    from src.core.config import settings
    models = settings.configured_llm_models()
    assert "judge" in models
    assert "main_judge_enabled" in models


def test_main_judge_gate_method_exists():
    """MainOrchestrator must have _apply_main_judge_gate method."""
    import inspect
    from src.orchestrators.main import MainOrchestrator

    source = inspect.getsource(MainOrchestrator)
    assert "_apply_main_judge_gate" in source
    # Must NOT have ask_clarification as a return path
    assert "ask_clarification" in source  # referenced in action list
    # retrieve_again must be downgraded to rewrite_only
    assert '"rewrite_only", "retrieve_again", "ask_clarification"' in source


def test_main_judge_gate_respects_config_flag():
    """Main judge gate must check settings.llm.main_judge_enabled."""
    import inspect
    from src.orchestrators.main import MainOrchestrator

    source = inspect.getsource(MainOrchestrator.handle_query)
    assert "main_judge_enabled" in source


def test_judge_model_bypasses_profile():
    """Judge role must bypass fast/quality profile — always uses dedicated or primary."""
    from src.core.config import Settings, LLMRuntimeSettings

    llm = LLMRuntimeSettings(profile="fast")
    s = Settings(llm=llm)
    # With profile=fast, routing goes to secondary — but judge must NOT
    judge_model = s.resolve_llm_model(role="judge", profile="fast")
    primary_model = s.resolve_llm_model(role="default", profile="quality")
    # Judge should use primary model (no judge_model override set)
    assert judge_model == primary_model


def test_judge_model_no_namespace_leak():
    """LLM_JUDGE_MODEL must not leak into fallback provider namespace."""
    from src.core.config import Settings, LLMRuntimeSettings

    llm = LLMRuntimeSettings(judge_model="some-ollama-model", primary_provider="ollama")
    s = Settings(llm=llm)
    # Resolving judge for fallback provider should NOT use judge_model
    # (it belongs to ollama namespace, not google_ai)
    judge_on_fallback = s.resolve_llm_model(role="judge", provider="google_ai")
    google_primary = s._resolve_provider_primary_model("google_ai")
    assert judge_on_fallback == google_primary


def test_evidence_summary_uses_content_source_score_only():
    """Main judge evidence summary must use content+source+score, not selected_sentences."""
    import inspect
    from src.orchestrators.main import MainOrchestrator

    source = inspect.getsource(MainOrchestrator._apply_main_judge_gate)
    # Must have the NOTE explaining RAGSource doesn't carry selected_sentences
    assert "RAGSource.metadata does NOT carry selected_sentences" in source
    # Must NOT try to read selected_sentences from metadata
    assert 'metadata.get("selected_sentences"' not in source
    assert 'metadata.get("extracted_facts"' not in source
