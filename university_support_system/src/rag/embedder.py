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
        batch_size: int | None = None,
        device: str | None = None,
    ):
        self.model_name = model_name or settings.embedding.model
        self.batch_size = batch_size or settings.embedding.batch_size
        self.device = device or settings.embedding.device
        self.resolved_device = self._resolve_device(self.device)
        self._model: SentenceTransformer | None = None

        model_lower = self.model_name.lower()
        self._is_e5_model = "e5" in model_lower
        self._is_bge_model = "bge" in model_lower
        self._config_dimension_validated = False

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
            if settings.cache.enabled and settings.cache.embedding_model_cache_enabled and cached_model is not None:
                self._model = cached_model
                self._validate_configured_dimension()
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
                self._validate_configured_dimension()
                if settings.cache.enabled and settings.cache.embedding_model_cache_enabled:
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

    def _validate_configured_dimension(self) -> None:
        """Fail fast when the configured dimension does not match the loaded model."""
        if self._model is None or self._config_dimension_validated:
            return

        actual_dimension = int(self._model.get_sentence_embedding_dimension())
        expected_dimension = int(settings.embedding.dimension)
        if expected_dimension > 0 and actual_dimension != expected_dimension:
            raise ValueError(
                "Embedding model dimension mismatch: "
                f"model={self.model_name!r} actual={actual_dimension} configured={expected_dimension}. "
                "Update EMBEDDING_DIMENSION or reindex with the intended model."
            )

        self._config_dimension_validated = True

    def _switch_to_cpu_after_cuda_failure(self) -> bool:
        """Move embedding generation to CPU when CUDA state becomes unsafe."""
        if self.resolved_device != "cuda" or not settings.embedding.cuda_fallback_to_cpu:
            return False

        logger.warning(
            "embedding_cuda_failed_falling_back_to_cpu",
            model=self.model_name,
            batch_size=self.batch_size,
        )
        self._model = None
        self.resolved_device = "cpu"
        self.device = "cpu"
        self._config_dimension_validated = False
        return True

    def _encode_texts(self, texts: List[str], *, is_query: bool):
        with profile_stage(
            "rag.embedder.encode",
            count=len(texts),
            batch_size=self.batch_size,
            is_query=is_query,
            device=self.resolved_device,
        ):
            return self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=len(texts) > self.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

    @property
    def dimension(self) -> int:
        """Vektor boyutu."""
        return self.model.get_sentence_embedding_dimension()

    @staticmethod
    def _validate_embedding_batch(
        *,
        input_count: int,
        embeddings: List[List[float]],
        expected_dimension: int,
    ) -> None:
        """Ensure model output can safely be written to/query Chroma."""
        if len(embeddings) != input_count:
            raise ValueError(
                f"Embedding count mismatch: input_count={input_count}, output_count={len(embeddings)}"
            )

        bad_dimensions = {
            index: len(vector)
            for index, vector in enumerate(embeddings)
            if len(vector) != expected_dimension
        }
        if bad_dimensions:
            first_index, first_dimension = next(iter(bad_dimensions.items()))
            raise ValueError(
                "Embedding dimension mismatch in batch: "
                f"expected={expected_dimension}, first_bad_index={first_index}, first_bad_dimension={first_dimension}"
            )

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
            embeddings = self._encode_texts(texts, is_query=is_query)
        except RuntimeError:
            if not self._switch_to_cpu_after_cuda_failure():
                logger.exception("embedding_failed", count=len(texts))
                raise
            embeddings = self._encode_texts(texts, is_query=is_query)
        except (OSError, ValueError):
            logger.exception("embedding_failed", count=len(texts))
            raise

        result = [emb.tolist() for emb in embeddings]
        self._validate_embedding_batch(
            input_count=len(texts),
            embeddings=result,
            expected_dimension=self.dimension,
        )

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
