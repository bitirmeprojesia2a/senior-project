"""Policy helpers for rule-based department routing."""

from __future__ import annotations

import re

from src.core.constants import Department, TaskType
from src.core.query_markers import ACADEMIC_DEPARTMENT_CONTEXT_MARKERS
from src.core.text_normalization import normalize_text
from src.routing.query_concepts import (
    CONCEPT_ACADEMIC_CALENDAR,
    CONCEPT_AKTS,
    CONCEPT_ANNOUNCEMENT,
    CONCEPT_CAP,
    CONCEPT_COMPLAINT,
    CONCEPT_COURSE_CODE,
    CONCEPT_EXEMPTION,
    CONCEPT_GRADUATION,
    CONCEPT_HORIZONTAL_TRANSFER,
    CONCEPT_IDENTITY_CARD,
    CONCEPT_INTERNATIONAL,
    CONCEPT_INTERNSHIP,
    CONCEPT_MAKEUP_EXAM,
    CONCEPT_REGISTRATION,
    CONCEPT_SCHOLARSHIP,
    CONCEPT_SINGLE_EXAM,
    CONCEPT_STUDENT_DOCUMENT,
    CONCEPT_STUDENT_SERVICES,
    CONCEPT_TIMING,
    CONCEPT_YAZ_OKULU,
    CAPABILITY_ANNOUNCEMENT,
    extract_query_concepts,
)

