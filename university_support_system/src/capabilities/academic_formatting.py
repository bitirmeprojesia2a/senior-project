"""Formatting helpers for academic capability records."""

from __future__ import annotations

from typing import Any

from src.db.schedule_data import (
    format_schedule_course_name,
    format_schedule_day,
    format_schedule_group,
    format_schedule_label,
    schedule_group_sort_key,
)


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
        semester = record.get("curriculum_semester") or record.get("semester")
        class_year = _class_year_from_semester(semester)
        prerequisites = record.get("prerequisites") or []
        pieces = [f"{code} {name}".strip() or "Ders"]
        if credit:
            pieces.append(f"{credit} kredi")
        if akts:
            pieces.append(f"{akts} AKTS")
        if semester:
            semester_text = f"{semester}. yariyil"
            if class_year:
                semester_text += f" ({class_year}. sinif)"
            pieces.append(semester_text)
        if prerequisites:
            items = "; ".join(_format_prerequisite(item) for item in prerequisites)
            pieces.append(f"on kosul: {items}")
        elif "onkosul" in str(metadata.get("query") or "").lower():
            pieces.append("kayitli on kosul yok")
        if len(pieces) <= 1:
            return pieces[0]
        return f"{pieces[0]} dersi " + ", ".join(pieces[1:]) + " olarak kayitli."

    if capability == "curriculum.semester_courses":
        semester = metadata.get("semester")
        if not records:
            return f"{semester}. yariyil icin mufredat veritabaninda ders kaydi bulunamadi."
        return _format_grouped_course_list(
            records,
            heading=f"{semester}. yariyil dersleri:",
        )

    if capability == "schedule.weekly_program":
        if message == "schedule_filter_required" or metadata.get("needs_schedule_filter"):
            program = metadata.get("program") or "ilgili program"
            return (
                f"{program} ders programini karisik listelememek icin sinif/donem bilgisi gerekiyor. "
                "Ornegin 'Bilgisayar Muhendisligi 3. sinif guz ders programi' diye sorabilirsiniz. "
                "Tum siniflari istiyorsaniz 'tum siniflar' diye belirtin."
            )
        if not records:
            return "Bu filtrelerle ders programi veritabaninda kayit bulunamadi."
        if metadata.get("all_schedule_groups"):
            program = metadata.get("program") or "program"
            return _format_schedule_by_group(
                records,
                heading=f"{format_schedule_label(program)} için bulunan ders programı satırları:",
            )
        return _format_schedule(records, heading="Bulunan ders programı satırları:")

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


def _format_grouped_course_list(records: list[dict[str, Any]], *, heading: str) -> str:
    groups: list[tuple[str, list[dict[str, Any]]]] = [
        ("Zorunlu dersler", []),
        ("Teknik/secmeli dersler", []),
        ("Sosyal/universite secmeli dersleri", []),
        ("Staj/MUP", []),
        ("Diger dersler", []),
    ]
    group_map = {name: bucket for name, bucket in groups}
    seen: set[tuple[str, str]] = set()
    for record in records:
        code = str(record.get("course_code") or record.get("code") or "").strip()
        name = str(record.get("course_name") or record.get("name") or "").strip()
        key = (code.upper(), name.lower())
        if key in seen:
            continue
        seen.add(key)
        course_type = str(record.get("course_type") or "").lower()
        normalized_name = name.lower()
        if course_type in {"staj", "mup", "sanayi"} or "staj" in normalized_name:
            group_map["Staj/MUP"].append(record)
        elif course_type in {"teknik_secmeli", "lab_secmeli", "secmeli_grup"}:
            group_map["Teknik/secmeli dersler"].append(record)
        elif course_type in {"sosyal_secmeli", "universite_secmeli"}:
            group_map["Sosyal/universite secmeli dersleri"].append(record)
        elif course_type in {"zorunlu", "entegre", "ortak"} or not course_type:
            group_map["Zorunlu dersler"].append(record)
        else:
            group_map["Diger dersler"].append(record)

    lines = [heading]
    for group_name, bucket in groups:
        if not bucket:
            continue
        lines.append("")
        lines.append(f"{group_name}:")
        for record in bucket:
            lines.append(f"- {_format_course_line(record)}")
    return "\n".join(lines)


def _format_course_line(record: dict[str, Any]) -> str:
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
    return f"{code} {name}{suffix}".strip()


def _format_schedule(records: list[dict[str, Any]], *, heading: str) -> str:
    lines = [heading]
    limit = 120
    for record in records[:limit]:
        day = format_schedule_day(record.get("day") or record.get("day_name") or record.get("day_of_week") or "")
        start = record.get("start_time") or ""
        end = record.get("end_time") or ""
        name = format_schedule_course_name(record.get("course_name") or record.get("name") or "")
        group = format_schedule_group(record.get("schedule_group") or "")
        room = record.get("classroom") or record.get("room") or ""
        group_text = f" | {group}" if group else ""
        room_text = f" | Derslik: {room}" if room else ""
        time_text = f"{start}-{end}" if start or end else ""
        lines.append(f"- {day} {time_text} | {name}{group_text}{room_text}".strip())
    if len(records) > limit:
        lines.append(f"... {len(records) - limit} satir daha var; sinif veya gun belirtirseniz daraltabilirim.")
    return "\n".join(lines)


def _format_schedule_by_group(records: list[dict[str, Any]], *, heading: str) -> str:
    lines = [heading]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        group = (
            format_schedule_group(record.get("schedule_group") or "")
            or "Sınıf/grup belirtilmeyen dersler"
        )
        grouped.setdefault(group, []).append(record)
    emitted = 0
    limit = 1000
    for group in sorted(grouped, key=schedule_group_sort_key):
        lines.append("")
        lines.append(f"{group}:")
        for record in grouped[group]:
            if emitted >= limit:
                break
            day = format_schedule_day(record.get("day") or record.get("day_name") or record.get("day_of_week") or "")
            start = record.get("start_time") or ""
            end = record.get("end_time") or ""
            name = format_schedule_course_name(record.get("course_name") or record.get("name") or "")
            room = record.get("classroom") or record.get("room") or ""
            room_text = f" | Derslik: {room}" if room else ""
            time_text = f"{start}-{end}" if start or end else ""
            lines.append(f"- {day} {time_text} | {name}{room_text}".strip())
            emitted += 1
    if len(records) > emitted:
        lines.append(f"... {len(records) - emitted} satir daha var; sinif veya gun belirtirseniz daraltabilirim.")
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


def _class_year_from_semester(value: Any) -> int | None:
    try:
        semester = int(str(value))
    except (TypeError, ValueError):
        return None
    return (semester + 1) // 2
