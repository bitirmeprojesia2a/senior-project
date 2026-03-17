"""
RAG Pipeline Unit Testleri

Document loader, text preprocessor, chunker ve embedder testleri.
ChromaDB testleri mock httpx client ile yapılır.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.constants import Department
from src.rag.document_loader import Document, DocumentLoader
from src.rag.text_preprocessor import TextPreprocessor
from src.rag.chunker import Chunk, TextChunker


# ═══════════════════════════════════════════════════
# Document Loader Testleri
# ═══════════════════════════════════════════════════

class TestDocumentLoader:
    """DocumentLoader testleri."""

    def test_load_txt_file(self, tmp_path):
        """TXT dosyası yüklenebilir."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Bu bir test metnidir. Yeterince uzun olmalı ki minimum uzunluk kontrolünden geçsin.", encoding="utf-8")

        loader = DocumentLoader(min_content_length=10)
        doc = loader.load_file(txt_file, category="test")

        assert doc is not None
        assert "test metnidir" in doc.content
        assert doc.metadata["file_type"] == "txt"
        assert doc.metadata["category"] == "test"
        assert doc.metadata["department"] == "unknown"

    def test_load_txt_with_cp1254_encoding(self, tmp_path):
        """Windows Türkçe encoding'li TXT okunabilir."""
        txt_file = tmp_path / "turkish.txt"
        txt_file.write_bytes("Öğrenci İşleri Daire Başkanlığı — Çalışma Esasları".encode("cp1254"))

        loader = DocumentLoader(min_content_length=10)
        doc = loader.load_file(txt_file)

        assert doc is not None
        assert "Öğrenci" in doc.content

    def test_skip_short_files(self, tmp_path):
        """Çok kısa dosyalar atlanır."""
        txt_file = tmp_path / "short.txt"
        txt_file.write_text("Kısa", encoding="utf-8")

        loader = DocumentLoader(min_content_length=50)
        doc = loader.load_file(txt_file)

        assert doc is None

    def test_unsupported_extension(self, tmp_path):
        """Desteklenmeyen dosya türleri atlanır."""
        xlsx_file = tmp_path / "test.xlsx"
        xlsx_file.write_text("data", encoding="utf-8")

        loader = DocumentLoader()
        doc = loader.load_file(xlsx_file)

        assert doc is None

    def test_load_directory(self, tmp_path):
        """Klasördeki tüm dosyalar yüklenir."""
        (tmp_path / "doc1.txt").write_text("Bu birinci test dokümanıdır. " * 5, encoding="utf-8")
        (tmp_path / "doc2.txt").write_text("Bu ikinci test dokümanıdır. " * 5, encoding="utf-8")
        (tmp_path / "skip.xlsx").write_text("atlanacak", encoding="utf-8")

        loader = DocumentLoader(min_content_length=10)
        docs = loader.load_directory(tmp_path)

        assert len(docs) == 2

    def test_load_directory_with_subdirs(self, tmp_path):
        """Alt klasörlerdeki dosyalar da yüklenir."""
        sub = tmp_path / "yönergeler"
        sub.mkdir()
        (sub / "yonerge1.txt").write_text("Yönerge içeriği buraya gelir. " * 5, encoding="utf-8")

        loader = DocumentLoader(min_content_length=10)
        docs = loader.load_directory(tmp_path, recursive=True)

        assert len(docs) == 1
        assert docs[0].metadata["category"] == "yönergeler"

    def test_nonexistent_directory(self):
        """Var olmayan klasör boş liste döndürür."""
        loader = DocumentLoader()
        docs = loader.load_directory(Path("/nonexistent/path"))
        assert docs == []

    def test_detect_department_from_academic_programs_path(self, tmp_path):
        """Academic programs klasöründen departman ve alt kategori tespit edilir."""
        target_dir = tmp_path / "academic_programs" / "yonergeler_egitim"
        target_dir.mkdir(parents=True)
        txt_file = target_dir / "bilgisayar_muhendisligi_plan.txt"
        txt_file.write_text("Bu bir akademik program dokümanıdır. " * 5, encoding="utf-8")

        loader = DocumentLoader(min_content_length=10)
        doc = loader.load_file(txt_file)

        assert doc is not None
        assert doc.metadata["department"] == "academic_programs"
        assert doc.metadata["subcategory"] == "yonergeler_egitim"
        assert doc.metadata["bolum"] == "bilgisayar_muhendisligi"

    def test_detect_department_from_finance_path(self, tmp_path):
        """finance klasörü resmi finance departmanına map edilir."""
        target_dir = tmp_path / "finance" / "yonergeler"
        target_dir.mkdir(parents=True)
        txt_file = target_dir / "harc_ucretleri.txt"
        txt_file.write_text("Bu bir finans dokümanıdır. " * 5, encoding="utf-8")

        loader = DocumentLoader(min_content_length=10)
        doc = loader.load_file(txt_file)

        assert doc is not None
        assert doc.metadata["department"] == "finance"

    def test_detect_bolum_returns_genel_for_multiple_matches(self):
        """Birden fazla bölüm eşleşirse belge genel kabul edilir."""
        loader = DocumentLoader()

        bolum_kodu, bolum_adi = loader._detect_bolum("bilgisayar_makine_ortak_yonerge.txt")

        assert bolum_kodu == "genel"
        assert bolum_adi == "Genel"


