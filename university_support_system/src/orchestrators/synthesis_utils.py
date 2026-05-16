"""Helpers for multi-department final answer synthesis."""

from __future__ import annotations

import json
import os

from src.core.constants import Department
from src.db.schemas import DepartmentResponse
from src.orchestrators.response_utils import (
    DEPARTMENT_DISPLAY_ORDER,
    compact_text,
    is_announcement_response,
    response_eligible_for_global_synthesis,
    response_core_answer,
    response_needs_contact_suggestion,
)
from src.core.text_normalization import normalize_text
from src.quality.evidence import (
    extract_factual_claims,
    select_evidence_sentences,
)
from src.quality.evidence_answer_validator import extract_value_labels, validate_evidence_answer

_INTERNAL_PATH_PREFIXES = ("/app/data/", "/app/", "data/raw/", "data/")


def _clean_source_name(source_name: str) -> str:
    """Strip internal container/deployment paths from source names."""
    for prefix in _INTERNAL_PATH_PREFIXES:
        if source_name.startswith(prefix):
            source_name = source_name[len(prefix):]
    # Sadece dosya adını tut (uzun alt-dizin yollarını temizle)
    if "/" in source_name and not source_name.startswith("http"):
        source_name = os.path.basename(source_name)
    return source_name


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
        # Dosya yolunu temizle — sadece dosya adını göster
        source_name = _clean_source_name(str(source_name))
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
            ("source_family", 120),
            ("source_owner", 120),
            ("department", 80),
            ("specialist", 120),
            ("contract_match_reason", 220),
            ("policy_alignment", 0),
            ("value_roles", 0),
            ("score", 0),
        ):
            value = item.get(key)
            if value is None:
                continue
            if key == "score":
                entry[key] = value
            elif key == "policy_alignment":
                compact_alignment = _compact_policy_alignment(value)
                if compact_alignment:
                    entry[key] = compact_alignment
            elif key == "value_roles":
                compact_roles = _compact_value_roles(value)
                if compact_roles:
                    entry[key] = compact_roles
            else:
                entry[key] = compact_text(str(value), max_len=max_len)
        if entry:
            compacted.append(entry)
        if len(compacted) >= max_items:
            break
    return compacted


def _compact_policy_alignment(value: object) -> dict[str, object]:
    """Keep only synthesis-critical alignment fields to avoid prompt bloat."""
    if not isinstance(value, dict):
        return {}
    compacted: dict[str, object] = {}
    for key in (
        "status",
        "query_facet",
        "query_target_program",
        "matched_facets",
        "matched_programs",
        "conflict_facets",
        "conflict_programs",
    ):
        item = value.get(key)
        if item in (None, "", [], {}):
            continue
        if isinstance(item, list):
            compacted[key] = [compact_text(str(part), max_len=80) for part in item[:3]]
        else:
            compacted[key] = compact_text(str(item), max_len=120)
    return compacted


