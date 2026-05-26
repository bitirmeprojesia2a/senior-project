"""Announcement source synchronization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser
import re
from typing import Protocol
from urllib.parse import urljoin, urlparse

import httpx

from src.core.text_normalization import collapse_whitespace, normalize_text
from src.db import get_session
from src.db.announcement_sources import (
    AnnouncementCandidate,
    AnnouncementLinkCandidate,
    AnnouncementSourceRecord,
    AnnouncementSyncStats,
    create_announcement_sync_run,
    finalize_announcement_sync_run,
    mark_announcement_source_sync_result,
    upsert_announcements_for_source,
)
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.prompt_templates import ANNOUNCEMENT_SUMMARY_REFINER_SYSTEM_PROMPT

_ANCHOR_TITLE_MIN_LENGTH = 12
_DATE_PATTERNS = (
    "%d.%m.%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
)
_TURKISH_MONTHS = {
    "ocak": 1,
    "subat": 2,
    "mart": 3,
    "nisan": 4,
    "mayis": 5,
    "haziran": 6,
    "temmuz": 7,
    "agustos": 8,
    "eylul": 9,
    "ekim": 10,
    "kasim": 11,
    "aralik": 12,
}
_GENERIC_NAV_TITLES = frozenset(
    {
        "ana sayfa",
        "home",
        "iletisim",
        "hakkimizda",
        "duyurular",
        "haberler",
        "detay",
        "devami",
        "read more",
        "daha fazlasi",
        "daha fazlası",
        "tum duyurular",
        "tum haberler",
    }
)
_TAG_CLEANUP_PATTERNS = (
    re.compile(r"(?is)<script.*?>.*?</script>"),
    re.compile(r"(?is)<style.*?>.*?</style>"),
    re.compile(r"(?is)<noscript.*?>.*?</noscript>"),
)
_BLOCK_END_RE = re.compile(r"(?i)</(?:p|div|section|article|li|h[1-6]|br|tr|td)>")
_TAG_RE = re.compile(r"(?s)<[^>]+>")
_DATE_RE = re.compile(r"\b(\d{1,2}[./]\d{1,2}[./]\d{4}|\d{4}-\d{2}-\d{2})\b")
_DATE_WORD_MONTH_RE = re.compile(
    r"\b(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})\b"
)
_OMU_ANNOUNCEMENT_PATH_MARKERS = (
    "/tr/icerik/duyuru/",
    "/icerik/duyuru/",
)
_OMU_FACULTY_ANNOUNCEMENT_PATH_MARKERS = (
    "/tr/haberler/",
    "/haberler/",
    "/tr/duyurular/",
    "/duyurular/",
)
_OMU_DETAIL_SKIP_LINES = frozenset(
    {
        "duyuru",
        "paylas",
        "dinle",
        "link kopyalandi!",
        "link kopyalandi",
        "onceki duyuru",
        "sonraki duyuru",
    }
)
_OMU_DETAIL_STOP_LINES = frozenset(
    {
        "hizli erisim",
        "yerleskelerimiz",
        "sosyal medyada biz",
        "iletisim",
    }
)
_OMU_DETAIL_STOP_SUBSTRINGS = frozenset(
    {
        "ilginizi cekebilir",
        "sayfa basina git",
    }
)
_OMU_DETAIL_NOISE_MARKERS = (
    "facebook",
    "instagram",
    "youtube",
    "linkedin",
    "x.com",
    "copyright",
)
_FACULTY_DETAIL_SKIP_LINES = frozenset(
    {
        "duyurular",
        "haberler",
        "paylas",
        "dinle",
        "link kopyalandi",
        "link kopyalandi!",
    }
)
_FACULTY_DETAIL_STOP_MARKERS = frozenset(
    {
        "baglantilar",
        "ilgili baglantilar",
        "iletisim",
        "hizli linkler",
        "copyright",
        "choose colour",
        "tum duyuru ve haberler",
        "ogrenci isleri",
        "omu de yasam",
        "son haberler",
        "etkinlikler",
    }
)
_UNSUPPORTED_ANNOUNCEMENT_EXTENSIONS = (
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
)
_ATTACHMENT_LINK_EXTENSIONS = (
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".rar",
)
_IMPORTANT_LINK_KEYWORDS = frozenset(
    {
        "tiklayiniz",
        "tıklayınız",
        "indir",
        "dosya",
        "ek",
        "ek dosya",
        "program",
        "basvuru",
        "başvuru",
        "form",
        "takvim",
        "kilavuz",
        "kılavuz",
        "liste",
        "sonuc",
        "sonuç",
    }
)
_LINK_NOISE_MARKERS = frozenset(
    {
        "facebook",
        "instagram",
        "linkedin",
        "youtube",
        "x.com",
        "twitter",
        "paylas",
        "share",
    }
)
_LINK_NOISE_LABELS = frozenset(
    {
        "en",
        "tr",
        "lisans programi",
        "yüksek lisans programı",
        "yuksek lisans programi",
        "doktora programi",
        "doktora programı",
        "degisim programlari",
        "değişim programları",
        "program ciktilari",
        "program çıktıları",
    }
)
_LINK_NOISE_URL_PARTS = frozenset(
    {
        "/en/",
        "/tr/egitim-ogretim/",
        "/tr/kurumsal/",
        "/tr/idari/",
        "/tr/ogrenci/",
    }
)
_NEWS_ITEM_BLOCK_RE = re.compile(
    r'(?is)<article[^>]+class=["\'](?=[^"\']*news-item)(?=[^"\']*page-row)[^"\']*["\'][^>]*>(.*?)</article>\s*(?:<!--.*?-->)?'
)
_NEWS_ITEM_LINK_RE = re.compile(
    r'(?is)<h(?:2|3)[^>]*>.*?<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>.*?</h(?:2|3)>'
)
_NEWS_ITEM_SUMMARY_RE = re.compile(r"(?is)<p[^>]*>(.*?)</p>")
_OMU_LIST_ITEM_BLOCK_RE = re.compile(
    r'(?is)<li[^>]+class=["\'][^"\']*ht-layout[^"\']*["\'][^>]*>(.*?)</li>'
)
_OMU_LIST_ITEM_LINK_RE = re.compile(
    r'(?is)<div[^>]+class=["\'][^"\']*ht-heading-title-text[^"\']*["\'][^>]*>.*?<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
)
_OMU_LIST_ITEM_TIMESTAMP_RE = re.compile(
    r'(?is)<div[^>]+class=["\'][^"\']*ht-timestamp[^"\']*["\'][^>]*>(.*?)</div>'
)
_META_DESCRIPTION_RE = re.compile(
    r'(?is)<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\']([^"\']+)["\']'
)
_HABERLER_PAGE_LINK_RE = re.compile(r"/tr/haberler/page:(\d+)", re.IGNORECASE)
_RAW_URL_RE = re.compile(r"https?://\S+")
_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]+")
_SUMMARY_SKIP_LINES = frozenset(
    {
        "son haberler",
        "etkinlikler",
        "duyuru",
        "haberler",
        "paylas",
        "link kopyalandi",
        "dinle",
    }
)


class AnnouncementHTTPClient(Protocol):
    """Protocol for fetcher injection in sync workflows."""

    async def get_text(self, url: str) -> str:
        """Return the response body as text."""


class AnnouncementSummaryRefiner(Protocol):
    """Optional one-time summary cleanup used during sync."""

    async def refine(
        self,
        *,
        title: str,
        summary: str | None,
        original_text: str | None,
        links: tuple[AnnouncementLinkCandidate, ...],
    ) -> str | None:
        """Return a cleaned display summary."""


@dataclass(frozen=True)
class AnnouncementReference:
    """Minimal link extracted from a source listing page."""

    title: str
    source_url: str
    published_at: datetime | None = None
    teaser: str | None = None


@dataclass(frozen=True)
class AnnouncementSourceSyncResult:
    """User-facing sync result for a single source."""

    source: AnnouncementSourceRecord
    status: str
    stats: AnnouncementSyncStats
    error_message: str | None = None


def _build_dry_run_stats(candidates: list[AnnouncementCandidate]) -> AnnouncementSyncStats:
    """Estimate dry-run counts without querying persistence."""

    seen_keys: set[str] = set()
    unique_count = 0
    for candidate in candidates:
        dedupe_key = candidate.source_url or normalize_text(candidate.title)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        unique_count += 1
    return AnnouncementSyncStats(
        items_found=len(candidates),
        items_inserted=unique_count,
        items_updated=0,
        items_deactivated=0,
    )


class HttpxAnnouncementHTTPClient:
    """Default HTTP client for announcement synchronization."""

    def __init__(
        self,
        *,
        timeout_seconds: int = 20,
        user_agent: str = "omu-destek-duyuru-sync/1.0",
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    async def get_text(self, url: str) -> str:
        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text


class LLMAnnouncementSummaryRefiner:
    """LLM-backed cleaner used only when heuristic summaries look weak."""

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self._llm_service = llm_service or LLMService()

    async def refine(
        self,
        *,
        title: str,
        summary: str | None,
        original_text: str | None,
        links: tuple[AnnouncementLinkCandidate, ...],
    ) -> str | None:
        prompt = _build_announcement_summary_refiner_prompt(
            title=title,
            summary=summary,
            original_text=original_text,
            links=links,
        )
        try:
            response = await self._llm_service.generate(
                prompt,
                system=ANNOUNCEMENT_SUMMARY_REFINER_SYSTEM_PROMPT,
                model_role="specialist_synthesis",
            )
        except LLMServiceError:
            return None
        cleaned = _clean_refined_display_summary(response)
        return cleaned or None


class NoOpAnnouncementSummaryRefiner:
    """Fast default refiner for bulk sync runs."""

    async def refine(
        self,
        *,
        title: str,
        summary: str | None,
        original_text: str | None,
        links: tuple[AnnouncementLinkCandidate, ...],
    ) -> str | None:
        return None


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


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    match = _DATE_RE.search(value)
    if match is None:
        word_match = _DATE_WORD_MONTH_RE.search(value)
        if word_match is None:
            return None
        month_key = normalize_text(word_match.group(2))
        month = _TURKISH_MONTHS.get(month_key)
        if month is None:
            return None
        try:
            return datetime(
                year=int(word_match.group(3)),
                month=month,
                day=int(word_match.group(1)),
                tzinfo=UTC,
            )
        except ValueError:
            return None
    for pattern in _DATE_PATTERNS:
        try:
            return datetime.strptime(match.group(1), pattern).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def _normalize_reference_url(raw_url: str | None, *, base_url: str) -> str | None:
    if not raw_url:
        return None
    lowered = raw_url.strip().lower()
    if lowered.startswith(("javascript:", "mailto:", "tel:", "#")):
        return None
    return urljoin(base_url, raw_url.strip())


def extract_announcement_links_from_html(
    html: str | None,
    *,
    base_url: str,
    source_url: str,
    title: str | None = None,
    max_links: int = 5,
) -> tuple[AnnouncementLinkCandidate, ...]:
    """Extract important attachment or helper links from an announcement detail page."""

    if not html:
        return ()

    parser = _AnchorCollector()
    parser.feed(html)
    seen_urls: set[str] = set()
    links: list[AnnouncementLinkCandidate] = []
    source_domain = urlparse(source_url).netloc

    for raw_href, raw_label in parser.anchors:
        resolved = _normalize_reference_url(raw_href, base_url=base_url)
        if resolved is None or resolved == source_url:
            continue
        if resolved in seen_urls:
            continue
        parsed = urlparse(resolved)
        is_attachment = _is_attachment_url(resolved)
        is_detail_child = _is_detail_child_link(resolved, source_url)
        if parsed.netloc and source_domain and parsed.netloc != source_domain and not is_attachment:
            continue
        if not is_attachment and not is_detail_child:
            continue
        if is_attachment and not _attachment_matches_announcement_scope(
            resolved,
            source_url=source_url,
            title=title,
        ):
            continue
        if not _looks_like_important_link(raw_label, resolved):
            continue
        seen_urls.add(resolved)
        label = _derive_link_label(raw_label, resolved)
        link_type = "attachment" if is_attachment else "related"
        links.append(
            AnnouncementLinkCandidate(
                label=label,
                url=resolved,
                link_type=link_type,
                sort_order=len(links),
            )
        )
        if len(links) >= max_links:
            break

    return tuple(links)


def _is_supported_announcement_url(url: str) -> bool:
    normalized = normalize_text(url)
    return not normalized.endswith(_UNSUPPORTED_ANNOUNCEMENT_EXTENSIONS)


def _looks_like_binary_payload(payload: str | None) -> bool:
    if not payload:
        return False
    if "\x00" in payload:
        return True
    leading = payload.lstrip()
    if leading.startswith("%PDF-"):
        return True
    return False


def _is_attachment_url(url: str) -> bool:
    normalized = normalize_text(url)
    parsed = urlparse(normalized)
    path = parsed.path or normalized
    return any(path.endswith(extension) for extension in _ATTACHMENT_LINK_EXTENSIONS)


def _looks_like_valid_announcement_title(title: str) -> bool:
    compact = collapse_whitespace(title)
    normalized = normalize_text(compact)
    if len(compact) < _ANCHOR_TITLE_MIN_LENGTH:
        return False
    if normalized in _GENERIC_NAV_TITLES:
        return False
    if compact.count(" ") < 1 and len(compact) < 20:
        return False
    return True


def _looks_like_important_link(label: str, url: str) -> bool:
    normalized_label = normalize_text(label)
    normalized_url = normalize_text(url)
    if any(marker in normalized_url for marker in _LINK_NOISE_MARKERS):
        return False
    if normalized_label in _LINK_NOISE_LABELS:
        return False
    if any(part in normalized_url for part in _LINK_NOISE_URL_PARTS):
        return False
    if _is_attachment_url(url):
        return True
    if any(keyword in normalized_label for keyword in _IMPORTANT_LINK_KEYWORDS):
        return True
    if any(keyword in normalized_url for keyword in _IMPORTANT_LINK_KEYWORDS):
        return True
    return False


def _derive_link_label(label: str, url: str) -> str:
    compact_label = collapse_whitespace(label)
    normalized_label = normalize_text(compact_label)
    generic_labels = {
        "",
        "tiklayiniz",
        "tıklayınız",
        "tiklayiniz.",
        "detay",
        "detayi",
        "inceleyiniz",
        "buraya tiklayiniz",
        "burayi tiklayiniz",
    }
    if normalized_label and normalized_label not in generic_labels:
        return compact_label

    parsed = urlparse(url)
    filename = parsed.path.rsplit("/", 1)[-1]
    filename = re.sub(r"\.[A-Za-z0-9]+$", "", filename)
    filename = collapse_whitespace(filename.replace("-", " ").replace("_", " "))
    return filename or compact_label or url


def _is_detail_child_link(url: str, source_url: str) -> bool:
    normalized_url = collapse_whitespace(url).rstrip("/")
    normalized_source = collapse_whitespace(source_url).rstrip("/")
    return bool(normalized_source) and normalized_url.startswith(f"{normalized_source}/")


def _attachment_matches_announcement_scope(
    url: str,
    *,
    source_url: str,
    title: str | None = None,
) -> bool:
    if _is_detail_child_link(url, source_url):
        return True

    source_slug = normalize_text(urlparse(source_url).path.rsplit("/", 1)[-1])
    attachment_path = normalize_text(urlparse(url).path)
    if source_slug and source_slug in attachment_path:
        return True

    normalized_title = normalize_text(title or "")
    if not normalized_title:
        return True
    title_tokens = [
        token
        for token in normalized_title.split()
        if len(token) >= 4
    ]
    if not title_tokens:
        return False
    overlap = sum(1 for token in title_tokens if token in attachment_path)
    return overlap >= min(2, len(title_tokens))


def _clean_html_fragment(fragment: str | None) -> str | None:
    if not fragment:
        return None
    cleaned = fragment
    for pattern in _TAG_CLEANUP_PATTERNS:
        cleaned = pattern.sub(" ", cleaned)
    cleaned = _BLOCK_END_RE.sub("\n", cleaned)
    cleaned = _TAG_RE.sub(" ", cleaned)
    cleaned = collapse_whitespace(unescape(cleaned))
    return cleaned or None


def _extract_paginated_news_page_urls(
    html: str,
    *,
    base_url: str,
    list_url: str,
) -> list[str]:
    base_domain = urlparse(base_url).netloc
    current_url = urlparse(list_url)
    target_prefix = normalize_text(current_url.path.rstrip("/"))
    parser = _AnchorCollector()
    parser.feed(html)

    page_urls: dict[int, str] = {}
    for raw_href, _title in parser.anchors:
        resolved = _normalize_reference_url(raw_href, base_url=base_url)
        if resolved is None:
            continue
        parsed = urlparse(resolved)
        if base_domain and parsed.netloc and parsed.netloc != base_domain:
            continue
        normalized_path = normalize_text(parsed.path)
        if target_prefix and not normalized_path.startswith(target_prefix):
            continue
        match = _HABERLER_PAGE_LINK_RE.search(parsed.path)
        if match is None:
            continue
        page_number = int(match.group(1))
        if page_number <= 1:
            continue
        page_urls[page_number] = resolved

    return [page_urls[number] for number in sorted(page_urls)]


def extract_announcement_references_from_html(
    html: str,
    *,
    base_url: str,
    max_items: int,
) -> list[AnnouncementReference]:
    """Extract a deduplicated set of likely announcement links from an index page."""

    parser = _AnchorCollector()
    parser.feed(html)
    seen: set[str] = set()
    references: list[AnnouncementReference] = []
    base_domain = urlparse(base_url).netloc

    for raw_href, title in parser.anchors:
        source_url = _normalize_reference_url(raw_href, base_url=base_url)
        if source_url is None or not _looks_like_valid_announcement_title(title):
            continue
        parsed = urlparse(source_url)
        if base_domain and parsed.netloc and parsed.netloc != base_domain:
            continue
        dedupe_key = f"{normalize_text(title)}::{source_url}"
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        references.append(
            AnnouncementReference(
                title=collapse_whitespace(title),
                source_url=source_url,
                published_at=_parse_date(title),
            )
        )
        if len(references) >= max_items:
            break

    return references


def extract_omu_announcement_references_from_html(
    html: str,
    *,
    base_url: str,
    max_items: int,
) -> list[AnnouncementReference]:
    """Extract OMU announcement detail links from the central announcement listing."""

    regex_references: list[AnnouncementReference] = []
    seen_urls: set[str] = set()
    base_domain = urlparse(base_url).netloc

    for block in _OMU_LIST_ITEM_BLOCK_RE.findall(html):
        link_match = _OMU_LIST_ITEM_LINK_RE.search(block)
        if link_match is None:
            continue
        source_url = _normalize_reference_url(link_match.group(1), base_url=base_url)
        compact_title = _clean_html_fragment(link_match.group(2))
        if source_url is None or compact_title is None:
            continue
        if not _looks_like_valid_announcement_title(compact_title):
            continue
        parsed = urlparse(source_url)
        if base_domain and parsed.netloc and parsed.netloc != base_domain:
            continue
        normalized_path = normalize_text(parsed.path)
        if not any(marker in normalized_path for marker in _OMU_ANNOUNCEMENT_PATH_MARKERS):
            continue
        if source_url in seen_urls:
            continue
        timestamp_match = _OMU_LIST_ITEM_TIMESTAMP_RE.search(block)
        published_at = _parse_date(_clean_html_fragment(timestamp_match.group(1)) if timestamp_match else None)
        seen_urls.add(source_url)
        regex_references.append(
            AnnouncementReference(
                title=compact_title,
                source_url=source_url,
                published_at=published_at,
            )
        )
        if len(regex_references) >= max_items:
            return regex_references

    if regex_references:
        return regex_references

    parser = _AnchorCollector()
    parser.feed(html)
    references: list[AnnouncementReference] = []

    for raw_href, title in parser.anchors:
        source_url = _normalize_reference_url(raw_href, base_url=base_url)
        if source_url is None or not _looks_like_valid_announcement_title(title):
            continue
        parsed = urlparse(source_url)
        if base_domain and parsed.netloc and parsed.netloc != base_domain:
            continue
        normalized_path = normalize_text(parsed.path)
        if not any(marker in normalized_path for marker in _OMU_ANNOUNCEMENT_PATH_MARKERS):
            continue
        if source_url in seen_urls:
            continue
        seen_urls.add(source_url)
        references.append(
            AnnouncementReference(
                title=collapse_whitespace(title),
                source_url=source_url,
                published_at=None,
            )
        )
        if len(references) >= max_items:
            break

    return references


def extract_omu_faculty_home_references_from_html(
    html: str,
    *,
    base_url: str,
    max_items: int,
) -> list[AnnouncementReference]:
    """Extract announcement/news cards from OMU faculty or department homepages."""

    regex_references: list[AnnouncementReference] = []
    seen_urls: set[str] = set()
    base_domain = urlparse(base_url).netloc
    for block_match in _NEWS_ITEM_BLOCK_RE.finditer(html):
        block = block_match.group(1)
        link_match = _NEWS_ITEM_LINK_RE.search(block)
        if link_match is None:
            continue
        source_url = _normalize_reference_url(link_match.group(1), base_url=base_url)
        if source_url is None or not _is_supported_announcement_url(source_url):
            continue
        compact_title = _clean_html_fragment(link_match.group(2))
        if compact_title is None or not _looks_like_valid_announcement_title(compact_title):
            continue
        parsed = urlparse(source_url)
        if base_domain and parsed.netloc and parsed.netloc != base_domain:
            continue
        normalized_path = normalize_text(parsed.path)
        if not any(marker in normalized_path for marker in _OMU_FACULTY_ANNOUNCEMENT_PATH_MARKERS):
            continue
        if source_url in seen_urls:
            continue
        teaser_match = _NEWS_ITEM_SUMMARY_RE.search(block)
        teaser = _clean_html_fragment(teaser_match.group(1)) if teaser_match else None
        seen_urls.add(source_url)
        regex_references.append(
            AnnouncementReference(
                title=compact_title,
                source_url=source_url,
                published_at=None,
                teaser=teaser,
            )
        )
        if len(regex_references) >= max_items:
            return regex_references
    if regex_references:
        return regex_references

    parser = _AnchorCollector()
    parser.feed(html)
    seen_urls = set()
    references: list[AnnouncementReference] = []

    for raw_href, title in parser.anchors:
        source_url = _normalize_reference_url(raw_href, base_url=base_url)
        if source_url is None or not _is_supported_announcement_url(source_url):
            continue
        compact_title = collapse_whitespace(title)
        if not _looks_like_valid_announcement_title(compact_title):
            continue
        parsed = urlparse(source_url)
        if base_domain and parsed.netloc and parsed.netloc != base_domain:
            continue
        normalized_path = normalize_text(parsed.path)
        if not any(marker in normalized_path for marker in _OMU_FACULTY_ANNOUNCEMENT_PATH_MARKERS):
            continue
        if source_url in seen_urls:
            continue
        seen_urls.add(source_url)
        references.append(
            AnnouncementReference(
                title=compact_title,
                source_url=source_url,
                published_at=None,
                teaser=None,
            )
        )
        if len(references) >= max_items:
            break

    return references


def extract_readable_text_from_html(html: str) -> str:
    """Reduce HTML into a compact text blob suitable for heuristic summaries."""

    cleaned = html
    for pattern in _TAG_CLEANUP_PATTERNS:
        cleaned = pattern.sub(" ", cleaned)
    cleaned = _BLOCK_END_RE.sub("\n", cleaned)
    cleaned = _TAG_RE.sub(" ", cleaned)
    cleaned = unescape(cleaned)
    lines = [
        collapse_whitespace(line)
        for line in cleaned.splitlines()
        if collapse_whitespace(line)
    ]
    return "\n".join(lines)


def _find_last_title_line_index(lines: list[str], *, title: str | None) -> int | None:
    normalized_title = normalize_text(title or "")
    if not normalized_title:
        return None
    matches = [
        index
        for index, line in enumerate(lines)
        if normalize_text(line) == normalized_title
    ]
    if not matches:
        return None
    return matches[-1]


def _find_preferred_title_line_index(lines: list[str], *, title: str | None) -> int | None:
    normalized_title = normalize_text(title or "")
    if not normalized_title:
        return None
    matches = [
        index
        for index, line in enumerate(lines)
        if normalize_text(line) == normalized_title
    ]
    if not matches:
        return None
    if len(matches) >= 2 and (matches[1] - matches[0]) <= 3:
        return matches[1]
    return matches[0]


def _looks_like_metadata_date_line(line: str) -> bool:
    normalized_line = normalize_text(line)
    if _parse_date(line) is None:
        return False
    date_match = _DATE_RE.search(line)
    if date_match is None:
        date_match = _DATE_WORD_MONTH_RE.search(line)
    date_start = date_match.start() if date_match is not None else len(line)
    if date_start > 24 and len(normalized_line) > 60:
        return False
    if ":" in line or "," in line:
        return True
    if "-" in line:
        return True
    if len(line) <= 32:
        return True
    if len(normalized_line.split()) <= 5:
        return True
    return False


def _looks_like_author_line(line: str) -> bool:
    normalized_line = normalize_text(line)
    if not normalized_line:
        return False
    if normalized_line.startswith("yazar:"):
        return True
    words = normalized_line.split()
    if len(words) > 5:
        return False
    if len(normalized_line) > 48:
        return False
    return any(char.isalpha() for char in normalized_line)


def _looks_like_markup_noise(line: str) -> bool:
    normalized_line = normalize_text(line)
    if not normalized_line:
        return True
    return "style" in normalized_line and "background" in normalized_line


def _pick_summary_line(text: str) -> str | None:
    for raw_line in text.splitlines():
        line = collapse_whitespace(raw_line)
        if not line:
            continue
        if _looks_like_markup_noise(line):
            continue
        normalized_line = normalize_text(line)
        if normalized_line in _SUMMARY_SKIP_LINES:
            continue
        if normalized_line in {"", ".", ".."}:
            continue
        stripped_punct = normalized_line.replace(" ", "")
        if stripped_punct and all(char in ".-–—•" for char in stripped_punct):
            continue
        if len(normalized_line) < 2:
            continue
        if len(normalized_line.split()) <= 2 and len(normalized_line) < 20 and "." not in line and ":" not in line:
            continue
        return line
    return None


def _looks_like_weak_display_summary(summary: str | None) -> bool:
    normalized = normalize_text(summary or "")
    if not normalized:
        return True
    if len(normalized) < 18:
        return True
    weak_markers = (
        "tiklayiniz",
        "tıklayınız",
        "goruntulemek icin",
        "görüntülemek için",
        "detay",
        "inceleyiniz",
    )
    if any(marker in normalized for marker in weak_markers):
        return True
    return False


def _build_display_summary_base(
    *,
    title: str,
    summary: str | None,
    original_text: str | None,
) -> str:
    text = collapse_whitespace(summary) or collapse_whitespace(original_text) or collapse_whitespace(title)
    if len(text) > 280:
        text = f"{text[:277].rstrip()}..."
    return _clean_refined_display_summary(text)


def _should_refine_display_summary(
    *,
    summary: str | None,
    original_text: str | None,
) -> bool:
    compact_summary = collapse_whitespace(summary)
    compact_text = collapse_whitespace(original_text)
    if _looks_like_weak_display_summary(compact_summary):
        return True
    if compact_text and len(compact_text) > 500 and compact_summary and len(compact_summary) < 80:
        return True
    return False


def _build_announcement_summary_refiner_prompt(
    *,
    title: str,
    summary: str | None,
    original_text: str | None,
    links: tuple[AnnouncementLinkCandidate, ...],
) -> str:
    link_lines = [
        f"- {link.label}: {link.url}"
        for link in links[:5]
    ]
    return (
        f"Baslik: {title}\n"
        f"Mevcut ozet: {summary or '-'}\n"
        f"Ham metin: {original_text or '-'}\n"
        f"Ek baglantilar:\n{chr(10).join(link_lines) if link_lines else '-'}"
    )


def _clean_refined_display_summary(text: str | None) -> str:
    cleaned = collapse_whitespace(text)
    cleaned = _RAW_URL_RE.sub("", cleaned)
    cleaned = _EMOJI_RE.sub("", cleaned)
    cleaned = collapse_whitespace(cleaned)
    return cleaned


def _has_useful_content(text: str) -> bool:
    for raw_line in text.splitlines():
        line = collapse_whitespace(raw_line)
        if not line:
            continue
        normalized_line = normalize_text(line)
        if normalized_line in _SUMMARY_SKIP_LINES:
            continue
        if _looks_like_markup_noise(line):
            continue
        if _looks_like_metadata_date_line(line) or _looks_like_author_line(line):
            continue
        if len(normalized_line) >= 40:
            return True
    return False


def extract_meta_description_from_html(html: str | None) -> str | None:
    if not html:
        return None
    for match in _META_DESCRIPTION_RE.findall(html):
        cleaned = _clean_html_fragment(match)
        if cleaned:
            return cleaned
    return None


def extract_omu_announcement_text_from_html(
    html: str,
    *,
    title: str | None = None,
) -> str:
    """Extract a cleaner text body from OMU announcement detail pages."""

    raw_text = extract_readable_text_from_html(html)
    lines = [collapse_whitespace(line) for line in raw_text.splitlines() if collapse_whitespace(line)]
    if not lines:
        return ""

    start_index = _find_preferred_title_line_index(lines, title=title)
    if start_index is None:
        start_index = 0
    else:
        start_index += 1

    body_lines: list[str] = []
    for line in lines[start_index:]:
        normalized_line = normalize_text(line)
        if not normalized_line:
            continue
        if _looks_like_markup_noise(line):
            continue
        if normalized_line in _OMU_DETAIL_SKIP_LINES:
            continue
        if normalized_line in _OMU_DETAIL_STOP_LINES:
            break
        if any(marker in normalized_line for marker in _OMU_DETAIL_STOP_SUBSTRINGS):
            break
        if any(marker in normalized_line for marker in _OMU_DETAIL_NOISE_MARKERS):
            continue
        body_lines.append(line)

    if not body_lines:
        return raw_text

    while body_lines:
        first_line = body_lines[0]
        normalized_first = normalize_text(first_line)
        next_line = body_lines[1] if len(body_lines) > 1 else ""
        if normalized_first in _OMU_DETAIL_SKIP_LINES:
            body_lines.pop(0)
            continue
        if _looks_like_author_line(first_line) and (
            _looks_like_metadata_date_line(next_line) or normalize_text(next_line).startswith("guncelleme")
        ):
            body_lines.pop(0)
            continue
        if _looks_like_metadata_date_line(first_line) or normalized_first.startswith("guncelleme"):
            body_lines.pop(0)
            continue
        break

    return "\n".join(body_lines).strip()


def extract_omu_faculty_home_text_from_html(
    html: str,
    *,
    title: str | None = None,
) -> str:
    """Trim nav/footer shell from OMU faculty and department news pages."""

    raw_text = extract_readable_text_from_html(html)
    lines = [collapse_whitespace(line) for line in raw_text.splitlines() if collapse_whitespace(line)]
    if not lines:
        return ""

    start_index = _find_preferred_title_line_index(lines, title=title)
    if start_index is None:
        start_index = 0
    else:
        start_index += 1

    normalized_title = normalize_text(title or "")
    body_lines: list[str] = []
    for line in lines[start_index:]:
        normalized_line = normalize_text(line)
        if not normalized_line:
            continue
        if _looks_like_markup_noise(line):
            continue
        if normalized_line in _FACULTY_DETAIL_SKIP_LINES:
            continue
        if normalized_line == normalized_title and body_lines:
            break
        if normalized_line in _FACULTY_DETAIL_STOP_MARKERS:
            break
        body_lines.append(line)

    while body_lines:
        first_line = body_lines[0]
        normalized_first = normalize_text(first_line)
        if normalized_first in _FACULTY_DETAIL_SKIP_LINES or normalized_first == normalized_title:
            body_lines.pop(0)
            continue
        if normalized_first.startswith("yazar:") or _looks_like_metadata_date_line(first_line):
            body_lines.pop(0)
            continue
        break

    return "\n".join(body_lines).strip()


def _extract_references_for_source(
    source: AnnouncementSourceRecord,
    index_html: str,
) -> list[AnnouncementReference]:
    if source.parser_key == "omu_faculty_home_announcements":
        return extract_omu_faculty_home_references_from_html(
            index_html,
            base_url=source.base_url or source.list_url,
            max_items=source.max_items_per_run,
        )
    if source.parser_key == "omu_main_announcements":
        return extract_omu_announcement_references_from_html(
            index_html,
            base_url=source.base_url or source.list_url,
            max_items=source.max_items_per_run,
        )
    return extract_announcement_references_from_html(
        index_html,
        base_url=source.base_url or source.list_url,
        max_items=source.max_items_per_run,
    )


async def _collect_references_for_source(
    source: AnnouncementSourceRecord,
    *,
    http_client: AnnouncementHTTPClient,
) -> list[AnnouncementReference]:
    index_html = await http_client.get_text(source.list_url)
    references = _extract_references_for_source(source, index_html)
    max_items = source.max_items_per_run
    if len(references) >= max_items:
        return references[:max_items]

    normalized_list_url = normalize_text(source.list_url)
    should_follow_pages = (
        source.parser_key == "omu_faculty_home_announcements"
        and "/tr/haberler" in normalized_list_url
    )
    if not should_follow_pages:
        return references

    page_urls = _extract_paginated_news_page_urls(
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
        page_refs = extract_omu_faculty_home_references_from_html(
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


def _extract_detail_text_for_source(
    source: AnnouncementSourceRecord,
    *,
    detail_html: str | None,
    reference: AnnouncementReference,
) -> str:
    if not detail_html:
        return ""
    if _looks_like_binary_payload(detail_html):
        return ""
    if source.parser_key == "omu_faculty_home_announcements":
        return extract_omu_faculty_home_text_from_html(
            detail_html,
            title=reference.title,
        )
    if source.parser_key == "omu_main_announcements":
        return extract_omu_announcement_text_from_html(
            detail_html,
            title=reference.title,
        )
    return extract_readable_text_from_html(detail_html)


def build_candidate_from_reference(
    reference: AnnouncementReference,
    *,
    source: AnnouncementSourceRecord,
    detail_html: str | None,
    fallback_department: str | None,
    fallback_faculty: str | None,
) -> AnnouncementCandidate:
    """Build a normalized candidate from a listing reference and optional detail page."""

    detail_text = _extract_detail_text_for_source(
        source,
        detail_html=detail_html,
        reference=reference,
    )
    teaser_text = reference.teaser or ""
    meta_description = extract_meta_description_from_html(detail_html)
    detail_summary = _pick_summary_line(detail_text) if detail_text and _has_useful_content(detail_text) else None
    teaser_summary = _pick_summary_line(teaser_text) if teaser_text else None
    meta_summary = _pick_summary_line(meta_description or "") if meta_description else None
    links = extract_announcement_links_from_html(
        detail_html,
        base_url=source.base_url or reference.source_url,
        source_url=reference.source_url,
        title=reference.title,
    )
    summary = detail_summary or teaser_summary or meta_summary
    if summary and len(summary) > 280:
        summary = f"{summary[:277].rstrip()}..."
    original_text = detail_text if _has_useful_content(detail_text) else ""
    if not original_text:
        if teaser_summary:
            original_text = teaser_text
        elif meta_summary:
            original_text = meta_description or ""
        else:
            original_text = reference.title
    if source.parser_key == "omu_faculty_home_announcements":
        published_at = reference.published_at
    else:
        published_at = reference.published_at or _parse_date(detail_html) or _parse_date(detail_text)
    return AnnouncementCandidate(
        title=reference.title,
        source_url=reference.source_url,
        original_text=original_text,
        summary=summary,
        display_summary=_build_display_summary_base(
            title=reference.title,
            summary=summary,
            original_text=original_text,
        ),
        published_at=published_at,
        faculty=fallback_faculty,
        department=fallback_department,
        links=links,
    )


async def sync_announcement_source(
    source: AnnouncementSourceRecord,
    *,
    http_client: AnnouncementHTTPClient | None = None,
    summary_refiner: AnnouncementSummaryRefiner | None = None,
    dry_run: bool = False,
    allow_deactivation: bool = True,
    fetch_details: bool = True,
) -> AnnouncementSourceSyncResult:
    """Fetch, parse and persist announcements for one source."""

    http_client = http_client or HttpxAnnouncementHTTPClient()
    try:
        references = await _collect_references_for_source(
            source,
            http_client=http_client,
        )
        candidates: list[AnnouncementCandidate] = []
        for reference in references:
            detail_html = None
            if fetch_details:
                try:
                    detail_html = await http_client.get_text(reference.source_url)
                except Exception:
                    detail_html = None
            candidates.append(
                build_candidate_from_reference(
                    reference,
                    source=source,
                    detail_html=detail_html,
                    fallback_department=source.department,
                    fallback_faculty=source.faculty,
                )
            )
        if summary_refiner is None:
            summary_refiner = NoOpAnnouncementSummaryRefiner()
        refined_candidates: list[AnnouncementCandidate] = []
        for candidate in candidates:
            display_summary = candidate.display_summary
            if _should_refine_display_summary(
                summary=candidate.summary,
                original_text=candidate.original_text,
            ):
                try:
                    refined = await summary_refiner.refine(
                        title=candidate.title,
                        summary=candidate.summary,
                        original_text=candidate.original_text,
                        links=candidate.links,
                    )
                except Exception:
                    refined = None
                if refined:
                    display_summary = refined
            refined_candidates.append(
                AnnouncementCandidate(
                    title=candidate.title,
                    source_url=candidate.source_url,
                    original_text=candidate.original_text,
                    summary=candidate.summary,
                    display_summary=display_summary,
                    published_at=candidate.published_at,
                    faculty=candidate.faculty,
                    department=candidate.department,
                    links=candidate.links,
                )
            )
        candidates = refined_candidates
    except Exception as exc:
        if dry_run:
            return AnnouncementSourceSyncResult(
                source=source,
                status="failed",
                stats=AnnouncementSyncStats(),
                error_message=str(exc),
            )
        async with get_session() as session:
            run = await create_announcement_sync_run(session, source_id=source.id)
            empty_stats = AnnouncementSyncStats()
            await finalize_announcement_sync_run(
                session,
                run=run,
                status="failed",
                stats=empty_stats,
                error_message=str(exc),
            )
            await mark_announcement_source_sync_result(
                session,
                source_id=source.id,
                success=False,
                error_message=str(exc),
            )
        return AnnouncementSourceSyncResult(
            source=source,
            status="failed",
            stats=AnnouncementSyncStats(),
            error_message=str(exc),
        )

    if dry_run and source.id <= 0:
        return AnnouncementSourceSyncResult(
            source=source,
            status="dry_run",
            stats=_build_dry_run_stats(candidates),
        )

    async with get_session() as session:
        run = None
        if not dry_run:
            run = await create_announcement_sync_run(session, source_id=source.id)
        stats = await upsert_announcements_for_source(
            session,
            source=source,
            candidates=candidates,
            dry_run=dry_run,
            allow_deactivation=allow_deactivation,
        )
        if not dry_run and run is not None:
            await finalize_announcement_sync_run(
                session,
                run=run,
                status="completed",
                stats=stats,
            )
            await mark_announcement_source_sync_result(
                session,
                source_id=source.id,
                success=True,
            )
        return AnnouncementSourceSyncResult(
            source=source,
            status="dry_run" if dry_run else "completed",
            stats=stats,
        )


async def sync_announcement_sources(
    sources: list[AnnouncementSourceRecord],
    *,
    http_client: AnnouncementHTTPClient | None = None,
    summary_refiner: AnnouncementSummaryRefiner | None = None,
    dry_run: bool = False,
    allow_deactivation: bool = True,
    fetch_details: bool = True,
) -> list[AnnouncementSourceSyncResult]:
    """Synchronize multiple announcement sources sequentially."""

    results: list[AnnouncementSourceSyncResult] = []
    for source in sources:
        results.append(
            await sync_announcement_source(
                source,
                http_client=http_client,
                summary_refiner=summary_refiner,
                dry_run=dry_run,
                allow_deactivation=allow_deactivation,
                fetch_details=fetch_details,
            )
        )
    return results
