"""RAG indexing pipeline."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import structlog
from tqdm import tqdm

from src.core.constants import Department, collection_name_for_department, normalize_department_value
from src.rag.chunker import Chunk, TextChunker
from src.rag.document_loader import Document, DocumentLoader
from src.rag.embedder import Embedder
from src.rag.indexer import ChromaIndexer
from src.rag.text_preprocessor import TextPreprocessor

logger = structlog.get_logger()


class IndexingPipeline:
    """End-to-end document indexing flow for ChromaDB."""

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        collection_name: str | None = None,
        embedding_model: str | None = None,
        chroma_url: str | None = None,
    ):
        self._explicit_collection_name = collection_name
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
    ) -> dict[str, Any]:
        """Run the indexing pipeline and return summary stats."""
        source_dir = Path(source_dir)
        self.indexer.collection_name = self._resolve_collection_name(source_dir)
        logger.info("pipeline_start", source=str(source_dir), reindex=reindex)

        self._prepare_collection(reindex=reindex)

        documents = self._load_documents(source_dir)
        if not documents:
            logger.error("no_documents_found", path=str(source_dir))
            return {"error": "Hic dosya bulunamadi"}

        documents = self._clean_documents(documents)
        chunks = self._split_chunks(documents)
        if not chunks:
            return {"error": "Chunk olusturulamadi"}

        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = self._generate_embeddings(chunk_texts)
        if embeddings is None:
            return {"error": "Embedding uretimi basarisiz"}

        metadatas = [chunk.metadata for chunk in chunks]
        ids = self._generate_content_hash_ids(chunk_texts, metadatas)
        total_in_db = self._index_chunks(
            ids=ids,
            chunk_texts=chunk_texts,
            embeddings=embeddings,
            metadatas=metadatas,
            reindex=reindex,
        )
        if total_in_db is None:
            return {"error": "ChromaDB indeksleme basarisiz"}

        self._write_doc_registry(source_dir, documents, chunks)

        chunk_stats = self.chunker.get_stats(chunks)
        stats = self._build_stats(
            source_dir=source_dir,
            documents=documents,
            chunk_stats=chunk_stats,
            total_in_db=total_in_db,
        )
        self._print_report(stats)
        logger.info("pipeline_complete", **stats)
        return stats

    def _prepare_collection(self, *, reindex: bool) -> None:
        """Ensure the target collection exists and is ready."""
        if reindex:
            logger.info("deleting_existing_collection")
            self.indexer.delete_collection()
        self.indexer.create_collection()

    def _load_documents(self, source_dir: Path) -> list[Document]:
        """Load raw source documents from disk."""
        print("\n[1/5] Dosyalar yukleniyor...")
        documents = self.loader.load_directory(source_dir)
        print(f"   OK: {len(documents)} dosya yuklendi")
        return documents

    def _clean_documents(self, documents: list[Document]) -> list[Document]:
        """Normalize loaded documents and drop empty ones."""
        print("[2/5] Metinler temizleniyor...")
        for doc in tqdm(documents, desc="   Temizleme"):
            doc.content = self.preprocessor.clean(doc.content)

        cleaned_documents = [doc for doc in documents if doc.content.strip()]
        print(f"   OK: {len(cleaned_documents)} dosya temizlendi")
        return cleaned_documents

    def _split_chunks(self, documents: list[Document]) -> list[Chunk]:
        """Split cleaned documents into chunks."""
        print("[3/5] Chunk'lara ayriliyor...")
        chunks = self.chunker.split_documents(documents)
        chunk_stats = self.chunker.get_stats(chunks)
        print(
            f"   OK: {chunk_stats['total']} chunk olusturuldu "
            f"(ort: {chunk_stats.get('avg_size', 0)} karakter)"
        )
        return chunks

    def _generate_embeddings(self, chunk_texts: list[str]) -> list[list[float]] | None:
        """Generate embeddings for chunks."""
        print("[4/5] Embedding'ler uretiliyor...")
        print(f"   Model: {self.embedder.model_name}")
        try:
            embeddings = self.embedder.embed_texts(chunk_texts, is_query=False)
        except (OSError, RuntimeError, ValueError):
            logger.exception("embedding_generation_failed")
            return None

        print(f"   OK: {len(embeddings)} vektor uretildi ({self.embedder.dimension} boyut)")
        return embeddings

    def _index_chunks(
        self,
        *,
        ids: list[str],
        chunk_texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        reindex: bool,
    ) -> int | None:
        """Persist chunks to ChromaDB and return total stored chunks."""
        print("[5/5] ChromaDB'ye indeksleniyor...")
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
            total_in_db = self.indexer.count()
        except httpx.HTTPError:
            logger.exception("indexing_failed")
            return None

        print(f"   OK: {total_in_db} chunk ChromaDB'ye kaydedildi")
        return total_in_db

    def _build_stats(
        self,
        *,
        source_dir: Path,
        documents: list[Document],
        chunk_stats: dict[str, Any],
        total_in_db: int,
    ) -> dict[str, Any]:
        """Build the indexing summary payload."""
        return {
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

    @staticmethod
    def _print_report(stats: dict[str, Any]) -> None:
        """Print a short CLI report."""
        print("\n" + "=" * 50)
        print("Indeksleme Raporu")
        print("=" * 50)
        print(f"   Dosya sayisi:     {stats['documents_loaded']}")
        print(f"   Chunk sayisi:     {stats['total_chunks']}")
        print(f"   Ort. chunk:       {stats['avg_chunk_size']} karakter")
        print(f"   Min/Max chunk:    {stats['min_chunk_size']}/{stats['max_chunk_size']}")
        print(f"   Toplam karakter:  {stats['total_characters']:,}")
        print(f"   Embedding modeli: {stats['embedding_model']}")
        print(f"   Vektor boyutu:    {stats['embedding_dimension']}")
        print(f"   ChromaDB'de:      {stats['documents_in_db']} chunk")
        print("=" * 50 + "\n")

    def _resolve_collection_name(self, source_dir: Path) -> str:
        """Resolve the collection name from the source path."""
        if self._explicit_collection_name:
            return self._explicit_collection_name
        department = self._detect_department_from_source_dir(source_dir)
        return collection_name_for_department(department)

    @staticmethod
    def _detect_department_from_source_dir(source_dir: Path) -> Department:
        """Infer the top-level department from the source directory."""
        department_values = {department.value: department for department in Department}
        for part in source_dir.resolve().parts:
            normalized = normalize_department_value(part)
            if normalized in department_values:
                return department_values[normalized]
        raise ValueError(f"Kaynak klasor yolundan resmi departman tespit edilemedi: {source_dir}")

    def test_query(self, query: str, n_results: int = 3) -> dict[str, Any]:
        """Run a simple search sanity check against the indexed collection."""
        print(f'\nSorgu: "{query}"')

        query_embedding = self.embedder.embed_single(query, is_query=True)
        results = self.indexer.query(query_embedding, n_results=n_results)

        if results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            distances = results["distances"][0] if results.get("distances") else []
            metadatas = results["metadatas"][0] if results.get("metadatas") else []

            print(f"   {len(docs)} sonuc bulundu:\n")
            for index, (doc, dist) in enumerate(zip(docs, distances), start=1):
                source = metadatas[index - 1].get("source", "?") if index - 1 < len(metadatas) else "?"
                similarity = 1 - dist
                print(f"   [{index}] (benzerlik: {similarity:.3f}) [{source}]")
                print(f"       {doc[:200]}...")
                print()
        else:
            print("   Sonuc bulunamadi.")

        return results

    @staticmethod
    def _generate_content_hash_ids(
        texts: list[str],
        metadatas: list[dict[str, Any]],
    ) -> list[str]:
        """Generate deterministic chunk ids from source and content."""
        ids: list[str] = []
        for index, text in enumerate(texts):
            source = metadatas[index].get("source", "") if index < len(metadatas) else ""
            raw = f"{source}::{text}"
            digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
            ids.append(f"chunk_{digest}")
        return ids

    def _write_doc_registry(
        self,
        source_dir: Path,
        documents: list[Document],
        chunks: list[Chunk],
    ) -> None:
        """Write a registry file for indexed source documents."""
        try:
            registry_dir = Path(__file__).parent.parent.parent / "data" / "metadata"
            registry_dir.mkdir(parents=True, exist_ok=True)
            registry_path = registry_dir / "doc_registry.json"

            chunks_per_source: dict[str, int] = {}
            for chunk in chunks:
                source = chunk.metadata.get("source", "bilinmiyor")
                chunks_per_source[source] = chunks_per_source.get(source, 0) + 1

            doc_entries = []
            for doc in documents:
                source_name = doc.metadata.get("source", "bilinmiyor")
                content_hash = hashlib.sha256(doc.content.encode("utf-8")).hexdigest()[:16]
                doc_entries.append(
                    {
                        "filename": source_name,
                        "category": doc.metadata.get("category", "genel"),
                        "file_type": doc.metadata.get("file_type", "unknown"),
                        "char_count": len(doc.content),
                        "chunk_count": chunks_per_source.get(source_name, 0),
                        "content_hash": content_hash,
                    }
                )

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
            print(f"   Dokuman kaydi: {registry_path}")
            logger.info("doc_registry_written", path=str(registry_path))
        except (OSError, TypeError, ValueError):
            logger.exception("doc_registry_write_failed")

    def close(self) -> None:
        """Release held resources."""
        self.indexer.close()
