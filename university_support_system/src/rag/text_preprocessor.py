"""
Metin Ön İşleme

PDF ve TXT dosyalarından çıkarılan ham metni normalize eder.
Gereksiz boşluklar, header/footer tekrarları, sayfa numaraları,
belge referans kodları ve kontrol ibareleri temizlenir.

Kullanım:
    from src.rag.text_preprocessor import TextPreprocessor

    preprocessor = TextPreprocessor()
    clean_text = preprocessor.clean(raw_text)
"""

import re
from typing import List, Set

import structlog

from src.core.text_normalization import normalize_text

logger = structlog.get_logger()

# ── Üniversite Belgelerinde Sık Tekrar Eden Kalıplar ──────────────────
# Bu kalıplar chunk alanını yiyor ve vektör kalitesini düşürüyor.

# Belge referans kodları (ör: "PP1.2.PRS.0042, R0, Şubat 2024 Sayfa 1 / 6")
RE_DOC_REFERENCE = re.compile(
    r"(?m)^\s*PP\d[\d.]*PRS[\d.]*.*?Sayfa\s*\d+\s*/\s*\d+\s*$",
    re.IGNORECASE,
)

# "Bu dokümanın basılı hali kontrolsüz doküman kabul edilmektedir." vb.
RE_KONTROLSUZ = re.compile(
    r"(?m)^\s*Bu\s+dokümanın\s+basılı\s+hali\s+kontrolsüz.*$",
    re.IGNORECASE,
)

# "Lütfen web sitesinden en son versiyonuna ulaşınız." vb.
RE_WEB_UYARI = re.compile(
    r"(?m)^\s*Lütfen\s+web\s+sitesinden\s+en\s+son\s+versiyonuna.*$",
    re.IGNORECASE,
)

# Sayfa numarası desenleri (genişletilmiş)
RE_PAGE_PATTERNS = [
    re.compile(r"(?m)^\s*[Ss]ayfa\s*\d+\s*(/\s*\d+)?\s*$"),
    re.compile(r"(?m)^\s*\d+\s*/\s*\d+\s*$"),
    re.compile(r"(?m)^\s*-\s*\d+\s*-\s*$"),            # "- 5 -" formatı
    re.compile(r"(?m)^\s*\[\s*\d+\s*\]\s*$"),            # "[5]" formatı
]

# Tekrarlayan üniversite başlıkları (sayfa başı header'ları)
RE_UNIV_HEADER = re.compile(
    r"(?m)^\s*T\.?\s*C\.?\s*$",
    re.IGNORECASE,
)