CAP_OR_YAP_IN_QUERY = re.compile(
    r"\b(?:çap|cap)(?:i|a|in|dan|ta|tan|lar|lari|larin)?\b|\b(?:yandal|yan\s+dal)\b",
    re.IGNORECASE,
)
_ROUTING_NEGATION_WORDS: tuple[str, ...] = (
    "sormuyorum",
    "sormuyodum",
    "sormadim",
    "degil",
    "istemiyorum",
    "bahsetmiyorum",
    "kastetmiyorum",
)
ROUTING_PAYMENT_MARKERS: tuple[str, ...] = (
    "ucret", "harc", "odeme", "taksit", "dekont",
    "katki payi", "borc", "borclu", "iade", "fazla ucret",
    "ogrenim ucreti", "banka", "havale", "tahsilat",
)
ROUTING_REGISTRATION_MARKERS: tuple[str, ...] = (
    "kayit", "kayd", "yenileme", "ders kaydi",
    "ders secimi", "ders ekleme", "ders birakma",
)
ROUTING_TIMING_MARKERS: tuple[str, ...] = (
    "basvuru", "ne zaman", "zaman", "takvim", "tarih", "surec",
    "son gun", "son tarih", "acildi mi", "basladi mi",
    "ne kadar surer", "hangisi once",
)
ROUTING_ACADEMIC_CONTEXT_MARKERS: tuple[str, ...] = ACADEMIC_DEPARTMENT_CONTEXT_MARKERS
ROUTING_ACADEMIC_CALENDAR_MARKERS: tuple[str, ...] = (
    "akademik takvim",
    "kayit donemi",
    "ders kaydi takvimi",
    "ders kayit tarihi",
    "yariyil baslangici",
    "donem baslangici",
    "final donemi",
    "final sinavlari",
    "final sinavlarinin",
    "butunleme sinavlari",
    "butunleme sinavlarinin",
    "ara sinavlari",
    "ara sinavlarinin",
    "sinav takvimi",
    "sinav tarihleri",
)
ROUTING_FORMAL_RULE_MARKERS: tuple[str, ...] = (
    "azami",
    "azami sure",
    "azami ogrenim suresi",
    "butunleme",
    "devam zorunlulugu",
    "devam yuzdesi",
    "devamsizlik",
    "not sistemi",
    "degerlendirme sistemi",
    "bagil degerlendirme",
    "harf notu",
    "gecme notu",
    "basari notu",
    "sinif tekrari",
    "ders tekrari",
    # Sınav hakkı/kuralı
    "sinav hakki",
    "kac kez sinav",
    "sinav sayisi",
    "sinava girme sarti",
    "final sinavi sart",
    "butunleme hakki",
    "sinav hakkina",
)
ROUTING_STUDENT_AFFAIRS_RULE_MARKERS: tuple[str, ...] = (
    "butunleme",
    "butunleme hakki",
    "devamsizlik",
    "devam zorunlulugu",
    "devam kosulu",
    "kopya",
    "disiplin",
    "disiplin sureci",
    "sorusturma",
    "sikayet",
    "hocami sikayet",
    "hocam sikayet",
    "ogretim elemani",
    "akademik personel",
    "etik",
    "tutanak",
    "ders tekrari",
    "basarisiz oldugum",
    "basarisiz olunan",
    "tekrar alabilir",
)
ROUTING_STUDENT_AFFAIRS_ADMIN_MARKERS: tuple[str, ...] = (
    "itiraz",
    "not itiraz",
    "sinav notu itiraz",
    "maddi hata",
    "kopya",
    "disiplin",
    "disiplin sureci",
    "disiplin cezasi",
    "sorusturma",
    "sikayet",
    "hocami sikayet",
    "hocam sikayet",
    "ogretim elemani",
    "akademik personel",
    "etik",
    "tutanak",
    "notum sisteme",
    "notlarim sisteme",
    "not girmemis",
    "not girilmemis",
    "sisteme girmemis",
    "sisteme girilmemis",
)
ROUTING_GRADE_VISIBILITY_MARKERS: tuple[str, ...] = (
    "sinav notlarimi",
    "sinav notlarim",
    "ders notlarimi",
    "ders notlarim",
    "notlarimi nereden",
    "notlarim nereden",
    "notlarimi nerede",
    "notlarim nerede",
    "notlarimi nasil",
    "notlarim nasil",
)
ROUTING_PROCEDURAL_VISIBILITY_MARKERS: tuple[str, ...] = (
    "nereden",
    "nerede",
    "nasil",
    "gorebilirim",
    "goruntuleyebilirim",
    "takip edebilirim",
    "bakabilirim",
)
ROUTING_PEDAGOGICAL_FORMATION_MARKERS: tuple[str, ...] = (
    "pedagojik formasyon",
    "formasyon ders",
    "formasyon egitimi",
)
ROUTING_HORIZONTAL_TRANSFER_MARKERS: tuple[str, ...] = (
    "yatay gecis",
    "kurum ici yatay",
    "kurumlar arasi yatay",
    "ek madde",
)
ROUTING_MAX_DURATION_MARKERS: tuple[str, ...] = (
    "azami",
    "azami sure",
    "azami ogrenim suresi",
    "program suresi",
    "ek sure",
    "sure hakki",
)
ROUTING_INTERNATIONAL_MARKERS: tuple[str, ...] = (
    "erasmus",
    "uluslararasi",
    "yabanci",
    "ikamet",
    "denklik",
    "tomer",
    "yos",
    "exchange",
    "mevlana",
    "farabi",
    "degisim programi",
    "yabanci ogrenci",
    "goc idaresi",
)
ROUTING_CAP_MARKERS: tuple[str, ...] = (
    "cap", "cift anadal", "cift ana dal", "yandal", "yan dal",
    "ikinci lisans",
)
ROUTING_STUDENT_DOCUMENT_MARKERS: tuple[str, ...] = (
    "transkript",
    "ogrenci belgesi",
    "ogrenci kimlik",
    "ogrenci kimligi",
    "ogrenci kart",
    "kimlik kart",
    "kimlik karti",
    "kimligim kayip",
    "kimligimi kaybettim",
    "kartim kayip",
    "kartimi kaybettim",
    "transkript belgesi",
    "diploma eki",
    "not dokumu",
    "kayit belgesi",
    "ogrenci durum belgesi",
    "askerlik belgesi",
    "tecil belgesi",
)
ROUTING_STUDENT_DOCUMENT_REQUEST_MARKERS: tuple[str, ...] = (
    "belge nasil al",
    "belgemi nasil al",
    "belgeyi nasil al",
    "nereden alabilirim",
    "belge almak istiyorum",
    "belge basvurusu",
)
ROUTING_STUDENT_SERVICES_MARKERS: tuple[str, ...] = (
    "sifre",
    "parola",
    "ubys",
    "obs",
    "ilisik kesme",
    "kayit dondurma",
    "donem dondurma",
    "dondur",
    "kayit sildirme",
    "kaydimi sil",
    "kaydini sil",
    "kaydi sil",
    "sifre sifirlama",
    "giris yapamiyorum",
    "ilisik",
    "ayril",
    "birak",
    "ayrilmak",
    "birakmak",
    "ayrilma",
    "birakma",
)
ROUTING_SCHOLARSHIP_MARKERS: tuple[str, ...] = (
    "burs",
    "hibe",
    "scholarship",
    "yemek bursu",
    "kismi zamanli",
    "burs basvurusu",
    "basari bursu",
    "ihtiyac bursu",
)
ROUTING_ANNOUNCEMENT_MARKERS: tuple[str, ...] = (
    "duyuru",
    "duyurular",
    "haber",
    "haberler",
    "guncel duyuru",
    "guncel duyur",
    "son duyuru",
    "son duyur",
    "son aciklanan",
    "yeni duyuru",
    "duyuru var mi",
    "duyurular neler",
    "duyurulari",
    "ilan",
    "ilanlar",
    "bilgilendirme",
)
ROUTING_INTERNSHIP_MARKERS: tuple[str, ...] = (
    "staj",
    "mup",
    "mesleki uygulama",
    "sanayi uygulamasi",
    "bitirme projesi",
    "zorunlu staj",
    "staj defteri",
    "staj sigorta",
)
ROUTING_SUMMER_SCHOOL_MARKERS: tuple[str, ...] = (
    "yaz okulu",
    "yaz okuluna",
    "yaz okulundan",
    "yaz donemi",
    "yaz ogretimi",
    "misafir ogrenci",
    "yaz okulu basvuru",
    "yaz okulu kayit",
)
ROUTING_GENERAL_AKTS_MARKERS: tuple[str, ...] = (
    "mezun olmak icin kac akts gerekir",
    "mezuniyet icin kac akts gerekir",
    "kac akts tamamlamali",
    "kac akts tamamlamalidir",
    "akts tamamlamali",
    "akts tamamlamalidir",
    "toplam akts",
    "akts gerekli",
    "kredi gerekli",
    "mezuniyet kredisi",
)
ROUTING_AKTS_MARKERS: tuple[str, ...] = (
    "akts", "ects", "kredim", "akts hesap",
    "donem akts", "toplam akts", "mezuniyet akts",
    "akts hakki", "kredi hakki", "kredi siniri",
    "donem yuku", "ders yuku", "maximum akts",
    "azami akts", "azami kredi",
)
# Sadece ders kaydi/GANO iliskili AKTS markerlari — müfredat AKTS degil
ROUTING_AKTS_REGISTRATION_MARKERS: tuple[str, ...] = (
    "akts hakki", "akts hakki", "kredi hakki", "kredi siniri",
    "donem yuku", "ders yuku", "maximum akts", "azami akts", "azami kredi",
    "gano", "gno", "kac akts alabilirim", "kac kredi alabilirim",
    "akts siniri", "kredi siniri", "donemlik akts",
)
ROUTING_SINGLE_EXAM_MARKERS: tuple[str, ...] = (
    "tek ders sinavi", "tek ders", "tek sinav",
)
ROUTING_MAKEUP_EXAM_MARKERS: tuple[str, ...] = (
    "butunleme", "butunleme sinavi", "ek sinav",
    "ek sinav hakki", "mazeret sinavi", "mazeret",
)
ROUTING_IDENTITY_CARD_MARKERS: tuple[str, ...] = (
    "kimlik karti", "ogrenci kimligi", "ogrenci kimlik",
    "kimlik kaybi", "kimlik yenileme", "kimlik basvuru",
)
ROUTING_GRADUATION_MARKERS: tuple[str, ...] = (
    "mezuniyet",
    "mezun",
    "diploma",
    "ilisik kesme",
    "ilisik kesilecek",
)
ROUTING_PERSONAL_MARKERS: tuple[str, ...] = (
    # İyelik ekli kişisel veri kategorileri
    "ortalamam",
    "notlarim",
    "gno",
    "transkript",
    "borcum",
    "borcun",
    "harcim",
    "odemem",
    "bursum",
    "aliyor muyum",
    "durumum",
    "mezuniyetime",
    "dersim",
    "derslerim",
    "kredim",
    "kaldi",
    "tamamladim",
    "kaydim",
    "not ortalamam",
    "stajim",
    # İyelik ekli ek kalıplar
    "kac dersim",
    "kac kredim",
    "staj durumum",
    "devamsizligim",
    "sinav sonucum",
    "notlarimi",
    "diplomami",
    "belgemi",
    "burs durumum",
    "odeme durumum",
    "kayit durumum",
    "mezuniyet durumum",
    # İyeliksiz ama kişisel veri talep kalıpları
    "not ortalama",
    "kalan ders",
    "akts durumu",
    "kredi durumu",
    "borc sorgula",
    "harc sorgula",
)
NORMALIZED_COURSE_CODE_IN_QUERY = re.compile(r"\b[a-z]{2,}\s?\d{3,4}\b", re.IGNORECASE)


def normalize_routing_text(text: str) -> str:
    """Normalize text for router keyword checks."""
    return normalize_text(text)


def contains_any(normalized_text: str, markers: tuple[str, ...]) -> bool:
    """Return whether normalized text includes any marker."""
    return any(marker in normalized_text for marker in markers)


_PERSONAL_POSSESSIVE_RE = re.compile(
    r"\b(?:not|gno|kredi|akts|ders|staj|burs|harc|borc|kayit|mezuniyet|diploma|transkript)"
    r"(?:im|in|imiz|iniz|um|un|umuz|unuz|"
    r"larim|larin|larimiz|lariniz|lerim|lerin|lerimiz|leriniz)\b",
    re.IGNORECASE,
)

_PERSONAL_QUESTION_MARKERS = (
    "kac", "nedir", "nasil", "goster", "sorgula", "ogren",
    "bilebilirmiyim", "var mi", "ne kadar",
)

# Kural/fark/karsilastirma sorulari kisisel veri talebi degildir.
# Bu kalıplar varsa looks_like_personal_data_query False donmeli.
_NON_PERSONAL_QUERY_PATTERNS = (
    "fark", "fark nedir", "arasinda fark",
    "karsilastir", "karsilastirma",
    "hangi kosullar", "kosullar neler",
    "kural", "yonerge", "yonetmelik",
    "ne zamana kadar", "sartlari neler",
    "adim adim", "surec nasil",
    "nereye", "hangi belge", "hangi belgeler",
    "nereden", "nerede", "gorebilirim", "goruntuleyebilirim",
    "hazirlamaliyim", "yatirdiktan sonra",
    "danisman", "onay sureci", "basindan sonuna",
    "tum surec", "anlatir misin",
    "girebilir miyim", "tekrar alabilir",
    # Prosedur/politika sinyalleri — kisisel veri talebi degildir
    "ne yapabilirim", "ne yapmaliyim", "ne yapmam gerekiyor",
    "ne yapacagim", "ne yapacağım",
    "nasil yapabilirim", "nasil yapmaliyim",
    "kesilir mi", "odenir mi", "oder miyim", "sayilir mi",
    "etkilenir mi", "etkiler mi", "gerekir mi",
    "yapabilir miyim", "yapabilir miydim", "basvurabilir miyim",
    "zorunda miyim", "muaf miyim",
)

