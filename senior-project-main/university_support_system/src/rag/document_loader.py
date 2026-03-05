"""
Doküman Yükleyici

PDF ve TXT dosyalarını okuyarak ham metin ve metadata üretir.

Desteklenen formatlar:
    - PDF: pdfplumber ile metin çıkarma
    - TXT: UTF-8 okuma (fallback: cp1254 Windows Türkçe)

Kullanım:
    from src.rag.document_loader import DocumentLoader

    loader = DocumentLoader()
    documents = loader.load_directory("data/raw/student_affairs/")
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pdfplumber
import structlog

logger = structlog.get_logger()


@dataclass
class Document:
    """Yüklenmiş doküman."""

    content: str
    metadata: dict = field(default_factory=dict)

    @property
    def char_count(self) -> int:
        """Karakter sayısı."""
        return len(self.content)

    @property
    def word_count(self) -> int:
        """Kelime sayısı."""
        return len(self.content.split())


class DocumentLoader:
    """
    PDF ve TXT dosyalarını yükler.

    Args:
        min_content_length: Minimum karakter sayısı (kısa dosyaları atla).
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

    def __init__(self, min_content_length: int = 50):
        self.min_content_length = min_content_length

    def load_file(self, file_path: Path, category: str = "genel") -> Optional[Document]:
        """
        Tek dosyayı yükler.

        Args:
            file_path: Dosya yolu.
            category: Dosyanın kategorisi (yönergeler, yönetmelikler vb.).

        Returns:
            Document nesnesi veya None (dosya okunamazsa).
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix not in self.SUPPORTED_EXTENSIONS:
            logger.warning("unsupported_file_type", path=str(file_path), suffix=suffix)
            return None

        try:
            if suffix == ".pdf":
                content = self._load_pdf(file_path)
            else:
                content = self._load_txt(file_path)

            # Minimum uzunluk kontrolü
            if len(content.strip()) < self.min_content_length:
                logger.warning(
                    "file_too_short",
                    path=file_path.name,
                    length=len(content.strip()),
                    min_required=self.min_content_length,
                )
                return None

            metadata = {
                "source": file_path.name,
                "file_path": str(file_path),
                "category": category,
                "department": "student_affairs",
                "file_type": suffix.lstrip("."),
                "char_count": len(content),
            }

            logger.info(
                "file_loaded",
                file=file_path.name,
                chars=len(content),
                words=len(content.split()),
            )

            return Document(content=content, metadata=metadata)

        except Exception as e:
            logger.error("file_load_error", path=str(file_path), error=str(e))
            return None

    def load_directory(
        self,
        directory: Path,
        category: Optional[str] = None,
        recursive: bool = True,
    ) -> List[Document]:
        """
        Klasördeki tüm desteklenen dosyaları yükler.

        Args:
            directory: Klasör yolu.
            category: Kategori adı. None ise klasör adı kullanılır.
            recursive: Alt klasörlere de bak.

        Returns:
            Yüklenmiş doküman listesi.
        """
        directory = Path(directory)
        if not directory.exists():
            logger.error("directory_not_found", path=str(directory))
            return []

        documents: List[Document] = []

        # Dosyaları topla
        if recursive:
            files = [
                f for f in directory.rglob("*")
                if f.suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]
        else:
            files = [
                f for f in directory.iterdir()
                if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]

        logger.info("scanning_directory", path=str(directory), file_count=len(files))

        for file_path in sorted(files):
            # Kategori: belirtilmemişse üst klasör adı
            file_category = category or file_path.parent.name
            doc = self.load_file(file_path, category=file_category)
            if doc is not None:
                documents.append(doc)

        logger.info(
            "directory_loaded",
            total_files=len(files),
            loaded=len(documents),
            skipped=len(files) - len(documents),
        )

        return documents

    def _load_pdf(self, file_path: Path) -> str:
        """PDF dosyasından metin çıkarır."""
        pages_text: List[str] = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)

        return "\n\n".join(pages_text)

    def _load_txt(self, file_path: Path) -> str:
        """TXT dosyasını okur (UTF-8, fallback: cp1254 Windows Türkçe)."""
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="cp1254")
