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
    has_graduation_payment_overlap,
    has_general_akts_markers,
    has_horizontal_transfer_markers,
    has_internship_markers,
    has_summer_school_markers,
    has_formal_rule_markers,
    has_international_markers,
    has_akts_markers,
    has_akts_registration_markers,
    has_makeup_exam_markers,
    has_max_duration_markers,
    has_pedagogical_formation_markers,
    has_single_exam_markers,
    has_student_services_payment_overlap,
    has_scholarship_markers,
    has_student_affairs_rule_markers,
    has_student_services_markers,
    has_student_document_markers,
    has_student_document_request_markers,
    has_payment_registration_timing_overlap,
    has_registration_process_overlap,
    has_student_affairs_admin_markers,
    looks_like_grade_visibility_procedure,
    looks_like_personal_data_query as looks_like_personal_data_query_by_policy,
    looks_like_personal_credit_progress_query,
    looks_like_vague_application_timing_query,
    normalize_routing_text,
    should_skip_llm_for_academic_context_query as should_skip_llm_for_academic_context_query_by_policy,
)
from src.routing.query_concepts import (
    CAPABILITY_ANNOUNCEMENT,
    CONCEPT_ACADEMIC_CALENDAR,
    CONCEPT_COMPLAINT,
    CONCEPT_COURSE_CODE,
    CONCEPT_EXEMPTION,
    CONCEPT_HORIZONTAL_TRANSFER,
    CONCEPT_INTERNSHIP,
    CONCEPT_REGISTRATION,
    CONCEPT_STUDENT_DOCUMENT,
    CONCEPT_STUDENT_SERVICES,
    DOMAIN_ACADEMIC_CALENDAR,
    DOMAIN_STUDENT_AFFAIRS_ADMIN,
    DOMAIN_STUDENT_AFFAIRS_PROCEDURE,
    extract_query_concepts,
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
    authoritative: bool = False


class DepartmentRouter:
    """LLM-first router with deterministic guardrails and rule fallback."""

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
        """Route a query, optionally using prior conversation hints.

        LLM routing is primary; rule-based routing is computed for fallback
        and used only when the LLM call fails or times out. Personal data
        queries remain deterministic (no LLM needed).
        """
        # Rule-based decision always computed — used as LLM fallback
        rule_decision = self._apply_routing_overrides(
            query,
            self._route_with_rules(query),
            llm_primary=False,
        )
        rule_decision = self._apply_conversation_hints(
            query=query,
            decision=rule_decision,
            preferred_departments=preferred_departments or [],
        )

        # Personal data queries are deterministic — skip LLM entirely
        if self._should_skip_llm_for_personal_query(query, rule_decision):
            personal_decision = self._boost_rule_decision_for_personal(rule_decision)
            return self._to_result(
                query,
                personal_decision,
                task_type=preferred_task_type or self._detect_task_type(query, personal_decision.departments),
            )

        if self._should_skip_llm_when_no_department_signal(query, rule_decision):
            return self._to_result(
                query,
                rule_decision,
                task_type=preferred_task_type or self._detect_task_type(query, rule_decision.departments),
            )

        # LLM routing is primary — always call unless personal query
        try:
            llm_decision = self._apply_routing_overrides(
                query,
                await self._analyze_intent_with_llm(query, fallback=rule_decision, llm_profile=llm_profile),
                llm_primary=True,
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
        except Exception:
            logger.warning("llm_routing_failed_fallback_to_rules query=%r", query)
            return self._to_result(
                query,
                rule_decision,
                task_type=preferred_task_type or self._detect_task_type(query, rule_decision.departments),
            )

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
            "gerekiyor",
            "gerekiyor mu", "sayilir mi", "etkilenir mi",
            "etkiler mi", "kesilir mi", "oder miyim", "mahsup",
            "zorunda miyim", "girebilir miyim",
            "mi ", "mu ", "miyim", "muyum", "miyiz", "muyuz",
            "yapabil", "yapamam", "yapabilir", "yapamaz",
        )
        if any(m in normalized for m in _CONDITIONAL):
            return True

        _PROCESS = (
            "adim adim", "nasil isliyor", "tum kosul",
            "hangi adim", "sureci nasil", "tum surec",
            "basindan sonuna", "danisman onay",
            "danismanin onay", "ders kaydindan",
            "nereye yatir", "hangi belge", "hangi belgeler",
            "hazirlamaliyim",
            "nasil", "ne yap", "nereden", "nereye",
            "hangi birim", "hangi prosedur",
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
    def _should_skip_llm_when_no_department_signal(
        query: str,
        decision: _RuleRoutingDecision,
    ) -> bool:
        """Skip LLM only for low-information chatter, not semantic no-keyword queries."""
        if decision.strategy != RoutingStrategy.CLARIFICATION or decision.departments:
            return False
        if decision.authoritative:
            return True
        normalized = normalize_routing_text(query).strip(" \t\r\n?.!,;:")
        tokens = normalized.split()
        if len(tokens) <= 1:
            return True
        low_information_markers = (
            "merhaba",
            "selam",
            "yardim",
            "yardim istiyorum",
            "bir konuda yardim",
            "bir sorum var",
        )
        if len(tokens) <= 5 and any(marker in normalized for marker in low_information_markers):
            return True
        return False

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

    def _apply_routing_overrides(
        self,
        query: str,
        decision: _RuleRoutingDecision,
        *,
        llm_primary: bool = False,
    ) -> _RuleRoutingDecision:
        overridden = self._compute_routing_override(query, decision)
        if llm_primary and overridden is not decision and not overridden.authoritative:
            logger.info(
                "semantic_routing_override_skipped_after_llm query=%r original_departments=%s override_departments=%s",
                query,
                [dept.value for dept in decision.departments],
                [dept.value for dept in overridden.departments],
            )
            return decision
        if overridden is decision or decision.intent is None or overridden.authoritative:
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
            authoritative=overridden.authoritative,
        )

    def _compute_routing_override(self, query: str, decision: _RuleRoutingDecision) -> _RuleRoutingDecision:
        lowered = normalize_routing_text(query)
        concepts = extract_query_concepts(lowered)
        intent = decision.intent

        if concepts.has(CONCEPT_COURSE_CODE):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Ders kodu tespit edildi; akademik program kaynaklari oncelikli.",
                intent=intent,
                authoritative=True,
            )

        if (
            intent is not None
            and intent.target_capability == CAPABILITY_ANNOUNCEMENT
            and CAPABILITY_ANNOUNCEMENT in concepts.blocked_primary_capabilities
        ):
            confidence = max(decision.confidence, 0.86)
            if concepts.domain_guard == DOMAIN_ACADEMIC_CALENDAR or concepts.has(CONCEPT_ACADEMIC_CALENDAR):
                reasoning = "Akademik takvim/tarih sorusu; duyuru primary akisi bloke edildi."
            elif concepts.domain_guard == DOMAIN_STUDENT_AFFAIRS_ADMIN or concepts.has(CONCEPT_COMPLAINT):
                reasoning = "Idari/sikayet proseduru; duyuru primary akisi bloke edildi."
            else:
                reasoning = "Prosedur sorusu; duyuru primary akisi bloke edildi."
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning=reasoning,
                intent=intent.model_copy(update={"target_capability": "none"}),
                authoritative=True,
            )

        if has_pedagogical_formation_markers(lowered):
            confidence = max(decision.confidence, 0.86)
            return _RuleRoutingDecision(
                departments=[Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning=(
                    "Pedagojik formasyon ders/program kurali sorusu; "
                    "akademik program kaynaklari oncelikli."
                ),
                intent=intent,
                authoritative=True,
            )

        if (
            contains_any(lowered, ("uzaktan egitim", "uzaktan ders", "5-i", "5 i", "5i"))
            and contains_any(
                lowered,
                (
                    "sinav",
                    "degerlendirme",
                    "basari",
                    "yuz yuze",
                    "cevrimici",
                    "online",
                ),
            )
        ):
            confidence = max(decision.confidence, 0.88)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning=(
                    "Uzaktan egitimde sinav ve basari degerlendirmesi sorusu; "
                    "ogrenci isleri uygulama, akademik programlar mevzuat boyutunu birlikte ele almali."
                ),
                intent=intent,
                authoritative=True,
            )

        if has_international_markers(lowered) and contains_any(lowered, ("kayit", "kayd")) and (
            contains_any(lowered, ("ucret", "harc", "odeme", "katki payi", "ogrenim ucreti"))
            or contains_any(lowered, ("ikamet", "belge", "evrak", "goc idaresi"))
        ):
            confidence = max(decision.confidence, 0.87)
            departments = [Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS]
            if contains_any(lowered, ("ucret", "harc", "odeme", "katki payi", "ogrenim ucreti")):
                departments.append(Department.FINANCE)
            return _RuleRoutingDecision(
                departments=departments,
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning=(
                    "Uluslararasi kayit sorusu ucret/ikamet/belge boyutlari tasiyor; "
                    "akademik program, ogrenci isleri ve gerekirse finans birlikte ele alinmali."
                ),
                intent=intent,
                authoritative=True,
            )

        if has_max_duration_markers(lowered) and contains_any(
            lowered,
            ("ucret", "harc", "katki payi", "odeme", "oder miyim", "odenir mi"),
        ):
            confidence = max(decision.confidence, 0.86)
            return _RuleRoutingDecision(
                departments=[Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS, Department.FINANCE],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning=(
                    "Azami/ek sure kurali odeme yukumlulugu ile birlikte soruluyor; "
                    "akademik kural, idari surec ve finans paralel ele alinmali."
                ),
                intent=intent,
                authoritative=True,
            )

        if has_horizontal_transfer_markers(lowered) and has_scholarship_markers(lowered):
            confidence = max(decision.confidence, 0.86)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning=(
                    "Yatay gecis burs/harc etkisiyle birlikte soruluyor; "
                    "ogrenci isleri ve finans birlikte ele alinmali."
                ),
                intent=intent,
                authoritative=True,
            )

        if has_horizontal_transfer_markers(lowered) and contains_any(
            lowered,
            ("muafiyet", "muaf", "intibak", "ders saydir", "ders saydirma"),
        ):
            confidence = max(decision.confidence, 0.86)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning=(
                    "Yatay gecis sonrasi muafiyet/intibak basvurusu idari surec sorusu; "
                    "duyuru akisi yerine ogrenci isleri kaynaklari oncelikli."
                ),
                intent=intent,
                authoritative=True,
            )

        if has_graduation_payment_overlap(lowered):
            confidence = max(decision.confidence, 0.87)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning=(
                    "Mezuniyet/diploma veya ilisik kesme baglami odeme/borc yukumluluguyle "
                    "birlikte soruluyor; ogrenci isleri ve finans paralel ele alinmali."
                ),
                intent=intent,
                authoritative=True,
            )

        if has_student_document_markers(lowered) or has_student_document_request_markers(lowered):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Transkript veya ogrenci belgesi niteliginde soru; ogrenci isleri oncelikli.",
                intent=intent,
                authoritative=True,
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
                authoritative=True,
            )

        if has_international_markers(lowered) and has_registration_process_overlap(lowered):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning=(
                    "Erasmus veya uluslararasi kayit sureci sorusu; "
                    "academic_programs uluslararasi surec ajani oncelikli."
                ),
                intent=intent,
                authoritative=True,
            )

        if looks_like_vague_application_timing_query(query):
            intent = intent or IntentAnalysis(
                complexity="simple",
                is_personal=False,
                force_llm_synthesis=False,
                query_type="factual",
                reasoning="basvuru turu belirsiz",
                primary_intent="unknown",
                target_capability="none",
                required_slots=["application_type"],
                missing_slots=["application_type"],
            )
            return _RuleRoutingDecision(
                departments=[],
                confidence=0.42,
                confidence_level=ConfidenceLevel.LOW,
                strategy=RoutingStrategy.CLARIFICATION,
                reasoning="Basvuru tarihi sorusu hangi basvuru turu oldugunu belirtmiyor.",
                intent=intent,
                authoritative=True,
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

        if has_registration_process_overlap(lowered):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Kayit islemi, kayit yenileme veya ders kaydi sureci sorusu; ogrenci isleri oncelikli.",
                intent=intent,
                authoritative=True,
            )

        if has_announcement_markers(lowered):
            return _RuleRoutingDecision(
                departments=[],
                confidence=0.70,
                confidence_level=ConfidenceLevel.MEDIUM,
                strategy=RoutingStrategy.CLARIFICATION,
                reasoning="Duyuru sorusu; canli veri gerektirir, dogrudan duyuru akisina yonlendirilmeli.",
                intent=intent,
            )

        if has_summer_school_markers(lowered):
            confidence = max(decision.confidence, 0.86)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning="Yaz okulu sorusu; ogrenci isleri (kayit/prosedur) + akademik programlar (yonerge) birlikte cevaplamali.",
                intent=intent,
                authoritative=True,
            )

        if has_single_exam_markers(lowered) or has_makeup_exam_markers(lowered):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Tek ders, ek sinav, butunleme veya mazeret sinavi proseduru; ogrenci isleri oncelikli.",
                intent=intent,
                authoritative=True,
            )

        # AKTS/GANO ders kaydi hakki sorulari — mezuniyet toplam AKTS degil,
        # kayit/yonetmelik proseduru. Registration + regulation kaynaklari gerekli.
        # Sadece spesifik registration markerlari (gano, akts hakki, kredi siniri vb.)
        # parallel route'a gitsin. Generic "akts" müfredat agent'inda kalmali.
        if has_akts_registration_markers(lowered):
            confidence = max(decision.confidence, 0.82)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.PARALLEL,
                reasoning="AKTS/kredi hakki, ders yuku veya GANO-AKTS iliskisi; kayit ve mevzuat kaynaklari gerekli.",
                intent=intent,
                authoritative=True,
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
                authoritative=True,
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

        if contains_any(lowered, ("ucret", "harc", "odeme", "taksit", "dekont", "katki payi")) and not contains_any(
            lowered,
            ("kayit", "yenileme", "ders kaydi", "burs"),
        ):
            confidence = max(decision.confidence, 0.84)
            return _RuleRoutingDecision(
                departments=[Department.FINANCE],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning="Odeme veya ucret odakli soru; finans oncelikli.",
                intent=intent,
                authoritative=True,
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
            if has_international_markers(lowered):
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
                    authoritative=True,
                )
            return _RuleRoutingDecision(
                departments=[Department.FINANCE],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning=(
                    "Burs odakli soru; finans ana ve varsayilan sorumlu departman olarak secildi."
                ),
                intent=intent,
                authoritative=True,
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
                authoritative=True,
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
                authoritative=True,
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

        if has_student_affairs_rule_markers(lowered):
            confidence = max(decision.confidence, 0.83)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning=(
                    "Devam, devamsizlik, butunleme, disiplin veya ders tekrari gibi "
                    "genel ogrenci isleri kural/prosedur sorusu."
                ),
                intent=intent,
                authoritative=True,
            )

        if has_student_affairs_admin_markers(lowered) or looks_like_grade_visibility_procedure(lowered):
            confidence = max(decision.confidence, 0.83)
            return _RuleRoutingDecision(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=confidence,
                confidence_level=self._confidence_level(confidence),
                strategy=RoutingStrategy.DIRECT,
                reasoning=(
                    "Sinav notu, not itirazi, kopya/disiplin veya not girisi gibi "
                    "idari ogrenci isleri proseduru."
                ),
                intent=intent,
                authoritative=True,
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
        intent = decision.intent or IntentAnalysis(
            complexity="simple",
            is_personal=True,
            force_llm_synthesis=False,
            query_type="factual",
            reasoning="Kisisel veri sinyali kural tabanli olarak belirlendi.",
        )
        return _RuleRoutingDecision(
            departments=list(decision.departments),
            confidence=confidence,
            confidence_level=self._confidence_level(confidence),
            strategy=decision.strategy,
            reasoning=(
                "Kisisel veri sinyali; kural tabanli yonlendirme kullanildi "
                "(LLM yonlendirmesi atlandi)."
            ),
            intent=intent.model_copy(update={"is_personal": True}),
            authoritative=True,
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
                    authoritative=decision.authoritative,
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
            authoritative=decision.authoritative,
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
            intent = self._parse_intent(payload)
            departments = self._parse_departments(payload.get("departments", []))
            confidence = float(payload.get("confidence", 0.0))
            reasoning = payload.get("reasoning") or "LLM tabanli niyet analizi karari."

            if not departments:
                if intent.target_capability in {"announcement", "event"} or intent.missing_slots:
                    return _RuleRoutingDecision(
                        departments=[],
                        confidence=confidence,
                        confidence_level=self._confidence_level(confidence),
                        strategy=RoutingStrategy.CLARIFICATION,
                        reasoning=reasoning,
                        intent=intent,
                    )
                logger.warning("LLM niyet analizi gecerli departman icermedi; fallback kullanilacak.")
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
        _VALID_TARGET_CAPABILITY = {"announcement", "event", "none"}

        raw_complexity = str(payload.get("complexity", "simple")).strip().lower()
        raw_query_type = str(payload.get("query_type", "factual")).strip().lower()
        raw_target_capability = str(payload.get("target_capability", "none")).strip().lower()

        complexity = raw_complexity if raw_complexity in _VALID_COMPLEXITY else "simple"
        query_type = raw_query_type if raw_query_type in _VALID_QUERY_TYPE else "factual"
        target_capability = (
            raw_target_capability
            if raw_target_capability in _VALID_TARGET_CAPABILITY
            else "none"
        )
        force_llm = bool(payload.get("force_llm_synthesis", complexity != "simple"))
        canonical_query = str(payload.get("canonical_query") or "").strip() or None
        primary_intent = str(payload.get("primary_intent") or "").strip().lower() or None
        required_slots = DepartmentRouter._parse_slot_list(payload.get("required_slots"))
        missing_slots = DepartmentRouter._parse_slot_list(payload.get("missing_slots"))

        return IntentAnalysis(
            complexity=complexity,  # type: ignore[arg-type]
            is_personal=bool(payload.get("is_personal", False)),
            force_llm_synthesis=force_llm,
            query_type=query_type,  # type: ignore[arg-type]
            reasoning=payload.get("reasoning"),
            canonical_query=canonical_query,
            primary_intent=primary_intent,
            target_capability=target_capability,  # type: ignore[arg-type]
            required_slots=required_slots,
            missing_slots=missing_slots,
        )

    @staticmethod
    def _parse_slot_list(raw_value: Any) -> list[str]:
        if not isinstance(raw_value, list):
            return []
        parsed: list[str] = []
        for item in raw_value:
            value = str(item).strip().lower()
            if value and value not in parsed:
                parsed.append(value)
        return parsed

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
        intent = decision.intent
        if decision.departments:
            intent = self._apply_rule_complexity_intent(query, intent)

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
            intent=intent,
        )

    def _apply_rule_complexity_intent(
        self,
        query: str,
        intent: IntentAnalysis | None,
    ) -> IntentAnalysis | None:
        """Preserve deterministic complexity signals when the routing LLM is too shallow."""
        if not self._is_complex_query(query):
            return intent

        inferred = self._infer_complex_intent(query)
        if intent is None:
            return inferred
        if intent.force_llm_synthesis and intent.complexity != "simple":
            return intent

        updates: dict[str, Any] = {"force_llm_synthesis": True}
        if intent.complexity == "simple":
            updates["complexity"] = inferred.complexity
        if intent.query_type == "factual":
            updates["query_type"] = inferred.query_type
        updates["is_personal"] = self._looks_like_personal_data_query(query)
        return intent.model_copy(update=updates)

    def _infer_complex_intent(self, query: str) -> IntentAnalysis:
        normalized = normalize_routing_text(query)
        comparison_markers = ("arasindaki fark", "farkli mi", "karsilastir", "hangisi")
        process_markers = (
            "adim adim",
            "sureci",
            "surec",
            "nasil isliyor",
            "basindan sonuna",
            "tum surec",
            "danisman onay",
            "danismanin onay",
            "ders kaydindan",
        )
        conditional_markers = (
            "olursa",
            "olursam",
            "durumda",
            "gerekir mi",
            "sayilir mi",
            "kesilir mi",
            "oder miyim",
            "zorunda miyim",
        )

        if any(marker in normalized for marker in comparison_markers):
            complexity = "comparison"
            query_type = "comparative"
        elif any(marker in normalized for marker in process_markers):
            complexity = "process_chain"
            query_type = "procedural"
        elif any(marker in normalized for marker in conditional_markers):
            complexity = "complex"
            query_type = "conditional"
        else:
            complexity = "complex"
            query_type = "procedural"

        return IntentAnalysis(
            complexity=complexity,  # type: ignore[arg-type]
            is_personal=self._looks_like_personal_data_query(query),
            force_llm_synthesis=True,
            query_type=query_type,  # type: ignore[arg-type]
            reasoning="Kural tabanli karmasiklik sinyali LLM sentezini zorunlu kildi.",
        )
