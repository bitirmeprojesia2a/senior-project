from src.llm.prompt_templates import _apply_institution_context


def test_institution_context_rewrites_default_identity(monkeypatch):
    from src.llm import prompt_templates

    monkeypatch.setattr(prompt_templates.settings.institution, "short_name", "ABC")
    monkeypatch.setattr(prompt_templates.settings.institution, "short_name_ascii", "ABC")
    monkeypatch.setattr(prompt_templates.settings.institution, "name", "ABC Üniversitesi")
    monkeypatch.setattr(prompt_templates.settings.institution, "name_ascii", "ABC Universitesi")

    rendered = _apply_institution_context(
        "Bu yanıt Ondokuz Mayıs Üniversitesi (OMÜ) öğrenci destek sistemi için üretilecektir. "
        "Bu üniversite OMÜ'dür (Ondokuz Mayıs Üniversitesi). Başka üniversite adı kullanma."
    )

    assert "ABC Üniversitesi (ABC) öğrenci destek sistemi" in rendered
    assert "Bu kurum ABC (ABC Üniversitesi) bağlamındadır" in rendered
    assert "Ondokuz Mayıs Üniversitesi" not in rendered
    assert "OMÜ" not in rendered


def test_answer_prompts_use_configured_default_institution():
    from src.core.config import settings
    from src.llm.prompt_templates import GENERAL_QA_SYSTEM_PROMPT, MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT

    assert settings.institution.name in GENERAL_QA_SYSTEM_PROMPT
    assert settings.institution.short_name in GENERAL_QA_SYSTEM_PROMPT
    assert settings.institution.short_name in MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT
