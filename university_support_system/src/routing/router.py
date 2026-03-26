"""
Sorgu Yönlendirme Servisi

Kural tabanlı hızlı yönlendirme ile LLM tabanlı belirsizlik çözümünü
birleştirir ve RoutingResult üretir.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from src.core.constants import (
    ConfidenceLevel,
    Department,
    KEYWORD_MATCH_THRESHOLD,
    ROUTING_HIGH_CONFIDENCE_THRESHOLD,
    ROUTING_LOW_CONFIDENCE_THRESHOLD,
    RoutingStrategy,
    TaskType,
    get_department_config,
)
from src.db.schemas import RoutingResult
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.prompt_templates import DEPARTMENT_ROUTING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _RuleRoutingDecision:
    """Kural tabanlı yönlendirme ara çıktısı."""

    departments: list[Department]
    confidence: float
    confidence_level: ConfidenceLevel
    strategy: RoutingStrategy
    reasoning: str


class DepartmentRouter:
    """Kural tabanlı ve LLM destekli departman router'ı."""

    def __init__(
        self,
        llm_service: LLMService | None = None,
        high_confidence_threshold: float = ROUTING_HIGH_CONFIDENCE_THRESHOLD,
        low_confidence_threshold: float = ROUTING_LOW_CONFIDENCE_THRESHOLD,
        keyword_match_threshold: float = KEYWORD_MATCH_THRESHOLD,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        self.high_confidence_threshold = high_confidence_threshold
        self.low_confidence_threshold = low_confidence_threshold
        self.keyword_match_threshold = keyword_match_threshold

    async def route(self, query: str) -> RoutingResult:
        """Sorguyu ilgili departman(lar)a yönlendirir."""
        rule_decision = self._route_with_rules(query)

        if self._is_rule_decision_confident(rule_decision):
            return self._to_result(query, rule_decision, task_type=self._detect_task_type(query, rule_decision.departments))

        llm_decision = await self._route_with_llm(query, fallback=rule_decision)
        return self._to_result(query, llm_decision, task_type=self._detect_task_type(query, llm_decision.departments))

    def _is_rule_decision_confident(self, decision: _RuleRoutingDecision) -> bool:
        """Kural sonucunun doğrudan kullanılabilecek kadar net olup olmadığını söyler."""
        if decision.strategy == RoutingStrategy.DIRECT and decision.confidence >= self.keyword_match_threshold:
            return True
        if decision.strategy == RoutingStrategy.PARALLEL and decision.confidence >= self.high_confidence_threshold:
            return True
        return False

    def _score_departments(self, query: str) -> dict[Department, float]:
        """Anahtar kelime eşleşmesine göre departman skoru üretir."""
        normalized_query = query.casefold()
        scores: dict[Department, float] = {}

        for department in Department:
            keywords = get_department_config(department).keywords
            matches = sum(1 for keyword in keywords if keyword.casefold() in normalized_query)
            # Kısa kullanıcı sorgularında 2-3 güçlü eşleşme genellikle yeterli sinyal üretir.
            scores[department] = round(min(matches / 3, 1.0), 4)

        return scores

    def _route_with_rules(self, query: str) -> _RuleRoutingDecision:
        """Yalnızca keyword skorları ile yönlendirme kararı üretir."""
        scores = self._score_departments(query)
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_department, best_score = ordered[0]
        second_score = ordered[1][1] if len(ordered) > 1 else 0.0

        if best_score <= 0:
            return _RuleRoutingDecision(
                departments=[],
                confidence=0.0,
                confidence_level=ConfidenceLevel.LOW,
                strategy=RoutingStrategy.CLARIFICATION,
                reasoning="Kural tabanlı eşleşmede belirgin departman sinyali bulunamadı.",
            )

        if best_score >= self.keyword_match_threshold and (best_score - second_score) > 0.2:
            return _RuleRoutingDecision(
                departments=[best_department],
                confidence=best_score,
                confidence_level=self._confidence_level(best_score),
                strategy=RoutingStrategy.DIRECT,
                reasoning=f"Kural tabanlı yönlendirme en güçlü eşleşme olarak {best_department.value} seçti.",
            )

        close_departments = [department for department, score in ordered if score > 0 and (best_score - score) <= 0.2]
        strategy = RoutingStrategy.PARALLEL if len(close_departments) > 1 else RoutingStrategy.DIRECT

        return _RuleRoutingDecision(
            departments=close_departments or [best_department],
            confidence=best_score,
            confidence_level=self._confidence_level(best_score),
            strategy=strategy,
            reasoning="Kural tabanlı yönlendirme birden fazla yakın eşleşme buldu.",
        )

    async def _route_with_llm(self, query: str, fallback: _RuleRoutingDecision) -> _RuleRoutingDecision:
        """Belirsiz sorgularda LLM ile yönlendirme kararı alır."""
        try:
            response = await self.llm_service.generate(
                prompt=query,
                system=DEPARTMENT_ROUTING_SYSTEM_PROMPT,
                json_mode=True,
            )
            payload = json.loads(response)
            departments = self._parse_departments(payload.get("departments", []))
            confidence = float(payload.get("confidence", 0.0))
            reasoning = payload.get("reasoning") or "LLM tabanlı yönlendirme kararı."

            if not departments:
                logger.warning("LLM yönlendirme yanıtı geçerli departman içermedi; fallback kullanılacak.")
                return fallback

            strategy = RoutingStrategy.PARALLEL if len(departments) > 1 else RoutingStrategy.DIRECT
            if confidence < self.low_confidence_threshold:
                strategy = RoutingStrategy.CLARIFICATION

            return _RuleRoutingDecision(
                departments=departments,
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=strategy,
                reasoning=reasoning,
            )
        except (LLMServiceError, ValueError, TypeError, json.JSONDecodeError) as exc:
            logger.warning("LLM yönlendirme başarısız oldu, kural tabanlı fallback kullanılacak: %s", exc)
            return fallback

    def _parse_departments(self, raw_departments: list[Any]) -> list[Department]:
        """LLM veya dış kaynaktan gelen departman değerlerini filtreler."""
        parsed: list[Department] = []
        for value in raw_departments:
            try:
                department = Department(str(value))
            except ValueError:
                continue
            if department not in parsed:
                parsed.append(department)
        return parsed

    def _confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Skora göre güven seviyesi üretir."""
        if confidence >= self.high_confidence_threshold:
            return ConfidenceLevel.HIGH
        if confidence >= self.low_confidence_threshold:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def _detect_task_type(self, query: str, departments: list[Department]) -> TaskType | None:
        """Temel görev tipi tespiti yapar."""
        normalized_query = query.casefold()

        if Department.FINANCE in departments:
            if any(keyword in normalized_query for keyword in ("burs",)):
                return TaskType.SCHOLARSHIP_QUERY
            if any(keyword in normalized_query for keyword in ("odeme", "ödeme", "harç", "harc", "dekont", "taksit")):
                return TaskType.TUITION_QUERY
            return TaskType.PAYMENT_QUERY

        if Department.STUDENT_AFFAIRS in departments:
            if any(keyword in normalized_query for keyword in ("kayit", "kayıt", "kayd", "yatay", "dikey", "muafiyet", "intibak")):
                return TaskType.REGISTRATION_QUERY
            if any(keyword in normalized_query for keyword in ("not", "gno", "transkript", "mezuniyet")):
                return TaskType.ACADEMIC_QUERY
            return TaskType.COURSE_QUERY

        if Department.ACADEMIC_PROGRAMS in departments:
            if any(keyword in normalized_query for keyword in ("yönerge", "yonerge", "yönetmelik", "yonetmelik", "politika", "prosedür", "prosedur", "genelge")):
                return TaskType.PROCEDURE_QUERY
            return TaskType.COURSE_QUERY

        return None

    def _to_result(
        self,
        query: str,
        decision: _RuleRoutingDecision,
        task_type: TaskType | None,
    ) -> RoutingResult:
        """Ara yönlendirme kararını şema sonucuna çevirir."""
        if decision.strategy == RoutingStrategy.CLARIFICATION and not decision.departments:
            return RoutingResult(
                departments=[],
                confidence=decision.confidence,
                confidence_level=decision.confidence_level,
                strategy=RoutingStrategy.CLARIFICATION,
                reasoning=decision.reasoning,
                task_type=task_type,
            )

        return RoutingResult(
            departments=decision.departments,
            confidence=decision.confidence,
            confidence_level=decision.confidence_level,
            strategy=decision.strategy,
            reasoning=decision.reasoning,
            task_type=task_type,
        )