class TestDocument:
    """Document dataclass testleri."""

    def test_char_count(self):
        """Karakter sayısı doğru hesaplanır."""
        doc = Document(content="Merhaba Dünya")
        assert doc.char_count == 13

    def test_word_count(self):
        """Kelime sayısı doğru hesaplanır."""
        doc = Document(content="Bu bir test cümlesidir")
        assert doc.word_count == 4


# ═══════════════════════════════════════════════════
# Text Preprocessor Testleri
# ═══════════════════════════════════════════════════

class TestTextPreprocessor:
    """TextPreprocessor testleri."""

    def test_normalize_whitespace(self):
        """Fazla boşluklar temizlenir."""
        preprocessor = TextPreprocessor()
        result = preprocessor.clean("Bu   bir    test")
        assert "   " not in result
        assert "Bu bir test" in result

    def test_remove_page_numbers(self):
        """Sayfa numaraları kaldırılır."""
        preprocessor = TextPreprocessor()
        text = "İçerik burada\nSayfa 1\nBaşka içerik"
        result = preprocessor.clean(text)
        assert "Sayfa 1" not in result
        assert "İçerik burada" in result

    def test_remove_repeated_headers(self):
        """Tekrarlanan header/footer satırları kaldırılır."""
        preprocessor = TextPreprocessor()
        header = "T.C. Ondokuz Mayıs Üniversitesi"
        text = "\n".join([
            header, "İçerik 1", "",
            header, "İçerik 2", "",
            header, "İçerik 3", "",
            header, "İçerik 4",
        ])
        result = preprocessor.clean(text)
        assert result.count(header) == 0  # 4 kez → header kabul edilerek kaldırıldı

    def test_empty_input(self):
        """Boş girdi boş string döndürür."""
        preprocessor = TextPreprocessor()
        assert preprocessor.clean("") == ""
        assert preprocessor.clean("   ") == ""

    def test_clean_batch(self):
        """Toplu temizleme çalışır."""
        preprocessor = TextPreprocessor()
        results = preprocessor.clean_batch(["  Merhaba  ", "  Dünya  "])
        assert results == ["Merhaba", "Dünya"]


# ═══════════════════════════════════════════════════
# Chunker Testleri
# ═══════════════════════════════════════════════════

