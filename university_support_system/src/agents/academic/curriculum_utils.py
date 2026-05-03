"""Utility helpers for curriculum and course-list handling."""

from __future__ import annotations

import re
from typing import Any

from src.core.text_normalization import iter_alias_matches_longest_first, normalize_text

EXTRA_COURSE_LIST_KEYWORDS = (
    "dersleri neler",
    "dersleri nelerdir",
    "donem dersleri",
    "yariyil dersleri",
)

COURSE_LIST_KEYWORDS = (
    "acik ders", "bu donem", "hangi dersler", "ders listesi",
    "sinif dersleri", "bolum dersleri",
)
SCHEDULE_QUERY_MARKERS = (
    "ders programi",
    "haftalik program",
    "hangi saatte",
    "hangi gun",
    "derslik",
    "ne zaman",
)
SCHEDULE_DAY_MARKERS = {
    "pazartesi": "Pazartesi",
    "sali": "Sali",
    "carsamba": "Carsamba",
    "persembe": "Persembe",
    "cuma": "Cuma",
}
SCHEDULE_GROUP_MARKERS = {
    "1. sinif": {"1. SINIF", "I", "I.SINIF"},
    "2. sinif": {"2. SINIF", "II", "II.SINIF"},
    "3. sinif": {"3. SINIF", "III", "III.SINIF"},
    "4. sinif": {"4. SINIF", "IV", "IV.SINIF"},
    "ek1": {"EK1"},
    "ek2": {"EK2"},
}
PREREQUISITE_KEYWORDS = (
    "onkosul", "önkoşul", "on kosul", "ön koşul", "on sart", "ön şart",
    "onsart", "önşart",
)
COURSE_CODE_PATTERN = re.compile(r"\b[A-ZÇĞİÖŞÜ]{2,6}\s?\d{3,4}\b", re.IGNORECASE)
DEPARTMENT_CONTEXT_MARKERS = (
    "mufredat",
    "müfredat",
    "yariyil",
    "yarıyıl",
    "donem",
    "dönem",
    "secmeli",
    "seçmeli",
    "teknik secmeli",
    "alan secmeli",
    "zorunlu ders",
    "ders listesi",
    "hangi dersler",
    "ders plani",
    "ders programi",
    "ders icerigi",
    "akts gerekli",
    "kredi gerekli",
    "toplam akts",
    "toplam kredi",
    "bolum dersleri",
    "sinif dersleri",
)
DEPARTMENT_CONTEXT_MESSAGE = (
    "Bu akademik program sorusunu dogru cevaplayabilmem icin once bolum veya program bilgisini bilmem gerekiyor. "
    "Ornegin 'Bilgisayar Muhendisligi icin 1. yariyil dersleri nelerdir?' veya "
    "'Kimya bolumu teknik secmeli dersleri hangileri?' seklinde sorabilirsin. "
    "Kisisel ilerleme bilgisi istiyorsan OTP ile giris yapman yeterli; bolum bilgin oturumdan alinabilir."
)
PERSONAL_PROGRESS_MARKERS = (
    "tamamladım",
    "tamamladim",
    "kredim",
    "kredilerim",
    "aldığım akts",
    "aldigim akts",
    "akts'im",
    "aktsim",
    "kalan akts",
    "eksik akts",
    "eksik kredi",
    "kalan kredi",
)
SEMESTER_QUERY_PATTERN = re.compile(
    r"\b([1-8])\s*\.?\s*(?:yariyil|yarıyıl|donem|dönem)\b",
    re.IGNORECASE,
)
SEMESTER_WORDS = {
    "birinci": 1,
    "ilk": 1,
    "ikinci": 2,
    "ucuncu": 3,
    "dorduncu": 4,
    "besinci": 5,
    "altinci": 6,
    "yedinci": 7,
    "sekizinci": 8,
}
ELECTIVE_GROUP_TYPES = {"secmeli_grup", "teknik_secmeli", "lab_secmeli", "sosyal_secmeli"}
LANGUAGE_COURSE_CODE_PREFIXES = ("YD", "YDA", "YDF", "YDI")
LANGUAGE_COURSE_NAME_MARKERS = (
    "almanca",
    "fransizca",
    "ingilizce",
    "yabanci dil",
)
SHARED_DEPARTMENT_MARKERS = (
    "temel bilimler",
    "yabanci diller",
    "ataturk ilkeleri",
    "turk dili",
    "is sagligi",
    "muhendislik fakultesi ortak",
    "sosyal secmeli",
)
DEPARTMENT_NAME_SUFFIXES = (
    "bolumu",
    "bolum",
    "programi",
    "program",
    "anabilim dali",
    "abd",
    "lisans",
    "onlisans",
)
KNOWN_DEPARTMENT_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Bilgisayar Muhendisligi",
        ("bilgisayar muhendisligi", "bil muh", "bil-muhendislik"),
    ),
    (
        "Elektrik-Elektronik Mühendisliği",
        ("elektrik elektronik muhendisligi", "eem", "eem muhendislik"),
    ),
    (
        "İstatistik",
        ("istatistik", "ist bolumu", "ist-fen"),
    ),
    (
        "Fizik",
        ("fizik", "fizik-fen"),
    ),
    (
        "Fen Bilgisi Öğretmenliği",
        ("fen bilgisi ogretmenligi", "fen bilgisi", "mfbeb"),
    ),
    (
        "Matematik Öğretmenliği",
        ("matematik ogretmenligi", "mf matematik"),
    ),
    (
        "Müzik Öğretmenliği",
        ("muzik ogretmenligi", "guzel sanatlar muzik", "müzik öğretmenliği"),
    ),
    (
        "Resim İş Öğretmenliği",
        ("resim is ogretmenligi", "resim ogretmenligi", "guzel sanatlar resim"),
    ),
)

