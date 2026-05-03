"""Student life support agent."""

from __future__ import annotations

from typing import Sequence

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.llm.prompt_templates import STUDENT_LIFE_AGENT_SYSTEM_PROMPT


class StudentLifeAgent(BaseSpecialistAgent):
    _IDENTITY_CARD_MARKERS = (
        "kimlik",
        "kimlig",
        "kart",
    )
    _LOST_CARD_MARKERS = (
        "kayip",
        "kaybett",
        "kaybol",
    )

    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="student_life_agent",
                name="Student Life Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Ogrenci hayati, topluluklar ve genel destek sorularini yanitlar.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Kimlik karti nasil alinir?", "Ogrenci topluluguna nasil katilirim?"),
                tags=("student_affairs", "student_life"),
                system_prompt=STUDENT_LIFE_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )

    @classmethod
    def _is_lost_identity_card_query(cls, query_text: str) -> bool:
        lowered = normalize_text(query_text)
        return (
            any(marker in lowered for marker in cls._IDENTITY_CARD_MARKERS)
            and any(marker in lowered for marker in cls._LOST_CARD_MARKERS)
        )

    def _should_force_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        if self._is_lost_identity_card_query(query_text):
            return True
        return super()._should_force_llm_synthesis(
            query_text,
            results,
            db_context=db_context,
        )

    def _filter_results_for_answer(
        self,
        query_text: str,
        results: Sequence[dict],
    ) -> list[dict]:
        filtered = super()._filter_results_for_answer(query_text, results)
        if not self._is_lost_identity_card_query(query_text):
            return filtered

        def _is_identity_card_source(item: dict) -> bool:
            metadata = item.get("metadata") or {}
            haystack = normalize_text(
                " ".join(
                    str(value)
                    for value in (
                        item.get("source", ""),
                        item.get("content", ""),
                        metadata.get("source", ""),
                        metadata.get("file_name", ""),
                    )
                )
            )
            return (
                "kimlik" in haystack
                and ("kart" in haystack or "dekont" in haystack or "kaybed" in haystack)
            )

        preferred = [item for item in filtered if _is_identity_card_source(item)]
        return preferred or filtered

    def _build_source_only_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        if self._is_lost_identity_card_query(query_text):
            return (
                "Ogrenci kimlik kartinizi kaybettiyseniz yeni kimlik karti basvurusu yapmaniz gerekir. "
                "Kimlik ucreti yatirildigina dair dekontu PP.4.7.FR.0163 Kimlik Karti Basvuru Formuna "
                "eklemelisiniz. Sistem kaynakli nedenlerle kullanilamayan kimlik kartlari ise ucretsiz degistirilir."
            )
        return super()._build_source_only_answer(
            query_text,
            results,
            db_context=db_context,
        )
