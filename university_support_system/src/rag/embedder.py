"""Embedding uretici."""

from typing import ClassVar, List

import structlog
import torch
from sentence_transformers import SentenceTransformer

from src.core.config import settings
from src.core.profiling import profile_stage

logger = structlog.get_logger()

E5_QUERY_PREFIX = "query: "
E5_PASSAGE_PREFIX = "passage: "


class Embedder:
    """Metin embedding uretici."""

    _MODEL_CACHE: ClassVar[dict[tuple[str, str, bool], SentenceTransformer]] = {}

    @classmethod
    def clear_model_cache(cls) -> None:
        """Paylasilan embedding model cache'ini temizler."""
        cls._MODEL_CACHE.clear()

    def __init__(
        self,
        model_name: str | None = None,
        batch_size: int = 32,
        device: str | None = None,
    ):
        self.model_name = model_name or settings.embedding.model
        self.batch_size = batch_size
        self.device = device or settings.embedding.device
        self.resolved_device = self._resolve_device(self.device)
        self._model: SentenceTransformer | None = None

        model_lower = self.model_name.lower()
        self._is_e5_model = "e5" in model_lower
        self._is_bge_model = "bge" in model_lower

    @staticmethod
    def _resolve_device(device: str) -> str:
        """Istenen cihazi mevcut ortama gore cozumler."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device

    @property
    def model(self) -> SentenceTransformer:
        """Model'i lazy olarak yukler."""
        if self._model is None:
            cache_key = (
                self.model_name,
                self.resolved_device,
                settings.embedding.local_files_only,
            )
            cached_model = self._MODEL_CACHE.get(cache_key)
            if cached_model is not None:
                self._model = cached_model
                logger.info(
                    "embedding_model_cache_hit",
                    model=self.model_name,
                    requested_device=self.device,
                    resolved_device=self.resolved_device,
                    dimension=self._model.get_sentence_embedding_dimension(),
                    is_e5=self._is_e5_model,
                    is_bge=self._is_bge_model,
                    local_files_only=settings.embedding.local_files_only,
                )
                return self._model

            logger.info(
                "loading_embedding_model",
                model=self.model_name,
                requested_device=self.device,
                resolved_device=self.resolved_device,
            )
            with profile_stage(
                "rag.embedder.load_model",
                model=self.model_name,
                device=self.resolved_device,
            ):
                self._model = SentenceTransformer(
                    self.model_name,
                    device=self.resolved_device,
                    local_files_only=settings.embedding.local_files_only,
                )
                self._MODEL_CACHE[cache_key] = self._model
            logger.info(
                "embedding_model_loaded",
                model=self.model_name,
                requested_device=self.device,
                resolved_device=self.resolved_device,
                dimension=self._model.get_sentence_embedding_dimension(),
                is_e5=self._is_e5_model,
                is_bge=self._is_bge_model,
                local_files_only=settings.embedding.local_files_only,
            )
        return self._model

    @property
    def dimension(self) -> int:
        """Vektor boyutu."""
        return self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        """Metin listesini vektorlere donusturur."""
        if not texts:
            return []

        if self._is_e5_model:
            prefix = E5_QUERY_PREFIX if is_query else E5_PASSAGE_PREFIX
            texts = [f"{prefix}{t}" for t in texts]

        logger.info(
            "embedding_texts",
            count=len(texts),
            batch_size=self.batch_size,
            is_query=is_query,
        )

        try:
            with profile_stage(
                "rag.embedder.encode",
                count=len(texts),
                batch_size=self.batch_size,
                is_query=is_query,
            ):
                embeddings = self.model.encode(
                    texts,
                    batch_size=self.batch_size,
                    show_progress_bar=len(texts) > self.batch_size,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )
        except (OSError, RuntimeError, ValueError):
            logger.exception("embedding_failed", count=len(texts))
            raise

        result = [emb.tolist() for emb in embeddings]

        logger.info(
            "embedding_complete",
            count=len(result),
            dimension=len(result[0]) if result else 0,
        )

        return result

    def embed_single(self, text: str, is_query: bool = True) -> List[float]:
        """Tek bir metni vektore donusturur."""
        results = self.embed_texts([text], is_query=is_query)
        return results[0] if results else []
