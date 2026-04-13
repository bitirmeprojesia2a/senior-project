"""Orkestrator final yanit birlestirme yardimcilari."""

from __future__ import annotations

import re
import unicodedata

from src.core.constants import Department
from src.core.messages import CONTACT_SEPARATOR, CONTACT_SUGGESTION
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse, RAGSource

DEPARTMENT_SECTION_TITLES: dict[Department, str] = {
    Department.STUDENT_AFFAIRS: "Ogrenci Isleri",
    Department.ACADEMIC_PROGRAMS: "Akademik Programlar",
    Department.FINANCE: "Finans",
}

DEPARTMENT_DISPLAY_ORDER: dict[Department, int] = {
    Department.STUDENT_AFFAIRS: 0,
    Department.ACADEMIC_PROGRAMS: 1,
    Department.FINANCE: 2,
}

LOW_CONFIDENCE_RERANKER_SCORE_THRESHOLD = 0.23
LOW_CONFIDENCE_RETRIEVAL_SCORE_THRESHOLD = 0.05
GENERATION_MODE_LABELS = {
    "vt": "VT",
    "rag": "RAG",
    "llm": "LLM",
    "kural": "Kural",
}
ANNOUNCEMENT_SURFACE_DEPARTMENT = "announcement"
_GLOBAL_SYNTHESIS_ALLOWED_ERRORS = frozenset(
    {
        "department_context_required",
        "student_type_context_required",
    }
)


def split_answer_and_contact_flag(answer: str) -> tuple[str, bool]:
    """Cevabi ana govde ve iletisim eki olarak ayirir."""
    stripped = answer.strip()
    if CONTACT_SEPARATOR not in stripped:
        return stripped, False
    core, _ = stripped.split(CONTACT_SEPARATOR, 1)
    return core.rstrip(), True


def response_core_answer(response: DepartmentResponse) -> str:
    """DepartmentResponse icin sunum eklerinden arinmis ana cevap govdesi."""
    core, _ = split_answer_and_contact_flag(response.answer)
    return core


def response_needs_contact_suggestion(response: DepartmentResponse) -> bool:
    """Yeni yapisal bayrak veya eski gomulu format ile iletisim ekini tanir."""
    if bool(getattr(response, "include_contact_suggestion", False)):
        return True
    _, embedded = split_answer_and_contact_flag(response.answer)
    return embedded


def compact_text(value: str, *, max_len: int = 420) -> str:
    """Bosluklari sikistirir ve gerekirse kisaltir."""
    compact = re.sub(r"\s+", " ", value).strip()
    if len(compact) > max_len:
        return f"{compact[: max_len - 3].rstrip()}..."
    return compact


# ── Yabanci dil filtresi ──────────────────────────────────────────
# LLM bazen Turkce cevaba yabanci kelime sizdirir.
# CJK, Kiril, yaygin Ingilizce kelimeler ve Turkce'ye ait olmayan aksanlar.

# CJK Unified Ideographs + Hiragana + Katakana
_CJK_RE = re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uff00-\uffef]+')

# Kiril alfabesi
_CYRILLIC_RE = re.compile(r'[\u0400-\u04ff\u0500-\u052f]+')

# Yaygin Ingilizce kelimeler ve Turkce karsiliklari
_EN_TO_TR: dict[str, str] = {
    "international": "uluslararasi",
    "specific": "ozel",
    "required": "gerekli",
    "needed": "gerekli",
    "success": "basari",
    "contribution": "katki",
    "however": "ancak",
    "therefore": "bu nedenle",
    "necessary": "gerekli",
    "important": "onemli",
    "information": "bilgi",
    "application": "basvuru",
    "process": "surec",
    "condition": "kosul",
    "requirement": "gereksinim",
    "document": "belge",
    "student": "ogrenci",
    "university": "universite",
    "program": "program",
    "education": "egitim",
    "academic": "akademik",
    "must": "zorunlu",
    "should": "meli",
    "also": "ayrica",
    "registration": "kayit",
    "renewal": "yenileme",
    "semester": "donem",
    "fee": "ucret",
    "fees": "ucretler",
    "refund": "iade",
    "refunded": "iade edilir",
    "cancel": "iptal",
    "canceled": "iptal edilir",
    "graduate": "lisansustu",
    "doctoral": "doktora",
    "master": "yuksek lisans",
    "programs": "programlar",
    "language": "dil",
    "following": "su sekilde",
    "several": "birden fazla",
    "informatie": "bilgi",
    "details": "detaylar",
    "detail": "detay",
    "requirements": "kosullar",
    "conditions": "kosullar",
    "overview": "ozet",
    "timeline": "takvim",
    "approval": "onay",
    "approved": "onaylandi",
    "siguientes": "asagidaki",
}

