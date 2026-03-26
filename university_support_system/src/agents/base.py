"""Uzman ajanlar için ortak taban sınıflar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from a2a.types import AgentSkill, Task

from src.a2a import build_agent_card
from src.core.constants import Department, TaskType
from src.db.schemas import DepartmentResponse, RAGSource
from src.llm.llm_service import LLMService
from src.llm.prompt_templates import GENERAL_QA_SYSTEM_PROMPT
from src.rag.retriever import HybridRetriever


@dataclass(frozen=True)
class AgentDefinition:
    """Uzman ajan sabit tanımı."""

    agent_id: str
    name: str
    department: Department
    description: str
    task_types: tuple[TaskType, ...]
    examples: tuple[str, ...]
    tags: tuple[str, ...]


class BaseSpecialistAgent:
    """RAG + LLM tabanlı temel uzman ajan."""

    def __init__(
        self,
        definition: AgentDefinition,
        *,
        llm_service: LLMService | None = None,
        retriever_factory: Callable[[], HybridRetriever] | None = None,
    ) -> None:
        self.definition = definition
        self.llm_service = llm_service or LLMService()
        self._retriever_factory = retriever_factory or (lambda: HybridRetriever())

    @property
    def agent_id(self) -> str:
        return self.definition.agent_id

    @property
    def department(self) -> Department:
        return self.definition.department

    def build_card(self):
        """A2A AgentCard üretir."""
        skills = [
            AgentSkill(
                id=f"{self.agent_id}_skill",
                name=self.definition.name,
                description=self.definition.description,
                tags=list(self.definition.tags),
                examples=list(self.definition.examples),
                inputModes=["text"],
                outputModes=["text"],
            )
        ]
        return build_agent_card(
            agent_id=self.agent_id,
            name=self.definition.name,
            description=self.definition.description,
            url=f"https://omu.edu.tr/agents/{self.agent_id}",
            skills=skills,
        )

    async def handle_task(self, task: Task) -> DepartmentResponse:
        """A2A task'i işleyip departman yanıtı üretir."""
        query_text = str((task.metadata or {}).get("query_text", "")).strip()
        if not query_text:
            query_text = self._extract_query_from_task(task)

        retriever = self._retriever_factory()
        results = retriever.search(query_text, department=self.department)
        answer = await self._generate_answer(query_text, results)

        return DepartmentResponse(
            department=self.department,
            answer=answer,
            sources=[
                RAGSource(
                    content=item.get("content", ""),
                    score=float(item.get("score", 0.0)),
                    metadata=item.get("metadata", {}),
                )
                for item in results
            ],
            success=True,
        )

    def _extract_query_from_task(self, task: Task) -> str:
        """Task içindeki ilk text part'tan sorgu çıkarır."""
        message = task.status.message
        if message is None:
            return ""
        for part in message.parts:
            text = getattr(part, "text", None)
            if text:
                return str(text)
            root = getattr(part, "root", None)
            text = getattr(root, "text", None)
            if text:
                return str(text)
        return ""

    async def _generate_answer(self, query_text: str, results: Sequence[dict]) -> str:
        """Kaynakları kısa bağlama çevirip LLM ile yanıt üretir."""
        if not results:
            return (
                "Bu konuda elimde yeterli kaynak bulunamadi. "
                "Soruyu biraz daha detaylandirirsan veya ilgili birimle iletisime gecersen daha net yardimci olabilirim."
            )

        context_chunks = []
        for index, item in enumerate(results[:3], start=1):
            source = item.get("source", "bilinmiyor")
            content = item.get("content", "")
            context_chunks.append(f"[Kaynak {index}: {source}]\n{content}")

        prompt = (
            f"Soru:\n{query_text}\n\n"
            f"Baglam:\n{'\n\n'.join(context_chunks)}\n\n"
            "Yalnizca verilen baglama dayanarak kisa ve acik bir cevap üret."
        )
        return await self.llm_service.generate(prompt=prompt, system=GENERAL_QA_SYSTEM_PROMPT)
