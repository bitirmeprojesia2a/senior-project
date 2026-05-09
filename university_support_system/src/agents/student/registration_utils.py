"""Helpers for student affairs registration agent."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from collections.abc import Sequence

from src.core.text_normalization import iter_alias_matches_longest_first, normalize_text

REGISTRATION_TIMING_KEYWORDS: tuple[str, ...] = (
    "ne zaman",
    "tarih",
    "donem",
    "dönem",
    "takvim",
    "baslangic",
    "başlangıç",
    "bitis",
    "bitiş",
    "acik mi",
    "açık mı",
    "aktif",
    "son gun",
    "son tarih",
    "son basvuru",
    "kayit donemi",
)
EXPLICIT_REGISTRATION_TIMING_KEYWORDS: tuple[str, ...] = (
    "ne zaman",
    "tarih",
    "takvim",
    "baslangic",
    "bitis",
    "acik mi",
    "aktif",
    "son gun",
    "son tarih",
    "son basvuru",
)

REGISTRATION_TOPIC_MARKERS: dict[str, tuple[str, ...]] = {
    "cap": ("cap", "cift anadal", "cift ana dal", "ikinci lisans"),
    "yandal": ("yandal", "yan dal"),
    "yatay": ("yatay gecis", "yatay", "kurum ici yatay"),
    "dikey": ("dikey gecis", "dikey", "dgs"),
    "muafiyet": ("muafiyet", "intibak"),
    "dondurma": ("kayit dondurma", "donem dondurma", "donem izni", "dondur"),
    "silme": (
        "kayit sildirme",
        "kayit silme",
        "kaydimi sil",
        "kaydini sil",
        "kaydi sil",
        "ilisik kesme",
        "ilisigin kesil",
        "iliskesme",
        "ayrilma",
        "ayrilmak",
        "ayril",
        "birakma",
        "birakmak",
        "birak",
    ),
    "staj": ("staj", "zorunlu staj", "mustahaklik", "provizyon"),
}

REGISTRATION_QUERY_ASPECTS: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "document",
        ("belge", "evrak", "form", "dokuman"),
        ("belge", "evrak", "form", "dokuman", "nufus", "mustahaklik", "provizyon"),
    ),
    (
        "timing",
        ("ne zaman", "tarih", "takvim", "son basvuru", "son tarih", "donem"),
        ("ne zaman", "tarih", "takvim", "son basvuru", "son tarih", "baslangic", "bitis"),
    ),
    (
        "condition",
        ("kosul", "kosullari", "sart", "sartlari", "gerekli", "gerekiyor", "kriter"),
        ("kosul", "sart", "gerekli", "gerekir", "kriter", "ortalama", "yuzde", "basari", "kabul"),
    ),
    (
        "quota",
        ("kontenjan",),
        ("kontenjan",),
    ),
    (
        "fee",
        ("ucret", "harc", "odeme"),
        ("ucret", "harc", "odeme", "katki payi"),
    ),
    (
        "process",
        ("nasil", "surec", "basvuru", "basvurusu", "adim", "islem", "dikkat"),
        ("nasil", "surec", "basvuru", "elektronik", "online", "link", "adim", "islem"),
    ),
)

REGISTRATION_PROCESS_SYNTHESIS_MARKERS: tuple[str, ...] = (
    "tum islem",
    "tum surec",
    "adim adim",
    "sureci",
    "surec",
    "nasil yapacagim",
    "nasil yapilir",
    "ne yapmaliyim",
    "dikkat et",
    "donuste",
)

_UNRELATED_STUDENT_COMMUNITY_MARKERS: tuple[str, ...] = (
    "ogrenci topluluk",
    "topluluk yonergesi",
    "uyelik",
    "uyeligi",
    "sksdb",
    "etkinlik kurulu",
    "genel kurul toplantisi",
)

_STUDENT_COMMUNITY_QUERY_MARKERS: tuple[str, ...] = (
    "ogrenci toplulug",
    "ogrenci topluluk",
    "topluluga",
    "topluluktan",
    "kulup",
    "sksdb",
    "etkinlik kurulu",
    "uyelik",
    "uye olmak",
    "uyelikten",
)

_STUDENT_RECORD_TERMINATION_MARKERS: tuple[str, ...] = (
    "kayit sildir",
    "kayit sil",
    "kaydi sil",
    "kaydini sil",
    "kaydimi sil",
    "universite ile ilisig",
    "universitemiz ile ilisig",
    "yuksekogretim kurumundan cikar",
)

_FAQ_SOURCE_MARKERS: tuple[str, ...] = ("sss", "faq", "sik sorulan")

_COURSE_REGISTRATION_QUERY_MARKERS: tuple[str, ...] = (
    "ders kayd",
    "ders sec",
    "kayit yenile",
)

_COURSE_REGISTRATION_PROCESS_MARKERS: tuple[str, ...] = (
    "nasil",
    "surec",
    "adim",
    "basindan sonuna",
    "danisman",
    "onay",
    "yatirdiktan sonra",
    "ilk kez",
)

_COURSE_REGISTRATION_CONTENT_MARKERS: tuple[str, ...] = (
    "ubys.omu.edu.tr",
    "ogrenci bilgi sistemi",
    "ogrenci bilgi yonetim sistemi",
    "ders secimi",
    "ders kaydi",
    "kayit yenileme",
    "danisman onayi",
    "danisman onay",
    "sinif yoklama listesi",
    "yoklama listesi",
    "akademik takvim",
)

_LEAVE_RETURN_QUERY_MARKERS: tuple[str, ...] = (
    "dondur",
    "donem izni",
    "ara verdikten",
    "donuste",
    "geri don",
)

_LEAVE_RETURN_CONTENT_MARKERS: tuple[str, ...] = (
    "kayit dondurma suresinin bitiminde",
    "ayrildigi donemin",
    "ayrildigi yilin",
    "kaldigi yerden devam",
    "ogrenimine kaldigi yerden devam",
)

_GRADE_OBJECTION_QUERY_MARKERS: tuple[str, ...] = (
    "sinav notuma itiraz",
    "sinav sonucuna itiraz",
    "sinav sonuclarina itiraz",
    "notuma itiraz",
    "itiraz etmek istiyorum",
)

_GRADE_OBJECTION_CONTENT_MARKERS: tuple[str, ...] = (
    "bes is gunu",
    "bolum baskanligina",
    "bolum baskanina",
    "dilekce",
    "ilgili birime",
    "ilgili birim",
    "ogrenci otomasyon sistemine girilmesinin son gununden itibaren",
    "sinav sonuclarina nasil itiraz edebilirim",
    "sinav kagitlarinin yeniden incelenmesi",
)
_GRADE_OBJECTION_NEGATIVE_SOURCE_MARKERS: tuple[str, ...] = (
    "staj_",
    "_staj",
    "staj_ilkeleri",
    "staj_yonergesi",
    "staj_esas",
    "konukevi",
    "konsey",
    "topluluk",
    "kulup",
    "muafiyet",
    "intibak",
    "yuzde_on",
)

_GRADE_ENTRY_QUERY_MARKERS: tuple[str, ...] = (
    "notlarimi sisteme girmemis",
    "notlarim sisteme girmemis",
    "notum sisteme girmemis",
    "notlarimi sisteme girilmemis",
    "notum sisteme girilmemis",
    "hocam not girmemis",
    "hocam benim ders notlarimi sisteme girmemis",
)

_GRADE_ENTRY_CONTENT_MARKERS: tuple[str, ...] = (
    "oidb@omu.edu.tr",
    "bolum baskanina",
    "dekan/mudurunuze",
    "otomasyon sistemine teknik destek",
    "not bildirim",
    "not duzeltme",
)
_GRADE_ENTRY_NEGATIVE_SOURCE_MARKERS: tuple[str, ...] = (
    "staj_",
    "_staj",
    "staj_ilkeleri",
    "staj_yonergesi",
    "staj_esas",
    "konukevi",
    "konsey",
    "topluluk",
    "kulup",
    "muafiyet",
    "intibak",
)

_WITHDRAWAL_QUERY_MARKERS: tuple[str, ...] = (
    "universiteyi birak",
    "universiteden ayril",
    "ayrilmak istiyorum",
    "birakip ayril",
    "kayit sildirme",
    "kaydi sildirme",
    "kaydimi sildirme",
    "ilisik kesme",
)

_WITHDRAWAL_CONTENT_MARKERS: tuple[str, ...] = (
    "ubys uzerinden talepte bulunarak ilisik kesme sureci baslat",
    "ilisik kesme talebinde bulun",
    "ilisik kesme formu",
    "kayit sildirme formu",
    "dilekce",
    "ogrenci isleri",
    "ilgili birim",
    "universite ile ilisigi kesilir",
    "tekrar kaydolamaz",
    "ogrencilik hakkiniz sona erer",
    "yazili istegi uzerine kaydi silinir",
)
_WITHDRAWAL_NEGATIVE_SOURCE_MARKERS: tuple[str, ...] = (
    "kimlik_karti",
    "konukevi",
    "topluluk",
    "kulup",
    "staj",
    "isyeri",
    "yaz_okulu",
)

_DISCIPLINE_QUERY_MARKERS: tuple[str, ...] = (
    "kopya",
    "disiplin",
    "disiplin sureci",
    "disiplin cezasi",
    "sikayet",
    "hocami sikayet",
    "hocam sikayet",
    "ogretim elemani",
    "akademik personel",
    "etik",
    "dilekce",
)

_DISCIPLINE_CONTENT_MARKERS: tuple[str, ...] = (
    "yuksekogretim kurumlari ogrenci disiplin yonetmeligi",
    "disiplin sucu",
    "kopya muamelesi",
    "kopya cekmek",
    "kopya verme",
    "sinav gorevlisi",
    "cep telefonu ile herhangi bir sekilde ilgilenen",
)

_DISCIPLINE_NEGATIVE_SOURCE_MARKERS: tuple[str, ...] = (
    "staj",
    "isyeri",
    "mesleki_uygulama",
    "konukevi",
)

_MUAFIYET_QUERY_MARKERS: tuple[str, ...] = (
    "muafiyet",
    "intibak",
)

_MUAFIYET_CONTENT_MARKERS: tuple[str, ...] = (
    "uc hafta",
    "3 hafta",
    "dilekce",
    "muafiyet komisyonu",
    "intibak komisyonu",
    "yonetim kurulu",
    "karar cikana kadar",
    "derslere devam",
)

_SINGLE_EXAM_QUERY_MARKERS: tuple[str, ...] = (
    "tek ders",
    "tek ders sinavi",
    "tek derse",
)

_SINGLE_EXAM_CONTENT_MARKERS: tuple[str, ...] = (
    "mufredatinizda tanimli butun dersleri almis",
    "daha once devam sartini sagladiginiz tek ders",
    "tek ders sinavina girebilirsiniz",
    "butunleme sinavlarini takip eden",
    "en az cc",
)

_SINGLE_EXAM_NEGATIVE_SOURCE_MARKERS: tuple[str, ...] = (
    "dis hekimligi",
    "doktorluk",
    "tip fakultesi",
    "uluslararasi ogrenci",
    "pedagojik formasyon",
)

_SUMMER_SCHOOL_QUERY_MARKERS: tuple[str, ...] = (
    "yaz okulu",
    "yaz okuluna",
    "yaz okulundan",
    "yaz donemi",
)

_SUMMER_SCHOOL_CONTENT_MARKERS: tuple[str, ...] = (
    "yaz okulunda derslere devam zorunludur",
    "omu ve/veya diger universite",
    "yaz okulunda ders alabilir",
    "dersin acilabilmesi",
    "en az 35 egitim",
    "yaz okulu sonu sinavi",
)

_SUMMER_SCHOOL_NEGATIVE_SOURCE_MARKERS: tuple[str, ...] = (
    "yabanci dil",
    "pedagojik formasyon",
    "egitim ogretim politikasi",
)

_COURSE_DELAY_QUERY_MARKERS: tuple[str, ...] = (
    "okulum uzuyor",
    "okul uzuyor",
    "donem uzuyor",
    "donemim uzuyor",
    "ders yuzunden",
    "dersimden kaldim",
    "dersten kaldim",
    "basarisiz oldugum",
    "basarisiz oldum",
    "hic almadigim",
    "alt donem ders",
    "eksik ders",
    "mezun olamiyorum",
    "uzatma",
    "nasil cozebilirim",
    "ne yapabilirim",
)

_COURSE_DELAY_CONTENT_MARKERS: tuple[str, ...] = (
    "eksik ders alarak donem uzatmamak",
    "mufredat durum kontrolu",
    "transkriptinizle karsilastirmaniz",
    "oncelikle basarisiz oldugunuz",
    "hic almadigi alt donem",
    "tum dersleri almak ve basarmak zorundadir",
    "basarisiz oldugunuz ders/dersler",
    "devam kosulu yerine getirilmis",
    # Solution-oriented markers
    "tek ders sinavi",
    "yaz okulu",
    "butunleme sinavi",
    "butunleme hakki",
    "ek sinav",
    "azami ogrenim suresi",
    "azami sure",
    "ek sure",
    "donem uzatma",
    "mezuniyet sinavi",
)

_COURSE_DELAY_NEGATIVE_SOURCE_MARKERS: tuple[str, ...] = (
    "yks",
    "taban puan",
    "dis hekimligi",
    "tip fakultesi",
    "uzaktan egitim",
    "pedagojik formasyon",
    "uluslararasi ogrenci",
    # Prerequisite content is not a solution source
    "on_kosul",
    "prerequisite",
    "on kosullu ders",
    "on kosul",
)

@dataclass(frozen=True)
class RegistrationProfilePolicy:
    query_markers: tuple[str, ...]
    content_markers: tuple[str, ...]
    negative_source_markers: tuple[str, ...] = ()
    prefer_faq_sources: bool = False
    preferred_top_k: int | None = None


_REGISTRATION_PROFILE_POLICIES: dict[str, RegistrationProfilePolicy] = {
    "grade_objection": RegistrationProfilePolicy(
        query_markers=_GRADE_OBJECTION_QUERY_MARKERS,
        content_markers=_GRADE_OBJECTION_CONTENT_MARKERS,
        negative_source_markers=_GRADE_OBJECTION_NEGATIVE_SOURCE_MARKERS,
        prefer_faq_sources=True,
        preferred_top_k=10,
    ),
    "grade_entry": RegistrationProfilePolicy(
        query_markers=_GRADE_ENTRY_QUERY_MARKERS,
        content_markers=_GRADE_ENTRY_CONTENT_MARKERS,
        negative_source_markers=_GRADE_ENTRY_NEGATIVE_SOURCE_MARKERS,
        prefer_faq_sources=True,
        preferred_top_k=10,
    ),
    "withdrawal": RegistrationProfilePolicy(
        query_markers=_WITHDRAWAL_QUERY_MARKERS,
        content_markers=_WITHDRAWAL_CONTENT_MARKERS,
        negative_source_markers=_WITHDRAWAL_NEGATIVE_SOURCE_MARKERS,
        preferred_top_k=12,
    ),
    "discipline": RegistrationProfilePolicy(
        query_markers=_DISCIPLINE_QUERY_MARKERS,
        content_markers=_DISCIPLINE_CONTENT_MARKERS,
        negative_source_markers=_DISCIPLINE_NEGATIVE_SOURCE_MARKERS,
        preferred_top_k=10,
    ),
    "muafiyet": RegistrationProfilePolicy(
        query_markers=_MUAFIYET_QUERY_MARKERS,
        content_markers=_MUAFIYET_CONTENT_MARKERS,
        prefer_faq_sources=True,
        preferred_top_k=12,
    ),
    "single_exam": RegistrationProfilePolicy(
        query_markers=_SINGLE_EXAM_QUERY_MARKERS,
        content_markers=_SINGLE_EXAM_CONTENT_MARKERS,
        negative_source_markers=_SINGLE_EXAM_NEGATIVE_SOURCE_MARKERS,
        prefer_faq_sources=True,
        preferred_top_k=12,
    ),
    "summer_school": RegistrationProfilePolicy(
        query_markers=_SUMMER_SCHOOL_QUERY_MARKERS,
        content_markers=_SUMMER_SCHOOL_CONTENT_MARKERS,
        negative_source_markers=_SUMMER_SCHOOL_NEGATIVE_SOURCE_MARKERS,
        preferred_top_k=12,
    ),
    "course_delay": RegistrationProfilePolicy(
        query_markers=_COURSE_DELAY_QUERY_MARKERS,
        content_markers=_COURSE_DELAY_CONTENT_MARKERS,
        negative_source_markers=_COURSE_DELAY_NEGATIVE_SOURCE_MARKERS,
        prefer_faq_sources=True,
        preferred_top_k=12,
    ),
}

_REGISTRATION_QUERY_PROFILES: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = tuple(
    (name, policy.query_markers, policy.content_markers)
    for name, policy in _REGISTRATION_PROFILE_POLICIES.items()
)

_COURSE_REGISTRATION_PROCESS_TOP_K = 6
_SKIP_ENRICHMENT_PROFILES: frozenset[str] = frozenset({
    "grade_objection",
    "grade_entry",
    "withdrawal",
})

_COURSE_REGISTRATION_MARKER_WEIGHTS: dict[str, int] = {
    "ubys.omu.edu.tr": 10,
    "ogrenci bilgi sistemi": 8,
    "ogrenci bilgi yonetim sistemi": 8,
    "sinif yoklama listesi": 4,
    "yoklama listesi": 4,
    "danisman onayi": 3,
    "danisman onay": 3,
    "ders secimi": 3,
    "akademik takvim": 3,
    "kayit yenileme": 3,
    "kayit dondurma suresinin bitiminde": 6,
    "ayrildigi donemin": 5,
    "ayrildigi yilin": 5,
    "kaldigi yerden devam": 5,
    "ogrenimine kaldigi yerden devam": 5,
}


def normalize_registration_text(text: str) -> str:
    return normalize_text(text)


def is_course_registration_process_query(query_text: str) -> bool:
    lowered = normalize_registration_text(query_text)
    has_course_registration = any(marker in lowered for marker in _COURSE_REGISTRATION_QUERY_MARKERS)
    has_process_signal = any(marker in lowered for marker in _COURSE_REGISTRATION_PROCESS_MARKERS)
    return has_course_registration and has_process_signal


def should_skip_registration_result_enrichment(query_text: str) -> bool:
    """Skip neighbor expansion for compact FAQ-style registration procedures."""
    lowered = normalize_registration_text(query_text)
    if is_course_registration_process_query(lowered):
        return True
    return detect_registration_query_profile(lowered) in _SKIP_ENRICHMENT_PROFILES


_VT_EXCLUDE_TOPICS: tuple[str, ...] = (
    "kayit dondurma",
    "donem dondurma",
    "kayit sildirme",
    "ilisik kesme",
    "muafiyet",
    "intibak",
    "yatay",
    "dikey",
    "cap",
    "cift anadal",
    "yan dal",
    "staj",
    "mezuniyet",
    "burs",
    "harc",
    "ucret",
    "katki payi",
    "ek sure",
    "devamsizlik",
    "butunleme",
    "sinav",
    "ders secimi",
    "ders ekleme",
    "ders birakma",
)

_PROCESS_NOT_TIMING: tuple[str, ...] = (
    "nasil yapilir",
    "nasil yapacagim",
    "nasil isliyor",
    "sureci nasil",
    "adim adim",
    "ne yapmaliyim",
    "danismanin onayi",
    "danismanin onay",
    "danisman onay",
    "onay sureci",
    "basindan sonuna",
    "tum surec",
)

_REGISTRATION_CONTEXT: tuple[str, ...] = (
    "kayit",
    "ders kaydi",
)

_REGISTRATION_PAYMENT_MARKERS: tuple[str, ...] = (
    "ucret",
    "harc",
    "katki payi",
    "odeme",
)

_ACADEMIC_CALENDAR_PDF = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "raw"
    / "student_affairs"
    / "takvimler"
    / "2025_2026_genel_akademik_takvim.pdf"
)


def _extract_pdf_text(path: Path) -> str:
    try:
        import pdfplumber
    except ImportError:
        return ""

    try:
        with pdfplumber.open(str(path)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        return ""


def _extract_calendar_row(label: str) -> tuple[str, str] | None:
    text = _extract_pdf_text(_ACADEMIC_CALENDAR_PDF)
    if not text:
        return None
    normalized_label = normalize_registration_text(label)
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if normalized_label not in normalize_registration_text(line):
            continue
        matches = re.findall(
            r"\d{2}(?:-\d{2})?\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{4}",
            line,
        )
        if len(matches) >= 2:
            return matches[0], matches[1]
    return None


_COURSE_START_CALENDAR_MARKERS: tuple[str, ...] = (
    "derslerin baslamasi",
    "dersler ne zaman basliyor",
    "dersler ne zaman baslar",
    "ders baslangic",
    "derslerin baslangic",
    "donem baslangic",
    "yariyil baslangic",
)
_COURSE_END_CALENDAR_MARKERS: tuple[str, ...] = (
    "derslerin bitimi",
    "ders bitimi",
    "ders bitis",
    "ders bitis tarihi",
    "son ders tarihi",
    "son ders gunu",
    "derslerin sonu",
    "dersler ne zaman bitiyor",
    "dersler ne zaman biter",
    "ders sonu",
    "donem sonu",
    "yariyil sonu",
)


def _requested_academic_calendar_term(lowered_query: str) -> str | None:
    if "bahar" in lowered_query:
        return "spring"
    if "guz" in lowered_query:
        return "fall"
    return None


def _format_academic_calendar_row_answer(
    *,
    row_label: str,
    display_label: str,
    lowered_query: str,
) -> tuple[str, dict] | None:
    row = _extract_calendar_row(row_label)
    if row is None:
        return None
    fall, spring = row
    term = _requested_academic_calendar_term(lowered_query)
    metadata = {
        "source": str(_ACADEMIC_CALENDAR_PDF),
        "label": row_label,
        "fall": fall,
        "spring": spring,
    }
    if term == "spring":
        return (
            f"Genel akademik takvime gore bahar doneminde {display_label} "
            f"{spring} tarihidir.",
            metadata,
        )
    if term == "fall":
        return (
            f"Genel akademik takvime gore guz doneminde {display_label} "
            f"{fall} tarihidir.",
            metadata,
        )
    return (
        f"Genel akademik takvime gore {display_label} guz donemi icin {fall}, "
        f"bahar donemi icin {spring} tarihidir.",
        metadata,
    )


def _build_course_calendar_answer(lowered_query: str) -> tuple[str, dict] | None:
    if any(marker in lowered_query for marker in _COURSE_END_CALENDAR_MARKERS):
        return _format_academic_calendar_row_answer(
            row_label="Derslerin Bitimi",
            display_label="derslerin bitimi",
            lowered_query=lowered_query,
        )
    if any(marker in lowered_query for marker in _COURSE_START_CALENDAR_MARKERS):
        return _format_academic_calendar_row_answer(
            row_label="Derslerin Baslamasi",
            display_label="derslerin baslamasi",
            lowered_query=lowered_query,
        )
    return None


def build_general_exam_calendar_answer(query_text: str) -> tuple[str, dict] | None:
    """Return structured academic calendar dates for broad calendar date queries."""
    lowered = normalize_registration_text(query_text)

    course_calendar_answer = _build_course_calendar_answer(lowered)
    if course_calendar_answer is not None:
        return course_calendar_answer

    wants_date = any(marker in lowered for marker in ("ne zaman", "tarih", "takvim"))
    if not wants_date:
        return None

    # "program" icerse bile takvim sinyali guclu ise devam et
    # (ornegin: "bilgisayar muhendisligi bahar doneminde final sinav tarihi")
    if "program" in lowered and not any(
        marker in lowered
        for marker in (
            "final sinav", "yariyil sonu sinav", "donem sonu sinav",
            "butunleme sinav", "ara sinav", "akademik takvim",
            "sinav takvim", "sinav tarih",
        )
    ):
        return None

    if "final sinav" in lowered or "yariyil sonu sinav" in lowered or "donem sonu sinav" in lowered:
        if any(marker in lowered for marker in ("sonuc", "giril", "not giris", "son gun")):
            row = _extract_calendar_row("Yariyil Sonu Sinav Sonuclarinin Internetten Girilmesinin Son Gunu")
            if row is None:
                return None
            fall, spring = row
            return (
                "Genel akademik takvime gore yariyil sonu/final sinav sonuclarinin "
                f"internetten girilmesinin son gunu guz donemi icin {fall}, "
                f"bahar donemi icin {spring} tarihidir.",
                {
                    "source": str(_ACADEMIC_CALENDAR_PDF),
                    "label": "Yariyil Sonu Sinav Sonuclarinin Internetten Girilmesinin Son Gunu",
                    "fall": fall,
                    "spring": spring,
                },
            )
        row = _extract_calendar_row("Yariyil Sonu Sinavlari")
        if row is None:
            return None
        fall, spring = row
        return (
            "Genel akademik takvime gore yariyil sonu/final sinavlari "
            f"guz donemi icin {fall}, bahar donemi icin {spring} tarihlerindedir.",
            {
                "source": str(_ACADEMIC_CALENDAR_PDF),
                "label": "Yariyil Sonu Sinavlari",
                "fall": fall,
                "spring": spring,
            },
        )

    if "butunleme sinav" in lowered:
        row = _extract_calendar_row("Butunleme Sinavlari")
        if row is None:
            return None
        fall, spring = row
        return (
            "Genel akademik takvime gore butunleme sinavlari "
            f"guz donemi icin {fall}, bahar donemi icin {spring} tarihlerindedir.",
            {
                "source": str(_ACADEMIC_CALENDAR_PDF),
                "label": "Butunleme Sinavlari",
                "fall": fall,
                "spring": spring,
            },
        )

    return None


def is_registration_timing_query(query_text: str) -> bool:
    lowered = normalize_registration_text(query_text)

    has_registration_context = any(kw in lowered for kw in _REGISTRATION_CONTEXT)
    has_payment_marker = any(kw in lowered for kw in _REGISTRATION_PAYMENT_MARKERS)
    has_timing = any(
        normalize_registration_text(kw) in lowered
        for kw in REGISTRATION_TIMING_KEYWORDS
    )
    has_explicit_timing = any(
        normalize_registration_text(kw) in lowered
        for kw in EXPLICIT_REGISTRATION_TIMING_KEYWORDS
    )

    if any(kw in lowered for kw in _PROCESS_NOT_TIMING):
        return False

    if any(
        kw in lowered
        for kw in (
            "kayit dondurma",
            "donem dondurma",
            "kayit sildirme",
            "ilisik kesme",
        )
    ):
        return False

    if has_registration_context and has_payment_marker and has_explicit_timing:
        return True

    if any(kw in lowered for kw in _VT_EXCLUDE_TOPICS):
        return False

    if "kayit donemi" in lowered:
        return True

    if not has_timing:
        return False

    return has_registration_context


def should_force_registration_llm_synthesis(
    query_text: str,
    results: Sequence[dict],
) -> bool:
    if not results:
        return False
    lowered = normalize_registration_text(query_text)
    profile = detect_registration_query_profile(lowered)
    if profile in {"discipline", "summer_school", "single_exam", "course_delay"}:
        return True
    if is_course_registration_process_query(query_text):
        return True
    if any(marker in lowered for marker in REGISTRATION_PROCESS_SYNTHESIS_MARKERS):
        return any(
            marker in lowered
            for topic_markers in REGISTRATION_TOPIC_MARKERS.values()
            for marker in topic_markers
        )
    if (
        any(marker in lowered for marker in ("muafiyet", "intibak"))
        and any(marker in lowered for marker in ("ne zaman", "tarih", "sure", "son tarih"))
        and any(marker in lowered for marker in ("devam", "karar cikana kadar"))
    ):
        return True
    return False


def preferred_registration_search_top_k(query_text: str) -> int | None:
    lowered = normalize_registration_text(query_text)
    if is_course_registration_process_query(query_text):
        return _COURSE_REGISTRATION_PROCESS_TOP_K
    profile = detect_registration_query_profile(lowered)
    profile_policy = get_registration_profile_policy(profile)
    if profile_policy and profile_policy.preferred_top_k is not None:
        return profile_policy.preferred_top_k
    if any(marker in lowered for marker in ("muafiyet", "intibak")):
        return _REGISTRATION_PROFILE_POLICIES["muafiyet"].preferred_top_k
    return None


def build_registration_intro(query_text: str) -> str:
    lowered = normalize_registration_text(query_text)
    if "cap" in lowered or "cift anadal" in lowered:
        return "CAP basvurusu icin en ilgili kaynakta su bilgi yer aliyor:"
    if "yandal" in lowered or "yan dal" in lowered:
        return "Yandal basvurusu icin en ilgili kaynakta su bilgi yer aliyor:"
    if "yatay" in lowered:
        return "Yatay gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:"
    if "dikey" in lowered:
        return "Dikey gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:"
    return "En ilgili ogrenci isleri kaynaginda su bilgi yer aliyor:"


def pick_preferred_registration_result(query_text: str, results: Sequence[dict]) -> dict | None:
    if not results:
        return None

    normalized_query = normalize_registration_text(query_text)
    expected_topic_key, expected_markers = infer_registration_query_topic(normalized_query)
    expected_aspect = detect_registration_query_aspect(normalized_query)

    ranked = sorted(
        results,
        key=lambda item: (
            0 if matches_registration_topic(item, expected_markers) else 1,
            1 if has_conflicting_registration_topic(item, expected_topic_key) else 0,
            1 if is_unrelated_registration_source(item, expected_topic_key) else 0,
            0 if matches_registration_aspect(item, expected_aspect) else 1,
            1 if should_penalize_registration_qa(item, expected_aspect) else 0,
            -float(item.get("score", 0.0)),
        ),
    )
    return dict(ranked[0])


def filter_registration_answer_results(query_text: str, results: Sequence[dict]) -> list[dict]:
    normalized_query = normalize_registration_text(query_text)
    profile = detect_registration_query_profile(normalized_query)
    profile_policy = get_registration_profile_policy(profile)
    filtered = [
        item
        for item in results
        if not should_reject_registration_source_only_result(query_text, item)
    ]
    if profile_policy and profile_policy.negative_source_markers:
        profile_filtered = [
            item for item in filtered if not is_negative_registration_profile_source(item, profile)
        ]
        if profile_filtered:
            filtered = profile_filtered
        elif profile == "discipline":
            return []
    if profile_policy is not None:
        profile_marker_filtered = [
            item for item in filtered
            if registration_profile_marker_count(item, query_text=query_text) > 0
        ]
        if profile_marker_filtered:
            filtered = profile_marker_filtered
        elif profile == "discipline":
            return []
    return filtered or list(results)


def detect_registration_query_profile(normalized_query: str) -> str | None:
    alias_groups = (
        (profile, policy.query_markers)
        for profile, policy in _REGISTRATION_PROFILE_POLICIES.items()
    )
    for profile, marker in iter_alias_matches_longest_first(alias_groups):
        if marker in normalized_query:
            return profile
    return None


def get_registration_profile_policy(profile: str | None) -> RegistrationProfilePolicy | None:
    if profile is None:
        return None
    return _REGISTRATION_PROFILE_POLICIES.get(profile)


def registration_profile_marker_count(
    item: dict,
    *,
    query_text: str,
) -> int:
    normalized_query = normalize_registration_text(query_text)
    profile = detect_registration_query_profile(normalized_query)
    profile_policy = get_registration_profile_policy(profile)
    if profile_policy is None:
        return 0
    content_markers = profile_policy.content_markers
    source = normalize_registration_text(item.get("source", ""))
    metadata = normalize_registration_text((item.get("metadata") or {}).get("file_name", ""))
    content = normalize_registration_text(item.get("content", "")[:1200])
    haystack = f"{source} {metadata} {content}"
    score = sum(1 for marker in content_markers if marker in haystack)
    if profile_policy.prefer_faq_sources and is_faq_registration_source(item):
        score += 2
    return score


def is_negative_registration_profile_source(item: dict, profile: str | None) -> bool:
    profile_policy = get_registration_profile_policy(profile)
    if profile_policy is None or not profile_policy.negative_source_markers:
        return False
    source = normalize_registration_text(item.get("source", ""))
    metadata = normalize_registration_text((item.get("metadata") or {}).get("file_name", ""))
    content = normalize_registration_text(item.get("content", "")[:400])
    haystack = f"{source} {metadata} {content}"
    return any(marker in haystack for marker in profile_policy.negative_source_markers)


def rank_registration_results(
    results: Sequence[dict],
    *,
    query_text: str,
) -> list[dict]:
    normalized_query = normalize_registration_text(query_text)
    profile = detect_registration_query_profile(normalized_query)
    profile_policy = get_registration_profile_policy(profile)
    return sorted(
        (dict(item) for item in results),
        key=lambda item: (
            1 if is_negative_registration_profile_source(item, profile) else 0,
            -registration_profile_marker_count(item, query_text=query_text),
            0 if profile_policy and profile_policy.prefer_faq_sources and is_faq_registration_source(item) else 1,
            -float(item.get("score", 0.0)),
        ),
    )


def rank_course_registration_process_results(
    results: Sequence[dict],
    *,
    query_text: str | None = None,
) -> list[dict]:
    ranked = sorted(
        (compact_course_registration_process_result(item) for item in results),
        key=lambda item: (
            1 if is_likely_unrelated_registration_process_source(item) else 0,
            -course_registration_process_marker_count(item, query_text=query_text),
            0 if is_faq_registration_source(item) else 1,
            -float(item.get("score", 0.0)),
        ),
    )
    return ranked


def course_registration_process_marker_count(
    item: dict,
    *,
    query_text: str | None = None,
) -> int:
    source = normalize_registration_text(item.get("source", ""))
    metadata = normalize_registration_text((item.get("metadata") or {}).get("file_name", ""))
    content = normalize_registration_text(item.get("content", ""))
    haystack = f"{source} {metadata} {content}"
    score = 0
    for marker in _COURSE_REGISTRATION_CONTENT_MARKERS:
        if marker in haystack:
            score += _COURSE_REGISTRATION_MARKER_WEIGHTS.get(marker, 1)
    normalized_query = normalize_registration_text(query_text or "")
    if any(marker in normalized_query for marker in _LEAVE_RETURN_QUERY_MARKERS):
        for marker in _LEAVE_RETURN_CONTENT_MARKERS:
            if marker in haystack:
                score += _COURSE_REGISTRATION_MARKER_WEIGHTS.get(marker, 1)
    return score


def compact_course_registration_process_result(item: dict) -> dict:
    result = dict(item)
    content = str(result.get("content", ""))
    if len(content) < 500:
        return result

    parts = re.split(r"(?<=[\.\?])\s+", content)
    kept: list[str] = []
    for part in parts:
        normalized = normalize_registration_text(part)
        if any(
            marker in normalized
            for marker in (*_COURSE_REGISTRATION_CONTENT_MARKERS, *_LEAVE_RETURN_CONTENT_MARKERS)
        ):
            kept.append(part.strip())

    if kept:
        result["content"] = " ".join(kept)
    return result


def is_faq_registration_source(item: dict) -> bool:
    source = normalize_registration_text(item.get("source", ""))
    metadata = normalize_registration_text((item.get("metadata") or {}).get("file_name", ""))
    return any(marker in source or marker in metadata for marker in _FAQ_SOURCE_MARKERS)


def is_likely_unrelated_registration_process_source(item: dict) -> bool:
    source = normalize_registration_text(item.get("source", ""))
    content = normalize_registration_text(item.get("content", "")[:500])
    if "document.pdf" in source:
        return True
    return False


def matches_registration_topic(item: dict, expected_markers: tuple[str, ...]) -> bool:
    if not expected_markers:
        return True
    source = normalize_registration_text(item.get("source", ""))
    content = normalize_registration_text(item.get("content", "")[:600])
    return any(marker in source or marker in content for marker in expected_markers)


def has_conflicting_registration_topic(item: dict, expected_topic_key: str | None) -> bool:
    if not expected_topic_key:
        return False

    source = normalize_registration_text(item.get("source", ""))
    content = normalize_registration_text(item.get("content", "")[:600])
    matched_topics = {
        topic_key
        for topic_key, topic_markers in REGISTRATION_TOPIC_MARKERS.items()
        if any(marker in source or marker in content for marker in topic_markers)
    }

    matched_topics.discard(expected_topic_key)
    if expected_topic_key == "dondurma":
        matched_topics.discard("silme")
    if expected_topic_key == "silme":
        matched_topics.discard("dondurma")
    return bool(matched_topics)


def is_unrelated_registration_source(item: dict, expected_topic_key: str | None) -> bool:
    if expected_topic_key not in {"silme", "dondurma"}:
        return False
    source = normalize_registration_text(item.get("source", ""))
    metadata = normalize_registration_text((item.get("metadata") or {}).get("file_name", ""))
    content = normalize_registration_text(item.get("content", "")[:1200])
    haystack = f"{source} {metadata} {content}"
    if not any(marker in haystack for marker in _UNRELATED_STUDENT_COMMUNITY_MARKERS):
        if expected_topic_key == "silme" and any(marker in haystack for marker in _WITHDRAWAL_NEGATIVE_SOURCE_MARKERS):
            return True
        return False
    # Ogrenci toplulugu/uyelik yonergeleri akademik kayit silme veya
    # kayit dondurma surecinin kaynagi degildir; yalnizca soru acikca
    # topluluk/uyelik hakkindaysa kullanilmalidir.
    return True


def detect_registration_query_aspect(normalized_query: str) -> str | None:
    for aspect, query_markers, _content_markers in REGISTRATION_QUERY_ASPECTS:
        for _aspect, marker in iter_alias_matches_longest_first(((aspect, query_markers),)):
            if marker in normalized_query:
                return aspect
    return None


def infer_registration_query_topic(normalized_query: str) -> tuple[str | None, tuple[str, ...]]:
    """Infer registration topic using the longest matching query marker."""
    topic_aliases = {
        topic_key: (*topic_markers, topic_key)
        for topic_key, topic_markers in REGISTRATION_TOPIC_MARKERS.items()
    }
    for topic_key, marker in iter_alias_matches_longest_first(topic_aliases.items()):
        if marker in normalized_query:
            return topic_key, REGISTRATION_TOPIC_MARKERS[topic_key]
    return None, ()


def matches_registration_aspect(item: dict, expected_aspect: str | None) -> bool:
    if not expected_aspect:
        return True

    aspect_markers = next(
        (
            content_markers
            for aspect, _query_markers, content_markers in REGISTRATION_QUERY_ASPECTS
            if aspect == expected_aspect
        ),
        (),
    )
    if not aspect_markers:
        return True

    source = normalize_registration_text(item.get("source", ""))
    content = normalize_registration_text(item.get("content", "")[:900])
    return any(marker in source or marker in content for marker in aspect_markers)


def should_penalize_registration_qa(item: dict, expected_aspect: str | None) -> bool:
    if expected_aspect not in {"document", "timing", "condition", "quota"}:
        return False

    source = normalize_registration_text(item.get("source", ""))
    metadata = normalize_registration_text((item.get("metadata") or {}).get("file_name", ""))
    content = str(item.get("content", "")[:240])
    normalized_content = normalize_registration_text(content)

    if any(marker in source or marker in metadata for marker in _FAQ_SOURCE_MARKERS):
        return True

    return (
        "?" in content
        and any(marker in normalized_content for marker in ("ogrencisiyim", "miyim", "miyiz", "zorunda miyim"))
    )


def should_reject_registration_source_only_result(query_text: str, item: dict) -> bool:
    normalized_query = normalize_registration_text(query_text)
    profile = detect_registration_query_profile(normalized_query)
    profile_marker_score = registration_profile_marker_count(item, query_text=query_text)
    query_is_student_community = any(
        marker in normalized_query
        for marker in _STUDENT_COMMUNITY_QUERY_MARKERS
    )
    if not query_is_student_community:
        source = normalize_registration_text(item.get("source", ""))
        metadata = normalize_registration_text((item.get("metadata") or {}).get("file_name", ""))
        content = normalize_registration_text(item.get("content", "")[:1200])
        haystack = f"{source} {metadata} {content}"
        if any(marker in haystack for marker in _UNRELATED_STUDENT_COMMUNITY_MARKERS):
            return True

    expected_topic_key, _expected_markers = infer_registration_query_topic(normalized_query)
    if not query_is_student_community and is_unrelated_registration_source(item, expected_topic_key):
        return True
    if profile in {"grade_objection", "grade_entry", "discipline", "withdrawal"}:
        return is_negative_registration_profile_source(item, profile)
    if profile == "muafiyet" and profile_marker_score > 0:
        return False
    expected_aspect = detect_registration_query_aspect(normalized_query)
    if expected_aspect not in {"document", "timing", "condition", "quota"}:
        return False
    if not matches_registration_aspect(item, expected_aspect):
        return True
    return should_penalize_registration_qa(item, expected_aspect)
