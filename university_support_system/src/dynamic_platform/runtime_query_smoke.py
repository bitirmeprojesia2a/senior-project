"""HTTP query smoke checks for an already running dynamic tenant runtime."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_TENANT_BASE_URLS = {
    "acme_demo": "http://127.0.0.1:18000",
    "city_demo": "http://127.0.0.1:28000",
}

DEFAULT_TENANT_QUERIES = {
    "acme_demo": "VPN erişimi için nasıl talep açarım?",
    "city_demo": "Ruhsat ön başvurusu için hangi belgeler gerekir?",
}


@dataclass(frozen=True)
class DynamicQuerySmokeReport:
    tenant_key: str
    ok: bool
    base_url: str
    endpoint: str
    query: str
    status: str
    http_status: int | None
    latency_ms: float | None
    answer_status: str | None
    selected_capabilities: list[str]
    agents: list[str]
    sources: list[str]
    final_owner: str | None
    answer_preview: str
    errors: list[str]
    warnings: list[str]
    raw_response: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "base_url": self.base_url,
            "endpoint": self.endpoint,
            "query": self.query,
            "status": self.status,
            "http_status": self.http_status,
            "latency_ms": self.latency_ms,
            "answer_status": self.answer_status,
            "selected_capabilities": self.selected_capabilities,
            "agents": self.agents,
            "sources": self.sources,
            "final_owner": self.final_owner,
            "answer_preview": self.answer_preview,
            "errors": self.errors,
            "warnings": self.warnings,
            "raw_response": self.raw_response,
            "notes": [
                "This command only calls an already running dynamic /dynamic/query endpoint.",
                "It does not start, stop, build, pull, index, or mutate protected classic runtime services.",
            ],
        }


def run_dynamic_query_smoke(
    *,
    tenant_key: str,
    base_url: str | None = None,
    query: str | None = None,
    timeout_seconds: float = 10.0,
) -> DynamicQuerySmokeReport:
    resolved_base_url = (base_url or DEFAULT_TENANT_BASE_URLS.get(tenant_key) or "").rstrip("/")
    resolved_query = query or DEFAULT_TENANT_QUERIES.get(tenant_key) or "Merhaba, bu tenant hangi konuda destek veriyor?"
    endpoint = f"{resolved_base_url}/dynamic/query" if resolved_base_url else ""
    errors: list[str] = []
    warnings: list[str] = []
    if not resolved_base_url:
        errors.append("No base URL provided and no default URL is known for this tenant.")
        return DynamicQuerySmokeReport(
            tenant_key=tenant_key,
            ok=False,
            base_url=resolved_base_url,
            endpoint=endpoint,
            query=resolved_query,
            status="missing_base_url",
            http_status=None,
            latency_ms=None,
            answer_status=None,
            selected_capabilities=[],
            agents=[],
            sources=[],
            final_owner=None,
            answer_preview="",
            errors=errors,
            warnings=warnings,
            raw_response=None,
        )

    payload = json.dumps(
        {
            "query": resolved_query,
            "conversation_id": f"runtime-query-smoke-{tenant_key}",
            "user_id": "runtime-query-smoke",
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    started = time.perf_counter()
    http_status: int | None = None
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            http_status = response.status
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        http_status = exc.code
        body = exc.read().decode("utf-8", errors="replace")
        errors.append(f"HTTP {exc.code}: {body[:300]}")
    except URLError as exc:
        errors.append(f"Connection error: {exc.reason}")
        body = ""
    except TimeoutError:
        errors.append(f"Timed out after {timeout_seconds} seconds.")
        body = ""
    latency_ms = round((time.perf_counter() - started) * 1000, 2)

    raw_response: dict[str, Any] | None = None
    if body:
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                raw_response = parsed
            else:
                errors.append("Response JSON was not an object.")
        except json.JSONDecodeError as exc:
            errors.append(f"Response was not valid JSON: {exc}")

    answer_status = str(raw_response.get("answer_status")) if raw_response and raw_response.get("answer_status") else None
    selected_capabilities = _string_list(raw_response.get("selected_capabilities") if raw_response else None)
    agents = _string_list(raw_response.get("agents") if raw_response else None)
    sources = _string_list(raw_response.get("sources") if raw_response else None)
    final_owner = str(raw_response.get("final_owner")) if raw_response and raw_response.get("final_owner") else None
    answer = str(raw_response.get("answer")) if raw_response and raw_response.get("answer") else ""
    answer_preview = _preview(answer)

    if raw_response and answer_status != "answered":
        warnings.append(f"Dynamic runtime returned answer_status={answer_status or 'unknown'}.")
    if raw_response and not sources:
        warnings.append("Dynamic runtime returned no tenant sources.")
    if raw_response and raw_response.get("tenant_key") != tenant_key:
        errors.append(f"Response tenant_key={raw_response.get('tenant_key')!r} did not match requested tenant.")

    ok = not errors and http_status is not None and 200 <= http_status < 300 and raw_response is not None
    return DynamicQuerySmokeReport(
        tenant_key=tenant_key,
        ok=ok,
        base_url=resolved_base_url,
        endpoint=endpoint,
        query=resolved_query,
        status="ok" if ok else "failed",
        http_status=http_status,
        latency_ms=latency_ms,
        answer_status=answer_status,
        selected_capabilities=selected_capabilities,
        agents=agents,
        sources=sources,
        final_owner=final_owner,
        answer_preview=answer_preview,
        errors=errors,
        warnings=warnings,
        raw_response=raw_response,
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _preview(text: str, limit: int = 500) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."

