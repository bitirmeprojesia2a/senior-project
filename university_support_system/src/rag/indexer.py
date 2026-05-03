"""
ChromaDB İndeksleyici

ChromaDB REST API ile iletişim kurar (httpx üzerinden).
Collection oluşturma, doküman ekleme ve benzerlik sorgusu yapar.

NOT: chromadb Python paketi yerine doğrudan REST API kullanılır.
     Bu sayede ek bağımlılık gerekmez ve her platformda çalışır.
     Mevcut repo, docker-compose içinde pinlenen ChromaDB 0.5.23 ile uyumlu REST uçlarını kullanır.

Kullanım:
    from src.rag.indexer import ChromaIndexer

    indexer = ChromaIndexer()
    from src.core.constants import Department, collection_name_for_department

    indexer.create_collection(collection_name_for_department(Department.STUDENT_AFFAIRS))
    indexer.add_documents(chunks, embeddings)
"""

from typing import Any, Dict, List, Optional

import httpx
import structlog

from src.core.config import settings

logger = structlog.get_logger()


class ChromaIndexer:
    """
    ChromaDB REST API client.

    Docker'da çalışan ChromaDB sunucusuna httpx ile bağlanır.
    Mevcut uygulama, repo içinde pinli ChromaDB 0.5.23 REST sözleşmesine göre çalışır.

    Args:
        base_url: ChromaDB sunucu URL'si. None ise config'den okunur.
        collection_name: Varsayılan koleksiyon adı.
    """

    def __init__(
        self,
        base_url: str | None = None,
        collection_name: str | None = None,
    ):
        self.base_url = base_url or settings.chroma.url
        self.collection_name = collection_name
        self._client = httpx.Client(base_url=self.base_url, timeout=30.0)
        self._collection_id: Optional[str] = None

    # ── Collection Yönetimi ──────────────────────

    def create_collection(self, name: str | None = None) -> str:
        """
        Koleksiyon oluşturur veya mevcut olanı döndürür.

        Returns:
            Collection ID.
        """
        col_name = name or self.collection_name
        if not col_name:
            raise ValueError("Koleksiyon adi belirtilmeli.")

        # Önce mevcut mu kontrol et
        try:
            response = self._client.get("/api/v1/collections")
            response.raise_for_status()
            existing = response.json()

            for col in existing:
                if col["name"] == col_name:
                    self._collection_id = col["id"]
                    logger.info("collection_exists", name=col_name, id=self._collection_id)
                    return self._collection_id
        except httpx.HTTPStatusError as e:
            logger.warning("list_collections_failed", status=e.response.status_code, body=e.response.text[:200])

        # Yeni oluştur
        response = self._client.post(
            "/api/v1/collections",
            json={
                "name": col_name,
                "metadata": {"department": self._infer_department_from_collection_name(col_name)},
            },
        )

        if response.status_code not in (200, 201):
            logger.error("create_collection_failed", status=response.status_code, body=response.text[:300])
            response.raise_for_status()

        data = response.json()
        self._collection_id = data["id"]
        logger.info("collection_created", name=col_name, id=self._collection_id)
        return self._collection_id

    def delete_collection(self, name: str | None = None) -> bool:
        """Koleksiyonu siler."""
        col_name = name or self.collection_name
        if not col_name:
            raise ValueError("Silinecek koleksiyon adi belirtilmeli.")
        try:
            # ChromaDB 0.5.x'te silme işlemi name ile yapılır ve REST path'i /api/v1/collections/{name} şeklindedir
            response = self._client.delete(f"/api/v1/collections/{col_name}")
            if response.status_code == 200:
                self._collection_id = None
                logger.info("collection_deleted", name=col_name)
                return True
            logger.warning("collection_delete_failed", name=col_name, status=response.status_code)
            return False
        except httpx.HTTPError as e:
            logger.warning("collection_not_found", name=col_name, error=str(e))
            return False

    def get_collection_id(self) -> str:
        """Mevcut koleksiyon ID'sini döndürür, yoksa oluşturur."""
        if not self.collection_name:
            raise ValueError("Koleksiyon adi belirtilmeden islem yapilamaz.")
        if self._collection_id is None:
            self.create_collection()
        return self._collection_id  # type: ignore[return-value]

    # ── Doküman İşlemleri ────────────────────────

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]] | None = None,
    ) -> None:
        """
        Chunk'ları koleksiyona ekler.

        Args:
            ids: Benzersiz chunk ID'leri.
            documents: Chunk metinleri.
            embeddings: Vektörler.
            metadatas: Metadata listesi (opsiyonel).
        """
        self._batch_write("add", ids, documents, embeddings, metadatas)

    def upsert_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]] | None = None,
    ) -> None:
        """
        Chunk'ları koleksiyona ekler veya günceller (idempotent).

        Aynı ID'ye sahip chunk varsa güncellenir, yoksa eklenir.
        Hash tabanlı ID kullanıldığında aynı içerik tekrar indekslenmez.
        """
        self._batch_write("upsert", ids, documents, embeddings, metadatas)

    def _batch_write(
        self,
        operation: str,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]] | None = None,
    ) -> None:
        """Batch halinde add veya upsert yapar."""
        collection_id = self.get_collection_id()
        self._validate_write_payload(ids, documents, embeddings, metadatas)

        clean_metadatas = None
        if metadatas:
            clean_metadatas = [self._clean_metadata(m) for m in metadatas]

        batch_size = 100
        total_written = 0

        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_docs = documents[i:i + batch_size]
            batch_embs = embeddings[i:i + batch_size]
            batch_meta = clean_metadatas[i:i + batch_size] if clean_metadatas else None

            payload: Dict[str, Any] = {
                "ids": batch_ids,
                "documents": batch_docs,
                "embeddings": batch_embs,
            }
            if batch_meta:
                payload["metadatas"] = batch_meta

            response = self._client.post(
                f"/api/v1/collections/{collection_id}/{operation}",
                json=payload,
            )
            response.raise_for_status()
            total_written += len(batch_ids)

            logger.debug(
                f"batch_{operation}",
                batch=i // batch_size + 1,
                count=len(batch_ids),
                total=total_written,
            )

        logger.info(f"documents_{operation}", total=total_written, collection=self.collection_name)

    @staticmethod
    def _validate_write_payload(
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]] | None,
    ) -> None:
        """Validate payload shape before sending a batch to Chroma."""
        if not (len(ids) == len(documents) == len(embeddings)):
            raise ValueError(
                "Chroma write payload length mismatch: "
                f"ids={len(ids)}, documents={len(documents)}, embeddings={len(embeddings)}"
            )
        if metadatas is not None and len(metadatas) != len(ids):
            raise ValueError(
                "Chroma write metadata length mismatch: "
                f"ids={len(ids)}, metadatas={len(metadatas)}"
            )
        if not ids:
            return

        expected_dimension = len(embeddings[0])
        if expected_dimension <= 0:
            raise ValueError("Chroma write payload contains an empty embedding vector")

        bad_embedding = next(
            (
                (index, len(vector))
                for index, vector in enumerate(embeddings)
                if len(vector) != expected_dimension
            ),
            None,
        )
        if bad_embedding is not None:
            index, actual_dimension = bad_embedding
            raise ValueError(
                "Chroma write embedding dimension mismatch: "
                f"expected={expected_dimension}, index={index}, actual={actual_dimension}"
            )

    @staticmethod
    def _infer_department_from_collection_name(collection_name: str) -> str:
        """Koleksiyon adından departman değerini çıkarır."""
        if collection_name.endswith("_docs"):
            return collection_name[:-5]
        return collection_name

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Benzerlik sorgusu yapar.

        Args:
            query_embedding: Sorgu vektörü.
            n_results: Döndürülecek sonuç sayısı.
            where: Metadata filtreleme (opsiyonel).

        Returns:
            ChromaDB sorgu sonucu.
        """
        collection_id = self.get_collection_id()

        payload: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            payload["where"] = where

        response = self._client.post(
            f"/api/v1/collections/{collection_id}/query",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def get_all(self) -> Dict[str, Any]:
        """
        Koleksiyondaki tüm dokümanları ve metadataları getirir.
        BM25 gibi in-memory çalışan arama motorlarını beslemek için kullanılır.
        """
        collection_id = self.get_collection_id()
        response = self._client.post(
            f"/api/v1/collections/{collection_id}/get",
            json={
                "include": ["documents", "metadatas"]
            },
        )
        response.raise_for_status()
        return response.json()

    def count(self) -> int:
        """Koleksiyondaki doküman sayısını döndürür."""
        collection_id = self.get_collection_id()
        response = self._client.get(
            f"/api/v1/collections/{collection_id}/count",
        )
        response.raise_for_status()
        return response.json()

    # ── Yardımcılar ──────────────────────────────

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Metadata'yı ChromaDB uyumlu hale getirir.
        Sadece string, int, float, bool kabul edilir.
        """
        clean: Dict[str, str] = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean[key] = value  # type: ignore[assignment]
            else:
                clean[key] = str(value)
        return clean

    def close(self) -> None:
        """HTTP client'ı kapatır."""
        self._client.close()

    def health_check(self) -> bool:
        """ChromaDB sunucusu erişilebilir mi?"""
        try:
            response = self._client.get("/api/v1/heartbeat")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
