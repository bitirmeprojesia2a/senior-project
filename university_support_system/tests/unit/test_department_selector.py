"""Department specialist selector contract-first behavior."""

from types import SimpleNamespace

import pytest

from src.core.constants import Department, TaskType
from src.orchestrators.department_factories import (
    build_academic_programs_orchestrator,
    build_finance_orchestrator,
    build_student_affairs_orchestrator,
)


class _FakeAgent:
    def __init__(self, name: str, department: Department):
        self.name = name
        self.department = department
        self.agent_id = f"{name}_agent"
        self.definition = SimpleNamespace(name=f"{name.title()} Agent")


def _student_affairs_orchestrator():
    return build_student_affairs_orchestrator(
        [
            _FakeAgent("registration", Department.STUDENT_AFFAIRS),
            _FakeAgent("graduation", Department.STUDENT_AFFAIRS),
            _FakeAgent("internship", Department.STUDENT_AFFAIRS),
            _FakeAgent("student_life", Department.STUDENT_AFFAIRS),
        ]
    )


def _finance_orchestrator():
    return build_finance_orchestrator(
        [
            _FakeAgent("tuition", Department.FINANCE),
            _FakeAgent("scholarship", Department.FINANCE),
        ]
    )


def _academic_programs_orchestrator():
    return build_academic_programs_orchestrator(
        [
            _FakeAgent("curriculum", Department.ACADEMIC_PROGRAMS),
            _FakeAgent("regulation", Department.ACADEMIC_PROGRAMS),
            _FakeAgent("international", Department.ACADEMIC_PROGRAMS),
        ]
    )


def test_contract_capability_overrides_legacy_keyword_shadow():
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        "Staj basvurusu nasil yapilir?",
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {"topic": "kayit dondurma"},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == "registration_agent"
    assert metadata["selected_by"] == "contract"
    assert metadata["contract"]["agent_id"] == "registration_agent"
    assert metadata["registry"]["agent_id"] == "registration_agent"
    assert metadata["legacy_keyword"]["agent_id"] == "internship_agent"
    assert metadata["legacy_keyword"]["matches_selected"] is False


def test_contract_policy_topic_selects_specific_student_affairs_specialist():
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        "Bu surec nasil isler?",
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {"topic": "staj", "question_type": "procedure"},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == "internship_agent"
    assert metadata["selected_by"] == "contract"
    assert metadata["registry"]["topic"] == "student_affairs_internship_policy"
    assert metadata["task_type"]["agent_id"] == "registration_agent"
    assert metadata["legacy_keyword"]["agent_id"] is None


def test_contract_selector_ignores_evidence_source_names():
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        "Peki not ortalamasi kac olmali?",
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {
                        "topic": "CAP / Cift Anadal",
                        "question_type": "eligibility",
                        "must_answer": ["not ortalamasi kosulu"],
                        "preferred_sources": ["yonerge_onlisans_lisans_staj.pdf"],
                    },
                    "evidence_contract": {
                        "preferred_sources": ["yonerge_onlisans_lisans_staj.pdf"],
                    },
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
            "decision_contract": {
                "contract": {
                    "query": {
                        "effective": (
                            "Cift anadal programi basvurusu icin "
                            "not ortalamasi kac olmali?"
                        ),
                    },
                    "conversation": {
                        "active_topic": "CAP / Cift Anadal",
                        "frame": {
                            "source_hints": ["yonerge_onlisans_lisans_staj.pdf"],
                        },
                    },
                    "capabilities": {
                        "selected": "student_affairs.policy_lookup",
                    },
                    "retrieval": {
                        "source_hints": ["yonerge_onlisans_lisans_staj.pdf"],
                    },
                    "evidence": {
                        "top_sources": ["yonerge_onlisans_lisans_staj.pdf"],
                    },
                }
            },
        },
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == "registration_agent"
    assert metadata["selected_by"] == "contract"
    assert metadata["contract"]["agent_id"] == "registration_agent"
    assert metadata["registry"]["agent_id"] == "registration_agent"
    assert metadata["legacy_keyword"]["agent_id"] is None


def test_registry_keeps_cap_gpa_followup_on_registration_despite_graduation_context():
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.ACADEMIC_QUERY,
        "Peki not ortalamasi kac olmali?",
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "intent": "cap_gpa_requirement",
                    "params": {
                        "topic": "CAP / Cift Anadal",
                        "question_type": "eligibility",
                        "must_answer": ["not ortalamasi", "mezuniyet kosullari"],
                    },
                    "answer_contract": {
                        "must_answer": [
                            "CAP basvurusu icin gereken GANO",
                            "mezuniyet hakkini etkilemeyen basvuru kosulu",
                        ]
                    },
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
            "decision_contract": {
                "contract": {
                    "query": {"effective": "CAP icin not ortalamasi kac olmali?"},
                    "conversation": {"active_topic": "CAP basvurusu ve mezuniyet"},
                    "capabilities": {"selected": "student_affairs.policy_lookup"},
                    "retrieval": {"must_answer": ["not ortalamasi kosulu"]},
                }
            },
        },
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == "registration_agent"
    assert metadata["selected_by"] == "contract"
    assert metadata["registry"]["topic"] == "student_affairs_registration_policy"


