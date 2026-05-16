"""Transcript extraction and compact question answering helpers.

This module intentionally keeps OCR/text extraction outside the main RAG flow.
Uploaded transcript facts are user-scoped context, not institutional sources.
"""

from __future__ import annotations

import io
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from src.core.text_normalization import normalize_text


_MAX_STORED_COURSES = 240
_DEFAULT_TTL_SECONDS = 60 * 60 * 6
_COURSE_CODE_RE = re.compile(r"\b([A-ZÇĞİÖŞÜ]{2,8}\s?\d{3,4}[A-Z]?)\b", re.IGNORECASE)
_GRADE_RE = re.compile(r"\b(AA|BA|BB|CB|CC|DC|DD|FD|FF|YT|YZ|G|K|P|F)\b", re.IGNORECASE)
_NUMBER_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[,.]\d{1,2})?)(?!\d)")
_FAILED_GRADES = {"FF", "FD", "K", "YZ", "F"}
_PASSED_GRADES = {"AA", "BA", "BB", "CB", "CC", "DC", "DD", "YT", "G", "P"}
_TEXT_EXTENSIONS = {".txt", ".csv"}
_PDF_EXTENSIONS = {".pdf"}
_DOCX_EXTENSIONS = {".docx"}
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
_EXPLICIT_TRANSCRIPT_MARKERS = (
    "transkript",
    "not dokumu",
    "not dokum",
)
_PERSONAL_TRANSCRIPT_MARKERS = (
    "aktsim",
    "kredim",
    "gectigim",
    "kaldigim",
    "derslerim",
    "ortalamam",
)
_TRANSCRIPT_METRIC_MARKERS = (
    "toplam akts",
    "toplam kredi",
    "kac akts",
    "kac kredi",
    "basarisiz",
    "basarili ders",
    "gno",
    "agno",
)
_INSTITUTIONAL_AKTS_MARKERS = (
    "mezun",
    "mezuniyet",
    "program",
    "lisans",
    "onlisans",
    "dis hekimligi",
    "tip",
    "muhendisligi",
    "ogretmenligi",
    "icin kac akts",
)


class TranscriptProcessingError(RuntimeError):
    """Raised when a transcript file cannot be extracted safely."""


class LLMGenerateProtocol(Protocol):
    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
        model_role: str = "default",
        llm_profile: str | None = None,
    ) -> str:
        ...


@dataclass(frozen=True)
class TranscriptCourse:
    code: str
    name: str
    credit: float | None = None
    akts: float | None = None
    grade: str | None = None
    status: str = "unknown"


@dataclass(frozen=True)
class TranscriptDocument:
    filename: str
    text: str
    courses: tuple[TranscriptCourse, ...] = ()
    total_akts: float | None = None
    total_credit: float | None = None
    gpa: float | None = None
    extraction_mode: str = "text"
    warnings: tuple[str, ...] = ()

    @property
    def passed_courses(self) -> tuple[TranscriptCourse, ...]:
        return tuple(course for course in self.courses if course.status == "passed")

    @property
    def failed_courses(self) -> tuple[TranscriptCourse, ...]:
        return tuple(course for course in self.courses if course.status == "failed")


@dataclass
class _StoredTranscript:
    document: TranscriptDocument
    user_id: str
    stored_at: float = field(default_factory=time.monotonic)


class TranscriptSessionStore:
    """Small TTL store keyed by Slack conversation context.

    Keeping this separate from ConversationContextService prevents uploaded
    personal documents from becoming normal RAG/conversation memory.
    """

    def __init__(self, *, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> None:
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, _StoredTranscript] = {}

    def put(self, *, context_id: str, user_id: str, document: TranscriptDocument) -> None:
        self._purge_expired()
        self._items[context_id] = _StoredTranscript(document=document, user_id=user_id)

    def get(self, *, context_id: str, user_id: str) -> TranscriptDocument | None:
        self._purge_expired()
        item = self._items.get(context_id)
        if item is None or item.user_id != user_id:
            return None
        return item.document

    def _purge_expired(self) -> None:
        now = time.monotonic()
        expired = [
            key
            for key, value in self._items.items()
            if now - value.stored_at > self.ttl_seconds
        ]
        for key in expired:
            self._items.pop(key, None)


