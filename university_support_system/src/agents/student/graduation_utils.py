"""Helpers for graduation-focused student affairs logic."""

from __future__ import annotations

from src.core.text_normalization import normalize_text


PROGRAM_LEVEL_RESOLVER_SCHEMA = "omu.program_level_resolver.v1"

PERSONAL_KEYWORDS: tuple[str, ...] = (
    "notlarim",
    "transkriptim",
    "ortalamam",
    "dersim",
    "derslerim",
    "kredim",
    "kredilerim",
    "kaldi",
    "kalan",
    "eksik",
    "mezuniyetime",
    "mezuniyetim",
    "aldigim",
    "gectigim",
    "tamamladim",
    "not ortalamam",
    "gno ortalamam",
    "durumum",
    "stajim",
    "bitirme projem",
)

HYBRID_KEYWORDS: tuple[str, ...] = (
    "mezun olabilir miyim",
    "karsilastirir",
    "sagliyor muyum",
    "yetecek mi",
    "mezuniyet durumum",
    "ne kadar kaldi",
    "eksigim var mi",
    "tamamladim mi",
)

GENERAL_AKTS_RULE_KEYWORDS: tuple[str, ...] = (
    "kac akts gerekir",
    "kac akts tamamlamali",
    "kac akts tamamlamalidir",
    "akts tamamlamali",
    "akts tamamlamalidir",
    "akts gerekli",
    "akts gerekir",
    "toplam akts",
    "mezun olmak icin",
    "mezuniyet icin",
    "kac kredi gerekir",
    "kredi gerekli",
    "toplam kredi",
    "mezuniyet kredisi",
)

GRADUATION_AKTS_POLICY_FACET = "graduation_akts"

ASSOCIATE_LEVEL_MARKERS: tuple[str, ...] = (
    "onlisans",
    "on lisans",
    "2 yillik",
    "iki yillik",
    "meslek yuksekokulu",
    "myo",
)

BACHELOR_LEVEL_MARKERS: tuple[str, ...] = (
    "lisans",
    "4 yillik",
    "dort yillik",
    "fakulte",
    "muhendisligi",
    "ogretmenligi",
    "egitimi",
)

SPECIAL_LONG_PROGRAM_MARKERS: tuple[str, ...] = (
    "tip",
    "dis hekimligi",
    "eczacilik",
    "veteriner",
)

ASSOCIATE_PROGRAM_MARKERS: tuple[str, ...] = (
    "myo",
    "meslek yuksekokulu",
    "meslek yuksek okulu",
    "onlisans",
    "on lisans",
    "2 yillik",
    "iki yillik",
)

BACHELOR_PROGRAM_MARKERS: tuple[str, ...] = (
    "muhendisligi",
    "ogretmenligi",
    "egitimi",
    "fakultesi",
    "lisans programi",
    "4 yillik",
    "dort yillik",
)

_GENERAL_RULE_SIGNALS: tuple[str, ...] = (
    "en az kac",
    "en fazla kac",
    "kac olmali",
    "ne kadar olmali",
    "kac olmalidir",
    "gerekir",
    "gerekli",
    "gereklidir",
    "zorunlu",
    "olmalidir",
    "yeterli mi",
    "sart",
    "kosul",
    "kural",
)

_PROCEDURAL_OVERRIDE_SIGNALS: tuple[str, ...] = (
    "nereye",
    "nerede",
    "nereden",
    "ne yapmaliyim",
    "ne yapmam gerekiyor",
    "ne yapabilirim",
    "yapabilir",
    "basvuru",
    "surec",
    "sisteme girmemis",
    "girilmemis",
    "girmemis",
    "alinir",
    "alabilirim",
    "goruntuleyebilirim",
    "goruntulerim",
    "gorebilirim",
    "gorerim",
    "hata",
    "sorun",
    "problem",
    "butunleme",
    "devamsizlik",
    "tekrar",
    "ile",
)


def _has_general_rule_signal(lowered: str) -> bool:
    return any(s in lowered for s in _GENERAL_RULE_SIGNALS)


# Negation patterns: if a personal keyword is followed by "yok", "yoktu", etc.
# the person is NOT requesting personal data — they are stating they don't have it.
# E.g. "transkriptim yok" → not personal, stating a condition.
_NEGATION_AFTER_POSSESSIVE: tuple[str, ...] = (
    "yok",
    "yoktu",
    "yoksa",
    "gelmedi",
    "alinmadi",
    "bulunmuyor",
    "eksik",
    "girilmedi",
    "girilmemis",
)