_VAGUE_APPLICATION_TIMING_TOKENS = {
    "sey",
    "basvuru",
    "basvurusu",
    "ne",
    "zaman",
    "tarih",
    "tarihi",
    "son",
    "gun",
}


def looks_like_personal_data_query(query: str) -> bool:
    """Return whether query likely asks for personal/private student data."""
    lowered = normalize_routing_text(query)

    if has_pedagogical_formation_markers(lowered):
        return False

    # Kural/fark/karsilastirma sorulari kisisel veri talebi degildir.
    # Ornek: "kayit dondurma ile kayit yaptirmamak arasinda fark" → kural sorusu
    # Ornek: "mezuniyet icin gerekli kosullar" → kural sorusu
    if contains_any(lowered, _NON_PERSONAL_QUERY_PATTERNS):
        return False

    # Marker tabanli kontrol
    if contains_any(lowered, ROUTING_PERSONAL_MARKERS):
        return True
    # İyelik eki + soru kalıbı kombinasyonu
    if _PERSONAL_POSSESSIVE_RE.search(lowered):
        if any(m in lowered for m in _PERSONAL_QUESTION_MARKERS):
            return True
    return False


def looks_like_vague_application_timing_query(query: str) -> bool:
    """Return whether application timing intent lacks a concrete application domain."""
    lowered = normalize_routing_text(query)
    tokens = set(re.findall(r"[a-z0-9]+", lowered))
    if "basvuru" not in lowered:
        return False
    if not contains_any(lowered, ROUTING_TIMING_MARKERS):
        return False
    if tokens and tokens <= _VAGUE_APPLICATION_TIMING_TOKENS:
        return True
    known_context_markers = (
        ROUTING_CAP_MARKERS
        + ROUTING_REGISTRATION_MARKERS
        + ROUTING_ACADEMIC_CONTEXT_MARKERS
        + ROUTING_INTERNSHIP_MARKERS
        + ROUTING_SCHOLARSHIP_MARKERS
        + ROUTING_INTERNATIONAL_MARKERS
        + ROUTING_HORIZONTAL_TRANSFER_MARKERS
        + ROUTING_STUDENT_SERVICES_MARKERS
    )
    return not contains_any(lowered, known_context_markers)


