"""Duyuru ajani."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.text_normalization import contains_any_normalized, normalize_text
from src.db.announcements import AnnouncementRecord, fetch_relevant_announcements
from src.db.schemas import DepartmentResponse, RAGSource
from src.llm.prompt_templates import ANNOUNCEMENT_AGENT_SYSTEM_PROMPT


_ANNOUNCEMENT_SUMMARY_FOLLOW_UP_MARKERS: tuple[str, ...] = (
    "ozet",
    "ozeti",
    "ozetle",
    "özet",
    "özeti",
    "özetle",
    "detay",
    "detayi",
    "icerik",
    "içerik",
    "devami",
    "devamı",
    "link",
    "linki",
)

_ANNOUNCEMENT_ORDINAL_INDEXES: dict[str, int] = {
    "ilk": 0,
    "birinci": 0,
    "1": 0,
    "ikinci": 1,
    "ikincisi": 1,
    "2": 1,
    "ucuncu": 2,
    "ucuncusu": 2,
    "üçüncü": 2,
    "üçüncüsü": 2,
    "3": 2,
    "dorduncu": 3,
    "dorduncusu": 3,
    "dördüncü": 3,
    "dördüncüsü": 3,
    "4": 3,
    "besinci": 4,
    "besincisi": 4,
    "beşinci": 4,
    "beşincisi": 4,
    "5": 4,
}


class AnnouncementAgent(BaseSpecialistAgent):
    """Aktif duyurulari veritabanindan okuyup kisa cevap ureten ajan."""

    def __init__(
        self,
        *,
        announcement_fetcher: Callable[..., Awaitable[list[AnnouncementRecord]]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="announcement_agent",
                name="Announcement Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Genel duyuru sorgulari icin veritabani destekli duyuru ajani.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Son duyurular neler?",),
                tags=("announcement", "shared"),
                system_prompt=ANNOUNCEMENT_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._announcement_fetcher = announcement_fetcher or fetch_relevant_announcements

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        if not query_text:
            query_text = self._extract_query_from_task(task)

        source_refs = self._normalize_source_refs(metadata.get("conversation_source_refs"))
        summary_source_ref = self._select_source_ref_for_summary_follow_up(
            query_text,
            source_refs,
        )
        if summary_source_ref:
            selected_announcements = await self._announcement_fetcher(
                summary_source_ref,
                department=self._resolve_department_filter(metadata),
                faculty=self._normalize_optional_text(metadata.get("faculty")),
                unit_name=self._normalize_optional_text(metadata.get("unit_name")),
                limit=1,
                allow_latest_fallback=False,
            )
            if selected_announcements:
                selected_item = selected_announcements[0]
                return DepartmentResponse(
                    department=self.department,
                    answer=self._format_single_announcement_summary(selected_item),
                    sources=[self._build_source(selected_item)],
                    generation_mode="vt",
                    success=True,
                )

        announcements = await self._announcement_fetcher(
            query_text,
            department=self._resolve_department_filter(metadata),
            faculty=self._normalize_optional_text(metadata.get("faculty")),
            unit_name=self._normalize_optional_text(metadata.get("unit_name")),
            limit=self._safe_int(metadata.get("limit"), default=8, minimum=1, maximum=10),
            allow_latest_fallback=self._safe_bool(
                metadata.get("allow_latest_fallback"),
                default=True,
            ),
        )

        has_more = len(announcements) > 5
        display_items = announcements[:5]

        if not announcements:
            if self._safe_bool(metadata.get("allow_latest_fallback"), default=True):
                answer = (
                    "Şu anda sistemde kayıtlı aktif duyuru bulunmuyor. "
                    "Duyuru verileri yüklendiğinde en güncel duyuruları doğrudan listeleyebilirim."
                )
            else:
                answer = (
                    "Bu arama için ilgili aktif duyuru bulunamadı. "
                    "Daha genel duyuruları listelemek isterseniz 'güncel duyurular neler?' diye sorabilirsiniz."
                )
            sources: list[RAGSource] = []
        else:
            answer = self._format_announcements(display_items, has_more=has_more)
            sources = [self._build_source(item) for item in display_items]

        return DepartmentResponse(
            department=self.department,
            answer=answer,
            sources=sources,
            generation_mode="vt",
            success=True,
        )

    def _resolve_department_filter(self, metadata: dict) -> str | list[str] | None:
        department = self._normalize_optional_text(metadata.get("department"))
        if department:
            return department

        departments = metadata.get("departments")
        if isinstance(departments, (list, tuple)) and departments:
            resolved_departments = [
                normalized
                for normalized in (
                    self._normalize_optional_text(item) for item in departments
                )
                if normalized is not None
            ]
            if resolved_departments:
                return resolved_departments

        return None

    def _normalize_optional_text(self, value) -> str | None:
        text = str(value).strip() if value is not None else ""
        return text or None

    def _safe_int(self, value, *, default: int, minimum: int, maximum: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = default
        return max(minimum, min(parsed, maximum))

    def _safe_bool(self, value, *, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"true", "1", "yes", "evet"}:
            return True
        if text in {"false", "0", "no", "hayir", "hayÄ±r"}:
            return False
        return default

    def _format_announcements(self, announcements: list[AnnouncementRecord], *, has_more: bool = False) -> str:
        lines = ["İlgili duyurular:"]

        for index, item in enumerate(announcements[:5], start=1):
            summary = (
                item.display_summary
                or item.summary
                or item.original_text
                or "Özet bilgisi bulunmuyor."
            ).strip()
            if len(summary) > 280:
                summary = f"{summary[:277].rstrip()}..."

            published = ""
            if item.published_at is not None:
                published = f" ({item.published_at.date().isoformat()})"
                stale_cutoff = datetime.now(UTC) - timedelta(days=180)
                if item.published_at < stale_cutoff:
                    published += " ⚠ eski duyuru"

            lines.append(f"{index}. {item.title}{published}")
            lines.append(f"   {summary}")
            if item.source_url:
                lines.append(f"   Detay: {item.source_url}")
            for link in item.links[:3]:
                lines.append(f"   Ek bağlantı: {link.label} - {link.url}")

        if has_more:
            lines.append("   ... ve daha fazla duyuru var. Tümünü görmek için ilgili birim sayfasını ziyaret edin.")
        lines.append('Listedeki bir duyuru için "2. duyuruyu özetle" gibi yazabilirsiniz.')
        return "\n".join(lines)

    def _format_single_announcement_summary(self, item: AnnouncementRecord) -> str:
        summary = (
            item.display_summary
            or item.summary
            or item.original_text
            or "Özet bilgisi bulunmuyor."
        ).strip()
        summary = " ".join(summary.split())
        if len(summary) > 1000:
            summary = f"{summary[:997].rstrip()}..."

        lines = [f"Duyuru özeti: {item.title}"]
        if item.published_at is not None:
            lines.append(f"Tarih: {item.published_at.date().isoformat()}")
        lines.append(summary)
        if item.source_url:
            lines.append(f"Detay: {item.source_url}")
        for link in item.links[:5]:
            lines.append(f"Ek bağlantı: {link.label} - {link.url}")
        return "\n".join(lines)

    def _select_source_ref_for_summary_follow_up(
        self,
        query_text: str,
        source_refs: list[str],
    ) -> str | None:
        if not source_refs:
            return None

        normalized_query = normalize_text(query_text)
        if not contains_any_normalized(normalized_query, _ANNOUNCEMENT_SUMMARY_FOLLOW_UP_MARKERS):
            return None

        selected_index = self._extract_ordinal_index(normalized_query)
        if selected_index is None:
            selected_index = 0
        if selected_index < 0 or selected_index >= len(source_refs):
            return None
        return source_refs[selected_index]

    def _extract_ordinal_index(self, normalized_query: str) -> int | None:
        for token in re.findall(r"\b\d+\.?\b|[a-zçğıöşü]+", normalized_query, flags=re.IGNORECASE):
            cleaned = token.rstrip(".")
            if cleaned in _ANNOUNCEMENT_ORDINAL_INDEXES:
                return _ANNOUNCEMENT_ORDINAL_INDEXES[cleaned]
        return None

    def _normalize_source_refs(self, value) -> list[str]:
        if not isinstance(value, (list, tuple)):
            return []
        refs: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                refs.append(text)
        return refs[:5]

    def _build_source(self, item: AnnouncementRecord) -> RAGSource:
        return RAGSource(
            content=item.summary or item.original_text or item.title,
            score=1.0,
            metadata={
                "record_type": "announcement",
                "announcement_id": item.id,
                "title": item.title,
                "display_summary": item.display_summary,
                "source_url": item.source_url,
                "unit_name": item.unit_name,
                "links": [
                    {
                        "label": link.label,
                        "url": link.url,
                        "link_type": link.link_type,
                    }
                    for link in item.links
                ],
                "faculty": item.faculty,
                "department": item.department,
                "published_at": item.published_at.isoformat() if item.published_at else None,
            },
        )