class TranscriptProcessor:
    """Extract transcript text/facts and answer transcript-scoped questions."""

    def __init__(self, *, llm_service: LLMGenerateProtocol | None = None) -> None:
        self.llm_service = llm_service

    def process_bytes(self, *, filename: str, content: bytes, mimetype: str | None = None) -> TranscriptDocument:
        if not content:
            raise TranscriptProcessingError("Dosya boş görünüyor.")
        extension = Path(filename or "").suffix.lower()
        text, mode, warnings = self._extract_text(
            filename=filename,
            content=content,
            mimetype=mimetype,
            extension=extension,
        )
        if not text.strip():
            raise TranscriptProcessingError("Dosyadan okunabilir transkript metni çıkarılamadı.")

        courses = tuple(_parse_courses(text))[:_MAX_STORED_COURSES]
        total_akts = _extract_total_value(text, kind="akts")
        total_credit = _extract_total_value(text, kind="credit")
        if total_akts is None:
            summed_akts = sum(course.akts or 0 for course in courses if course.status != "failed")
            total_akts = summed_akts if summed_akts > 0 else None
        if total_credit is None:
            summed_credit = sum(course.credit or 0 for course in courses if course.status != "failed")
            total_credit = summed_credit if summed_credit > 0 else None

        return TranscriptDocument(
            filename=filename or "transkript",
            text=_compact_raw_text(text),
            courses=courses,
            total_akts=total_akts,
            total_credit=total_credit,
            gpa=_extract_gpa(text),
            extraction_mode=mode,
            warnings=tuple(warnings),
        )

    async def answer_question(
        self,
        *,
        document: TranscriptDocument,
        query: str,
        llm_profile: str | None = None,
    ) -> str:
        deterministic = _answer_transcript_question(document=document, query=query)
        if deterministic is not None:
            return deterministic
        if self.llm_service is None:
            return _format_transcript_summary(document)

        prompt = _build_llm_transcript_prompt(document=document, query=query)
        try:
            answer = await self.llm_service.generate(
                prompt,
                system=_TRANSCRIPT_QA_SYSTEM_PROMPT,
                model_role="final_refinement",
                llm_profile=llm_profile,
            )
        except Exception:
            return _format_transcript_summary(document)
        cleaned = (answer or "").strip()
        return cleaned or _format_transcript_summary(document)

    def _extract_text(
        self,
        *,
        filename: str,
        content: bytes,
        mimetype: str | None,
        extension: str,
    ) -> tuple[str, str, list[str]]:
        warnings: list[str] = []
        normalized_mimetype = (mimetype or "").lower()
        if extension in _PDF_EXTENSIONS or "pdf" in normalized_mimetype:
            return _extract_pdf_text(content), "pdf_text", warnings
        if extension in _DOCX_EXTENSIONS:
            return _extract_docx_text(content), "docx_text", warnings
        if extension in _TEXT_EXTENSIONS or normalized_mimetype.startswith("text/"):
            return _decode_text(content), "plain_text", warnings
        if extension in _IMAGE_EXTENSIONS or normalized_mimetype.startswith("image/"):
            text = _extract_image_ocr_text(content)
            if text:
                return text, "image_ocr", warnings
            warnings.append("Görsel OCR motoru kurulu değil veya metin çıkarılamadı.")
            raise TranscriptProcessingError(
                "Görsel transkript için OCR motoru şu ortamda hazır değil. PDF veya metin tabanlı transkript yükleyin."
            )
        return _decode_text(content), "plain_text_fallback", warnings


def is_transcript_followup_query(query: str | None) -> bool:
    raw_lower = (query or "").lower()
    if re.search(r"\b(?:akts|kredi)\s*['’]?\s*(?:im|ım|m)\b", raw_lower):
        return True
    normalized = normalize_text(query or "")
    if not normalized:
        return False
    tokens = set(normalized.split())
    if any(marker in normalized for marker in _EXPLICIT_TRANSCRIPT_MARKERS):
        return True
    if any(marker in normalized for marker in _PERSONAL_TRANSCRIPT_MARKERS):
        return True
    if ("akts" in tokens or "kredi" in tokens) and tokens & {"im", "m", "benim"}:
        return True
    has_personal_marker = any(marker in normalized for marker in ("benim", "bende", "aldigim", "kaldim", "gectim"))
    has_metric_marker = any(marker in normalized for marker in ("akts", "kredi", "ders", "ortalama"))
    if has_metric_marker and any(marker in normalized for marker in _INSTITUTIONAL_AKTS_MARKERS) and not has_personal_marker:
        return False
    if any(marker in normalized for marker in _TRANSCRIPT_METRIC_MARKERS) and has_personal_marker:
        return True
    return has_personal_marker and has_metric_marker