def has_payment_registration_timing_overlap(normalized_text: str) -> bool:
    """Return whether query mixes payment and registration timing signals."""
    return (
        contains_any(normalized_text, ROUTING_PAYMENT_MARKERS)
        and contains_any(normalized_text, ROUTING_REGISTRATION_MARKERS)
        and contains_any(normalized_text, ROUTING_TIMING_MARKERS)
    )


def has_registration_process_overlap(normalized_text: str) -> bool:
    """Return whether query is clearly about a registration timing/process flow."""
    return (
        contains_any(normalized_text, ROUTING_REGISTRATION_MARKERS)
        and (
            contains_any(normalized_text, ROUTING_TIMING_MARKERS)
            or contains_any(
                normalized_text,
                ("nasil", "surec", "adim", "ne yapmaliyim", "ne yapacagim"),
            )
        )
        and not contains_any(normalized_text, ROUTING_PAYMENT_MARKERS)
    )


def has_student_services_payment_overlap(normalized_text: str) -> bool:
    """Return whether student-services flow is mixed with an explicit payment burden."""
    return has_student_services_markers(normalized_text) and contains_any(
        normalized_text,
        ROUTING_PAYMENT_MARKERS,
    )


def has_graduation_payment_overlap(normalized_text: str) -> bool:
    """Return whether graduation/clearance context is mixed with a payment burden."""
    return contains_any(normalized_text, ROUTING_GRADUATION_MARKERS) and contains_any(
        normalized_text,
        ROUTING_PAYMENT_MARKERS,
    )


def has_academic_calendar_markers(normalized_text: str) -> bool:
    """Return whether query is clearly about registration or academic calendar dates."""
    return extract_query_concepts(normalized_text).has(CONCEPT_ACADEMIC_CALENDAR) or contains_any(
        normalized_text, ROUTING_ACADEMIC_CALENDAR_MARKERS
    )


