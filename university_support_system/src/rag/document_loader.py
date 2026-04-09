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

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import unicodedata

import pdfplumber
import structlog

from src.core.constants import known_department_directory_names, normalize_department_value

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

    # Bilinen departman klasör isimleri
    KNOWN_DEPARTMENTS = known_department_directory_names()

    # Dosya adından akademik bölüm tespiti için anahtar kelime eşlemeleri.
    # Her key bir bölüm kodu, value ise (bölüm_tam_adı, [anahtar_kelimeler]) tuple'ı.
    # Anahtar kelimeler dosya adının lowercase halinde aranır.
    BOLUM_KEYWORDS: dict[str, tuple[str, list[str]]] = {
        "bilgisayar_muhendisligi": (
            "Bilgisayar Mühendisliği",
            ["bilgisayar", "bilgi_güv", "siber_güvenlik", "yazılım"],
        ),
        "elektrik_elektronik_muhendisligi": (
            "Elektrik-Elektronik Mühendisliği",
            ["eem", "elektrik", "elektronik"],
        ),
        "makine_muhendisligi": (
            "Makine Mühendisliği",
            ["makine", "mbm"],
        ),
        "insaat_muhendisligi": (
            "İnşaat Mühendisliği",
            ["inşaat", "inş_müh"],
        ),
        "endustri_muhendisligi": (
            "Endüstri Mühendisliği",
            ["endüstri", "end_454"],
        ),
        "cevre_muhendisligi": (
            "Çevre Mühendisliği",
            ["çevre_mühendisliği"],
        ),
        "kimya_muhendisligi": (
            "Kimya Mühendisliği",
            ["kimya_müh", "kimyamuh"],
        ),
        "kimya": (
            "Kimya",
            ["fef_kimya", "kimya_biyoloji", "kimya_mbg"],
        ),
        "biyoloji": (
            "Biyoloji",
            ["biyoloji"],
        ),
        "fizik": (
            "Fizik",
            ["fizik"],
        ),
        "matematik": (
            "Matematik",
            ["matematik", "mat_bitirme"],
        ),
        "istatistik": (
            "İstatistik",
            ["istatistik"],
        ),
        "tip_fakultesi": (
            "Tıp Fakültesi",
            ["tıp_fakültesi", "tip_fakultesi", "tıpta_uzmanlık", "intörn"],
        ),
        "dis_hekimligi": (
            "Diş Hekimliği",
            ["diş_hekimliği", "dis_hekimligi"],
        ),
        "veteriner": (
            "Veteriner Fakültesi",
            ["veteriner"],
        ),
        "guzel_sanatlar": (
            "Güzel Sanatlar Fakültesi",
            ["güzel_sanatlar"],
        ),
        "egitim_fakultesi": (
            "Eğitim Fakültesi",
            [
                "sınıf_eğitimi", "okul_öncesi_öğretmenliği",
                "sosyal_bilgiler_eğitimi", "özel_eğitim",
                "ingiliz_dili_eğitimi", "pedagojik_formasyon",
            ],
        ),
        "muhendislik_fakultesi": (
            "Mühendislik Fakültesi",
            ["mühendislik_fakültesi_ortak", "mühendislik_fakültesi_sınav"],
        ),
    }

    def __init__(self, min_content_length: int = 50):
        self.min_content_length = min_content_length

    @staticmethod
    def _normalize_source_name(filename: str) -> str:
        """Kaynak adlarini tutarli eslesme ve gosterim icin NFC'ye sabitler."""
        return unicodedata.normalize("NFC", filename)

    def _detect_department(self, file_path: Path) -> tuple[str, str]:
        """
        Dosya yolundan departman ve alt kategori bilgisini çıkarır.

        Yol yapısı: data/raw/{department}/{subcategory}/dosya.pdf
        Örnek: data/raw/academic_programs/yonergeler_egitim/uzaktan_egitim.pdf
               → department="academic_programs", subcategory="yonergeler_egitim"

        Returns:
            (department, subcategory) tuple'ı.
            Bulunamazsa ("unknown", "genel") döner.
        """
        parts = file_path.resolve().parts

        for i, part in enumerate(parts):
            if part in self.KNOWN_DEPARTMENTS:
                department = normalize_department_value(part)
                # Alt kategori: departman klasöründen sonraki ilk klasör
                if i + 1 < len(parts) - 1:  # -1: dosya adını hariç tut
                    subcategory = parts[i + 1]
                else:
                    subcategory = "genel"
                return department, subcategory

        return "unknown", "genel"

    def _detect_bolum(self, filename: str) -> tuple[str, str]:
        """
        Dosya adından akademik bölümü tespit eder.

        Dosya adının lowercase halinde BOLUM_KEYWORDS'teki anahtar kelimeleri
        arar. Tek ve net bir eşleşme varsa ilgili bölümü döndürür.
        Birden fazla farklı bölüm eşleşirse belgeyi genel kabul eder.

        Args:
            filename: Dosya adı (uzantı dahil).

        Returns:
            (bolum_kodu, bolum_adi) tuple'ı.
            Eşleşme yoksa veya birden fazla bölüm eşleşirse
            ("genel", "Genel") döner.
        """
        name_lower = filename.lower()
        matched_bolumler: list[tuple[str, str]] = []

        for bolum_kodu, (bolum_adi, keywords) in self.BOLUM_KEYWORDS.items():
            if any(keyword in name_lower for keyword in keywords):
                matched_bolumler.append((bolum_kodu, bolum_adi))

        if len(matched_bolumler) == 1:
            return matched_bolumler[0]

        if len(matched_bolumler) > 1:
            logger.info(
                "multiple_bolum_matches",
                filename=filename,
                matches=[bolum_kodu for bolum_kodu, _ in matched_bolumler],
            )

        return "genel", "Genel"

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
            normalized_name = self._normalize_source_name(file_path.name)

            if suffix == ".pdf":
                content = self._load_pdf(file_path)
            else:
                content = self._load_txt(file_path)

            content = self._clean_content(content)

            # Minimum uzunluk kontrolü
            if len(content.strip()) < self.min_content_length:
                logger.warning(
                    "file_too_short",
                    path=normalized_name,
                    length=len(content.strip()),
                    min_required=self.min_content_length,
                )
                return None

            # Departman ve alt kategoriyi dosya yolundan otomatik çıkar
            department, subcategory = self._detect_department(file_path)

            # Akademik bölümü dosya adından tespit et
            bolum_kodu, bolum_adi = self._detect_bolum(normalized_name)

            metadata = {
                "source": normalized_name,
                "display_source": normalized_name,
                "file_path": str(file_path),
                "category": category,
                "department": department,
                "subcategory": subcategory,
                "bolum": bolum_kodu,
                "bolum_adi": bolum_adi,
                "file_type": suffix.lstrip("."),
                "char_count": len(content),
            }

            logger.info(
                "file_loaded",
                file=normalized_name,
                department=department,
                subcategory=subcategory,
                bolum=bolum_kodu,
                chars=len(content),
                words=len(content.split()),
            )

            return Document(content=content, metadata=metadata)

        except (OSError, UnicodeError, ValueError) as exc:
            logger.error("file_load_error", path=str(file_path), error=str(exc))
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
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
        except Exception as exc:
            # Bazı PDF'ler bozuk/uyumsuz font sözlükleri yüzünden pdfminer içinde
            # parse hatası verir. Tek bir dosya yüzünden tüm indeksleme akışını
            # düşürmek yerine bu dosyayı atlamak için ValueError'a çeviriyoruz.
            raise ValueError(f"PDF metni çıkarılamadı: {exc}") from exc

        return "\n\n".join(pages_text)

    def _load_txt(self, file_path: Path) -> str:
        """TXT dosyasını okur (UTF-8, fallback: cp1254 Windows Türkçe)."""
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="cp1254")

    _LINK_PLACEHOLDER_PATTERN = re.compile(
        r"(?:Tıklayınız|Tiklayiniz|Tıkla|Buraya Tıklayın|Click Here)[\s.]*",
        re.IGNORECASE,
    )
    _REPEATED_WHITESPACE_PATTERN = re.compile(r"\n{3,}")

    @classmethod
    def _clean_content(cls, text: str) -> str:
        """Remove link placeholders and excessive whitespace from loaded content."""
        text = cls._LINK_PLACEHOLDER_PATTERN.sub("", text)
        text = cls._REPEATED_WHITESPACE_PATTERN.sub("\n\n", text)
        return text.strip()
