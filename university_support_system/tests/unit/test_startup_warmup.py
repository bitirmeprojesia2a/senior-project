from __future__ import annotations

from src.a2a.targets import SpecialistTarget
from src.core.constants import Capability, Department, academic_schedule_collection_name, collection_name_for_department
from src.rag.retriever import HybridRetriever
from src.startup.warmup import resolve_warmup_collections, resolve_warmup_llm_roles


def test_resolve_warmup_collections_for_academic_specialist_includes_schedule() -> None:
    target = SpecialistTarget(
        department=Department.ACADEMIC_PROGRAMS,
        agent_id="curriculum_agent",
    )

    assert resolve_warmup_collections(target) == [
        collection_name_for_department(Department.ACADEMIC_PROGRAMS),
        academic_schedule_collection_name(),
    ]


def test_resolve_warmup_collections_for_capability_is_empty() -> None:
    assert resolve_warmup_collections(Capability.ANNOUNCEMENT) == []


def test_resolve_warmup_llm_roles_for_specialist_excludes_routing() -> None:
    target = SpecialistTarget(
        department=Department.STUDENT_AFFAIRS,
        agent_id="registration_agent",
    )

    assert resolve_warmup_llm_roles(target) == [
        "evidence_selection",
        "final_refinement",
        "specialist_synthesis",
    ]


def test_hybrid_retriever_prewarm_runs_probe_search_and_rerank(monkeypatch) -> None:
    calls: list[tuple] = []

    def fake_init(self, *args, **kwargs) -> None:
        self.k = 5
        self.embedder = type(
            "FakeEmbedder",
            (),
            {
                "model": object(),
                "embed_single": lambda _self, text, is_query=True: calls.append(("embed", text, is_query)),
            },
        )()
        self.reranker = type(
            "FakeReranker",
            (),
            {
                "model": object(),
                "rerank": lambda _self, query, candidates, top_k=5: calls.append(
                    ("rerank", query, len(candidates), top_k)
                ),
            },
        )()

    monkeypatch.setattr(HybridRetriever, "__init__", fake_init)
    monkeypatch.setattr(
        HybridRetriever,
        "_ensure_ensemble",
        lambda self, collection_name: calls.append(("ensure", collection_name)),
    )
    monkeypatch.setattr(
        HybridRetriever,
        "_search_collection_candidates",
        lambda self, collection_name, query: calls.append(("search", collection_name, query)) or [
            {"content": "Warm-up icerigi", "score": 0.1, "source": "test", "metadata": {}}
        ],
    )
    monkeypatch.setattr(
        HybridRetriever,
        "close",
        lambda self: calls.append(("close",)),
    )

    HybridRetriever.prewarm(
        [collection_name_for_department(Department.STUDENT_AFFAIRS)],
        include_reranker=True,
    )

    assert ("ensure", collection_name_for_department(Department.STUDENT_AFFAIRS)) in calls
    assert any(call[0] == "embed" for call in calls)
    assert any(call[0] == "search" for call in calls)
    assert any(call[0] == "rerank" for call in calls)
    assert calls[-1] == ("close",)