# Turkce'ye ait olmayan aksanli harfler (é, è, ê, ñ, å, ø, vb.)
# Türkçe'de sadece: ç, ğ, ı, ö, ş, ü ve büyük karşılıkları geçerli.
_NON_TURKISH_ACCENT_RE = re.compile(r'\b\w*[éèêëàáâãåæìíîïòóôõøùúûÿñ\u00df]\w*\b', re.IGNORECASE)


_FOREIGN_DIACRITIC_WORD_RE = re.compile(r"\b[^\W\d_]+\b", re.UNICODE)
_TURKISH_EXTENDED_CHARS = frozenset("abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")
_ASCII_WORD_RE = re.compile(r"\b[a-z]{2,}\b", re.IGNORECASE)
_ENGLISH_LINE_HINTS = frozenset(
    {
        "the", "and", "for", "with", "that", "this", "from", "after", "before",
        "during", "will", "would", "should", "could", "must", "is", "are", "was",
        "were", "be", "been", "being", "if", "then", "than", "into", "through",
        "because", "while", "where", "when", "which", "registration", "semester",
        "fee", "fees", "refund", "refunded", "cancel", "canceled", "program", "programs",
        "language", "student", "students", "application", "required", "however", "therefore",
    }
)


def _strip_foreign_words(text: str) -> str:
    """Cevaptaki yabanci dil kalintilarini temizler."""
    # 1) CJK ve Kiril iceren kelimeleri/kalintileri sil
    text = _CJK_RE.sub('', text)
    text = _CYRILLIC_RE.sub('', text)

    # 2) Yaygin Ingilizce kelimeleri Turkce karsiliklariyla degistir.

    def _apply_case_style(match: re.Match, replacement: str) -> str:
        word = match.group(0)
        if word.isupper():
            return replacement.upper()
        if word[:1].isupper():
            return replacement[:1].upper() + replacement[1:]
        return replacement

    for en_word, tr_word in _EN_TO_TR.items():
        # Tam kelime eslesmesi icin word boundary
        pattern = re.compile(r'\b' + re.escape(en_word) + r'\b', re.IGNORECASE)
        text = pattern.sub(lambda match: _apply_case_style(match, tr_word), text)

    text = re.sub(r"\bonce_online\b", "once online", text, flags=re.IGNORECASE)
    text = re.sub(r"\badem(?:as|\u00e1s)\b", "ayrica", text, flags=re.IGNORECASE)
    text = re.sub(r"\btambi(?:en|\u00e9n)\b", "ayrica", text, flags=re.IGNORECASE)
    text = re.sub(r"\bpor favor\b", "lutfen", text, flags=re.IGNORECASE)

    # 3) Turkce'ye ait olmayan aksanli kelimeleri temizle
    #    Ornek: "konkrét" → "konkret", "éxito" → sil
    def _replace_non_turkish_accent(m: re.Match) -> str:
        word = m.group(0)
        # Basit normalizasyon: aksanli harfleri aksansiz karsiligina cevir
        accent_map = str.maketrans({
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'å': 'a',
            'æ': 'ae',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ø': 'o',
            'ù': 'u', 'ú': 'u', 'û': 'u',
            'ÿ': 'y', 'ñ': 'n', 'ß': 'ss',
        })
        return word.translate(accent_map)

    text = _NON_TURKISH_ACCENT_RE.sub(_replace_non_turkish_accent, text)

    def _normalize_foreign_diacritic_word(match: re.Match) -> str:
        word = match.group(0)
        if not any(ord(ch) > 127 for ch in word):
            return word
        if all((ch in _TURKISH_EXTENDED_CHARS) or ord(ch) < 128 for ch in word):
            return word
        decomposed = unicodedata.normalize("NFKD", word)
        stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
        ascii_only = stripped.encode("ascii", "ignore").decode("ascii")
        return ascii_only or stripped or word

    text = _FOREIGN_DIACRITIC_WORD_RE.sub(_normalize_foreign_diacritic_word, text)
    text = re.sub(r"\bhe\s+thong\w*\b", "sistem", text, flags=re.IGNORECASE)

    # 4) Hala baskin sekilde Ingilizce kalan satirlari tumden at.
    cleaned_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            cleaned_lines.append(raw_line)
            continue
        normalized_line = normalize_text(line)
        tokens = _ASCII_WORD_RE.findall(normalized_line)
        english_hits = sum(token in _ENGLISH_LINE_HINTS for token in tokens)
        if tokens and len(tokens) >= 5 and english_hits >= 3 and (english_hits * 2) >= len(tokens):
            continue
        cleaned_lines.append(raw_line)
    text = "\n".join(cleaned_lines)

    # 5) Temizleme sonrasi olusan cift bosluklari ve bos satirlari duzelt
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\bsu sekilde gibidir\b', 'su sekildedir', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbirden fazla kaynaklardan\b', 'birden fazla kaynaktan', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbilgi verir misin\b', 'bilgi vereyim', text, flags=re.IGNORECASE)
    # Yabanci dil sızıntıları
    text = re.sub(r'\bsiguientes\b', 'asagidaki', text, flags=re.IGNORECASE)
    text = re.sub(r'\bonce_online\b', 'once online', text, flags=re.IGNORECASE)
    text = re.sub(r'\bademás\b', 'ayrica', text, flags=re.IGNORECASE)
    text = re.sub(r'\btambién\b', 'ayrica', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpor favor\b', 'lutfen', text, flags=re.IGNORECASE)

    return text.strip()


def clean_final_answer(answer: str) -> str:
    """LLM veya birlesik cevaptan kalan basit bicim artefaktlarini temizler."""
    cleaned = answer.replace("**", "").strip()
    cleaned = re.sub(
        r"^(?:Test,\s*)?Sen\s+Ondokuz\s+Mayis\s+Universitesi.*?(?:\n\s*\n|$)",
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )
    cleaned = re.sub(
        r"^(?:Test,\s*)?Sen\s+Ondokuz\s+Mayıs\s+Üniversitesi.*?(?:\n\s*\n|$)",
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )
    cleaned = re.sub(
        r"(?im)^\s*Uzun zamandir bu konularla.*?$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Acik bir bilgi kaynagi bulamadim, ancak.*?$",
        "Verilen kaynaklarda bu soruyu dogrudan yanitlayan net bir bilgi bulunmuyor.",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Açık bir bilgi kaynağı bulamadım, ancak.*?$",
        "Verilen kaynaklarda bu soruyu dogrudan yanitlayan net bir bilgi bulunmuyor.",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Onerime gore,.*?$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"^(?:Test,\s*)?Sayin Ogrenci,\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?im)^\s*Lutfen not ediniz ki,.*?$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:Kaynaklar|Kanitlar|Sonuc)\s*:\s*",
        "",
        cleaned,
    )
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = _strip_foreign_words(cleaned)
    return cleaned


def is_announcement_response(response: DepartmentResponse) -> bool:
    """Duyuru ajanindan gelen saf duyuru cevaplarini tanir."""
    answer = response.answer.strip()
    if answer.startswith("Ilgili duyurular:"):
        return True
    return bool(response.sources) and all(
        source.metadata.get("record_type") == "announcement"
        for source in response.sources
    )


def response_eligible_for_global_synthesis(response: DepartmentResponse) -> bool:
    """Return whether a response is safe and useful to include in global synthesis."""
    if not response.answer.strip() or is_announcement_response(response):
        return False
    return bool(response.success) or response.error in _GLOBAL_SYNTHESIS_ALLOWED_ERRORS


def surface_department_label(response: DepartmentResponse) -> str:
    """Internal department kimliginden ayri, kullanici/raporlama yuzey etiketini doner."""
    if is_announcement_response(response):
        return ANNOUNCEMENT_SURFACE_DEPARTMENT
    return response.department.value


def collect_surface_departments(responses: list[DepartmentResponse]) -> list[str]:
    """Response listesinden sira koruyarak yuzey departman etiketlerini cikarir."""
    return list(
        dict.fromkeys(
            surface_department_label(response)
            for response in responses
            if response.answer.strip()
        )
    )


def top_source_score(response: DepartmentResponse) -> float:
    """Bir departman cevabindaki en yuksek kaynak skorunu doner."""
    if not response.sources:
        return 0.0
    return max(float(source.score) for source in response.sources)


def _source_low_confidence_threshold(source: RAGSource) -> float:
    score_type = str((source.metadata or {}).get("score_type", "retrieval")).strip().lower()
    if score_type == "reranker":
        return LOW_CONFIDENCE_RERANKER_SCORE_THRESHOLD
    return LOW_CONFIDENCE_RETRIEVAL_SCORE_THRESHOLD


def is_low_confidence_rag_response(response: DepartmentResponse) -> bool:
    """Sadece dusuk skorlu RAG sonuclarina dayanan zayif cevaplari tanir."""
    if is_announcement_response(response):
        return False
    if response.db_data:
        return False
    if not response.sources:
        return False
    return all(
        float(source.score) < _source_low_confidence_threshold(source)
        for source in response.sources
    )


def filter_low_confidence_responses(responses: list[DepartmentResponse]) -> list[DepartmentResponse]:
    """Guclu cevaplar varken cok dusuk skorlu yanitlari finalden ayiklar."""
    if len(responses) < 2:
        return responses

    strong_non_announcement = [
        response
        for response in responses
        if not is_announcement_response(response) and not is_low_confidence_rag_response(response)
    ]
    if not strong_non_announcement:
        return responses

    filtered = [
        response
        for response in responses
        if is_announcement_response(response) or not is_low_confidence_rag_response(response)
    ]
    return filtered or responses


def format_source_summary_from_responses(responses: list[DepartmentResponse]) -> str:
    """Final cevap icin kisa kaynak ozeti uretir."""
    lines: list[str] = []
    seen: set[str] = set()

    for response in responses:
        if response.sources:
            for source in response.sources:
                label = _format_source_label(source)
                if label and label not in seen:
                    seen.add(label)
                    lines.append(f"- {label}")
            continue

        label = _infer_non_document_source_label(response)
        if label and label not in seen:
            seen.add(label)
            lines.append(f"- {label}")

    return "\n".join(lines)


def append_source_summary(answer: str, responses: list[DepartmentResponse]) -> str:
    """Cevabin sonuna kaynak ozetini ekler."""
    if not answer.strip() or "Kaynak Ozeti:" in answer:
        return answer

    summary = format_source_summary_from_responses(responses)
    if not summary:
        return answer
    return f"{answer.rstrip()}\n\nKaynak Ozeti:\n{summary}"


def append_generation_summary(answer: str, responses: list[DepartmentResponse]) -> str:
    """Cevabin sonuna hangi veri yollarinin kullanildigini ekler."""
    if not answer.strip() or "Uretim Turu:" in answer:
        return answer
    if not responses:
        return answer

    lines = format_generation_summary_lines(responses)
    if not lines:
        return answer
    return f"{answer.rstrip()}\n\nUretim Turu:\n{chr(10).join(lines)}"


def append_source_summary_for_sources(answer: str, sources: list[RAGSource]) -> str:
    """Tek basina kaynak listesi verilen cevaplara kaynak ozeti ekler."""
    if not answer.strip() or "Kaynak Ozeti:" in answer:
        return answer
    if not sources:
        return answer

    labels: list[str] = []
    seen: set[str] = set()
    for source in sources:
        label = _format_source_label(source)
        if label and label not in seen:
            seen.add(label)
            labels.append(f"- {label}")
    if not labels:
        return answer
    return f"{answer.rstrip()}\n\nKaynak Ozeti:\n{chr(10).join(labels)}"


def format_generation_summary_lines(responses: list[DepartmentResponse]) -> list[str]:
    """Departman bazinda cevap uretim turlerini etiketler."""
    meaningful = [response for response in responses if response.answer.strip()]
    if not meaningful:
        return []

    non_announcement = [
        response for response in meaningful if not is_announcement_response(response)
    ]
    target = non_announcement or meaningful
    multi_department = len({response.department for response in target}) > 1

    lines: list[str] = []
    for response in target:
        label = _format_generation_mode_label(_infer_generation_mode(response))
        if multi_department:
            title = DEPARTMENT_SECTION_TITLES.get(response.department, response.department.value)
            lines.append(f"- {title}: {label}")
        else:
            lines.append(f"- {label}")
    return lines


def collect_generation_modes(responses: list[DepartmentResponse]) -> list[str]:
    """Yanitlardan yapisal uretim modu listesi uretir."""
    meaningful = [response for response in responses if response.answer.strip()]
    if not meaningful:
        return []
    return list(
        dict.fromkeys(
            _infer_generation_mode(response)
            for response in meaningful
        )
    )


def _format_source_label(source: RAGSource) -> str | None:
    metadata = source.metadata or {}
    record_type = metadata.get("record_type")
    if record_type == "announcement":
        title = metadata.get("title") or compact_text(source.content, max_len=80)
        url = metadata.get("source_url")
        return f"Duyuru kaydi: {title}" + (f" ({url})" if url else "")

    filename = (
        metadata.get("display_source")
        or metadata.get("source")
        or metadata.get("filename")
        or metadata.get("file_name")
        or metadata.get("source_url")
    )
    if filename:
        return f"Belge: {filename}"
    if source.content:
        return f"Belge parcasi: {compact_text(source.content, max_len=80)}"
    return None


def _infer_generation_mode(response: DepartmentResponse) -> str:
    explicit = (response.generation_mode or "").strip().lower()
    if explicit:
        return explicit

    answer = response.answer.strip()
    if response.error in {
        "authentication_required",
        "student_id_required",
        "department_context_required",
        "student_not_found",
    }:
        return "kural"
    if answer.startswith("Ilgili birim iletisim bilgileri:"):
        return "kural"
    if is_announcement_response(response):
        return "vt"
    if response.db_data and response.sources:
        return "vt+rag"
    if response.db_data:
        return "vt"
    if response.sources:
        return "rag"
    return "kural"


def _format_generation_mode_label(mode: str) -> str:
    parts = [
        GENERATION_MODE_LABELS.get(part, part.upper())
        for part in str(mode or "kural").split("+")
        if part
    ]
    if not parts:
        return "Kural"
    return " + ".join(parts)


def _infer_non_document_source_label(response: DepartmentResponse) -> str | None:
    answer = response.answer.strip()
    db_data = response.db_data or {}

    if answer.startswith("Ilgili birim iletisim bilgileri:"):
        title = DEPARTMENT_SECTION_TITLES.get(response.department, response.department.value)
        return f"Ofis iletisim kaydi: {title}"

    if answer.startswith("Su anda sistemde kayitli aktif duyuru bulunmuyor"):
        return "Duyuru veritabani: eslesen aktif kayit bulunamadi"

    if not db_data:
        return None

    if response.department == Department.ACADEMIC_PROGRAMS:
        if isinstance(db_data, dict) and (
            "prerequisite_groups" in db_data or "course_code" in db_data
        ):
            return "Veritabani kaydi: ders onkosulu"
        if isinstance(db_data, dict) and "courses" in db_data:
            return "Veritabani kaydi: mufredat / ders plani"

    if response.department == Department.STUDENT_AFFAIRS:
        if isinstance(db_data, dict) and (
            "semester" in db_data or "registration_period_configured" in db_data
        ):
            return "Veritabani kaydi: kayit donemi"
        return "Veritabani kaydi: ogrenci isleri"

    if response.department == Department.FINANCE:
        if isinstance(db_data, dict) and (
            "annual_amount" in db_data or "semester_amount" in db_data
        ):
            return "Veritabani kaydi: ogrenim ucreti tablosu"
        return "Veritabani kaydi: finans"

    return None


def compose_department_answers(responses: list[DepartmentResponse]) -> str:
    """Departman cevaplarini tek veya coklu bolum formatinda birlestirir."""
    if not responses:
        return ""

    sections: list[str] = []
    include_contact = False
    meaningful = [response for response in responses if response.answer.strip()]
    meaningful.sort(
        key=lambda response: (
            1 if is_announcement_response(response) else 0,
            DEPARTMENT_DISPLAY_ORDER.get(response.department, 99),
        )
    )
    non_announcement = [
        response for response in meaningful if not is_announcement_response(response)
    ]
    multi_department = len({response.department for response in non_announcement}) > 1

    for response in meaningful:
        answer = response_core_answer(response).strip()
        if response_needs_contact_suggestion(response):
            include_contact = True

        if multi_department:
            if is_announcement_response(response):
                title = "Duyurular"
            else:
                title = DEPARTMENT_SECTION_TITLES.get(response.department, response.department.value)
            sections.append(f"{title}:\n{answer}")
        else:
            sections.append(answer)

    final_answer = "\n\n".join(section for section in sections if section)
    if include_contact:
        final_answer += CONTACT_SUGGESTION
    return final_answer
