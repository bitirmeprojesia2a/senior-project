"""Event source synchronization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlparse

from src.agents.announcement.sync import (
    HttpxAnnouncementHTTPClient,
    extract_announcement_links_from_html,
    extract_omu_announcement_text_from_html,
    extract_omu_faculty_home_text_from_html,
    extract_readable_text_from_html,
)
from src.core.text_normalization import collapse_whitespace, normalize_text
from src.db import get_session
from src.db.event_sources import (
    EventCandidate,
    EventLinkCandidate,
    EventSourceRecord,
    EventSyncStats,
    create_event_sync_run,
    finalize_event_sync_run,
    mark_event_source_sync_result,
    summarize_event_text,
    upsert_events_for_source,
)

_ANCHOR_TITLE_MIN_LENGTH = 8
_GENERIC_NAV_TITLES = frozenset(
    {
        "ana sayfa",
        "home",
        "iletisim",
        "hakkimizda",
        "duyurular",
        "haberler",
        "etkinlikler",
        "tum etkinlikler",
        "read more",
        "daha fazlasi",
        "detay",
    }
)
_EVENT_PATH_MARKERS = (
    "/tr/etkinlik",
    "/etkinlik",
)
_DATE_PATTERNS = ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d")
_TURKISH_MONTHS = {
    "oca": 1,
    "ocak": 1,
    "sub": 2,
    "subat": 2,
    "mar": 3,
    "mart": 3,
    "nis": 4,
    "nisan": 4,
    "may": 5,
    "mayis": 5,
    "haz": 6,
    "haziran": 6,
    "tem": 7,
    "temmuz": 7,
    "agu": 8,
    "agustos": 8,
    "eyl": 9,
    "eylul": 9,
    "eki": 10,
    "ekim": 10,
    "kas": 11,
    "kasim": 11,
    "ara": 12,
    "aralik": 12,
}
_DATE_RE = re.compile(r"\b(\d{1,2}[./]\d{1,2}[./]\d{4}|\d{4}-\d{2}-\d{2})\b")
_DATE_WORD_MONTH_RE = re.compile(
    r"\b(\d{1,2})\s+([A-Za-zCIGOSUacgiosu]+)\s+(\d{4})\b",
    re.IGNORECASE,
)
_MONTH_DAY_RE = re.compile(
    r"\b([A-Za-zCIGOSUacgiosu]{3,})\s+(\d{1,2})\b",
    re.IGNORECASE,
)
_TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")
_DATE_RANGE_RE = re.compile(
    r"(?P<first>\d{1,2}[./]\d{1,2}[./]\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-zCIGOSUacgiosu]+\s+\d{4})"
    r"\s*(?:-|/|–|—|ile|to)\s*"
    r"(?P<second>\d{1,2}[./]\d{1,2}[./]\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-zCIGOSUacgiosu]+\s+\d{4})",
    re.IGNORECASE,
)
_NEWS_ITEM_BLOCK_RE = re.compile(
    r'(?is)<article[^>]+class=["\'](?=[^"\']*news-item)(?=[^"\']*page-row)[^"\']*["\'][^>]*>(.*?)</article>\s*(?:<!--.*?-->)?'
)
_NEWS_ITEM_LINK_RE = re.compile(
    r'(?is)<h(?:2|3)[^>]*>.*?<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>.*?</h(?:2|3)>'
)
_NEWS_ITEM_SUMMARY_RE = re.compile(r"(?is)<p[^>]*>(.*?)</p>")
_EVENTS_PAGE_LINK_RE = re.compile(r"/tr/etkinlik(?:ler)?/page:(\d+)", re.IGNORECASE)
_LOCATION_PREFIXES = ("yer", "konum", "mekan", "mekan bilgisi", "salon", "platform")
_ORGANIZER_PREFIXES = ("duzenleyen", "organizatör", "organizer", "ev sahibi", "koordinator")
_EVENT_TYPE_KEYWORDS = (
    ("hackathon", "hackathon"),
    ("zirve", "zirve"),
    ("calistay", "calistay"),
    ("workshop", "workshop"),
    ("konferans", "konferans"),
    ("seminer", "seminer"),
    ("panel", "panel"),
    ("kurs", "kurs"),
    ("konser", "konser"),
    ("senlik", "senlik"),
    ("toren", "toren"),
    ("fuar", "fuar"),
    ("yarisma", "yarisma"),
    ("oryantasyon", "oryantasyon"),
    ("bilgilendirme", "bilgilendirme"),
    ("mezuniyet", "mezuniyet"),
    ("mezunlar", "mezunlar"),
    ("kariyer", "kariyer"),
    ("tanitim", "tanitim"),
    ("sergi", "sergi"),
    ("webinar", "webinar"),
    ("egitim", "egitim"),
    ("soylesi", "soylesi"),
)
_LEADING_EVENT_DATE_PREFIXES = (
    "tarih",
    "etkinlik tarihi",
    "baslangic",
    "baslangic tarihi",
    "baslangic saati",
    "gun",
)
_TRAILING_EVENT_DATE_PREFIXES = (
    "bitis",
    "bitis tarihi",
    "bitis saati",
)
_EVENT_SALUTATION_MARKERS = (
    "degerli",
    "kiymetli",
    "sevgili",
)
_EVENT_SIGNATURE_MARKERS = (
    "dekanligi",
    "mudurlugu",
    "koordinatorlugu",
)
_LOCATION_HINT_RE = re.compile(
    r"((?:[A-ZÇĞİÖŞÜ][^\s.;,\n]*\s+){0,4}(?:Salonu|Salonunda|Merkezi|Merkezinde|Kampusu|Kampüsü|Amfi|Amfisi))"
)
_ORGANIZER_HINT_RE = re.compile(
    r"([A-Z0-9ÇĞİÖŞÜ][^.;\n]{2,120}?)\s+tarafindan\b",
    re.IGNORECASE,
)
_SHELL_TEXT_MARKERS = (
    "toggle navigation",
    "copyright",
    "hizli linkler",
    "bize ulasin",
    "omu de yasam",
    "powered by grav",
)
_LOCATION_LINE_HINTS = (
    "salonu",
    "salonunda",
    "kampusu",
    "kampusunde",
    "merkezi",
    "merkezinde",
    "zoom",
    "teams",
    "youtube",
    "online",
)


@dataclass(frozen=True)
class EventReference:
    """Minimal link extracted from an event listing page."""

    title: str
    source_url: str
    teaser: str | None = None
    starts_at: datetime | None = None
    location: str | None = None
    date_hint: str | None = None
    time_hint: str | None = None


@dataclass(frozen=True)
class EventSourceSyncResult:
    """User-facing sync result for a single source."""

    source: EventSourceRecord
    status: str
    stats: EventSyncStats
    error_message: str | None = None


@dataclass(frozen=True)
class _ParsedDateTime:
    value: datetime
    has_time: bool


class EventHTTPClient(HttpxAnnouncementHTTPClient):
    """Default HTTP client for event synchronization."""


class _AnchorCollector(HTMLParser):
    """Collect anchors from an HTML page with lightweight title heuristics."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._anchors: list[tuple[str | None, str]] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = dict(attrs)
        self._current_href = attr_map.get("href")
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is None:
            return
        cleaned = collapse_whitespace(data)
        if cleaned:
            self._current_text.append(cleaned)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current_href is None:
            return
        title = collapse_whitespace(" ".join(self._current_text))
        self._anchors.append((self._current_href, title))
        self._current_href = None
        self._current_text = []

    @property
    def anchors(self) -> list[tuple[str | None, str]]:
        return self._anchors