def has_payment_markers(normalized_text: str) -> bool:
    """Return whether query contains payment/fee related markers."""
    return contains_any(normalized_text, ROUTING_PAYMENT_MARKERS)


def has_cap_markers(normalized_text: str) -> bool:
    """Return whether query mentions CAP/YAP style programs."""
    concepts = extract_query_concepts(normalized_text)
    return concepts.has(CONCEPT_CAP) or bool(CAP_OR_YAP_IN_QUERY.search(normalized_text)) or contains_any(
        normalized_text, ROUTING_CAP_MARKERS
    )


def has_formal_rule_markers(normalized_text: str) -> bool:
    """Return whether query looks like a formal academic rule/policy question."""
    return contains_any(normalized_text, ROUTING_FORMAL_RULE_MARKERS)


def has_student_affairs_rule_markers(normalized_text: str) -> bool:
    """Return whether a formal rule belongs primarily to student affairs procedures."""
    concepts = extract_query_concepts(normalized_text)
    return concepts.has(CONCEPT_COMPLAINT) or contains_any(normalized_text, ROUTING_STUDENT_AFFAIRS_RULE_MARKERS)


def has_student_affairs_admin_markers(normalized_text: str) -> bool:
    """Return whether query is about administrative exam/note workflows."""
    concepts = extract_query_concepts(normalized_text)
    return concepts.has(CONCEPT_COMPLAINT) or contains_any(normalized_text, ROUTING_STUDENT_AFFAIRS_ADMIN_MARKERS)


def looks_like_grade_visibility_procedure(normalized_text: str) -> bool:
    """Return whether query asks where/how to view grades, not the grades themselves."""
    return contains_any(normalized_text, ROUTING_GRADE_VISIBILITY_MARKERS) and contains_any(
        normalized_text,
        ROUTING_PROCEDURAL_VISIBILITY_MARKERS,
    )


def has_pedagogical_formation_markers(normalized_text: str) -> bool:
    """Return whether query is about pedagogical formation program rules."""
    return contains_any(normalized_text, ROUTING_PEDAGOGICAL_FORMATION_MARKERS)


def has_horizontal_transfer_markers(normalized_text: str) -> bool:
    """Return whether query mentions horizontal transfer processes."""
    if has_cap_markers(normalized_text) and _has_negated_marker(
        normalized_text, ROUTING_HORIZONTAL_TRANSFER_MARKERS
    ):
        return False
    return extract_query_concepts(normalized_text).has(CONCEPT_HORIZONTAL_TRANSFER) or contains_any(
        normalized_text, ROUTING_HORIZONTAL_TRANSFER_MARKERS
    )


def _has_negated_marker(normalized_text: str, markers: tuple[str, ...]) -> bool:
    for marker in markers:
        match = re.search(
            rf"(?<!\w){re.escape(marker)}[a-z]*(?!\w)",
            normalized_text,
            re.IGNORECASE,
        )
        if not match:
            continue
        following = normalized_text[match.end() : match.end() + 48]
        if any(
            re.search(rf"(?<!\w){re.escape(word)}(?!\w)", following)
            for word in _ROUTING_NEGATION_WORDS
        ):
            return True
    return False


def has_max_duration_markers(normalized_text: str) -> bool:
    """Return whether query mentions maximum program duration / extra time rules."""
    return contains_any(normalized_text, ROUTING_MAX_DURATION_MARKERS)


def has_international_markers(normalized_text: str) -> bool:
    """Return whether query is about international or Erasmus processes."""
    return extract_query_concepts(normalized_text).has(CONCEPT_INTERNATIONAL) or contains_any(
        normalized_text, ROUTING_INTERNATIONAL_MARKERS
    )


