"""Duyuru sorgulama yardimcilari."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import re

from sqlalchemy import Select, desc, or_, select

from src.core.constants import Department
from src.core.text_normalization import iter_alias_matches_longest_first, normalize_text
from src.db.connection import get_session
from src.db.support_models import Announcement, AnnouncementLink

_ANNOUNCEMENT_STOPWORDS = {
    "acaba",
    "ait",
    "ama",
    "ben",
    "bir",
    "biri",
    "bu",
    "da",
    "daha",
    "de",
    "duyuru",
    "duyurular",
    "duyurulari",
    "duyuruları",
    "gibi",
    "guncel",
    "güncel",
    "hangi",
    "ilgili",
    "alakali",
    "icin",
    "için",
    "ile",
    "link",
    "linki",
    "mi",
    "mu",
    "mı",
    "mü",
    "nasil",
    "nasıl",
    "nedir",
    "ne",
    "neler",
    "olan",
    "olarak",
    "son",
    "ve",
    "var",
}
_ANNOUNCEMENT_LINK_NOISE_LABELS = {
    "is akis surecleri",
}
_ANNOUNCEMENT_LINK_NOISE_URL_PARTS = {
    "/home/isakis.pdf",
}
_ANNOUNCEMENT_UNIT_ALIASES: dict[str, tuple[str, ...]] = {
    "Bilgisayar Muhendisligi": (
        "bilgisayar muhendisligi",
        "bilgisayar muhendisligi bolumu",
        "bil muh",
        "bilgisayar muh",
    ),
    "Matematik ve Fen Bilimleri Egitimi": (
        "matematik ve fen bilimleri egitimi",
        "matematik fen bilimleri egitimi",
        "mfbeb",
    ),
    "Guzel Sanatlar Egitimi": (
        "guzel sanatlar egitimi",
        "guzel sanatlar egitimi bolumu",
        "guzel sanatlar",
    ),
    "Elektrik Elektronik Muhendisligi": (
        "elektrik elektronik muhendisligi",
        "elektrik elektronik muhendisligi bolumu",
        "elektrik elktronik muhendisligi",
        "elektrik-elektronik muhendisligi",
        "elektrik elektronik",
        "elektrik elktronik",
        "eem",
        "eem bolumu",
        "eem muhendisligi",
        "ee muh",
    ),
    "Fizik": (
        "fizik bolumu",
        "fizik",
    ),
    "Istatistik": (
        "istatistik bolumu",
        "istatistik",
        "istat",
    ),
}
_ANNOUNCEMENT_FACULTY_ALIASES: dict[str, tuple[str, ...]] = {
    "Muhendislik Fakultesi": (
        "muhendislik fakultesi",
        "muhendislik fakultesindeki",
        "muhendislikteki",
    ),
    "Fen Fakultesi": (
        "fen fakultesi",
        "fen fakultesindeki",
        "fendeki",
    ),
    "Fen Edebiyat Fakultesi": (
        "fen edebiyat fakultesi",
        "fen edebiyattaki",
        "fen edebiyatteki",
        "fen edebiyatta",
    ),
    "Egitim Fakultesi": (
        "egitim fakultesi",
        "egitim fakultesindeki",
        "egitimdeki",
    ),
}
_LATEST_ANNOUNCEMENT_MARKERS = (
    "son duyurular",
    "son duyuru",
    "guncel duyurular",
    "guncel duyuru",
    "son haberler",
    "guncel haberler",
)


@dataclass(frozen=True)
class AnnouncementRecord:
    """Agent katmanina donen duyuru ozet modeli."""

    id: int
    title: str
    display_summary: str | None
    summary: str | None
    original_text: str | None
    source_url: str | None
    faculty: str | None
    unit_name: str | None
    department: str | None
    published_at: datetime | None
    links: tuple["AnnouncementLinkRecord", ...] = field(default_factory=tuple)
    content_hash: str | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class AnnouncementLinkRecord:
    """Small view model for stored announcement attachment links."""

    label: str
    url: str
    link_type: str


_ANNOUNCEMENT_SOURCE_REF_RE = re.compile(
    r"^announcement:(?P<id>\d+)(?::(?P<version>[a-zA-Z0-9_-]{6,80}))?$"
)


def build_announcement_source_ref(
    *,
    announcement_id: int,
    content_hash: str | None = None,
    updated_at: datetime | None = None,
) -> str:
    """Build a stable, versioned reference for follow-up/detail requests."""

    version = ""
    if content_hash:
        version = content_hash[:12]
    elif updated_at is not None:
        version = str(int(updated_at.timestamp()))
    return f"announcement:{announcement_id}:{version}" if version else f"announcement:{announcement_id}"


def parse_announcement_source_ref(value: object | None) -> tuple[int, str | None] | None:
    """Parse a versioned announcement reference from conversation state."""

    text = str(value or "").strip()
    match = _ANNOUNCEMENT_SOURCE_REF_RE.match(text)
    if not match:
        return None
    return int(match.group("id")), match.group("version")


def extract_announcement_keywords(query_text: str) -> list[str]:
    """Sorgudan duyuru aramada kullanilacak anahtar kelimeleri ayiklar."""

    tokens = re.findall(r"[a-z0-9]{3,}", normalize_text(query_text))
    seen: set[str] = set()
    keywords: list[str] = []

    for token in tokens:
        if token in _ANNOUNCEMENT_STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        keywords.append(token)

    return keywords[:6]


def _apply_department_filters(
    stmt: Select[tuple[Announcement]],
    *,
    department: Department | str | list[str] | tuple[str, ...] | None,
    faculty: str | None,
    include_general_faculty: bool = True,
    unit_name: str | None = None,
    include_general_unit: bool = True,
) -> Select[tuple[Announcement]]:
    department_values: list[str] = []
    if isinstance(department, Department):
        department_values = [department.value]
    elif isinstance(department, (list, tuple)):
        department_values = [str(item).strip() for item in department if str(item).strip()]
    elif department:
        department_values = [str(department).strip()]

    if department_values:
        stmt = stmt.where(
            or_(
                Announcement.department.in_(department_values),
                Announcement.department.is_(None),
            )
        )
    if faculty:
        if include_general_faculty:
            stmt = stmt.where(
                or_(
                    Announcement.faculty == faculty,
                    Announcement.faculty.is_(None),
                )
            )
        else:
            stmt = stmt.where(Announcement.faculty == faculty)
    if unit_name:
        if include_general_unit:
            stmt = stmt.where(
                or_(
                    Announcement.unit_name == unit_name,
                    Announcement.unit_name.is_(None),
                )
            )
        else:
            stmt = stmt.where(Announcement.unit_name == unit_name)
    return stmt


def _detect_unit_scope(query_text: str) -> str | None:
    normalized_query = normalize_text(query_text)
    for unit_name, alias in iter_alias_matches_longest_first(_ANNOUNCEMENT_UNIT_ALIASES.items()):
        if alias in normalized_query:
            return unit_name
    return None


def _detect_faculty_scope(query_text: str) -> str | None:
    normalized_query = normalize_text(query_text)
    for faculty_name, alias in iter_alias_matches_longest_first(_ANNOUNCEMENT_FACULTY_ALIASES.items()):
        if alias in normalized_query:
            return faculty_name
    return None


def _query_requests_latest_scoped_announcements(
    query_text: str,
    *,
    faculty: str | None,
    unit_name: str | None,
) -> bool:
    normalized_query = normalize_text(query_text)
    if not any(marker in normalized_query for marker in _LATEST_ANNOUNCEMENT_MARKERS):
        return False
    if not (faculty or unit_name):
        return False

    scope_aliases: list[str] = []
    if unit_name:
        normalized_unit = normalize_text(unit_name)
        scope_aliases.append(normalized_unit)
        scope_aliases.extend(_ANNOUNCEMENT_UNIT_ALIASES.get(unit_name, ()))
    if faculty:
        normalized_faculty = normalize_text(faculty)
        scope_aliases.append(normalized_faculty)
        scope_aliases.extend(_ANNOUNCEMENT_FACULTY_ALIASES.get(faculty, ()))

    candidate_keywords = extract_announcement_keywords(normalized_query)
    if not candidate_keywords:
        return True

    def _is_scope_keyword(keyword: str) -> bool:
        variants = {
            keyword,
            keyword.removesuffix("ki"),
            keyword.removesuffix("deki"),
            keyword.removesuffix("daki"),
            keyword.removesuffix("teki"),
            keyword.removesuffix("taki"),
        }
        for alias in scope_aliases:
            alias_tokens = re.findall(r"[a-z0-9]+", alias)
            for variant in variants:
                if not variant:
                    continue
                if variant in alias_tokens:
                    return True
                if any(
                    variant.startswith(alias_token) or alias_token.startswith(variant)
                    for alias_token in alias_tokens
                ):
                    return True
                if variant in alias or alias in variant:
                    return True
        return False

    return all(_is_scope_keyword(keyword) for keyword in candidate_keywords)


def _apply_keyword_filters(
    stmt: Select[tuple[Announcement]],
    *,
    keywords: list[str],
) -> Select[tuple[Announcement]]:
    if not keywords:
        return stmt

    keyword_clauses = []
    for keyword in keywords:
        pattern = f"%{keyword}%"
        keyword_clauses.append(
            or_(
                Announcement.title.ilike(pattern),
                Announcement.summary.ilike(pattern),
                Announcement.original_text.ilike(pattern),
            )
        )
    return stmt.where(or_(*keyword_clauses))


async def _execute_announcement_query(
    session,
    *,
    stmt: Select[tuple[Announcement]],
    keywords: list[str],
    query_text: str,
    recent_cutoff: datetime,
    limit: int,
    recent_only: bool,
    use_keywords: bool = True,
) -> list[Announcement]:
    if recent_only:
        stmt = stmt.where(
            or_(
                Announcement.published_at.is_(None),
                Announcement.published_at >= recent_cutoff,
            )
        )

    fetch_limit = max(limit * 30, 120) if use_keywords and keywords else max(limit * 10, 30)
    stmt = stmt.order_by(
        Announcement.published_at.desc().nulls_last(),
        desc(Announcement.last_seen_at),
        desc(Announcement.id),
    ).limit(fetch_limit)
    rows = list((await session.execute(stmt)).scalars().all())
    if use_keywords and keywords:
        rows = [
            item
            for item in rows
            if _announcement_keyword_match_score(item, keywords=keywords, query_text=query_text) > 0
        ]
        rows.sort(
            key=lambda item: (
                _announcement_keyword_match_score(item, keywords=keywords, query_text=query_text),
                item.source_id is not None,
                item.published_at or item.last_seen_at or datetime.min.replace(tzinfo=UTC),
                int(item.id),
            ),
            reverse=True,
        )
    else:
        source_backed_rows = [item for item in rows if item.source_id is not None]
        if len(source_backed_rows) >= limit:
            rows = source_backed_rows
    return rows[:limit]


def _announcement_keyword_match_score(
    item: Announcement,
    *,
    keywords: list[str],
    query_text: str,
) -> int:
    normalized_title = normalize_text(item.title or "")
    normalized_summary = normalize_text(
        " ".join(
            part for part in (
                item.display_summary,
                item.summary,
                item.original_text,
            )
            if part
        )
    )
    combined = f"{normalized_title} {normalized_summary}".strip()
    if not combined:
        return 0

    score = 0
    for keyword in keywords:
        if keyword in normalized_title:
            score += 4
        elif keyword in normalized_summary:
            score += 2

    normalized_query = normalize_text(query_text)
    for phrase in ("tek ders", "sinav programi", "ders programi", "ara sinav", "haftalik ders"):
        if phrase in normalized_query and phrase in combined:
            score += 6

    return score


def _top_announcement_match_score(
    items: list[Announcement],
    *,
    keywords: list[str],
    query_text: str,
) -> int:
    if not items or not keywords:
        return 0
    return max(
        _announcement_keyword_match_score(item, keywords=keywords, query_text=query_text)
        for item in items
    )


def _announcement_match_is_weak(
    items: list[Announcement],
    *,
    keywords: list[str],
    query_text: str,
) -> bool:
    return _top_announcement_match_score(items, keywords=keywords, query_text=query_text) < 10


async def _load_announcement_links(
    session,
    announcement_ids: list[int],
) -> dict[int, tuple[AnnouncementLinkRecord, ...]]:
    if not announcement_ids:
        return {}

    link_rows = list(
        (
            await session.execute(
                select(AnnouncementLink)
                .where(AnnouncementLink.announcement_id.in_(announcement_ids))
                .order_by(
                    AnnouncementLink.announcement_id.asc(),
                    AnnouncementLink.sort_order.asc(),
                    AnnouncementLink.id.asc(),
                )
            )
        )
        .scalars()
        .all()
    )
    grouped_links: dict[int, list[AnnouncementLinkRecord]] = {}
    for link in link_rows:
        normalized_label = normalize_text(link.label)
        normalized_url = normalize_text(link.url)
        if normalized_label in _ANNOUNCEMENT_LINK_NOISE_LABELS:
            continue
        if any(part in normalized_url for part in _ANNOUNCEMENT_LINK_NOISE_URL_PARTS):
            continue
        grouped_links.setdefault(int(link.announcement_id), []).append(
            AnnouncementLinkRecord(
                label=link.label,
                url=link.url,
                link_type=link.link_type,
            )
        )
    return {
        announcement_id: tuple(items)
        for announcement_id, items in grouped_links.items()
    }


def _announcement_to_record(
    item: Announcement,
    *,
    links: tuple[AnnouncementLinkRecord, ...] = (),
) -> AnnouncementRecord:
    return AnnouncementRecord(
        id=int(item.id),
        title=item.title,
        display_summary=item.display_summary,
        summary=item.summary,
        original_text=item.original_text,
        source_url=item.source_url,
        faculty=item.faculty,
        unit_name=item.unit_name,
        department=item.department,
        published_at=item.published_at,
        links=links,
        content_hash=item.content_hash,
        updated_at=item.updated_at,
    )


async def fetch_announcement_by_source_ref(
    source_ref: str,
) -> AnnouncementRecord | None:
    """Fetch a single active announcement by versioned conversation reference.

    If the content hash in the reference no longer matches the row, return None
    instead of silently serving a stale announcement detail.
    """

    parsed = parse_announcement_source_ref(source_ref)
    if parsed is None:
        return None
    announcement_id, version = parsed
    async with get_session() as session:
        item = await session.get(Announcement, announcement_id)
        if item is None or not item.is_active:
            return None
        if version:
            current_ref = build_announcement_source_ref(
                announcement_id=int(item.id),
                content_hash=item.content_hash,
                updated_at=item.updated_at,
            )
            if current_ref != source_ref:
                return None
        link_map = await _load_announcement_links(session, [int(item.id)])
        return _announcement_to_record(
            item,
            links=link_map.get(int(item.id), ()),
        )


async def fetch_relevant_announcements(
    query_text: str,
    *,
    department: Department | str | list[str] | tuple[str, ...] | None = None,
    faculty: str | None = None,
    unit_name: str | None = None,
    limit: int = 3,
    recent_days: int = 30,
    allow_latest_fallback: bool = True,
    probe_mode: str | None = None,
    require_keyword_match: bool = False,
    minimum_match_score: int | None = None,
) -> list[AnnouncementRecord]:
    """Sorgu ile ilgili aktif duyurulari getirir."""

    keywords = extract_announcement_keywords(query_text)
    is_supplemental_probe = normalize_text(probe_mode) == "supplemental"
    recent_cutoff = datetime.now(UTC) - timedelta(days=recent_days)
    resolved_unit_name = unit_name or _detect_unit_scope(query_text)
    resolved_faculty = faculty or _detect_faculty_scope(query_text)
    effective_keywords = keywords
    if _query_requests_latest_scoped_announcements(
        query_text,
        faculty=resolved_faculty,
        unit_name=resolved_unit_name,
    ):
        effective_keywords = []
    if require_keyword_match and not effective_keywords:
        return []
    strict_keyword_score = minimum_match_score
    if is_supplemental_probe and (strict_keyword_score is None or strict_keyword_score <= 0):
        strict_keyword_score = 10

    async with get_session() as session:
        general_only_base_stmt = (
            select(Announcement)
            .where(Announcement.is_active.is_(True))
            .where(Announcement.faculty.is_(None))
            .where(Announcement.unit_name.is_(None))
        )
        exact_base_stmt = _apply_department_filters(
            select(Announcement).where(Announcement.is_active.is_(True)),
            department=department,
            faculty=resolved_faculty,
            include_general_faculty=False,
            unit_name=resolved_unit_name,
            include_general_unit=False,
        )
        inclusive_base_stmt = _apply_department_filters(
            select(Announcement).where(Announcement.is_active.is_(True)),
            department=department,
            faculty=resolved_faculty,
            include_general_faculty=True,
            unit_name=resolved_unit_name,
            include_general_unit=True,
        )

        announcements: list[Announcement] = []

        if resolved_faculty or resolved_unit_name:
            announcements = await _execute_announcement_query(
                session,
                stmt=exact_base_stmt,
                keywords=effective_keywords,
                query_text=query_text,
                recent_cutoff=recent_cutoff,
                limit=limit,
                recent_only=True,
            )
            if announcements and effective_keywords and _announcement_match_is_weak(
                announcements,
                keywords=effective_keywords,
                query_text=query_text,
            ):
                if is_supplemental_probe:
                    announcements = []
                else:
                    older_exact = await _execute_announcement_query(
                        session,
                        stmt=exact_base_stmt,
                        keywords=effective_keywords,
                        query_text=query_text,
                        recent_cutoff=recent_cutoff,
                        limit=limit,
                        recent_only=False,
                    )
                    if _top_announcement_match_score(
                        older_exact,
                        keywords=effective_keywords,
                        query_text=query_text,
                    ) > _top_announcement_match_score(
                        announcements,
                        keywords=effective_keywords,
                        query_text=query_text,
                    ):
                        announcements = older_exact
            if not announcements and allow_latest_fallback:
                announcements = await _execute_announcement_query(
                    session,
                    stmt=exact_base_stmt,
                    keywords=effective_keywords,
                    query_text=query_text,
                    recent_cutoff=recent_cutoff,
                    limit=limit,
                    recent_only=False,
                )
            if not announcements and allow_latest_fallback and effective_keywords:
                announcements = await _execute_announcement_query(
                    session,
                    stmt=exact_base_stmt,
                    keywords=effective_keywords,
                    query_text=query_text,
                    recent_cutoff=recent_cutoff,
                    limit=limit,
                    recent_only=False,
                    use_keywords=False,
                )

        if not announcements and not faculty and not resolved_unit_name:
            announcements = await _execute_announcement_query(
                session,
                stmt=general_only_base_stmt,
                keywords=effective_keywords,
                query_text=query_text,
                recent_cutoff=recent_cutoff,
                limit=limit,
                recent_only=True,
            )
            if announcements and effective_keywords and _announcement_match_is_weak(
                announcements,
                keywords=effective_keywords,
                query_text=query_text,
            ):
                if is_supplemental_probe:
                    announcements = []
                else:
                    older_general = await _execute_announcement_query(
                        session,
                        stmt=general_only_base_stmt,
                        keywords=effective_keywords,
                        query_text=query_text,
                        recent_cutoff=recent_cutoff,
                        limit=limit,
                        recent_only=False,
                    )
                    if _top_announcement_match_score(
                        older_general,
                        keywords=effective_keywords,
                        query_text=query_text,
                    ) > _top_announcement_match_score(
                        announcements,
                        keywords=effective_keywords,
                        query_text=query_text,
                    ):
                        announcements = older_general
            if not announcements and allow_latest_fallback:
                announcements = await _execute_announcement_query(
                    session,
                    stmt=general_only_base_stmt,
                    keywords=effective_keywords,
                    query_text=query_text,
                    recent_cutoff=recent_cutoff,
                    limit=limit,
                    recent_only=False,
                )
            if not announcements and allow_latest_fallback and effective_keywords:
                announcements = await _execute_announcement_query(
                    session,
                    stmt=general_only_base_stmt,
                    keywords=effective_keywords,
                    query_text=query_text,
                    recent_cutoff=recent_cutoff,
                    limit=limit,
                    recent_only=False,
                    use_keywords=False,
                )

        if not announcements:
            announcements = await _execute_announcement_query(
                session,
                stmt=inclusive_base_stmt,
                keywords=effective_keywords,
                query_text=query_text,
                recent_cutoff=recent_cutoff,
                limit=limit,
                recent_only=True,
            )
            if announcements and effective_keywords and _announcement_match_is_weak(
                announcements,
                keywords=effective_keywords,
                query_text=query_text,
            ):
                if is_supplemental_probe:
                    announcements = []
                else:
                    older_inclusive = await _execute_announcement_query(
                        session,
                        stmt=inclusive_base_stmt,
                        keywords=effective_keywords,
                        query_text=query_text,
                        recent_cutoff=recent_cutoff,
                        limit=limit,
                        recent_only=False,
                    )
                    if _top_announcement_match_score(
                        older_inclusive,
                        keywords=effective_keywords,
                        query_text=query_text,
                    ) > _top_announcement_match_score(
                        announcements,
                        keywords=effective_keywords,
                        query_text=query_text,
                    ):
                        announcements = older_inclusive

        if not announcements and allow_latest_fallback:
            announcements = await _execute_announcement_query(
                session,
                stmt=inclusive_base_stmt,
                keywords=effective_keywords,
                query_text=query_text,
                recent_cutoff=recent_cutoff,
                limit=limit,
                recent_only=False,
            )
        if not announcements and allow_latest_fallback and effective_keywords:
            announcements = await _execute_announcement_query(
                session,
                stmt=inclusive_base_stmt,
                keywords=effective_keywords,
                query_text=query_text,
                recent_cutoff=recent_cutoff,
                limit=limit,
                recent_only=False,
                use_keywords=False,
            )

        if announcements and strict_keyword_score is not None and effective_keywords:
            announcements = [
                item
                for item in announcements
                if _announcement_keyword_match_score(
                    item,
                    keywords=effective_keywords,
                    query_text=query_text,
                ) >= strict_keyword_score
            ]

        link_map = await _load_announcement_links(
            session,
            [int(item.id) for item in announcements],
        )

        return [
            _announcement_to_record(item, links=link_map.get(int(item.id), ()))
            for item in announcements
        ]
