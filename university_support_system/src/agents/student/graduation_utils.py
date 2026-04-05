"""Helpers for graduation-focused student affairs logic."""

from __future__ import annotations

from src.core.text_normalization import normalize_text

PERSONAL_KEYWORDS: tuple[str, ...] = (
    "gno",
    "notlarim",
    "notlarım",
    "transkriptim",
    "ortalamam",
    "dersim",
    "derslerim",
    "kredim",
    "kredilerim",
    "kaldi",
    "kaldı",
    "kalan",
    "eksik",
    "mezuniyetime",
    "mezuniyetim",
    "aldığım",
    "aldigim",
    "gectigim",
    "geçtiğim",
    "tamamladım",
    "tamamladim",
)

HYBRID_KEYWORDS: tuple[str, ...] = (
    "mezun olabilir miyim",
    "yeterli mi",
    "karsilastirir",
    "sagliyor muyum",
    "sağlıyor muyum",
    "yetecek mi",
    "mezuniyet durumum",
    "ne kadar kaldi",
    "ne kadar kaldı",
    "kac ders",
    "kaç ders",
)


def is_graduation_personal_query(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    return any(keyword in lowered for keyword in PERSONAL_KEYWORDS)


def is_graduation_hybrid_query(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    return any(keyword in lowered for keyword in HYBRID_KEYWORDS)


def format_academic_snapshot(snapshot: dict) -> str:
    lines = [f"{snapshot['student_name']} icin akademik durum ozeti:"]
    if snapshot.get("gpa") is not None:
        lines.append(f"- GNO: {float(snapshot['gpa']):.2f}")
    lines.append(
        f"- Tamamlanan kredi: {snapshot.get('completed_credits', 0)} / {snapshot.get('total_credits', 0)}"
    )
    lines.append(f"- Kayit durumu: {snapshot.get('registration_status', 'bilinmiyor')}")

    recent_courses = snapshot.get("recent_courses") or []
    if recent_courses:
        lines.append("- Son ders kayitlari:")
        for course in recent_courses[:3]:
            grade = course.get("grade") or "not girilmedi"
            lines.append(
                f"  * {course['course_code']} {course['course_name']} | {course['semester']} | {grade}"
            )

    return "\n".join(lines)
