"""Her uzman ajan icin kapsamli birim testleri.

Test edilen ajanlar:
  1. RegistrationAgent   – zamanlama sorgusu, donem bilgisi
  2. GraduationAgent     – kisisel, hibrit, genel sorgu
  3. InternshipAgent     – alt konu tespiti (staj/bitirme/mup/sanayi), capraz referans
  4. StudentLifeAgent    – RAG tabanli genel yanit
  5. CurriculumAgent     – onkosul sorgusu + alias yonlendirme, ders listesi
  6. RegulationAgent     – belge referansli yanitlar
  7. InternationalAgent  – uluslararasi harc capraz yonlendirmesi
  8. TuitionAgent        – kisisel harc, auth kontrol, snapshot formatlama
  9. ScholarshipAgent    – kisisel burs, uygunluk kontrolu
 10. AnnouncementAgent   – duyuru getirme ve formatlama
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.a2a import extract_department_response
from src.agents.academic.agents import (
    CurriculumAgent,
    InternationalAgent,
    RegulationAgent,
)
from src.agents.announcement.agent import AnnouncementAgent
from src.agents.base import BaseSpecialistAgent
from src.agents.finance.agents import ScholarshipAgent, TuitionAgent
from src.agents.student.agents import (
    GraduationAgent,
    InternshipAgent,
    RegistrationAgent,
    StudentLifeAgent,
)
from src.core.constants import Department


# ──────────────────────────────────────────────────────────
# Yardimci fonksiyonlar
# ──────────────────────────────────────────────────────────

def _task(
    query: str,
    *,
    student_id: int | None = None,
    is_authenticated: bool = False,
    **extra_meta,
):
    meta = {"query_text": query, "student_id": student_id, "is_authenticated": is_authenticated}
    meta.update(extra_meta)
    return SimpleNamespace(
        id=f"test-task-{uuid4()}",
        contextId="test-context",
        metadata=meta,
        status=SimpleNamespace(message=None),
    )


def _mock_retriever_factory(
    *,
    content: str = "Ornek belge icerigi.",
    score: float = 0.85,
    metadata: dict | None = None,
):
    mock_retriever = MagicMock()
    payload_metadata = {"file_name": "test_source.pdf"}
    if metadata:
        payload_metadata.update(metadata)
    mock_retriever.search = MagicMock(return_value=[
        {
            "content": content,
            "source": "test_source.pdf",
            "score": score,
            "metadata": payload_metadata,
        }
    ])
    mock_retriever.enrich_results = MagicMock(side_effect=lambda results, department=None: results)
    return MagicMock(return_value=mock_retriever)


def _mock_llm():
    llm = MagicMock()
    llm.generate = AsyncMock(return_value="LLM tarafindan uretilen yanit.")
    llm.is_available = True
    return llm


def _agent_kwargs():
    return {
        "llm_service": _mock_llm(),
        "retriever_factory": _mock_retriever_factory(),
        "contact_fetcher": AsyncMock(return_value=[]),
    }


@pytest.fixture(autouse=True)
def _unwrap_a2a_responses(monkeypatch):
    """A2A handle_task kontratini mevcut DepartmentResponse testlerine uyarlar."""

    original_handle_task = BaseSpecialistAgent.handle_task

    async def _wrapped_handle_task(self, task):
        result = await original_handle_task(self, task)
        extracted = extract_department_response(result)
        return extracted or result

    monkeypatch.setattr(BaseSpecialistAgent, "handle_task", _wrapped_handle_task)


# ══════════════════════════════════════════════════════════
# 0. LLM Bypass Mekanizmasi (BaseSpecialistAgent)
# ══════════════════════════════════════════════════════════

_HIGH_SCORE_LONG_CONTENT = (
    "Kayit sureci hakkinda detayli bilgi: 2026-Bahar donemi kayitlari 10-21 Subat "
    "tarihleri arasinda yapilacaktir. Kayit icin gerekli belgeler..."
)
_VERY_LONG_SOURCE_CONTENT = (
    "Madde 5 - CAP basvuru, kabul ve kayit kosullari soyledir. "
    + ("Basvuru kosulu ayrintisi " * 65)
    + "SON-BOLUM-TAM-METIN"
)


class TestLLMBypassMechanism:
    """RAG skoru yeterliyse ve icerik yeterince uzunsa LLM bypass edilmeli."""

    @pytest.mark.asyncio
    async def test_high_score_long_content_bypasses_llm(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT, score=0.85,
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Kayit nasil yapilir?"))

        assert response.success is True
        assert _HIGH_SCORE_LONG_CONTENT in response.answer
        llm.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_high_score_long_content_is_not_truncated_in_direct_rag_answer(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_VERY_LONG_SOURCE_CONTENT, score=0.85,
        )

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("CAP basvurusu nasil yapilir?"))

        assert response.success is True
        assert "SON-BOLUM-TAM-METIN" in response.answer
        assert "(Kaynak: test_source.pdf)" in response.answer

    @pytest.mark.asyncio
    async def test_high_reranker_score_allows_direct_rag_answer(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT,
            score=0.82,
            metadata={"score_type": "reranker"},
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("CAP basvuru kosullari nelerdir?"))

        assert response.success is True
        assert _HIGH_SCORE_LONG_CONTENT in response.answer
        llm.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_low_reranker_score_falls_back_to_llm(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT,
            score=0.30,
            metadata={"score_type": "reranker"},
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("CAP basvuru kosullari nelerdir?"))

        assert response.success is True
        llm.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_retrieval_score_uses_lower_direct_threshold(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT,
            score=0.30,
            metadata={"score_type": "retrieval"},
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Kayit adimlari nelerdir?"))

        assert response.success is True
        assert _HIGH_SCORE_LONG_CONTENT in response.answer
        llm.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_low_score_falls_back_to_llm(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT, score=0.20,
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Kayit nasil yapilir?"))

        assert response.success is True
        llm.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_short_content_falls_back_to_llm(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content="Kisa bilgi.", score=0.90,
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Kayit nasil yapilir?"))

        assert response.success is True
        llm.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_force_llm_skips_bypass(self):
        """GraduationAgent hybrid sorgusu force_llm=True kullanir."""
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT, score=0.95,
        )
        llm = kwargs["llm_service"]
        snapshot = TestGraduationAgent._SNAPSHOT

        agent = GraduationAgent(
            academic_fetcher=AsyncMock(return_value=snapshot), **kwargs,
        )
        response = await agent.handle_task(
            _task("Mezun olabilir miyim?", student_id=9, is_authenticated=True),
        )

        assert response.success is True
        llm.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_llm_failure_fallback_keeps_full_source_chunk(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_VERY_LONG_SOURCE_CONTENT, score=0.20,
        )
        llm = kwargs["llm_service"]
        llm.generate = AsyncMock(side_effect=asyncio.TimeoutError())

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("CAP basvurusu nasil yapilir?"))

        assert response.success is True
        assert "Eldeki en ilgili kaynakta su bilgi yer aliyor:" in response.answer
        assert "SON-BOLUM-TAM-METIN" in response.answer

    @pytest.mark.asyncio
    async def test_specialist_llm_prompt_limits_source_chunk_only_in_prompt(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_VERY_LONG_SOURCE_CONTENT, score=0.20,
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("CAP basvurusu nasil yapilir?"))

        assert response.success is True
        llm.generate.assert_awaited_once()
        prompt = llm.generate.await_args.kwargs["prompt"]
        assert "Madde 5 - CAP basvuru, kabul ve kayit kosullari" in prompt
        assert "SON-BOLUM-TAM-METIN" not in prompt
        assert "..." in prompt

    @pytest.mark.asyncio
    async def test_contact_request_falls_back_to_department_contacts(self):
        kwargs = _agent_kwargs()
        kwargs["contact_fetcher"] = AsyncMock(
            side_effect=[
                [],
                [
                    SimpleNamespace(
                        unit_name="Program Isleri Ofisi",
                        person_name="Ayse Kaya",
                        title="Uzman",
                        phone_ext="7304",
                        email="program.isleri@omu.edu.tr",
                    )
                ],
            ]
        )

        agent = RegulationAgent(**kwargs)
        response = await agent.handle_task(_task("Iletisim bilgisi"))

        assert response.success is True
        assert "Program Isleri Ofisi" in response.answer
        assert "program.isleri@omu.edu.tr" in response.answer
        assert kwargs["contact_fetcher"].await_count == 2


# ══════════════════════════════════════════════════════════
# 1. RegistrationAgent
# ══════════════════════════════════════════════════════════

class TestRegistrationAgent:

    @pytest.mark.asyncio
    async def test_timing_query_injects_period_info(self):
        period = SimpleNamespace(
            semester="2026-Bahar",
            start_date=datetime(2026, 2, 10, tzinfo=timezone.utc),
            end_date=datetime(2026, 2, 21, tzinfo=timezone.utc),
            is_active=True,
            timing_status="active",
        )
        agent = RegistrationAgent(
            period_fetcher=AsyncMock(return_value=period),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(_task("Ders kaydi ne zaman basliyor?"))

        assert response.success is True
        assert "2026-Bahar" in response.answer
        assert "10.02.2026" in response.answer

    @pytest.mark.asyncio
    async def test_non_timing_query_skips_period_lookup(self):
        fetcher = AsyncMock(return_value=None)
        agent = RegistrationAgent(period_fetcher=fetcher, **_agent_kwargs())

        response = await agent.handle_task(_task("Yatay gecis nasil yapilir?"))

        assert response.success is True
        fetcher.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_timing_query_when_no_active_period(self):
        agent = RegistrationAgent(
            period_fetcher=AsyncMock(return_value=None),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(_task("Kayit tarihleri ne zaman?"))

        assert response.success is True
        assert "2026-Bahar" not in response.answer

    @pytest.mark.asyncio
    async def test_timing_query_reports_upcoming_period_honestly(self):
        period = SimpleNamespace(
            semester="2026-Guz",
            start_date=datetime(2026, 8, 26, tzinfo=timezone.utc),
            end_date=datetime(2026, 9, 6, tzinfo=timezone.utc),
            is_active=False,
            timing_status="upcoming",
        )
        agent = RegistrationAgent(
            period_fetcher=AsyncMock(return_value=period),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(_task("Kayit tarihleri ne zaman?"))

        assert response.success is True
        assert "planlanmistir" in response.answer
        assert "2026-Guz" in response.answer

    def test_source_only_answer_keeps_full_preferred_chunk(self):
        agent = RegistrationAgent(**_agent_kwargs())

        answer = agent._build_source_only_answer(
            "Yatay gecis nasil yapilir?",
            [
                {
                    "content": _VERY_LONG_SOURCE_CONTENT,
                    "source": "yonerge.pdf",
                    "score": 0.91,
                    "metadata": {"file_name": "yonerge.pdf"},
                }
            ],
        )

        assert "SON-BOLUM-TAM-METIN" in answer
        assert "(Kaynak: yonerge.pdf)" in answer


# ══════════════════════════════════════════════════════════
# 2. GraduationAgent
# ══════════════════════════════════════════════════════════

class TestGraduationAgent:

    _SNAPSHOT = {
        "student_id": 9,
        "student_name": "Mehmet Kaya",
        "gpa": 3.10,
        "completed_credits": 140,
        "total_credits": 240,
        "registration_status": "active",
        "recent_courses": [
            {
                "course_code": "BIL400",
                "course_name": "Bitirme Projesi",
                "semester": "2026-Bahar",
                "grade": "BA",
                "status": "completed",
            }
        ],
    }

    @pytest.mark.asyncio
    async def test_personal_query_returns_academic_snapshot(self):
        agent = GraduationAgent(
            academic_fetcher=AsyncMock(return_value=self._SNAPSHOT),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("GNO'm kac?", student_id=9, is_authenticated=True)
        )

        assert response.success is True
        assert "GNO: 3.10" in response.answer
        assert "BIL400" in response.answer

    @pytest.mark.asyncio
    async def test_personal_query_requires_auth(self):
        agent = GraduationAgent(
            academic_fetcher=AsyncMock(),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Notlarim nasil?", student_id=9, is_authenticated=False)
        )

        assert response.success is False
        assert response.error == "authentication_required"

    @pytest.mark.asyncio
    async def test_hybrid_query_combines_db_and_rag(self):
        agent = GraduationAgent(
            academic_fetcher=AsyncMock(return_value=self._SNAPSHOT),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Mezun olabilir miyim?", student_id=9, is_authenticated=True)
        )

        assert response.success is True
        assert response.db_data is not None
        assert response.sources is not None

    @pytest.mark.asyncio
    async def test_general_query_uses_rag(self):
        agent = GraduationAgent(
            academic_fetcher=AsyncMock(),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(_task("Mezuniyet sarti nedir?"))

        assert response.success is True


# ══════════════════════════════════════════════════════════
# 3. InternshipAgent
# ══════════════════════════════════════════════════════════

class TestInternshipAgent:

    @pytest.mark.asyncio
    async def test_general_query_uses_rag_and_bypass(self):
        agent = InternshipAgent(**_agent_kwargs())

        response = await agent.handle_task(
            _task("Staj basvurusu nasil yapilir?")
        )

        assert response.success is True
        assert response.department == Department.STUDENT_AFFAIRS

    @pytest.mark.asyncio
    async def test_cross_reference_to_finance_for_fee_queries(self):
        agent = InternshipAgent(**_agent_kwargs())

        response = await agent.handle_task(
            _task("Staj ucreti geri odemesi nasil yapilir?")
        )

        assert response.success is True
        assert "finans birimi" in response.answer.lower() or "scholarship_agent" in response.answer

    @pytest.mark.asyncio
    async def test_no_cross_reference_for_general_queries(self):
        agent = InternshipAgent(**_agent_kwargs())

        response = await agent.handle_task(
            _task("Staj suresi kac gun?")
        )

        assert response.success is True
        assert "scholarship_agent" not in response.answer


# ══════════════════════════════════════════════════════════
# 4. StudentLifeAgent
# ══════════════════════════════════════════════════════════

class TestStudentLifeAgent:

    @pytest.mark.asyncio
    async def test_general_query_returns_rag_response(self):
        agent = StudentLifeAgent(**_agent_kwargs())

        response = await agent.handle_task(
            _task("Ogrenci topluluguna nasil katilirim?")
        )

        assert response.success is True
        assert response.department == Department.STUDENT_AFFAIRS


# ══════════════════════════════════════════════════════════
# 5. CurriculumAgent
# ══════════════════════════════════════════════════════════

class TestCurriculumAgent:

    @pytest.mark.asyncio
    async def test_prerequisite_query_fetches_from_db(self):
        prereq_data = {
            "course_code": "BIL204",
            "course_name": "Algoritmalar",
            "credits": 3,
            "akts": 6,
            "prerequisites": [
                {"course_code": "BIL203", "course_name": "Veri Yapilari", "group": 1}
            ],
            "prerequisite_groups": {
                1: [{"course_code": "BIL203", "course_name": "Veri Yapilari", "group": 1}]
            },
            "redirected_from": None,
        }
        agent = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=prereq_data),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("BIL204 onkosulu ne?")
        )

        assert response.success is True
        assert response.db_data is not None

    @pytest.mark.asyncio
    async def test_prerequisite_alias_redirect(self):
        prereq_data = {
            "course_code": "TBMAT112",
            "course_name": "Matematik 2",
            "credits": 3,
            "akts": 5,
            "prerequisites": [
                {"course_code": "TBMAT111", "course_name": "Matematik 1", "group": 1}
            ],
            "prerequisite_groups": {
                1: [{"course_code": "TBMAT111", "course_name": "Matematik 1", "group": 1}]
            },
            "redirected_from": "TBMAT102",
        }
        agent = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=prereq_data),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("TBMAT102 onkosulu nedir?")
        )

        assert response.success is True
        assert "TBMAT102" in response.db_data.get("redirected_from", "")

    @pytest.mark.asyncio
    async def test_course_list_query_fetches_active_period(self):
        period = SimpleNamespace(semester="2026-Bahar")
        courses = [
            {"course_code": "BIL101", "course_name": "Bil. Muh. Giris", "credits": 3, "akts": 5},
            {"course_code": "BIL103", "course_name": "Programlamaya Giris I", "credits": 3, "akts": 5},
        ]
        agent = CurriculumAgent(
            period_fetcher=AsyncMock(return_value=period),
            course_fetcher=AsyncMock(return_value=courses),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Bu donem hangi dersler acik?", student_department="Bilgisayar Muhendisligi")
        )

        assert response.success is True

    @pytest.mark.asyncio
    async def test_general_query_falls_through_to_rag(self):
        agent = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=None),
            period_fetcher=AsyncMock(return_value=None),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Mufredat hakkinda bilgi ver", student_department="Bilgisayar Muhendisligi")
        )

        assert response.success is True


# ══════════════════════════════════════════════════════════
# 6. RegulationAgent
# ══════════════════════════════════════════════════════════

class TestRegulationAgent:

    @pytest.mark.asyncio
    async def test_returns_document_referenced_answer(self):
        agent = RegulationAgent(**_agent_kwargs())

        response = await agent.handle_task(
            _task("Sinav yonetmeligi ne diyor?")
        )

        assert response.success is True
        assert response.sources is not None

    def test_source_only_answer_keeps_full_preferred_chunk(self):
        agent = RegulationAgent(**_agent_kwargs())

        answer = agent._build_source_only_answer(
            "CAP yonergesi ne diyor?",
            [
                {
                    "content": _VERY_LONG_SOURCE_CONTENT,
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "score": 0.93,
                    "metadata": {"file_name": "yonerge_cift_anadal_yandal.pdf"},
                }
            ],
        )

        assert "SON-BOLUM-TAM-METIN" in answer
        assert "(Kaynak: yonerge_cift_anadal_yandal.pdf)" in answer

    @pytest.mark.asyncio
    async def test_no_results_returns_guidance(self):
        kwargs = _agent_kwargs()
        mock_retriever = MagicMock()
        mock_retriever.search = MagicMock(return_value=[])
        kwargs["retriever_factory"] = MagicMock(return_value=mock_retriever)

        agent = RegulationAgent(**kwargs)

        response = await agent.handle_task(
            _task("Cok belirsiz bir kural sorusu")
        )

        assert response.success is True
        assert "bulunamadi" in response.answer.lower() or "mevzuat" in response.answer.lower()


# ══════════════════════════════════════════════════════════
# 7. InternationalAgent
# ══════════════════════════════════════════════════════════

class TestInternationalAgent:

    @pytest.mark.asyncio
    async def test_international_tuition_query_adds_finance_reference(self):
        agent = InternationalAgent(**_agent_kwargs())

        response = await agent.handle_task(
            _task("Uluslararasi ogrenci harc ucreti ne kadar?")
        )

        assert response.success is True
        assert "finans birimi" in response.answer.lower() or "tuition_agent" in response.answer

    @pytest.mark.asyncio
    async def test_general_international_query_no_finance_ref(self):
        agent = InternationalAgent(**_agent_kwargs())

        response = await agent.handle_task(
            _task("Erasmus basvurusu nasil yapilir?")
        )

        assert response.success is True
        assert "tuition_agent" not in response.answer


# ══════════════════════════════════════════════════════════
# 8. TuitionAgent
# ══════════════════════════════════════════════════════════

class TestTuitionAgent:

    _SNAPSHOT_WITH_DEBT = {
        "student_id": 7,
        "student_name": "Ahmet Yilmaz",
        "tuition": {
            "semester": "2026-Bahar",
            "total_amount": 15000.0,
            "paid_amount": 10000.0,
            "has_debt": True,
            "debt_amount": 5000.0,
            "due_date": "2026-03-31",
            "last_payment_date": None,
        },
    }

    _SNAPSHOT_PAID = {
        "student_id": 7,
        "student_name": "Ahmet Yilmaz",
        "tuition": {
            "semester": "2026-Bahar",
            "total_amount": 12000.0,
            "paid_amount": 12000.0,
            "has_debt": False,
            "debt_amount": 0.0,
            "due_date": "2026-03-31",
            "last_payment_date": "2026-02-10",
        },
    }

    @pytest.mark.asyncio
    async def test_personal_query_shows_debt_info(self):
        agent = TuitionAgent(
            tuition_fetcher=AsyncMock(return_value=self._SNAPSHOT_WITH_DEBT),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Harc borcum ne kadar?", student_id=7, is_authenticated=True)
        )

        assert response.success is True
        assert "5000.00 TL borc" in response.answer

    @pytest.mark.asyncio
    async def test_personal_query_shows_paid_info(self):
        agent = TuitionAgent(
            tuition_fetcher=AsyncMock(return_value=self._SNAPSHOT_PAID),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Odeme durumum nedir?", student_id=7, is_authenticated=True)
        )

        assert response.success is True
        assert "kapanmis" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_requires_auth_for_personal_query(self):
        agent = TuitionAgent(tuition_fetcher=AsyncMock(), **_agent_kwargs())

        response = await agent.handle_task(
            _task("Borcum var mi?", student_id=7, is_authenticated=False)
        )

        assert response.success is False
        assert response.error == "authentication_required"

    @pytest.mark.asyncio
    async def test_student_not_found(self):
        agent = TuitionAgent(
            tuition_fetcher=AsyncMock(return_value=None),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Taksitlerimi goster", student_id=999, is_authenticated=True)
        )

        assert response.success is False
        assert response.error == "student_not_found"

    @pytest.mark.asyncio
    async def test_general_tuition_query_uses_rag(self):
        agent = TuitionAgent(tuition_fetcher=AsyncMock(), **_agent_kwargs())

        response = await agent.handle_task(
            _task("Harc ucretleri ne kadar?")
        )

        assert response.success is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize("query", ["Kayit yenileme ucreti ne kadar?", "Kayıt yenileme ücreti ne kadar?"])
    async def test_structured_fee_query_uses_catalog_without_breaking_source_extension(
        self,
        query,
        monkeypatch,
    ):
        async def _fake_catalog_lookup(*, student_type, unit_name, academic_year=None):
            assert student_type == "international"
            return {
                "academic_year": "2025-2026",
                "student_type": "international",
                "unit_name": "Mühendislik Fakültesi",
                "annual_amount": 47000.0,
                "semester_amount": 23500.0,
                "currency": "TRY",
                "source_document": "uluslararasi_ucretler.pdf",
            }

        monkeypatch.setattr(
            "src.agents.finance.tuition_agent.fetch_tuition_fee_catalog_entry",
            _fake_catalog_lookup,
        )

        agent = TuitionAgent(tuition_fetcher=AsyncMock(), **_agent_kwargs())
        response = await agent.handle_task(
            _task(
                query,
                student_type="Uluslararasi ogrenci",
                student_faculty="Muhendislik Fakultesi",
            )
        )

        assert response.success is True
        assert "47.000,00 TL" in response.answer
        assert "23.500,00 TL" in response.answer
        assert "uluslararasi_ucretler.pdf" in response.answer


# ══════════════════════════════════════════════════════════
# 9. ScholarshipAgent
# ══════════════════════════════════════════════════════════

class TestScholarshipAgent:

    _SNAPSHOT = {
        "student_id": 8,
        "student_name": "Ayse Demir",
        "gpa": 3.40,
        "scholarship": {
            "program_name": "Basari Bursu",
            "monthly_amount": 1500.0,
            "status": "active",
            "start_date": "2025-10-01",
            "end_date": None,
        },
        "latest_application": {
            "program_name": "Basari Bursu",
            "status": "approved",
            "application_date": "2025-09-15",
        },
    }

    @pytest.mark.asyncio
    async def test_personal_query_shows_scholarship_info(self):
        agent = ScholarshipAgent(
            scholarship_fetcher=AsyncMock(return_value=self._SNAPSHOT),
            eligibility_fetcher=AsyncMock(return_value=[]),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Burs durumum ne?", student_id=8, is_authenticated=True)
        )

        assert response.success is True
        assert "Basari Bursu" in response.answer
        assert "GNO: 3.40" in response.answer

    @pytest.mark.asyncio
    async def test_eligibility_check_appends_eligible_scholarships(self):
        eligible = [
            {"name": "Ozel Burs", "monthly_amount": 2000, "min_gpa": 3.0, "deadline": "2026-04-01"},
        ]
        agent = ScholarshipAgent(
            scholarship_fetcher=AsyncMock(return_value=self._SNAPSHOT),
            eligibility_fetcher=AsyncMock(return_value=eligible),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Bursum var mi?", student_id=8, is_authenticated=True)
        )

        assert response.success is True
        assert "Ozel Burs" in response.answer

    @pytest.mark.asyncio
    async def test_requires_auth(self):
        agent = ScholarshipAgent(
            scholarship_fetcher=AsyncMock(),
            eligibility_fetcher=AsyncMock(return_value=[]),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Basvurum ne durumda?", student_id=8, is_authenticated=False)
        )

        assert response.success is False
        assert response.error == "authentication_required"


# ══════════════════════════════════════════════════════════
# 10. AnnouncementAgent
# ══════════════════════════════════════════════════════════

class TestAnnouncementAgent:

    @pytest.mark.asyncio
    async def test_returns_formatted_announcements(self):
        announcements = [
            SimpleNamespace(
                id=1,
                title="Ders Kayit Tarihleri Aciklandi",
                summary="2026-Bahar donemi ders kayit tarihleri 10-21 Subat olarak belirlenmistir.",
                original_text=None,
                source_url="https://omu.edu.tr/duyuru/1",
                faculty="Muhendislik",
                department="Bilgisayar Muhendisligi",
                published_at=datetime(2026, 1, 5, tzinfo=timezone.utc),
            ),
        ]
        agent = AnnouncementAgent(
            announcement_fetcher=AsyncMock(return_value=announcements),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Son duyurular neler?")
        )

        assert response.success is True
        assert "Ders Kayit Tarihleri" in response.answer
        assert len(response.sources) == 1
        assert response.sources[0].metadata["record_type"] == "announcement"

    @pytest.mark.asyncio
    async def test_no_announcements_returns_guidance(self):
        agent = AnnouncementAgent(
            announcement_fetcher=AsyncMock(return_value=[]),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Son duyurular neler?")
        )

        assert response.success is True
        assert "duyuru bulunmuyor" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_long_summary_truncated(self):
        long_text = "A" * 500
        announcements = [
            SimpleNamespace(
                id=2,
                title="Test",
                summary=long_text,
                original_text=None,
                source_url=None,
                faculty=None,
                department=None,
                published_at=None,
            ),
        ]
        agent = AnnouncementAgent(
            announcement_fetcher=AsyncMock(return_value=announcements),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(_task("Duyurular?"))

        assert response.success is True
        assert "..." in response.answer