class TestTextChunker:
    """TextChunker testleri."""

    def test_basic_chunking(self):
        """Metin chunk'lara bölünür."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "Bu bir test cümlesidir. " * 20  # ~480 karakter
        chunks = chunker.split_text(text, metadata={"source": "test.txt"})

        assert len(chunks) > 1
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.char_count <= 60 for c in chunks)  # Biraz tolerans

    def test_metadata_propagation(self):
        """Kaynak metadata her chunk'a kopyalanır."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "Uzun metin " * 50
        chunks = chunker.split_text(text, metadata={"source": "doc.pdf", "category": "yönergeler"})

        for chunk in chunks:
            assert chunk.metadata["source"] == "doc.pdf"
            assert chunk.metadata["category"] == "yönergeler"
            assert "chunk_index" in chunk.metadata
            assert "chunk_count" in chunk.metadata

    def test_chunk_index_ordering(self):
        """Chunk indeksleri sıralı."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "Test metin parçası. " * 30
        chunks = chunker.split_text(text)

        for i, chunk in enumerate(chunks):
            assert chunk.metadata["chunk_index"] == i

    def test_empty_text(self):
        """Boş metin boş liste döndürür."""
        chunker = TextChunker()
        assert chunker.split_text("") == []
        assert chunker.split_text("   ") == []

    def test_get_stats(self):
        """Chunk istatistikleri doğru hesaplanır."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        text = "Bu bir istatistik testi. " * 50
        chunks = chunker.split_text(text)
        stats = chunker.get_stats(chunks)

        assert stats["total"] == len(chunks)
        assert stats["total"] > 0
        assert stats["min_size"] <= stats["avg_size"] <= stats["max_size"]

    def test_split_documents(self):
        """Birden fazla doküman chunk'lanır."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        docs = [
            Document(content="Birinci doküman " * 20, metadata={"source": "doc1.txt"}),
            Document(content="İkinci doküman " * 20, metadata={"source": "doc2.txt"}),
        ]
        chunks = chunker.split_documents(docs)

        assert len(chunks) > 2
        sources = {c.metadata["source"] for c in chunks}
        assert "doc1.txt" in sources
        assert "doc2.txt" in sources


class TestChunk:
    """Chunk dataclass testleri."""

    def test_char_and_word_count(self):
        """Chunk boyut hesaplamaları doğru."""
        chunk = Chunk(content="Üç kelime burada")
        assert chunk.char_count == 16
        assert chunk.word_count == 3


class TestContentHashIds:
    """Pipeline hash tabanlı ID üretimi testleri."""

    def test_generates_correct_count(self):
        from src.rag.pipeline import IndexingPipeline

        texts = ["metin 1", "metin 2", "metin 3"]
        metas = [{"source": "a.txt"}, {"source": "b.txt"}, {"source": "c.txt"}]
        ids = IndexingPipeline._generate_content_hash_ids(texts, metas)
        assert len(ids) == 3

    def test_ids_start_with_chunk_prefix(self):
        from src.rag.pipeline import IndexingPipeline

        ids = IndexingPipeline._generate_content_hash_ids(
            ["test"], [{"source": "a.txt"}]
        )
        assert ids[0].startswith("chunk_")

    def test_same_content_same_id(self):
        from src.rag.pipeline import IndexingPipeline

        ids1 = IndexingPipeline._generate_content_hash_ids(
            ["aynı metin"], [{"source": "doc.txt"}]
        )
        ids2 = IndexingPipeline._generate_content_hash_ids(
            ["aynı metin"], [{"source": "doc.txt"}]
        )
        assert ids1[0] == ids2[0]

    def test_different_content_different_id(self):
        from src.rag.pipeline import IndexingPipeline

        ids = IndexingPipeline._generate_content_hash_ids(
            ["metin A", "metin B"],
            [{"source": "doc.txt"}, {"source": "doc.txt"}],
        )
        assert ids[0] != ids[1]

    def test_same_content_different_source_different_id(self):
        from src.rag.pipeline import IndexingPipeline

        ids = IndexingPipeline._generate_content_hash_ids(
            ["aynı metin", "aynı metin"],
            [{"source": "doc1.txt"}, {"source": "doc2.txt"}],
        )
        assert ids[0] != ids[1]


class TestPipelineCollectionResolution:
    """Pipeline koleksiyon çözümleme testleri."""

    def test_detect_department_from_source_dir(self, tmp_path):
        from src.rag.pipeline import IndexingPipeline

        source_dir = tmp_path / "academic_programs" / "yonergeler_egitim"
        source_dir.mkdir(parents=True)

        department = IndexingPipeline._detect_department_from_source_dir(source_dir)

        assert department == Department.ACADEMIC_PROGRAMS

    def test_detect_department_from_finance_source_dir(self, tmp_path):
        from src.rag.pipeline import IndexingPipeline

        source_dir = tmp_path / "finance" / "yonergeler"
        source_dir.mkdir(parents=True)

        department = IndexingPipeline._detect_department_from_source_dir(source_dir)

        assert department == Department.FINANCE

    def test_resolve_collection_name_from_source_dir(self, tmp_path):
        from src.rag.pipeline import IndexingPipeline

        source_dir = tmp_path / "academic_programs" / "yonergeler_egitim"
        source_dir.mkdir(parents=True)
        pipeline = IndexingPipeline()

        collection_name = pipeline._resolve_collection_name(source_dir)

        assert collection_name == "academic_programs_docs"

    def test_detect_department_from_source_dir_raises_for_unknown_path(self, tmp_path):
        from src.rag.pipeline import IndexingPipeline

        source_dir = tmp_path / "rastgele_klasor"
        source_dir.mkdir(parents=True)

        with pytest.raises(ValueError):
            IndexingPipeline._detect_department_from_source_dir(source_dir)

    def test_explicit_collection_name_is_preserved(self, tmp_path):
        from src.rag.pipeline import IndexingPipeline

        source_dir = tmp_path / "academic_programs" / "yonergeler_egitim"
        source_dir.mkdir(parents=True)
        pipeline = IndexingPipeline(collection_name="ozel_koleksiyon")

        collection_name = pipeline._resolve_collection_name(source_dir)

        assert collection_name == "ozel_koleksiyon"
