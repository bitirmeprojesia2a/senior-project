"""LLM-as-a-Judge quality gate for risky answers.

Runs only on risky answers (numeric/date/fee/AKTS/GANO, regulation
compliance, "bilgi bulunamadı", multi-department, foreign token
suspicion, low intent coverage).  Maximum 1 quality loop.

Judge returns structured JSON with:
  approved, failure_reason, action, missing_intents,
  unsupported_claims, bad_tokens, suggested_query

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
Gorev: Verilen soru, cevap ve kaynak baglamini degerlendir. Cevap kalitesini denetle.

DEGERLENDIRME KRITERLERI:
1. Sayi/tarih/ucret/AKTS/GANO bilgisi dogru mu? Kaynakta varsa aynen korundu mu? Kaynakta yoksa uydurulmus mi?
2. Mevzuat/uygunluk cevabi kaynakla celisiyor mu? Kaynakta belirsizlik varsa cevap kesinlik ifade ediyor mu?
3. "Bilgi bulunamadi" denmis ama kaynaklarda ilgili bilgi var mi?
4. Cok departmanli cevapta her departmanin katkisi var mi?
5. Yabanci kelime/bozuk token var mi?
6. Cok parcali soruda tum alt niyetler cevaplandi mi?

JSON FORMAT:
{
  "approved": true/false,
  "failure_reason": "string|null",
  "action": "accept|rewrite_only|retrieve_again|ask_clarification",
  "missing_intents": ["time_date", "eligibility", ...],
  "unsupported_claims": ["string|null", ...],
  "bad_tokens": ["string|null", ...],
  "suggested_query": "string|null"
}

AKSİYON KURALLARI:
- accept: Cevap yeterli, kaynakla uyumlu.
- rewrite_only: Evidence iyi ama cevap kotu (yanlis sayi, yabanci token, eksik alt baslik).
- retrieve_again: Evidence soruyu kapsamiyor veya yanlis kaynaklar baskin.
- ask_clarification: Bolum/program/ogrenci turu gibi zorunlu bilgi eksik.

SADECE JSON yaz, baska hicbir sey yazma.
"""


# ── Risk detection ──────────────────────────────────────────────────

_NUMERIC_DATE_PATTERN = re.compile(
    r"\b\d+[.,]\d+\b"   # 3.28, 2,50
    r"|\b\d+\s*(?:AKTS|akts|kredi|TL|tl|€|\$)\b"
    r"|\b(?:GANO|gano|GNO|gno)\s*\d",
    re.IGNORECASE,
)
_FEE_PATTERN = re.compile(
    r"\b(?:ucret|katki payi|harc|fiyat|taksit|odeyebilir)\b",
    re.IGNORECASE,
)
_REGULATION_PATTERN = re.compile(
    r"\b(?:yonerge|yonetmelik|yonetmelik|mevzuat|yonerge|karar|esas)\b",
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


def _parse_judge_response(raw: str) -> JudgeResult:
    """Parse judge JSON response, with safe defaults."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from surrounding text
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
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
    )


async def run_judge(
    *,
    query: str,
    answer: str,
    evidence_summary: str,
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
    if not _is_risky_answer(
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
