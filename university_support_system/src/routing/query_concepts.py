"""Central query concept extraction for routing and orchestration policies."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from src.core.query_markers import ACADEMIC_DEPARTMENT_CONTEXT_MARKERS
from src.core.text_normalization import normalize_text


CONCEPT_ACADEMIC_CALENDAR = "academic_calendar"
CONCEPT_ANNOUNCEMENT = "announcement"
CONCEPT_APPLICATION = "application"
CONCEPT_ACADEMIC_PROGRAMS = "academic_programs"
CONCEPT_CAP = "cap"
CONCEPT_COMPLAINT = "complaint"
CONCEPT_COURSE_CODE = "course_code"
CONCEPT_COURSE_SCHEDULE = "course_schedule"
CONCEPT_EVENT = "event"
CONCEPT_EXEMPTION = "exemption"
CONCEPT_FEE = "fee"
CONCEPT_GRADUATION = "graduation"
CONCEPT_HORIZONTAL_TRANSFER = "horizontal_transfer"
CONCEPT_INTERNATIONAL = "international"
CONCEPT_INTERNSHIP = "internship"
CONCEPT_PERSONAL_DATA = "personal_data"
CONCEPT_REGISTRATION = "registration"
CONCEPT_SCHOLARSHIP = "scholarship"
CONCEPT_STUDENT_DOCUMENT = "student_document"
CONCEPT_STUDENT_SERVICES = "student_services"
CONCEPT_TIMING = "timing"
CONCEPT_YAZ_OKULU = "summer_school"
CONCEPT_AKTS = "akts"
CONCEPT_SINGLE_EXAM = "single_exam"
CONCEPT_MAKEUP_EXAM = "makeup_exam"
CONCEPT_IDENTITY_CARD = "identity_card"

CAPABILITY_ANNOUNCEMENT = "announcement"
CAPABILITY_EVENT = "event"

DOMAIN_STUDENT_AFFAIRS_ADMIN = "student_affairs_admin"
DOMAIN_STUDENT_AFFAIRS_PROCEDURE = "student_affairs_procedure"
DOMAIN_ACADEMIC_CALENDAR = "academic_calendar"
DOMAIN_FINANCE = "finance"
DOMAIN_ACADEMIC_PROGRAMS = "academic_programs"

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_COURSE_CODE_RE = re.compile(r"\b[a-z]{2,}\s?\d{3,4}\b", re.IGNORECASE)


def _n(value: str) -> str:
    return normalize_text(value)


def _markers(*values: str) -> tuple[str, ...]:
    return tuple(_n(value) for value in values)


_CONCEPT_MARKERS: dict[str, tuple[str, ...]] = {
    CONCEPT_ANNOUNCEMENT: _markers(
        "duyuru",
        "duyurular",
        "duyurusu",
        "haber",
        "haberler",
        "ilan",
        "ilanlar",
        "link",
        "guncel duyuru",
        "guncel duyur",
        "son duyuru",
        "son duyur",
        "son aciklanan",
        "yayimlandi",
        "yayinlandi",
    ),
    CONCEPT_EVENT: _markers(
        "etkinlik",
        "seminer",
        "konferans",
        "soylesi",
        "panel",
        "workshop",
        "atolye",
        "fuar",
        "sergi",
        "zirve",
        "kariyer gunu",
        "kariyer gunleri",
        "konser",
        "hackathon",
    ),
    CONCEPT_APPLICATION: _markers(
        "basvuru",
        "basvurusu",
        "basvurular",
        "basvurmak",
        "basvurabil",
        "muracaat",
    ),
    CONCEPT_TIMING: _markers(
        "ne zaman",
        "zaman",
        "takvim",
        "tarih",
        "surec",
        "son gun",
        "son tarih",
        "acildi mi",
        "basladi mi",
        "bitti mi",
        "kapandi mi",
        "ne kadar surer",
    ),
    CONCEPT_FEE: _markers(
        "ucret",
        "harc",
        "odeme",
        "taksit",
        "dekont",
        "katki payi",
        "borc",
        "borclu",
        "ogrenim ucreti",
        "iade",
    ),
    CONCEPT_REGISTRATION: _markers(
        "kayit",
        "kayd",
        "kayit yenileme",
        "ders kaydi",
        "ders secimi",
        "ders ekleme",
        "ders birakma",
    ),
    CONCEPT_ACADEMIC_CALENDAR: _markers(
        "akademik takvim",
        "kayit donemi",
        "ders kaydi takvimi",
        "derslerin baslamasi",
        "derslerin bitimi",
        "ders bitimi",
        "ders bitis",
        "ders bitis tarihi",
        "son ders tarihi",
        "dersler ne zaman basliyor",
        "dersler ne zaman bitiyor",
        "final sinavlari",
        "final sinavlarinin",
        "butunleme sinavlari",
        "butunleme sinavlarinin",
        "ara sinavlari",
        "sinav takvimi",
        "sinav tarihleri",
        "not giris",
        "notlarin giril",
        "girilmesinin son gunu",
    ),
    CONCEPT_HORIZONTAL_TRANSFER: _markers(
        "yatay gecis",
        "kurum ici yatay",
        "kurumlar arasi yatay",
        "ek madde",
    ),
    CONCEPT_EXEMPTION: _markers(
        "muafiyet",
        "muaf",
        "intibak",
        "ders saydir",
        "ders saydirma",
    ),
    CONCEPT_INTERNSHIP: _markers(
        "staj",
        "zorunlu staj",
        "staj formu",
        "staj defteri",
        "staj sigorta",
        "mup",
        "mesleki uygulama",
        "sanayi uygulamasi",
        "bitirme projesi",
    ),
    CONCEPT_COMPLAINT: _markers(
        "sikayet",
        "hocami sikayet",
        "hocam sikayet",
        "ogretim elemani",
        "akademik personel",
        "etik",
        "dilekce vermek istiyorum",
        "tutanak",
    ),
    CONCEPT_STUDENT_DOCUMENT: _markers(
        "transkript",
        "ogrenci belgesi",
        "ogrenci kimlik",
        "ogrenci kimligi",
        "ogrenci kart",
        "ogrenci karti",
        "kimlik kart",
        "kimlik karti",
        "kimligim kayip",
        "kimligimi kaybettim",
        "kartim kayip",
        "kartimi kaybettim",
        "diploma eki",
        "not dokumu",
    ),
    CONCEPT_STUDENT_SERVICES: _markers(
        "ubys",
        "obs",
        "sifre",
        "parola",
        "kayit dondurma",
        "donem dondurma",
        "ilisik kesme",
        "kayit sildirme",
        "kaydimi sil",
        "universiteyi birak",
        "okulu birak",
    ),
    CONCEPT_CAP: _markers(
        "cap",
        "capa",
        "cift anadal",
        "cift ana dal",
        "yandal",
        "yan dal",
        "ikinci lisans",
    ),
    CONCEPT_SCHOLARSHIP: _markers(
        "burs",
        "hibe",
        "scholarship",
        "yemek bursu",
        "kismi zamanli",
    ),
    CONCEPT_INTERNATIONAL: _markers(
        "erasmus",
        "uluslararasi",
        "yabanci",
        "yabanci ogrenci",
        "ikamet",
        "denklik",
        "tomer",
        "yos",
        "exchange",
        "mevlana",
        "farabi",
        "degisim programi",
    ),
    CONCEPT_GRADUATION: _markers(
        "mezun",
        "mezuniyet",
        "diploma",
        "gno",
        "ilisik kesme",
    ),
    CONCEPT_YAZ_OKULU: _markers("yaz okulu", "yaz okuluna", "yaz okulundan", "yaz donemi", "yaz ogretimi", "misafir ogrenci"),
    CONCEPT_COURSE_SCHEDULE: _markers("ders programi", "haftalik ders programi"),
    CONCEPT_AKTS: _markers(
        "akts", "ects", "kredim", "akts hesap",
        "donem akts", "toplam akts", "mezuniyet akts",
        "akts hakki", "kredi hakki", "kredi siniri",
        "donem yuku", "ders yuku", "maximum akts",
        "azami akts", "azami kredi",
    ),
    CONCEPT_SINGLE_EXAM: _markers(
        "tek ders sinavi", "tek ders", "tek sinav",
    ),
    CONCEPT_MAKEUP_EXAM: _markers(
        "butunleme", "butunleme sinavi", "ek sinav",
        "ek sinav hakki", "mazeret sinavi", "mazeret",
    ),
    CONCEPT_IDENTITY_CARD: _markers(
        "kimlik karti", "ogrenci kimligi", "ogrenci kimlik",
        "kimlik kaybi", "kimlik yenileme", "kimlik basvuru",
    ),
}

_PERSONAL_MARKERS = _markers(
    "ortalamam",
    "notlarim",
    "not ortalamam",
    "borcum",
    "harcim",
    "bursum",
    "derslerim",
    "kredim",
    "tamamladim",
    "kaydim",
    "stajim",
)

_PROCEDURAL_CONCEPTS = {
    CONCEPT_APPLICATION,
    CONCEPT_CAP,
    CONCEPT_COMPLAINT,
    CONCEPT_EXEMPTION,
    CONCEPT_HORIZONTAL_TRANSFER,
    CONCEPT_INTERNSHIP,
    CONCEPT_REGISTRATION,
    CONCEPT_STUDENT_DOCUMENT,
    CONCEPT_STUDENT_SERVICES,
    CONCEPT_YAZ_OKULU,
    CONCEPT_SINGLE_EXAM,
    CONCEPT_MAKEUP_EXAM,
    CONCEPT_IDENTITY_CARD,
}


@dataclass(frozen=True)
class QueryConceptProfile:
    """Normalized semantic signals used by router/orchestrator policies."""

    normalized_query: str
    tokens: frozenset[str]
    concepts: frozenset[str]
    explicit_capabilities: frozenset[str]
    blocked_primary_capabilities: frozenset[str]
    domain_guard: str | None = None

    def has(self, concept: str) -> bool:
        return concept in self.concepts

    def has_any(self, concepts: Iterable[str]) -> bool:
        return any(concept in self.concepts for concept in concepts)


def extract_query_concepts(query: object | None) -> QueryConceptProfile:
    """Extract coarse, reusable concepts from a user query.

    This is intentionally conservative: it is not a Turkish NLP stemmer, but a
    domain synonym layer that catches common suffix/phrase variants before the
    LLM and deterministic guardrails disagree.
    """
    normalized = normalize_text(query)
    tokens = frozenset(_TOKEN_RE.findall(normalized))
    concepts: set[str] = set()

    for concept, markers in _CONCEPT_MARKERS.items():
        if any(marker in normalized for marker in markers):
            concepts.add(concept)

    if _COURSE_CODE_RE.search(normalized):
        concepts.add(CONCEPT_COURSE_CODE)

    if any(normalize_text(marker) in normalized for marker in ACADEMIC_DEPARTMENT_CONTEXT_MARKERS):
        concepts.add(CONCEPT_ACADEMIC_PROGRAMS)

    if any(marker in normalized for marker in _PERSONAL_MARKERS):
        concepts.add(CONCEPT_PERSONAL_DATA)

    explicit_capabilities: set[str] = set()
    if CONCEPT_ANNOUNCEMENT in concepts:
        explicit_capabilities.add(CAPABILITY_ANNOUNCEMENT)
    if CONCEPT_EVENT in concepts:
        explicit_capabilities.add(CAPABILITY_EVENT)

    blocked_primary_capabilities: set[str] = set()
    if _should_block_primary_announcement(concepts):
        blocked_primary_capabilities.add(CAPABILITY_ANNOUNCEMENT)

    return QueryConceptProfile(
        normalized_query=normalized,
        tokens=tokens,
        concepts=frozenset(concepts),
        explicit_capabilities=frozenset(explicit_capabilities),
        blocked_primary_capabilities=frozenset(blocked_primary_capabilities),
        domain_guard=_infer_domain_guard(concepts),
    )


def _should_block_primary_announcement(concepts: set[str]) -> bool:
    if CONCEPT_ANNOUNCEMENT in concepts:
        return False
    if CONCEPT_ACADEMIC_CALENDAR in concepts:
        return True
    if concepts & _PROCEDURAL_CONCEPTS and (
        CONCEPT_TIMING in concepts
        or CONCEPT_APPLICATION in concepts
        or CONCEPT_COURSE_SCHEDULE in concepts
    ):
        return True
    if CONCEPT_COMPLAINT in concepts or CONCEPT_STUDENT_DOCUMENT in concepts:
        return True
    return False


def _infer_domain_guard(concepts: set[str]) -> str | None:
    if CONCEPT_COMPLAINT in concepts:
        return DOMAIN_STUDENT_AFFAIRS_ADMIN
    if CONCEPT_ACADEMIC_CALENDAR in concepts:
        return DOMAIN_ACADEMIC_CALENDAR
    if concepts & {
        CONCEPT_EXEMPTION,
        CONCEPT_HORIZONTAL_TRANSFER,
        CONCEPT_INTERNSHIP,
        CONCEPT_REGISTRATION,
        CONCEPT_STUDENT_DOCUMENT,
        CONCEPT_STUDENT_SERVICES,
    }:
        return DOMAIN_STUDENT_AFFAIRS_PROCEDURE
    if CONCEPT_FEE in concepts:
        return DOMAIN_FINANCE
    if concepts & {CONCEPT_CAP, CONCEPT_INTERNATIONAL, CONCEPT_COURSE_CODE, CONCEPT_COURSE_SCHEDULE}:
        return DOMAIN_ACADEMIC_PROGRAMS
    return None
