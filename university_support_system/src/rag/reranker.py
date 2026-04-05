"""Cross-encoder reranker."""

from typing import Any, ClassVar, Dict, List, Optional

import structlog
import torch
from sentence_transformers import CrossEncoder

from src.core.config import settings
from src.core.profiling import profile_stage

logger = structlog.get_logger()

DEFAULT_RERANKER_MODEL = "seroe/bge-reranker-v2-m3-turkish-triplet"


class CrossEncoderReranker:
    """Cross-encoder tabanli reranker."""

    _MODEL_CACHE: ClassVar[dict[tuple[str, int, str, bool], CrossEncoder]] = {}

    @classmethod
    def clear_model_cache(cls) -> None:
        """Paylasilan reranker model cache'ini temizler."""
        cls._MODEL_CACHE.clear()

    def __init__(
        self,
        model_name: str | None = None,
        max_length: int | None = None,
        batch_size: int | None = None,
        device: str | None = None,
    ):
        self.model_name = model_name or settings.reranker.model
        self.max_length = max_length or settings.reranker.max_length
        self.batch_size = batch_size or settings.reranker.batch_size
        self.device = device or settings.reranker.device
        self.resolved_device = self._resolve_device(self.device)
        self._model: Optional[CrossEncoder] = None
        self.last_run_succeeded: Optional[bool] = None

    @staticmethod
    def _resolve_device(device: str) -> str:
        """Istenen cihazi mevcut ortama gore cozumler."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            cache_key = (
                self.model_name,
                self.max_length,
                self.resolved_device,
                settings.reranker.local_files_only,
            )
            cached_model = self._MODEL_CACHE.get(cache_key)
            if cached_model is not None:
                self._model = cached_model
                logger.info(
                    "reranker_model_cache_hit",
                    model=self.model_name,
                    requested_device=self.device,
                    resolved_device=self.resolved_device,
                    local_files_only=settings.reranker.local_files_only,
                )
                return self._model

            logger.info(
                "loading_reranker_model",
                model=self.model_name,
                requested_device=self.device,
                resolved_device=self.resolved_device,
            )
            with profile_stage(
                "rag.reranker.load_model",
                model=self.model_name,
                device=self.resolved_device,
            ):
                self._model = CrossEncoder(
                    self.model_name,
                    max_length=self.max_length,
                    device=self.resolved_device,
                    local_files_only=settings.reranker.local_files_only,
                )
                self._MODEL_CACHE[cache_key] = self._model
            logger.info(
                "reranker_model_loaded",
                model=self.model_name,
                requested_device=self.device,
                resolved_device=self.resolved_device,
                local_files_only=settings.reranker.local_files_only,
            )
        return self._model

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Adaylari cross-encoder ile yeniden siralar."""
        if not candidates:
            self.last_run_succeeded = None
            return candidates

        pairs = [(query, c["content"]) for c in candidates]

        logger.debug(
            "reranking_start",
            candidate_count=len(candidates),
            model=self.model_name,
        )

        try:
            with profile_stage(
                "rag.reranker.predict",
                candidate_count=len(candidates),
                top_k=top_k,
            ):
                scores = self.model.predict(
                    pairs,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                )
        except (OSError, RuntimeError, ValueError):
            self.last_run_succeeded = False
            logger.exception("reranking_failed")
            return candidates[:top_k]

        self.last_run_succeeded = True

        for candidate, score in zip(candidates, scores):
            candidate["score"] = round(float(score), 4)

        candidates.sort(key=lambda c: c["score"], reverse=True)

        logger.debug(
            "reranking_complete",
            top_scores=[(c["source"], c["score"]) for c in candidates[:5]],
        )

        return candidates[:top_k]
