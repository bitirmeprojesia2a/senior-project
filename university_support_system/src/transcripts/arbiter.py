"""Routing arbiter for uploaded document context.

The arbiter decides whether a Slack message should be answered from the
currently uploaded document or from the normal institutional RAG flow.
It does not generate final answers.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from src.core.text_normalization import normalize_text
from src.transcripts.document_intent import (
    DocumentQuestionClassification,
    DocumentQuestionIntent,
    classify_document_question,
)
from src.transcripts.service import TranscriptDocument


class DocumentContextTarget(str, Enum):
    UPLOADED_DOCUMENT = "uploaded_document"
    INSTITUTIONAL_RAG = "institutional_rag"
    HYBRID_DOCUMENT_RAG = "hybrid_document_rag"
    CLARIFY = "clarify"


@dataclass(frozen=True)
class DocumentContextDecision:
    target: DocumentContextTarget
    confidence: float
    reason: str
    effective_query: str
    document_intent: DocumentQuestionIntent | None = None
    answer_strategy: str | None = None
    field_lookup_confidence: float | None = None
    used_hybrid_rag: bool = False

    def to_metadata(self) -> dict[str, object]:
        return {
            "target": self.target.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "effective_query": self.effective_query,
            "document_intent": self.document_intent.value if self.document_intent else None,
            "answer_strategy": self.answer_strategy,
            "field_lookup_confidence": self.field_lookup_confidence,
            "used_hybrid_rag": self.used_hybrid_rag,
        }


class ArbiterLLMProtocol(Protocol):
    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
        model_role: str = "default",
        llm_profile: str | None = None,
    ) -> str:
        ...


_GRADE_QUERY_RE = re.compile(r"\b(AA|BA|BB|CB|CC|DC|DD|FD|FF|YT|YZ|G|K|P|F)\b", re.IGNORECASE)
_WORD_RE = re.compile(r"[a-z0-9]+")

_DOCUMENT_REFERENCE_MARKERS = (
    "belgeye gore",
    "belgede",
    "belgedeki",
    "belgenin",
    "belge ne",
    "bu belge",
    "bu belgede",
    "yukledigim belge",
    "yuklenen belge",
    "dosyaya gore",
    "transkripte gore",
    "transkriptime gore",
    "bu transkript",
    "inceleyip",
)

_DOCUMENT_REPAIR_MARKERS = (
    "belgeye gore cevaplamadin",
    "belgeye gore cevapla",
    "cevaplamadin",
    "var ya",
    "var iste",
    "belgede var",
    "orada var",
    "yaziyor ya",
    "gosteriyor",
)

_TRANSCRIPT_METRIC_MARKERS = (
    "akts",
    "kredi",
    "gno",
    "agno",
    "gano",
    "ortalama",
    "not dagilimi",
    "harf notu",
    "basarisiz",
    "basarili",
    "kaldigim",
    "gectigim",
    "aldigim",
    "aldigi",
    "aldiklarim",
    "aldiklari",
    "almis",
    "almisim",
    "aldim",
    "dersim",
    "derslerim",
    "notum",
    "notlarim",
)

_COUNT_OR_LIST_MARKERS = (
    "kac",
    "kac tane",
    "sayisi",
    "say",
    "hangi",
    "hangileri",
    "neler",
    "liste",
    "listele",
)

_GRADUATION_PROGRESS_MARKERS = (
    "mezun",
    "mezuniyet",
    "kac kaldi",
    "tamamlamam",
)

_INSTITUTIONAL_MARKERS = (
    "harc",
    "borc",
    "ders kaydi",
    "kayit yenileme",
    "cap",
    "capa",
    "cift anadal",
    "yandal",
    "duyuru",
    "takvim",
    "basvuru tarih",
    "iletisim",
    "santral",
    "yonetmelik",
    "yaz okulu",
    "staj",
    "yatay gecis",
    "erasmus",
)

_GENERIC_DOCUMENT_ACTION_MARKERS = (
    "ozet",
    "ozetle",
    "yorumla",
    "incele",
    "ne diyor",
    "neler var",
    "ne hakkinda",
    "bu belge ne",
    "belge ne",
    "ne ise yariyor",
    "ise yariyor",
    "neye yarar",
    "ne icin",
    "amaci",
    "amac",
    "teslim",
    "nereye",
    "nereden",
    "basvur",
    "doldur",
    "imza",
    "imzalat",
)

_GENERIC_DOCUMENT_FIELD_MARKERS = (
    "adi",
    "ad",
    "soyad",
    "baba",
    "anne",
    "dogum",
    "tc",
    "kimlik",
    "ogrenci no",
    "program",
    "bolum",
    "fakulte",
    "sinif",
    "durum",
    "tarih",
    "kayit",
    "barkod",
)

_AMBIGUOUS_SHORT_FOLLOWUP_TOKENS = {
    "peki",
    "kac",
    "kacti",
    "hangileri",
    "neler",
    "listele",
}


class UploadedDocumentArbiter:
    def __init__(self, *, llm_service: ArbiterLLMProtocol | None = None) -> None:
        self.llm_service = llm_service

    async def decide(
        self,
        *,
        query: str,
        document: TranscriptDocument,
        last_query: str | None = None,
        llm_profile: str | None = None,
    ) -> DocumentContextDecision:
        normalized = normalize_text(query)
        deterministic = self._decide_with_rules(
            query=query,
            normalized=normalized,
            document=document,
            last_query=last_query,
        )
        if deterministic is not None:
            return deterministic

        llm_decision = await self._decide_with_llm(
            query=query,
            document=document,
            last_query=last_query,
            llm_profile=llm_profile,
        )
        if llm_decision is not None:
            return llm_decision

        return self._fallback_decision(
            query=query,
            normalized=normalized,
            document=document,
            last_query=last_query,
        )

    def _decide_with_rules(
        self,
        *,
        query: str,
        normalized: str,
        document: TranscriptDocument,
        last_query: str | None,
    ) -> DocumentContextDecision | None:
        if not normalized:
            return DocumentContextDecision(
                target=DocumentContextTarget.CLARIFY,
                confidence=0.7,
                reason="empty_query_with_active_document",
                effective_query=query,
                document_intent=DocumentQuestionIntent.CLARIFY,
                answer_strategy="clarify",
            )

        if last_query and any(marker in normalized for marker in ("belge icin sormuyorum", "belgeye gore sormuyorum")):
            return DocumentContextDecision(
                target=DocumentContextTarget.INSTITUTIONAL_RAG,
                confidence=0.82,
                reason="explicit_not_document_correction",
                effective_query=last_query,
                document_intent=DocumentQuestionIntent.INSTITUTIONAL_RAG,
                answer_strategy="institutional_rag",
            )

        classification = classify_document_question(query=query, document=document, last_query=last_query)
        if classification.intent == DocumentQuestionIntent.CLARIFY and classification.confidence < 0.62:
            return None
        return _decision_from_classification(
            classification=classification,
            query=query,
            normalized=normalized,
            last_query=last_query,
        )

    async def _decide_with_llm(
        self,
        *,
        query: str,
        document: TranscriptDocument,
        last_query: str | None,
        llm_profile: str | None,
    ) -> DocumentContextDecision | None:
        if self.llm_service is None:
            return None
        prompt = _build_llm_prompt(query=query, document=document, last_query=last_query)
        try:
            raw = await self.llm_service.generate(
                prompt,
                system=(
                    "You only classify routing target for an uploaded document context. "
                    "Return strict JSON and do not answer the user."
                ),
                json_mode=True,
                model_role="routing",
                llm_profile=llm_profile,
            )
        except Exception:
            return None
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            return None
        target = str(payload.get("target") or "")
        if target not in {item.value for item in DocumentContextTarget}:
            return None
        try:
            confidence = float(payload.get("confidence") or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0
        if confidence < 0.62:
            return None
        effective_query = str(payload.get("effective_query") or query)
        intent = _coerce_intent(payload.get("document_intent") or payload.get("intent"))
        return DocumentContextDecision(
            target=DocumentContextTarget(target),
            confidence=min(max(confidence, 0.0), 1.0),
            reason=str(payload.get("reason") or "llm_arbiter"),
            effective_query=effective_query,
            document_intent=intent,
            answer_strategy=_answer_strategy_for_intent(intent),
            used_hybrid_rag=DocumentContextTarget(target) == DocumentContextTarget.HYBRID_DOCUMENT_RAG,
        )

    def _fallback_decision(
        self,
        *,
        query: str,
        normalized: str,
        document: TranscriptDocument,
        last_query: str | None,
    ) -> DocumentContextDecision:
        if document.document_type == "transcript" and (
            _has_grade_query(query, normalized)
            or _has_transcript_metric(normalized)
            or _is_short_vague_followup(normalized, last_query)
        ):
            return DocumentContextDecision(
                target=DocumentContextTarget.UPLOADED_DOCUMENT,
                confidence=0.66,
                reason="fallback_document_priority",
                effective_query=_effective_document_query(query=query, normalized=normalized, last_query=last_query),
                document_intent=DocumentQuestionIntent.TRANSCRIPT_METRIC,
                answer_strategy="transcript_metric",
            )
        if _is_institutional_query(normalized):
            return DocumentContextDecision(
                target=DocumentContextTarget.INSTITUTIONAL_RAG,
                confidence=0.72,
                reason="fallback_institutional_marker",
                effective_query=query,
                document_intent=DocumentQuestionIntent.INSTITUTIONAL_RAG,
                answer_strategy="institutional_rag",
            )
        return DocumentContextDecision(
            target=DocumentContextTarget.CLARIFY,
            confidence=0.58,
            reason="ambiguous_active_document_query",
            effective_query=query,
            document_intent=DocumentQuestionIntent.CLARIFY,
            answer_strategy="clarify",
        )


def _has_document_reference(normalized: str) -> bool:
    return any(marker in normalized for marker in _DOCUMENT_REFERENCE_MARKERS)


def _decision_from_classification(
    *,
    classification: DocumentQuestionClassification,
    query: str,
    normalized: str,
    last_query: str | None,
) -> DocumentContextDecision:
    target = _target_for_intent(classification.intent)
    return DocumentContextDecision(
        target=target,
        confidence=classification.confidence,
        reason=classification.reason,
        effective_query=(
            query
            if target == DocumentContextTarget.INSTITUTIONAL_RAG
            else _effective_document_query(query=query, normalized=normalized, last_query=last_query)
        ),
        document_intent=classification.intent,
        answer_strategy=_answer_strategy_for_intent(classification.intent),
        field_lookup_confidence=classification.field_confidence,
        used_hybrid_rag=target == DocumentContextTarget.HYBRID_DOCUMENT_RAG,
    )


def _target_for_intent(intent: DocumentQuestionIntent) -> DocumentContextTarget:
    if intent == DocumentQuestionIntent.INSTITUTIONAL_RAG:
        return DocumentContextTarget.INSTITUTIONAL_RAG
    if intent == DocumentQuestionIntent.HYBRID_DOCUMENT_RAG:
        return DocumentContextTarget.HYBRID_DOCUMENT_RAG
    if intent == DocumentQuestionIntent.CLARIFY:
        return DocumentContextTarget.CLARIFY
    return DocumentContextTarget.UPLOADED_DOCUMENT


def _answer_strategy_for_intent(intent: DocumentQuestionIntent | None) -> str | None:
    if intent is None:
        return None
    if intent == DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP:
        return "field_lookup"
    if intent == DocumentQuestionIntent.TRANSCRIPT_METRIC:
        return "transcript_metric"
    if intent == DocumentQuestionIntent.HYBRID_DOCUMENT_RAG:
        return "hybrid_document_rag"
    return intent.value


def _coerce_intent(value: object) -> DocumentQuestionIntent | None:
    if value is None:
        return None
    try:
        return DocumentQuestionIntent(str(value))
    except ValueError:
        return None


def _has_generic_document_action(normalized: str) -> bool:
    return any(marker in normalized for marker in _GENERIC_DOCUMENT_ACTION_MARKERS)


def _has_generic_document_field_question(normalized: str) -> bool:
    if not any(marker in normalized for marker in ("ne", "nedir", "neymis", "neymiş", "hangi", "geciyor", "yaziyor")):
        return False
    return any(marker in normalized for marker in _GENERIC_DOCUMENT_FIELD_MARKERS)


def _query_matches_document_field(normalized: str, document: TranscriptDocument) -> bool:
    if not document.fields:
        return False
    query_tokens = set(_WORD_RE.findall(normalized)) - {
        "bu",
        "belge",
        "belgede",
        "belgedeki",
        "belgenin",
        "ne",
        "nedir",
        "neymis",
        "hangi",
        "olarak",
        "geciyor",
        "yaziyor",
        "var",
        "mi",
    }
    for field in document.fields:
        field_tokens = set(_WORD_RE.findall(field.key))
        if not field_tokens:
            continue
        if field.key in normalized:
            return True
        if len(query_tokens & field_tokens) / max(len(field_tokens), 1) >= 0.72:
            return True
    return False


def _has_transcript_metric(normalized: str) -> bool:
    return any(marker in normalized for marker in _TRANSCRIPT_METRIC_MARKERS)


def _has_count_or_list(normalized: str) -> bool:
    return any(marker in normalized for marker in _COUNT_OR_LIST_MARKERS)


def _has_graduation_progress(normalized: str) -> bool:
    return any(marker in normalized for marker in _GRADUATION_PROGRESS_MARKERS)


def _has_grade_query(raw_query: str, normalized: str) -> bool:
    if _GRADE_QUERY_RE.search(raw_query):
        return True
    tokens = set(_WORD_RE.findall(normalized))
    return bool(tokens & {"aa", "ba", "bb", "cb", "cc", "dc", "dd", "fd", "ff", "yt", "yz"})


def _is_institutional_query(normalized: str) -> bool:
    return any(marker in normalized for marker in _INSTITUTIONAL_MARKERS)


def _is_short_vague_followup(normalized: str, last_query: str | None) -> bool:
    if not last_query:
        return False
    tokens = set(_WORD_RE.findall(normalized))
    if len(tokens) > 5:
        return False
    return bool(tokens & _AMBIGUOUS_SHORT_FOLLOWUP_TOKENS)


def _effective_document_query(*, query: str, normalized: str, last_query: str | None) -> str:
    if last_query and any(marker in normalized for marker in _DOCUMENT_REPAIR_MARKERS):
        return f"{last_query}\nKullanici duzeltmesi: {query}"
    return query


def _build_llm_prompt(*, query: str, document: TranscriptDocument, last_query: str | None) -> str:
    return (
        "Aktif yuklenmis belge baglami var.\n"
        f"Belge turu: {document.document_type}\n"
        f"Dosya: {document.filename}\n"
        f"Program: {document.program_name or ''}\n"
        f"Ders sayisi: {len(document.courses)}\n"
        f"Toplam AKTS: {document.total_akts if document.total_akts is not None else ''}\n"
        f"Son belge sorusu: {last_query or ''}\n"
        f"Kullanici sorusu: {query}\n\n"
        "Karar ver:\n"
        "- uploaded_document: soru yuklenen belge/transkript uzerinden cevaplanmali.\n"
        "- institutional_rag: soru genel universite kaynaklari/RAG uzerinden cevaplanmali.\n"
        "- hybrid_document_rag: soru hem yuklenen belge hem de universite kaynaklariyla cevaplanmali.\n"
        "- clarify: hedef belirsiz, kullaniciya belgeye gore mi genel kaynaklara gore mi sorulmali.\n"
        "document_intent de sec: document_summary, document_procedure, document_field_lookup, "
        "transcript_metric, institutional_rag, hybrid_document_rag, clarify.\n"
        "JSON schema: {\"target\":\"uploaded_document|institutional_rag|hybrid_document_rag|clarify\","
        "\"document_intent\":\"...\",\"confidence\":0.0,\"reason\":\"...\",\"effective_query\":\"...\"}"
    )
