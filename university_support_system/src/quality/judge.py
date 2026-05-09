"""LLM-as-a-Judge quality gate for risky answers.

Runs only on risky answers (numeric/date/fee/AKTS/GANO, regulation
compliance, "bilgi bulunamadı", multi-department, foreign token
suspicion, low intent coverage).  Maximum 1 quality loop.

Judge returns structured JSON with:
  approved, failure_reason, action, missing_intents,
  unsupported_claims, bad_tokens, suggested_query, retry_plan

Actions: accept | rewrite_only | retrieve_again | ask_clarification
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field

from src.core.text_normalization import normalize_text

logger = logging.getLogger(__name__)

_JUDGE_TIMEOUT_SECONDS = 12

JUDGE_SYSTEM_PROMPT = """\
G\u00f6rev: Verilen soru, cevap ve kaynak ba\u011flam\u0131n\u0131 de\u011ferlendir. Cevap kalitesini denetle.

DE\u011eERLEND\u0130RME KR\u0130TERLER\u0130:
1. Say\u0131/tarih/\u00fccret/AKTS/GANO bilgisi do\u011fru mu? Kaynakta varsa aynen korundu mu? Kaynakta yoksa uydurulmu\u015f m\u0131?
2. Mevzuat/uygunluk cevab\u0131 kaynakla \u00e7eli\u015fiyor mu? Kaynakta belirsizlik varsa cevap kesinlik ifade ediyor mu?
3. "Bilgi bulunamad\u0131" denmi\u015f ama kaynaklarda ilgili bilgi var m\u0131?
4. \u00c7ok departmanl\u0131 cevapta her departman\u0131n katk\u0131s\u0131 var m\u0131?
5. Yabanc\u0131 kelime/bozuk token var m\u0131?
6. \u00c7ok par\u00e7al\u0131 soruda t\u00fcm alt niyetler cevapland\u0131 m\u0131?
7. Plan/cevap sozlesmesi verildiyse answer_contract.must_answer maddeleri cevapta kanitli sekilde karsilandi mi?
8. Evidence contract verildiyse kaynaklar beklenen konu veya kaynak turuyle uyumlu mu?

JSON FORMAT:
{
  "approved": true/false,
  "failure_reason": "string|null",
  "action": "accept|rewrite_only|retrieve_again|ask_clarification",
  "missing_intents": ["time_date", "eligibility", ...],
  "unsupported_claims": ["string|null", ...],
  "bad_tokens": ["string|null", ...],
  "suggested_query": "string|null",
  "retry_plan": {"capability":"string|null","query":"string|null","reason":"string|null"}|null
}

AKS\u0130YON KURALLARI:
- accept: Cevap yeterli, kaynakla uyumlu.
- rewrite_only: Evidence iyi ama cevap k\u00f6t\u00fc (yanl\u0131\u015f say\u0131, yabanc\u0131 token, eksik alt ba\u015fl\u0131k).
- retrieve_again: Evidence soruyu kapsam\u0131yor veya yanl\u0131\u015f kaynaklar bask\u0131n.
- ask_clarification: B\u00f6l\u00fcm/program/\u00f6\u011frenci t\u00fcr\u00fc gibi zorunlu bilgi eksik.

