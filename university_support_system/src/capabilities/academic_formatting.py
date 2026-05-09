"""Formatting helpers for academic capability records."""

from __future__ import annotations

from typing import Any


def records_for_prompt(records: list[dict[str, Any]], *, max_records: int) -> str:
    lines: list[str] = []
    for index, record in enumerate(records[:max_records], start=1):
        compact = _compact_record(record)
        pairs = [
            f"{key}={value}"
            for key, value in compact.items()
            if value not in (None, "", [], {})
        ]
        lines.append(f"{index}. " + " | ".join(pairs))
    return "\n".join(lines) if lines else "(kayit yok)"


def deterministic_answer_for_result(
    *,
    query: str,
    capability: str | None,
    records: list[dict[str, Any]],
    metadata: dict[str, Any],
    message: str | None,
) -> str:
    capability = capability or ""
    if capability == "finance.tuition_fee":
        if not records:
            return "Ogrenim ucreti veritabaninda bu bilgilerle eslesen kayit bulunamadi."
        record = records[0]
        student_type = record.get("student_type") or metadata.get("student_type")
        student_label = (
            "Turk ogrenci" if student_type == "domestic" else "uluslararasi ogrenci"
        )
        unit_name = record.get("unit_name") or metadata.get("unit_name") or "ilgili birim"
        annual_amount = _format_currency_tr(record.get("annual_amount"))
        semester_amount = _format_currency_tr(record.get("semester_amount"))
        source = record.get("source_document") or metadata.get("source_document")
        parts = [
            f"Ogrenim ucreti icin {student_label} / {unit_name} bilgisi veritabaninda kayitli.",
            f"Yillik ucret: {annual_amount}.",
        ]
        if record.get("semester_amount") is not None:
            parts.append(f"Donemlik ucret: {semester_amount}.")
        if source:
            parts.append(f"\n(Kaynak: {source})")
        return " ".join(parts)

    if capability == "calendar.academic_date":
        if not records:
            return "Akademik takvim veritabaninda bu tarih icin kayit bulunamadi."
        answer = str(records[0].get("answer") or "").strip()
        if answer:
            return answer
        label = records[0].get("label") or metadata.get("label") or "Ilgili tarih"
        fall = records[0].get("fall") or metadata.get("fall")
        spring = records[0].get("spring") or metadata.get("spring")
        if fall and spring:
            return f"{label}: guz donemi {fall}, bahar donemi {spring}."
        return records_for_prompt(records, max_records=1)

    if capability == "course.exists_in_program":
        program = metadata.get("program") or "program"
        course = metadata.get("course") or "ders"
        if not records:
            return (
                f"{program} mufredat veritabaninda {course} dersi icin kayit bulunamadi. "
                "Ders adi farkli yazilmis olabilir; ders kodu ile sorarsaniz daha kesin kontrol edebilirim."
            )
        first = records[0]
        code = first.get("course_code") or first.get("code") or ""
        name = first.get("course_name") or first.get("name") or course
        semester = first.get("semester") or first.get("curriculum_semester")
        semester_text = f" {semester}. yariyil icinde" if semester else ""
        return (
            f"{code} {name} dersi {program} mufredatinda{semester_text} gorunuyor."
        ).strip()

    if capability == "course.prerequisites":
        if not records:
            return "Bu ders icin on kosul kaydi bulunamadi."
        record = records[0]
        code = record.get("course_code") or metadata.get("course_code") or "Ders"
        name = record.get("course_name") or record.get("name") or ""
        akts = record.get("akts")
        prerequisites = record.get("prerequisites") or []
        title = f"{code} {name}".strip()
        suffix = f" ({akts} AKTS)" if akts else ""
        if prerequisites:
            items = "; ".join(_format_prerequisite(item) for item in prerequisites)
            return (
                f"{title}{suffix} dersinin on kosullari: {items}. "
                "On kosullu derslerden en az DD alinmis olmasi gerekir."
            )
        return f"{title}{suffix} dersi icin kayitli on kosul bulunmuyor."

    if capability == "course.detail":
        if not records:
            return "Bu ders icin mufredat veritabaninda kayit bulunamadi."
        record = records[0]
        code = record.get("course_code") or record.get("code") or metadata.get("course_code") or ""
        name = record.get("course_name") or record.get("name") or ""
        akts = record.get("akts")
        credit = record.get("credits") or record.get("credit")
        pieces = [f"{code} {name}".strip() or "Ders"]
        if credit:
            pieces.append(f"{credit} kredi")
        if akts:
            pieces.append(f"{akts} AKTS")
        if len(pieces) <= 1:
            return pieces[0]
        return " dersi ".join([pieces[0], ", ".join(pieces[1:]) + " olarak kayitli."])

    if capability == "curriculum.semester_courses":
        semester = metadata.get("semester")
        if not records:
            return f"{semester}. yariyil icin mufredat veritabaninda ders kaydi bulunamadi."
        return _format_course_list(
            records,
            heading=f"{semester}. yariyil doneminde kayitli {len(records)} ders/grup bulundu:",
        )

    if capability == "schedule.weekly_program":
        if not records:
            return "Bu filtrelerle ders programi veritabaninda kayit bulunamadi."
        return _format_schedule(records, heading="Bulunan ders programi satirlari:")

    return records_for_prompt(records, max_records=20)


def _compact_record(record: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "course_code",
        "course_name",
        "name",
        "credits",
        "credit",
        "akts",
        "semester",
        "curriculum_semester",
        "class_year",
        "day",
        "start_time",
        "end_time",
        "classroom",
        "schedule_group",
        "term",
        "prerequisites",
    ]
    return {key: record.get(key) for key in keys if key in record}


def _format_prerequisite(item: Any) -> str:
    if isinstance(item, dict):
        code = item.get("course_code") or item.get("code") or ""
        name = item.get("course_name") or item.get("name") or ""
        return f"{code} {name}".strip() or str(item)
    return str(item)


def _format_course_list(records: list[dict[str, Any]], *, heading: str) -> str:
    lines = [heading, ""]
    for record in records:
        code = record.get("course_code") or record.get("code") or ""
        name = record.get("course_name") or record.get("name") or ""
        credit = record.get("credits") or record.get("credit")
        akts = record.get("akts")
        details = []
        if credit:
            details.append(f"{credit}K")
        if akts:
            details.append(f"{akts} AKTS")
        suffix = f" ({' / '.join(details)})" if details else ""
        lines.append(f"- {code} {name}{suffix}".strip())
    return "\n".join(lines)


def _format_schedule(records: list[dict[str, Any]], *, heading: str) -> str:
    lines = [heading]
    for record in records:
        day = record.get("day") or record.get("day_name") or ""
        start = record.get("start_time") or ""
        end = record.get("end_time") or ""
        name = record.get("course_name") or record.get("name") or ""
        group = record.get("schedule_group") or ""
        room = record.get("classroom") or record.get("room") or ""
        group_text = f" | {group}" if group else ""
        room_text = f" | Derslik: {room}" if room else ""
        time_text = f"{start}-{end}" if start or end else ""
        lines.append(f"- {day} {time_text} | {name}{group_text}{room_text}".strip())
    return "\n".join(lines)


def _format_currency_tr(amount: Any) -> str:
    if amount is None:
        return "bilinmiyor"
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return str(amount)
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatted} TL"