def has_student_document_markers(normalized_text: str) -> bool:
    """Return whether query is clearly about transcript or student document retrieval."""
    concepts = extract_query_concepts(normalized_text)
    if concepts.has(CONCEPT_STUDENT_DOCUMENT) or contains_any(normalized_text, ROUTING_STUDENT_DOCUMENT_MARKERS):
        return True
    if has_international_markers(normalized_text):
        return False
    return "belge" in normalized_text and any(
        marker in normalized_text for marker in ("ogrenci", "transkript", "diploma")
    )


def has_student_document_request_markers(normalized_text: str) -> bool:
    """Return whether query explicitly asks how/where to obtain a student document."""
    return contains_any(normalized_text, ROUTING_STUDENT_DOCUMENT_REQUEST_MARKERS)


def has_student_services_markers(normalized_text: str) -> bool:
    """Return whether query is clearly about password/reset/freeze/withdrawal student services."""
    return extract_query_concepts(normalized_text).has(CONCEPT_STUDENT_SERVICES) or contains_any(
        normalized_text, ROUTING_STUDENT_SERVICES_MARKERS
    )


def has_scholarship_markers(normalized_text: str) -> bool:
    """Return whether query is about scholarship-like topics."""
    return extract_query_concepts(normalized_text).has(CONCEPT_SCHOLARSHIP) or contains_any(
        normalized_text, ROUTING_SCHOLARSHIP_MARKERS
    )


def has_announcement_markers(normalized_text: str) -> bool:
    """Return whether query asks for announcements / duyuru."""
    concepts = extract_query_concepts(normalized_text)
    return (
        concepts.has(CONCEPT_ANNOUNCEMENT)
        and CAPABILITY_ANNOUNCEMENT not in concepts.blocked_primary_capabilities
    ) or contains_any(normalized_text, ROUTING_ANNOUNCEMENT_MARKERS)


def has_internship_markers(normalized_text: str) -> bool:
    """Return whether query is clearly about internship-like procedures."""
    return extract_query_concepts(normalized_text).has(CONCEPT_INTERNSHIP) or contains_any(
        normalized_text, ROUTING_INTERNSHIP_MARKERS
    )


def has_summer_school_markers(normalized_text: str) -> bool:
    """Return whether query is about summer school (yaz okulu) procedures."""
    return extract_query_concepts(normalized_text).has(CONCEPT_YAZ_OKULU) or contains_any(
        normalized_text, ROUTING_SUMMER_SCHOOL_MARKERS
    )


def has_akts_markers(normalized_text: str) -> bool:
    """Return whether query is about AKTS/ECTS/kredi topics."""
    return extract_query_concepts(normalized_text).has(CONCEPT_AKTS) or contains_any(
        normalized_text, ROUTING_AKTS_MARKERS
    )


def has_akts_registration_markers(normalized_text: str) -> bool:
    """Return whether query is specifically about AKTS/kredi/GANO registration limits.

    Unlike has_akts_markers, this excludes generic 'akts' mentions that could
    be curriculum-related (e.g. 'bu ders kac akts?').
    """
    return contains_any(normalized_text, ROUTING_AKTS_REGISTRATION_MARKERS)


def has_single_exam_markers(normalized_text: str) -> bool:
    """Return whether query is about tek ders sinavi."""
    return extract_query_concepts(normalized_text).has(CONCEPT_SINGLE_EXAM) or contains_any(
        normalized_text, ROUTING_SINGLE_EXAM_MARKERS
    )


def has_makeup_exam_markers(normalized_text: str) -> bool:
    """Return whether query is about butunleme/ek sinav/mazeret."""
    return extract_query_concepts(normalized_text).has(CONCEPT_MAKEUP_EXAM) or contains_any(
        normalized_text, ROUTING_MAKEUP_EXAM_MARKERS
    )


def has_identity_card_markers(normalized_text: str) -> bool:
    """Return whether query is about ogrenci kimlik karti."""
    return extract_query_concepts(normalized_text).has(CONCEPT_IDENTITY_CARD) or contains_any(
        normalized_text, ROUTING_IDENTITY_CARD_MARKERS
    )


