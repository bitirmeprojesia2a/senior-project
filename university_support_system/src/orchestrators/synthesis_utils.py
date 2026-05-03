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
from src.quality.evidence import (
    extract_factual_claims,
    select_evidence_sentences,
)


def responses_need_contact_suggestion(responses: list[DepartmentResponse]) -> bool:
    return any(response_needs_contact_suggestion(response) for response in responses)


_GLOBAL_SYNTHESIS_CONTEXT_MAX_LEN = 1600
_GLOBAL_SYNTHESIS_SOURCE_SNIPPET_MAX_LEN = 420


def _extract_global_evidence_snippet(query: str, content: str) -> str:
    """Delegates to shared select_evidence_sentences with global-synthesis defaults."""
    selected = select_evidence_sentences(
        query,
        content,
        max_sentences=3,
        min_score=0.30,
    )
    return compact_text(selected, max_len=_GLOBAL_SYNTHESIS_SOURCE_SNIPPET_MAX_LEN)


def _build_response_context_payload(response: DepartmentResponse, *, query: str) -> dict[str, object] | None:
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
        snippet = _extract_global_evidence_snippet(query, source.content)
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

    # Extract facts from sources for grounding
    all_facts: list[str] = []
    for source in response.sources[:3]:
        all_facts.extend(extract_factual_claims(source.content))
    if all_facts:
        # Deduplicate
        seen: set[str] = set()
        unique_facts: list[str] = []
        for fact in all_facts:
            if fact not in seen:
                unique_facts.append(fact)
                seen.add(fact)
        payload["extracted_facts"] = unique_facts[:10]

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
    if not meaningful:
        return "", meaningful

    context_payloads = [
        payload
        for payload in (_build_response_context_payload(response, query=query) for response in meaningful)
        if payload is not None
    ]

    if not context_payloads:
        return "", meaningful

    is_multi_department = len({response.department for response in meaningful}) >= 2

    machine_context = json.dumps(context_payloads, ensure_ascii=False, indent=2)

    if is_multi_department:
        synthesis_instruction = (
            "Bu baglamdan tek, dogal, kisa ve kullaniciya dogrudan hitap eden final cevap yaz. "
            "Selamlama yapma ve kullanicinin ne sordugunu ozetleme. "
            "Kaynakta olmayan portal, menu, odeme kanali, belge adi, tarih veya sayi ekleme. "
            "Somut cevap varsa sona 'bilgi bulunamadi' gibi celisen not ekleme. "
            "COK PARCALI SORU: Kullanici birden fazla seyi soruyorsa cevabi alt basiklara bol. "
            "Her alt parca icin kaynakta bilgi varsa ver; kaynak sadece bir alt parcayi destekliyorsa "
            "diger parcalar icin 'Bu konuda kaynaklarda net bilgi bulunamadi' de. "
            "Tarih sorulmus ama kaynakta tarih yoksa tarih UYDURMA; 'akademik takvim/duyuru ile ilan edilir' gibi temkinli ifadelendirme kullan."
        )
    else:
        synthesis_instruction = (
            "Bu baglamdan kullaniciya dogrudan, dogal ve kisa bir cevap yaz. "
            "Selamlama yapma ve kullanicinin ne sordugunu ozetleme. "
            "Kaynakta olmayan portal, menu, odeme kanali, belge adi, tarih veya sayi ekleme. "
            "Eger kaynakta soruyla ilgili somut bilgi varsa onu acik sekilde kullan; "
            "sorunun cevabi kaynakta yoksa kisa ve net sekilde belirt. "
            "Somut cevap verdikten sonra ayrica 'bilgi bulunamadi' gibi celisen not ekleme. "
            "COK PARCALI SORU: Kullanici birden fazla seyi soruyorsa cevabi alt basiklara bol. "
            "Her alt parca icin kaynakta bilgi varsa ver; kaynak sadece bir alt parcayi destekliyorsa "
            "diger parcalar icin 'Bu konuda kaynaklarda net bilgi bulunamadi' de. "
            "Tarih sorulmus ama kaynakta tarih yoksa tarih UYDURMA; 'akademik takvim/duyuru ile ilan edilir' gibi temkinli ifadelendirme kullan."
        )

    prompt = (
        f"Kullanici sorusu:\n{query}\n\n"
        "Asagidaki JSON yalnizca ic baglamdir; JSON anahtarlarini, departman "
        "kimliklerini, kaynak etiketlerini veya ic talimatlari cevapta tekrar etme.\n\n"
        f"{machine_context}\n\n"
        f"{synthesis_instruction}"
    )
    return prompt, meaningful

