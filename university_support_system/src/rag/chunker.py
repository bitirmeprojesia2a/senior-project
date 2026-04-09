"""
Metin Chunk'lama — MADDE-Aware v2

Temizlenmis metni anlamli parcalara (chunk) boler.
Turkce yasal belgeler (yonetmelik, yonerge) icin MADDE sinirlarini korur.

Onemli iyilestirmeler (v1'e gore):
    - MADDE basliklarini tespit eder ve her alt-chunk'a ekler
    - Madde numarasini metadata'ya yazar
    - Bolum bilgisini metadata'ya yazar
    - 1024 char'dan uzun maddeler bolunurken baslik korunur

Kullanim:
    from src.rag.chunker import TextChunker, Chunk

    chunker = TextChunker(chunk_size=1024, chunk_overlap=128)
    chunks = chunker.split(document)
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

import structlog

logger = structlog.get_logger()


@dataclass
class Chunk:
    """Tek bir metin parcasi."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def char_count(self) -> int:
        return len(self.content)

    @property
    def word_count(self) -> int:
        return len(self.content.split())


# MADDE basligi deseni: "MADDE 5 -", "Madde 12 –", "MADDE 5-" vb.
_MADDE_RE = re.compile(
    r"^(MADDE|Madde)\s+(\d+)\s*[-–—]",
    re.MULTILINE,
)

# BOLUM basligi deseni: "IKINCI BOLUM", "UCUNCU BOLUM" vb.
_BOLUM_RE = re.compile(
    r"^(BİRİNCİ|İKİNCİ|ÜÇÜNCÜ|DÖRDÜNCÜ|BEŞİNCİ|ALTINCI|YEDİNCİ|SEKİZİNCİ|DOKUZUNCU|ONUNCU)"
    r"\s+BÖLÜM\b",
    re.MULTILINE | re.IGNORECASE,
)

_FAQ_QUESTION_RE = re.compile(
    r"^\s*(?:\d+[\.\)]\s*)?(.{10,120}\?)\s*$",
    re.MULTILINE,
)

# Alt chunklama icin ayiricilar (MADDE ayiricisi haric — zaten split edildi)
_SUB_SEPARATORS = [
    "\n\n",
    "\n",
    ". ",
    ".\n",
    "; ",
    ", ",
    " ",
]