SADECE JSON yaz, ba\u015fka hi\u00e7bir \u015fey yazma.
"""


# ── Risk detection ──────────────────────────────────────────────────

_NUMERIC_DATE_PATTERN = re.compile(
    r"\b\d+[.,]\d+\b"   # 3.28, 2,50
    r"|\b\d+\s*(?:AKTS|akts|kredi|TL|tl|\u20ac|\$)(?=\b|$)"
    r"|\b(?:GANO|gano|GNO|gno)\s*\d",
    re.IGNORECASE,
)
_FEE_PATTERN = re.compile(
    r"\b(?:[uü]cret|katk[ıi] pay[ıi]|har[cç]|fiyat|taksit|[oö]deyebilir|[oö]deme)\b",
    re.IGNORECASE,
)
_REGULATION_PATTERN = re.compile(
    r"\b(?:y[oö]nerge|y[oö]netmelik|mevzuat|karar|esas)\b",
    re.IGNORECASE,
)
_NO_INFO_PATTERN = re.compile(
    r"\bbilgi\s+bulunamad[ıi]\b|\bbulunamad[ıi]\b|\bkaynaklarda\s+net\s+bilgi\b",
    re.IGNORECASE,
)


def _is_risky_answer(
    answer: str,
    *,
    is_multi_department: bool = False,
    has_foreign_suspicion: bool = False,
    intent_coverage_is_low: bool = False,
) -> bool:
    """Determine if an answer is risky enough to warrant judge evaluation."""
    if _NUMERIC_DATE_PATTERN.search(answer):
        return True
    if _FEE_PATTERN.search(answer):
        return True
    if _REGULATION_PATTERN.search(answer):
        return True
    if _NO_INFO_PATTERN.search(answer):
        return True
    if is_multi_department:
        return True
    if has_foreign_suspicion:
        return True
    if intent_coverage_is_low:
        return True
    return False


# ── Judge result ────────────────────────────────────────────────────

@dataclass(frozen=True)
class JudgeResult:
    """Structured output from the LLM judge."""

    approved: bool
    failure_reason: str | None = None
    action: str = "accept"  # accept | rewrite_only | retrieve_again | ask_clarification
    missing_intents: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    bad_tokens: list[str] = field(default_factory=list)
    suggested_query: str | None = None
    retry_plan: dict | None = None


def _parse_judge_response(raw: str) -> JudgeResult:
    """Parse judge JSON response, with safe defaults."""
    if isinstance(raw, dict):
        payload = raw
    else:
        raw_text = str(raw or "")
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError:
            # Try to extract JSON from surrounding text.
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                try:
                    payload = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    return JudgeResult(approved=True, action="accept")
            else:
                return JudgeResult(approved=True, action="accept")

    action = str(payload.get("action", "accept")).strip().lower()
    if action not in ("accept", "rewrite_only", "retrieve_again", "ask_clarification"):
        action = "accept"

    return JudgeResult(
        approved=bool(payload.get("approved", True)),
        failure_reason=str(payload.get("failure_reason") or "").strip() or None,
        action=action,
        missing_intents=list(payload.get("missing_intents") or []),
        unsupported_claims=list(payload.get("unsupported_claims") or []),
        bad_tokens=list(payload.get("bad_tokens") or []),
        suggested_query=str(payload.get("suggested_query") or "").strip() or None,
        retry_plan=payload.get("retry_plan") if isinstance(payload.get("retry_plan"), dict) else None,
    )


async def run_judge(
    *,
    query: str,
    answer: str,
    evidence_summary: str,
    plan_decision: dict | None = None,
    answer_contract: dict | None = None,
    evidence_contract: dict | None = None,
    llm_service,
    llm_profile: str | None = None,
    is_multi_department: bool = False,
    has_foreign_suspicion: bool = False,
    intent_coverage_is_low: bool = False,
    missing_intents: list[str] | None = None,
) -> JudgeResult | None:
    """Run the judge on a risky answer. Returns None if not risky or on error.

    Only runs on risky answers. Maximum 1 quality loop is enforced by the caller.
    """
    has_plan_contract = bool(answer_contract or evidence_contract)
    if not has_plan_contract and not _is_risky_answer(
        answer,
        is_multi_department=is_multi_department,
        has_foreign_suspicion=has_foreign_suspicion,
        intent_coverage_is_low=intent_coverage_is_low,
    ):
        return None

    judge_prompt = json.dumps({
        "query": query,
        "answer": answer[:800],
        "evidence_summary": evidence_summary[:600],
        "plan_decision": plan_decision or {},
        "answer_contract": answer_contract or {},
        "evidence_contract": evidence_contract or {},
        "context": {
            "is_multi_department": is_multi_department,
            "has_foreign_suspicion": has_foreign_suspicion,
            "intent_coverage_is_low": intent_coverage_is_low,
            "missing_intents": missing_intents or [],
        },
    }, ensure_ascii=False, indent=2)

    try:
        raw = await asyncio.wait_for(
            llm_service.generate(
                prompt=judge_prompt,
                system=JUDGE_SYSTEM_PROMPT,
                json_mode=True,
                model_role="judge",
                llm_profile=llm_profile,
            ),
            timeout=_JUDGE_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        logger.warning("judge_failed reason=%s", type(exc).__name__)
        return None

    result = _parse_judge_response(raw)
    logger.info(
        "judge_result approved=%s action=%s failure=%s missing=%s unsupported=%s bad_tokens=%s",
        result.approved,
        result.action,
        result.failure_reason,
        result.missing_intents,
        result.unsupported_claims[:2],
        result.bad_tokens[:2],
    )
    return result
