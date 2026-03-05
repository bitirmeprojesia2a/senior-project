"""
Integration Test Fixture'ları

ChromaDB erişilebilirliğini kontrol eder ve gerekli fixture'ları sağlar.
ChromaDB çalışmıyorsa tüm integration testler otomatik atlanır.
"""

import json
from pathlib import Path

import httpx
import pytest


def _is_chromadb_available() -> bool:
    try:
        r = httpx.get("http://localhost:8100/api/v1/heartbeat", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


def _collection_has_data() -> bool:
    try:
        r = httpx.get("http://localhost:8100/api/v1/collections", timeout=2.0)
        if r.status_code != 200:
            return False
        collections = r.json()
        return any(c["name"] == "student_affairs_docs" for c in collections)
    except Exception:
        return False


chromadb_available = pytest.mark.skipif(
    not _is_chromadb_available(),
    reason="ChromaDB sunucusu erişilebilir değil (localhost:8100)",
)

collection_has_data = pytest.mark.skipif(
    not _collection_has_data(),
    reason="student_affairs_docs koleksiyonu mevcut değil veya boş",
)


@pytest.fixture(scope="session")
def test_questions():
    """Test soruları dosyasını yükler."""
    path = Path(__file__).parent.parent.parent / "data" / "test" / "rag_test_questions.json"
    if not path.exists():
        pytest.skip(f"Test soruları bulunamadı: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]


@pytest.fixture(scope="session")
def hybrid_retriever():
    """Session-scoped HybridRetriever — modeller sadece 1 kez yüklenir."""
    from src.rag.retriever import HybridRetriever

    retriever = HybridRetriever(cache_ttl=0)
    yield retriever
    retriever.close()