def test_registry_routes_explicit_graduation_document_topic_to_graduation_agent():
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.ACADEMIC_QUERY,
        "Mezuniyet diplomami ve transkriptimi nasil alirim?",
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {"topic": "mezuniyet diploma transkript"},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == "graduation_agent"
    assert metadata["registry"]["topic"] == "student_affairs_graduation_policy"


def test_registry_routes_student_life_policy_topic_to_student_life_agent():
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        "Ogrenci toplulugu kurmak icin akademik danisman sart mi?",
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {"topic": "ogrenci topluluklari"},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
    )

    assert decision.agent.agent_id == "student_life_agent"


@pytest.mark.parametrize(
    ("topic", "query"),
    [
        ("CAP basvurusu", "CAP basvurusu nasil yapilir?"),
        ("CAP not ortalamasi", "CAP icin not ortalamasi kac olmali?"),
        ("yandal GANO", "Yandal basvurusu icin GANO kac olmali?"),
        ("yatay gecis muafiyet intibak", "Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?"),
        ("akts hakki kredi siniri", "Bu donem AKTS hakki ve kredi siniri nedir?"),
        ("yaz okulu tek ders mazeret", "Yaz okulu ve tek ders basvurusu nasil yapilir?"),
        ("kayit dondurma", "Kayit dondurma basvurusu icin ne yapmaliyim?"),
    ],
)
def test_registry_routes_core_registration_policy_matrix_to_registration_agent(topic, query):
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        query,
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {"topic": topic, "question_type": "policy_lookup"},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
    )

    assert decision.agent.agent_id == "registration_agent"


@pytest.mark.parametrize(
    ("topic", "query", "expected_agent"),
    [
        ("mezuniyet diploma", "Mezuniyet diplomami nasil alirim?", "graduation_agent"),
        ("transkript", "Transkript belgemi nereden alirim?", "graduation_agent"),
        ("staj MUP", "MUP ve zorunlu staj basvurusu nasil yapilir?", "internship_agent"),
        ("ogrenci toplulugu", "Ogrenci toplulugu kurmak icin ne gerekir?", "student_life_agent"),
        ("konukevi yemek engelli", "Engelli ogrenci ve konukevi hizmetleri icin nereye basvurulur?", "student_life_agent"),
        ("bitirme", "Bitirme icin hangi islem yapilir?", "registration_agent"),
    ],
)
def test_registry_student_affairs_policy_specialist_audit_matrix(topic, query, expected_agent):
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        query,
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {"topic": topic, "question_type": "policy_lookup"},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == expected_agent
    assert metadata["selected_by"] == "contract"
    assert metadata["registry"]["allowed_specialists"] == [
        "registration_agent",
        "graduation_agent",
        "internship_agent",
        "student_life_agent",
    ]


def test_registry_routes_academic_policy_support_to_regulation_agent():
    orchestrator = _academic_programs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        "CAP basvurusu icin not ortalamasi kac olmali?",
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {"topic": "CAP not ortalamasi"},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == "regulation_agent"
    assert metadata["registry"]["topic"] == "academic_policy_support"


def test_registry_routes_curriculum_course_detail_to_curriculum_agent():
    orchestrator = _academic_programs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        "BIL203 dersinin AKTS'si ve on kosulu nedir?",
        metadata={
            "capability_planner": {
                "action": {"capability": "course.detail", "params": {"topic": "BIL203"}}
            },
            "source_owner": {"primary": "curriculum_catalog"},
        },
    )

    assert decision.agent.agent_id == "curriculum_agent"


def test_registry_routes_international_policy_to_international_agent():
    orchestrator = _academic_programs_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.PROCEDURE_QUERY,
        "Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?",
        metadata={
            "capability_planner": {
                "action": {"capability": "international.policy_lookup"}
            },
            "source_owner": {"primary": "international_policy"},
        },
    )

    assert decision.agent.agent_id == "international_agent"


def test_legacy_keyword_is_used_only_when_no_contract_or_task_type_candidate():
    orchestrator = _student_affairs_orchestrator()

    decision = orchestrator._select_agent_decision(
        None,
        "Staj basvurusu nasil yapilir?",
        metadata={},
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == "internship_agent"
    assert metadata["selected_by"] == "legacy_keyword_fallback"
    assert metadata["legacy_keyword"]["used_as_fallback"] is True


def test_source_owner_overrides_task_type_and_keyword_for_finance():
    orchestrator = _finance_orchestrator()

    decision = orchestrator._select_agent_decision(
        TaskType.SCHOLARSHIP_QUERY,
        "Burs uygunluk bilgisini ogrenebilir miyim?",
        metadata={
            "source_owner": {"primary": "tuition_fee_catalog"},
            "decision_contract": {
                "contract": {
                    "source_owner": {"primary": "tuition_fee_catalog"},
                    "capabilities": {"selected": None},
                }
            },
        },
    )

    metadata = decision.to_metadata()
    assert decision.agent.agent_id == "tuition_agent"
    assert metadata["selected_by"] == "contract"
    assert metadata["task_type"]["agent_id"] == "scholarship_agent"
    assert metadata["legacy_keyword"]["agent_id"] == "scholarship_agent"
    assert metadata["legacy_keyword"]["matches_selected"] is False
