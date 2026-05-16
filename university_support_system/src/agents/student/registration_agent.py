"""Registration-focused student affairs agent."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.agents.student.registration_utils import (
    build_general_exam_calendar_answer,
    build_payment_debt_course_registration_answer,
    build_registration_intro,
    preferred_registration_search_top_k,
    filter_registration_answer_results,
    is_course_registration_process_query,
    is_registration_timing_query,
    pick_preferred_registration_result,
    rank_registration_results,
    rank_course_registration_process_results,
    should_skip_registration_result_enrichment,
    should_reject_registration_source_only_result,
    should_force_registration_llm_synthesis,
)
from src.capabilities.academic_formatting import deterministic_answer_for_result
from src.capabilities.executor import execute_capability_action
from src.capabilities.models import CapabilityAction
from src.core.config import settings
from src.core.constants import Department, TaskType
from src.core.policy_facets import resolve_policy_facet
from src.db.registration_data import RegistrationPeriodInfo, fetch_preferred_registration_period
from src.db.schemas import DepartmentResponse, RAGSource
from src.llm.prompt_templates import REGISTRATION_AGENT_SYSTEM_PROMPT


class RegistrationAgent(BaseSpecialistAgent):
    def __init__(
        self,
        *,
        period_fetcher: Callable[[], Awaitable[RegistrationPeriodInfo | None]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="registration_agent",
                name="Registration Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Kayit, muafiyet ve yatay gecis sureclerini yonetir.",
                task_types=(TaskType.REGISTRATION_QUERY,),
                examples=("Ders kaydi ne zaman?", "Yatay gecis basvurusu nasil yapilir?"),
                tags=("student_affairs", "registration"),
                system_prompt=REGISTRATION_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._period_fetcher = period_fetcher or fetch_preferred_registration_period

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        if not query_text:
            query_text = self._extract_query_from_task(task)

        payment_debt_answer = build_payment_debt_course_registration_answer(query_text)
        if payment_debt_answer is not None:
            response_metadata = {
                "policy_facet": "payment_debt_course_registration",
                "source_owner": {"primary": "student_affairs_policy"},
            }
            if isinstance(metadata.get("answer_contract"), dict):
                response_metadata["answer_contract"] = metadata["answer_contract"]
            return DepartmentResponse(
                department=self.department,
                answer=payment_debt_answer,
                db_data={
                    "query_type": "payment_debt_course_registration",
                    "source": "registration_policy",
                },
                generation_mode="kural",
                sources=[
                    RAGSource(
                        content=payment_debt_answer,
                        score=1.0,
                        metadata={
                            "source": "sık_sorulan_sorular.txt",
                            "record_type": "payment_debt_course_registration_policy",
                        },
                    )
                ],
                include_contact_suggestion=True,
                success=True,
                metadata=response_metadata,
            )

        capability_response = await self._try_handle_capability_plan(query_text, metadata)
        if capability_response is not None:
            return capability_response
        task = self._prepare_policy_lookup_task(task, query_text, metadata)

        exam_calendar = build_general_exam_calendar_answer(query_text)
        if exam_calendar is not None:
            answer, calendar_data = exam_calendar
            return DepartmentResponse(
                department=self.department,
                answer=answer,
                db_data=calendar_data,
                generation_mode="vt",
                sources=[
                    RAGSource(
                        content=f"{calendar_data['label']}: {calendar_data['fall']} / {calendar_data['spring']}",
                        score=1.0,
                        metadata={
                            "source": "2025_2026_genel_akademik_takvim.pdf",
                            "record_type": "academic_calendar",
                        },
                    )
                ],
                include_contact_suggestion=True,
                success=True,
            )

        if self._is_timing_query(query_text):
            period = await self._period_fetcher()
            if period is not None:
                start = period.start_date.strftime("%d.%m.%Y")
                end = period.end_date.strftime("%d.%m.%Y")
                if period.timing_status == "active":
                    message = (
                        f"Su anda {period.semester} donemi kayit sureci aktiftir "
                        f"({start} - {end})."
                    )
                elif period.timing_status == "upcoming":
                    message = (
                        f"Veritabanindaki en yakin kayit donemi {period.semester} icin "
                        f"{start} - {end} tarihleri arasinda planlanmistir."
                    )
                else:
                    message = (
                        f"Veritabanindaki son kayit donemi {period.semester} icin "
                        f"{start} - {end} tarihleri arasindaydi. "
                        "Yeni donem tarihi su anda ayrica tanimli degil."
                    )
                return DepartmentResponse(
                    department=self.department,
                    answer=message,
                    db_data={
                        "semester": period.semester,
                        "start": start,
                        "end": end,
                        "timing_status": period.timing_status,
                    },
                    sources=[],
                    include_contact_suggestion=True,
                    success=True,
                )
            return DepartmentResponse(
                department=self.department,
                answer=(
                    "Kayıt dönemi tarihleri şu anda veritabanında tanımlı değil. "
                    "En güncel tarih bilgisi yayımlandığında doğrudan paylaşabilirim."
                ),
                db_data={"registration_period_configured": False},
                sources=[],
                include_contact_suggestion=True,
                success=True,
            )

        return await super().handle_department_task(task)

    async def _try_handle_capability_plan(
        self,
        query_text: str,
        metadata: dict,
    ) -> DepartmentResponse | None:
        planner_payload = metadata.get("capability_planner")
        if not isinstance(planner_payload, dict) or not planner_payload.get("apply"):
            return None

        action_payload = planner_payload.get("action")
        if not isinstance(action_payload, dict):
            return None
        try:
            action = CapabilityAction.model_validate(action_payload)
        except Exception:
            return None

        if action.is_none() or action.capability != "calendar.academic_date":
            return None
        if action.confidence < settings.capability_planner.confidence_threshold:
            return None

        result = await execute_capability_action(action)
        if not result.success:
            return None
        if not result.records:
            return None

        answer = deterministic_answer_for_result(
            query=query_text,
            capability=result.capability,
            records=result.records,
            metadata=result.metadata,
            message=result.message,
        )
        source = result.metadata.get("source")
        sources = []
        if source:
            sources.append(
                RAGSource(
                    content=answer,
                    score=1.0,
                    metadata={
                        "source": source,
                        "record_type": "academic_calendar",
                    },
                )
            )
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data={
                "query": query_text,
                "capability": result.capability,
                "params": result.params,
                "records": result.records,
                "metadata": result.metadata,
                "message": result.message,
            },
            generation_mode="vt",
            sources=sources,
            include_contact_suggestion=True,
            success=True,
            metadata={
                "capability_planner": {
                    "mode": planner_payload.get("mode"),
                    "capability": result.capability,
                    "confidence": action.confidence,
                    "record_count": len(result.records),
                    "message": result.message,
                }
            },
        )

    def _prepare_policy_lookup_task(
        self,
        task: Task,
        query_text: str,
        metadata: dict,
    ) -> Task:
        planner_payload = metadata.get("capability_planner")
        if not isinstance(planner_payload, dict) or not planner_payload.get("apply"):
            return task
        action_payload = planner_payload.get("action")
        if not isinstance(action_payload, dict):
            return task
        try:
            action = CapabilityAction.model_validate(action_payload)
        except Exception:
            return task
        if action.capability != "student_affairs.policy_lookup":
            return task
        if action.confidence < settings.capability_planner.confidence_threshold:
            return task

        params = dict(action.params or {})
        answer_contract = dict(action.answer_contract or {})
        evidence_contract = dict(action.evidence_contract or {})
        if params.get("must_answer") and not answer_contract.get("must_answer"):
            answer_contract["must_answer"] = params.get("must_answer")
        if params.get("preferred_sources") and not evidence_contract.get("preferred_sources"):
            evidence_contract["preferred_sources"] = params.get("preferred_sources")

        preferred_sources = [
            str(source).strip()
            for source in (evidence_contract.get("preferred_sources") or [])
            if str(source).strip()
        ]
        retrieval_parts = [
            params.get("query") or query_text,
            params.get("topic"),
            params.get("question_type"),
            *(answer_contract.get("must_answer") or []),
            *preferred_sources,
        ]
        retrieval_query_parts: list[str] = []
        seen_retrieval_parts: set[str] = set()
        for part in retrieval_parts:
            text = str(part or "").strip()
            if not text:
                continue
            key = text.casefold()
            if key in seen_retrieval_parts:
                continue
            seen_retrieval_parts.add(key)
            retrieval_query_parts.append(text)

        source_refs = list(metadata.get("conversation_source_refs") or [])
        for source in preferred_sources:
            if source not in source_refs:
                source_refs.append(source)

        updated_metadata = dict(metadata)
        updated_metadata["force_llm_synthesis"] = True
        if source_refs:
            updated_metadata["conversation_source_refs"] = source_refs
        updated_metadata["policy_lookup"] = {
            "intent": action.intent,
            "topic": params.get("topic"),
            "question_type": params.get("question_type"),
            "query": params.get("query") or query_text,
        }
        updated_metadata["policy_facet"] = resolve_policy_facet(
            query=params.get("query") or query_text,
            params=params,
            answer_contract=answer_contract,
        )
        updated_metadata["retrieval_query"] = " ".join(retrieval_query_parts) or query_text
        updated_metadata["plan_decision"] = action.to_plan_decision().model_dump()
        if answer_contract:
            updated_metadata["answer_contract"] = answer_contract
        if evidence_contract:
            updated_metadata["evidence_contract"] = evidence_contract

        try:
            return task.model_copy(update={"metadata": updated_metadata}, deep=True)
        except AttributeError:
            task.metadata = updated_metadata
            return task

    @staticmethod
    def _is_timing_query(query_text: str) -> bool:
        return is_registration_timing_query(query_text)

    def _should_force_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        if should_force_registration_llm_synthesis(query_text, results):
            return True
        return super()._should_force_llm_synthesis(
            query_text,
            results,
            db_context=db_context,
        )

    def _should_use_llm_evidence_selection(
        self,
        query_text: str,
        evidence_items: Sequence,
        *,
        force_llm: bool,
        db_context: str | None = None,
    ) -> bool:
        if is_course_registration_process_query(query_text):
            return False
        return super()._should_use_llm_evidence_selection(
            query_text,
            evidence_items,
            force_llm=force_llm,
            db_context=db_context,
        )

    def _should_enrich_results(self, query_text: str, results: Sequence[dict]) -> bool:
        if should_skip_registration_result_enrichment(query_text):
            return False
        return super()._should_enrich_results(query_text, results)

    def _llm_synthesis_timeout_seconds(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        llm_profile: str | None = None,
    ) -> float:
        if should_skip_registration_result_enrichment(query_text):
            return 4.0
        return super()._llm_synthesis_timeout_seconds(
            query_text,
            results,
            llm_profile=llm_profile,
        )

    def _filter_results_for_answer(
        self,
        query_text: str,
        results: Sequence[dict],
    ) -> list[dict]:
        filtered_results = filter_registration_answer_results(query_text, results)
        if is_course_registration_process_query(query_text):
            return rank_course_registration_process_results(
                filtered_results,
                query_text=query_text,
            )[:5]
        return rank_registration_results(
            filtered_results,
            query_text=query_text,
        )[:8]

    def _search_top_k(self, query_text: str, metadata: dict) -> int | None:
        _ = metadata
        return preferred_registration_search_top_k(query_text)

    def _build_source_only_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        if is_course_registration_process_query(query_text):
            prefix = f"{db_context}\n\n" if db_context else ""
            return (
                prefix
                + "Ders kaydınızı akademik takvimde belirtilen süre içinde "
                "ubys.omu.edu.tr adresinden/öğrenci bilgi sistemi üzerinden yapabilirsiniz. "
                "Kayıt öncesinde müfredat durumunuzu kontrol edin; ders seçimini tamamladıktan sonra "
                "danışman onayına gönderin. Danışman onayı olmayan ders kayıtları geçersizdir.\n\n"
                "(Kaynak: sık_sorulan_sorular.txt)"
            )

        preferred = self._pick_preferred_result(query_text, results)
        if preferred is None:
            return super()._build_source_only_answer(query_text, results, db_context=db_context)
        if should_reject_registration_source_only_result(query_text, preferred):
            safer_results = [
                item
                for item in results
                if not should_reject_registration_source_only_result(query_text, item)
            ]
            if safer_results:
                preferred = self._pick_preferred_result(query_text, safer_results)
            else:
                prefix = f"{db_context}\n\n" if db_context else ""
                return (
                    prefix
                    + "Bu konuda öğrenci işleri kaynaklarında doğrudan teyit edebildiğim net bir cevap bulamadım. "
                    "Soruyu biraz daha açık sorarsan zaman, belge veya koşul bilgisini daha doğru daraltabilirim."
                )

        content = self._compact_source_content(preferred.get("content", ""), max_len=None)
        source = preferred.get("source", "bilinmiyor")
        intro = build_registration_intro(query_text)
        prefix = f"{db_context}\n\n" if db_context else ""
        return f"{prefix}{intro}\n{content}\n\n(Kaynak: {source})"

    def _pick_preferred_result(self, query_text: str, results: Sequence[dict]) -> dict | None:
        return pick_preferred_registration_result(query_text, results)
