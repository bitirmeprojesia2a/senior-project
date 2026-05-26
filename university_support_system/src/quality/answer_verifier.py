"""Optional LLM-based answer verifier.

Disabled by default.  Only activated after benchmark evaluation
when ENABLE_LLM_ANSWER_VERIFIER=true in settings.

Compares the generated answer against evidence items using a focused
LLM prompt and returns structured verification results.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Sequence

from src.quality.evidence import EvidenceItem

if TYPE_CHECKING:
    from src.llm.llm_service import LLMService

logger = logging.getLogger(__name__)

_DEFAULT_VERIFIER_TIMEOUT = 5.0


@dataclass
class VerifierResult:
    """Result of the LLM verification check."""

    verified: bool = False
    supported_claims: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    missing_info: list[str] = field(default_factory=list)
    error: str | None = None
    raw_response: str = ""


def is_verifier_enabled() -> bool:
    """Check if the LLM answer verifier is enabled in settings."""
    try:
        from src.core.config import settings
        return getattr(
            getattr(settings, "quality", None),
            "enable_llm_answer_verifier",
            False,
        )
    except Exception:
        return False


def get_verifier_timeout() -> float:
    """Get the verifier timeout from settings."""
    try:
        from src.core.config import settings
        return float(
            getattr(
                getattr(settings, "quality", None),
                "llm_verifier_timeout_seconds",
                _DEFAULT_VERIFIER_TIMEOUT,
            )
        )
    except Exception:
        return _DEFAULT_VERIFIER_TIMEOUT


def _build_verifier_prompt(
    answer: str,
    evidence_items: Sequence[EvidenceItem],
) -> str:
    """Build a focused verification prompt."""
    evidence_text = ""
    for idx, item in enumerate(evidence_items[:5], start=1):
        evidence_text += (
            f"\n[Kaynak {idx}: {item.source_name}]\n"
            f"{item.selected_sentences}\n"
        )

    return (
        f"CEVAP:\n{answer}\n\n"
        f"KAYNAKLAR:{evidence_text}\n\n"
        "Cevabi kaynaklarla karsilastir. Her iddia icin:\n"
        "- supported: kaynakta acik destek var\n"
        "- unsupported: kaynakta destek yok\n"
        "- missing: cevapta olmasi gereken onemli bilgi kaynaklarda var ama cevapta yok\n\n"
        "JSON formatinda yanit ver:\n"
        '{"supported": [...], "unsupported": [...], "missing": [...]}'
    )


_VERIFIER_SYSTEM = (
    "Sen bir dogrulama ajansin. Verilen cevaptaki iddialari kaynaklarla "
    "karsilastirarak JSON formatinda rapor uretirsin. "
    "Yalnizca kaynaklarda ACIKCA gecen bilgileri 'supported' olarak isaretle. "
    "Kaynakta olmayan iddialari 'unsupported' olarak belirt. "
    "Kaynaklarda olan ama cevapta eksik kalan onemli bilgileri 'missing' olarak listele. "
    "Yalnizca JSON dondurmeli, baska aciklama ekleme."
)


async def verify_answer(
    answer: str,
    evidence_items: Sequence[EvidenceItem],
    llm_service: LLMService,
    *,
    timeout: float | None = None,
    llm_profile: str | None = None,
) -> VerifierResult:
    """Run LLM-based answer verification.

    Parameters
    ----------
    answer : str
        The generated answer to verify.
    evidence_items : list[EvidenceItem]
        Evidence items to verify against.
    llm_service : LLMService
        LLM service instance.
    timeout : float, optional
        Override the default timeout.
    llm_profile : str, optional
        LLM profile to use.

    Returns
    -------
    VerifierResult
        Structured verification result. On error, returns a result with
        error set and verified=False.
    """
    if not evidence_items:
        return VerifierResult(error="no_evidence_items")

    effective_timeout = timeout or get_verifier_timeout()
    prompt = _build_verifier_prompt(answer, evidence_items)

    try:
        raw = await asyncio.wait_for(
            llm_service.generate(
                prompt=prompt,
                system=_VERIFIER_SYSTEM,
                model_role="specialist_synthesis",
                llm_profile=llm_profile,
            ),
            timeout=effective_timeout,
        )
    except asyncio.TimeoutError:
        logger.warning("answer_verifier_timeout seconds=%.1f", effective_timeout)
        return VerifierResult(error="timeout")
    except Exception as exc:
        logger.warning("answer_verifier_error: %s", exc)
        return VerifierResult(error=str(exc))

    # Parse JSON response
    try:
        # Extract JSON from response (LLM might add extra text)
        json_start = raw.find("{")
        json_end = raw.rfind("}") + 1
        if json_start < 0 or json_end <= json_start:
            return VerifierResult(error="no_json_in_response", raw_response=raw)

        data = json.loads(raw[json_start:json_end])
        return VerifierResult(
            verified=True,
            supported_claims=data.get("supported", []),
            unsupported_claims=data.get("unsupported", []),
            missing_info=data.get("missing", []),
            raw_response=raw,
        )
    except (json.JSONDecodeError, KeyError) as exc:
        logger.warning("answer_verifier_parse_error: %s", exc)
        return VerifierResult(error=f"parse_error: {exc}", raw_response=raw)


def should_verify(
    evidence_items: Sequence[EvidenceItem],
    *,
    global_synthesis_used: bool = False,
    department_count: int = 1,
) -> bool:
    """Determine if the answer should be verified based on risk signals.

    Only meaningful when the verifier is enabled.  Always returns False
    when the verifier is disabled.
    """
    if not is_verifier_enabled():
        return False

    # Multiple departments → higher risk of cross-contamination
    if department_count >= 2 and global_synthesis_used:
        return True

    # Low top score
    if evidence_items:
        top_score = max(item.score for item in evidence_items)
        if top_score < 0.55:
            return True

    # Many definitive claims detected by evidence extraction
    definitive_count = sum(
        1 for item in evidence_items
        for fact in item.extracted_facts
        if any(
            w in fact
            for w in ("zorunludur", "yapilamaz", "gerekir", "yapilabilir")
        )
    )
    if definitive_count >= 4:
        return True

    return False
