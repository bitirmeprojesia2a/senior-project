from types import SimpleNamespace

import pytest

from src.agents.student.graduation_agent import GraduationAgent
from src.agents.student.graduation_utils import is_graduation_akts_total_query


def _task(query: str, **metadata):
    return SimpleNamespace(metadata={"query_text": query, **metadata})


def test_graduation_akts_total_query_detects_total_not_course_detail():
    assert is_graduation_akts_total_query("Onlisans mezuniyet icin kac AKTS tamamlamaliyim?")
    assert not is_graduation_akts_total_query("BIL203 dersinin AKTS'si kac?")


@pytest.mark.asyncio
async def test_graduation_agent_uses_level_rule_for_bachelor_akts():
    agent = GraduationAgent()

    response = await agent.handle_department_task(
        _task("Bilgisayar Muhendisligi lisans mezuniyet icin kac AKTS tamamlamaliyim?")
    )

    assert response.success is True
    assert response.metadata["policy_facet"] == "graduation_akts"
    assert response.db_data["graduation_akts"] == 240
    assert "240 AKTS" in response.answer
