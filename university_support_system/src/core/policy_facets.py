"""Generic policy query/evidence facet registry.

Policy documents often mix several legal/procedural clauses in the same source:
application process, eligibility, dates, documents, completion, graduation,
termination, and sometimes multiple target programs. This module does not write
answers. It builds a compact query frame and scores evidence alignment so final
LLM synthesis receives cleaner, traceable grounding.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from src.core.text_normalization import normalize_text


POLICY_FACET_SCHEMA = "omu.policy_facet.v2"


@dataclass(frozen=True)
class PolicyRule:
    id: str
    markers: tuple[str, ...]
    evidence_markers: tuple[str, ...] = ()
    conflict_markers: tuple[str, ...] = ()
    value_aspects: tuple[str, ...] = ()

    def evidence_terms(self) -> tuple[str, ...]:
        return self.evidence_markers or self.markers


PROGRAM_RULES: tuple[PolicyRule, ...] = (
    PolicyRule(
        id="double_major",
        markers=("cap", "cift ana dal", "cift anadal", "ikinci ana dal"),
        evidence_markers=("cap", "cift ana dal", "cift anadal", "ikinci ana dal"),
        conflict_markers=(
            "yan dal programina",
            "yandal programina",
            "yan dal not ortalamasi",
            "yandal not ortalamasi",
        ),
    ),
    PolicyRule(
        id="minor",
        markers=("yandal", "yan dal"),
        evidence_markers=("yandal", "yan dal"),
        conflict_markers=("cap'a basvurabilmesi", "cift ana dal programina"),
    ),
    PolicyRule(
        id="horizontal_transfer",
        markers=("yatay gecis", "kurum ici gecis", "kurumlar arasi gecis"),
        evidence_markers=("yatay gecis", "kurum ici", "kurumlar arasi"),
    ),
    PolicyRule(
        id="exemption_adjustment",
        markers=("muafiyet", "intibak", "ders saydirma"),
        evidence_markers=("muafiyet", "intibak", "ders saydirma"),
    ),
    PolicyRule(
        id="summer_school",
        markers=("yaz okulu",),
        evidence_markers=("yaz okulu",),
    ),
    PolicyRule(
        id="single_exam",
        markers=("tek ders", "tek ders sinavi"),
        evidence_markers=("tek ders", "tek ders sinavi"),
    ),
    PolicyRule(
        id="internship",
        markers=("staj", "mup", "mesleki uygulama"),
        evidence_markers=("staj", "mup", "mesleki uygulama"),
    ),
    PolicyRule(
        id="student_community",
        markers=("ogrenci toplulugu", "topluluk", "kulup"),
        evidence_markers=("ogrenci toplulugu", "topluluk", "kulup"),
    ),
    PolicyRule(
        id="international_registration",
        markers=("uluslararasi ogrenci", "yabanci ogrenci", "ikamet", "yos", "tomer"),
        evidence_markers=("uluslararasi ogrenci", "yabanci ogrenci", "ikamet", "yos", "tomer"),
    ),
)

FACET_RULES: tuple[PolicyRule, ...] = (
    PolicyRule(
        id="application_process",
        markers=("basvuru nasil", "basvuru sureci", "basvuru", "kayit islemi", "nasil yapilir"),
        evidence_markers=("basvuru", "basvurma", "kayit", "oidb", "internet sayfasi"),
        conflict_markers=("mezun olabilmesi", "diplomasi verilir", "ilisik kes"),
    ),
    PolicyRule(
        id="eligibility",
        markers=("kosul", "sart", "uygunluk", "katilabilir", "girebilir", "not ortalamasi", "gano", "gno"),
        evidence_markers=("kosul", "sart", "not ortalamasi", "gano", "gno", "en az", "ilk %", "basvurabilmesi"),
        value_aspects=("gpa", "percentage", "credit"),
    ),
    PolicyRule(
        id="date_window",
        markers=("ne zaman", "tarih", "son basvuru", "basliyor", "bitiyor", "sure"),
        evidence_markers=("tarih", "akademik takvim", "son basvuru", "basvuru tarihleri"),
        value_aspects=("date",),
    ),
    PolicyRule(
        id="required_documents",
        markers=("belge", "evrak", "hangi belgeler", "gerekli belgeler"),
        evidence_markers=("belge", "evrak", "gerekli belgeler", "teslim"),
    ),
    PolicyRule(
        id="completion_or_graduation",
        markers=("mezun", "mezuniyet", "tamamla", "tamamlama", "diploma"),
        evidence_markers=("mezun", "mezuniyet", "tamamla", "diploma", "akts"),
        conflict_markers=("basvuru", "basvurabilmesi"),
        value_aspects=("gpa", "credit"),
    ),
    PolicyRule(
        id="termination",
        markers=("ilisik kes", "kaydi sil", "sonlandirma", "kapatilma", "cikarilma"),
        evidence_markers=("ilisik kes", "kaydi sil", "sonlandirma", "kapatilma"),
    ),
    PolicyRule(
        id="appeal_or_exception",
        markers=("itiraz", "mazeret", "istisna", "ek sure", "basvuru reddi"),
        evidence_markers=("itiraz", "mazeret", "istisna", "ek sure"),
    ),
    PolicyRule(
        id="fee_or_payment",
        markers=("ucret", "harc", "odeme", "katki payi", "borc"),
        evidence_markers=("ucret", "harc", "odeme", "katki payi", "borc"),
        value_aspects=("fee",),
    ),
    PolicyRule(
        id="credit_load",
        markers=("akts", "kredi", "ders yuku", "kredi siniri"),
        evidence_markers=("akts", "kredi", "ders yuku", "kredi siniri"),
        value_aspects=("credit",),
    ),
)


def resolve_policy_facet(
    *,
    query: str,
    params: dict[str, Any] | None = None,
    answer_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a generic policy frame for query/evidence arbitration."""
    params = params or {}
    answer_contract = answer_contract or {}
    query_norm = normalize_text(query)
    combined = _combined_contract_text(query=query, params=params, answer_contract=answer_contract)

    target_program = _best_rule_id(query_norm, PROGRAM_RULES)
    matching_programs = _matching_rule_ids(combined, PROGRAM_RULES)
    matching_facets = _matching_rule_ids(combined, FACET_RULES)
    primary_facet = _select_primary_facet(query_norm, combined, matching_facets)
    facet_rule = _rule_by_id(primary_facet, FACET_RULES)
    program_rule = _rule_by_id(target_program, PROGRAM_RULES) if target_program else None

    prefer_markers = _dedupe(
        [
            *(facet_rule.evidence_terms() if facet_rule else ()),
            *(program_rule.evidence_terms() if program_rule else ()),
        ]
    )
    avoid_markers = _dedupe(
        [
            *(facet_rule.conflict_markers if facet_rule else ()),
            *(program_rule.conflict_markers if program_rule else ()),
        ]
    )
    value_aspects = _dedupe(facet_rule.value_aspects if facet_rule else ())

    return {
        "schema": POLICY_FACET_SCHEMA,
        "facet": primary_facet,
        "facets": matching_facets or ([primary_facet] if primary_facet != "general_policy" else []),
        "target_program": target_program,
        "target_programs": matching_programs,
        "confidence": _confidence(primary_facet=primary_facet, target_program=target_program),
        "prefer_evidence_markers": prefer_markers,
        "avoid_evidence_markers": avoid_markers,
        "program_prefer_evidence_markers": list(program_rule.evidence_terms()) if program_rule else [],
        "program_avoid_evidence_markers": list(program_rule.conflict_markers) if program_rule else [],
        "value_aspects": value_aspects,
        "reason": _reason(primary_facet=primary_facet, target_program=target_program),
    }