def _build_dry_run_stats(candidates: list[EventCandidate]) -> EventSyncStats:
    seen_keys: set[str] = set()
    unique_count = 0
    for candidate in candidates:
        dedupe_key = candidate.source_url or normalize_text(candidate.title)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        unique_count += 1
    return EventSyncStats(
        items_found=len(candidates),
        items_inserted=unique_count,
        items_updated=0,
        items_deactivated=0,
    )


def _normalize_reference_url(raw_href: str | None, *, base_url: str) -> str | None:
    if not raw_href:
        return None
    cleaned = collapse_whitespace(raw_href)
    if not cleaned or cleaned.startswith("#") or cleaned.lower().startswith("javascript:"):
        return None
    resolved = urljoin(base_url, cleaned)
    parsed = urlparse(resolved)
    if not parsed.scheme.startswith("http") or not parsed.netloc:
        return None
    return resolved


def _clean_html_fragment(fragment: str | None) -> str | None:
    if not fragment:
        return None
    text = re.sub(r"(?is)<[^>]+>", " ", fragment)
    text = collapse_whitespace(unescape(text))
    return text or None


def _looks_like_valid_event_title(title: str | None) -> bool:
    compact = collapse_whitespace(title)
    if len(compact) < _ANCHOR_TITLE_MIN_LENGTH:
        return False
    return normalize_text(compact) not in _GENERIC_NAV_TITLES


