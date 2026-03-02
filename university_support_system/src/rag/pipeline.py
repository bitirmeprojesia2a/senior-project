"""
RAG Indeksleme Pipeline — v2

Tum adimlari birlestirir:
    1. Dosya yukleme (PDF + TXT)
    2. Metin temizleme (header/footer, sayfa numaralari, belge kalintilari)
    3. Chunk'lama (MADDE-aware, madde basligi korunur)
    4. Embedding uretimi (BAAI/bge-m3, 1024-D)
    5. ChromaDB'ye indeksleme

Kullanim:
    from src.rag.pipeline import IndexingPipeline

    pipeline = IndexingPipeline()
    stats = pipeline.run("data/raw/student_affairs/")
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from tqdm import tqdm
import structlog

from src.rag.document_loader import DocumentLoader
from src.rag.text_preprocessor import TextPreprocessor
from src.rag.chunker import TextChunker, Chunk
from src.rag.embedder import Embedder
from src.rag.indexer import ChromaIndexer

logger = structlog.get_logger()


class IndexingPipeline:
    """
    Doküman indeksleme pipeline'ı.

    Args:
        chunk_size: Chunk boyutu (karakter). Varsayılan: 1024
        chunk_overlap: Chunk örtüşme (karakter). Varsayılan: 128
        collection_name: ChromaDB koleksiyon adı.
        embedding_model: Embedding modeli. None ise config'den.
        chroma_url: ChromaDB URL'si. None ise config'den.
    """

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        collection_name: str = "student_affairs_docs",
        embedding_model: str | None = None,
        chroma_url: str | None = None,
    ):
        self.loader = DocumentLoader()
        self.preprocessor = TextPreprocessor()
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedder = Embedder(model_name=embedding_model)
        self.indexer = ChromaIndexer(
            base_url=chroma_url,
            collection_name=collection_name,
        )

    def run(
        self,
        source_dir: str | Path,
        reindex: bool = False,
    ) -> Dict[str, Any]:
        """
        Pipeline'ı çalıştırır.

        Args:
            source_dir: Kaynak dosyaların klasörü.
            reindex: True ise mevcut koleksiyonu silip yeniden oluşturur.

        Returns:
            İndeksleme istatistikleri.
        """
        source_dir = Path(source_dir)
        logger.info("pipeline_start", source=str(source_dir), reindex=reindex)

        # 1. Koleksiyon hazırlığı
        if reindex:
            logger.info("deleting_existing_collection")
            self.indexer.delete_collection()
        self.indexer.create_collection()

        # 2. Dosyaları yükle
        print("\n📂 Dosyalar yükleniyor...")
        documents = self.loader.load_directory(source_dir)
        if not documents:
            logger.error("no_documents_found", path=str(source_dir))
            return {"error": "Hiç dosya bulunamadı"}

        print(f"   ✅ {len(documents)} dosya yüklendi")

        # 3. Metin temizleme
        print("🧹 Metinler temizleniyor...")
        for doc in tqdm(documents, desc="   Temizleme"):
            doc.content = self.preprocessor.clean(doc.content)

        # Temizleme sonrası boş olanları filtrele
        documents = [d for d in documents if d.content.strip()]
        print(f"   ✅ {len(documents)} dosya temizlendi")

        # 4. Chunk'lama
        print("✂️  Chunk'lara ayrılıyor...")
        chunks = self.chunker.split_documents(documents)
        chunk_stats = self.chunker.get_stats(chunks)
        print(f"   ✅ {chunk_stats['total']} chunk oluşturuldu (ort: {chunk_stats.get('avg_size', 0)} karakter)")

        if not chunks:
            return {"error": "Chunk oluşturulamadı"}

        # 5. Embedding üretimi — is_query=False (belge/passage olarak işle)
        print("🧠 Embedding'ler üretiliyor...")
        print(f"   Model: {self.embedder.model_name}")
        chunk_texts = [c.content for c in chunks]
        try:
            embeddings = self.embedder.embed_texts(chunk_texts, is_query=False)
        except Exception:
            logger.exception("embedding_generation_failed")
            return {"error": "Embedding üretimi başarısız"}
        print(f"   ✅ {len(embeddings)} vektör üretildi ({self.embedder.dimension} boyut)")

        # 6. ChromaDB'ye indeksle (hash tabanlı ID — idempotent)
        print("💾 ChromaDB'ye indeksleniyor...")
        metadatas = [c.metadata for c in chunks]
        ids = self._generate_content_hash_ids(chunk_texts, metadatas)

        try:
            if reindex:
                self.indexer.add_documents(
                    ids=ids,
                    documents=chunk_texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
            else:
                self.indexer.upsert_documents(
                    ids=ids,
                    documents=chunk_texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
        except Exception:
            logger.exception("indexing_failed")
            return {"error": "ChromaDB indeksleme başarısız"}

        total_in_db = self.indexer.count()
        print(f"   ✅ {total_in_db} chunk ChromaDB'ye kaydedildi")

        # 7. Doküman kaydı (doc_registry.json) oluştur
        self._write_doc_registry(source_dir, documents, chunks)

        # 8. Sonuç raporu
        stats = {
            "source_dir": str(source_dir),
            "documents_loaded": len(documents),
            "total_chunks": chunk_stats["total"],
            "avg_chunk_size": chunk_stats.get("avg_size", 0),
            "min_chunk_size": chunk_stats.get("min_size", 0),
            "max_chunk_size": chunk_stats.get("max_size", 0),
            "total_characters": chunk_stats.get("total_chars", 0),
            "embedding_model": self.embedder.model_name,
            "embedding_dimension": self.embedder.dimension,
            "collection_name": self.indexer.collection_name,
            "documents_in_db": total_in_db,
        }

        print("\n" + "=" * 50)
        print("📊 İndeksleme Raporu")
        print("=" * 50)
        print(f"   Dosya sayısı:     {stats['documents_loaded']}")
        print(f"   Chunk sayısı:     {stats['total_chunks']}")
        print(f"   Ort. chunk:       {stats['avg_chunk_size']} karakter")
        print(f"   Min/Max chunk:    {stats['min_chunk_size']}/{stats['max_chunk_size']}")
        print(f"   Toplam karakter:  {stats['total_characters']:,}")
        print(f"   Embedding modeli: {stats['embedding_model']}")
        print(f"   Vektör boyutu:    {stats['embedding_dimension']}")
        print(f"   ChromaDB'de:      {stats['documents_in_db']} chunk")
        print("=" * 50 + "\n")

        logger.info("pipeline_complete", **stats)
        return stats

    def test_query(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Test sorgusu yapar — pipeline doğru çalışıyor mu kontrol eder.

        Args:
            query: Test sorusu.
            n_results: Kaç sonuç döndürülsün.

        Returns:
            Sorgu sonuçları.
        """
        print(f"\n🔍 Sorgu: \"{query}\"")

        # E5 modeli ise is_query=True ile sorgu prefix'i eklenir
        query_embedding = self.embedder.embed_single(query, is_query=True)
        results = self.indexer.query(query_embedding, n_results=n_results)

        if results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            distances = results["distances"][0] if results.get("distances") else []
            metadatas = results["metadatas"][0] if results.get("metadatas") else []

            print(f"   {len(docs)} sonuç bulundu:\n")
            for i, (doc, dist) in enumerate(zip(docs, distances)):
                source = metadatas[i].get("source", "?") if i < len(metadatas) else "?"
                similarity = 1 - dist  # ChromaDB distance → similarity
                print(f"   [{i+1}] (benzerlik: {similarity:.3f}) [{source}]")
                print(f"       {doc[:200]}...")
                print()
        else:
            print("   Sonuç bulunamadı.")

        return results

    @staticmethod
    def _generate_content_hash_ids(
        texts: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> List[str]:
        """İçerik + kaynak tabanlı SHA-256 hash ID'leri üretir."""
        ids = []
        for i, text in enumerate(texts):
            source = metadatas[i].get("source", "") if i < len(metadatas) else ""
            raw = f"{source}::{text}"
            digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
            ids.append(f"chunk_{digest}")
        return ids

    def _write_doc_registry(
        self,
        source_dir: Path,
        documents: list,
        chunks: list,
    ) -> None:
        """İndekslenen dokümanların kaydını data/metadata/doc_registry.json'a yazar."""
        try:
            registry_dir = Path(__file__).parent.parent.parent / "data" / "metadata"
            registry_dir.mkdir(parents=True, exist_ok=True)
            registry_path = registry_dir / "doc_registry.json"

            chunks_per_source: Dict[str, int] = {}
            for chunk in chunks:
                src = chunk.metadata.get("source", "bilinmiyor")
                chunks_per_source[src] = chunks_per_source.get(src, 0) + 1

            doc_entries = []
            for doc in documents:
                source_name = doc.metadata.get("source", "bilinmiyor")
                content_hash = hashlib.sha256(doc.content.encode("utf-8")).hexdigest()[:16]
                doc_entries.append({
                    "filename": source_name,
                    "category": doc.metadata.get("category", "genel"),
                    "file_type": doc.metadata.get("file_type", "unknown"),
                    "char_count": len(doc.content),
                    "chunk_count": chunks_per_source.get(source_name, 0),
                    "content_hash": content_hash,
                })

            registry = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_dir": str(source_dir),
                "total_documents": len(documents),
                "total_chunks": len(chunks),
                "embedding_model": self.embedder.model_name,
                "collection_name": self.indexer.collection_name,
                "documents": doc_entries,
            }

            registry_path.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"   📋 Doküman kaydı: {registry_path}")
            logger.info("doc_registry_written", path=str(registry_path))
        except Exception:
            logger.exception("doc_registry_write_failed")

    def close(self) -> None:
        """Kaynakları serbest bırakır."""
        self.indexer.close()
