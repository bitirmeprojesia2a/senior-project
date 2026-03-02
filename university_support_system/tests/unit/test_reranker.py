"""
CrossEncoderReranker Unit Testleri

Cross-encoder modelini mock'layarak reranking mantığını test eder.
"""

from unittest.mock import MagicMock, patch, PropertyMock
import numpy as np

import pytest

from src.rag.reranker import CrossEncoderReranker


@pytest.fixture
def mock_cross_encoder():
    """Mock CrossEncoder modeli."""
    model = MagicMock()
    model.predict.return_value = np.array([0.9, 0.3, 0.7, 0.1, 0.5])
    return model


@pytest.fixture
def sample_candidates():
    """Örnek aday belge listesi."""
    return [
        {"content": "ÇAP başvurusu ÖİDB'den yapılır.", "source": "cap.pdf", "score": 0.0},
        {"content": "Yaz okulu harçları.", "source": "yaz.pdf", "score": 0.0},
        {"content": "ÇAP not ortalaması 2.5 olmalıdır.", "source": "cap.pdf", "score": 0.0},
        {"content": "Spor tesisleri bilgileri.", "source": "spor.pdf", "score": 0.0},
        {"content": "ÇAP danışmanlık süreci.", "source": "cap.pdf", "score": 0.0},
    ]


class TestRerankerRerank:
    """rerank() metodu testleri."""

    def test_reranks_by_score(self, mock_cross_encoder, sample_candidates):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("ÇAP başvurusu", sample_candidates, top_k=5)

        assert len(results) == 5
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_top_k_limits_results(self, mock_cross_encoder, sample_candidates):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("ÇAP başvurusu", sample_candidates, top_k=3)

        assert len(results) == 3

    def test_scores_assigned_correctly(self, mock_cross_encoder, sample_candidates):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("ÇAP başvurusu", sample_candidates, top_k=5)

        assert results[0]["score"] == 0.9
        assert results[1]["score"] == 0.7

    def test_empty_candidates(self, mock_cross_encoder):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("test", [], top_k=5)

        assert results == []
        mock_cross_encoder.predict.assert_not_called()

    def test_single_candidate(self, mock_cross_encoder):
        mock_cross_encoder.predict.return_value = np.array([0.85])

        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        candidates = [{"content": "Tek belge.", "source": "a.pdf", "score": 0.0}]
        results = reranker.rerank("test", candidates, top_k=5)

        assert len(results) == 1
        assert results[0]["score"] == 0.85

    def test_preserves_metadata(self, mock_cross_encoder, sample_candidates):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("test", sample_candidates, top_k=5)

        for r in results:
            assert "content" in r
            assert "source" in r


class TestRerankerInit:
    """Constructor testleri."""

    def test_default_model_from_config(self):
        reranker = CrossEncoderReranker()
        assert "reranker" in reranker.model_name.lower() or "bge" in reranker.model_name.lower()

    def test_custom_model(self):
        reranker = CrossEncoderReranker(model_name="custom/model")
        assert reranker.model_name == "custom/model"

    def test_custom_max_length(self):
        reranker = CrossEncoderReranker(max_length=256)
        assert reranker.max_length == 256

    def test_custom_batch_size(self):
        reranker = CrossEncoderReranker(batch_size=8)
        assert reranker.batch_size == 8

    def test_lazy_model_loading(self):
        reranker = CrossEncoderReranker()
        assert reranker._model is None