def is_graduation_personal_query(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    if _has_general_rule_signal(lowered):
        return False
    if any(s in lowered for s in _PROCEDURAL_OVERRIDE_SIGNALS):
        return False
    # "<personal_keyword> yok" → NOT a personal data request
    if any(neg in lowered for neg in _NEGATION_AFTER_POSSESSIVE):
        if any(kw in lowered for kw in PERSONAL_KEYWORDS):
            return False
    if "gno" in lowered:
        possessive = any(p in lowered for p in ("gnom", "gno'm", "ortalamam"))
        if not possessive:
            return False
        return True
    return any(keyword in lowered for keyword in PERSONAL_KEYWORDS)


def is_graduation_hybrid_query(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    if _has_general_rule_signal(lowered):
        return False
    if "kac ders" in lowered:
        if any(p in lowered for p in ("en fazla", "en cok", "maksimum", "sinir")):
            return False
    return any(keyword in lowered for keyword in HYBRID_KEYWORDS)


def is_general_akts_rule_query(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    if any(marker in lowered for marker in ("cap", "cift anadal", "cift ana dal", "yandal", "yan dal", "formasyon")):
        return False
    if "akts" not in lowered and "ects" not in lowered:
        return False
    if is_graduation_personal_query(query_text):
        return False
    return any(keyword in lowered for keyword in GENERAL_AKTS_RULE_KEYWORDS)


def is_graduation_akts_total_query(query_text: str, *, policy_facet: str | None = None) -> bool:
    """Return whether the query asks for total AKTS needed for graduation.

    This is deliberately narrower than any AKTS query. Course AKTS, semester
    load and elective credits must not be pulled into this contract.
    """
    lowered = normalize_text(query_text)
    if any(marker in lowered for marker in ("cap", "cift anadal", "cift ana dal", "yandal", "yan dal", "formasyon")):
        return False
    if normalize_text(policy_facet) == GRADUATION_AKTS_POLICY_FACET:
        if not any(marker in lowered for marker in ("dersin akts", "ders akts", "kac kredilik ders")):
            return True
    if "akts" not in lowered and "ects" not in lowered and "kredi" not in lowered:
        return False
    if any(marker in lowered for marker in ("donem icin", "donemde", "yariyil", "dersin akts", "ders akts")):
        if not any(marker in lowered for marker in ("mezun", "toplam", "bitirmek")):
            return False
    if is_graduation_personal_query(query_text):
        return False
    return any(keyword in lowered for keyword in GENERAL_AKTS_RULE_KEYWORDS) or (
        "toplam" in lowered and any(marker in lowered for marker in ("mezun", "bitirmek", "tamamlamali"))
    )


def infer_graduation_education_level(
    query_text: str,
    *,
    student_department: str | None = None,
) -> str | None:
    """Infer the education level for deterministic graduation AKTS totals."""
    resolution = resolve_program_level(
        query_text,
        student_department=student_department,
    )
    return resolution.get("education_level")


def resolve_program_level(
    query_text: str,
    *,
    student_department: str | None = None,
    student_education_level: str | None = None,
) -> dict[str, str | None]:
    """Resolve the education level behind a program/AKTS query.

    This deliberately uses program-level rules instead of program-specific
    patches.  The caller can rely on normal engineering/teaching bachelor
    programs resolving to ``bachelor`` while long professional programs stay
    outside the deterministic 240-AKTS rule.
    """
    verified_level = normalize_text(student_education_level or "")
    if verified_level in {"associate", "onlisans", "on lisans"}:
        return _program_level_payload("associate", "verified_student_profile")
    if verified_level in {"bachelor", "lisans"}:
        return _program_level_payload("bachelor", "verified_student_profile")
    if verified_level in {"special_long", "long_professional"}:
        return _program_level_payload("special_long", "verified_student_profile")

    text = " ".join(part for part in (query_text, student_department or "") if part)
    lowered = normalize_text(text)

    if any(marker in lowered for marker in SPECIAL_LONG_PROGRAM_MARKERS):
        return _program_level_payload("special_long", "program_name_heuristic")
    if any(marker in lowered for marker in ASSOCIATE_LEVEL_MARKERS + ASSOCIATE_PROGRAM_MARKERS):
        return _program_level_payload("associate", "program_name_heuristic")
    if any(marker in lowered for marker in BACHELOR_LEVEL_MARKERS + BACHELOR_PROGRAM_MARKERS):
        return _program_level_payload("bachelor", "program_name_heuristic")

    try:
        from src.agents.academic.curriculum_utils import infer_department_from_query
    except Exception:
        canonical_program = None
    else:
        canonical_program = infer_department_from_query(text)
    canonical_text = normalize_text(canonical_program or "")
    if canonical_text:
        if any(marker in canonical_text for marker in SPECIAL_LONG_PROGRAM_MARKERS):
            return _program_level_payload("special_long", "canonical_program_alias")
        if any(marker in canonical_text for marker in ASSOCIATE_PROGRAM_MARKERS):
            return _program_level_payload("associate", "canonical_program_alias")
        if any(marker in canonical_text for marker in BACHELOR_PROGRAM_MARKERS):
            return _program_level_payload("bachelor", "canonical_program_alias")

    return _program_level_payload(None, "unresolved")


def _program_level_payload(level: str | None, reason: str) -> dict[str, str | None]:
    return {
        "schema": PROGRAM_LEVEL_RESOLVER_SCHEMA,
        "education_level": level,
        "reason": reason,
    }


def format_academic_snapshot(snapshot: dict) -> str:
    lines = [f"{snapshot['student_name']} icin akademik ozet:"]
    if snapshot.get("gpa") is not None:
        lines.append(f"- GNO: {float(snapshot['gpa']):.2f}")
    lines.append(
        f"- Tamamlanan kredi: {snapshot.get('completed_credits', 0)} / {snapshot.get('total_credits', 0)}"
    )
    lines.append(f"- Kayit durumu: {snapshot.get('registration_status', 'bilinmiyor')}")

    recent_courses = snapshot.get("recent_courses") or []
    recent_limit = snapshot.get("recent_course_limit")
    if recent_courses:
        if recent_limit:
            lines.append(
                f"- Not: Bu ozet tam transkript yerine gecmez; son {recent_limit} ders kaydini gosterir."
            )
        else:
            lines.append("- Not: Bu ozet tam transkript yerine gecmez.")

    if recent_courses:
        lines.append("- Son ders kayitlari:")
        for course in recent_courses[:3]:
            grade = course.get("grade") or "not girilmedi"
            lines.append(
                f"  * {course['course_code']} {course['course_name']} | {course['semester']} | {grade}"
            )

    return "\n".join(lines)