def _decode_text(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1254", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def _extract_pdf_text(content: bytes) -> str:
    try:
        import pdfplumber
    except ImportError as exc:
        raise TranscriptProcessingError("PDF metni okumak için pdfplumber kurulu değil.") from exc
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as exc:
        raise TranscriptProcessingError("PDF dosyası okunamadı.") from exc


def _extract_docx_text(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise TranscriptProcessingError("DOCX metni okumak için python-docx kurulu değil.") from exc
    try:
        document = Document(io.BytesIO(content))
    except Exception as exc:
        raise TranscriptProcessingError("DOCX dosyası okunamadı.") from exc
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _extract_image_ocr_text(content: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract
    except Exception:
        return ""
    try:
        image = Image.open(io.BytesIO(content))
        return str(pytesseract.image_to_string(image, lang="tur+eng") or "")
    except Exception:
        return ""


def _parse_courses(text: str) -> list[TranscriptCourse]:
    courses: list[TranscriptCourse] = []
    seen: set[tuple[str, str, str | None]] = set()
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if len(line) < 8:
            continue
        code_match = _COURSE_CODE_RE.search(line)
        if not code_match:
            continue
        course = _parse_course_line(line, code_match)
        if course is None:
            continue
        key = (normalize_text(course.code), normalize_text(course.name), course.grade)
        if key in seen:
            continue
        seen.add(key)
        courses.append(course)
    return courses


def _parse_course_line(line: str, code_match: re.Match[str]) -> TranscriptCourse | None:
    code = code_match.group(1).replace(" ", "").upper()
    tail = line[code_match.end() :].strip(" -|")
    if not tail:
        return None
    grade_match = None
    for match in _GRADE_RE.finditer(tail):
        grade_match = match
    grade = grade_match.group(1).upper() if grade_match else _grade_from_status_words(tail)
    number_region = tail[: grade_match.start()] if grade_match else tail
    numbers = [_to_float(match.group(1)) for match in _NUMBER_RE.finditer(number_region)]
    numbers = [number for number in numbers if number is not None]
    credit = numbers[-2] if len(numbers) >= 2 else None
    akts = numbers[-1] if numbers else None
    name_region = tail[: grade_match.start()] if grade_match else tail
    first_number = _NUMBER_RE.search(name_region)
    if first_number:
        name_region = name_region[: first_number.start()]
    name = name_region.strip(" -|:;")
    if not name or len(name) < 2:
        name = tail[:80].strip(" -|:;")
    status = _status_from_grade_and_text(grade=grade, text=tail)
    return TranscriptCourse(code=code, name=name[:120], credit=credit, akts=akts, grade=grade, status=status)


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def _grade_from_status_words(text: str) -> str | None:
    normalized = normalize_text(text)
    if "basarisiz" in normalized or "kaldi" in normalized:
        return "FF"
    if "basarili" in normalized or "gecti" in normalized:
        return "G"
    return None


def _status_from_grade_and_text(*, grade: str | None, text: str) -> str:
    normalized = normalize_text(text)
    if "basarisiz" in normalized or "kaldi" in normalized:
        return "failed"
    if "basarili" in normalized or "gecti" in normalized:
        return "passed"
    if not grade:
        return "unknown"
    if grade.upper() in _FAILED_GRADES:
        return "failed"
    if grade.upper() in _PASSED_GRADES:
        return "passed"
    return "unknown"


def _extract_total_value(text: str, *, kind: str) -> float | None:
    label_patterns = (
        (r"(?:toplam|kazanılan|kazanilan|tamamlanan|başarılan|basarilan)\s+(?:akts|ects)", "akts"),
        (r"(?:akts|ects)\s+(?:toplamı|toplami|toplam|kazanılan|kazanilan)", "akts"),
        (r"(?:toplam|kazanılan|kazanilan|tamamlanan)\s+(?:kredi|ulusal kredi)", "credit"),
        (r"(?:kredi|ulusal kredi)\s+(?:toplamı|toplami|toplam|kazanılan|kazanilan)", "credit"),
    )
    candidates: list[float] = []
    for label, label_kind in label_patterns:
        if label_kind != kind:
            continue
        pattern = re.compile(label + r"[^0-9]{0,30}(\d{1,3}(?:[,.]\d{1,2})?)", re.IGNORECASE)
        candidates.extend(
            value
            for value in (_to_float(match.group(1)) for match in pattern.finditer(text))
            if value is not None
        )
    if not candidates:
        return None
    return max(candidates)


def _extract_gpa(text: str) -> float | None:
    patterns = (
        r"\b(?:gno|gano|agno|genel not ortalaması|genel not ortalamasi)\b[^0-9]{0,30}(\d{1,2}[,.]\d{1,2})",
        r"\b(?:cgpa|gpa)\b[^0-9]{0,30}(\d{1,2}[,.]\d{1,2})",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _to_float(match.group(1))
    return None


def _answer_transcript_question(*, document: TranscriptDocument, query: str) -> str | None:
    normalized = normalize_text(query)
    if any(marker in normalized for marker in ("kaldi", "kaldigim", "basarisiz", "ff", "fd")):
        return _format_course_list(
            title="Transkriptte başarısız görünen dersler",
            courses=document.failed_courses,
            empty="Transkriptte başarısız ders tespit edemedim.",
        )
    if any(marker in normalized for marker in ("gectigim", "basarili", "gecen ders", "geçtiğim")):
        return _format_course_list(
            title="Transkriptte başarılı görünen dersler",
            courses=document.passed_courses,
            empty="Transkriptte başarılı ders tespit edemedim.",
        )
    if "akts" in normalized:
        if document.total_akts is None:
            return "Transkriptte toplam AKTS bilgisini güvenilir biçimde çıkaramadım."
        return f"Transkriptte görünen toplam AKTS: {_format_number(document.total_akts)}."
    if "kredi" in normalized:
        if document.total_credit is None:
            return "Transkriptte toplam kredi bilgisini güvenilir biçimde çıkaramadım."
        return f"Transkriptte görünen toplam kredi: {_format_number(document.total_credit)}."
    if any(marker in normalized for marker in ("ortalama", "gno", "agno", "gano")):
        if document.gpa is None:
            return "Transkriptte genel not ortalaması bilgisini güvenilir biçimde çıkaramadım."
        return f"Transkriptte görünen genel not ortalaması: {_format_number(document.gpa)}."
    if any(marker in normalized for marker in ("ozet", "durum", "ne gorunuyor", "neler var")):
        return _format_transcript_summary(document)
    return None


def _format_transcript_summary(document: TranscriptDocument) -> str:
    parts = [
        f"Transkript okundu: {document.filename}",
        f"Tespit edilen ders sayısı: {len(document.courses)}",
    ]
    if document.total_akts is not None:
        parts.append(f"Toplam AKTS: {_format_number(document.total_akts)}")
    if document.total_credit is not None:
        parts.append(f"Toplam kredi: {_format_number(document.total_credit)}")
    if document.gpa is not None:
        parts.append(f"GNO/AGNO: {_format_number(document.gpa)}")
    failed_count = len(document.failed_courses)
    if failed_count:
        parts.append(f"Başarısız görünen ders: {failed_count}")
    if document.warnings:
        parts.append("Not: " + " ".join(document.warnings))
    return "\n".join(f"- {part}" for part in parts)


def _format_course_list(*, title: str, courses: tuple[TranscriptCourse, ...], empty: str) -> str:
    if not courses:
        return empty
    lines = [f"{title}:"]
    for course in courses[:30]:
        details = []
        if course.akts is not None:
            details.append(f"AKTS {_format_number(course.akts)}")
        if course.credit is not None:
            details.append(f"kredi {_format_number(course.credit)}")
        if course.grade:
            details.append(f"not {course.grade}")
        suffix = f" ({', '.join(details)})" if details else ""
        lines.append(f"- {course.code} {course.name}{suffix}")
    if len(courses) > 30:
        lines.append(f"- ... {len(courses) - 30} ders daha var.")
    return "\n".join(lines)


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".replace(".", ",").rstrip("0").rstrip(",")


def _compact_raw_text(text: str, *, limit: int = 12000) -> str:
    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip()


def _build_llm_transcript_prompt(*, document: TranscriptDocument, query: str) -> str:
    rows = [
        {
            "code": course.code,
            "name": course.name,
            "credit": course.credit,
            "akts": course.akts,
            "grade": course.grade,
            "status": course.status,
        }
        for course in document.courses[:80]
    ]
    return (
        f"Kullanıcı sorusu: {query}\n"
        "Transkript özet verisi:\n"
        f"- dosya: {document.filename}\n"
        f"- toplam_akts: {document.total_akts}\n"
        f"- toplam_kredi: {document.total_credit}\n"
        f"- gno_agno: {document.gpa}\n"
        f"- dersler: {rows}\n"
        "Yanıtı yalnızca bu transkript verisine dayandır."
    )


_TRANSCRIPT_QA_SYSTEM_PROMPT = """\
Kullanıcının yüklediği transkript verisine göre kısa ve güvenli cevap ver.
Kurallar:
- Transkriptte olmayan bilgiyi uydurma.
- Program mezuniyet şartı, yönetmelik veya kurum politikası yorumu yapma; yalnız transkriptte görünen kişisel ders/AKTS/kredi/not bilgisini kullan.
- Belirsiz çıkarım gerekiyorsa bunu açıkça belirt.
- Cevabı en fazla 4 cümlede tut; ders listesi istenirse maddeleyebilirsin.
"""
