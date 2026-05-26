"""Regulation-focused academic programs agent."""

from __future__ import annotations

from collections.abc import Sequence

from src.agents.academic.regulation_utils import (
    build_regulation_intro,
    pick_preferred_regulation_result,
)
from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.llm.prompt_templates import REGULATION_AGENT_SYSTEM_PROMPT


class RegulationAgent(BaseSpecialistAgent):
    """Yonetmelik, yonerge ve mevzuat uzman ajani."""

    _SIMPLE_PEDAGOGICAL_TRANSCRIPT_MARKERS = (
        "pedagojik formasyon",
        "formasyon ders",
        "transkript",
        "ortalamaya dahil",
        "mezuniyet ortalamas",
    )

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

    def _should_force_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        lowered = normalize_text(query_text)
        if "cap" in lowered or "cift anadal" in lowered or "cift ana dal" in lowered:
            return True
        if "onlisans" in lowered or "on lisans" in lowered:
            return True
        return super()._should_force_llm_synthesis(
            query_text,
            results,
            db_context=db_context,
        )

    def _build_source_only_answer(
        self,
        query_text: str,
        results: list[dict] | tuple[dict, ...],
        *,
        db_context: str | None = None,
    ) -> str:
        lowered = normalize_text(query_text)
        if (
            ("cap" in lowered or "cift anadal" in lowered or "cift ana dal" in lowered)
            and any(marker in lowered for marker in ("onlisans", "on lisans", "iki yillik"))
        ):
            prefix = f"{db_context}\n\n" if db_context else ""
            return (
                prefix
                + "Kaynakta CAP, ana dal lisans programını üstün başarıyla yürüten öğrencilerin "
                "ikinci bir dalda lisans diploması almak üzere öğrenim görmesi olarak tanımlanır. "
                "Bu nedenle kaynak bilgisinden hareketle önlisans/iki yıllık program öğrencileri için "
                "ÇAP uygun görünmüyor; kesin başvuru uygunluğu için ilgili birimin ÇAP/YAP duyurusu ve "
                "danışmanlığı kontrol edilmelidir.\n\n"
                "(Kaynak: yonerge_cift_anadal_yandal.pdf)"
            )

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

    def _should_enrich_results(self, query_text: str, results: Sequence[dict]) -> bool:
        lowered = query_text.casefold()
        if "formasyon" in lowered and any(
            marker in lowered for marker in self._SIMPLE_PEDAGOGICAL_TRANSCRIPT_MARKERS
        ):
            return False
        return super()._should_enrich_results(query_text, results)
