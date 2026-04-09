"""Regulation-focused academic programs agent."""

from __future__ import annotations

from src.agents.academic.regulation_utils import (
    build_regulation_intro,
    pick_preferred_regulation_result,
    should_skip_regulation_llm_synthesis,
)
from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.llm.prompt_templates import REGULATION_AGENT_SYSTEM_PROMPT


class RegulationAgent(BaseSpecialistAgent):
    """Yonetmelik, yonerge ve mevzuat uzman ajani."""

    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="regulation_agent",
                name="Regulation Agent",
                department=Department.ACADEMIC_PROGRAMS,
                description="Yonerge, yonetmelik ve mevzuat sorularini yanitlar.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Yonetmelik nerede?", "Ozel ogrenci yonergesi nedir?"),
                tags=("academic_programs", "regulation"),
                system_prompt=REGULATION_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )

    def _should_skip_llm_synthesis(
        self,
        query_text: str,
        results: list[dict] | tuple[dict, ...],
        *,
        db_context: str | None = None,
    ) -> bool:
        return should_skip_regulation_llm_synthesis(query_text, results)

    def _build_source_only_answer(
        self,
        query_text: str,
        results: list[dict] | tuple[dict, ...],
        *,
        db_context: str | None = None,
    ) -> str:
        preferred = self._pick_preferred_result(query_text, results)
        if preferred is None:
            return super()._build_source_only_answer(query_text, results, db_context=db_context)

        content = self._compact_source_content(preferred.get("content", ""), max_len=None)
        source = preferred.get("source", "bilinmiyor")
        prefix = f"{db_context}\n\n" if db_context else ""
        intro = build_regulation_intro(query_text)
        return f"{prefix}{intro}\n{content}\n\n(Kaynak: {source})"

    def _pick_preferred_result(
        self,
        query_text: str,
        results: list[dict] | tuple[dict, ...],
    ) -> dict | None:
        return pick_preferred_regulation_result(query_text, results)
