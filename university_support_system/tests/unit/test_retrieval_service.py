from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import retrieval_service as retrieval_service_module
from src.api.retrieval_service import create_retrieval_service_app
from src.core.constants import Department
from src.rag.remote import RemoteHybridRetriever


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class _FakeHttpClient:
    def __init__(self) -> None:
        self.posts: list[tuple[str, dict]] = []

    def post(self, url: str, *, json: dict) -> _FakeResponse:
        self.posts.append((url, json))
        return _FakeResponse({"results": [{"content": "remote", "score": 0.9, "metadata": {}}]})

    def close(self) -> None:
        return None


class _FakeRetriever:
    def search(self, query: str, **kwargs):
        return [
            {
                "content": f"search:{query}",
                "score": 0.8,
                "source": "test",
                "metadata": {"department": kwargs["department"].value},
            }
        ]

    def enrich_results(self, results: list[dict], **kwargs):
        return [{**results[0], "content": "enriched", "metadata": {"department": kwargs["department"].value}}]

    def close(self) -> None:
        return None


def test_remote_hybrid_retriever_sends_search_payload(monkeypatch) -> None:
    fake_client = _FakeHttpClient()
    monkeypatch.setattr("src.rag.remote.httpx.Client", lambda timeout: fake_client)

    retriever = RemoteHybridRetriever(base_url="http://retrieval-service:8140", timeout_seconds=12)
    results = retriever.search(
        "Ders kaydi nasil yapilir?",
        top_k=7,
        department=Department.STUDENT_AFFAIRS,
        source_hints=["sik_sorulan_sorular.txt"],
        topic_hint="ders kaydi",
        student_department="Bilgisayar Muhendisligi",
    )

    assert results[0]["content"] == "remote"
    assert fake_client.posts == [
        (
            "http://retrieval-service:8140/search",
            {
                "query": "Ders kaydi nasil yapilir?",
                "top_k": 7,
                "department": "student_affairs",
                "source_hints": ["sik_sorulan_sorular.txt"],
                "topic_hint": "ders kaydi",
                "student_department": "Bilgisayar Muhendisligi",
            },
        )
    ]


def test_retrieval_service_search_and_enrich(monkeypatch) -> None:
    retrieval_service_module.get_retriever.cache_clear()
    monkeypatch.setattr(retrieval_service_module, "get_retriever", lambda: _FakeRetriever())

    app = create_retrieval_service_app()
    with TestClient(app) as client:
        search = client.post(
            "/search",
            json={"query": "Mezuniyet sartlari", "department": "student_affairs"},
        )
        enrich = client.post(
            "/enrich",
            json={
                "department": "academic_programs",
                "results": [{"content": "raw", "score": 0.5, "metadata": {}}],
            },
        )

    assert search.status_code == 200
    assert search.json()["results"][0]["content"] == "search:Mezuniyet sartlari"
    assert search.json()["results"][0]["metadata"]["department"] == "student_affairs"
    assert enrich.status_code == 200
    assert enrich.json()["results"][0]["content"] == "enriched"
    assert enrich.json()["results"][0]["metadata"]["department"] == "academic_programs"
