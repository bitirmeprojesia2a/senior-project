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
from src.db.schemas import IntentAnalysis, RoutingResult
from src.llm.prompt_templates import DEPARTMENT_ROUTING_SYSTEM_PROMPT, build_routing_user_prompt
from src.routing.routing_policy import (
    NORMALIZED_COURSE_CODE_IN_QUERY,
    contains_any,
    detect_task_type as detect_task_type_by_policy,
    has_academic_calendar_markers,
    has_announcement_markers,
    has_cap_markers,
    has_general_akts_markers,
    has_internship_markers,
    has_formal_rule_markers,
    has_international_markers,
    has_student_services_payment_overlap,
    has_scholarship_markers,
    has_student_services_markers,
    has_student_document_markers,
    has_student_document_request_markers,
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
    intent: IntentAnalysis | None = None


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

        if self._is_rule_decision_confident(rule_decision, query):
            return self._to_result(
                query,
                rule_decision,
                task_type=preferred_task_type or self._detect_task_type(query, rule_decision.departments),
            )

        llm_decision = self._apply_routing_overrides(
            query,
            await self._analyze_intent_with_llm(query, fallback=rule_decision, llm_profile=llm_profile),
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

    def _is_rule_decision_confident(self, decision: _RuleRoutingDecision, query: str) -> bool:
        """Yalnizca cok yuksek keyword eslesmelerinde VE basit sorgularda LLM'i atla."""
        if decision.confidence < 0.95:
            return False
        if decision.strategy not in (RoutingStrategy.DIRECT, RoutingStrategy.PARALLEL):
            return False
        return not self._is_complex_query(query)

    @staticmethod
    def _is_complex_query(query: str) -> bool:
        """Heuristik karmasiklik tespiti. True ise LLM intent analizi zorunludur."""
        normalized = normalize_routing_text(query)

        if query.count("?") >= 2:
            return True

        if len(normalized.split()) > 18:
            return True

        _COMPARISON = (
            "arasindaki fark", "farkli mi", "karsilastir",
            "yoksa", "hangisi daha",
        )
        if any(m in normalized for m in _COMPARISON):
            return True

        _CONDITIONAL = (
            "olursa", "olursam", "durumda", "gerekir mi",
            "gerekiyor mu", "sayilir mi", "etkilenir mi",
            "etkiler mi", "kesilir mi", "mahsup",
        )
        if any(m in normalized for m in _CONDITIONAL):
            return True

        _PROCESS = (
            "adim adim", "nasil isliyor", "tum kosul",
            "hangi adim", "sureci nasil",
        )
        if any(m in normalized for m in _PROCESS):
            return True

        if normalized.count(" ve ") >= 2:
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
        overridden = self._compute_routing_override(query, decision)
        if overridden is decision or decision.intent is None:
            return overridden
        merged_depts = list(overridden.departments)
        for dept in decision.departments:
            if dept not in merged_depts:
                merged_depts.append(dept)
        if merged_depts == list(overridden.departments):
            return overridden
        return _RuleRoutingDecision(
            departments=merged_depts,
            confidence=overridden.confidence,
            confidence_level=overridden.confidence_level,
            strategy=RoutingStrategy.PARALLEL if len(merged_depts) > 1 else RoutingStrategy.DIRECT,
            reasoning=overridden.reasoning + " LLM departman sinyalleri korundu.",
            intent=overridden.intent,
        )

    def _compute_routing_override(self, query: str, decision: _RuleRoutingDecision) -> _RuleRoutingDecision:
        lowered = normalize_routing_text(query)
        intent = decision.intent

        if has_student_document_markers(lowered) or has_student_document_request_markers(lowered):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Transkript veya ogrenci belgesi niteliginde soru; ogrenci isleri oncelikli.",
                intent=intent,
            )

        if has_student_services_payment_overlap(lowered):
            confidence = max(decision.confidence, 0.87)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning=(
                    "Kayit dondurma veya benzeri idari surec, odeme yukumluluguyle birlikte soruluyor; "
                    "ogrenci isleri ve finans paralel ele alinmali."
                ),
                intent=intent,
            )

        if has_student_services_markers(lowered):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="UBYS, sifre, kayit/donem dondurma veya ilisik kesme odakli soru; ogrenci isleri oncelikli.",
                intent=intent,
            )

        if has_announcement_markers(lowered):
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=0.70,
                confidence_level=ConfidenceLevel.MEDIUM,
                strategy=RoutingStrategy.CLARIFICATION,
                reasoning="Duyuru sorusu; canli veri gerektirir, mevcut kaynaklarda yanitlanamaz.",
                intent=intent,
            )

        if has_internship_markers(lowered):
            confidence = max(decision.confidence, 0.86)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Staj, MUP, sanayi uygulamasi veya bitirme sureci; ogrenci isleri oncelikli.",
                intent=intent,
            )

        if contains_any(lowered, ("katki payi", "borc", "borclu", "iade", "fazla ucret", "harc burosu")):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.FINANCE],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Katki payi, borc, iade veya ucret duzeltme odakli soru; finans oncelikli.",
                intent=intent,
            )

        if has_general_akts_markers(lowered):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Program bazli mezuniyet AKTS sorusu; ogrenci isleri oncelikli ve structured veri kullanilmali.",
                intent=intent,
            )

        if has_scholarship_markers(lowered):
            confidence = max(decision.confidence, 0.83)
            if has_international_markers(lowered) and "burs" not in lowered:
                return _RuleRoutingDecision(
                    departments=[Department.ACADEMIC_PROGRAMS, Department.FINANCE],
                    confidence=confidence,
                    confidence_level=self._confidence_level(confidence),
                    strategy=RoutingStrategy.PARALLEL,
                    reasoning=(
                        "Uluslararasi hibe veya benzeri bir burs sorusu; "
                        "academic_programs ve finance birlikte ele alinmali."
                    ),
                    intent=intent,
                )
            if contains_any(lowered, ("basvuru", "ne zaman", "tarih", "surec", "son tarih")):
                return _RuleRoutingDecision(
                    departments=[Department.FINANCE, Department.STUDENT_AFFAIRS],
                    confidence=confidence,
                    confidence_level=self._confidence_level(confidence),
                    strategy=RoutingStrategy.PARALLEL,
                    reasoning=(
                        "Burs basvurusu/takvimi sorusu; finance ve ogrenci isleri "
                        "academic_programs yerine oncelikli ele alinmali."
                    ),
                    intent=intent,
                )
            return _RuleRoutingDecision(
                departments=[Department.FINANCE, Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning=(
                    "Burs odakli soru; finance ana departman, ogrenci isleri destek departmani olarak secildi."
                ),
                intent=intent,
            )

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
                intent=intent,
            )

        if has_academic_calendar_markers(lowered):
            confidence = max(decision.confidence, 0.8)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Akademik takvim veya kayit donemi sorusu; ogrenci isleri oncelikli.",
                intent=intent,
            )

        if has_cap_markers(lowered) and not has_international_markers(lowered):
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
                    intent=intent,
                )
            return _RuleRoutingDecision(
                departments=[Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="CAP/YAP kosul veya mufredat sorusu; akademik programlar oncelikli.",
                intent=intent,
            )

        if has_formal_rule_markers(lowered):
            confidence = max(decision.confidence, 0.8)
            return _RuleRoutingDecision(
                departments=[Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Akademik kural veya yonetmelik niteliginde soru; akademik programlar oncelikli.",
                intent=intent,
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
                intent=intent,
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
                    intent=intent,
                )

        # Kisisel veri sinyali: not ortalamam, borcum, transkript vb.
        # Bu sorular academic_programs'e degil student_affairs'e yonlendirilmeli
        if looks_like_personal_data_query_by_policy(lowered):
            if Department.ACADEMIC_PROGRAMS in decision.departments:
                confidence = max(decision.confidence, 0.78)
                return _RuleRoutingDecision(
                    departments=[Department.STUDENT_AFFAIRS],
                    confidence=confidence,
                    confidence_level=self._confidence_level(confidence),
                    strategy=RoutingStrategy.DIRECT,
                    reasoning="Kisisel veri sinyali; ogrenci isleri oncelikli.",
                    intent=intent,
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
            intent=decision.intent,
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
                    intent=decision.intent,
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
            intent=decision.intent,
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

        _SECONDARY_DEPT_MIN_SCORE = 0.25
        _SECONDARY_DEPT_MAX_GAP = 0.15
        close_departments = [
            department
            for department, score in ordered
            if score >= _SECONDARY_DEPT_MIN_SCORE
            and (best_score - score) <= _SECONDARY_DEPT_MAX_GAP
        ]
        if not close_departments:
            close_departments = [best_department]
        strategy = RoutingStrategy.PARALLEL if len(close_departments) > 1 else RoutingStrategy.DIRECT

        return _RuleRoutingDecision(
            departments=close_departments or [best_department],
            confidence=best_score,
            confidence_level=self._confidence_level(best_score),
            strategy=strategy,
            reasoning="Kural tabanli yonlendirme birden fazla yakin eslesme buldu.",
        )

    @staticmethod
    def _extract_json_from_response(response: str) -> dict | None:
        """Groq JSON mode bozulduğunda regex ile JSON bloğu çıkar."""
        import re as _re
        # Yöntem 1: { ... } bloğu bul (iç içe geçmemiş)
        brace_match = _re.search(r'\{[^{}]*\}', response, _re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        # Yöntem 2: Kaçış karakterlerini temizle ve tekrar dene
        cleaned = response.replace('\\"', '"').replace('\\\\', '\\')
        brace_match = _re.search(r'\{[^{}]*\}', cleaned, _re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        return None

    async def _analyze_intent_with_llm(
        self,
        query: str,
        fallback: _RuleRoutingDecision,
        *,
        llm_profile: str | None = None,
    ) -> _RuleRoutingDecision:
        """LLM ile niyet analizi yapar: departman + complexity + is_personal + force_llm."""
        from src.llm.llm_service import LLMServiceError

        # Kural tabanli is_personal ipucu hesapla
        rule_is_personal = self._looks_like_personal_data_query(query)

        user_prompt = build_routing_user_prompt(
            query,
            rule_is_personal_hint=rule_is_personal,
        )

        try:
            response = await asyncio.wait_for(
                self.llm_service.generate(
                    prompt=user_prompt,
                    system=DEPARTMENT_ROUTING_SYSTEM_PROMPT,
                    json_mode=True,
                    model_role="routing",
                    llm_profile=llm_profile,
                ),
                timeout=LLM_ROUTING_TIMEOUT_SECONDS,
            )
            try:
                payload = json.loads(response)
            except json.JSONDecodeError:
                payload = self._extract_json_from_response(response)
                if payload is None:
                    logger.warning("groq_json_parse_failed_fallback response=%r", response[:200])
                    return fallback
                logger.info("groq_json_recovered_via_regex")
            departments = self._parse_departments(payload.get("departments", []))
            confidence = float(payload.get("confidence", 0.0))
            reasoning = payload.get("reasoning") or "LLM tabanli niyet analizi karari."

            if not departments:
                logger.warning("LLM niyet analizi gecerli departman icermedi; fallback kullanilacak.")
                return fallback

            strategy = RoutingStrategy.PARALLEL if len(departments) > 1 else RoutingStrategy.DIRECT
            if confidence < self.low_confidence_threshold:
                strategy = RoutingStrategy.CLARIFICATION

            intent = self._parse_intent(payload)

            return _RuleRoutingDecision(
                departments=departments,
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=strategy,
                reasoning=reasoning,
                intent=intent,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "LLM niyet analizi %ss icinde tamamlanmadi, kural tabanli fallback kullanilacak.",
                LLM_ROUTING_TIMEOUT_SECONDS,
            )
            return fallback
        except (LLMServiceError, ValueError, TypeError, json.JSONDecodeError) as exc:
            logger.warning(
                "LLM niyet analizi basarisiz oldu, kural tabanli fallback kullanilacak: %s",
                exc,
            )
            return fallback

    @staticmethod
    def _parse_intent(payload: dict[str, Any]) -> IntentAnalysis:
        """LLM JSON ciktisindaki niyet alanlarini ayristirir."""
        _VALID_COMPLEXITY = {"simple", "complex", "comparison", "process_chain"}
        _VALID_QUERY_TYPE = {"factual", "procedural", "comparative", "conditional"}

        raw_complexity = str(payload.get("complexity", "simple")).strip().lower()
        raw_query_type = str(payload.get("query_type", "factual")).strip().lower()

        complexity = raw_complexity if raw_complexity in _VALID_COMPLEXITY else "simple"
        query_type = raw_query_type if raw_query_type in _VALID_QUERY_TYPE else "factual"
        force_llm = bool(payload.get("force_llm_synthesis", complexity != "simple"))

        return IntentAnalysis(
            complexity=complexity,  # type: ignore[arg-type]
            is_personal=bool(payload.get("is_personal", False)),
            force_llm_synthesis=force_llm,
            query_type=query_type,  # type: ignore[arg-type]
            reasoning=payload.get("reasoning"),
        )

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
                intent=decision.intent,
            )

        return RoutingResult(
            departments=decision.departments,
            confidence=decision.confidence,
            confidence_level=decision.confidence_level,
            strategy=decision.strategy,
            reasoning=decision.reasoning,
            task_type=task_type,
            intent=decision.intent,
        )