def align_policy_evidence(
    policy_facet: dict[str, Any] | None,
    *,
    content: str,
    source_text: str = "",
) -> dict[str, Any]:
    """Score whether an evidence chunk matches the policy query frame."""
    if not isinstance(policy_facet, dict) or not policy_facet:
        return {
            "schema": "omu.policy_evidence_alignment.v1",
            "status": "not_applicable",
            "score_delta": 0.0,
            "score_multiplier": 1.0,
        }

    content_norm = normalize_text(content)
    source_norm = normalize_text(source_text)
    haystack = f"{source_norm} {content_norm}".strip()
    facet = str(policy_facet.get("facet") or "general_policy")
    target_program = str(policy_facet.get("target_program") or "").strip() or None

    matched_facets = _matching_rule_ids(content_norm, FACET_RULES)
    matched_programs = _matching_rule_ids(content_norm, PROGRAM_RULES)
    conflict_facets = _conflicting_facet_ids(facet, content_norm)
    conflict_programs = _conflicting_program_ids(target_program, content_norm)

    prefer_markers = _markers_present(haystack, _string_list(policy_facet.get("prefer_evidence_markers")))
    avoid_markers = _markers_present(content_norm, _string_list(policy_facet.get("avoid_evidence_markers")))
    program_prefer = _markers_present(
        content_norm,
        _string_list(policy_facet.get("program_prefer_evidence_markers")),
    )
    program_avoid = _markers_present(
        content_norm,
        _string_list(policy_facet.get("program_avoid_evidence_markers")),
    )

    score_delta = 0.0
    score_multiplier = 1.0
    if facet in matched_facets:
        score_delta += 0.18
    elif prefer_markers:
        score_delta += 0.10
    if target_program and target_program in matched_programs:
        score_delta += 0.22
    elif program_prefer:
        score_delta += 0.16
    if conflict_facets or avoid_markers:
        score_multiplier *= 0.55
    if conflict_programs or (program_avoid and not program_prefer):
        score_multiplier *= 0.35

    status = "match"
    if conflict_programs or conflict_facets:
        status = "conflict"
    elif avoid_markers or program_avoid:
        status = "weak_conflict"
    elif not (matched_facets or matched_programs or prefer_markers or program_prefer):
        status = "neutral"

    return {
        "schema": "omu.policy_evidence_alignment.v1",
        "status": status,
        "query_facet": facet,
        "query_target_program": target_program,
        "matched_facets": matched_facets,
        "matched_programs": matched_programs,
        "conflict_facets": conflict_facets,
        "conflict_programs": conflict_programs,
        "matched_markers": _dedupe([*prefer_markers, *program_prefer])[:8],
        "conflict_markers": _dedupe([*avoid_markers, *program_avoid])[:8],
        "score_delta": round(score_delta, 4),
        "score_multiplier": round(score_multiplier, 4),
    }