def _compact_value_roles(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    roles: list[dict[str, object]] = []
    for item in value[:6]:
        if not isinstance(item, dict):
            continue
        entry = {
            key: compact_text(str(item.get(key) or ""), max_len=80)
            for key in ("value", "role", "policy_alignment_status")
            if str(item.get(key) or "").strip()
        }
        if entry:
            roles.append(entry)
    return roles


def _build_packet_context_payload(
    response: DepartmentResponse,
    *,
    packet: dict[str, object],
    answer: str,
) -> dict[str, object] | None:
    facts = _compact_packet_items(packet.get("facts"), max_items=8)
    selected_sources = _compact_packet_items(packet.get("selected_sources"), max_items=4)
    required_values = [
        compact_text(str(item), max_len=80)
        for item in (packet.get("required_values") if isinstance(packet.get("required_values"), list) else [])
        if str(item).strip()
    ][:10]
    supporting_claims = [
        compact_text(str(item), max_len=260)
        for item in (packet.get("supporting_claims") if isinstance(packet.get("supporting_claims"), list) else [])
        if str(item).strip()
    ][:6]
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
    for key, max_len in (
        ("source_owner", 160),
        ("source_family", 120),
        ("department", 80),
        ("specialist", 120),
        ("contract_match_reason", 220),
    ):
        value = packet.get(key)
        if value:
            evidence_packet[key] = compact_text(str(value), max_len=max_len)
    if facts:
        evidence_packet["facts"] = facts
    if selected_sources:
        evidence_packet["selected_sources"] = selected_sources
    if required_values:
        evidence_packet["required_values"] = required_values
    if supporting_claims:
        evidence_packet["supporting_claims"] = supporting_claims
    value_arbitration = packet.get("value_arbitration") if isinstance(packet.get("value_arbitration"), dict) else {}
    if value_arbitration:
        evidence_packet["value_arbitration"] = value_arbitration
    source_family = compact_text(str(packet.get("source_family") or ""), max_len=120)
    if source_family:
        evidence_packet["source_family"] = source_family
    answer_contract = packet.get("answer_contract") if isinstance(packet.get("answer_contract"), dict) else {}
    evidence_contract = packet.get("evidence_contract") if isinstance(packet.get("evidence_contract"), dict) else {}
    if answer_contract:
        evidence_packet["answer_contract"] = answer_contract
    if evidence_contract:
        evidence_packet["evidence_contract"] = evidence_contract
    policy_facet = packet.get("policy_facet") if isinstance(packet.get("policy_facet"), dict) else {}
    if policy_facet:
        evidence_packet["policy_facet"] = policy_facet
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


def _payload_contract_match_score(payload: dict[str, object], *, query: str) -> tuple[float, int]:
    packet = payload.get("evidence_packet") if isinstance(payload.get("evidence_packet"), dict) else {}
    haystack = normalize_text(
        " ".join(
            str(value or "")
            for value in (
                query,
                payload.get("department"),
                packet.get("source_owner"),
                packet.get("source_family"),
                packet.get("specialist"),
                packet.get("contract_match_reason"),
                packet.get("required_values"),
                packet.get("supporting_claims"),
                packet.get("policy_facet"),
            )
        )
    )
    score = 0.0
    if "required_values" in packet:
        score += 2.0
    if "student_affairs_policy" in haystack:
        score += 1.0
    if "registration_agent" in haystack:
        score += 1.0
    if "academic_policy_support" in haystack or "regulation_agent" in haystack:
        score += 0.5
    query_norm = normalize_text(query)
    if any(marker in query_norm for marker in ("cap", "cift anadal", "yandal", "gano", "gno", "not ortalamasi")):
        if "registration_agent" in haystack:
            score += 2.0
        if "regulation_agent" in haystack:
            score += 0.75
        if "graduation_agent" in haystack and "registration_agent" not in haystack:
            score -= 1.0
    department = str(payload.get("department") or "")
    order = DEPARTMENT_DISPLAY_ORDER.get(Department(department), 99) if department in {item.value for item in Department} else 99
    return (-score, order)


def _fallback_statement_score(query: str, statement: str) -> float:
    normalized_query = normalize_text(query)
    normalized_statement = normalize_text(statement)
    if not normalized_statement:
        return 0.0

    query_terms = {
        term
        for term in normalized_query.split()
        if len(term) >= 3
        and term not in {"icin", "olan", "peki", "kac", "nasil", "nedir", "olmali", "gerekir"}
    }
    overlap = sum(1.0 for term in query_terms if term in normalized_statement)
    value_bonus = 1.5 if extract_value_labels(statement) else 0.0
    return overlap + value_bonus


def _append_fallback_statement(
    candidates: list[tuple[float, int, str]],
    *,
    query: str,
    statement: str,
    seen: set[str],
) -> None:
    text = compact_text(statement, max_len=320)
    if not text or text in seen:
        return
    seen.add(text)
    candidates.append((_fallback_statement_score(query, text), len(candidates), text))


def build_evidence_packet_fallback_answer(
    responses: list[DepartmentResponse],
    *,
    query: str = "",
) -> str | None:
    """Build a user-facing fallback when final LLM synthesis cannot run."""
    statement_candidates: list[tuple[float, int, str]] = []
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
            _append_fallback_statement(
                statement_candidates,
                query=query,
                statement=str(fact.get("claim") or ""),
                seen=seen,
            )

        if facts:
            continue

        selected_sources = _compact_packet_items(packet.get("selected_sources"), max_items=3)
        for source in selected_sources:
            _append_fallback_statement(
                statement_candidates,
                query=query,
                statement=str(source.get("snippet") or ""),
                seen=seen,
            )

        for limit in packet.get("limits") if isinstance(packet.get("limits"), list) else []:
            text = compact_text(str(limit), max_len=220)
            if text and text not in seen:
                seen.add(text)
                limits.append(text)

    if not statement_candidates:
        for response in sorted(
            responses,
            key=lambda item: DEPARTMENT_DISPLAY_ORDER.get(item.department, 99),
        ):
            for source in response.sources[:3]:
                for claim in extract_factual_claims(source.content)[:8]:
                    _append_fallback_statement(
                        statement_candidates,
                        query=query,
                        statement=claim,
                        seen=seen,
                    )
                if statement_candidates:
                    break
            if statement_candidates:
                break

    statements = [
        item[2]
        for item in sorted(
            statement_candidates,
            key=lambda item: (-item[0], item[1]),
        )
    ]

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


def _build_synthesis_value_contract(
    query: str,
    responses: list[DepartmentResponse],
) -> dict[str, object]:
    try:
        validation = validate_evidence_answer(query=query, answer="", responses=responses)
    except Exception:
        return {}
    arbitration = validation.value_arbitration or {}
    primary_values = [
        compact_text(str(item), max_len=80)
        for item in (arbitration.get("primary_values") or [])
        if str(item).strip()
    ]
    related_values = [
        compact_text(str(item), max_len=80)
        for item in (arbitration.get("related_values") or [])
        if str(item).strip()
    ]
    secondary_values = [
        compact_text(str(item), max_len=80)
        for item in (arbitration.get("secondary_values") or [])
        if str(item).strip()
    ]
    conflicting_values = [
        compact_text(str(item), max_len=80)
        for item in (arbitration.get("conflicting_values") or [])
        if str(item).strip()
    ]
    if not any((primary_values, related_values, secondary_values, conflicting_values)):
        return {}
    required_claims = [
        {
            "claim": compact_text(claim.claim, max_len=260),
            "source": compact_text(str(claim.source or ""), max_len=160),
            "values": [value.raw for value in claim.required_values],
            "role": claim.value_role,
        }
        for claim in validation.required_claims[:4]
    ]
    return {
        "mode": "deterministic_value_arbitration",
        "primary_values": primary_values,
        "related_values": related_values,
        "secondary_values": secondary_values,
        "conflicting_values": conflicting_values,
        "required_claims": required_claims,
    }


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
    context_payloads.sort(key=lambda payload: _payload_contract_match_score(payload, query=query))

    if not context_payloads:
        return "", meaningful

    is_multi_department = len({response.department for response in meaningful}) >= 2

    value_contract = _build_synthesis_value_contract(query, meaningful)
    machine_payload: object = (
        {
            "synthesis_value_contract": value_contract,
            "department_contexts": context_payloads,
        }
        if value_contract
        else context_payloads
    )
    machine_context = json.dumps(machine_payload, ensure_ascii=False, indent=2)

    if is_multi_department:
        synthesis_instruction = (
            "Bu bağlamdan tek, doğal, kısa ve kullanıcıya doğrudan hitap eden final cevap yaz. "
            "Selamlama yapma ve kullanıcının ne sorduğunu özetleme. "
            "Kaynakta olmayan portal, menü, ödeme kanalı, belge adı, tarih veya sayı ekleme. "
            "answer_summary ile evidence/snippet veya extracted_facts çelişirse, somut sayı ve koşul içeren "
            "evidence/snippet bilgilerini esas al. "
            "evidence_packet.required_values varsa, kullanici sorusuyla ilgili olanlari kaynak baglami destekliyorsa koru; "
            "kaynakta olmayan deger ekleme. "
            "synthesis_value_contract varsa primary_values kullanicinin sorusuna verilecek ana degerlerdir; "
            "secondary_values/conflicting_values icindeki degerleri kullanici ozellikle karsilastirma istemedikce cevapta yazma. "
            "evidence_packet.value_arbitration varsa primary_values ana cevaptir; secondary_values/conflicting_values "
            "ana cevap gibi yazilmaz ve tekil deger sorusunda tercihen hic yazilmaz. related_values ana cevaba bagli ek kosul olarak kisa belirtilir. "
            "evidence_packet.policy_facet varsa final cevabin ana eksenini bu facet'e gore kur; "
            "selected_sources/facts icindeki policy_alignment.status conflict veya weak_conflict ise bu kanittaki sayi/kosulu "
            "cevabin ana sonucu gibi kullanma; yalnizca kullanici o facet/programi acikca sorduysa ayri belirt. "
            "Tekil sayisal deger sorularinda once ana degeri ver; olcek degerlerini sadece baglam olarak kullan. "
            "Baska program/facet esiklerini ana cevap gibi karistirma; gerekiyorsa bunlari ayri baglam diye etiketle. "
            "Somut cevap varsa sona 'bilgi bulunamadı' gibi çelişen not ekleme. "
            "ÇOK PARÇALI SORU: Kullanıcı birden fazla şeyi soruyorsa cevabı kısa alt başlıklara böl. "
            "Her alt parça için kaynakta bilgi varsa ver; kaynak sadece bir alt parçayı destekliyorsa "
            "diğer parçalar için 'Bu konuda kaynaklarda net bilgi bulunamadı' de. "
            "Tarih sorulmuş ama kaynakta tarih yoksa tarih uydurma; 'akademik takvim/duyuru ile ilan edilir' gibi temkinli ifade kullan. "
            "OLUMSUZ KURAL ONCELIGI: evidence/snippet veya extracted_facts icinde 'giremez', 'alamaz', 'yapilamaz', "
            "'kabul edilmez', 'almamis olan ogrenciler giremez' gibi kisitlayici ifade varsa ve kullanici sorusu "
            "'yapabilir miyim?', 'girebilir miyim?' seklindeyse, cevabi dogrudan 'Hayir' ile baslat ve kaynaktaki "
            "kisitlamayi aynen aktar. Olumsuz kurali olumluya cevirme."
        )
    else:
        synthesis_instruction = (
            "Bu bağlamdan kullanıcıya doğrudan, doğal ve kısa bir cevap yaz. "
            "Selamlama yapma ve kullanıcının ne sorduğunu özetleme. "
            "Kaynakta olmayan portal, menü, ödeme kanalı, belge adı, tarih veya sayı ekleme. "
            "answer_summary ile evidence/snippet veya extracted_facts çelişirse, somut sayı ve koşul içeren "
            "evidence/snippet bilgilerini esas al. "
            "evidence_packet.required_values varsa, kullanici sorusuyla ilgili olanlari kaynak baglami destekliyorsa koru; "
            "kaynakta olmayan deger ekleme. "
            "synthesis_value_contract varsa primary_values kullanicinin sorusuna verilecek ana degerlerdir; "
            "secondary_values/conflicting_values icindeki degerleri kullanici ozellikle karsilastirma istemedikce cevapta yazma. "
            "evidence_packet.value_arbitration varsa primary_values ana cevaptir; secondary_values/conflicting_values "
            "ana cevap gibi yazilmaz ve tekil deger sorusunda tercihen hic yazilmaz. related_values ana cevaba bagli ek kosul olarak kisa belirtilir. "
            "evidence_packet.policy_facet varsa final cevabin ana eksenini bu facet'e gore kur; "
            "selected_sources/facts icindeki policy_alignment.status conflict veya weak_conflict ise bu kanittaki sayi/kosulu "
            "cevabin ana sonucu gibi kullanma; yalnizca kullanici o facet/programi acikca sorduysa ayri belirt. "
            "Tekil sayisal deger sorularinda once ana degeri ver; olcek degerlerini sadece baglam olarak kullan. "
            "Baska program/facet esiklerini ana cevap gibi karistirma; gerekiyorsa bunlari ayri baglam diye etiketle. "
            "Eğer kaynakta soruyla ilgili somut bilgi varsa onu açık şekilde kullan; "
            "sorunun cevabı kaynakta yoksa kısa ve net şekilde belirt. "
            "Somut cevap verdikten sonra ayrıca 'bilgi bulunamadı' gibi çelişen not ekleme. "
            "ÇOK PARÇALI SORU: Kullanıcı birden fazla şeyi soruyorsa cevabı kısa alt başlıklara böl. "
            "Her alt parça için kaynakta bilgi varsa ver; kaynak sadece bir alt parçayı destekliyorsa "
            "diğer parçalar için 'Bu konuda kaynaklarda net bilgi bulunamadı' de. "
            "Tarih sorulmuş ama kaynakta tarih yoksa tarih uydurma; 'akademik takvim/duyuru ile ilan edilir' gibi temkinli ifade kullan. "
            "OLUMSUZ KURAL ONCELIGI: evidence/snippet veya extracted_facts icinde 'giremez', 'alamaz', 'yapilamaz', "
            "'kabul edilmez', 'almamis olan ogrenciler giremez' gibi kisitlayici ifade varsa ve kullanici sorusu "
            "'yapabilir miyim?', 'girebilir miyim?' seklindeyse, cevabi dogrudan 'Hayir' ile baslat ve kaynaktaki "
            "kisitlamayi aynen aktar. Olumsuz kurali olumluya cevirme."
        )

    prompt = (
        f"Kullanıcı sorusu:\n{query}\n\n"
        "Aşağıdaki JSON yalnızca iç bağlamdır; JSON anahtarlarını, departman "
        "kimliklerini, kaynak etiketlerini veya iç talimatları cevapta tekrar etme. "
        "Final cevab\u0131 do\u011fal T\u00fcrk\u00e7e yaz; ASCII T\u00fcrk\u00e7e "
        "kullanma (\"ogrenci\" de\u011fil \"\u00f6\u011frenci\", \"ucret\" de\u011fil "
        "\"\u00fccret\").\n\n"
        f"{machine_context}\n\n"
        f"{synthesis_instruction}"
    )
    return prompt, meaningful