def has_general_akts_markers(normalized_text: str) -> bool:
    """Return whether query asks for a program-level AKTS graduation rule."""
    return ("akts" in normalized_text or "ects" in normalized_text) and contains_any(
        normalized_text,
        ROUTING_GENERAL_AKTS_MARKERS,
    )


def looks_like_personal_credit_progress_query(normalized_text: str) -> bool:
    """Return whether query asks about a student's own AKTS/kredi progress."""
    return "tamamladim" in normalized_text and (
        "akts" in normalized_text
        or "kredim" in normalized_text
        or "kredilerim" in normalized_text
    )


def should_skip_llm_for_academic_context_query(
    query: str,
    departments: list[Department],
) -> bool:
    """Return whether the query is already clearly academic-context bound."""
    if Department.ACADEMIC_PROGRAMS not in departments:
        return False
    lowered = normalize_routing_text(query)
    return bool(NORMALIZED_COURSE_CODE_IN_QUERY.search(lowered)) or contains_any(
        lowered,
        ROUTING_ACADEMIC_CONTEXT_MARKERS,
    )


def detect_task_type(query: str, departments: list[Department]) -> TaskType | None:
    """Infer a coarse task type from the query and routed departments."""
    normalized_query = normalize_routing_text(query)

    if Department.FINANCE in departments:
        if any(keyword in normalized_query for keyword in ("burs", "hibe", "scholarship")):
            return TaskType.SCHOLARSHIP_QUERY
        if any(keyword in normalized_query for keyword in ("odeme", "harc", "dekont", "taksit", "ucret")):
            return TaskType.TUITION_QUERY
        return TaskType.PAYMENT_QUERY

    if (CAP_OR_YAP_IN_QUERY.search(normalized_query) or contains_any(normalized_query, ROUTING_CAP_MARKERS)) and Department.STUDENT_AFFAIRS in departments:
        if contains_any(normalized_query, ROUTING_TIMING_MARKERS):
            return TaskType.PROCEDURE_QUERY
        return TaskType.COURSE_QUERY

    if Department.STUDENT_AFFAIRS in departments:
        if has_internship_markers(normalized_query):
            return TaskType.PROCEDURE_QUERY
        if has_student_affairs_admin_markers(normalized_query) or looks_like_grade_visibility_procedure(normalized_query):
            return TaskType.REGISTRATION_QUERY
        if has_academic_calendar_markers(normalized_query):
            return TaskType.REGISTRATION_QUERY
        if any(keyword in normalized_query for keyword in ("kayit", "kayd", "yatay", "dikey", "muafiyet", "intibak", "takvim")):
            return TaskType.REGISTRATION_QUERY
        if has_student_services_markers(normalized_query):
            return TaskType.REGISTRATION_QUERY
        if has_general_akts_markers(normalized_query):
            return TaskType.ACADEMIC_QUERY
        if any(
            keyword in normalized_query
            for keyword in (
                "not",
                "gno",
                "transkript",
                "mezuniyet",
                "diploma",
                "bagil",
                "butunleme",
                "devamsizlik",
                "devam zorunlulugu",
                "devam kosulu",
                "ders tekrari",
                "yaz okulu",
                "akts",
                "kredi",
                "kredim",
                "kredilerim",
                "tamamladim",
            )
        ):
            return TaskType.ACADEMIC_QUERY
        return TaskType.COURSE_QUERY

    if Department.ACADEMIC_PROGRAMS in departments:
        if any(
            keyword in normalized_query
            for keyword in (
                "yonerge",
                "yonetmelik",
                "politika",
                "prosedur",
                "genelge",
                "azami",
                "butunleme",
                "devam zorunlulugu",
                "not sistemi",
                "erasmus",
                "uluslararasi",
                "ikamet",
                "denklik",
                "tomer",
                "yos",
            )
        ):
            return TaskType.PROCEDURE_QUERY
        return TaskType.COURSE_QUERY

    return None
