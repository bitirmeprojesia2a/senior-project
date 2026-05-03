"""Slack formatting yardimcilari testleri."""

from src.slack.formatting import normalize_slack_text, split_slack_message


def test_normalize_slack_text_removes_mentions_and_unescapes_links():
    text = "<@U123> Ders kaydi &amp; harc <https://omu.edu.tr|OMU> ne zaman?"

    assert normalize_slack_text(text) == "Ders kaydi & harc OMU (https://omu.edu.tr) ne zaman?"


def test_split_slack_message_chunks_long_text():
    chunks = split_slack_message("a" * 12, max_chars=5)

    assert chunks == ["aaaaa", "aaaaa", "aa"]
