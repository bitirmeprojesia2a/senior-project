"""Orkestrator final yanit birlestirme yardimcilari."""

from __future__ import annotations

import re

from src.core.constants import Department
from src.core.messages import CONTACT_SEPARATOR, CONTACT_SUGGESTION
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

LOW_CONFIDENCE_RAG_SCORE_THRESHOLD = 0.02
GENERATION_MODE_LABELS = {
    "vt": "VT",
    "rag": "RAG",
    "llm": "LLM",
    "kural": "Kural",
}


def split_answer_and_contact_flag(answer: str) -> tuple[str, bool]:
    """Cevabi ana govde ve iletisim eki olarak ayirir."""
    stripped = answer.strip()
    if CONTACT_SEPARATOR not in stripped:
        return stripped, False
    core, _ = stripped.split(CONTACT_SEPARATOR, 1)
    return core.rstrip(), True


def compact_text(value: str, *, max_len: int = 420) -> str:
    """Bosluklari sikistirir ve gerekirse kisaltir."""
    compact = re.sub(r"\s+", " ", value).strip()
    if len(compact) > max_len:
        return f"{compact[: max_len - 3].rstrip()}..."
    return compact


def clean_final_answer(answer: str) -> str:
    """LLM veya birlesik cevaptan kalan basit bicim artefaktlarini temizler."""
    cleaned = answer.replace("**", "").strip()
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
        "Verilen kaynaklarda bu soruyu dogrudan yanitlayan net bir bilgi bulunmuyor.",
        cleaned,
    )
    cleaned = re.sub(
        r"(?im)^\s*Açık bir bilgi kaynağı bulamadım, ancak.*?$",
        "Verilen kaynaklarda bu soruyu dogrudan yanitlayan net bir bilgi bulunmuyor.",
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


def top_source_score(response: DepartmentResponse) -> float:
    """Bir departman cevabindaki en yuksek kaynak skorunu doner."""
    if not response.sources:
        return 0.0
    return max(float(source.score) for source in response.sources)


def is_low_confidence_rag_response(response: DepartmentResponse) -> bool:
    """Sadece dusuk skorlu RAG sonuclarina dayanan zayif cevaplari tanir."""
    if is_announcement_response(response):
        return False
    if response.db_data:
        return False
    if not response.sources:
        return False
    return top_source_score(response) < LOW_CONFIDENCE_RAG_SCORE_THRESHOLD


def filter_low_confidence_responses(responses: list[DepartmentResponse]) -> list[DepartmentResponse]:
    """Guclu cevaplar varken cok dusuk skorlu yanitlari finalden ayiklar."""
    if len(responses) < 2:
        return responses

    strong_non_announcement = [
        response
        for response in responses
        if not is_announcement_response(response) and not is_low_confidence_rag_response(response)
    ]
    if not strong_non_announcement:
        return responses

    filtered = [
        response
        for response in responses
        if is_announcement_response(response) or not is_low_confidence_rag_response(response)
    ]
    return filtered or responses


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
    if not answer.strip() or "Kaynak Ozeti:" in answer:
        return answer

    summary = format_source_summary_from_responses(responses)
    if not summary:
        return answer
    return f"{answer.rstrip()}\n\nKaynak Ozeti:\n{summary}"


def append_generation_summary(answer: str, responses: list[DepartmentResponse]) -> str:
    """Cevabin sonuna hangi veri yollarinin kullanildigini ekler."""
    if not answer.strip() or "Uretim Turu:" in answer:
        return answer
    if not responses:
        return answer

    lines = format_generation_summary_lines(responses)
    if not lines:
        return answer
    return f"{answer.rstrip()}\n\nUretim Turu:\n{chr(10).join(lines)}"


def append_source_summary_for_sources(answer: str, sources: list[RAGSource]) -> str:
    """Tek basina kaynak listesi verilen cevaplara kaynak ozeti ekler."""
    if not answer.strip() or "Kaynak Ozeti:" in answer:
        return answer
    if not sources:
        return answer

    labels: list[str] = []
    seen: set[str] = set()
    for source in sources:
        label = _format_source_label(source)
        if label and label not in seen:
            seen.add(label)
            labels.append(f"- {label}")
    if not labels:
        return answer
    return f"{answer.rstrip()}\n\nKaynak Ozeti:\n{chr(10).join(labels)}"


def format_generation_summary_lines(responses: list[DepartmentResponse]) -> list[str]:
    """Departman bazinda cevap uretim turlerini etiketler."""
    meaningful = [response for response in responses if response.answer.strip()]
    if not meaningful:
        return []

    non_announcement = [
        response for response in meaningful if not is_announcement_response(response)
    ]
    target = non_announcement or meaningful
    multi_department = len({response.department for response in target}) > 1

    lines: list[str] = []
    for response in target:
        label = _format_generation_mode_label(_infer_generation_mode(response))
        if multi_department:
            title = DEPARTMENT_SECTION_TITLES.get(response.department, response.department.value)
            lines.append(f"- {title}: {label}")
        else:
            lines.append(f"- {label}")
    return lines


def _format_source_label(source: RAGSource) -> str | None:
    metadata = source.metadata or {}
    record_type = metadata.get("record_type")
    if record_type == "announcement":
        title = metadata.get("title") or compact_text(source.content, max_len=80)
        url = metadata.get("source_url")
        return f"Duyuru kaydi: {title}" + (f" ({url})" if url else "")

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
    meaningful.sort(
        key=lambda response: (
            1 if is_announcement_response(response) else 0,
            DEPARTMENT_DISPLAY_ORDER.get(response.department, 99),
        )
    )
    non_announcement = [
        response for response in meaningful if not is_announcement_response(response)
    ]
    multi_department = len({response.department for response in non_announcement}) > 1

    for response in meaningful:
        answer = response.answer.strip()
        if CONTACT_SEPARATOR in answer:
            answer = answer.split(CONTACT_SEPARATOR, 1)[0].rstrip()
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
