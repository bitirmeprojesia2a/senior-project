import pytest
from unittest.mock import AsyncMock
from src.a2a import A2AQueryPayload, build_query_task

from src.agents.student.registration_utils import is_payment_debt_course_registration_query
from src.agents.academic.curriculum_utils import is_prerequisite_query
from src.agents.academic.curriculum_agent import CurriculumAgent
from src.agents.student.internship_agent import InternshipAgent


def test_payment_debt_course_registration_query():
    # Katkı payı veya öğrenim ücretini ödemeyen öğrenci ders kaydı veya kayıt yenileme yapabilir mi?
    q1 = "Katki payi veya ogrenim ucretini odemeyen ogrenci ders kaydi veya kayit yenileme yapabilir mi?"
    assert is_payment_debt_course_registration_query(q1)

    # Katkı payı veya öğrenim ücretini yatırmayan öğrenci ders kaydı yapabilir mi?
    q2 = "Katki payi veya ogrenim ucretini yatirmayan ogrenci ders kaydi yapabilir mi?"
    assert is_payment_debt_course_registration_query(q2)


def test_prerequisite_query_blockers():
    # If blocker words are present, it should return False
    # "önkoşul/mezuniyet/ÇAP açısından" contains "cap" and "onkosul"
    q_blocked = "onkosul/mezuniyet/cap acisindan dikkat etmem gereken sartlar"
    assert not is_prerequisite_query(q_blocked)

    # Without blockers, it should return True
    q_clean = "bilgisayar muhendisligi dersi onkosul sarti nedir"
    assert is_prerequisite_query(q_clean)


@pytest.mark.asyncio
async def test_general_prerequisite_query_bypasses_lookup():
    agent = CurriculumAgent(
        course_fetcher=AsyncMock(),
        course_title_fetcher=AsyncMock(),
        prerequisite_fetcher=AsyncMock(),
    )

    q_general = "bilgisayar muhendisligi dersleri icin onkosul acisindan dikkat edilmesi gereken sartlar nelerdir?"

    # Run the method
    resp = await agent._try_build_prerequisite_response(
        query_text=q_general,
        lowered=q_general,
        effective_department="Bilgisayar Mühendisliği"
    )

    assert resp is None


@pytest.mark.asyncio
async def test_internship_summer_school_overlap():
    agent = InternshipAgent()

    # "Staj tarihlerim yaz okuluyla çakışırsa ders alabilir miyim?"
    query = "Staj tarihlerim yaz okuluyla cakisirse ders alabilir miyim?"
    payload = A2AQueryPayload(
        query_text=query,
        context_id="ctx-test-staj-overlap",
        task_type="procedure_query",
    )
    task = build_query_task(payload)

    resp = await agent.handle_department_task(task)
    assert resp.success
    assert resp.generation_mode == "kural"
    assert "Genel kural olarak staj, ders veya yaz okulu" in resp.answer


def test_staj_yaz_okulu_routing():
    from src.core.specialist_ownership import _student_policy_route
    
    # A query with staj and yaz okulu should resolve to internship_agent, not registration_agent
    route = _student_policy_route("staj tarihlerim yaz okuluyla cakisirsa ders alabilir miyim?")
    assert route.agent_id == "internship_agent"