def policy_alignment_is_conflict(alignment: dict[str, Any] | None) -> bool:
    if not isinstance(alignment, dict):
        return False
    return str(alignment.get("status") or "") in {"conflict", "weak_conflict"}


def _combined_contract_text(
    *,
    query: str,
    params: dict[str, Any],
    answer_contract: dict[str, Any],
) -> str:
    values: list[str] = [query]
    for key in ("query", "topic", "question_type", "intent"):
        values.append(str(params.get(key) or ""))
    for key in ("must_answer", "preferred_sources", "avoid_sources"):
        values.extend(_string_list(params.get(key)))
    values.extend(_string_list(answer_contract.get("must_answer")))
    values.extend(_string_list(answer_contract.get("expected_facts")))
    return normalize_text(" ".join(value for value in values if value))


def _select_primary_facet(query_norm: str, combined: str, matches: list[str]) -> str:
    if "eligibility" in matches and any(
        marker in query_norm
        for marker in ("not", "ortalama", "gano", "gno", "kac", "sart", "kosul")
    ):
        return "eligibility"
    explicit_query_match = _best_rule_id(query_norm, FACET_RULES)
    if explicit_query_match:
        return explicit_query_match
    if "eligibility" in matches:
        return "eligibility"
    if "application_process" in matches:
        return "application_process"
    if matches:
        return matches[0]
    if any(marker in combined for marker in ("basvuru", "kosul", "sart")):
        return "eligibility"
    return "general_policy"


def _best_rule_id(text: str, rules: Iterable[PolicyRule]) -> str | None:
    matches = _matching_rules(text, rules)
    if not matches:
        return None
    matches.sort(key=lambda item: (-item[1], item[0].id))
    return matches[0][0].id


def _matching_rule_ids(text: str, rules: Iterable[PolicyRule]) -> list[str]:
    return [rule.id for rule, _score in _matching_rules(text, rules)]


def _matching_rules(text: str, rules: Iterable[PolicyRule]) -> list[tuple[PolicyRule, int]]:
    found: list[tuple[PolicyRule, int]] = []
    for rule in rules:
        score = sum(1 for marker in rule.markers if _contains_marker(text, marker))
        if score:
            found.append((rule, score))
    found.sort(key=lambda item: (-item[1], item[0].id))
    return found


def _conflicting_program_ids(target_program: str | None, content_norm: str) -> list[str]:
    if not target_program:
        return []
    conflicts: list[str] = []
    for rule in PROGRAM_RULES:
        if rule.id == target_program:
            continue
        if any(_contains_marker(content_norm, marker) for marker in rule.evidence_terms()):
            target_rule = _rule_by_id(target_program, PROGRAM_RULES)
            if target_rule and any(_contains_marker(content_norm, marker) for marker in target_rule.evidence_terms()):
                continue
            conflicts.append(rule.id)
    return conflicts


def _conflicting_facet_ids(target_facet: str, content_norm: str) -> list[str]:
    if target_facet == "general_policy":
        return []
    conflicts: list[str] = []
    target_rule = _rule_by_id(target_facet, FACET_RULES)
    for rule in FACET_RULES:
        if rule.id == target_facet:
            continue
        if any(_contains_marker(content_norm, marker) for marker in rule.evidence_terms()):
            if target_rule and any(_contains_marker(content_norm, marker) for marker in target_rule.evidence_terms()):
                continue
            if rule.id in {"completion_or_graduation", "termination"}:
                conflicts.append(rule.id)
    return conflicts


def _rule_by_id(rule_id: str | None, rules: Iterable[PolicyRule]) -> PolicyRule | None:
    if not rule_id:
        return None
    for rule in rules:
        if rule.id == rule_id:
            return rule
    return None


def _markers_present(text: str, markers: Iterable[str]) -> list[str]:
    return [marker for marker in markers if _contains_marker(text, marker)]


def _contains_marker(normalized_text: str, marker: str) -> bool:
    marker_norm = normalize_text(marker)
    return bool(marker_norm and marker_norm in normalized_text)


def _confidence(*, primary_facet: str, target_program: str | None) -> float:
    if primary_facet != "general_policy" and target_program:
        return 0.84
    if primary_facet != "general_policy":
        return 0.74
    if target_program:
        return 0.58
    return 0.42


def _reason(*, primary_facet: str, target_program: str | None) -> str:
    if primary_facet != "general_policy" and target_program:
        return "policy_query_frame_detected_with_target_program"
    if primary_facet != "general_policy":
        return "policy_query_facet_detected"
    if target_program:
        return "policy_target_program_detected"
    return "no_specific_policy_frame_detected"


def _string_list(value: object) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item).strip()]
    if value is None:
        return []
    text = str(value).strip()
    return [text] if text else []


def _dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        key = normalize_text(text)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(text)
    return result