EXTRA_DEPARTMENT_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    # Daha ozel egitim/program adlari, "fizik" veya "matematik" gibi
    # kisa bolum adlarindan once denenmelidir.
    (
        "Biyoloji Egitimi",
        ("biyoloji egitimi", "biyoloji ogretmenligi"),
    ),
    (
        "Fen Bilgisi Egitimi",
        ("fen bilgisi egitimi", "fen bilgisi ogretmenligi", "fen bilgisi", "mfbeb"),
    ),
    (
        "Fizik Egitimi",
        ("fizik egitimi", "fizik ogretmenligi"),
    ),
    (
        "Ilkogretim Matematik Egitimi",
        (
            "ilkogretim matematik egitimi",
            "ilkogretim matematik ogretmenligi",
            "ilkmat",
        ),
    ),
    (
        "Matematik Egitimi",
        ("matematik egitimi",),
    ),
    (
        "Okul Oncesi Ogretmenligi",
        ("okul oncesi ogretmenligi", "okul oncesi"),
    ),
    (
        "Sinif Ogretmenligi",
        ("sinif ogretmenligi", "sinif egitimi"),
    ),
    (
        "Biyoloji",
        ("biyoloji",),
    ),
    (
        "Matematik",
        ("matematik",),
    ),
    (
        "Fizik",
        ("fizik", "fizik-fen"),
    ),
    (
        "Elektrik-Elektronik Muhendisligi",
        ("elektrik elektronik muhendisligi", "eem", "eem muhendislik"),
    ),
    (
        "Istatistik",
        ("istatistik", "ist bolumu", "ist-fen"),
    ),
    (
        "Muzik Ogretmenligi",
        ("muzik ogretmenligi", "guzel sanatlar muzik"),
    ),
    (
        "Resim Is Ogretmenligi",
        ("resim is ogretmenligi", "resim ogretmenligi", "guzel sanatlar resim"),
    ),
)


