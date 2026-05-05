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
EVENT_SURFACE_DEPARTMENT = "event"
_GLOBAL_SYNTHESIS_ALLOWED_ERRORS = frozenset(
    {
        "department_context_required",
        "student_type_context_required",
    }
)
_NO_INFO_RESPONSE_PATTERNS = (
    "bu konuda elimde yeterli kaynak bulunamadi",
    "bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi",
    "bu konuda elimdeki kaynaklarda net bilgi bulunamadi",
    "verilen kaynaklarda bu soruyu dogrudan yanitlayan net bir bilgi bulunmuyor",
    "elimizdeki kaynaklarda bu konuda yeterli bilgi yok",
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

# Hangul (Korece) karakterler — kucuk LLM'ler bazen Korece token uretir
_HANGUL_RE = re.compile(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]+')

# Kiril alfabesi
_CYRILLIC_RE = re.compile(r'[\u0400-\u04ff\u0500-\u052f]+')

# Arapça/IBranice — LLM bazen bu bloklardan da karakter sizdirir
_ARABIC_HEBREW_RE = re.compile(r'[\u0590-\u05ff\u0600-\u06ff\u0750-\u077f]+')

# Yaygin Ingilizce kelimeler ve Turkce karsiliklari
_EN_TO_TR: dict[str, str] = {
    "international": "uluslararası",
    "specific": "özel",
    "required": "gerekli",
    "needed": "gerekli",
    "success": "başarı",
    "contribution": "katkı",
    "however": "ancak",
    "therefore": "bu nedenle",
    "necessary": "gerekli",
    "important": "önemli",
    "information": "bilgi",
    "informationen": "bilgi",
    "application": "başvuru",
    "process": "süreç",
    "condition": "koşul",
    "requirement": "gereksinim",
    "document": "belge",
    "student": "öğrenci",
    "university": "üniversite",
    "program": "program",
    "education": "eğitim",
    "academic": "akademik",
    "must": "zorunlu",
    "should": "meli",
    "also": "ayrıca",
    "registration": "kayıt",
    "renewal": "yenileme",
    "semester": "dönem",
    "fee": "ücret",
    "fees": "ücretler",
    "refund": "iade",
    "refunded": "iade edilir",
    "cancel": "iptal",
    "canceled": "iptal edilir",
    "graduate": "lisansüstü",
    "doctoral": "doktora",
    "master": "yüksek lisans",
    "programs": "programlar",
    "language": "dil",
    "following": "şu şekilde",
    "several": "birden fazla",
    "informatie": "bilgi",
    "details": "detaylar",
    "detail": "detay",
    "processi": "süreci",
    "applicants": "başvuru sahipleri",
    "applicantsi": "başvuru sahibi",
    "different": "farklı",
    "same": "aynı",
    "necessario": "gerekli",
    "podria": "",
    "requirements": "koşullar",
    "conditions": "koşullar",
    "overview": "özet",
    "timeline": "takvim",
    "approval": "onay",
    "approved": "onaylandı",
    "certain": "belirli",
    "siguientes": "aşağıdaki",
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
    # 1) CJK, Hangul, Kiril, Arapca/Ibranice iceren kelimeleri/kalintileri sil
    text = _CJK_RE.sub('', text)
    text = _HANGUL_RE.sub('', text)
    text = _CYRILLIC_RE.sub('', text)
    text = _ARABIC_HEBREW_RE.sub('', text)

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

    text = re.sub(r"\bonce_online\b", "önce online", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsucces(?:s)?ini\b", "başarısını", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsucces(?:s)?i\b", "başarısı", text, flags=re.IGNORECASE)
    text = re.sub(r"\badem(?:as|\u00e1s)\b", "ayrıca", text, flags=re.IGNORECASE)
    text = re.sub(r"\btambi(?:en|\u00e9n)\b", "ayrıca", text, flags=re.IGNORECASE)
    text = re.sub(r"\bpor favor\b", "lütfen", text, flags=re.IGNORECASE)
    text = re.sub(r"\bnecessario\s+podria\b", "gerekebilir", text, flags=re.IGNORECASE)

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
    text = re.sub(r'\bsu sekilde gibidir\b', 'şu şekildedir', text, flags=re.IGNORECASE)
    text = re.sub(r'\bşu şekilde gibidir\b', 'şu şekildedir', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbirden fazla kaynaklardan\b', 'birden fazla kaynaktan', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbilgi verir misin\b', 'bilgi vereyim', text, flags=re.IGNORECASE)
    # Yabanci dil sızıntıları
    text = re.sub(r'\bsiguientes\b', 'aşağıdaki', text, flags=re.IGNORECASE)
    text = re.sub(r'\bonce_online\b', 'önce online', text, flags=re.IGNORECASE)
    text = re.sub(r'\bademás\b', 'ayrıca', text, flags=re.IGNORECASE)
    text = re.sub(r'\btambién\b', 'ayrıca', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpor favor\b', 'lütfen', text, flags=re.IGNORECASE)
    # Ingilizce kelime sizintilari — LLM bazen Turkce cumle icinde Ingilizce kelimeler birakir
    text = re.sub(r'\b-contrib\b', '-katkı payı', text, flags=re.IGNORECASE)
    text = re.sub(r'\bcontrib\b', 'katkı payı', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhowever\b', 'ancak', text, flags=re.IGNORECASE)
    text = re.sub(r'\btherefore\b', 'bu nedenle', text, flags=re.IGNORECASE)
    text = re.sub(r'\bfurthermore\b', 'ayrıca', text, flags=re.IGNORECASE)
    text = re.sub(r'\bmoreover\b', 'ayrıca', text, flags=re.IGNORECASE)
    text = re.sub(r'\bnevertheless\b', 'buna rağmen', text, flags=re.IGNORECASE)
    text = re.sub(r'\baccordingly\b', 'buna göre', text, flags=re.IGNORECASE)
    text = re.sub(r'\bconsequently\b', 'sonuç olarak', text, flags=re.IGNORECASE)
    text = re.sub(r'\bspecifically\b', 'özel olarak', text, flags=re.IGNORECASE)
    text = re.sub(r'\bapproximately\b', 'yaklaşık', text, flags=re.IGNORECASE)
    text = re.sub(r'\brespectively\b', 'sırasıyla', text, flags=re.IGNORECASE)
    text = re.sub(r'\bregarding\b', 'ilgili', text, flags=re.IGNORECASE)
    text = re.sub(r'\badditionally\b', 'ayrıca', text, flags=re.IGNORECASE)
    text = re.sub(r'\bcontribution\b', 'katkı', text, flags=re.IGNORECASE)
    text = re.sub(r'\bexcluding\b', 'hariç', text, flags=re.IGNORECASE)
    text = re.sub(r'\bincluding\b', 'dahil', text, flags=re.IGNORECASE)
    # Almanca kelime sizintilari — kucuk LLM'ler bazen Almanca kelimeler de birakir
    text = re.sub(r'\bwichtig\b', 'önemli', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbeachten\b', 'dikkat et', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbitte\b', 'lütfen', text, flags=re.IGNORECASE)
    text = re.sub(r'\bjedoch\b', 'ancak', text, flags=re.IGNORECASE)
    text = re.sub(r'\baußerdem\b', 'ayrıca', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdaher\b', 'bu nedenle', text, flags=re.IGNORECASE)
    text = re.sub(r'\bsomit\b', 'böylece', text, flags=re.IGNORECASE)
    text = re.sub(r'\baber\b', 'fakat', text, flags=re.IGNORECASE)
    text = re.sub(r'\bauch\b', 'ayrıca', text, flags=re.IGNORECASE)
    text = re.sub(r'\bnur\b', 'sadece', text, flags=re.IGNORECASE)
    text = re.sub(r'\bnoch\b', 'hala', text, flags=re.IGNORECASE)
    # Hintce/Devanagari karakter sizintisi — kucuk LLM'ler bazen Hintce karakter uretir
    text = re.sub(r'[\u0900-\u097F]+', '', text)

    # 6) Uydurma/yabanci token kalintilari — LLM bazen anlamsiz birlesik kelimeler uretir
    text = re.sub(r'\bdentroslar\w*\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpossibilite\w*\b', 'olasılık', text, flags=re.IGNORECASE)
    text = re.sub(r'\bkonkret\b', 'somut', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbekannt\b', 'bilinen', text, flags=re.IGNORECASE)
    text = re.sub(r'\bcontinuation\b', 'devam', text, flags=re.IGNORECASE)
    text = re.sub(r'\bverificar\w*\b', 'doğrulama', text, flags=re.IGNORECASE)
    text = re.sub(r'\binformación\b', 'bilgi', text, flags=re.IGNORECASE)
    text = re.sub(r'\brequerido\b', 'gerekli', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpuede\b', 'olabilir', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdeber\w*\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bespec\w+\b', '', text, flags=re.IGNORECASE)  # Ispanyolca "especificar" vb.
    text = re.sub(r'\binformationen\b', 'bilgi', text, flags=re.IGNORECASE)
    text = re.sub(r'\bztr\b', 'zayi edilen', text, flags=re.IGNORECASE)
    # "tonabilir" — LLM bazen "tanınabilir" yerine "tonabilir" uretir
    text = re.sub(r'\btonabilir\b', 'tanınabilir', text, flags=re.IGNORECASE)
    text = re.sub(r'\btonabilir\w*\b', 'tanınabilir', text, flags=re.IGNORECASE)
    # Korece "필요" (gerekli) — en sik rastlanan Hangul token
    text = re.sub(r'필요', '', text)

    return text.strip()


def clean_final_answer(answer: str) -> str:
    """LLM veya birlesik cevaptan kalan basit bicim artefaktlarini temizler."""
    cleaned = answer.replace("**", "").strip()
    cleaned = re.split(
        r"(?im)^\s*(?:Uretim Turu|Üretim Türü|Kaynak Ozeti|Kaynak Özeti)\s*:\s*$",
        cleaned,
        maxsplit=1,
    )[0].rstrip()
    cleaned = re.sub(r"(?im)^\s*Merhaba,?\s*$", "", cleaned)
    cleaned = re.sub(
        r"(?im)^\s*(?:Siz,?\s*)?.{0,180}?(?:bilgi almak istiyorsunuz|hakkinda bilgi ariyorsunuz|hakkinda bilgi almak istiyorsunuz)\.?\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?ims)^\s*(?:YANITLAMA STRATEJISI|KAYNAK DOGRULAMA KURALLARI|DEPARTMAN SINIRI KURALLARI)\s*:\s*(?:\n\s*(?:[-*]|\d+[.)]).*?)+(?=\n\s*\n|\Z)",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:YANITLAMA STRATEJISI|KAYNAK DOGRULAMA KURALLARI|DEPARTMAN SINIRI KURALLARI)\s*:?\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:Benchmark|Test)\s*,\s*",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:#+\s*)?(?:Benchmark|Test)\s*:?\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:Benchmark|Test)\s*:\s*",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:Soru|Sorulan soru|Kullanici sorusu)\s*:\s*.*?$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:Yanit|Yanıt|Cevap|Sorunun cevabı|Sorunun cevabi)\s*:\s*",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:Kaynak Bilgisi|Belge kaynaklari|Kaynak Doğrulama|Kaynak Dogrulama)\s*:\s*.*?$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:#+\s*)?(?:Kaynak Bilgisi|Bilgi Kaynagi|Bilgi Kaynağı|Kaynak Izlentileri|Kaynak İzlentileri)\s*:?\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:KAYNAK|Kanit|Kanıt)\s+\d+\s*:\s*.*?$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Sizden gelen sorulara verilecek yaniti hazirlamaya calisacagim\..*?$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Sira geldi soruya yanit verme islemine baslamak\s*:\s*",
        "",
        cleaned,
    )
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
        "Verilen kaynaklarda bu soruyu doğrudan yanıtlayan net bir bilgi bulunmuyor.",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Açık bir bilgi kaynağı bulamadım, ancak.*?$",
        "Verilen kaynaklarda bu soruyu doğrudan yanıtlayan net bir bilgi bulunmuyor.",
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
        r"(?im)^.*?\bcumle bulunamad[ıi]\.?\s*(?:.*?\byonlendir\.?)?\s*$",
        "Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)\s*(?:Ogrenci Isleri|Akademik Programlar|Finans)'?ne yonlendir\.?",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:Kaynaklar|Kanitlar|Sonuc)\s*:\s*",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*(?:Bu cevap|Bu yanit),?\s+OMU.*?i[çc]in\s+uretilmistir\.?\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Kesin yanit icin kaynaklardan devam ediyoruz\s*:?\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Yukar[ıi]daki bilgilendirmeler dogrultusunda,?\s*(?:OMU ogrencileri icin)?\s*:?\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"\bdevama devam zorunlulugu\b",
        "devam zorunlulugu",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bdevam zorunlulugunuz degmez\b",
        "devam zorunlulugunuz degismez",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bonay[ıi]gereken\b",
        "onayi gereken",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bonay(?:\u0131|i)gereken\b",
        "onayi gereken",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = _strip_foreign_words(cleaned)

    # Intra-line repetition loop detection:
    # LLMs (especially small ones) sometimes fall into generation loops
    # where the same phrase repeats many times within a single line.
    # Detect 4+ word phrases repeating 3+ times and truncate.
    def _truncate_repetition_loops(text: str) -> str:
        out_lines: list[str] = []
        for line in text.split("\n"):
            if len(line) > 200:
                words = line.split()
                for ngram_size in (6, 5, 4):
                    if len(words) < ngram_size * 3:
                        continue
                    for start in range(len(words) - ngram_size * 3 + 1):
                        ngram = " ".join(words[start:start + ngram_size])
                        # Count occurrences of this ngram in the rest of the line
                        rest = " ".join(words[start:])
                        count = rest.count(ngram)
                        if count >= 3:
                            # Truncate: keep up to just after the first occurrence
                            first_end = start + ngram_size
                            line = " ".join(words[:first_end])
                            words = line.split()
                            break
                    else:
                        continue
                    break
            out_lines.append(line)
        return "\n".join(out_lines)

    cleaned = _truncate_repetition_loops(cleaned)

    # Sentence deduplication: remove exact duplicate lines
    lines = cleaned.split("\n")
    seen_normalized: set[str] = set()
    deduped_lines: list[str] = []
    for line in lines:
        from src.core.text_normalization import normalize_text as _norm
        normalized_line = _norm(line.strip())
        # Keep empty lines and very short lines (formatting)
        if not normalized_line or len(normalized_line) < 15:
            deduped_lines.append(line)
            continue
        if normalized_line in seen_normalized:
            continue
        seen_normalized.add(normalized_line)
        deduped_lines.append(line)

    # Cross-line structural repetition: lines sharing the same
    # 5-word prefix pattern are capped at 2 occurrences max.
    _prefix_counts: dict[str, int] = {}
    _struct_deduped: list[str] = []
    for line in deduped_lines:
        words = line.split()
        if len(words) >= 5:
            prefix = " ".join(words[:5]).lower()
            count = _prefix_counts.get(prefix, 0)
            if count >= 2:
                continue
            _prefix_counts[prefix] = count + 1
        _struct_deduped.append(line)
    cleaned = "\n".join(_struct_deduped)

    # Remove empty markdown headings (e.g. "### " with nothing after)
    cleaned = re.sub(r"(?m)^#+\s*$", "", cleaned)

    # Remove repeated consecutive headings
    cleaned = re.sub(r"(?m)^(#+\s+.+)\n\1$", r"\1", cleaned)

    no_info_line_re = re.compile(
        r"(?im)^\s*(?:Bu konuda elimdeki kaynaklarda net bilgi bulunamad[ıi]\.?|"
        r"Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamad[ıi]\.?|"
        r"Cevap bulunamad[ıi]\.?)\s*$"
    )
    non_no_info_text = no_info_line_re.sub("", cleaned).strip()
    if non_no_info_text and len(normalize_text(non_no_info_text).split()) >= 8:
        cleaned = no_info_line_re.sub("", cleaned)

    cleaned = cleaned.rstrip()
    if not re.search(r"[.!?:)]\s*$", cleaned) and re.search(
        r"(?i)\b(?:i[cç]in|ve|veya|ayrica|fakat|ise|olarak|olan)\s*$",
        cleaned,
    ):
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        if len(sentences) > 1:
            cleaned = " ".join(sentences[:-1]).strip()

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
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
    if bool(response.success) or response.error in _GLOBAL_SYNTHESIS_ALLOWED_ERRORS:
        return True
    # Kaynak bulunmus ama dusuk skor nedeniyle kural-tabanli "bilgi bulunamadi"
    # donmus cevaplari da senteze dahil et — LLM kaynakları degerlendirsin.
    if response.sources:
        return True
    return False


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


def is_no_info_response(response: DepartmentResponse) -> bool:
    """Kaynak olsa bile kullaniciya fiilen bilgi vermeyen fallback cevaplarini tanir."""
    if is_announcement_response(response):
        return False
    normalized_answer = normalize_text(response_core_answer(response))
    return any(pattern in normalized_answer for pattern in _NO_INFO_RESPONSE_PATTERNS)


def filter_low_confidence_responses(responses: list[DepartmentResponse]) -> list[DepartmentResponse]:
    """Guclu cevaplar varken cok dusuk skorlu yanitlari finalden ayiklar."""
    if len(responses) < 2:
        return responses

    announcement_responses = [
        response for response in responses if is_announcement_response(response)
    ]
    non_announcement = [
        response for response in responses if not is_announcement_response(response)
    ]
    if announcement_responses and non_announcement and all(
        is_no_info_response(response) for response in non_announcement
    ):
        return announcement_responses

    strong_non_announcement = [
        response
        for response in responses
        if (
            not is_announcement_response(response)
            and not is_low_confidence_rag_response(response)
            and not is_no_info_response(response)
        )
    ]
    if not strong_non_announcement:
        return responses

    filtered = [
        response
        for response in responses
        if (
            not is_announcement_response(response)
            and not is_low_confidence_rag_response(response)
            and not is_no_info_response(response)
        )
    ]
    return filtered or strong_non_announcement or responses


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
    if not answer.strip() or "Kaynak Ozeti:" in answer or "Kaynak Özeti:" in answer:
        return answer

    summary = format_source_summary_from_responses(responses)
    if not summary:
        return answer
    return f"{answer.rstrip()}\n\nKaynak Özeti:\n{summary}"


def append_generation_summary(
    answer: str,
    responses: list[DepartmentResponse],
    *,
    used_global_synthesis: bool = False,
) -> str:
    """Cevabin sonuna hangi veri yollarinin kullanildigini ekler."""
    if not answer.strip() or "Uretim Turu:" in answer or "Üretim Türü:" in answer:
        return answer
    if not responses and not used_global_synthesis:
        return answer

    lines = format_generation_summary_lines(
        responses,
        used_global_synthesis=used_global_synthesis,
    )
    if not lines:
        return answer
    return f"{answer.rstrip()}\n\nÜretim Türü:\n{chr(10).join(lines)}"


def append_source_summary_for_sources(answer: str, sources: list[RAGSource]) -> str:
    """Tek basina kaynak listesi verilen cevaplara kaynak ozeti ekler."""
    if not answer.strip() or "Kaynak Ozeti:" in answer or "Kaynak Özeti:" in answer:
        return answer
    if not sources:
        return answer

    labels: list[str] = []
    seen: set[str] = set()
    for source in sources[:5]:
        label = _format_source_label(source)
        if label and label not in seen:
            seen.add(label)
            labels.append(f"- {label}")
    if not labels:
        return answer
    extra = len(sources) - 5
    if extra > 0:
        labels.append(f"- ... ve {extra} kaynak daha")
    return f"{answer.rstrip()}\n\nKaynak Özeti:\n{chr(10).join(labels)}"


def format_generation_summary_lines(
    responses: list[DepartmentResponse],
    *,
    used_global_synthesis: bool = False,
) -> list[str]:
    """Departman bazinda cevap uretim turlerini etiketler."""
    meaningful = [response for response in responses if response.answer.strip()]
    if not meaningful and not used_global_synthesis:
        return []

    non_announcement = [
        response for response in meaningful if not is_announcement_response(response)
    ]
    target = non_announcement or meaningful
    multi_department = len({response.department for response in target}) > 1

    lines: list[str] = []
    if used_global_synthesis:
        lines.append("- Final Sentez: LLM")
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
    if record_type == "event":
        link_type = str(metadata.get("link_type") or "").strip().lower()
        label = metadata.get("label") or metadata.get("title") or compact_text(source.content, max_len=80)
        url = metadata.get("source_url") or metadata.get("url")
        prefix = "Etkinlik eki" if link_type == "attachment" else "Etkinlik kaydi"
        return f"{prefix}: {label}" + (f" ({url})" if url else "")

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
        if isinstance(db_data, dict) and db_data.get("query_type") == "schedule_lookup":
            return "Veritabani kaydi: ders programi"
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
    has_strong_rag = any(
        (
            not is_announcement_response(r)
            and not is_low_confidence_rag_response(r)
            and not is_no_info_response(r)
        )
        for r in meaningful
    )
    meaningful.sort(
        key=lambda response: (
            1 if is_announcement_response(response) and has_strong_rag else 0,
            0 if is_announcement_response(response) else 1,
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
