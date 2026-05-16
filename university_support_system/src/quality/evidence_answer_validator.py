"""Deterministic evidence-to-answer validation.

This module is intentionally non-LLM. It checks whether a final answer
preserves high-signal factual values already present in the selected evidence.
When it finds a risky mismatch, the orchestrator can escalate to the existing
main judge instead of introducing a second judge layer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Sequence, TypeVar

from src.core.policy_facets import align_policy_evidence, policy_alignment_is_conflict
from src.core.text_normalization import collapse_whitespace, normalize_text
from src.db.schemas import DepartmentResponse
from src.quality.evidence import EVIDENCE_STOPWORDS, extract_factual_claims

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_VALUE_RE = re.compile(r"(?:%\s*\d+(?:[,.]\d+)?|\byuzde\s+\d+(?:[,.]\d+)?\b|\b\d+(?:[,.]\d+)?\b)")
_MONTH_RE = re.compile(
    r"\b(?:ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)\b"
)
_THRESHOLD_VALUE_RE = re.compile(
    r"\b(?:en\s+az|en\s+cok|asgari|azami|minimum|maksimum)\s+"
    r"(%?\s*\d+(?:[,.]\d+)?)\b"
)
_NO_INFO_RE = re.compile(
    r"\b(?:bilgi\s+bulunamad|bulunamadi|belirtilmemis|net\s+degil"
    r"|net\s+bilgi\s+yok|yer\s+almiyor|kaynakta\s+.*?\s+yok"
    r"|kaynaklarda\s+.*?\s+yok|tam\s+olarak\s+.*?net\s+degil)\b"
)

_VALUE_QUERY_MARKERS = (
    "kac",
    "ne kadar",
    "tarih",
    "ne zaman",
    "basliyor",
    "bitiyor",
    "son basvuru",
    "sure",
    "gun",
    "hafta",
    "ay",
    "yil",
    "ucret",
    "harc",
    "katki payi",
    "tl",
    "lira",
    "akts",
    "ects",
    "kredi",
    "not",
    "ortalama",
    "gno",
    "gano",
    "yuzde",
    "oran",
)
_VALUE_CONTRACT_MARKERS = _VALUE_QUERY_MARKERS + (
    "sayi",
    "sayisal",
    "deger",
    "tutar",
    "kosul",
    "sart",
    "threshold",
    "date",
    "amount",
    "fee",
    "credit",
    "gpa",
)
_VALUE_CAPABILITIES = frozenset({
    "calendar.academic_date",
    "course.detail",
    "finance.tuition_fee",
})

_ASPECT_MARKERS: dict[str, tuple[str, ...]] = {
    "gpa": ("not", "ortalama", "gno", "gano"),
    "fee": ("ucret", "harc", "katki payi", "tl", "lira", "odeme"),
    "course_credit": ("akts", "ects", "kredi"),
    "date": ("tarih", "ne zaman", "basliyor", "bitiyor", "son basvuru", "donem"),
    "percentage": ("%", "yuzde", "oran", "ilk"),
}
_SOURCE_FAMILY_MARKERS = (
    ("academic_calendar", ("akademik_takvim", "akademik takvim", "calendar")),
    ("tuition_fee_catalog", ("tuition", "harc", "ucret", "katki payi")),
    ("curriculum_catalog", ("curriculum", "mufredat", "ders plani", "akts")),
    ("student_affairs_policy", ("yonetmelik", "yonerge", "cap", "cift anadal", "ogrenci_isleri")),
    ("international_policy", ("uluslararasi", "international", "yabanci")),
)
_PROGRAM_SPECIFIC_MARKERS: dict[str, tuple[str, ...]] = {
    "double_major": ("cap", "cift ana dal", "cift anadal", "ikinci ana dal", "ana dal"),
    "minor": ("yandal", "yan dal"),
    "horizontal_transfer": ("yatay gecis", "kurum ici", "kurumlar arasi"),
    "exemption_adjustment": ("muafiyet", "intibak", "ders saydirma"),
    "summer_school": ("yaz okulu",),
    "single_exam": ("tek ders",),
    "internship": ("staj", "mup", "mesleki uygulama"),
}
_POLICY_DATE_DOMAIN_QUERY_MARKERS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (
        ("pedagojik formasyon", "formasyon egitimi", "formasyon sertifika", "mezunlar icin"),
        ("pedagojik", "formasyon", "sertifika", "mezun"),
    ),
    (
        ("uluslararasi", "uluslararas", "international", "yabanci", "erasmus", "degisim", "protokol"),
        ("uluslararasi", "uluslararas", "international", "yabanci", "ikamet", "kabul", "erasmus", "degisim", "protokol"),
    ),
)
_T = TypeVar("_T")


@dataclass(frozen=True)
class EvidenceNumber:
    raw: str
    canonical: str
    aliases: tuple[str, ...]
    is_percent: bool
    is_decimal: bool
    position: int


@dataclass(frozen=True)
class RequiredClaim:
    claim: str
    source: str | None
    required_values: tuple[EvidenceNumber, ...]
    reason: str
    value_role: str = "answer_threshold"
    policy_alignment_status: str | None = None
    policy_target_program: str | None = None
    policy_matched_programs: tuple[str, ...] = ()
    arbitration_score: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "claim": self.claim[:400],
            "source": self.source,
            "required_values": [value.raw for value in self.required_values],
            "reason": self.reason,
            "value_role": self.value_role,
            "policy_alignment_status": self.policy_alignment_status,
            "policy_target_program": self.policy_target_program,
            "policy_matched_programs": list(self.policy_matched_programs),
            "arbitration_score": self.arbitration_score,
        }


@dataclass(frozen=True)
class EvidenceClaimCandidate:
    claim: str
    context: str
    source: str | None
    policy_alignment: dict[str, object] | None = None
    policy_facet: dict[str, object] | None = None


@dataclass(frozen=True)
class AnswerValidationResult:
    status: str = "pass"  # pass | check | fail
    risk_level: str = "none"  # none | medium | high
    reason: str = "not_applicable"
    requires_judge: bool = False
    evidence_claim_count: int = 0
    required_claims: tuple[RequiredClaim, ...] = field(default_factory=tuple)
    missing_values: tuple[str, ...] = field(default_factory=tuple)
    conflicting_values: tuple[str, ...] = field(default_factory=tuple)
    answer_values: tuple[str, ...] = field(default_factory=tuple)
    mode: str = "shadow"
    enforceable_by_contract: bool = False
    value_arbitration: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "risk_level": self.risk_level,
            "reason": self.reason,
            "requires_judge": self.requires_judge,
            "mode": self.mode,
            "enforceable_by_contract": self.enforceable_by_contract,
            "evidence_claim_count": self.evidence_claim_count,
            "required_claims": [claim.to_dict() for claim in self.required_claims[:5]],
            "missing_values": list(self.missing_values),
            "conflicting_values": list(self.conflicting_values),
            "answer_values": list(self.answer_values),
            "value_arbitration": dict(self.value_arbitration),
        }

    def to_judge_context(self) -> str:
        if self.status == "pass":
            return ""
        lines = [
            f"Deterministic validator status: {self.status}",
            f"Reason: {self.reason}",
        ]
        if self.missing_values:
            lines.append(f"Missing evidence values in answer: {', '.join(self.missing_values)}")
        if self.conflicting_values:
            lines.append(f"Potential conflicting answer values: {', '.join(self.conflicting_values)}")
        if self.required_claims:
            lines.append("Supporting evidence claims:")
            for claim in self.required_claims[:3]:
                values = ", ".join(value.raw for value in claim.required_values)
                source = f" ({claim.source})" if claim.source else ""
                role = f" role={claim.value_role}" if claim.value_role else ""
                lines.append(f"- {collapse_whitespace(claim.claim)[:260]} | required={values}{role}{source}")
        if self.value_arbitration:
            primary = self.value_arbitration.get("primary_values") or []
            secondary = self.value_arbitration.get("secondary_values") or []
            conflicting = self.value_arbitration.get("conflicting_values") or []
            if primary:
                lines.append(f"Primary evidence values: {', '.join(str(item) for item in primary)}")
            if secondary:
                lines.append(f"Secondary evidence values: {', '.join(str(item) for item in secondary)}")
            if conflicting:
                lines.append(f"Conflicting evidence values: {', '.join(str(item) for item in conflicting)}")
        return "\n".join(lines)


def validate_evidence_answer(
    *,
    query: str,
    answer: str,
    responses: Sequence[DepartmentResponse],
    mode: str = "shadow",
) -> AnswerValidationResult:
    """Validate final answer against selected evidence without calling an LLM."""
    if mode == "off":
        return AnswerValidationResult(reason="disabled", mode=mode)

    enforceable_by_contract = contracts_require_value_preservation(responses)
    normalized_query = normalize_text(query)
    if not _query_needs_value_check(normalized_query):
        return AnswerValidationResult(
            reason="query_does_not_require_value_check",
            mode=mode,
            enforceable_by_contract=enforceable_by_contract,
        )

    claims = list(_collect_evidence_claims(responses))
    if not claims:
        return AnswerValidationResult(
            reason="no_evidence_claims",
            mode=mode,
            enforceable_by_contract=enforceable_by_contract,
        )

    query_terms = _query_terms(normalized_query)
    query_aspects = _aspects(normalized_query)
    required_claims: list[RequiredClaim] = []
    secondary_values: list[str] = []
    conflicting_evidence_values: list[str] = []
    for candidate in claims:
        effective_alignment = _effective_policy_alignment(candidate)
        normalized_claim = normalize_text(candidate.claim)
        normalized_context = normalize_text(candidate.context or candidate.claim)
        if not _claim_is_relevant(
            normalized_context,
            query_terms=query_terms,
            query_aspects=query_aspects,
        ):
            continue
        required_values, reason = _required_values_for_claim(
            normalized_query=normalized_query,
            normalized_claim=normalized_claim,
        )
        if required_values:
            if reason == "date_or_time_value" and not _policy_date_claim_is_required(
                candidate=candidate,
                normalized_query=normalized_query,
                normalized_claim=normalized_claim,
                normalized_context=normalized_context,
                policy_alignment=effective_alignment,
            ):
                secondary_values.extend(value.raw for value in required_values)
                continue
            if policy_alignment_is_conflict(effective_alignment):
                target = (
                    conflicting_evidence_values
                    if str((effective_alignment or {}).get("status") or "") == "conflict"
                    else secondary_values
                )
                target.extend(value.raw for value in required_values)
                continue
            required_claims.append(
                RequiredClaim(
                    claim=collapse_whitespace(candidate.claim),
                    source=candidate.source,
                    required_values=tuple(required_values),
                    reason=reason,
                    value_role=_value_role_for_required_claim(reason, effective_alignment),
                    policy_alignment_status=str((effective_alignment or {}).get("status") or "") or None,
                    policy_target_program=str((effective_alignment or {}).get("query_target_program") or "") or None,
                    policy_matched_programs=tuple(
                        str(item)
                        for item in ((effective_alignment or {}).get("matched_programs") or [])
                        if str(item).strip()
                    ),
                    arbitration_score=_required_claim_arbitration_score(
                        normalized_claim=normalized_claim,
                        normalized_context=normalized_context,
                        policy_alignment=effective_alignment,
                        reason=reason,
                    ),
                )
            )

    required_claims, demoted_values = _arbitrate_competing_required_claims(required_claims)
    secondary_values.extend(demoted_values)
    arbitration = _build_value_arbitration(
        required_claims,
        secondary_values=secondary_values,
        conflicting_values=conflicting_evidence_values,
    )
    if not required_claims:
        return AnswerValidationResult(
            reason="no_query_relevant_required_values",
            evidence_claim_count=len(claims),
            mode=mode,
            enforceable_by_contract=enforceable_by_contract,
            value_arbitration=arbitration,
        )

    answer_numbers = _extract_numbers(normalize_text(answer))
    normalized_answer = normalize_text(answer)
    answer_aliases = {alias for value in answer_numbers for alias in value.aliases}
    required_values = _dedupe(
        value for claim in required_claims for value in claim.required_values
    )
    evidence_aliases = {alias for value in required_values for alias in value.aliases}
    missing = [
        value.raw
        for value in required_values
        if not (set(value.aliases) & answer_aliases)
    ]
    answer_value_labels = tuple(_dedupe(value.raw for value in answer_numbers))

    if not missing:
        if _NO_INFO_RE.search(normalize_text(answer)):
            return AnswerValidationResult(
                status="fail",
                risk_level="high",
                reason="answer_denies_available_evidence",
                requires_judge=True,
                mode=mode,
                enforceable_by_contract=enforceable_by_contract,
                evidence_claim_count=len(claims),
                required_claims=tuple(required_claims),
                missing_values=tuple(),
                answer_values=answer_value_labels,
                value_arbitration=arbitration,
            )
        return AnswerValidationResult(
            status="pass",
            risk_level="none",
            reason="required_values_preserved",
            mode=mode,
            enforceable_by_contract=enforceable_by_contract,
            evidence_claim_count=len(claims),
            required_claims=tuple(required_claims),
            answer_values=answer_value_labels,
            value_arbitration=arbitration,
        )

    conflicting_values = [
        value.raw
        for value in answer_numbers
        if not (set(value.aliases) & evidence_aliases)
        and not _answer_value_is_allowed_context(
            normalized_answer=normalized_answer,
            value=value,
            query_aspects=query_aspects,
        )
    ]
    conflicting_values = list(_dedupe(conflicting_values))
    no_info_answer = bool(_NO_INFO_RE.search(normalize_text(answer)))
    status = "fail" if no_info_answer or conflicting_values else "check"
    reason = (
        "answer_denies_available_evidence"
        if no_info_answer
        else "answer_conflicts_with_evidence_values"
        if conflicting_values
        else "answer_missing_required_evidence_values"
    )
    return AnswerValidationResult(
        status=status,
        risk_level="high" if status == "fail" else "medium",
        reason=reason,
        requires_judge=True,
        mode=mode,
        enforceable_by_contract=enforceable_by_contract,
        evidence_claim_count=len(claims),
        required_claims=tuple(required_claims),
        missing_values=tuple(_dedupe(missing)),
        conflicting_values=tuple(conflicting_values),
        answer_values=answer_value_labels,
        value_arbitration=arbitration,
    )


def should_enforce_validation(result: AnswerValidationResult) -> bool:
    """Return whether a validation result may force the main judge."""
    return (
        result.mode == "contract_enforce"
        and result.enforceable_by_contract
        and result.requires_judge
    )


def extract_value_labels(text: str) -> list[str]:
    """Return stable value labels found in text for evidence packet diagnostics."""
    return list(_dedupe(value.raw for value in _extract_numbers(normalize_text(text))))


def contracts_require_value_preservation(responses: Sequence[DepartmentResponse]) -> bool:
    """Detect whether planner/answer contracts explicitly need value preservation."""
    for response in responses:
        for contract in _iter_contracts(response):
            if _contract_requires_value_preservation(contract):
                return True
    return False


def _query_needs_value_check(normalized_query: str) -> bool:
    return any(_contains_marker(normalized_query, marker) for marker in _VALUE_QUERY_MARKERS)


def _query_terms(normalized_query: str) -> set[str]:
    return {
        token
        for token in _TOKEN_RE.findall(normalized_query)
        if len(token) > 2 and token not in EVIDENCE_STOPWORDS
    }


def _aspects(normalized_text: str) -> set[str]:
    return {
        aspect
        for aspect, markers in _ASPECT_MARKERS.items()
        if any(_contains_marker(normalized_text, marker) for marker in markers)
    }


def _contains_marker(normalized_text: str, marker: str) -> bool:
    normalized_marker = normalize_text(marker)
    if not normalized_marker:
        return False
    if len(normalized_marker) <= 3 and normalized_marker.isalnum():
        return bool(re.search(rf"\b{re.escape(normalized_marker)}\b", normalized_text))
    return normalized_marker in normalized_text


def _claim_is_relevant(
    normalized_claim: str,
    *,
    query_terms: set[str],
    query_aspects: set[str],
) -> bool:
    if not query_terms and not query_aspects:
        return True
    claim_terms = {
        token
        for token in _TOKEN_RE.findall(normalized_claim)
        if len(token) > 2 and token not in EVIDENCE_STOPWORDS
    }
    if query_terms & claim_terms:
        return True
    claim_aspects = _aspects(normalized_claim)
    return bool(query_aspects & claim_aspects)


def _collect_evidence_claims(
    responses: Sequence[DepartmentResponse],
) -> Iterable[EvidenceClaimCandidate]:
    seen: set[str] = set()
    for response in responses:
        metadata = response.metadata if isinstance(response.metadata, dict) else {}
        packet = metadata.get("evidence_packet") if isinstance(metadata, dict) else None
        packet_policy_facet = (
            packet.get("policy_facet")
            if isinstance(packet, dict) and isinstance(packet.get("policy_facet"), dict)
            else None
        )
        if isinstance(packet, dict):
            for fact in packet.get("facts") or []:
                claim, source, policy_alignment, context = _claim_from_packet_item(fact)
                if claim:
                    normalized = normalize_text(claim)
                    if normalized not in seen:
                        seen.add(normalized)
                        yield EvidenceClaimCandidate(
                            claim=claim,
                            context=context or claim,
                            source=source,
                            policy_alignment=policy_alignment,
                            policy_facet=packet_policy_facet,
                        )
            for source_item in packet.get("selected_sources") or []:
                claim, source, policy_alignment = _snippet_from_packet_source(source_item)
                if claim:
                    normalized = normalize_text(claim)
                    if normalized not in seen:
                        seen.add(normalized)
                        yield EvidenceClaimCandidate(
                            claim=claim,
                            context=claim,
                            source=source,
                            policy_alignment=policy_alignment,
                            policy_facet=packet_policy_facet,
                        )

        for source in response.sources[:3]:
            source_name = str(
                source.metadata.get("source")
                or source.metadata.get("filename")
                or source.metadata.get("relative_path")
                or ""
            ).strip() or None
            source_alignment = (
                source.metadata.get("policy_alignment")
                if isinstance(source.metadata.get("policy_alignment"), dict)
                else None
            )
            source_policy_facet = (
                source.metadata.get("policy_facet")
                if isinstance(source.metadata.get("policy_facet"), dict)
                else None
            )
            extracted = extract_factual_claims(source.content)
            if not extracted and _MONTH_RE.search(normalize_text(source.content)):
                extracted = [collapse_whitespace(source.content)[:500]]
            for claim in extracted[:8]:
                normalized = normalize_text(claim)
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    yield EvidenceClaimCandidate(
                        claim=claim,
                        context=source.content,
                        source=source_name,
                        policy_alignment=source_alignment,
                        policy_facet=source_policy_facet,
                    )


def _iter_contracts(response: DepartmentResponse) -> Iterable[dict]:
    metadata = response.metadata if isinstance(response.metadata, dict) else {}
    packet = metadata.get("evidence_packet") if isinstance(metadata, dict) else None
    candidates = [metadata, packet] if isinstance(packet, dict) else [metadata]
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        for key in ("answer_contract", "evidence_contract", "plan_decision"):
            value = candidate.get(key)
            if isinstance(value, dict):
                yield value
        planner = candidate.get("capability_planner")
        if isinstance(planner, dict):
            action = planner.get("action")
            if isinstance(action, dict):
                yield action


def _contract_requires_value_preservation(contract: dict) -> bool:
    capability = str(contract.get("capability") or "").strip()
    if capability in _VALUE_CAPABILITIES:
        return True
    if contract.get("preserve_values") is True or contract.get("requires_value_preservation") is True:
        return True
    if isinstance(contract.get("required_values"), list) and contract.get("required_values"):
        return True
    text_parts: list[str] = []
    for key in (
        "must_answer",
        "expected_facts",
        "key_facts",
        "required_facts",
        "preferred_sources",
        "topic",
        "intent",
        "question_type",
    ):
        value = contract.get(key)
        if isinstance(value, (list, tuple, set)):
            text_parts.extend(str(item) for item in value)
        elif value is not None:
            text_parts.append(str(value))
    haystack = normalize_text(" ".join(text_parts))
    return any(marker in haystack for marker in _VALUE_CONTRACT_MARKERS)


def _claim_from_packet_item(
    item: object,
) -> tuple[str | None, str | None, dict[str, object] | None, str | None]:
    if isinstance(item, dict):
        claim = str(
            item.get("claim")
            or item.get("text")
            or item.get("fact")
            or item.get("snippet")
            or ""
        ).strip()
        source = str(item.get("source") or item.get("source_name") or "").strip() or None
        alignment = item.get("policy_alignment") if isinstance(item.get("policy_alignment"), dict) else None
        context = str(item.get("support") or item.get("snippet") or item.get("context") or claim or "").strip()
        return claim or None, source, alignment, context or None
    text = str(item or "").strip()
    return text or None, None, None, text or None


def _snippet_from_packet_source(item: object) -> tuple[str | None, str | None, dict[str, object] | None]:
    if not isinstance(item, dict):
        text = str(item or "").strip()
        return text or None, None, None
    snippet = str(item.get("snippet") or item.get("content") or "").strip()
    source = str(item.get("source") or item.get("source_name") or "").strip() or None
    alignment = item.get("policy_alignment") if isinstance(item.get("policy_alignment"), dict) else None
    return snippet or None, source, alignment


def _effective_policy_alignment(candidate: EvidenceClaimCandidate) -> dict[str, object] | None:
    """Prefer claim-level policy alignment over chunk-level alignment."""
    existing = candidate.policy_alignment if isinstance(candidate.policy_alignment, dict) else None
    if policy_alignment_is_conflict(existing):
        return existing
    facet = candidate.policy_facet if isinstance(candidate.policy_facet, dict) else None
    if not facet:
        return existing

    claim_alignment = align_policy_evidence(
        facet,
        content=candidate.claim,
        source_text=candidate.source or "",
    )
    if policy_alignment_is_conflict(claim_alignment):
        return claim_alignment

    context = candidate.context or candidate.claim
    if context and normalize_text(context) != normalize_text(candidate.claim):
        context_alignment = align_policy_evidence(
            facet,
            content=context,
            source_text=candidate.source or "",
        )
        if policy_alignment_is_conflict(context_alignment):
            return context_alignment

    if existing:
        return existing
    return claim_alignment


def _value_role_for_required_claim(
    reason: str,
    policy_alignment: dict[str, object] | None,
) -> str:
    status = str((policy_alignment or {}).get("status") or "")
    if status == "weak_conflict":
        return "secondary_program_threshold"
    if status == "conflict":
        return "conflicting_threshold"
    if reason in {"gpa_threshold", "fee_value", "course_akts_value", "course_credit_value", "date_or_time_value"}:
        return "answer_threshold"
    if reason == "percentage_value":
        return "related_condition"
    return "supporting_value"


def _policy_date_claim_is_required(
    *,
    candidate: EvidenceClaimCandidate,
    normalized_query: str,
    normalized_claim: str,
    normalized_context: str,
    policy_alignment: dict[str, object] | None,
) -> bool:
    """Require policy dates only when the claim itself carries target context."""
    if policy_alignment_is_conflict(policy_alignment):
        return False
    source_family = infer_source_family(source=candidate.source, claim=normalized_context)
    if source_family == "academic_calendar":
        return True
    if _policy_date_domain_mismatches_query(
        source=candidate.source,
        normalized_context=normalized_context,
        normalized_query=normalized_query,
    ):
        return False
    if source_family == "international_policy" and not any(
        marker in normalized_query
        for marker in ("uluslararasi", "yabanci", "international", "erasmus", "degisim", "protokol")
    ):
        return False
    target_program = str((policy_alignment or {}).get("query_target_program") or "")
    target_markers = _PROGRAM_SPECIFIC_MARKERS.get(target_program, ())
    if target_markers and not any(
        _contains_marker(f"{normalized_claim} {normalized_context}", marker)
        for marker in target_markers
    ):
        return False
    if _looks_like_bare_date_or_duration(normalized_claim):
        return _policy_context_strongly_supports_date(
            normalized_query=normalized_query,
            normalized_context=normalized_context,
            policy_alignment=policy_alignment,
        )

    claim_terms = _query_terms(normalized_claim)
    query_terms = _query_terms(normalized_query)
    meaningful_overlap = {
        term for term in (claim_terms & query_terms)
        if term not in {"tarih", "zaman", "sure", "gun", "hafta", "basvuru", "yapmali"}
    }
    if meaningful_overlap:
        return True

    strong_process_markers = (
        "egitim ogretim",
        "ogretimin basladigi",
        "basladigi tarihten itibaren",
        "tarihten itibaren",
        "basvuru suresi",
        "basvuru tarih",
        "hafta icinde",
        "gun icinde",
        "son basvuru",
    )
    if any(marker in normalized_claim for marker in strong_process_markers):
        return True

    if target_markers and any(_contains_marker(normalized_claim, marker) for marker in target_markers):
        return True

    return False


def _policy_date_domain_mismatches_query(
    *,
    source: str | None,
    normalized_context: str,
    normalized_query: str,
) -> bool:
    haystack = normalize_text(f"{source or ''} {normalized_context}")
    for source_markers, query_markers in _POLICY_DATE_DOMAIN_QUERY_MARKERS:
        if any(marker in haystack for marker in source_markers) and not any(
            marker in normalized_query for marker in query_markers
        ):
            return True
    return False


def _policy_context_strongly_supports_date(
    *,
    normalized_query: str,
    normalized_context: str,
    policy_alignment: dict[str, object] | None,
) -> bool:
    context_terms = _query_terms(normalized_context)
    query_terms = _query_terms(normalized_query)
    meaningful_overlap = {
        term for term in (context_terms & query_terms)
        if term not in {"tarih", "zaman", "sure", "gun", "hafta", "ay", "yil", "basvuru", "yapmali"}
    }
    target_program = str((policy_alignment or {}).get("query_target_program") or "")
    target_markers = _PROGRAM_SPECIFIC_MARKERS.get(target_program, ())
    has_target_context = bool(
        target_markers and any(_contains_marker(normalized_context, marker) for marker in target_markers)
    )
    strong_process_markers = (
        "egitim ogretim",
        "ogretimin basladigi",
        "basladigi tarihten itibaren",
        "tarihten itibaren",
        "basvuru suresi",
        "basvuru tarih",
        "hafta icinde",
        "gun icinde",
        "son basvuru",
    )
    has_process_context = any(marker in normalized_context for marker in strong_process_markers)
    return has_process_context and (bool(meaningful_overlap) or has_target_context)


def _looks_like_bare_date_or_duration(normalized_claim: str) -> bool:
    text = collapse_whitespace(normalized_claim)
    if not text:
        return True
    if re.fullmatch(r"\d{1,2}(?:[./]\d{1,2})?(?:[./]\d{2,4})?", text):
        return True
    if re.fullmatch(r"\d{1,2}\s+\d{1,2}\s+\d{2,4}", text):
        return True
    if re.fullmatch(r"\d+\s*(?:gun|hafta|ay|yil)", text):
        return True
    return False


def _build_value_arbitration(
    required_claims: Sequence[RequiredClaim],
    *,
    secondary_values: Sequence[str],
    conflicting_values: Sequence[str],
) -> dict[str, object]:
    primary_values = [
        value.raw
        for claim in required_claims
        if claim.value_role == "answer_threshold"
        for value in claim.required_values
    ]
    related_values = [
        value.raw
        for claim in required_claims
        if claim.value_role == "related_condition"
        for value in claim.required_values
    ]
    return {
        "primary_values": list(_dedupe(primary_values)),
        "related_values": list(_dedupe(related_values)),
        "secondary_values": list(_dedupe(secondary_values)),
        "conflicting_values": list(_dedupe(conflicting_values)),
    }


def _required_claim_arbitration_score(
    *,
    normalized_claim: str,
    normalized_context: str,
    policy_alignment: dict[str, object] | None,
    reason: str,
) -> int:
    if reason != "gpa_threshold":
        return 0
    alignment = policy_alignment or {}
    score = 0
    if str(alignment.get("status") or "") == "match":
        score += 1
    target_program = str(alignment.get("query_target_program") or "")
    matched_programs = {str(item) for item in alignment.get("matched_programs") or []}
    if target_program and target_program in matched_programs:
        score += 4
    markers = _PROGRAM_SPECIFIC_MARKERS.get(target_program, ())
    if markers and any(_contains_marker(normalized_claim, marker) for marker in markers):
        score += 4
    elif markers and any(_contains_marker(normalized_context, marker) for marker in markers):
        score += 2
    if any(marker in normalized_claim for marker in ("basvurabilmesi", "basvuru", "sart", "kosul")):
        score += 1
    if any(marker in normalized_claim for marker in ("basari siralam", "ilk %", "yuzde")):
        score += 2
    if "ana dal not ortalam" in normalized_claim and any(
        marker in normalized_claim for marker in ("basari siralam", "ilk %", "yuzde")
    ):
        score += 2
    if any(marker in normalized_claim for marker in ("kaydi silinir", "kayit silinir", "silinir")):
        score -= 2
    return score


def _arbitrate_competing_required_claims(
    claims: list[RequiredClaim],
) -> tuple[list[RequiredClaim], list[str]]:
    by_reason: dict[str, list[RequiredClaim]] = {}
    for claim in claims:
        by_reason.setdefault(claim.reason, []).append(claim)

    result: list[RequiredClaim] = []
    demoted_values: list[str] = []
    for reason, grouped in by_reason.items():
        if reason != "gpa_threshold" or len(grouped) <= 1:
            result.extend(grouped)
            continue
        canonical_values = {
            value.canonical
            for claim in grouped
            for value in claim.required_values
        }
        if len(canonical_values) <= 1:
            result.extend(grouped)
            continue
        best_score = max(claim.arbitration_score for claim in grouped)
        if best_score <= 0:
            result.extend(grouped)
            continue
        winners = [claim for claim in grouped if claim.arbitration_score == best_score]
        losers = [claim for claim in grouped if claim.arbitration_score < best_score]
        result.extend(winners)
        demoted_values.extend(
            value.raw
            for claim in losers
            for value in claim.required_values
        )
    return result, demoted_values


def _answer_value_is_allowed_context(
    *,
    normalized_answer: str,
    value: EvidenceNumber,
    query_aspects: set[str],
) -> bool:
    if "gpa" not in query_aspects:
        return False
    window_before = normalized_answer[max(0, value.position - 55): value.position]
    window_after = normalized_answer[value.position: value.position + 65]
    window = f"{window_before} {window_after}"
    if value.is_percent and any(marker in window for marker in ("ilk", "basari", "siralam")):
        return True
    return bool(re.search(r"\b(?:uzerinden|puan\s+uzerinden)\b", window_after[:40]))


def _required_values_for_claim(
    *,
    normalized_query: str,
    normalized_claim: str,
) -> tuple[list[EvidenceNumber], str]:
    values = _extract_numbers(normalized_claim)
    if not values:
        return [], ""
    aspects = _aspects(normalized_query)
    if "gpa" in aspects and _aspects(normalized_claim) & {"gpa"}:
        threshold_values = _threshold_values(normalized_claim, values)
        if threshold_values:
            return threshold_values, "gpa_threshold"
        decimal_values = [value for value in values if value.is_decimal]
        if decimal_values:
            return [decimal_values[-1]], "gpa_decimal_fallback"
    if "fee" in aspects:
        return _near_marker_values(normalized_claim, values, _ASPECT_MARKERS["fee"]) or values, "fee_value"
    if "course_credit" in aspects:
        if "akts" in normalized_query or "ects" in normalized_query:
            if "akts" not in normalized_claim and "ects" not in normalized_claim:
                return [], ""
            akts_values = _near_marker_values(normalized_claim, values, ("akts", "ects"))
            if akts_values:
                return akts_values, "course_akts_value"
        if "kredi" in normalized_query:
            if "kredi" not in normalized_claim:
                return [], ""
            credit_values = _near_marker_values(normalized_claim, values, ("kredi",))
            if credit_values:
                return credit_values, "course_credit_value"
        return (
            _near_marker_values(normalized_claim, values, _ASPECT_MARKERS["course_credit"])
            or values
        ), "course_credit_value"
    if "date" in aspects:
        if _looks_like_multi_date_claim(normalized_claim, values):
            return [], "ambiguous_multi_date_claim"
        return values, "date_or_time_value"
    if "percentage" in aspects:
        percent_values = [value for value in values if value.is_percent]
        return percent_values or values, "percentage_value"
    if ("kac" in normalized_query or "ne kadar" in normalized_query) and not aspects:
        return values, "numeric_question_value"
    return [], ""


def _threshold_values(normalized_claim: str, values: Sequence[EvidenceNumber]) -> list[EvidenceNumber]:
    selected: list[EvidenceNumber] = []
    for match in _THRESHOLD_VALUE_RE.finditer(normalized_claim):
        matched = _canonicalize_number(match.group(1))
        for value in values:
            if value.canonical == matched and value not in selected:
                selected.append(value)
    return selected


def _near_marker_values(
    normalized_claim: str,
    values: Sequence[EvidenceNumber],
    markers: Sequence[str],
) -> list[EvidenceNumber]:
    selected: list[EvidenceNumber] = []
    for value in values:
        window = normalized_claim[max(0, value.position - 45): value.position + 45]
        if any(marker in window for marker in markers):
            selected.append(value)
    return selected


def _extract_numbers(normalized_text: str) -> list[EvidenceNumber]:
    values: list[EvidenceNumber] = []
    for match in _VALUE_RE.finditer(normalized_text):
        if _looks_like_structural_number(normalized_text, match.start(), match.end()):
            continue
        raw = collapse_whitespace(match.group(0))
        canonical = _canonicalize_number(raw)
        if not canonical:
            continue
        is_percent = raw.startswith("%") or raw.startswith("yuzde")
        is_decimal = "," in raw or "." in raw
        aliases = _number_aliases(canonical, is_percent=is_percent)
        values.append(
            EvidenceNumber(
                raw=raw,
                canonical=canonical,
                aliases=aliases,
                is_percent=is_percent,
                is_decimal=is_decimal,
                position=match.start(),
            )
        )
    return values


def _looks_like_structural_number(text: str, start: int, end: int) -> bool:
    raw = text[start:end]
    if "," in raw or "." in raw or raw.startswith("%") or raw.startswith("yuzde"):
        return False
    if re.search(r"\bmadde\s*$", text[max(0, start - 12):start]):
        return True
    if text[max(0, start - 1):start] == "(" and text[end:end + 1] == ")":
        return True
    line_start = text.rfind("\n", 0, start) + 1
    prefix = text[line_start:start]
    next_char = text[end:end + 1]
    return not prefix.strip() and next_char in {".", ")"}


def _canonicalize_number(raw: str) -> str:
    text = collapse_whitespace(raw).lower()
    is_percent = text.startswith("%") or text.startswith("yuzde")
    text = text.replace("yuzde", "").replace("%", "").strip()
    text = text.replace(" ", "")
    if _looks_like_thousands_number(text):
        text = text.replace(".", "")
    else:
        text = text.replace(",", ".")
    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        return ""
    if "." in text:
        integer, fraction = text.split(".", 1)
        fraction = fraction.rstrip("0")
        text = integer if not fraction else f"{integer}.{fraction}"
    text = text.lstrip("0") or "0"
    return f"%{text}" if is_percent else text


def _number_aliases(canonical: str, *, is_percent: bool) -> tuple[str, ...]:
    aliases = {canonical}
    if is_percent and canonical.startswith("%"):
        aliases.add(canonical[1:])
    return tuple(sorted(aliases))


def _looks_like_thousands_number(text: str) -> bool:
    if "," in text:
        return False
    return bool(re.fullmatch(r"\d{1,3}(?:\.\d{3})+", text))


def _looks_like_multi_date_claim(normalized_claim: str, values: Sequence[EvidenceNumber]) -> bool:
    if len(values) <= 2:
        return False
    month_count = len(_MONTH_RE.findall(normalized_claim))
    year_count = sum(1 for value in values if len(value.canonical.lstrip("%")) == 4)
    return month_count >= 2 or year_count >= 2


def infer_source_family(*, source: str | None = None, claim: str | None = None) -> str | None:
    haystack = normalize_text(f"{source or ''} {claim or ''}")
    for family, markers in _SOURCE_FAMILY_MARKERS:
        if any(marker in haystack for marker in markers):
            return family
    return None


def _dedupe(values: Iterable[_T]) -> tuple[_T, ...]:
    result: list[_T] = []
    for value in values:
        if value not in result:
            result.append(value)
    return tuple(result)
