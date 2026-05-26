"""
Integration Test Fixture'ları

ChromaDB erişilebilirliğini kontrol eder ve gerekli fixture'ları sağlar.
ChromaDB çalışmıyorsa tüm integration testler otomatik atlanır.
"""

import json
from pathlib import Path

import httpx
import pytest

REQUIRED_COLLECTIONS = ("student_affairs_docs",)
OPTIONAL_COLLECTIONS = ("academic_programs_docs",)


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
        collection_names = {c["name"] for c in collections}
        return all(name in collection_names for name in REQUIRED_COLLECTIONS)
    except Exception:
        return False


def _has_collection(name: str) -> bool:
    try:
        r = httpx.get("http://localhost:8100/api/v1/collections", timeout=2.0)
        if r.status_code != 200:
            return False
        collections = r.json()
        return any(collection["name"] == name for collection in collections)
    except Exception:
        return False


chromadb_available = pytest.mark.skipif(
    not _is_chromadb_available(),
    reason="ChromaDB sunucusu erişilebilir değil (localhost:8100)",
)

collection_has_data = pytest.mark.skipif(
    not _collection_has_data(),
    reason=(
        "Mevcut integration veri seti için gerekli koleksiyonlar mevcut değil: "
        f"{', '.join(REQUIRED_COLLECTIONS)}"
    ),
)

academic_collection_has_data = pytest.mark.skipif(
    not _has_collection("academic_programs_docs"),
    reason=(
        "Academic programs integration smoke testi icin gerekli koleksiyon mevcut degil: "
        "academic_programs_docs"
    ),
)


# ── Session-Scoped Shared Fixtures ──────────────────────


@pytest.fixture(scope="session")
def shared_embedder():
    """Session-scoped Embedder; ağır model sadece 1 kez yüklenir."""
    from src.rag.embedder import Embedder

    embedder = Embedder()
    return embedder


@pytest.fixture(scope="session")
def test_questions():
    """Test soruları dosyasını yükler."""
    path = Path(__file__).parent.parent.parent / "data" / "test" / "rag_test_questions.json"
    if not path.exists():
        pytest.skip(f"Test soruları bulunamadı: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [
        question
        for question in data["questions"]
        if question.get("department", "student_affairs") == "student_affairs"
    ]


@pytest.fixture(scope="session")
def academic_program_questions():
    """Academic programs soru alt kümesini yükler."""
    path = Path(__file__).parent.parent.parent / "data" / "test" / "rag_test_questions.json"
    if not path.exists():
        pytest.skip(f"Test soruları bulunamadı: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [
        question
        for question in data["questions"]
        if question.get("department") == "academic_programs"
    ]


@pytest.fixture(scope="session")
def hybrid_retriever():
    """Session-scoped HybridRetriever; modeller sadece 1 kez yüklenir, cache aktif."""
    from src.rag.retriever import HybridRetriever

    retriever = HybridRetriever(cache_ttl=300)
    yield retriever
    retriever.close()


@pytest.fixture(scope="session")
def cached_retriever():
    """Cache testi için ayrı session-scoped retriever (cache_ttl=60)."""
    from src.rag.retriever import HybridRetriever

    retriever = HybridRetriever(cache_ttl=60)
    yield retriever
    retriever.close()
