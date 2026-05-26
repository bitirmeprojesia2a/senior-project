"""International and exchange-focused academic programs agent."""

from __future__ import annotations

from a2a.types import Task

from src.agents.academic.regulation_utils import (
    build_regulation_intro,
    exchange_grant_context_rank,
    incoming_exchange_context_rank,
    needs_international_finance_reference,
    pick_preferred_regulation_result,
    rank_regulation_results,
    wants_exchange_grant_info,
    wants_incoming_exchange_info,
)
from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.capabilities.models import CapabilityAction
from src.core.constants import Department, TaskType
from src.core.config import settings
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse
from src.llm.prompt_templates import INTERNATIONAL_AGENT_SYSTEM_PROMPT


class InternationalAgent(BaseSpecialistAgent):
    """Uluslararasi ogrenci uzman ajani. Harc sorularinda finance yonlendirmesi yapar."""

    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="international_agent",
                name="International Agent",
                department=Department.ACADEMIC_PROGRAMS,
                description="Uluslararasi ogrenci ve Erasmus odakli sorulara bakar.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Erasmus basvurusu nasil yapilir?", "Ikamet izni icin ne gerekir?"),
                tags=("academic_programs", "international"),
                system_prompt=INTERNATIONAL_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        task = self._prepare_policy_lookup_task(task, query_text, metadata)

        response = await super().handle_department_task(task)

        if response.success and self._needs_finance_reference(query_text):
            response = response.model_copy(
                update={
                    "answer": response.answer
                    + (
                        "\n\nNot: Uluslararası öğrenci harç ücretleri ve ödeme detayları için "
                        "finans birimi (tuition_agent) ile iletişime geçmeniz önerilir."
                    )
                }
            )

        return response

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
        if action.capability != "international.policy_lookup":
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
        if params.get("avoid_sources") and not evidence_contract.get("avoid_sources"):
            evidence_contract["avoid_sources"] = params.get("avoid_sources")

        preferred_sources = [
            str(source).strip()
            for source in (evidence_contract.get("preferred_sources") or [])
            if str(source).strip()
        ]
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
        updated_metadata["retrieval_query"] = params.get("query") or query_text
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
    def _needs_finance_reference(query_text: str) -> bool:
        return needs_international_finance_reference(query_text)

    def _build_source_only_answer(
        self,
        query_text: str,
        results: list[dict] | tuple[dict, ...],
        *,
        db_context: str | None = None,
    ) -> str:
        grant_answer = self._build_exchange_grant_answer(
            query_text,
            results,
            db_context=db_context,
        )
        if grant_answer is not None:
            return grant_answer

        preferred = self._pick_preferred_result(query_text, results)
        if preferred is None:
            return super()._build_source_only_answer(query_text, results, db_context=db_context)

        content = self._compact_source_content(preferred.get("content", ""), max_len=None)
        source = preferred.get("source", "bilinmiyor")
        prefix = f"{db_context}\n\n" if db_context else ""
        intro = build_regulation_intro(query_text)
        return f"{prefix}{intro}\n{content}\n\n(Kaynak: {source})"

    def _filter_results_for_answer(
        self,
        query_text: str,
        results: list[dict] | tuple[dict, ...],
    ) -> list[dict]:
        ranked = rank_regulation_results(query_text, results)
        if wants_incoming_exchange_info(query_text):
            incoming_results = [
                item
                for item in ranked
                if incoming_exchange_context_rank(item, True) <= 1
            ]
            if incoming_results:
                return incoming_results[:5]
        return ranked or list(results)

    def _search_top_k(self, query_text: str, metadata: dict) -> int | None:
        _ = metadata
        if wants_exchange_grant_info(query_text) or wants_incoming_exchange_info(query_text):
            return 10
        return None

    def _build_exchange_grant_answer(
        self,
        query_text: str,
        results: list[dict] | tuple[dict, ...],
        *,
        db_context: str | None = None,
    ) -> str | None:
        if not wants_exchange_grant_info(query_text):
            return None

        ranked = rank_regulation_results(query_text, results)
        payment = next(
            (item for item in ranked if exchange_grant_context_rank(item, True) == 0),
            None,
        )
        if payment is None:
            return None

        payment_text = normalize_text(payment.get("content", ""))
        source = payment.get("source", "bilinmiyor")
        lines = []
        if db_context:
            lines.append(db_context)
            lines.append("")
        lines.append(build_regulation_intro(query_text))

        if "her yil ulusal ajans" in payment_text or "ulusal ajans tarafindan belirlenir" in payment_text:
            lines.append(
                "- Kaynakta sabit bir TL/Euro hibe tutarı yer almıyor; hibe miktarı, "
                "ödeme usulü ve tarihi her yıl Ulusal Ajans tarafından belirlenir."
            )
        else:
            lines.append(
                "- Kaynakta sabit bir hibe tutarı net olarak bulunamadı; ilgili kaynak "
                "hibe ödeme koşullarını açıklıyor."
            )

        if "iki taksitte" in payment_text or "%80" in payment_text or "% 80" in payment_text:
            lines.append(
                "- Ödeme iki taksitte yapılır: ilk ödeme, öngörülen süreye göre "
                "hesaplanan hibenin %80'i; ikinci ödeme ise hareketlilik sonunda "
                "kesinleşen süreye göre yeniden hesaplanan tutardır."
            )
        if "hibe sozlesmesi" in payment_text:
            lines.append(
                "- İlk taksit öncesinde Öğrenci Hibe Sözleşmesi imzalanır; ikinci "
                "taksit için dönüş belgelerinin UİB'ye teslim edilmesi gerekir."
            )

        if any(marker in normalize_text(query_text) for marker in ("basvuru", "nasil", "surec")):
            application = self._find_exchange_application_result(ranked)
            if application is not None:
                lines.append(
                    "- Başvuru bilgileri UİB/OMÜ internet sayfalarında ve bölüm/program "
                    "duyuru alanlarında ilan edilir; öğrenciler duyuruda belirtilen "
                    "tarihler arasında başvuru yapar."
                )
                source = f"{source}; {application.get('source', 'bilinmiyor')}"
            else:
                lines.append(
                    "- Bu kaynak setinde başvuru adımlarını netleştiren ek bir parça "
                    "bulunamadı; güncel başvuru duyurusu ayrıca kontrol edilmeli."
                )

        lines.append("")
        lines.append(f"(Kaynak: {source})")
        return "\n".join(lines)

    @staticmethod
    def _find_exchange_application_result(results: list[dict]) -> dict | None:
        markers = (
            "basvurularla ilgili bilgi",
            "basvuru tarihleri",
            "duyurularda belirtilen tarihler",
            "online basvuru",
            "internet sayfalarinda",
        )
        for item in results:
            content = normalize_text(item.get("content", ""))
            if any(marker in content for marker in markers):
                return item
        return None

    def _pick_preferred_result(
        self,
        query_text: str,
        results: list[dict] | tuple[dict, ...],
    ) -> dict | None:
        return pick_preferred_regulation_result(query_text, results)
