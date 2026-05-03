"""Event source helper testleri."""

from datetime import UTC, datetime

from src.db.event_sources import build_event_content_hash, summarize_event_text


def test_build_event_content_hash_changes_with_start_time():
    first = build_event_content_hash(
        title="Kariyer Gunleri",
        source_url="https://example.com/events/kariyer-gunleri",
        original_text="Etkinlik aciklamasi",
        starts_at=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
        location="Ataturk Kongre Merkezi",
    )
    second = build_event_content_hash(
        title="Kariyer Gunleri",
        source_url="https://example.com/events/kariyer-gunleri",
        original_text="Etkinlik aciklamasi",
        starts_at=datetime(2026, 4, 21, 10, 0, tzinfo=UTC),
        location="Ataturk Kongre Merkezi",
    )

    assert first != second


def test_summarize_event_text_appends_location_when_available():
    summary = summarize_event_text(
        title="Kariyer Gunleri",
        original_text="Farkli sektorlerden konusmacilar ogrencilerle bulusacak.",
        location="Ataturk Kongre Merkezi",
    )

    assert "Ataturk Kongre Merkezi" in summary


def test_summarize_event_text_falls_back_to_title():
    summary = summarize_event_text(
        title="Bahar Senligi",
        original_text=None,
        location=None,
    )

    assert summary == "Bahar Senligi"
