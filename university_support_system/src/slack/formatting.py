"""Slack metin temizleme ve cevap bolme yardimcilari."""

from __future__ import annotations

import html
import re

DEFAULT_MAX_SLACK_MESSAGE_CHARS = 3500

_BOT_MENTION_RE = re.compile(r"<@[A-Z0-9][A-Z0-9._-]*>\s*", re.IGNORECASE)
_ANGLE_LINK_RE = re.compile(r"<([^>|]+)\|([^>]+)>")
_ANGLE_URL_RE = re.compile(r"<(https?://[^>]+)>")
_WHITESPACE_RE = re.compile(r"[ \t]+")


def normalize_slack_text(text: str | None) -> str:
    """Slack event text'ini bot mention ve HTML entity'lerinden arindirir."""

    if not text:
        return ""
    cleaned = html.unescape(text)
    cleaned = _BOT_MENTION_RE.sub("", cleaned)
    cleaned = _ANGLE_LINK_RE.sub(r"\2 (\1)", cleaned)
    cleaned = _ANGLE_URL_RE.sub(r"\1", cleaned)
    cleaned = _WHITESPACE_RE.sub(" ", cleaned)
    return cleaned.strip()


def split_slack_message(
    text: str | None,
    *,
    max_chars: int = DEFAULT_MAX_SLACK_MESSAGE_CHARS,
) -> list[str]:
    """Slack limitlerine guvenli kalmak icin uzun metni parcalara ayirir."""

    cleaned = (text or "").strip()
    if not cleaned:
        return ["Cevap üretilemedi. Lütfen sorunuzu biraz daha açık yazar mısınız?"]
    if len(cleaned) <= max_chars:
        return [cleaned]

    chunks: list[str] = []
    current = ""
    for paragraph in cleaned.splitlines():
        paragraph = paragraph.rstrip()
        candidate = f"{current}\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        while len(paragraph) > max_chars:
            chunks.append(paragraph[:max_chars].rstrip())
            paragraph = paragraph[max_chars:].lstrip()
        current = paragraph

    if current:
        chunks.append(current)
    return chunks
