"""Chroma indexer payload validation tests."""

import pytest

from src.rag.indexer import ChromaIndexer


class TestChromaIndexerPayloadValidation:
    def test_accepts_consistent_payload(self):
        ChromaIndexer._validate_write_payload(
            ids=["1", "2"],
            documents=["a", "b"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            metadatas=[{"source": "a.txt"}, {"source": "b.txt"}],
        )

    def test_rejects_length_mismatch(self):
        with pytest.raises(ValueError, match="payload length mismatch"):
            ChromaIndexer._validate_write_payload(
                ids=["1", "2"],
                documents=["a"],
                embeddings=[[0.1, 0.2], [0.3, 0.4]],
                metadatas=None,
            )

    def test_rejects_metadata_length_mismatch(self):
        with pytest.raises(ValueError, match="metadata length mismatch"):
            ChromaIndexer._validate_write_payload(
                ids=["1", "2"],
                documents=["a", "b"],
                embeddings=[[0.1, 0.2], [0.3, 0.4]],
                metadatas=[{"source": "a.txt"}],
            )

    def test_rejects_empty_embedding_vector(self):
        with pytest.raises(ValueError, match="empty embedding"):
            ChromaIndexer._validate_write_payload(
                ids=["1"],
                documents=["a"],
                embeddings=[[]],
                metadatas=None,
            )

    def test_rejects_embedding_dimension_mismatch(self):
        with pytest.raises(ValueError, match="embedding dimension mismatch"):
            ChromaIndexer._validate_write_payload(
                ids=["1", "2"],
                documents=["a", "b"],
                embeddings=[[0.1, 0.2], [0.3]],
                metadatas=None,
            )
