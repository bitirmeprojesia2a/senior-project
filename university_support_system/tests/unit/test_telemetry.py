"""Telemetry discovery helper tests."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

import pytest

import src.db.telemetry as telemetry_module
from src.core.config import settings
from src.core.constants import Department
from src.db.support_models import AgentRegistry, AgentTask, QueryLog
from src.db.telemetry import TelemetryService


class _FakeExecuteResult:
    def __init__(self, row):
        self._row = row

    def one_or_none(self):
        return self._row


class _FakeSession:
    def __init__(self, row):
        self._row = row

    async def execute(self, stmt):
        _ = stmt
        return _FakeExecuteResult(self._row)


@asynccontextmanager
async def _fake_get_session(row):
    yield _FakeSession(row)


@pytest.mark.asyncio
async def test_resolve_department_endpoint_returns_fresh_registry_endpoint(monkeypatch):
    fresh_heartbeat = datetime.now(UTC) - timedelta(seconds=10)
    monkeypatch.setattr(settings.a2a, "discovery_ttl_seconds", 120.0)
    monkeypatch.setattr(
        telemetry_module,
        "get_session",
        lambda: _fake_get_session(("http://registry-finance:8103", fresh_heartbeat)),
    )

    resolved = await TelemetryService().resolve_department_endpoint(Department.FINANCE)

    assert resolved == "http://registry-finance:8103"


@pytest.mark.asyncio
async def test_resolve_department_endpoint_ignores_stale_registry_endpoint(monkeypatch):
    stale_heartbeat = datetime.now(UTC) - timedelta(seconds=300)
    monkeypatch.setattr(settings.a2a, "discovery_ttl_seconds", 120.0)
    monkeypatch.setattr(
        telemetry_module,
        "get_session",
        lambda: _fake_get_session(("http://registry-finance:8103", stale_heartbeat)),
    )

    resolved = await TelemetryService().resolve_department_endpoint(Department.FINANCE)

    assert resolved is None


@pytest.mark.asyncio
async def test_resolve_department_endpoint_accepts_missing_heartbeat_when_row_exists(monkeypatch):
    monkeypatch.setattr(settings.a2a, "discovery_ttl_seconds", 120.0)
    monkeypatch.setattr(
        telemetry_module,
        "get_session",
        lambda: _fake_get_session(("http://registry-finance:8103", None)),
    )

    resolved = await TelemetryService().resolve_department_endpoint(Department.FINANCE)

    assert resolved == "http://registry-finance:8103"


@pytest.mark.asyncio
async def test_get_a2a_diagnostics_summarizes_recent_tasks(monkeypatch, db_session):
    now = datetime.now(UTC)
    sender = AgentRegistry(
        agent_id="main_orchestrator",
        name="Main Orchestrator",
        department="system",
        role="main_orchestrator",
        is_active=True,
        last_heartbeat=now,
    )
    receiver = AgentRegistry(
        agent_id="event_agent",
        name="Event Agent",
        department="event",
        role="capability_agent",
        endpoint="http://agent-event:8105",
        is_active=True,
        last_heartbeat=now,
    )
    db_session.add_all([sender, receiver])
    await db_session.flush()
    db_session.add_all(
        [
            QueryLog(
                query_text="Bu hafta etkinlik var mi?",
                departments=["event"],
                status="completed",
                response_time_ms=120,
                created_at=now,
            ),
            QueryLog(
                query_text="Failing query",
                departments=["event"],
                status="failed",
                error="boom",
                created_at=now,
            ),
            AgentTask(
                task_id="task-ok",
                sender_agent_id=sender.id,
                receiver_agent_id=receiver.id,
                task_type="event_query",
                status="completed",
                payload={"query_text": "Bu hafta etkinlik var mi?", "trace": {"trace_id": "trace-ok"}},
                result={"success": True, "latency_ms": 42.5},
                completed_at=now,
                created_at=now,
            ),
            AgentTask(
                task_id="task-fail",
                sender_agent_id=sender.id,
                receiver_agent_id=receiver.id,
                task_type="event_query",
                status="failed",
                payload={"query_text": "Failing query", "trace": {"trace_id": "trace-fail"}},
                result={"latency_ms": 75.0},
                error_msg="timeout",
                completed_at=now,
                created_at=now,
            ),
        ]
    )
    await db_session.flush()

    @asynccontextmanager
    async def _session_override():
        yield db_session

    monkeypatch.setattr(telemetry_module, "get_session", _session_override)

    diagnostics = await TelemetryService().get_a2a_diagnostics(
        window_minutes=60,
        recent_limit=1,
    )

    assert diagnostics["status"] == "ok"
    assert diagnostics["overview"]["query_count"] == 2
    assert diagnostics["overview"]["query_failure_count"] == 1
    assert diagnostics["overview"]["agent_task_count"] == 2
    assert diagnostics["overview"]["agent_task_failure_count"] == 1
    assert diagnostics["overview"]["avg_response_time_ms"] == 120.0
    assert diagnostics["agents"][0]["agent_id"] == "event_agent"
    assert diagnostics["agents"][0]["total_tasks"] == 2
    assert diagnostics["agents"][0]["failed_tasks"] == 1
    assert diagnostics["agents"][0]["latency_sample_count"] == 2
    assert diagnostics["agents"][0]["avg_latency_ms"] == 58.75
    assert diagnostics["recent_failures"][0]["task_id"] == "task-fail"
    assert diagnostics["recent_failures"][0]["trace_id"] == "trace-fail"
