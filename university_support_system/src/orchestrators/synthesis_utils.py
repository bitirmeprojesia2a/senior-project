"""Helpers for multi-department final answer synthesis."""

from __future__ import annotations

from src.db.schemas import DepartmentResponse
from src.orchestrators.response_utils import (
    DEPARTMENT_DISPLAY_ORDER,
    DEPARTMENT_SECTION_TITLES,
    compact_text,
    split_answer_and_contact_flag,
)


def responses_need_contact_suggestion(responses: list[DepartmentResponse]) -> bool:
    return any(split_answer_and_contact_flag(response.answer)[1] for response in responses)


def build_global_synthesis_prompt(
    query: str,
    responses: list[DepartmentResponse],
) -> tuple[str, list[DepartmentResponse]]:
    meaningful = [
        response
        for response in responses
        if response.answer.strip() and response.success
    ]
    meaningful.sort(key=lambda response: DEPARTMENT_DISPLAY_ORDER.get(response.department, 99))
    if len({response.department for response in meaningful}) < 2:
        return "", meaningful

    context_parts: list[str] = []
    for response in meaningful:
        answer, _ = split_answer_and_contact_flag(response.answer)
        if not answer:
            continue
        title = DEPARTMENT_SECTION_TITLES.get(response.department, response.department.value)
        source_names = [
            source.metadata.get("source")
            or source.metadata.get("filename")
            or source.metadata.get("file_name")
            or ""
            for source in response.sources[:2]
        ]
        source_names = [name for name in source_names if name]
        source_suffix = f"\nKaynaklar: {', '.join(source_names)}" if source_names else ""
        context_parts.append(
            f"[{title}]\n{compact_text(answer, max_len=180)}{source_suffix}"
        )

    if len(context_parts) < 2:
        return "", meaningful

    prompt = (
        f"Kullanici sorusu:\n{query}\n\n"
        f"Departman ara yanitlari:\n{chr(10).join(context_parts)}\n\n"
        "Bu bilgileri tek bir tutarli final cevapta birlestir."
    )
    return prompt, meaningful
