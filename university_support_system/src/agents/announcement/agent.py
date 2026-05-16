"""Duyuru ajani."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.text_normalization import contains_any_normalized, normalize_text
from src.db.announcements import (
    AnnouncementRecord,
    _detect_faculty_scope,
    _detect_unit_scope,
    build_announcement_source_ref,
    fetch_announcement_by_source_ref,
    fetch_relevant_announcements,
    parse_announcement_source_ref,
)
from src.db.schemas import DepartmentResponse, RAGSource
from src.llm.prompt_templates import (
    ANNOUNCEMENT_AGENT_SYSTEM_PROMPT,
    ANNOUNCEMENT_SUMMARY_REFINER_SYSTEM_PROMPT,
)


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


def _as_aware_utc(value: datetime) -> datetime:
    """Normalize DB/test datetimes before current/stale comparisons."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


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
        summary_requested = self._is_summary_follow_up(query_text)
        summary_source_ref = self._select_source_ref_for_summary_follow_up(
            query_text,
            source_refs,
        )
        if summary_requested:
            selected_item: AnnouncementRecord | None = None
            if summary_source_ref and parse_announcement_source_ref(summary_source_ref) is not None:
                selected_item = await fetch_announcement_by_source_ref(summary_source_ref)
                if selected_item is None:
                    return DepartmentResponse(
                        department=self.department,
                        answer=(
                            "Listedeki duyuru guncellenmis veya artik aktif olmayabilir. "
                            "Guncel listeyi yenilemek icin 'guncel duyurular neler?' diye sorabilirsiniz."
                        ),
                        sources=[],
                        generation_mode="vt",
                        success=True,
                    )
            elif summary_source_ref:
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
            elif self._looks_like_title_summary_request(query_text):
                selected_announcements = await self._announcement_fetcher(
                    query_text,
                    department=self._resolve_department_filter(metadata),
                    faculty=self._normalize_optional_text(metadata.get("faculty")),
                    unit_name=self._normalize_optional_text(metadata.get("unit_name")),
                    limit=1,
                    allow_latest_fallback=False,
                )
                if selected_announcements:
                    selected_item = selected_announcements[0]
            if selected_item is not None:
                return DepartmentResponse(
                    department=self.department,
                    answer=await self._format_single_announcement_summary(
                        selected_item,
                        llm_profile=self._normalize_optional_text(metadata.get("llm_profile")),
                    ),
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
            recent_days=self._safe_int(metadata.get("recent_days"), default=30, minimum=1, maximum=730),
            allow_latest_fallback=self._safe_bool(
                metadata.get("allow_latest_fallback"),
                default=self._default_allow_latest_fallback(query_text, metadata),
            ),
            probe_mode=self._normalize_optional_text(metadata.get("probe_mode")),
            require_keyword_match=self._safe_bool(metadata.get("require_keyword_match"), default=False),
            minimum_match_score=self._safe_int(metadata.get("minimum_match_score"), default=0, minimum=0, maximum=100),
        )

        has_more = len(announcements) > 5
        display_items = announcements[:5]

        if not announcements:
            if self._safe_bool(
                metadata.get("allow_latest_fallback"),
                default=self._default_allow_latest_fallback(query_text, metadata),
            ):
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

    def _default_allow_latest_fallback(self, query_text: str, metadata: dict) -> bool:
        if self._normalize_optional_text(metadata.get("faculty")):
            return False
        if self._normalize_optional_text(metadata.get("unit_name")):
            return False
        if _detect_faculty_scope(query_text) or _detect_unit_scope(query_text):
            return False
        return True

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
        if text in {"false", "0", "no", "hayir", "hayır"}:
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
                published_at = _as_aware_utc(item.published_at)
                published = f" ({published_at.date().isoformat()})"
                stale_cutoff = datetime.now(UTC) - timedelta(days=180)
                if published_at < stale_cutoff:
                    published += " ⚠ eski duyuru"

            lines.append(f"{index}. {item.title}{published}")
            lines.append(f"   {summary}")
            if item.source_url:
                lines.append(f"   Detay: {item.source_url}")
            for link in item.links[:3]:
                lines.append(f"   Ek bağlantı: {link.label} - {link.url}")

        if has_more:
            lines.append("   ... ve daha fazla duyuru var. Tümünü görmek için ilgili birim sayfasını ziyaret edin.")
        lines.append(
            'Bir duyurunun ozetini almak icin numarasini ya da basligini yazabilirsiniz: '
            '"2. duyuruyu ozetle" veya "CAP basvuru duyurusunu ozetle".'
        )
        return "\n".join(lines)

    async def _format_single_announcement_summary(
        self,
        item: AnnouncementRecord,
        *,
        llm_profile: str | None = None,
    ) -> str:
        llm_summary = await self._try_generate_llm_summary(item, llm_profile=llm_profile)
        summary = (
            llm_summary
            or item.display_summary
            or item.summary
            or item.original_text
            or "Özet bilgisi bulunmuyor."
        ).strip()
        summary = " ".join(summary.split())
        if len(summary) > 1000:
            summary = f"{summary[:997].rstrip()}..."

        lines = [f"Duyuru özeti: {item.title}"]
        if item.published_at is not None:
            lines.append(f"Tarih: {_as_aware_utc(item.published_at).date().isoformat()}")
        lines.append(summary)
        if item.source_url:
            lines.append(f"Detay: {item.source_url}")
        for link in item.links[:5]:
            lines.append(f"Ek bağlantı: {link.label} - {link.url}")
        return "\n".join(lines)

    async def _try_generate_llm_summary(
        self,
        item: AnnouncementRecord,
        *,
        llm_profile: str | None = None,
    ) -> str | None:
        if not self._should_use_llm_summary(item):
            return None
        generator = getattr(self.llm_service, "generate", None)
        if generator is None:
            return None

        body = (item.original_text or item.summary or item.display_summary or "").strip()
        if len(body) > 3500:
            body = f"{body[:3500].rstrip()}..."
        prompt = "\n".join(
            [
                f"Duyuru basligi: {item.title}",
                f"Yayin tarihi: {_as_aware_utc(item.published_at).date().isoformat() if item.published_at else 'Belirtilmemis'}",
                "Duyuru metni:",
                body,
            ]
        )
        try:
            generated = await generator(
                prompt,
                system=ANNOUNCEMENT_SUMMARY_REFINER_SYSTEM_PROMPT,
                model_role="final_refinement",
                llm_profile=llm_profile,
            )
        except Exception:
            return None

        cleaned = " ".join(str(generated or "").split()).strip()
        if not cleaned:
            return None
        if len(cleaned) > 1000:
            cleaned = f"{cleaned[:997].rstrip()}..."
        return cleaned

    def _should_use_llm_summary(self, item: AnnouncementRecord) -> bool:
        original = " ".join(str(item.original_text or "").split())
        if len(original) < 320:
            return False
        existing = " ".join(str(item.display_summary or item.summary or "").split())
        if not existing:
            return True
        return normalize_text(original) != normalize_text(existing)

    def _is_summary_follow_up(self, query_text: str) -> bool:
        normalized_query = normalize_text(query_text)
        return contains_any_normalized(
            normalized_query,
            _ANNOUNCEMENT_SUMMARY_FOLLOW_UP_MARKERS,
        )

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
            if self._looks_like_title_summary_request(normalized_query):
                return None
            selected_index = 0
        if selected_index < 0 or selected_index >= len(source_refs):
            return None
        return source_refs[selected_index]

    def _looks_like_title_summary_request(self, query_text: str) -> bool:
        normalized_query = normalize_text(query_text)
        if not contains_any_normalized(
            normalized_query,
            _ANNOUNCEMENT_SUMMARY_FOLLOW_UP_MARKERS,
        ):
            return False
        tokens = {
            token.rstrip(".")
            for token in re.findall(
                r"\b\d+\.?\b|[a-zçğıöşü]+",
                normalized_query,
                flags=re.IGNORECASE,
            )
        }
        ignored = set(_ANNOUNCEMENT_ORDINAL_INDEXES)
        ignored.update(
            {
                "baslik",
                "basligi",
                "detay",
                "detayi",
                "devami",
                "duyuru",
                "duyurular",
                "duyurulari",
                "duyurunun",
                "duyurusu",
                "duyurusunu",
                "duyuruyu",
                "haber",
                "haberi",
                "icerik",
                "ilan",
                "ilani",
                "link",
                "linki",
                "numara",
                "numarasi",
                "ozet",
                "ozeti",
                "ozetle",
            }
        )
        return bool(tokens - ignored)

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
        content_hash = getattr(item, "content_hash", None)
        updated_at = getattr(item, "updated_at", None)
        source_ref = build_announcement_source_ref(
            announcement_id=item.id,
            content_hash=content_hash,
            updated_at=updated_at,
        )
        return RAGSource(
            content=item.summary or item.original_text or item.title,
            score=1.0,
            metadata={
                "record_type": "announcement",
                "announcement_id": item.id,
                "source_ref": source_ref,
                "cache_version": source_ref,
                "content_hash": content_hash,
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
                "updated_at": updated_at.isoformat() if updated_at else None,
            },
        )