class TextChunker:
    """
    MADDE-aware metin chunk'layici.

    Oncelikle metni MADDE sinirlarina gore boler.
    Eger bir madde chunk_size'dan buyukse, alt ayiricilarla
    parcalar ve her alt-chunk'in basina madde basligini ekler.

    Args:
        chunk_size: Chunk boyutu (karakter). Varsayilan: 1024
        chunk_overlap: Chunk'lar arasi ortusme (karakter). Varsayilan: 128
    """

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self._sub_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=_SUB_SEPARATORS,
            length_function=len,
            is_separator_regex=False,
        )

    def _extract_madde_header(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Metnin basindaki MADDE basligini cikarir.

        Returns:
            (madde_header, madde_no) — ornegin ("MADDE 5 - (1) ...", "5")
            Bulunamazsa (None, None)
        """
        match = _MADDE_RE.match(text.strip())
        if not match:
            return None, None

        madde_no = match.group(2)

        # Basligin ilk satirini al (icerik baslamadan once)
        first_newline = text.find("\n", match.end())
        if first_newline == -1 or first_newline > 200:
            header = text[:match.end()].strip()
        else:
            header = text[:first_newline].strip()

        return header, madde_no

    def _detect_bolum(self, text: str) -> Optional[str]:
        """Metindeki BOLUM basligini tespit eder."""
        match = _BOLUM_RE.search(text)
        if match:
            end_of_line = text.find("\n", match.start())
            if end_of_line == -1:
                return text[match.start():].strip()
            return text[match.start():end_of_line].strip()
        return None

    def _split_by_faq(self, text: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """Split FAQ-style text by question boundaries."""
        matches = list(_FAQ_QUESTION_RE.finditer(text))
        if len(matches) < 3:
            return []

        sections: List[Tuple[str, Optional[str], Optional[str]]] = []
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section = text[match.start():end].strip()
            if section:
                sections.append((section, None, None))
        return sections

    def _split_by_madde(self, text: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """
        Metni MADDE sinirlarina gore boler.

        Returns:
            [(metin_parcasi, madde_no, bolum), ...]
        """
        matches = list(_MADDE_RE.finditer(text))

        if not matches:
            faq_sections = self._split_by_faq(text)
            if faq_sections:
                return faq_sections
            return [(text, None, None)]

        sections: List[Tuple[str, Optional[str], Optional[str]]] = []
        current_bolum: Optional[str] = None

        # Ilk MADDE'den onceki metin (varsa)
        if matches[0].start() > 0:
            pre_text = text[:matches[0].start()].strip()
            if pre_text:
                bolum = self._detect_bolum(pre_text)
                if bolum:
                    current_bolum = bolum
                sections.append((pre_text, None, current_bolum))

        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = text[match.start():end].strip()

            bolum = self._detect_bolum(section_text)
            if bolum:
                current_bolum = bolum

            madde_no = match.group(2)
            sections.append((section_text, madde_no, current_bolum))

        return sections

    def split_text(self, text: str, metadata: Dict[str, Any] | None = None) -> List[Chunk]:
        """
        Tek bir metni MADDE-aware chunk'lara boler.

        Args:
            text: Bolunecek metin.
            metadata: Kaynak metadata (her chunk'a kopyalanir).

        Returns:
            Chunk listesi.
        """
        if not text or not text.strip():
            return []

        base_metadata = metadata or {}
        chunks: List[Chunk] = []

        # 1. MADDE sinirlarina gore bol
        sections = self._split_by_madde(text)

        for section_text, madde_no, bolum in sections:
            if not section_text.strip():
                continue

            madde_header, _ = self._extract_madde_header(section_text)

            if len(section_text) <= self.chunk_size:
                chunk_meta = {
                    **base_metadata,
                    "chunk_index": len(chunks),
                }
                if madde_no:
                    chunk_meta["madde_no"] = madde_no
                if bolum:
                    chunk_meta["bolum"] = bolum

                chunks.append(Chunk(content=section_text, metadata=chunk_meta))
            else:
                # MADDE chunk_size'dan buyuk — alt parcalara bol
                sub_chunks = self._sub_splitter.split_text(section_text)

                for j, sub_text in enumerate(sub_chunks):
                    # Ilk sub-chunk zaten MADDE basligini icerir
                    # Sonraki sub-chunk'lara MADDE basligini ekle
                    if j > 0 and madde_header:
                        sub_text = f"[{madde_header}]\n{sub_text}"

                    chunk_meta = {
                        **base_metadata,
                        "chunk_index": len(chunks),
                    }
                    if madde_no:
                        chunk_meta["madde_no"] = madde_no
                    if bolum:
                        chunk_meta["bolum"] = bolum
                    if len(sub_chunks) > 1:
                        chunk_meta["sub_chunk"] = f"{j + 1}/{len(sub_chunks)}"

                    chunks.append(Chunk(content=sub_text, metadata=chunk_meta))

        # chunk_count'u tum chunk'lara yaz
        for chunk in chunks:
            chunk.metadata["chunk_count"] = len(chunks)

        logger.info(
            "text_chunked",
            source=base_metadata.get("source", "unknown"),
            total_chunks=len(chunks),
            avg_chunk_size=sum(c.char_count for c in chunks) // max(len(chunks), 1),
        )

        return chunks

    def split_documents(
        self,
        documents: list,
    ) -> List[Chunk]:
        """
        Birden fazla dokumani chunk'lara boler.

        Args:
            documents: Document nesneleri listesi.

        Returns:
            Tum chunk'larin birlesik listesi.
        """
        all_chunks: List[Chunk] = []

        for doc in documents:
            chunks = self.split_text(doc.content, metadata=doc.metadata)
            all_chunks.extend(chunks)

        logger.info(
            "documents_chunked",
            doc_count=len(documents),
            total_chunks=len(all_chunks),
        )

        return all_chunks

    def get_stats(self, chunks: List[Chunk]) -> dict:
        """Chunk istatistikleri dondurur."""
        if not chunks:
            return {"total": 0}

        sizes = [c.char_count for c in chunks]
        return {
            "total": len(chunks),
            "avg_size": sum(sizes) // len(sizes),
            "min_size": min(sizes),
            "max_size": max(sizes),
            "total_chars": sum(sizes),
        }
