"""Embedding ve reranker model cache testleri."""

from src.core.config import settings
from src.rag.embedder import Embedder
from src.rag.reranker import CrossEncoderReranker


class _FakeSentenceTransformer:
    init_count = 0

    def __init__(self, *args, **kwargs):
        type(self).init_count += 1

    def get_sentence_embedding_dimension(self):
        return 1024


class _FakeCrossEncoder:
    init_count = 0

    def __init__(self, *args, **kwargs):
        type(self).init_count += 1


def test_embedder_reuses_model_when_cache_enabled(monkeypatch):
    Embedder.clear_model_cache()
    _FakeSentenceTransformer.init_count = 0
    monkeypatch.setattr("src.rag.embedder.SentenceTransformer", _FakeSentenceTransformer)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "embedding_model_cache_enabled", True)

    first = Embedder(model_name="fake-model", device="cpu")
    second = Embedder(model_name="fake-model", device="cpu")

    assert first.model is second.model
    assert _FakeSentenceTransformer.init_count == 1

    Embedder.clear_model_cache()


def test_embedder_does_not_reuse_model_when_cache_disabled(monkeypatch):
    Embedder.clear_model_cache()
    _FakeSentenceTransformer.init_count = 0
    monkeypatch.setattr("src.rag.embedder.SentenceTransformer", _FakeSentenceTransformer)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "embedding_model_cache_enabled", False)

    first = Embedder(model_name="fake-model", device="cpu")
    second = Embedder(model_name="fake-model", device="cpu")

    assert first.model is not second.model
    assert _FakeSentenceTransformer.init_count == 2


def test_reranker_reuses_model_when_cache_enabled(monkeypatch):
    CrossEncoderReranker.clear_model_cache()
    _FakeCrossEncoder.init_count = 0
    monkeypatch.setattr("src.rag.reranker.CrossEncoder", _FakeCrossEncoder)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "reranker_model_cache_enabled", True)

    first = CrossEncoderReranker(model_name="fake-reranker", device="cpu")
    second = CrossEncoderReranker(model_name="fake-reranker", device="cpu")

    assert first.model is second.model
    assert _FakeCrossEncoder.init_count == 1

    CrossEncoderReranker.clear_model_cache()


def test_reranker_does_not_reuse_model_when_cache_disabled(monkeypatch):
    CrossEncoderReranker.clear_model_cache()
    _FakeCrossEncoder.init_count = 0
    monkeypatch.setattr("src.rag.reranker.CrossEncoder", _FakeCrossEncoder)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "reranker_model_cache_enabled", False)

    first = CrossEncoderReranker(model_name="fake-reranker", device="cpu")
    second = CrossEncoderReranker(model_name="fake-reranker", device="cpu")

    assert first.model is not second.model
    assert _FakeCrossEncoder.init_count == 2
