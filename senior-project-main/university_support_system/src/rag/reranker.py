"""
Cross-Encoder Reranker — Turkce icin optimize

Ensemble retrieval sonuclarini cross-encoder modeli ile yeniden siralar.
Bi-encoder (embedding) modeller sorgu ve belgeyi bagimsiz vectorize eder,
cross-encoder ise sorgu-belge ciftini BIRLIKTE degerlendirir — bu nedenle
cok daha dogru relevanslik puani uretir.

Model: seroe/bge-reranker-v2-m3-turkish-triplet
  - BAAI/bge-reranker-v2-m3 uzerine Turkce triplet veriyle fine-tune
  - MAP: 0.79 (val), 0.789 (test)

Kullanim:
    from src.rag.reranker import CrossEncoderReranker

    reranker = CrossEncoderReranker()
    reranked = reranker.rerank("soru", candidates, top_k=5)
"""

from typing import Any, Dict, List, Optional

import structlog
from sentence_transformers import CrossEncoder

from src.core.config import settings

logger = structlog.get_logger()

DEFAULT_RERANKER_MODEL = "seroe/bge-reranker-v2-m3-turkish-triplet"


class CrossEncoderReranker:
    """
    Cross-encoder tabanli reranker.

    Lazy init: model ilk rerank() cagrisinda yuklenir.

    Args:
        model_name: HuggingFace model adi.
        max_length: Maksimum token uzunlugu (sorgu + belge).
        batch_size: Cross-encoder batch boyutu.
    """

    def __init__(
        self,
        model_name: str | None = None,
        max_length: int | None = None,
        batch_size: int | None = None,
    ):
        self.model_name = model_name or settings.reranker.model
        self.max_length = max_length or settings.reranker.max_length
        self.batch_size = batch_size or settings.reranker.batch_size
        self._model: Optional[CrossEncoder] = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            logger.info("loading_reranker_model", model=self.model_name)
            self._model = CrossEncoder(
                self.model_name,
                max_length=self.max_length,
            )
            logger.info("reranker_model_loaded", model=self.model_name)
        return self._model

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Adaylari cross-encoder ile yeniden siralar.

        Args:
            query: Kullanicinin orijinal sorusu.
            candidates: Ensemble'dan gelen aday belge listesi.
                Her dict'te en az "content" anahtari olmali.
            top_k: Dondurelecek sonuc sayisi.

        Returns:
            Cross-encoder skoruna gore siralanmis sonuclar.
        """
        if not candidates:
            return candidates

        pairs = [(query, c["content"]) for c in candidates]

        logger.debug(
            "reranking_start",
            candidate_count=len(candidates),
            model=self.model_name,
        )

        try:
            scores = self.model.predict(
                pairs,
                batch_size=self.batch_size,
                show_progress_bar=False,
            )
        except Exception:
            logger.exception("reranking_failed")
            return candidates[:top_k]

        for candidate, score in zip(candidates, scores):
            candidate["score"] = round(float(score), 4)

        candidates.sort(key=lambda c: c["score"], reverse=True)

        logger.debug(
            "reranking_complete",
            top_scores=[
                (c["source"], c["score"]) for c in candidates[:5]
            ],
        )

        return candidates[:top_k]
