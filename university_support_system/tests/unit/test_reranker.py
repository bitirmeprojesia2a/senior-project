"""
CrossEncoderReranker Unit Testleri

Cross-encoder modelini mock'layarak reranking mantığını test eder.
"""

from unittest.mock import MagicMock, patch, PropertyMock
import numpy as np

import pytest

from src.core.config import settings
from src.rag.reranker import (
    CrossEncoderReranker,
    _CALIBRATION_SCALE,
    _CALIBRATION_SHIFT,
)


def _calibrated_score(raw_logit: float) -> float:
    adjusted = (raw_logit - _CALIBRATION_SHIFT) / _CALIBRATION_SCALE
    if adjusted >= 0:
        prob = 1.0 / (1.0 + np.exp(-adjusted))
    else:
        exp_adjusted = np.exp(adjusted)
        prob = exp_adjusted / (1.0 + exp_adjusted)
    return round(float(prob), 4)


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
        assert reranker.last_run_succeeded is True

    def test_top_k_limits_results(self, mock_cross_encoder, sample_candidates):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("ÇAP başvurusu", sample_candidates, top_k=3)

        assert len(results) == 3

    def test_scores_assigned_correctly(self, mock_cross_encoder, sample_candidates):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("ÇAP başvurusu", sample_candidates, top_k=5)

        assert results[0]["score"] == _calibrated_score(0.9)
        assert results[1]["score"] == _calibrated_score(0.7)
        assert results[0]["metadata"]["score_type"] == "reranker"
        assert results[0]["metadata"]["raw_reranker_logit"] == 0.9
        assert results[0]["metadata"]["reranker_score"] == _calibrated_score(0.9)
        assert results[0]["metadata"]["pre_rerank_score"] == 0.0

    def test_empty_candidates(self, mock_cross_encoder):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("test", [], top_k=5)

        assert results == []
        mock_cross_encoder.predict.assert_not_called()
        assert reranker.last_run_succeeded is None

    def test_single_candidate(self, mock_cross_encoder):
        mock_cross_encoder.predict.return_value = np.array([0.85])

        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        candidates = [{"content": "Tek belge.", "source": "a.pdf", "score": 0.0}]
        results = reranker.rerank("test", candidates, top_k=5)

        assert len(results) == 1
        assert results[0]["score"] == _calibrated_score(0.85)
        assert reranker.last_run_succeeded is True

    def test_preserves_metadata(self, mock_cross_encoder, sample_candidates):
        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("test", sample_candidates, top_k=5)

        for r in results:
            assert "content" in r
            assert "source" in r
        assert reranker.last_run_succeeded is True

    def test_sets_failure_flag_when_predict_raises(self, mock_cross_encoder, sample_candidates):
        mock_cross_encoder.predict.side_effect = RuntimeError("predict failed")

        reranker = CrossEncoderReranker()
        reranker._model = mock_cross_encoder

        results = reranker.rerank("test", sample_candidates, top_k=3)

        assert len(results) == 3
        assert reranker.last_run_succeeded is False


class TestRerankerInit:
    """Constructor testleri."""

    def test_default_model_from_config(self):
        reranker = CrossEncoderReranker()
        assert reranker.model_name == settings.reranker.model

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

    def test_auto_device_resolves_to_cpu_when_cuda_unavailable(self):
        with patch("src.rag.reranker.torch.cuda.is_available", return_value=False):
            reranker = CrossEncoderReranker()

        assert reranker.device == "auto"
        assert reranker.resolved_device == "cpu"

    def test_auto_device_resolves_to_cuda_when_available(self):
        with patch("src.rag.reranker.torch.cuda.is_available", return_value=True):
            reranker = CrossEncoderReranker()

        assert reranker.resolved_device == "cuda"

    def test_custom_device_is_preserved(self):
        reranker = CrossEncoderReranker(device="cpu")
        assert reranker.device == "cpu"
        assert reranker.resolved_device == "cpu"

    def test_model_loader_passes_resolved_device(self):
        with patch("src.rag.reranker.CrossEncoder") as mock_cross_encoder:
            mock_cross_encoder.return_value = MagicMock()

            reranker = CrossEncoderReranker(model_name="custom/model", max_length=256, device="cpu")
            _ = reranker.model

        mock_cross_encoder.assert_called_once_with(
            "custom/model",
            max_length=256,
            device="cpu",
            local_files_only=True,
        )
