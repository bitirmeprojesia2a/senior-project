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
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

import src.agents.base as base_module
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


def test_answer_completeness_and_evidence_boost_normalize_turkish_text():
    assert (
        BaseSpecialistAgent._check_answer_completeness(
            "Ne kadar süre var?",
            "Başvuru beş gün içerisinde yapılır.",
        )
        is None
    )

    results = [{"content": "Basvuru suresi bes gun icerisindedir.", "score": 0.10}]

    boosted = BaseSpecialistAgent._apply_evidence_boost("Basvuru tarihi ne zaman?", results)

    assert boosted[0]["score"] > 0.10


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


def _mock_retriever_factory_with_results(results: list[dict]):
    mock_retriever = MagicMock()
    mock_retriever.search = MagicMock(return_value=results)
    mock_retriever.enrich_results = MagicMock(side_effect=lambda items, department=None: items)
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
# 0. LLM-first sentez mekanizmasi (BaseSpecialistAgent)
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


class TestLLMFirstSynthesisMechanism:
    """RAG skoru yeterliyse son cevap LLM tarafindan sentezlenmeli."""

    @pytest.mark.asyncio
    async def test_remote_retrieval_local_fallback_is_shared(self, monkeypatch):
        class _FailingRemoteRetriever:
            def search(self, *args, **kwargs):
                raise RuntimeError("remote down")

        class _FakeLocalRetriever:
            instances = 0

            def __init__(self):
                type(self).instances += 1

            def search(self, *args, **kwargs):
                return [
                    {
                        "content": _HIGH_SCORE_LONG_CONTENT,
                        "source": "fallback.pdf",
                        "score": 0.9,
                        "metadata": {"file_name": "fallback.pdf"},
                    }
                ]

            def enrich_results(self, results, department=None):
                return results

        monkeypatch.setattr(base_module.settings.retrieval_service, "enabled", True)
        monkeypatch.setattr(base_module.settings.retrieval_service, "fallback_to_local", True)
        monkeypatch.setattr("src.rag.retriever.HybridRetriever", _FakeLocalRetriever)
        monkeypatch.setattr(base_module, "_SHARED_LOCAL_FALLBACK_RETRIEVER", None)

        agent = StudentLifeAgent(
            llm_service=_mock_llm(),
            retriever_factory=MagicMock(return_value=_FailingRemoteRetriever()),
            contact_fetcher=AsyncMock(return_value=[]),
        )

        first = await agent.handle_task(_task("Kayit nasil yapilir?"))
        second = await agent.handle_task(_task("Kayit nasil yapilir?"))

        assert first.success is True
        assert second.success is True
        assert _FakeLocalRetriever.instances == 1

    @pytest.mark.asyncio
    async def test_remote_enrich_local_fallback_is_shared(self, monkeypatch):
        class _PartiallyFailingRemoteRetriever:
            def search(self, *args, **kwargs):
                return [
                    {
                        "content": "Remote search sonucu.",
                        "source": "remote.pdf",
                        "score": 0.9,
                        "metadata": {"file_name": "remote.pdf"},
                    }
                ]

            def enrich_results(self, *args, **kwargs):
                raise RuntimeError("remote enrich down")

        class _FakeLocalRetriever:
            instances = 0

            def __init__(self):
                type(self).instances += 1

            def enrich_results(self, results, department=None):
                return [
                    {
                        **results[0],
                        "content": f"{_HIGH_SCORE_LONG_CONTENT} Local enrich.",
                    }
                ]

        monkeypatch.setattr(base_module.settings.retrieval_service, "enabled", True)
        monkeypatch.setattr(base_module.settings.retrieval_service, "fallback_to_local", True)
        monkeypatch.setattr("src.rag.retriever.HybridRetriever", _FakeLocalRetriever)
        monkeypatch.setattr(base_module, "_SHARED_LOCAL_FALLBACK_RETRIEVER", None)

        agent = StudentLifeAgent(
            llm_service=_mock_llm(),
            retriever_factory=MagicMock(return_value=_PartiallyFailingRemoteRetriever()),
            contact_fetcher=AsyncMock(return_value=[]),
        )

        response = await agent.handle_task(_task("Kayit nasil yapilir?"))

        assert response.success is True
        assert response.answer == "LLM tarafindan uretilen yanit."
        assert "Local enrich" in response.sources[0].content
        assert _FakeLocalRetriever.instances == 1

    @pytest.mark.asyncio
    async def test_high_score_long_content_uses_llm_synthesis(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT, score=0.85,
        )
        llm = kwargs["llm_service"]
        llm.generate.return_value = "LLM sentezli kayit yaniti."

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Kayit nasil yapilir?"))

        assert response.success is True
        assert response.answer == "LLM sentezli kayit yaniti."
        llm.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_llm_failure_fallback_keeps_high_score_long_content(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_VERY_LONG_SOURCE_CONTENT, score=0.85,
        )
        kwargs["llm_service"].generate = AsyncMock(side_effect=asyncio.TimeoutError())

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("CAP basvurusu nasil yapilir?"))

        assert response.success is True
        assert "SON-BOLUM-TAM-METIN" in response.answer
        assert "(Kaynak: test_source.pdf)" in response.answer

    @pytest.mark.asyncio
    async def test_high_reranker_score_uses_llm_synthesis(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=(
                "CAP basvuru kosullari icin ogrencinin ana dal programindaki "
                "basarisini surdurmesi, ilgili yonerge kosullarini saglamasi ve "
                "basvurunun akademik takvimde ilan edilen surede yapilmasi gerekir."
            ),
            score=0.82,
            metadata={"score_type": "reranker"},
        )
        llm = kwargs["llm_service"]
        llm.generate.return_value = "LLM sentezli CAP yaniti."

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("CAP basvuru kosullari nelerdir?"))

        assert response.success is True
        assert response.answer == "LLM sentezli CAP yaniti."
        llm.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_evidence_selector_enabled_runs_before_llm_synthesis(self, monkeypatch):
        monkeypatch.setattr(base_module.settings.rag, "llm_evidence_selection_enabled", True)
        monkeypatch.setattr(base_module.settings.rag, "llm_evidence_selection_min_candidates", 4)

        results = [
            {
                "content": f"{_HIGH_SCORE_LONG_CONTENT} {index}",
                "source": f"source_{index}.pdf",
                "score": 0.85 - (index * 0.01),
                "metadata": {"score_type": "reranker", "file_name": f"source_{index}.pdf"},
            }
            for index in range(4)
        ]
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory_with_results(results)
        llm = kwargs["llm_service"]
        llm.generate.side_effect = [
            json.dumps({"selected_ids": ["source_1.pdf"], "ranking": []}),
            "LLM selector sonrasi sentez.",
        ]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("CAP basvuru kosullari nelerdir?"))

        assert response.success is True
        assert response.answer == "LLM selector sonrasi sentez."
        assert llm.generate.await_count == 2
        assert llm.generate.await_args_list[0].kwargs["model_role"] == "evidence_selection"
        assert llm.generate.await_args_list[1].kwargs["model_role"] == "specialist_synthesis"

    @pytest.mark.asyncio
    async def test_registration_course_process_keeps_synthesis_but_skips_selector(self, monkeypatch):
        monkeypatch.setattr(base_module.settings.rag, "llm_evidence_selection_enabled", True)
        monkeypatch.setattr(base_module.settings.rag, "llm_evidence_selection_min_candidates", 4)

        results = [
            {
                "content": (
                    "Ders kaydi akademik takvimde belirtilen sure icinde "
                    "ubys.omu.edu.tr adresinden yapilir. Danisman onayi "
                    "tamamlandiktan sonra kayit gecerli olur."
                ),
                "source": f"sik_sorulan_sorular_{index}.txt",
                "score": 0.85 - (index * 0.01),
                "metadata": {"score_type": "reranker", "file_name": f"sik_sorulan_sorular_{index}.txt"},
            }
            for index in range(6)
        ]
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory_with_results(results)
        llm = kwargs["llm_service"]
        llm.generate.return_value = "Ders kaydi LLM sentezi."

        agent = RegistrationAgent(**kwargs)
        response = await agent.handle_task(_task("Ders kaydi nasil yapilir?"))

        assert response.success is True
        assert response.answer == "Ders kaydi LLM sentezi."
        assert llm.generate.await_count == 1
        assert llm.generate.await_args.kwargs["model_role"] == "specialist_synthesis"

    @pytest.mark.asyncio
    async def test_registration_course_process_skips_result_enrichment(self):
        results = [
            {
                "content": (
                    "Ders kaydi akademik takvimde belirtilen sure icinde "
                    "ubys.omu.edu.tr adresinden yapilir."
                ),
                "source": "sik_sorulan_sorular.txt",
                "score": 0.86,
                "metadata": {"score_type": "reranker", "file_name": "sik_sorulan_sorular.txt"},
            }
        ]
        retriever_factory = _mock_retriever_factory_with_results(results)
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = retriever_factory
        kwargs["llm_service"].generate.return_value = "Ders kaydi LLM sentezi."

        agent = RegistrationAgent(**kwargs)
        response = await agent.handle_task(_task("Ders kaydi nasil yapilir?"))

        assert response.success is True
        assert response.answer == "Ders kaydi LLM sentezi."
        retriever_factory.return_value.enrich_results.assert_not_called()
        assert agent._llm_synthesis_timeout_seconds(
            "Ders kaydi nasil yapilir?",
            results,
        ) == 4.0

    def test_registration_course_process_source_only_fallback_is_clean(self):
        agent = RegistrationAgent(**_agent_kwargs())
        answer = agent._build_source_only_answer("Ders kaydi nasil yapilir?", [])

        assert "ubys.omu.edu.tr" in answer
        assert "Kaynak:" in answer
        assert "GANO" not in answer

    @pytest.mark.asyncio
    async def test_registration_short_grade_objection_skips_result_enrichment(self):
        results = [
            {
                "content": "Sinav sonuclarina bes is gunu icinde bolum baskanligina dilekce ile itiraz edilir.",
                "source": "sik_sorulan_sorular.txt",
                "score": 0.86,
                "metadata": {"score_type": "reranker", "file_name": "sik_sorulan_sorular.txt"},
            }
        ]
        retriever_factory = _mock_retriever_factory_with_results(results)
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = retriever_factory
        kwargs["llm_service"].generate.return_value = "Not itirazi LLM sentezi."

        agent = RegistrationAgent(**kwargs)
        response = await agent.handle_task(_task("Sinav notuma nasil itiraz ederim?"))

        assert response.success is True
        retriever_factory.return_value.enrich_results.assert_not_called()

    @pytest.mark.asyncio
    async def test_registration_withdrawal_skips_result_enrichment(self):
        results = [
            {
                "content": "Kayit sildirme icin UBYS uzerinden ilisik kesme talebi baslatilabilir.",
                "source": "sik_sorulan_sorular.txt",
                "score": 0.86,
                "metadata": {"score_type": "reranker", "file_name": "sik_sorulan_sorular.txt"},
            }
        ]
        retriever_factory = _mock_retriever_factory_with_results(results)
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = retriever_factory
        kwargs["llm_service"].generate.return_value = "Ilisik kesme LLM sentezi."

        agent = RegistrationAgent(**kwargs)
        response = await agent.handle_task(_task("Universiteyi birakmak istiyorum ne yapmaliyim?"))

        assert response.success is True
        retriever_factory.return_value.enrich_results.assert_not_called()

    @pytest.mark.asyncio
    async def test_internship_simple_form_query_skips_result_enrichment(self):
        results = [
            {
                "content": "Zorunlu staj formu bolum web sayfasindan veya OMU Kalem formlarindan alinabilir.",
                "source": "staj_sikca_sorulanlar.pdf",
                "score": 0.86,
                "metadata": {"score_type": "reranker", "file_name": "staj_sikca_sorulanlar.pdf"},
            }
        ]
        retriever_factory = _mock_retriever_factory_with_results(results)
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = retriever_factory
        kwargs["llm_service"].generate.return_value = "Staj formu LLM sentezi."

        agent = InternshipAgent(**kwargs)
        response = await agent.handle_task(_task("Zorunlu staj formunu nereden alirim?"))

        assert response.success is True
        retriever_factory.return_value.enrich_results.assert_not_called()

    @pytest.mark.asyncio
    async def test_regulation_simple_pedagogical_transcript_query_skips_result_enrichment(self):
        results = [
            {
                "content": "Pedagojik formasyon dersleri transkripte ve mezuniyet ortalamasina dahil edilir.",
                "source": "pedagojik_formasyon_sorular.txt",
                "score": 0.86,
                "metadata": {"score_type": "reranker", "file_name": "pedagojik_formasyon_sorular.txt"},
            }
        ]
        retriever_factory = _mock_retriever_factory_with_results(results)
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = retriever_factory
        kwargs["llm_service"].generate.return_value = "Formasyon LLM sentezi."

        agent = RegulationAgent(**kwargs)
        response = await agent.handle_task(_task("Pedagojik formasyon dersleri transkripte dahil mi?"))

        assert response.success is True
        retriever_factory.return_value.enrich_results.assert_not_called()

    @pytest.mark.asyncio
    async def test_low_reranker_score_still_reaches_llm_when_sources_exist(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT,
            score=0.05,
            metadata={"score_type": "reranker"},
        )
        llm = kwargs["llm_service"]
        llm.generate.return_value = "Dusuk skorlu kaynaklardan LLM sentezi."

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Yonetmelik maddesi uyarinca belirtilen tarihlere uymak zorunlu mu?"))

        assert response.success is True
        llm.generate.assert_awaited_once()
        assert response.answer == "Dusuk skorlu kaynaklardan LLM sentezi."

    @pytest.mark.asyncio
    async def test_retrieval_score_uses_llm_synthesis_when_reliable(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT,
            score=0.30,
            metadata={"score_type": "retrieval"},
        )
        llm = kwargs["llm_service"]
        llm.generate.return_value = "LLM sentezli retrieval yaniti."

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Kayit adimlari nelerdir?"))

        assert response.success is True
        assert response.answer == "LLM sentezli retrieval yaniti."
        llm.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_low_score_uses_llm_when_source_exists(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=_HIGH_SCORE_LONG_CONTENT, score=0.20,
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Yonetmelik maddesi uyarinca belirtilen tarihlere uymak zorunlu mu?"))

        assert response.success is True
        llm.generate.assert_awaited_once()
        assert response.answer == "LLM tarafindan uretilen yanit."

    @pytest.mark.asyncio
    async def test_short_content_falls_back_to_llm(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content="Kisa bilgi.", score=0.55,
        )
        llm = kwargs["llm_service"]

        agent = StudentLifeAgent(**kwargs)
        response = await agent.handle_task(_task("Kayit nasil yapilir?"))

        assert response.success is True
        # Cok kisa/alakasiz evidence hÃ¢lÃ¢ guvenlik icin LLM'e gonderilmez.
        llm.generate.assert_awaited_once()
        assert response.answer == "LLM tarafindan uretilen yanit."

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
        long_content = (
            "Madde 5 - CAP basvuru, kabul ve kayit kosullari soyledir. "
            + ("Basvuru kosulu ayrintisi " * 140)
            + "SON-BOLUM-TAM-METIN"
        )
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=long_content, score=0.20,
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
    async def test_general_final_exam_query_uses_academic_calendar_pdf(self):
        fetcher = AsyncMock(return_value=None)
        agent = RegistrationAgent(
            period_fetcher=fetcher,
            **_agent_kwargs(),
        )

        response = await agent.handle_task(_task("Final sinavlari ne zaman?"))

        assert response.success is True
        assert response.generation_mode == "vt"
        assert "03-16 Ocak 2026" in response.answer
        assert "01-14 Haziran 2026" in response.answer
        fetcher.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_final_exam_result_entry_deadline_uses_academic_calendar_pdf(self):
        fetcher = AsyncMock(return_value=None)
        agent = RegistrationAgent(
            period_fetcher=fetcher,
            **_agent_kwargs(),
        )

        response = await agent.handle_task(_task("Final sinavlarinin sisteme girilmesinin son gunu ne zaman?"))

        assert response.success is True
        assert response.generation_mode == "vt"
        assert "19 Ocak 2026" in response.answer
        assert "16 Haziran 2026" in response.answer
        assert "03-16 Ocak 2026" not in response.answer
        fetcher.assert_not_awaited()

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

    @pytest.mark.asyncio
    async def test_mixed_fee_and_timing_query_still_uses_registration_period_info(self):
        period = SimpleNamespace(
            semester="2026-Bahar",
            start_date=datetime(2026, 2, 10, tzinfo=timezone.utc),
            end_date=datetime(2026, 2, 21, tzinfo=timezone.utc),
            is_active=False,
            timing_status="upcoming",
        )
        fetcher = AsyncMock(return_value=period)
        kwargs = _agent_kwargs()
        llm = kwargs["llm_service"]
        agent = RegistrationAgent(
            period_fetcher=fetcher,
            **kwargs,
        )

        response = await agent.handle_task(
            _task("Kayit yenileme ucreti ne kadar ve ne zaman yapilir?")
        )

        assert response.success is True
        assert "2026-Bahar" in response.answer
        assert "10.02.2026" in response.answer
        fetcher.assert_awaited_once()
        llm.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_registration_process_after_payment_skips_period_lookup_and_uses_llm_when_forced(self):
        fetcher = AsyncMock(return_value=None)
        kwargs = _agent_kwargs()
        llm = kwargs["llm_service"]
        agent = RegistrationAgent(period_fetcher=fetcher, **kwargs)

        response = await agent.handle_task(
            _task(
                "Kayit yenileme doneminde harc ucretimi yatirdiktan sonra ders kaydini nasil yapacagim, danisman onay sureci nasil isliyor?",
                force_llm_synthesis=True,
            )
        )

        assert response.success is True
        fetcher.assert_not_awaited()
        llm.generate.assert_awaited_once()

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
        assert "tam transkript yerine gecmez" in response.answer

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

    @pytest.mark.asyncio
    async def test_teaching_program_staj_query_does_not_use_engineering_sources(self):
        kwargs = _agent_kwargs()
        llm = kwargs["llm_service"]
        agent = InternshipAgent(**kwargs)

        response = await agent.handle_task(
            _task("Matematik ogretmenligi okuyorum staj yapmam gerekiyor mu?")
        )

        assert response.success is True
        assert "net dogrulayamiyorum" in response.answer
        assert "muhendislik staj belgelerine gore" in response.answer
        assert response.generation_mode == "kural"
        llm.generate.assert_not_awaited()


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

    @pytest.mark.asyncio
    async def test_lost_identity_card_variants_use_llm_synthesis_with_policy_sources(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=(
                "Kartin kaybedilmesi halinde yeni kimlik basvurusu sirasinda kimlik ucreti "
                "yatirildigina dair dekont PP.4.7.FR.0163 Kimlik Karti Basvuru Formuna eklenir."
            ),
            score=0.88,
            metadata={"score_type": "reranker", "file_name": "kimlik_karti_yonergesi.pdf"},
        )
        llm = kwargs["llm_service"]
        llm.generate.return_value = (
            "Kimlik kartinizi kaybettiyseniz yeni kimlik karti basvurusu yapip "
            "dekontu PP.4.7.FR.0163 formuna eklemelisiniz."
        )
        agent = StudentLifeAgent(**kwargs)

        for query in (
            "Ogrenci kartimi kaybettim",
            "Ogrenci kimlik kartim kayip",
            "Ogrenciyim kimligim kayip",
        ):
            response = await agent.handle_task(_task(query))

            assert response.success is True
            assert "PP.4.7.FR.0163" in response.answer
            assert "dekont" in response.answer
            assert response.generation_mode == "rag+llm"

        assert llm.generate.await_count == 3


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
    async def test_curriculum_semester_query_infers_department_from_text(self):
        courses = [
            {
                "course_code": "MÖAE206",
                "course_name": "Lineer Cebir II",
                "credits": 2,
                "akts": 4,
                "department": "Matematik Öğretmenliği",
                "curriculum_semester": 4,
                "course_type": "zorunlu",
                "elective_group": None,
            }
        ]
        curriculum_fetcher = AsyncMock(return_value=courses)
        agent = CurriculumAgent(
            curriculum_course_fetcher=curriculum_fetcher,
            period_fetcher=AsyncMock(return_value=None),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Matematik Ogretmenligi 4. yariyil dersleri nelerdir?")
        )

        assert response.success is True
        assert "MÖAE206" in response.answer
        curriculum_fetcher.assert_awaited_once_with(4, "Matematik Öğretmenliği")

    @pytest.mark.asyncio
    async def test_written_semester_course_list_uses_student_department(self):
        courses = [
            {
                "course_code": "BIL102",
                "course_name": "Programlamaya Giris II",
                "credits": 3,
                "akts": 5,
                "department": "Bilgisayar Muhendisligi",
                "curriculum_semester": 2,
                "course_type": "zorunlu",
                "elective_group": None,
            }
        ]
        curriculum_fetcher = AsyncMock(return_value=courses)
        agent = CurriculumAgent(
            curriculum_course_fetcher=curriculum_fetcher,
            period_fetcher=AsyncMock(return_value=None),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task(
                "ikinci dönem dersleri neler?",
                student_department="Bilgisayar Muhendisligi",
            )
        )

        assert response.success is True
        assert "BIL102" in response.answer
        assert response.generation_mode != "llm"
        curriculum_fetcher.assert_awaited_once_with(2, "Bilgisayar Muhendisligi")

    @pytest.mark.asyncio
    async def test_course_list_groups_foreign_language_options(self):
        courses = [
            {
                "course_code": "BIL104",
                "course_name": "Programlamaya Giris-II",
                "credits": 3,
                "akts": 5,
                "department": "Bilgisayar Muhendisligi",
                "curriculum_semester": 2,
                "course_type": "zorunlu",
                "elective_group": None,
            },
            {
                "course_code": "YDA102",
                "course_name": "Almanca II",
                "credits": 2,
                "akts": 2,
                "department": "Bilgisayar Muhendisligi",
                "curriculum_semester": 2,
                "course_type": "zorunlu",
                "elective_group": None,
            },
            {
                "course_code": "YDF102",
                "course_name": "Fransizca II",
                "credits": 2,
                "akts": 2,
                "department": "Bilgisayar Muhendisligi",
                "curriculum_semester": 2,
                "course_type": "zorunlu",
                "elective_group": None,
            },
            {
                "course_code": "YDI102",
                "course_name": "Ingilizce II",
                "credits": 2,
                "akts": 2,
                "department": "Bilgisayar Muhendisligi",
                "curriculum_semester": 2,
                "course_type": "zorunlu",
                "elective_group": None,
            },
        ]
        curriculum_fetcher = AsyncMock(return_value=courses)
        agent = CurriculumAgent(
            curriculum_course_fetcher=curriculum_fetcher,
            period_fetcher=AsyncMock(return_value=None),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task(
                "Bilgisayar Muhendisligi 2. yariyil dersleri neler?",
                student_department="Bilgisayar Muhendisligi",
            )
        )

        assert response.success is True
        assert "2. yariyil doneminde kayitli 2 ders/grup bulundu" in response.answer
        assert "Yabanci dil secenekleri" in response.answer
        assert "YDA102 Almanca II" in response.answer
        assert "\n- YDF102 Fransizca II" not in response.answer

    @pytest.mark.asyncio
    async def test_course_title_lookup_answers_class_or_semester_question(self):
        courses = [
            {
                "course_code": "BIL124",
                "course_name": "Olasilik ve Istatistige Giris",
                "credits": 3,
                "akts": 5,
                "department": "Elektrik-Elektronik Muhendisligi",
                "curriculum_semester": 2,
                "course_type": "zorunlu",
                "elective_group": None,
            }
        ]
        title_fetcher = AsyncMock(return_value=courses)
        agent = CurriculumAgent(
            course_title_fetcher=title_fetcher,
            prerequisite_fetcher=AsyncMock(return_value=None),
            period_fetcher=AsyncMock(return_value=None),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Olasilik ve istatistige giris dersi hangi sinifta?")
        )

        assert response.success is True
        assert response.generation_mode == "vt"
        assert "BIL124" in response.answer
        assert "2. yariyil" in response.answer
        title_fetcher.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_precise_schedule_query_prefers_structured_schedule_rows(self):
        schedule_rows = [
            {
                "course_code": "BIL309",
                "course_key": "bil309",
                "course_name": "Yazilim Mimarisi",
                "schedule_group": "3. SINIF",
                "section": None,
                "day_of_week": "Pazartesi",
                "start_time": "08:15:00",
                "end_time": "09:00:00",
                "classroom": "D101",
                "instructor": "Dr. A",
            }
        ]
        agent = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=None),
            period_fetcher=AsyncMock(return_value=None),
            schedule_course_fetcher=AsyncMock(return_value=schedule_rows),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("BIL309 dersi hangi saatte?", student_department="Bilgisayar Muhendisligi")
        )

        assert response.success is True
        assert "BIL309 dersi icin bulunan ders programi satirlari" in response.answer
        assert "Pazartesi 08:15:00-09:00:00" in response.answer
        assert "Derslik: D101" in response.answer

    @pytest.mark.asyncio
    async def test_generic_schedule_query_without_rows_does_not_fall_through_to_rag(self):
        kwargs = _agent_kwargs()
        agent = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=None),
            period_fetcher=AsyncMock(return_value=None),
            schedule_course_fetcher=AsyncMock(return_value=[]),
            schedule_department_fetcher=AsyncMock(return_value=[]),
            **kwargs,
        )

        response = await agent.handle_task(
            _task("Bilgisayar Muhendisligi ders programi nerede?", student_department="Bilgisayar Muhendisligi")
        )

        assert response.success is True
        assert response.generation_mode == "kural"
        assert "kayitli yapilandirilmis ders programi satiri bulunamadi" in response.answer
        kwargs["llm_service"].generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_generic_department_schedule_query_uses_structured_rows(self):
        schedule_rows = [
            {
                "course_code": "BIL204",
                "course_key": "bil204",
                "course_name": "Algoritmalar",
                "schedule_group": "2. SINIF",
                "section": None,
                "day_of_week": "Cuma",
                "start_time": "08:15:00",
                "end_time": "09:00:00",
                "classroom": "D202",
                "instructor": "Dr. C",
            },
            {
                "course_code": "BIL104",
                "course_key": "bil104",
                "course_name": "Programlamaya Giris II",
                "schedule_group": "1. SINIF",
                "section": None,
                "day_of_week": "Pazartesi",
                "start_time": "08:15:00",
                "end_time": "09:00:00",
                "classroom": "D101",
                "instructor": "Dr. A",
            }
        ]
        agent = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=None),
            period_fetcher=AsyncMock(return_value=None),
            schedule_department_fetcher=AsyncMock(return_value=schedule_rows),
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task("Ders programi", student_department="Bilgisayar Muhendisligi")
        )

        assert response.success is True
        assert response.generation_mode == "vt"
        assert "Bilgisayar Muhendisligi icin bulunan ders programi satirlari" in response.answer
        assert "1. sinif:" in response.answer
        assert "2. sinif:" in response.answer
        assert response.answer.index("1. sinif:") < response.answer.index("2. sinif:")
        assert "Pazartesi 08:15:00-09:00:00" in response.answer
        assert response.answer.index("Pazartesi 08:15:00-09:00:00") < response.answer.index(
            "Cuma 08:15:00-09:00:00"
        )

    @pytest.mark.asyncio
    async def test_department_schedule_query_infers_department_without_login_context(self):
        schedule_rows = [
            {
                "course_code": "FIZ102",
                "course_key": "fiz102",
                "course_name": "Fizik II",
                "schedule_group": "1. SINIF",
                "section": None,
                "day_of_week": "Sali",
                "start_time": "10:15:00",
                "end_time": "11:00:00",
                "classroom": "F1",
                "instructor": "Dr. B",
            }
        ]
        schedule_fetcher = AsyncMock(return_value=schedule_rows)
        agent = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=None),
            period_fetcher=AsyncMock(return_value=None),
            schedule_department_fetcher=schedule_fetcher,
            **_agent_kwargs(),
        )

        response = await agent.handle_task(_task("Fizik ders programi var mi?"))

        assert response.success is True
        assert response.generation_mode == "vt"
        assert "Fizik icin bulunan ders programi satirlari" in response.answer
        assert "Sali 10:15:00-11:00:00" in response.answer
        schedule_fetcher.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_explicit_schedule_department_overrides_login_department(self):
        schedule_rows = [
            {
                "course_code": "EEM214",
                "course_key": "eem214",
                "course_name": "Elektronik Devreler",
                "schedule_group": "2. SINIF",
                "section": None,
                "day_of_week": "Pazartesi",
                "start_time": "08:15:00",
                "end_time": "09:00:00",
                "classroom": "L244",
                "instructor": "Dr. C",
                "academic_year": "2025-2026",
                "term": "Bahar",
            }
        ]
        schedule_fetcher = AsyncMock(return_value=schedule_rows)
        agent = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=None),
            period_fetcher=AsyncMock(return_value=None),
            schedule_department_fetcher=schedule_fetcher,
            **_agent_kwargs(),
        )

        response = await agent.handle_task(
            _task(
                "Elektrik elektronik muhendisligi ders programi var mi?",
                student_department="Bilgisayar Muhendisligi",
            )
        )

        assert response.success is True
        assert "Elektrik-Elektronik Muhendisligi icin bulunan ders programi satirlari" in response.answer
        assert "Bilgisayar Muhendisligi" not in response.answer
        schedule_fetcher.assert_awaited_once_with(
            "Elektrik-Elektronik Muhendisligi",
            academic_year=None,
            term=None,
        )

    def test_schedule_term_selection_prefers_current_term_when_query_is_unspecified(self):
        rows = [
            {
                "course_code": "MAT101",
                "course_name": "Matematik-I",
                "schedule_group": "1. SINIF",
                "academic_year": "2025-2026",
                "term": "Guz",
            },
            {
                "course_code": "MAT102",
                "course_name": "Matematik-II",
                "schedule_group": "1. SINIF",
                "academic_year": "2025-2026",
                "term": "Bahar",
            },
        ]

        selected_rows, term_context = CurriculumAgent._select_schedule_rows_for_term(
            "Matematik ders programi var mi?",
            rows,
            default_term_key="bahar",
        )

        assert [row["course_code"] for row in selected_rows] == ["MAT102"]
        assert term_context == "2025-2026 Bahar"

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
    async def test_cap_questions_use_llm_synthesis_not_raw_source_only(self):
        kwargs = _agent_kwargs()
        kwargs["retriever_factory"] = _mock_retriever_factory(
            content=(
                "CAP, ana dal lisans programlarini ustun basariyla yuruten ogrencilerin "
                "ikinci bir dalda lisans diplomasi almak uzere ogrenim gormesini saglar."
            ),
            score=0.72,
            metadata={"score_type": "reranker", "file_name": "yonerge_cift_anadal_yandal.pdf"},
        )
        llm = kwargs["llm_service"]
        llm.generate.return_value = "Onlisans ogrencileri icin CAP uygun gorunmuyor; CAP ikinci lisans programidir."
        agent = RegulationAgent(**kwargs)

        response = await agent.handle_task(_task("Onlisans ogrencisiyim CAP yapabiliyor muyum?"))

        assert response.success is True
        assert response.answer.startswith("Onlisans ogrencileri")
        llm.generate.assert_awaited_once()

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

    @pytest.mark.asyncio
    async def test_incoming_erasmus_registration_prefers_incoming_source_chunk(self):
        kwargs = _agent_kwargs()
        llm = kwargs["llm_service"]
        kwargs.pop("retriever_factory")
        retriever = MagicMock()
        retriever.search = MagicMock(return_value=[
            {
                "content": (
                    "MADDE 12 - Program kapsaminda yurt disina gidecek ogrencilere "
                    "yapilacak hibe miktari ve odeme usulu aciklanir. "
                    "DORDUNCU BOLUM Gelen Erasmus ogrencileri Universiteye basvuru."
                ),
                "source": "avrupa_birligi_erasmus.pdf",
                "score": 0.61,
                "metadata": {
                    "file_name": "avrupa_birligi_erasmus.pdf",
                    "score_type": "reranker",
                },
            },
            {
                "content": (
                    "MADDE 9 - Degisim programi kapsaminda Ondokuz Mayis "
                    "Universitesinde egitim gormek uzere gelecek degisim ogrencileri "
                    "icin islem yapilir. Gelen degisim ogrencilerinin kayitlari "
                    "ilgili bolum tarafindan Ogrenci Isleri Otomasyon Sistemine "
                    "yapilir. Kayit sonrasinda ogrencilere ogrenci numarasi verilir "
                    "ve ogrenci kimlik karti cikarilir."
                ),
                "source": "uluslararasi_isbirlikleri_protokoller_degisim.pdf",
                "score": 0.49,
                "metadata": {
                    "file_name": "uluslararasi_isbirlikleri_protokoller_degisim.pdf",
                    "score_type": "reranker",
                },
            },
        ])
        retriever.enrich_results = MagicMock(side_effect=lambda results, department=None: results)
        agent = InternationalAgent(
            retriever_factory=MagicMock(return_value=retriever),
            **kwargs,
        )

        response = await agent.handle_task(
            _task("Arkadasim erasmus ile yeni geldi nasil kayit yaptirabilir?")
        )

        assert response.success is True
        assert response.generation_mode == "rag+llm"
        assert retriever.search.call_args.kwargs["top_k"] == 10
        assert response.answer == "LLM tarafindan uretilen yanit."
        llm.generate.assert_awaited_once()