def _is_event_url(source_url: str) -> bool:
    parsed = urlparse(source_url)
    normalized_path = normalize_text(parsed.path)
    return any(marker in normalized_path for marker in _EVENT_PATH_MARKERS)


def _extract_references_from_cards(
    html: str,
    *,
    base_url: str,
    max_items: int,
) -> list[EventReference]:
    references: list[EventReference] = []
    seen_urls: set[str] = set()
    base_domain = urlparse(base_url).netloc
    for block_match in _NEWS_ITEM_BLOCK_RE.finditer(html):
        block = block_match.group(1)
        link_match = _NEWS_ITEM_LINK_RE.search(block)
        if link_match is None:
            continue
        source_url = _normalize_reference_url(link_match.group(1), base_url=base_url)
        if source_url is None or not _is_event_url(source_url):
            continue
        parsed = urlparse(source_url)
        if base_domain and parsed.netloc and parsed.netloc != base_domain:
            continue
        title = _clean_html_fragment(link_match.group(2))
        if not _looks_like_valid_event_title(title):
            continue
        if source_url in seen_urls:
            continue
        teaser_match = _NEWS_ITEM_SUMMARY_RE.search(block)
        teaser = _clean_html_fragment(teaser_match.group(1)) if teaser_match else None
        starts_at, _, _ = _extract_event_window(teaser or "")
        location = _extract_location(teaser or "")
        seen_urls.add(source_url)
        references.append(
            EventReference(
                title=title or "",
                source_url=source_url,
                teaser=teaser,
                starts_at=starts_at,
                location=location,
            )
        )
        if len(references) >= max_items:
            break
    return references


