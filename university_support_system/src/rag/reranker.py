"""Cross-encoder reranker."""

from typing import Any, ClassVar, Dict, List, Optional
import math

import structlog
import torch
from sentence_transformers import CrossEncoder

from src.core.config import settings
from src.core.profiling import profile_stage

logger = structlog.get_logger()

DEFAULT_RERANKER_MODEL = "nreimers/mmarco-mMiniLMv2-L6-H384-v1"

# Reranker logit kalibrasyon parametreleri.
# L6 degerleri kaybolmasin: nreimers/mmarco-mMiniLMv2-L6-H384-v1 icin
# hesaplandi (40 soru, 400 aday). analyze_reranker_scores.py --all-profiles
# ciktisina dayanir. Eski degerler (ms-marco-MiniLM-L-6-v2):
# shift=1.2356, scale=6.0418
_CALIBRATION_BY_MODEL: dict[str, tuple[float, float]] = {
    "nreimers/mmarco-mminilmv2-l6-h384-v1": (0.0687, 0.5),
    # BGE FP16: analyze_reranker_scores.py --all-profiles
    # docs/archive/benchmarks/bge_fp16_reranker_score_analysis.json
    "baai/bge-reranker-v2-m3": (0.0652, 0.5),
    "cross-encoder/mmarco-mminilmv2-l12-h384-v1": (0.0, 1.0),
}

# Backward-compatible aliases for tests and callers that still import the
# original module-level constants directly. The L6 values remain preserved
# in _CALIBRATION_BY_MODEL; these aliases reflect the currently configured
# model so mocked rerank tests and runtime behavior stay aligned.
_CALIBRATION_SHIFT, _CALIBRATION_SCALE = _CALIBRATION_BY_MODEL.get(
    settings.reranker.model.lower(),
    (0.0, 1.0),
)


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
        self.torch_dtype = self._resolve_torch_dtype(settings.reranker.torch_dtype)
        self.calibration_shift, self.calibration_scale = self._calibration_for_model(self.model_name)
        self._model: Optional[CrossEncoder] = None
        self.last_run_succeeded: Optional[bool] = None

    @staticmethod
    def _resolve_device(device: str) -> str:
        """Istenen cihazi mevcut ortama gore cozumler."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device

    def _resolve_torch_dtype(self, dtype_name: str) -> torch.dtype | None:
        """Model agirlik hassasiyetini cozumler; CPU icin FP32 varsayilir."""
        if dtype_name == "auto":
            return None
        if self.resolved_device != "cuda" and dtype_name in {"float16", "bfloat16"}:
            logger.warning(
                "reranker_dtype_ignored_for_cpu",
                requested_dtype=dtype_name,
                resolved_device=self.resolved_device,
            )
            return None
        if dtype_name == "float16":
            return torch.float16
        if dtype_name == "bfloat16":
            return torch.bfloat16
        return torch.float32

    @staticmethod
    def _calibration_for_model(model_name: str) -> tuple[float, float]:
        """Modele ozel logit kalibrasyon parametrelerini dondurur."""
        return _CALIBRATION_BY_MODEL.get(model_name.lower(), (0.0, 1.0))

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            cache_key = (
                self.model_name,
                self.max_length,
                self.resolved_device,
                str(self.torch_dtype),
                settings.reranker.local_files_only,
            )
            cached_model = self._MODEL_CACHE.get(cache_key)
            if settings.cache.enabled and settings.cache.reranker_model_cache_enabled and cached_model is not None:
                self._model = cached_model
                logger.info(
                    "reranker_model_cache_hit",
                    model=self.model_name,
                    requested_device=self.device,
                    resolved_device=self.resolved_device,
                    torch_dtype=str(self.torch_dtype),
                    local_files_only=settings.reranker.local_files_only,
                )
                return self._model

            logger.info(
                "loading_reranker_model",
                model=self.model_name,
                requested_device=self.device,
                resolved_device=self.resolved_device,
                torch_dtype=str(self.torch_dtype),
            )
            with profile_stage(
                "rag.reranker.load_model",
                model=self.model_name,
                device=self.resolved_device,
            ):
                automodel_args = {}
                if self.torch_dtype is not None:
                    automodel_args["torch_dtype"] = self.torch_dtype
                cross_encoder_kwargs = {
                    "max_length": self.max_length,
                    "device": self.resolved_device,
                    "local_files_only": settings.reranker.local_files_only,
                }
                if automodel_args:
                    cross_encoder_kwargs["automodel_args"] = automodel_args
                self._model = CrossEncoder(self.model_name, **cross_encoder_kwargs)
                if settings.cache.enabled and settings.cache.reranker_model_cache_enabled:
                    self._MODEL_CACHE[cache_key] = self._model
            logger.info(
                "reranker_model_loaded",
                model=self.model_name,
                requested_device=self.device,
                resolved_device=self.resolved_device,
                torch_dtype=str(self.torch_dtype),
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
            raw_logit = float(score)
            adjusted = (raw_logit - self.calibration_shift) / self.calibration_scale
            prob = 1.0 / (1.0 + math.exp(-adjusted)) if adjusted >= 0 else math.exp(adjusted) / (1.0 + math.exp(adjusted))
            reranker_score = round(prob, 4)

            metadata = candidate.setdefault("metadata", {})
            metadata["pre_rerank_score"] = round(float(candidate.get("score", 0.0)), 4)
            metadata["raw_reranker_logit"] = round(raw_logit, 4)
            metadata["reranker_calibration_shift"] = self.calibration_shift
            metadata["reranker_calibration_scale"] = self.calibration_scale
            metadata["reranker_score"] = reranker_score
            metadata["score_type"] = "reranker"
            candidate["score"] = reranker_score

        candidates.sort(key=lambda c: c["score"], reverse=True)

        logger.info(
            "reranking_complete",
            query=query[:80],
            top_scores=[(c.get("source", "?"), round(c["score"], 4)) for c in candidates[:5]],
        )

        return candidates[:top_k]
