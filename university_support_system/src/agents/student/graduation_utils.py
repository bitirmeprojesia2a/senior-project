"""Helpers for graduation-focused student affairs logic."""

from __future__ import annotations

from src.core.text_normalization import normalize_text

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
    if "akts" not in lowered and "ects" not in lowered:
        return False
    if is_graduation_personal_query(query_text):
        return False
    return any(keyword in lowered for keyword in GENERAL_AKTS_RULE_KEYWORDS)


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
