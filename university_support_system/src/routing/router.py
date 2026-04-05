"""Department routing service."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

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
from src.llm.prompt_templates import DEPARTMENT_ROUTING_SYSTEM_PROMPT
from src.routing.routing_policy import (
    NORMALIZED_COURSE_CODE_IN_QUERY,
    contains_any,
    detect_task_type as detect_task_type_by_policy,
    has_academic_calendar_markers,
    has_cap_markers,
    has_formal_rule_markers,
    has_international_markers,
    has_payment_registration_timing_overlap,
    looks_like_personal_data_query as looks_like_personal_data_query_by_policy,
    looks_like_personal_credit_progress_query,
    normalize_routing_text,
    should_skip_llm_for_academic_context_query as should_skip_llm_for_academic_context_query_by_policy,
)

if TYPE_CHECKING:
    from src.llm.llm_service import LLMService

logger = logging.getLogger(__name__)

LLM_ROUTING_TIMEOUT_SECONDS = 12


@dataclass(frozen=True)
class _RuleRoutingDecision:
    """Intermediate result for rule-based routing."""

    departments: list[Department]
    confidence: float
    confidence_level: ConfidenceLevel
    strategy: RoutingStrategy
    reasoning: str


class DepartmentRouter:
    """Rule-based router with LLM fallback for ambiguous queries."""

    def __init__(
        self,
        llm_service: LLMService | None = None,
        high_confidence_threshold: float = ROUTING_HIGH_CONFIDENCE_THRESHOLD,
        low_confidence_threshold: float = ROUTING_LOW_CONFIDENCE_THRESHOLD,
        keyword_match_threshold: float = KEYWORD_MATCH_THRESHOLD,
    ) -> None:
        if llm_service is None:
            from src.llm.llm_service import LLMService

            llm_service = LLMService()
        self.llm_service = llm_service
        self.high_confidence_threshold = high_confidence_threshold
        self.low_confidence_threshold = low_confidence_threshold
        self.keyword_match_threshold = keyword_match_threshold

    async def route(
        self,
        query: str,
        *,
        llm_profile: str | None = None,
        preferred_departments: list[Department] | None = None,
        preferred_task_type: TaskType | None = None,
    ) -> RoutingResult:
        """Route a query to the relevant departments."""
        return await self.route_with_hints(
            query,
            llm_profile=llm_profile,
            preferred_departments=preferred_departments,
            preferred_task_type=preferred_task_type,
        )

    async def route_with_hints(
        self,
        query: str,
        *,
        llm_profile: str | None = None,
        preferred_departments: list[Department] | None = None,
        preferred_task_type: TaskType | None = None,
    ) -> RoutingResult:
        """Route a query, optionally using prior conversation hints."""
        rule_decision = self._apply_routing_overrides(query, self._route_with_rules(query))
        rule_decision = self._apply_conversation_hints(
            query=query,
            decision=rule_decision,
            preferred_departments=preferred_departments or [],
        )

        if self._is_rule_decision_confident(rule_decision):
            return self._to_result(
                query,
                rule_decision,
                task_type=preferred_task_type or self._detect_task_type(query, rule_decision.departments),
            )

        if self._should_skip_llm_for_personal_query(query, rule_decision):
            boosted = self._boost_rule_decision_for_personal(rule_decision)
            boosted = self._apply_routing_overrides(query, boosted)
            return self._to_result(
                query,
                boosted,
                task_type=preferred_task_type or self._detect_task_type(query, boosted.departments),
            )

        if self._should_skip_llm_for_academic_context_query(query, rule_decision):
            boosted = self._apply_routing_overrides(query, rule_decision)
            return self._to_result(
                query,
                boosted,
                task_type=preferred_task_type or self._detect_task_type(query, boosted.departments),
            )

        if self._should_skip_llm_when_no_department_signal(rule_decision):
            return self._to_result(
                query,
                rule_decision,
                task_type=preferred_task_type or self._detect_task_type(query, rule_decision.departments),
            )

        llm_decision = self._apply_routing_overrides(
            query,
            await self._route_with_llm(query, fallback=rule_decision, llm_profile=llm_profile),
        )
        llm_decision = self._apply_conversation_hints(
            query=query,
            decision=llm_decision,
            preferred_departments=preferred_departments or [],
        )
        return self._to_result(
            query,
            llm_decision,
            task_type=preferred_task_type or self._detect_task_type(query, llm_decision.departments),
        )

    def _is_rule_decision_confident(self, decision: _RuleRoutingDecision) -> bool:
        if decision.strategy == RoutingStrategy.DIRECT and decision.confidence >= self.keyword_match_threshold:
            return True
        if decision.strategy == RoutingStrategy.PARALLEL and decision.confidence >= self.high_confidence_threshold:
            return True
        return False

    @staticmethod
    def _looks_like_personal_data_query(query: str) -> bool:
        return looks_like_personal_data_query_by_policy(query)

    @staticmethod
    def _should_skip_llm_when_no_department_signal(decision: _RuleRoutingDecision) -> bool:
        return decision.strategy == RoutingStrategy.CLARIFICATION and not decision.departments

    def _should_skip_llm_for_personal_query(
        self,
        query: str,
        decision: _RuleRoutingDecision,
    ) -> bool:
        if decision.strategy == RoutingStrategy.CLARIFICATION and not decision.departments:
            return False
        if not decision.departments:
            return False
        return self._looks_like_personal_data_query(query)

    @staticmethod
    def _should_skip_llm_for_academic_context_query(
        query: str,
        decision: _RuleRoutingDecision,
    ) -> bool:
        return should_skip_llm_for_academic_context_query_by_policy(query, decision.departments)

    def _apply_routing_overrides(self, query: str, decision: _RuleRoutingDecision) -> _RuleRoutingDecision:
        lowered = normalize_routing_text(query)

        if has_payment_registration_timing_overlap(lowered):
            confidence = max(decision.confidence, 0.86)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning=(
                    "Odeme/ucret ve kayit takvimi birlikte soruluyor; "
                    "finance ve ogrenci isleri paralel ele alinmali."
                ),
            )

        if has_academic_calendar_markers(lowered):
            confidence = max(decision.confidence, 0.8)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Akademik takvim veya kayit donemi sorusu; ogrenci isleri oncelikli.",
            )

        if has_cap_markers(lowered):
            confidence = max(decision.confidence, 0.82)
            if contains_any(lowered, ("basvuru", "ne zaman", "takvim", "tarih", "surec")):
                return _RuleRoutingDecision(
                    departments=[Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS],
                    confidence=confidence,
                    confidence_level=self._confidence_level(confidence),
                    strategy=RoutingStrategy.PARALLEL,
                    reasoning=(
                        "CAP/YAP basvuru veya takvim sorusu; ogrenci isleri ve "
                        "akademik programlar birlikte ele alinmali."
                    ),
                )
            return _RuleRoutingDecision(
                departments=[Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="CAP/YAP kosul veya mufredat sorusu; akademik programlar oncelikli.",
            )

        if has_formal_rule_markers(lowered):
            confidence = max(decision.confidence, 0.8)
            return _RuleRoutingDecision(
                departments=[Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Akademik kural veya yonetmelik niteliginde soru; akademik programlar oncelikli.",
            )

        if has_international_markers(lowered):
            confidence = max(decision.confidence, 0.8)
            departments = [Department.ACADEMIC_PROGRAMS]
            strategy = RoutingStrategy.DIRECT
            if Department.FINANCE in decision.departments:
                departments = [Department.ACADEMIC_PROGRAMS, Department.FINANCE]
                strategy = RoutingStrategy.PARALLEL
            return _RuleRoutingDecision(
                departments=departments,
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=strategy,
                reasoning="Erasmus veya uluslararasi surec sorusu; academic_programs oncelikli.",
            )

        if looks_like_personal_credit_progress_query(lowered):
            if decision.departments == [Department.ACADEMIC_PROGRAMS]:
                confidence = max(decision.confidence, 0.78)
                return _RuleRoutingDecision(
                    departments=[Department.STUDENT_AFFAIRS],
                    confidence=confidence,
                    confidence_level=self._confidence_level(confidence),
                    strategy=RoutingStrategy.DIRECT,
                    reasoning=(
                        decision.reasoning
                        + " Kisisel AKTS/kredi ilerlemesi; ogrenci isleri oncelikli."
                    ),
                )

        return decision

    def _boost_rule_decision_for_personal(self, decision: _RuleRoutingDecision) -> _RuleRoutingDecision:
        confidence = max(decision.confidence, 0.78)
        return _RuleRoutingDecision(
            departments=list(decision.departments),
            confidence=confidence,
            confidence_level=self._confidence_level(confidence),
            strategy=decision.strategy,
            reasoning=(
                "Kisisel veri sinyali; kural tabanli yonlendirme kullanildi "
                "(LLM yonlendirmesi atlandi)."
            ),
        )

    def _apply_conversation_hints(
        self,
        *,
        query: str,
        decision: _RuleRoutingDecision,
        preferred_departments: list[Department],
    ) -> _RuleRoutingDecision:
        if not preferred_departments:
            return decision
        if decision.departments:
            overlap = [dept for dept in decision.departments if dept in preferred_departments]
            if overlap:
                confidence = max(decision.confidence, 0.8)
                return _RuleRoutingDecision(
                    departments=list(dict.fromkeys(decision.departments)),
                    confidence=confidence,
                    confidence_level=self._confidence_level(confidence),
                    strategy=decision.strategy,
                    reasoning=(
                        decision.reasoning
                        + " Onceki konusma baglamindaki departman sinyali ile desteklendi."
                    ),
                )
            return decision
        confidence = max(decision.confidence, 0.74)
        return _RuleRoutingDecision(
            departments=list(dict.fromkeys(preferred_departments)),
            confidence=confidence,
            confidence_level=self._confidence_level(confidence),
            strategy=(
                RoutingStrategy.DIRECT
                if len(preferred_departments) == 1
                else RoutingStrategy.PARALLEL
            ),
            reasoning=(
                "Yeni soru follow-up olarak goruldu; onceki konusmadaki departman baglami kullanildi."
            ),
        )

    def _score_departments(self, query: str) -> dict[Department, float]:
        normalized_query = normalize_routing_text(query)
        scores: dict[Department, float] = {}

        for department in Department:
            keywords = get_department_config(department).keywords
            matches = sum(1 for keyword in keywords if normalize_routing_text(keyword) in normalized_query)
            scores[department] = round(min(matches / 3, 1.0), 4)

        if NORMALIZED_COURSE_CODE_IN_QUERY.search(normalized_query):
            scores[Department.ACADEMIC_PROGRAMS] = max(scores[Department.ACADEMIC_PROGRAMS], round(2 / 3, 4))

        return scores

    def _route_with_rules(self, query: str) -> _RuleRoutingDecision:
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
                reasoning="Kural tabanli eslesmede belirgin departman sinyali bulunamadi.",
            )

        if best_score >= self.keyword_match_threshold and (best_score - second_score) > 0.2:
            return _RuleRoutingDecision(
                departments=[best_department],
                confidence=best_score,
                confidence_level=self._confidence_level(best_score),
                strategy=RoutingStrategy.DIRECT,
                reasoning=f"Kural tabanli yonlendirme en guclu eslesme olarak {best_department.value} secti.",
            )

        close_departments = [
            department
            for department, score in ordered
            if score > 0 and (best_score - score) <= 0.2
        ]
        strategy = RoutingStrategy.PARALLEL if len(close_departments) > 1 else RoutingStrategy.DIRECT

        return _RuleRoutingDecision(
            departments=close_departments or [best_department],
            confidence=best_score,
            confidence_level=self._confidence_level(best_score),
            strategy=strategy,
            reasoning="Kural tabanli yonlendirme birden fazla yakin eslesme buldu.",
        )

    async def _route_with_llm(
        self,
        query: str,
        fallback: _RuleRoutingDecision,
        *,
        llm_profile: str | None = None,
    ) -> _RuleRoutingDecision:
        from src.llm.llm_service import LLMServiceError

        try:
            response = await asyncio.wait_for(
                self.llm_service.generate(
                    prompt=query,
                    system=DEPARTMENT_ROUTING_SYSTEM_PROMPT,
                    json_mode=True,
                    model_role="routing",
                    llm_profile=llm_profile,
                ),
                timeout=LLM_ROUTING_TIMEOUT_SECONDS,
            )
            payload = json.loads(response)
            departments = self._parse_departments(payload.get("departments", []))
            confidence = float(payload.get("confidence", 0.0))
            reasoning = payload.get("reasoning") or "LLM tabanli yonlendirme karari."

            if not departments:
                logger.warning("LLM yonlendirme yaniti gecerli departman icermedi; fallback kullanilacak.")
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
        except asyncio.TimeoutError:
            logger.warning(
                "LLM yonlendirme %ss icinde tamamlanmadi, kural tabanli fallback kullanilacak.",
                LLM_ROUTING_TIMEOUT_SECONDS,
            )
            return fallback
        except (LLMServiceError, ValueError, TypeError, json.JSONDecodeError) as exc:
            logger.warning(
                "LLM yonlendirme basarisiz oldu, kural tabanli fallback kullanilacak: %s",
                exc,
            )
            return fallback

    def _parse_departments(self, raw_departments: list[Any]) -> list[Department]:
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
        if confidence >= self.high_confidence_threshold:
            return ConfidenceLevel.HIGH
        if confidence >= self.low_confidence_threshold:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def _detect_task_type(self, query: str, departments: list[Department]) -> TaskType | None:
        return detect_task_type_by_policy(query, departments)

    def _to_result(
        self,
        query: str,
        decision: _RuleRoutingDecision,
        task_type: TaskType | None,
    ) -> RoutingResult:
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