# ══════════════════════════════════════════════════════════
# 8. TuitionAgent
# ══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_international_agent_erasmus_grant_amount_query_prioritizes_grant_payment_chunk(monkeypatch):
    monkeypatch.setattr(base_module.settings.rag, "llm_evidence_selection_enabled", False)
    kwargs = _agent_kwargs()
    llm = kwargs["llm_service"]
    kwargs.pop("retriever_factory")
    retriever = MagicMock()
    retriever.search = MagicMock(return_value=[
        {
            "content": (
                "MADDE 8 - Basvurularla ilgili bilgi internet sayfasinda ilan edilir. "
                "Ogrenciler duyurularda belirtilen tarihler arasinda online basvuru yapar."
            ),
            "source": "avrupa_birligi_erasmus.pdf",
            "score": 0.66,
            "metadata": {
                "file_name": "avrupa_birligi_erasmus.pdf",
                "score_type": "reranker",
            },
        },
        {
            "content": (
                "MADDE 9 - Universiteye tahsis edilen hibe miktari ogrenim, staj, "
                "personel egitimi ve ders verme hareketlilikleri icin ayrilir."
            ),
            "source": "avrupa_birligi_erasmus.pdf",
            "score": 0.64,
            "metadata": {
                "file_name": "avrupa_birligi_erasmus.pdf",
                "score_type": "reranker",
            },
        },
        {
            "content": (
                "MADDE 12 - Program kapsaminda yurt disina gidecek ogrencilere "
                "yapilacak hibe miktari, odeme usulu ve tarihi her yil Ulusal Ajans "
                "tarafindan belirlenir. Odemeler iki taksitte yapilir; ilk odeme "
                "hesap edilen hibenin %80'i tutarindadir."
            ),
            "source": "avrupa_birligi_erasmus.pdf",
            "score": 0.56,
            "metadata": {
                "file_name": "avrupa_birligi_erasmus.pdf",
                "score_type": "reranker",
            },
        },
        {
            "content": (
                "MADDE 18 - Erasmus programi cercevesinde yerlestirilmis personel "
                "ile hibe sozlesmesi imzalanir. Personelin hibesinin ilk %80'lik "
                "kismi o yil icin belirlenen miktarda odenir."
            ),
            "source": "avrupa_birligi_erasmus.pdf",
            "score": 0.58,
            "metadata": {
                "file_name": "avrupa_birligi_erasmus.pdf",
                "score_type": "reranker",
            },
        },
    ])
    retriever.enrich_results = MagicMock(side_effect=lambda results, department=None: results)
    agent = InternationalAgent(
        retriever_factory=MagicMock(return_value=retriever),
        **kwargs,
    )

    response = await agent.handle_task(
        _task("Erasmus bursu ne kadar ve nasil basvurulur?")
    )

    assert response.success is True
    assert response.generation_mode == "rag+llm"
    llm.generate.assert_awaited_once()
    retriever.search.assert_called_once()
    assert retriever.search.call_args.kwargs["top_k"] == 10
    prompt = llm.generate.await_args.kwargs["prompt"]
    assert prompt.index("MADDE 12") > 0
    assert prompt.index("MADDE 18") > 0
    assert prompt.index("MADDE 12") > prompt.index("MADDE 8")
    assert prompt.index("MADDE 12") > prompt.index("MADDE 9")
    assert "Ulusal Ajans" in prompt
    assert "%80" in prompt


