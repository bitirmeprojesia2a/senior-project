"""Helpers for multi-department final answer synthesis."""

from __future__ import annotations

import json

from src.db.schemas import DepartmentResponse
from src.orchestrators.response_utils import (
    DEPARTMENT_DISPLAY_ORDER,
    compact_text,
    is_announcement_response,
    response_eligible_for_global_synthesis,
    response_core_answer,
    response_needs_contact_suggestion,
)


def responses_need_contact_suggestion(responses: list[DepartmentResponse]) -> bool:
    return any(response_needs_contact_suggestion(response) for response in responses)


_GLOBAL_SYNTHESIS_CONTEXT_MAX_LEN = 1600
_GLOBAL_SYNTHESIS_SOURCE_SNIPPET_MAX_LEN = 260


def _build_response_context_payload(response: DepartmentResponse) -> dict[str, object] | None:
    answer = response_core_answer(response)
    if not answer:
        return None

    evidence_items: list[dict[str, str]] = []

    for index, source in enumerate(response.sources[:2], start=1):
        source_name = (
            source.metadata.get("source")
            or source.metadata.get("filename")
            or source.metadata.get("file_name")
            or f"Kaynak {index}"
        )
        snippet = compact_text(
            source.content,
            max_len=_GLOBAL_SYNTHESIS_SOURCE_SNIPPET_MAX_LEN,
        )
        evidence_items.append(
            {
                "source": str(source_name),
                "snippet": snippet,
            }
        )

    payload: dict[str, object] = {
        "department": response.department.value,
        "answer_summary": compact_text(answer, max_len=_GLOBAL_SYNTHESIS_CONTEXT_MAX_LEN),
    }
    if evidence_items:
        payload["evidence"] = evidence_items
    if response.db_data:
        payload["has_structured_data"] = True

    return payload


def build_global_synthesis_prompt(
    query: str,
    responses: list[DepartmentResponse],
) -> tuple[str, list[DepartmentResponse]]:
    meaningful = [
        response
        for response in responses
        if response_eligible_for_global_synthesis(response)
    ]
    meaningful.sort(key=lambda response: DEPARTMENT_DISPLAY_ORDER.get(response.department, 99))
    if len({response.department for response in meaningful}) < 2:
        return "", meaningful

    context_payloads = [
        payload
        for payload in (_build_response_context_payload(response) for response in meaningful)
        if payload is not None
    ]

    if len(context_payloads) < 2:
        return "", meaningful

    machine_context = json.dumps(context_payloads, ensure_ascii=False, indent=2)
    prompt = (
        f"Kullanici sorusu:\n{query}\n\n"
        "Asagidaki JSON yalnizca ic baglamdir. "
        "JSON anahtarlarini, departman kimliklerini veya kayit etiketlerini cevapta tekrar etme.\n\n"
        f"{machine_context}\n\n"
        "Bu bilgileri tek bir tutarli final cevapta birlestir.\n"
        "KURALLAR:\n"
        "- YALNIZCA verilen kanit ve departman ozetlerindeki bilgileri kullan. Yeni bilgi EKLEME.\n"
        "- Kanit varsa departman ozetinden once kaniti esas al.\n"
        "- Soruyla dogrudan ilgili olmayan madde, tebligat veya belge parcalarini kullanma.\n"
        "- Ayni bilgiyi tekrar etme.\n"
        "- YALNIZCA Turkce yaz. Ingilizce kelime KULLANMA.\n"
        "- 'Ogrenci Isleri:', 'Akademik Programlar:', 'Finans:', 'Kaynaklar:', 'Kanitlar:' veya 'Sonuc:' gibi basliklar yazma.\n"
        "- Tek parca, dogal bir final cevap yaz; departman departman ayirma.\n"
        "- Yalnizca kullanicinin isine yarayan somut adim, tarih, kosul ve sonucu kisa bicimde yaz."
    )
    return prompt, meaningful