def is_personal_progress_query(lowered: str) -> bool:
    """Return whether query asks about personal academic progress."""
    return any(marker in lowered for marker in PERSONAL_PROGRESS_MARKERS)


def has_department_specific_content(
    core_courses: list[dict[str, Any]],
    elective_groups: dict[str, dict[str, Any]],
) -> bool:
    """Return whether department-specific course content exists."""
    if core_courses:
        return True
    return any(bucket.get("group") or bucket.get("options") for bucket in elective_groups.values())


def partition_courses_for_department(
    courses: list[dict[str, Any]],
    normalized_department: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Split course list into core, service, and elective-group buckets."""
    core_courses: list[dict[str, Any]] = []
    service_courses: list[dict[str, Any]] = []
    elective_groups: dict[str, dict[str, Any]] = {}

    for course in courses:
        course_type = normalize_text(course.get("course_type"))
        course_name = str(course.get("course_name", ""))
        course_department = normalize_text(course.get("department"))
        group_code = str(course.get("elective_group") or course.get("course_code") or "")

        is_group_placeholder = (
            course_type == "secmeli_grup"
            or (course_type == "sosyal_secmeli" and "grup" in normalize_text(course_name))
        )
        is_elective_option = (
            course_type in ELECTIVE_GROUP_TYPES
            and not is_group_placeholder
            and bool(course.get("elective_group"))
        )
        belongs_to_department = is_department_specific_match(
            normalized_department,
            course_department,
        )

        if is_group_placeholder or is_elective_option:
            target_bucket = elective_groups if belongs_to_department else None
            if target_bucket is None:
                service_courses.append(course)
                continue
            bucket = target_bucket.setdefault(group_code, {"group": None, "options": []})
            if is_group_placeholder:
                bucket["group"] = course
            else:
                bucket["options"].append(course)
            continue

        if belongs_to_department:
            core_courses.append(course)
        else:
            service_courses.append(course)

    return core_courses, service_courses, elective_groups


def split_language_choice_courses(
    courses: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Separate foreign-language alternatives from the main course list."""
    regular_courses: list[dict[str, Any]] = []
    language_courses: list[dict[str, Any]] = []

    for course in courses:
        if is_language_choice_course(course):
            language_courses.append(course)
        else:
            regular_courses.append(course)

    return regular_courses, language_courses


def is_language_choice_course(course: dict[str, Any]) -> bool:
    """Return whether a course row is a foreign-language option."""
    code = str(course.get("course_code") or "").upper().replace(" ", "")
    name = normalize_text(course.get("course_name"))
    if not code.startswith(LANGUAGE_COURSE_CODE_PREFIXES):
        return False
    return any(marker in name for marker in LANGUAGE_COURSE_NAME_MARKERS)


def is_department_specific_match(
    normalized_department: str,
    course_department: str,
) -> bool:
    """Return whether a course belongs to the requested department."""
    if not normalized_department:
        return True
    if not course_department:
        return False
    if any(marker in course_department for marker in SHARED_DEPARTMENT_MARKERS):
        return False

    canonical_requested = canonical_department_name(normalized_department)
    canonical_course = canonical_department_name(course_department)
    if not canonical_requested or not canonical_course:
        return False

    return (
        canonical_course == canonical_requested
        or canonical_course.startswith(f"{canonical_requested} ")
        or canonical_course.endswith(f" {canonical_requested}")
    )


def canonical_department_name(value: str) -> str:
    """Normalize department naming variants into a comparable form."""
    normalized = normalize_text(value)
    for suffix in DEPARTMENT_NAME_SUFFIXES:
        normalized = normalized.replace(suffix, " ")
    return " ".join(normalized.split())


def infer_department_from_query(query_text: str) -> str | None:
    """Known program adlarini soru metninden cikar."""
    normalized = normalize_text(query_text)
    for department, alias in iter_alias_matches_longest_first(
        EXTRA_DEPARTMENT_ALIASES + KNOWN_DEPARTMENT_ALIASES
    ):
        if alias in normalized:
            return department
    return None


def format_course_lines(courses: list[dict[str, Any]]) -> list[str]:
    """Format course items into bullet strings."""
    return [f"- {format_course_line(course)}" for course in sorted(courses, key=lambda item: item["course_code"])]


def format_course_line(course: dict[str, Any]) -> str:
    """Format a single course line."""
    akts = course.get("akts", course["credits"])
    return f"{course['course_code']} {course['course_name']} ({course['credits']}K / {akts} AKTS)"


def is_course_list_query(lowered: str) -> bool:
    """Return whether the query asks for a course list."""
    return any(
        keyword in lowered
        for keyword in COURSE_LIST_KEYWORDS + EXTRA_COURSE_LIST_KEYWORDS
    )


def is_schedule_query(lowered: str) -> bool:
    """Return whether the query asks about timetable/schedule details."""
    return any(keyword in lowered for keyword in SCHEDULE_QUERY_MARKERS)


def is_generic_schedule_listing_query(lowered: str) -> bool:
    """Return whether the query asks for the department timetable as a whole."""
    return any(
        marker in lowered
        for marker in ("ders programi", "haftalik program")
    )


def extract_schedule_day(lowered: str) -> str | None:
    """Extract an explicit weekday marker from the query."""
    for marker, canonical in SCHEDULE_DAY_MARKERS.items():
        if marker in lowered:
            return canonical
    return None


def extract_schedule_groups(lowered: str) -> set[str]:
    """Extract requested schedule groups such as 1. SINIF or EK1."""
    matches: set[str] = set()
    for marker, aliases in SCHEDULE_GROUP_MARKERS.items():
        if marker in lowered:
            matches.update(aliases)
    return matches


def wants_specific_schedule_lookup(lowered: str, query_text: str) -> bool:
    """Return whether a structured timetable lookup is worth attempting."""
    if COURSE_CODE_PATTERN.search(query_text):
        return True
    if extract_schedule_day(lowered):
        return True
    if extract_schedule_groups(lowered):
        return True
    if is_generic_schedule_listing_query(lowered):
        return True
    return any(marker in lowered for marker in ("hangi saatte", "hangi gun", "derslik"))


def is_prerequisite_query(lowered: str) -> bool:
    """Return whether the query asks about prerequisites."""
    return any(keyword in lowered for keyword in PREREQUISITE_KEYWORDS)


def extract_curriculum_semester(query_text: str) -> int | None:
    """Extract curriculum semester number from a query."""
    match = SEMESTER_QUERY_PATTERN.search(query_text)
    if match is not None:
        return int(match.group(1))

    normalized = normalize_text(query_text)
    semester_context_markers = ("donem", "yariyil")
    has_semester_context = any(marker in normalized for marker in semester_context_markers)
    has_course_list_context = is_course_list_query(normalized)
    if not has_semester_context and not has_course_list_context:
        return None
    for marker, semester in SEMESTER_WORDS.items():
        if marker in normalized:
            return semester
    return None


_RULE_CONTEXT_BYPASS: tuple[str, ...] = (
    "devam zorunlulugu",
    "devamsizlik",
    "basarisiz",
    "sinav",
    "degerlendirme",
    "not sistemi",
    "tekrar",
    "kural",
    "yonetmelik",
    "yonerge",
    "nasil degisir",
    "ne olur",
    "etkilenir mi",
    "sayilir mi",
    "muaf",
    "kosul",
    "sart",
)


def needs_department_context(
    lowered: str,
    query_text: str,
    student_department: str,
) -> bool:
    """Return whether curriculum questions need department/program clarification."""
    if student_department:
        return False
    if COURSE_CODE_PATTERN.search(query_text):
        return False
    if any(signal in lowered for signal in _RULE_CONTEXT_BYPASS):
        return False
    return any(marker in lowered for marker in DEPARTMENT_CONTEXT_MARKERS)
