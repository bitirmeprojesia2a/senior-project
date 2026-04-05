"""Orkestrator final yanit birlestirme yardimcilari."""

from __future__ import annotations

import re

from src.core.constants import Department
from src.core.messages import CONTACT_SEPARATOR, CONTACT_SUGGESTION
from src.db.schemas import DepartmentResponse

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
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def compose_department_answers(responses: list[DepartmentResponse]) -> str:
    """Departman cevaplarini tek veya coklu bolum formatinda birlestirir."""
    if not responses:
        return ""

    sections: list[str] = []
    include_contact = False
    meaningful = [response for response in responses if response.answer.strip()]
    meaningful.sort(key=lambda response: DEPARTMENT_DISPLAY_ORDER.get(response.department, 99))
    multi_department = len({response.department for response in meaningful}) > 1

    for response in meaningful:
        answer = response.answer.strip()
        if CONTACT_SEPARATOR in answer:
            answer = answer.split(CONTACT_SEPARATOR, 1)[0].rstrip()
            include_contact = True

        if multi_department:
            title = DEPARTMENT_SECTION_TITLES.get(response.department, response.department.value)
            sections.append(f"{title}:\n{answer}")
        else:
            sections.append(answer)

    final_answer = "\n\n".join(section for section in sections if section)
    if include_contact:
        final_answer += CONTACT_SUGGESTION
    return final_answer