@pytest.mark.asyncio
async def test_international_agent_erasmus_grant_source_only_states_missing_fixed_amount():
    kwargs = _agent_kwargs()
    llm = kwargs["llm_service"]
    kwargs.pop("retriever_factory")
    retriever = MagicMock()
    retriever.search = MagicMock(return_value=[
        {
            "content": (
                "MADDE 12 - Program kapsaminda yurt disina gidecek ogrencilere "
                "yapilacak hibe miktari, odeme usulu ve tarihi her yil Ulusal Ajans "
                "tarafindan belirlenir. Odemeler iki taksitte yapilir; ilk odeme "
                "hesap edilen hibenin %80'i tutarindadir. Ogrenci Hibe Sozlesmesi "
                "imzalanir."
            ),
            "source": "avrupa_birligi_erasmus.pdf",
            "score": 0.56,
            "metadata": {
                "file_name": "avrupa_birligi_erasmus.pdf",
                "score_type": "reranker",
            },
        },
        {
            "content": (
                "MADDE 8 - Basvurularla ilgili bilgi UIB'nin ve universitenin "
                "internet sayfalarinda ilan edilir. Ogrenciler duyurularda "
                "belirtilen tarihler arasinda basvuru yapar."
            ),
            "source": "avrupa_birligi_erasmus.pdf",
            "score": 0.50,
            "metadata": {
                "file_name": "avrupa_birligi_erasmus.pdf",
                "score_type": "reranker",
            },
        },
    ])
    retriever.enrich_results = MagicMock(side_effect=lambda results, department=None: results)
    agent = InternationalAgent(
        retriever_factory=MagicMock(return_value=retriever),
        **kwargs,
    )

    response = await agent.handle_task(
        _task(
            "Erasmus bursu ne kadar ve nasil basvurulur?",
            disable_specialist_llm=True,
        )
    )

    assert response.success is True
    assert response.generation_mode == "rag"
    assert "sabit bir TL/Euro hibe tutari yer almiyor" in response.answer
    assert "Ulusal Ajans" in response.answer
    assert "%80" in response.answer
    assert "Basvuru bilgileri" in response.answer
    llm.generate.assert_not_awaited()


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
            _task("Harc borcumu goster", student_id=999, is_authenticated=True)
        )

        assert response.success is False
        assert response.error == "student_not_found"

    @pytest.mark.asyncio
    async def test_general_tuition_query_uses_rag(self):
        agent = TuitionAgent(tuition_fetcher=AsyncMock(), **_agent_kwargs())

        response = await agent.handle_task(
            _task("Harc ucretleri ne kadar?")
        )

        assert response.success is False
        assert response.error == "student_type_context_required"
        assert "ogrenci turune ve birime gore degisiyor" in response.answer.lower()

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

    @pytest.mark.asyncio
    async def test_structured_fee_query_uses_profile_student_type_when_query_omits_it(
        self,
        monkeypatch,
    ):
        async def _fake_catalog_lookup(*, student_type, unit_name, academic_year=None):
            assert student_type == "domestic"
            assert unit_name == "dis hekimligi fakultesi"
            return {
                "academic_year": "2025-2026",
                "student_type": "domestic",
                "unit_name": "Dis Hekimligi Fakultesi",
                "annual_amount": 3057.0,
                "semester_amount": None,
                "currency": "TRY",
                "source_document": "turk_ogrenci_ucretleri.pdf",
            }

        monkeypatch.setattr(
            "src.agents.finance.tuition_agent.fetch_tuition_fee_catalog_entry",
            _fake_catalog_lookup,
        )

        agent = TuitionAgent(tuition_fetcher=AsyncMock(), **_agent_kwargs())
        response = await agent.handle_task(
            _task(
                "Dis hekimligi donem ucreti ne kadar?",
                student_type="domestic",
            )
        )

        assert response.success is True
        assert "3.057,00 TL" in response.answer
        assert "Turk ogrenci" in response.answer

    @pytest.mark.asyncio
    async def test_explicit_query_student_type_overrides_profile_student_type(
        self,
        monkeypatch,
    ):
        async def _fake_catalog_lookup(*, student_type, unit_name, academic_year=None):
            assert student_type == "international"
            assert unit_name == "dis hekimligi fakultesi"
            return {
                "academic_year": "2025-2026",
                "student_type": "international",
                "unit_name": "Dis Hekimligi Fakultesi",
                "annual_amount": 203000.0,
                "semester_amount": None,
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
                "Dis hekimligi donem ucreti yabanci ogrenciler icin ne kadar?",
                student_type="domestic",
            )
        )

        assert response.success is True
        assert "203.000,00 TL" in response.answer
        assert "uluslararasi ogrenci" in response.answer

    @pytest.mark.asyncio
    async def test_structured_fee_catalog_miss_falls_back_to_rag(self, monkeypatch):
        async def _missing_catalog_lookup(*, student_type, unit_name, academic_year=None):
            return None

        monkeypatch.setattr(
            "src.agents.finance.tuition_agent.fetch_tuition_fee_catalog_entry",
            _missing_catalog_lookup,
        )

        agent = TuitionAgent(tuition_fetcher=AsyncMock(), **_agent_kwargs())
        response = await agent.handle_task(
            _task(
                "Dis hekimligi donem ucreti Turk ogrenciyim",
                student_type="Turk ogrenci",
            )
        )

        assert response.success is True
        assert response.error is None
        assert "veritabaninda bulunmuyor" not in response.answer


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
                display_summary="2026-Bahar donemi ders kayit tarihleri 10-21 Subat olarak belirlenmistir.",
                links=[],
                original_text=None,
                source_url="https://omu.edu.tr/duyuru/1",
                faculty="Muhendislik",
                department="Bilgisayar Muhendisligi",
                unit_name="Muhendislik Fakultesi",
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
                display_summary=long_text,
                links=[],
                original_text=None,
                source_url=None,
                faculty=None,
                department=None,
                unit_name=None,
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