def _extract_listing_context(
    html: str,
    *,
    title: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    lines = [
        collapse_whitespace(line)
        for line in extract_readable_text_from_html(html).splitlines()
        if collapse_whitespace(line)
    ]
    normalized_title = normalize_text(title)
    if not normalized_title:
        return None, None, None, None

    indices = [
        index
        for index, line in enumerate(lines)
        if normalize_text(line) == normalized_title
    ]
    for index in indices:
        before = list(reversed(lines[max(0, index - 2) : index]))
        after = lines[index + 1 : index + 5]
        date_hint = next(
            (
                line
                for line in before + after
                if _DATE_RE.search(line) or _DATE_WORD_MONTH_RE.search(line) or _MONTH_DAY_RE.search(line)
            ),
            None,
        )
        time_hint = next((line for line in after if _TIME_RE.search(line)), None)
        location = next(
            (
                line
                for line in after
                if normalize_text(line) != normalized_title
                and any(hint in normalize_text(line) for hint in _LOCATION_LINE_HINTS)
            ),
            None,
        )
        if time_hint:
            time_match = _TIME_RE.search(time_hint)
            if time_match is not None:
                time_hint = time_match.group(0)
                if location is None:
                    inline_location = collapse_whitespace(time_hint and after[after.index(next(line for line in after if _TIME_RE.search(line)))] or "")
                    inline_location = collapse_whitespace(inline_location[time_match.end() :])
                    location = location or _sanitize_location(inline_location)
        teaser_parts = [part for part in (date_hint, time_hint, location) if part]
        teaser = " ".join(teaser_parts) if teaser_parts else None
        if teaser or date_hint or time_hint or location:
            return teaser, date_hint, time_hint, location
    return None, None, None, None


def _enrich_references_from_listing_html(
    references: list[EventReference],
    *,
    html: str,
) -> list[EventReference]:
    enriched: list[EventReference] = []
    for reference in references:
        teaser, date_hint, time_hint, location = _extract_listing_context(
            html,
            title=reference.title,
        )
        enriched.append(
            EventReference(
                title=reference.title,
                source_url=reference.source_url,
                teaser=reference.teaser or teaser,
                starts_at=reference.starts_at,
                location=_sanitize_location(reference.location or location),
                date_hint=date_hint,
                time_hint=time_hint,
            )
        )
    return enriched


def extract_event_references_from_html(
    html: str,
    *,
    base_url: str,
    max_items: int,
) -> list[EventReference]:
    """Extract event detail links from a listing page."""

    card_references = _extract_references_from_cards(
        html,
        base_url=base_url,
        max_items=max_items,
    )
    if card_references:
        return _enrich_references_from_listing_html(card_references, html=html)

    parser = _AnchorCollector()
    parser.feed(html)
    seen_urls: set[str] = set()
    references: list[EventReference] = []
    base_domain = urlparse(base_url).netloc

    for raw_href, raw_title in parser.anchors:
        source_url = _normalize_reference_url(raw_href, base_url=base_url)
        if source_url is None or not _is_event_url(source_url):
            continue
        parsed = urlparse(source_url)
        if base_domain and parsed.netloc and parsed.netloc != base_domain:
            continue
        title = collapse_whitespace(raw_title)
        if not _looks_like_valid_event_title(title):
            continue
        if source_url in seen_urls:
            continue
        seen_urls.add(source_url)
        references.append(
            EventReference(
                title=title,
                source_url=source_url,
            )
        )
        if len(references) >= max_items:
            break

    return _enrich_references_from_listing_html(references, html=html)


def _extract_paginated_event_page_urls(
    html: str,
    *,
    base_url: str,
    list_url: str,
) -> list[str]:
    page_urls: list[str] = []
    seen: set[str] = set()
    for match in _EVENTS_PAGE_LINK_RE.finditer(html):
        page_url = _normalize_reference_url(match.group(0), base_url=base_url)
        if page_url is None or page_url == list_url or page_url in seen:
            continue
        seen.add(page_url)
        page_urls.append(page_url)
    return page_urls


def _effective_parser_key(source: EventSourceRecord) -> str:
    parser_key = collapse_whitespace(source.parser_key or "")
    if parser_key and parser_key != "generic_html":
        return parser_key

    parsed = urlparse(source.list_url)
    normalized_path = normalize_text(parsed.path)
    normalized_host = normalize_text(parsed.netloc)
    if "omu.edu.tr" not in normalized_host or "/tr/etkinlikler" not in normalized_path:
        return parser_key or "generic_html"
    if normalized_host == "www.omu.edu.tr":
        return "omu_main_events"
    return "omu_faculty_home_events"


def _parse_datetime_fragment(value: str | None) -> _ParsedDateTime | None:
    if not value:
        return None
    match = _DATE_RE.search(value)
    date_value: datetime | None = None
    if match is not None:
        raw_date = match.group(1)
        for pattern in _DATE_PATTERNS:
            try:
                parsed = datetime.strptime(raw_date, pattern)
            except ValueError:
                continue
            date_value = parsed.replace(tzinfo=UTC)
            break
    else:
        word_match = _DATE_WORD_MONTH_RE.search(value)
        if word_match is None:
            return None
        month_key = normalize_text(word_match.group(2))
        month = _TURKISH_MONTHS.get(month_key)
        if month is None:
            return None
        try:
            date_value = datetime(
                year=int(word_match.group(3)),
                month=month,
                day=int(word_match.group(1)),
                tzinfo=UTC,
            )
        except ValueError:
            return None

    time_match = _TIME_RE.search(value)
    has_time = time_match is not None
    if time_match is not None and date_value is not None:
        date_value = date_value.replace(
            hour=int(time_match.group(1)),
            minute=int(time_match.group(2)),
        )
    return _ParsedDateTime(value=date_value, has_time=has_time) if date_value else None


def _parse_month_day_fragment(value: str | None, *, year: int | None) -> _ParsedDateTime | None:
    if not value or year is None:
        return None
    match = _MONTH_DAY_RE.search(value)
    if match is None:
        return None
    month = _TURKISH_MONTHS.get(normalize_text(match.group(1)))
    if month is None:
        return None
    try:
        date_value = datetime(
            year=year,
            month=month,
            day=int(match.group(2)),
            tzinfo=UTC,
        )
    except ValueError:
        return None
    time_match = _TIME_RE.search(value)
    has_time = time_match is not None
    if time_match is not None:
        date_value = date_value.replace(
            hour=int(time_match.group(1)),
            minute=int(time_match.group(2)),
        )
    return _ParsedDateTime(value=date_value, has_time=has_time)


def _extract_event_window(text: str) -> tuple[datetime | None, datetime | None, bool]:
    if not text:
        return None, None, False

    cleaned_lines = [
        collapse_whitespace(line)
        for line in extract_readable_text_from_html(text).splitlines()
        if collapse_whitespace(line)
    ]

    range_match = _DATE_RANGE_RE.search(text)
    if range_match is not None:
        first = _parse_datetime_fragment(range_match.group("first"))
        second = _parse_datetime_fragment(range_match.group("second"))
        if first and second:
            return first.value, second.value, not first.has_time and not second.has_time

    explicit_start: _ParsedDateTime | None = None
    explicit_end: _ParsedDateTime | None = None
    parsed_values: list[_ParsedDateTime] = []
    seen_iso: set[str] = set()
    for line in cleaned_lines[:8]:
        normalized_line = normalize_text(line)
        parsed = _parse_datetime_fragment(line)
        if parsed is None:
            continue
        if any(normalized_line.startswith(prefix) for prefix in _TRAILING_EVENT_DATE_PREFIXES):
            explicit_end = parsed
            continue
        if any(normalized_line.startswith(prefix) for prefix in _LEADING_EVENT_DATE_PREFIXES):
            explicit_start = parsed
            continue
        key = parsed.value.isoformat()
        if key in seen_iso:
            continue
        seen_iso.add(key)
        parsed_values.append(parsed)
        if len(parsed_values) >= 3:
            break

    if explicit_start is not None:
        return (
            explicit_start.value,
            explicit_end.value if explicit_end is not None else None,
            not explicit_start.has_time and (explicit_end is None or not explicit_end.has_time),
        )

    if not parsed_values:
        return None, None, False

    starts_at = parsed_values[0].value
    if starts_at.year < 2000:
        for candidate in parsed_values[1:]:
            if candidate.value.year >= 2000:
                starts_at = candidate.value
                break
    ends_at = None
    all_day = not starts_at.hour and not starts_at.minute and not parsed_values[0].has_time
    return starts_at, ends_at, all_day


def _extract_prefixed_value(text: str, prefixes: tuple[str, ...]) -> str | None:
    for raw_line in extract_readable_text_from_html(text).splitlines():
        line = collapse_whitespace(raw_line)
        if not line:
            continue
        normalized = normalize_text(line)
        for prefix in prefixes:
            if not normalized.startswith(prefix):
                continue
            parts = re.split(r"\s*[:\-]\s*", line, maxsplit=1)
            if len(parts) == 2:
                value = collapse_whitespace(parts[1])
                return value or None
    return None


def _extract_location(text: str) -> str | None:
    prefixed = _extract_prefixed_value(text, _LOCATION_PREFIXES)
    if prefixed:
        return prefixed
    for raw_line in extract_readable_text_from_html(text).splitlines()[:6]:
        line = collapse_whitespace(raw_line)
        if not line:
            continue
        matches = list(_LOCATION_HINT_RE.finditer(line))
        if matches:
            return collapse_whitespace(matches[-1].group(1))
    return None


def _sanitize_location(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = collapse_whitespace(value)
    cleaned = re.sub(r"^\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?\s*", "", cleaned)
    cleaned = cleaned.strip(" -:,.")
    return cleaned or None


def _extract_organizer(text: str) -> str | None:
    prefixed = _extract_prefixed_value(text, _ORGANIZER_PREFIXES)
    if prefixed:
        return prefixed
    for raw_line in extract_readable_text_from_html(text).splitlines()[:6]:
        line = collapse_whitespace(raw_line)
        if not line:
            continue
        match = _ORGANIZER_HINT_RE.search(line)
        if match is not None:
            return collapse_whitespace(match.group(1))
    return None


def _sanitize_organizer(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = collapse_whitespace(value.strip(" -:,."))
    if not cleaned:
        return None
    if len(cleaned) > 90:
        return None
    if _DATE_RE.search(cleaned) or _DATE_WORD_MONTH_RE.search(cleaned) or _TIME_RE.search(cleaned):
        return None
    return cleaned


def _infer_event_type(*, title: str, text: str) -> str | None:
    normalized_title = normalize_text(title)
    for keyword, event_type in _EVENT_TYPE_KEYWORDS:
        if keyword in normalized_title:
            return event_type

    first_lines = [
        collapse_whitespace(line)
        for line in extract_readable_text_from_html(text).splitlines()
        if collapse_whitespace(line)
    ][:3]
    combined = normalize_text(" ".join(first_lines))
    for keyword, event_type in _EVENT_TYPE_KEYWORDS:
        if keyword in combined:
            return event_type
    return None


def _clean_event_body_text(text: str) -> str:
    lines = [collapse_whitespace(line) for line in text.splitlines() if collapse_whitespace(line)]
    while lines and any(marker in normalize_text(lines[0]) for marker in _EVENT_SALUTATION_MARKERS):
        lines.pop(0)
    while lines and any(marker in normalize_text(lines[-1]) for marker in _EVENT_SIGNATURE_MARKERS):
        lines.pop()
    return "\n".join(lines).strip()


def _is_low_quality_event_text(
    text: str,
    *,
    source: EventSourceRecord,
) -> bool:
    cleaned = collapse_whitespace(text)
    if not cleaned:
        return True
    normalized = normalize_text(cleaned)
    if any(marker in normalized for marker in _SHELL_TEXT_MARKERS):
        return True
    generic_lines = {
        normalize_text(source.faculty or ""),
        normalize_text(source.unit_name or ""),
        "muhendislik fakultesi",
        "bilgisayar muhendisligi bolumu",
    }
    lines = [collapse_whitespace(line) for line in text.splitlines() if collapse_whitespace(line)]
    return len(lines) == 1 and normalize_text(lines[0]) in generic_lines


def _extract_publication_datetime(detail_html: str | None) -> datetime | None:
    if not detail_html:
        return None
    raw_text = extract_readable_text_from_html(detail_html)
    for line in raw_text.splitlines()[:10]:
        cleaned = collapse_whitespace(line)
        if not cleaned:
            continue
        normalized = normalize_text(cleaned)
        if "tarih" not in normalized and not _DATE_RE.search(cleaned) and not _DATE_WORD_MONTH_RE.search(cleaned):
            continue
        parsed = _parse_datetime_fragment(cleaned)
        if parsed is not None:
            return parsed.value
    return None


def _build_reference_starts_at(
    reference: EventReference,
    *,
    publication_dt: datetime | None,
) -> datetime | None:
    if reference.starts_at is not None:
        return reference.starts_at

    year = publication_dt.year if publication_dt is not None else None
    parsed = _parse_datetime_fragment(reference.date_hint)
    if parsed is None:
        parsed = _parse_month_day_fragment(reference.date_hint, year=year)
    if parsed is None and publication_dt is not None:
        parsed = _ParsedDateTime(
            value=publication_dt,
            has_time=bool(publication_dt.hour or publication_dt.minute),
        )
    if parsed is None:
        return None
    if reference.time_hint:
        time_match = _TIME_RE.search(reference.time_hint)
        if time_match is not None:
            return parsed.value.replace(
                hour=int(time_match.group(1)),
                minute=int(time_match.group(2)),
            )
    return parsed.value


def _format_event_datetime(value: datetime) -> str:
    if value.hour or value.minute:
        return value.astimezone(UTC).strftime("%d.%m.%Y %H:%M")
    return value.astimezone(UTC).strftime("%d.%m.%Y")


def _build_fallback_event_text(
    *,
    title: str,
    starts_at: datetime | None,
    location: str | None,
    organizer: str | None,
) -> str:
    parts = [title]
    if starts_at is not None:
        parts.append(f"Tarih: {_format_event_datetime(starts_at)}")
    if location:
        parts.append(f"Konum: {location}")
    if organizer:
        parts.append(f"Duzenleyen: {organizer}")
    return ". ".join(parts)


def _build_event_summary(
    *,
    title: str,
    detail_text: str,
    teaser: str | None,
    location: str | None,
) -> str:
    lines = [collapse_whitespace(line) for line in detail_text.splitlines() if collapse_whitespace(line)]
    preferred_line = ""
    for line in lines:
        normalized_line = normalize_text(line)
        if any(marker in normalized_line for marker in _EVENT_SALUTATION_MARKERS):
            continue
        if len(line) < 20:
            continue
        preferred_line = line
        break
    summary_source = preferred_line or teaser or detail_text
    summary_location = None if "konum:" in normalize_text(summary_source) else location
    return summarize_event_text(
        title=title,
        original_text=summary_source,
        location=summary_location,
    )


def _extract_detail_text_for_source(
    source: EventSourceRecord,
    *,
    detail_html: str | None,
    reference: EventReference,
) -> str:
    if not detail_html:
        return ""
    parser_key = _effective_parser_key(source)
    if parser_key == "omu_faculty_home_events":
        cleaned = extract_omu_faculty_home_text_from_html(
            detail_html,
            title=reference.title,
        )
        return cleaned or extract_readable_text_from_html(detail_html)
    if parser_key == "omu_main_events":
        return extract_readable_text_from_html(detail_html)
    return extract_readable_text_from_html(detail_html)


def _extract_references_for_source(
    source: EventSourceRecord,
    index_html: str,
) -> list[EventReference]:
    return extract_event_references_from_html(
        index_html,
        base_url=source.base_url or source.list_url,
        max_items=source.max_items_per_run,
    )


async def _collect_references_for_source(
    source: EventSourceRecord,
    *,
    http_client: EventHTTPClient,
) -> list[EventReference]:
    index_html = await http_client.get_text(source.list_url)
    references = _extract_references_for_source(source, index_html)
    max_items = source.max_items_per_run
    if len(references) >= max_items:
        return references[:max_items]

    normalized_list_url = normalize_text(source.list_url)
    if "/tr/etkinlik" not in normalized_list_url:
        return references

    page_urls = _extract_paginated_event_page_urls(
        index_html,
        base_url=source.base_url or source.list_url,
        list_url=source.list_url,
    )
    if not page_urls:
        return references

    collected = list(references)
    seen_urls = {item.source_url for item in references}
    for page_url in page_urls:
        if len(collected) >= max_items:
            break
        try:
            page_html = await http_client.get_text(page_url)
        except Exception:
            continue
        page_refs = extract_event_references_from_html(
            page_html,
            base_url=source.base_url or source.list_url,
            max_items=max_items,
        )
        for ref in page_refs:
            if ref.source_url in seen_urls:
                continue
            seen_urls.add(ref.source_url)
            collected.append(ref)
            if len(collected) >= max_items:
                break

    return collected[:max_items]


def build_event_candidate_from_reference(
    reference: EventReference,
    *,
    source: EventSourceRecord,
    detail_html: str | None,
    fallback_department: str | None,
    fallback_faculty: str | None,
) -> EventCandidate:
    """Build a normalized event candidate from listing and detail content."""

    detail_text = _extract_detail_text_for_source(
        source,
        detail_html=detail_html,
        reference=reference,
    )
    publication_dt = _extract_publication_datetime(detail_html)
    cleaned_detail_text = _clean_event_body_text(detail_text)
    if _is_low_quality_event_text(cleaned_detail_text, source=source):
        cleaned_detail_text = ""
    starts_at, ends_at, all_day = _extract_event_window(cleaned_detail_text or reference.teaser or "")
    starts_at = starts_at or _build_reference_starts_at(reference, publication_dt=publication_dt)
    if starts_at and starts_at.year < 2000 and publication_dt and publication_dt.year >= 2000:
        starts_at = _build_reference_starts_at(reference, publication_dt=publication_dt) or publication_dt
    location = _sanitize_location(_extract_location(cleaned_detail_text) or reference.location)
    organizer = _sanitize_organizer(_extract_organizer(cleaned_detail_text))
    if not cleaned_detail_text:
        cleaned_detail_text = _build_fallback_event_text(
            title=reference.title,
            starts_at=starts_at,
            location=location,
            organizer=organizer,
        )
        all_day = bool(starts_at and not starts_at.hour and not starts_at.minute)
    summary = _build_event_summary(
        title=reference.title,
        detail_text=cleaned_detail_text,
        teaser=reference.teaser,
        location=location,
    )
    event_type = _infer_event_type(
        title=reference.title,
        text=cleaned_detail_text or reference.teaser or "",
    )
    original_text = cleaned_detail_text or reference.teaser or reference.title
    links = extract_announcement_links_from_html(
        detail_html,
        base_url=source.base_url or reference.source_url,
        source_url=reference.source_url,
        title=reference.title,
    )
    return EventCandidate(
        title=reference.title,
        source_url=reference.source_url,
        original_text=original_text,
        summary=summary,
        display_summary=summary,
        starts_at=starts_at,
        ends_at=ends_at,
        location=location,
        organizer=organizer,
        event_type=event_type,
        all_day=all_day,
        faculty=fallback_faculty,
        unit_name=source.unit_name,
        department=fallback_department,
        links=tuple(
            EventLinkCandidate(
                label=link.label,
                url=link.url,
                link_type=link.link_type,
                sort_order=link.sort_order,
            )
            for link in links
        ),
    )


async def sync_event_source(
    source: EventSourceRecord,
    *,
    http_client: EventHTTPClient | None = None,
    dry_run: bool = False,
    allow_deactivation: bool = True,
    fetch_details: bool = True,
) -> EventSourceSyncResult:
    """Fetch, parse and persist events for one source."""

    http_client = http_client or EventHTTPClient()
    try:
        references = await _collect_references_for_source(
            source,
            http_client=http_client,
        )
        candidates: list[EventCandidate] = []
        for reference in references:
            detail_html = None
            if fetch_details:
                try:
                    detail_html = await http_client.get_text(reference.source_url)
                except Exception:
                    detail_html = None
            candidates.append(
                build_event_candidate_from_reference(
                    reference,
                    source=source,
                    detail_html=detail_html,
                    fallback_department=source.department,
                    fallback_faculty=source.faculty,
                )
            )
    except Exception as exc:
        if dry_run:
            return EventSourceSyncResult(
                source=source,
                status="failed",
                stats=EventSyncStats(),
                error_message=str(exc),
            )
        async with get_session() as session:
            run = await create_event_sync_run(session, source_id=source.id)
            empty_stats = EventSyncStats()
            await finalize_event_sync_run(
                session,
                run=run,
                status="failed",
                stats=empty_stats,
                error_message=str(exc),
            )
            await mark_event_source_sync_result(
                session,
                source_id=source.id,
                success=False,
                error_message=str(exc),
            )
        return EventSourceSyncResult(
            source=source,
            status="failed",
            stats=EventSyncStats(),
            error_message=str(exc),
        )

    if dry_run and source.id <= 0:
        return EventSourceSyncResult(
            source=source,
            status="dry_run",
            stats=_build_dry_run_stats(candidates),
        )

    async with get_session() as session:
        run = None
        if not dry_run:
            run = await create_event_sync_run(session, source_id=source.id)
        stats = await upsert_events_for_source(
            session,
            source=source,
            candidates=candidates,
            dry_run=dry_run,
            allow_deactivation=allow_deactivation,
        )
        if not dry_run and run is not None:
            await finalize_event_sync_run(
                session,
                run=run,
                status="completed",
                stats=stats,
            )
            await mark_event_source_sync_result(
                session,
                source_id=source.id,
                success=True,
            )
        return EventSourceSyncResult(
            source=source,
            status="dry_run" if dry_run else "completed",
            stats=stats,
        )


async def sync_event_sources(
    sources: list[EventSourceRecord],
    *,
    http_client: EventHTTPClient | None = None,
    dry_run: bool = False,
    allow_deactivation: bool = True,
    fetch_details: bool = True,
) -> list[EventSourceSyncResult]:
    """Synchronize multiple event sources sequentially."""

    results: list[EventSourceSyncResult] = []
    for source in sources:
        results.append(
            await sync_event_source(
                source,
                http_client=http_client,
                dry_run=dry_run,
                allow_deactivation=allow_deactivation,
                fetch_details=fetch_details,
            )
        )
    return results
