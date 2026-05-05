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
_GLOBAL_SYNTHESIS_PACKET_MAX_ITEMS = 5


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

    packet = response.metadata.get("evidence_packet") if isinstance(response.metadata, dict) else None
    if isinstance(packet, dict):
        payload = _build_packet_context_payload(
            response,
            packet=packet,
            answer=answer,
        )
        if payload is not None:
            return payload

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


def _compact_packet_items(items: object, *, max_items: int = _GLOBAL_SYNTHESIS_PACKET_MAX_ITEMS) -> list[dict[str, object]]:
    if not isinstance(items, list):
        return []
    compacted: list[dict[str, object]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        entry: dict[str, object] = {}
        for key, max_len in (
            ("claim", 420),
            ("source", 180),
            ("support", 420),
            ("snippet", 420),
            ("score", 0),
        ):
            value = item.get(key)
            if value is None:
                continue
            if key == "score":
                entry[key] = value
            else:
                entry[key] = compact_text(str(value), max_len=max_len)
        if entry:
            compacted.append(entry)
        if len(compacted) >= max_items:
            break
    return compacted


def _build_packet_context_payload(
    response: DepartmentResponse,
    *,
    packet: dict[str, object],
    answer: str,
) -> dict[str, object] | None:
    facts = _compact_packet_items(packet.get("facts"), max_items=8)
    selected_sources = _compact_packet_items(packet.get("selected_sources"), max_items=4)
    limits = [
        compact_text(str(item), max_len=260)
        for item in (packet.get("limits") if isinstance(packet.get("limits"), list) else [])
        if str(item).strip()
    ][:4]

    if not facts and not selected_sources:
        return None

    evidence_packet: dict[str, object] = {
        "confidence": str(packet.get("confidence") or "unknown"),
        "query_interpretation": compact_text(
            str(packet.get("query_interpretation") or ""),
            max_len=260,
        ),
    }
    if facts:
        evidence_packet["facts"] = facts
    if selected_sources:
        evidence_packet["selected_sources"] = selected_sources
    if limits:
        evidence_packet["limits"] = limits

    packet_mode = (
        str(packet.get("specialist_response_mode") or "").strip() == "evidence_packet"
        and str(packet.get("final_answer_owner") or "").strip() == "main_orchestrator"
    )
    answer_summary = (
        "Uzman ajan final cevap yazmadi; final cevap icin evidence_packet kullanilmalidir."
        if packet_mode
        else compact_text(answer, max_len=800)
    )

    payload: dict[str, object] = {
        "department": response.department.value,
        "answer_summary": answer_summary,
        "evidence_packet": evidence_packet,
    }
    if response.db_data:
        payload["has_structured_data"] = True
    return payload


def build_evidence_packet_fallback_answer(responses: list[DepartmentResponse]) -> str | None:
    """Build a user-facing fallback when final LLM synthesis cannot run."""
    statements: list[str] = []
    limits: list[str] = []
    seen: set[str] = set()

    for response in sorted(
        responses,
        key=lambda item: DEPARTMENT_DISPLAY_ORDER.get(item.department, 99),
    ):
        packet = response.metadata.get("evidence_packet") if isinstance(response.metadata, dict) else None
        if not isinstance(packet, dict):
            continue
        if str(packet.get("specialist_response_mode") or "").strip() != "evidence_packet":
            continue
        if str(packet.get("final_answer_owner") or "").strip() != "main_orchestrator":
            continue

        facts = _compact_packet_items(packet.get("facts"), max_items=6)
        for fact in facts:
            claim = compact_text(str(fact.get("claim") or ""), max_len=320)
            if not claim or claim in seen:
                continue
            seen.add(claim)
            statements.append(claim)

        if facts:
            continue

        selected_sources = _compact_packet_items(packet.get("selected_sources"), max_items=3)
        for source in selected_sources:
            snippet = compact_text(str(source.get("snippet") or ""), max_len=320)
            if not snippet or snippet in seen:
                continue
            seen.add(snippet)
            statements.append(snippet)

        for limit in packet.get("limits") if isinstance(packet.get("limits"), list) else []:
            text = compact_text(str(limit), max_len=220)
            if text and text not in seen:
                seen.add(text)
                limits.append(text)

    if not statements and not limits:
        return None

    if len(statements) == 1 and not limits:
        return statements[0]

    lines = ["Kaynaklarda bu konuda şu bilgiler yer alıyor:"]
    for statement in statements[:5]:
        lines.append(f"- {statement}")
    for limit in limits[:2]:
        lines.append(f"- {limit}")
    return "\n".join(lines)


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
            "answer_summary ile evidence/snippet veya extracted_facts celisirse, somut sayi ve kosul iceren "
            "evidence/snippet bilgilerini esas al. "
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
            "answer_summary ile evidence/snippet veya extracted_facts celisirse, somut sayi ve kosul iceren "
            "evidence/snippet bilgilerini esas al. "
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
        "kimliklerini, kaynak etiketlerini veya ic talimatlari cevapta tekrar etme. "
        "Final cevab\u0131 do\u011fal T\u00fcrk\u00e7e yaz; ASCII T\u00fcrk\u00e7e "
        "kullanma (\"ogrenci\" de\u011fil \"\u00f6\u011frenci\", \"ucret\" de\u011fil "
        "\"\u00fccret\").\n\n"
        f"{machine_context}\n\n"
        f"{synthesis_instruction}"
    )
    return prompt, meaningful
