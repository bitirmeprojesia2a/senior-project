"""
Embedder Unit Testleri

Embedding modelini mock'layarak prefix mantığı, batch işleme
ve edge case'leri test eder.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import numpy as np
import pytest

from src.rag.embedder import E5_PASSAGE_PREFIX, E5_QUERY_PREFIX, Embedder


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer modeli."""
    model = MagicMock()
    model.encode.return_value = np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ])
    model.get_sentence_embedding_dimension.return_value = 3
    return model


class TestEmbedderInit:
    """Constructor testleri."""

    def test_default_model_from_config(self):
        embedder = Embedder()
        assert embedder.model_name is not None
        assert len(embedder.model_name) > 0

    def test_custom_model(self):
        embedder = Embedder(model_name="custom/model")
        assert embedder.model_name == "custom/model"

    def test_lazy_model_loading(self):
        embedder = Embedder()
        assert embedder._model is None

    def test_e5_model_detected(self):
        embedder = Embedder(model_name="intfloat/multilingual-e5-base")
        assert embedder._is_e5_model is True
        assert embedder._is_bge_model is False

    def test_bge_model_detected(self):
        embedder = Embedder(model_name="BAAI/bge-m3")
        assert embedder._is_bge_model is True
        assert embedder._is_e5_model is False

    def test_unknown_model_no_prefix(self):
        embedder = Embedder(model_name="some/random-model")
        assert embedder._is_e5_model is False
        assert embedder._is_bge_model is False

    def test_auto_device_resolves_to_cpu_when_cuda_unavailable(self):
        with patch("src.rag.embedder.torch.cuda.is_available", return_value=False):
            embedder = Embedder()

        assert embedder.device == "auto"
        assert embedder.resolved_device == "cpu"

    def test_auto_device_resolves_to_cuda_when_available(self):
        with patch("src.rag.embedder.torch.cuda.is_available", return_value=True):
            embedder = Embedder()

        assert embedder.resolved_device == "cuda"

    def test_custom_device_is_preserved(self):
        embedder = Embedder(device="cpu")
        assert embedder.device == "cpu"
        assert embedder.resolved_device == "cpu"

    def test_model_loader_passes_resolved_device(self):
        with patch("src.rag.embedder.SentenceTransformer") as mock_transformer:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 3
            mock_transformer.return_value = mock_model

            embedder = Embedder(model_name="BAAI/bge-m3", device="cpu")
            _ = embedder.model

        mock_transformer.assert_called_once_with("BAAI/bge-m3", device="cpu")


class TestEmbedTexts:
    """embed_texts() metodu testleri."""

    def test_returns_vectors(self, mock_sentence_transformer):
        embedder = Embedder(model_name="BAAI/bge-m3")
        embedder._model = mock_sentence_transformer

        results = embedder.embed_texts(["metin 1", "metin 2"])

        assert len(results) == 2
        assert len(results[0]) == 3

    def test_empty_list_returns_empty(self, mock_sentence_transformer):
        embedder = Embedder(model_name="BAAI/bge-m3")
        embedder._model = mock_sentence_transformer

        results = embedder.embed_texts([])

        assert results == []
        mock_sentence_transformer.encode.assert_not_called()

    def test_e5_query_prefix_added(self, mock_sentence_transformer):
        mock_sentence_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        embedder = Embedder(model_name="intfloat/multilingual-e5-base")
        embedder._model = mock_sentence_transformer

        embedder.embed_texts(["test sorusu"], is_query=True)

        call_args = mock_sentence_transformer.encode.call_args
        texts_passed = call_args[0][0]
        assert texts_passed[0].startswith(E5_QUERY_PREFIX)

    def test_e5_passage_prefix_added(self, mock_sentence_transformer):
        mock_sentence_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        embedder = Embedder(model_name="intfloat/multilingual-e5-base")
        embedder._model = mock_sentence_transformer

        embedder.embed_texts(["belge içeriği"], is_query=False)

        call_args = mock_sentence_transformer.encode.call_args
        texts_passed = call_args[0][0]
        assert texts_passed[0].startswith(E5_PASSAGE_PREFIX)

    def test_bge_no_prefix_added(self, mock_sentence_transformer):
        mock_sentence_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        embedder = Embedder(model_name="BAAI/bge-m3")
        embedder._model = mock_sentence_transformer

        embedder.embed_texts(["test metni"], is_query=True)

        call_args = mock_sentence_transformer.encode.call_args
        texts_passed = call_args[0][0]
        assert texts_passed[0] == "test metni"

    def test_normalize_embeddings_enabled(self, mock_sentence_transformer):
        mock_sentence_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        embedder = Embedder(model_name="BAAI/bge-m3")
        embedder._model = mock_sentence_transformer

        embedder.embed_texts(["test"])

        call_args = mock_sentence_transformer.encode.call_args
        assert call_args[1]["normalize_embeddings"] is True


class TestEmbedSingle:
    """embed_single() metodu testleri."""

    def test_returns_single_vector(self, mock_sentence_transformer):
        mock_sentence_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        embedder = Embedder(model_name="BAAI/bge-m3")
        embedder._model = mock_sentence_transformer

        result = embedder.embed_single("test metni")

        assert isinstance(result, list)
        assert len(result) == 3

    def test_default_is_query_true(self, mock_sentence_transformer):
        mock_sentence_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        embedder = Embedder(model_name="intfloat/multilingual-e5-base")
        embedder._model = mock_sentence_transformer

        embedder.embed_single("sorgu metni")

        call_args = mock_sentence_transformer.encode.call_args
        texts_passed = call_args[0][0]
        assert texts_passed[0].startswith(E5_QUERY_PREFIX)
