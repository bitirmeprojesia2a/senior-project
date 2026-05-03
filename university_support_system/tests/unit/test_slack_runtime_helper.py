"""Slack runtime helper CLI tests."""

from __future__ import annotations

from pathlib import Path

from scripts import slack_runtime


def test_slack_runtime_up_a2a_uses_full_compose_stack(monkeypatch):
    captured = {}

    def fake_run(command):
        captured["command"] = command
        return 0

    monkeypatch.setattr(slack_runtime, "_run", fake_run)
    monkeypatch.setattr(
        "sys.argv",
        ["slack_runtime.py", "up", "--runtime", "a2a"],
    )

    assert slack_runtime.main() == 0

    command = captured["command"]
    assert "docker-compose.a2a-existing-infra.yml" in command
    assert "docker-compose.slack.yml" in command
    assert command[-2:] == ["--no-build", "slack-bot-a2a"]


def test_slack_runtime_stop_inprocess_uses_slack_only_compose(monkeypatch):
    captured = {}

    def fake_run(command):
        captured["command"] = command
        return 0

    monkeypatch.setattr(slack_runtime, "_run", fake_run)
    monkeypatch.setattr(
        "sys.argv",
        ["slack_runtime.py", "stop", "--runtime", "inprocess"],
    )

    assert slack_runtime.main() == 0

    command = captured["command"]
    assert "docker-compose.a2a-existing-infra.yml" not in command
    assert "docker-compose.slack.yml" in command
    assert command[-2:] == ["stop", "slack-bot-inprocess"]


def test_slack_runtime_up_with_build_passes_compose_build_flag(monkeypatch):
    captured = {}

    def fake_run(command):
        captured["command"] = command
        return 0

    monkeypatch.setattr(slack_runtime, "_run", fake_run)
    monkeypatch.setattr(
        "sys.argv",
        ["slack_runtime.py", "up", "--runtime", "a2a", "--build"],
    )

    assert slack_runtime.main() == 0

    command = captured["command"]
    assert "--build" in command
    assert "--no-build" not in command
    assert command[-1] == "slack-bot-a2a"


def test_slack_a2a_compose_includes_a2a_security_environment():
    compose_text = Path("docker-compose.slack.yml").read_text(encoding="utf-8")

    expected_keys = [
        "SERVER_INTERNAL_API_KEY",
        "A2A_INTERNAL_API_KEY",
        "A2A_REQUIRE_SERVICE_IDENTITY",
        "A2A_REQUIRE_REQUEST_SIGNATURE",
        "A2A_REQUEST_SIGNATURE_SECRET",
        "A2A_ALLOWED_CALLER_IDS",
        "A2A_DISCOVERY_AGENT_CARD_ENABLED",
    ]

    for key in expected_keys:
        assert key in compose_text
