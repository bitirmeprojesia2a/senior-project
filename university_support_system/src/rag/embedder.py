"""
Embedding Uretici — v2

Metinleri vektor temsillerine donusturur.
sentence-transformers kutuphanesini kullanir.

Desteklenen Modeller:
    - BAAI/bge-m3: 1024-D, 8192 token, dense+sparse, prefix GEREKSIZ
    - intfloat/multilingual-e5-base: 768-D, 514 token, "query:"/"passage:" prefix GEREKLI
    - intfloat/multilingual-e5-large: 1024-D, 514 token, "query:"/"passage:" prefix GEREKLI

Kullanim:
    from src.rag.embedder import Embedder

    embedder = Embedder()
    vectors = embedder.embed_texts(["Harc borcu", "Ders kaydi"])
"""

from typing import List

from sentence_transformers import SentenceTransformer
import structlog

from src.core.config import settings

logger = structlog.get_logger()

E5_QUERY_PREFIX = "query: "
E5_PASSAGE_PREFIX = "passage: "


class Embedder:
    """
    Metin embedding uretici.

    Model ilk kullanimda yuklenir (lazy init).
    E5 modelleri icin otomatik prefix eklenir,
    diger modeller (BGE-M3 vb.) prefix gerektirmez.

    Args:
        model_name: Hugging Face model adi. None ise config'den okunur.
        batch_size: Toplu embedding uretim boyutu.
    """

    def __init__(
        self,
        model_name: str | None = None,
        batch_size: int = 32,
    ):
        self.model_name = model_name or settings.embedding.model
        self.batch_size = batch_size
        self._model: SentenceTransformer | None = None

        model_lower = self.model_name.lower()
        self._is_e5_model = "e5" in model_lower
        self._is_bge_model = "bge" in model_lower

    @property
    def model(self) -> SentenceTransformer:
        """Model'i lazy olarak yukler."""
        if self._model is None:
            logger.info("loading_embedding_model", model=self.model_name)
            self._model = SentenceTransformer(self.model_name)
            logger.info(
                "embedding_model_loaded",
                model=self.model_name,
                dimension=self._model.get_sentence_embedding_dimension(),
                is_e5=self._is_e5_model,
                is_bge=self._is_bge_model,
            )
        return self._model

    @property
    def dimension(self) -> int:
        """Vektor boyutu."""
        return self.model.get_sentence_embedding_dimension()

    def embed_texts(
        self, texts: List[str], is_query: bool = False
    ) -> List[List[float]]:
        """
        Metin listesini vektorlere donusturur.

        Args:
            texts: Metin listesi.
            is_query: True ise sorgu, False ise belge olarak isler.
                      (Sadece E5 modelleri icin prefix eklenir)

        Returns:
            Vektor listesi.
        """
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
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=len(texts) > self.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        except Exception:
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
        """
        Tek bir metni vektore donusturur.

        Args:
            text: Vektorlenecek metin.
            is_query: True ise sorgu olarak (varsayilan), False ise belge olarak isler.

        Returns:
            Vektor (dimension boyutlu float listesi).
        """
        results = self.embed_texts([text], is_query=is_query)
        return results[0] if results else []
