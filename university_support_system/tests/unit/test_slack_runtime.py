"""Slack runtime launcher tests."""

from __future__ import annotations

from argparse import Namespace

from scripts import slack_runtime
from scripts.run_slack_bot import _configure_runtime_env


def test_configure_slack_runtime_inprocess(monkeypatch):
    monkeypatch.delenv("A2A_MODE", raising=False)
    monkeypatch.delenv("A2A_SPECIALIST_MODE", raising=False)

    _configure_runtime_env(
        Namespace(
            runtime="inprocess",
            a2a_endpoint_profile="local",
            transport_protocol="jsonrpc",
            slack_env_prefix=None,
        )
    )

    import os

    assert os.environ["A2A_MODE"] == "inprocess"
    assert os.environ["A2A_SPECIALIST_MODE"] == "inprocess"


def test_configure_slack_runtime_a2a_uses_local_defaults(monkeypatch):
    for key in (
        "A2A_MODE",
        "A2A_SPECIALIST_MODE",
        "A2A_TRANSPORT_PROTOCOL",
        "A2A_STUDENT_AFFAIRS_URL",
        "A2A_ACADEMIC_PROGRAMS_URL",
        "A2A_FINANCE_URL",
    ):
        monkeypatch.delenv(key, raising=False)

    _configure_runtime_env(
        Namespace(
            runtime="a2a",
            a2a_endpoint_profile="local",
            transport_protocol="jsonrpc",
            slack_env_prefix=None,
        )
    )

    import os

    assert os.environ["A2A_MODE"] == "http"
    assert os.environ["A2A_SPECIALIST_MODE"] == "http"
    assert os.environ["A2A_TRANSPORT_PROTOCOL"] == "jsonrpc"
    assert os.environ["A2A_STUDENT_AFFAIRS_URL"] == "http://localhost:8101"
    assert os.environ["A2A_ACADEMIC_PROGRAMS_URL"] == "http://localhost:8102"
    assert os.environ["A2A_FINANCE_URL"] == "http://localhost:8103"


def test_configure_slack_runtime_a2a_can_copy_prefixed_tokens(monkeypatch):
    monkeypatch.delenv("A2A_STUDENT_AFFAIRS_URL", raising=False)
    monkeypatch.setenv("SLACK_A2A_BOT_TOKEN", "xoxb-a2a")
    monkeypatch.setenv("SLACK_A2A_SIGNING_SECRET", "secret-a2a")
    monkeypatch.setenv("SLACK_A2A_APP_TOKEN", "xapp-a2a")

    _configure_runtime_env(
        Namespace(
            runtime="a2a",
            a2a_endpoint_profile="docker",
            transport_protocol="jsonrpc",
            slack_env_prefix="SLACK_A2A",
        )
    )

    import os

    assert os.environ["SLACK_BOT_TOKEN"] == "xoxb-a2a"
    assert os.environ["SLACK_SIGNING_SECRET"] == "secret-a2a"
    assert os.environ["SLACK_APP_TOKEN"] == "xapp-a2a"
    assert os.environ["A2A_STUDENT_AFFAIRS_URL"] == "http://agent-student-affairs:8101"


def test_slack_runtime_a2a_stack_defaults_to_gpu_build_profile(monkeypatch):
    calls = []

    def fake_run(command, cwd, check):
        calls.append((command, cwd, check))

        class Completed:
            returncode = 0

        return Completed()

    monkeypatch.delenv("A2A_TORCH_VARIANT", raising=False)
    monkeypatch.delenv("A2A_BASE_IMAGE", raising=False)
    monkeypatch.delenv("A2A_TRANSPORT_PROTOCOL", raising=False)
    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr(
        "sys.argv",
        ["slack_runtime", "up", "--runtime", "a2a"],
    )

    assert slack_runtime.main() == 0

    import os

    assert os.environ["A2A_TORCH_VARIANT"] == "gpu"
    assert os.environ["A2A_BASE_IMAGE"] == slack_runtime.DEFAULT_A2A_GPU_BASE_IMAGE
    assert os.environ["A2A_TRANSPORT_PROTOCOL"] == "jsonrpc"
    assert any("docker-compose.a2a-app-gpu.yml" in part for part in calls[0][0])
    assert calls[0][0][-2:] == ["--no-build", "slack-bot-a2a"]


def test_slack_runtime_slack_only_does_not_force_gpu_build_profile(monkeypatch):
    def fake_run(command, cwd, check):
        class Completed:
            returncode = 0

        return Completed()

    monkeypatch.delenv("A2A_TORCH_VARIANT", raising=False)
    monkeypatch.delenv("A2A_BASE_IMAGE", raising=False)
    monkeypatch.delenv("A2A_TRANSPORT_PROTOCOL", raising=False)
    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr(
        "sys.argv",
        ["slack_runtime", "up", "--runtime", "a2a", "--no-a2a-stack"],
    )

    assert slack_runtime.main() == 0

    import os

    assert "A2A_TORCH_VARIANT" not in os.environ
    assert "A2A_BASE_IMAGE" not in os.environ
    assert "A2A_TRANSPORT_PROTOCOL" not in os.environ