class TextPreprocessor:
    """
    Türkçe metin ön işleme.

    İşlemler:
        1. Fazla boşluk ve boş satır temizliği
        2. Belge referans kodları ve kontrol ibareleri kaldırma
        3. Sayfa numarası kaldırma
        4. Header/footer tekrarı kaldırma (dinamik frekans analizi)
        5. Çok kısa anlamsız satırları kaldırma
        6. Son normalleştirme
    """

    def __init__(self, min_line_length: int = 3, header_repeat_threshold: int = 3):
        self.min_line_length = min_line_length
        self.header_repeat_threshold = header_repeat_threshold

    def clean(self, text: str) -> str:
        """
        Ham metni temizler ve normalize eder.

        Args:
            text: Ham metin.

        Returns:
            Temizlenmiş metin.
        """
        if not text or not text.strip():
            return ""

        text = self._normalize_whitespace(text)
        text = self._remove_document_artifacts(text)
        text = self._remove_page_numbers(text)
        text = self._remove_header_footer_repeats(text)
        text = self._remove_short_lines(text)
        text = self._normalize_final(text)

        return text.strip()

    def _normalize_whitespace(self, text: str) -> str:
        """Fazla boşluk ve tab'ları tek boşluğa çevirir."""
        text = text.replace("\t", " ")
        # Satır içi çoklu boşluk → tek boşluk
        text = re.sub(r"[^\S\n]+", " ", text)
        # 3+ boş satır → 2 boş satır
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    def _remove_document_artifacts(self, text: str) -> str:
        """
        Üniversite belgelerine özgü tekrar eden kalıntıları kaldırır:
        - Belge referans kodları (PP1.2.PRS.0042 vb.)
        - "Bu dokümanın basılı hali kontrolsüz..." uyarıları
        - "Lütfen web sitesinden..." yönlendirmeleri
        - Tekrarlayan "T.C." header'ları
        """
        text = RE_DOC_REFERENCE.sub("", text)
        text = RE_KONTROLSUZ.sub("", text)
        text = RE_WEB_UYARI.sub("", text)
        text = RE_UNIV_HEADER.sub("", text)
        return text

    def _remove_page_numbers(self, text: str) -> str:
        """Sayfa numaralarını kaldırır (genişletilmiş kalıplar)."""
        for pattern in RE_PAGE_PATTERNS:
            text = pattern.sub("", text)
        return text

    def _remove_header_footer_repeats(self, text: str) -> str:
        """
        Her sayfada tekrarlanan header/footer satırlarını kaldırır.
        Bir satır threshold (varsayılan 3) veya daha fazla tekrarlanıyorsa
        header/footer olarak kabul edilir ve kaldırılır.
        """
        lines = text.split("\n")

        line_counts: dict = {}
        for line in lines:
            stripped = line.strip()
            if stripped and self._looks_like_header_footer_candidate(stripped):
                line_counts[stripped] = line_counts.get(stripped, 0) + 1

        repeated: Set[str] = {
            line
            for line, count in line_counts.items()
            if count >= self.header_repeat_threshold
        }

        if repeated:
            logger.debug(
                "removing_repeated_lines",
                count=len(repeated),
                examples=list(repeated)[:3],
            )
            lines = [line for line in lines if line.strip() not in repeated]

        return "\n".join(lines)

    def _looks_like_header_footer_candidate(self, line: str) -> bool:
        """Yalnızca header/footer benzeri satırları tekrar temizliğine dahil et."""
        stripped = line.strip()
        if len(stripped) <= 5 or len(stripped) > 120:
            return False

        words = stripped.split()
        if len(words) > 10:
            return False

        if stripped.endswith((".", "?", "!")) and len(words) > 4:
            return False

        lowered = normalize_text(stripped)
        header_tokens = (
            "universite",
            "fakulte",
            "fakultesi",
            "dekanligi",
            "mudurlugu",
            "rektorlugu",
            "sayfa",
            "yonerge",
            "yonetmelik",
            "formu",
        )
        if any(token in lowered for token in header_tokens):
            return True

        alpha_chars = [char for char in stripped if char.isalpha()]
        if not alpha_chars:
            return False

        uppercase_ratio = sum(1 for char in alpha_chars if char.isupper()) / len(alpha_chars)
        return stripped.isupper() or uppercase_ratio >= 0.6

    def _remove_short_lines(self, text: str) -> str:
        """Çok kısa anlamsız satırları kaldırır."""
        lines = text.split("\n")
        cleaned: List[str] = []

        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                cleaned.append("")
                continue
            if stripped.isdigit():
                previous = next((item.strip() for item in reversed(lines[:index]) if item.strip()), "")
                next_line = next((item.strip() for item in lines[index + 1 :] if item.strip()), "")
                previous_normalized = previous.casefold()
                next_normalized = next_line.casefold()
                if (
                    previous_normalized in {"madde", "ek", "tablo", "bent", "fikra"}
                    or previous_normalized.startswith(("madde ", "ek ", "tablo "))
                    or next_normalized.startswith(("madde", "ek", "tablo", "bent", "fikra"))
                ):
                    cleaned.append(line)
                    continue
            if len(stripped) >= self.min_line_length:
                cleaned.append(line)

        return "\n".join(cleaned)

    def _normalize_final(self, text: str) -> str:
        """Son normalleştirme."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines)

    def clean_batch(self, texts: List[str]) -> List[str]:
        """Birden fazla metni toplu temizler."""
        return [self.clean(text) for text in texts]
