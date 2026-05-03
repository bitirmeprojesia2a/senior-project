"""A2A service identity headers, request signing and published service id helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import hmac
import json
import secrets
from threading import Lock
import time
from typing import Any

from src.core.constants import Capability, Department

A2A_CALLER_ID_HEADER = "X-A2A-Caller-ID"
A2A_TARGET_ID_HEADER = "X-A2A-Target-ID"
A2A_TIMESTAMP_HEADER = "X-A2A-Timestamp"
A2A_NONCE_HEADER = "X-A2A-Nonce"
A2A_BODY_SHA256_HEADER = "X-A2A-Body-SHA256"
A2A_SIGNATURE_HEADER = "X-A2A-Signature"
MAIN_ORCHESTRATOR_SERVICE_ID = "main_orchestrator"
_SIGNATURE_VERSION = "v1"

_DEPARTMENT_SERVICE_IDS = {
    Department.STUDENT_AFFAIRS: "agent-student-affairs",
    Department.ACADEMIC_PROGRAMS: "agent-academic",
    Department.FINANCE: "agent-finance",
}

_CAPABILITY_SERVICE_IDS = {
    Capability.ANNOUNCEMENT: "agent-announcement",
    Capability.EVENT: "agent-event",
}

_SPECIALIST_SERVICE_IDS = {
    "tuition_agent": "agent-finance-tuition",
    "scholarship_agent": "agent-finance-scholarship",
    "registration_agent": "agent-student-registration",
    "graduation_agent": "agent-student-graduation",
    "internship_agent": "agent-student-internship",
    "student_life_agent": "agent-student-life",
    "curriculum_agent": "agent-academic-curriculum",
    "regulation_agent": "agent-academic-regulation",
    "international_agent": "agent-academic-international",
}


class A2ANonceReplayCache:
    """Small process-local nonce cache for rejecting replayed signed requests."""

    def __init__(self) -> None:
        self._seen: dict[str, int] = {}
        self._lock = Lock()

    @staticmethod
    def _cache_key(*, caller_id: str | None, target_id: str | None, nonce: str) -> str:
        return "\n".join([caller_id or "", target_id or "", nonce])

    def record_once(
        self,
        *,
        caller_id: str | None,
        target_id: str | None,
        nonce: str,
        now: int,
        ttl_seconds: int,
    ) -> bool:
        """Return False when the caller/target/nonce tuple was already used."""
        expires_at = now + max(1, ttl_seconds)
        key = self._cache_key(caller_id=caller_id, target_id=target_id, nonce=nonce)
        with self._lock:
            expired_keys = [
                cached_key
                for cached_key, cached_expires_at in self._seen.items()
                if cached_expires_at <= now
            ]
            for cached_key in expired_keys:
                self._seen.pop(cached_key, None)

            if key in self._seen:
                return False
            self._seen[key] = expires_at
            return True


_DEFAULT_REPLAY_CACHE = A2ANonceReplayCache()


def default_a2a_replay_cache() -> A2ANonceReplayCache:
    """Return the process-local replay cache used by inbound A2A endpoints."""
    return _DEFAULT_REPLAY_CACHE


def department_service_id(department: Department) -> str:
    """Return the published standalone service id for a department orchestrator."""
    return _DEPARTMENT_SERVICE_IDS[department]


def capability_service_id(capability: Capability) -> str:
    """Return the published standalone service id for a capability agent."""
    return _CAPABILITY_SERVICE_IDS[capability]


def specialist_service_id(agent_id: str) -> str | None:
    """Return the published standalone service id for a specialist agent."""
    return _SPECIALIST_SERVICE_IDS.get(agent_id)


def canonical_a2a_body_bytes(body: Any) -> bytes:
    """Return stable JSON bytes used for A2A body hashes/signatures."""
    return json.dumps(
        body if body is not None else {},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def a2a_body_sha256(body: Any) -> str:
    """Return hex SHA-256 of the canonical A2A request body."""
    return hashlib.sha256(canonical_a2a_body_bytes(body)).hexdigest()


def _signature_base(
    *,
    caller_id: str | None,
    target_id: str | None,
    timestamp: str,
    nonce: str,
    body_sha256: str,
) -> str:
    return "\n".join(
        [
            _SIGNATURE_VERSION,
            caller_id or "",
            target_id or "",
            timestamp,
            nonce,
            body_sha256,
        ]
    )


def sign_a2a_request(
    *,
    body: Any,
    secret: str,
    caller_id: str | None,
    target_id: str | None,
    timestamp: str | None = None,
    nonce: str | None = None,
) -> dict[str, str]:
    """Build A2A request-signature headers for a canonical JSON body."""
    signed_at = timestamp or str(int(time.time()))
    request_nonce = nonce or secrets.token_urlsafe(16)
    body_hash = a2a_body_sha256(body)
    base = _signature_base(
        caller_id=caller_id,
        target_id=target_id,
        timestamp=signed_at,
        nonce=request_nonce,
        body_sha256=body_hash,
    )
    digest = hmac.new(
        secret.encode("utf-8"),
        base.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        A2A_TIMESTAMP_HEADER: signed_at,
        A2A_NONCE_HEADER: request_nonce,
        A2A_BODY_SHA256_HEADER: body_hash,
        A2A_SIGNATURE_HEADER: f"{_SIGNATURE_VERSION}={digest}",
    }


def verify_a2a_request_signature(
    *,
    body: Any,
    secret: str,
    caller_id: str | None,
    target_id: str | None,
    timestamp: str | None,
    nonce: str | None,
    body_sha256: str | None,
    signature: str | None,
    ttl_seconds: int,
    now: float | None = None,
    replay_cache: A2ANonceReplayCache | None = None,
) -> tuple[bool, str]:
    """Validate A2A request signature headers.

    Returns `(ok, detail)` so API code can translate the failure to an HTTP
    response without leaking the signing secret.
    """
    if not timestamp or not nonce or not body_sha256 or not signature:
        return False, "A2A request signature headers eksik."

    try:
        request_time = int(timestamp)
    except ValueError:
        return False, "A2A request timestamp gecersiz."

    current_time = int(now if now is not None else time.time())
    allowed_skew = max(0, int(ttl_seconds))
    if abs(current_time - request_time) > allowed_skew:
        return False, "A2A request signature zaman penceresi disinda."

    actual_body_hash = a2a_body_sha256(body)
    if not hmac.compare_digest(actual_body_hash, body_sha256):
        return False, "A2A request body hash eslesmedi."

    expected = sign_a2a_request(
        body=body,
        secret=secret,
        caller_id=caller_id,
        target_id=target_id,
        timestamp=timestamp,
        nonce=nonce,
    )[A2A_SIGNATURE_HEADER]
    if not hmac.compare_digest(expected, signature):
        return False, "A2A request signature eslesmedi."
    if replay_cache is not None and not replay_cache.record_once(
        caller_id=caller_id,
        target_id=target_id,
        nonce=nonce,
        now=current_time,
        ttl_seconds=allowed_skew,
    ):
        return False, "A2A request nonce daha once kullanilmis."
    return True, "ok"


def build_a2a_auth_headers(
    *,
    internal_api_key: str | None,
    caller_id: str,
    target_id: str | None = None,
    body: Mapping[str, Any] | None = None,
    signature_secret: str | None = None,
) -> dict[str, str]:
    """Build auth and service identity headers for internal A2A calls."""
    headers = {A2A_CALLER_ID_HEADER: caller_id}
    if target_id:
        headers[A2A_TARGET_ID_HEADER] = target_id
    if internal_api_key:
        headers["X-Internal-API-Key"] = internal_api_key
    if body is not None and signature_secret:
        headers.update(
            sign_a2a_request(
                body=body,
                secret=signature_secret,
                caller_id=caller_id,
                target_id=target_id,
            )
        )
    return headers


__all__ = [
    "A2A_BODY_SHA256_HEADER",
    "A2A_CALLER_ID_HEADER",
    "A2A_NONCE_HEADER",
    "A2A_SIGNATURE_HEADER",
    "A2A_TARGET_ID_HEADER",
    "A2A_TIMESTAMP_HEADER",
    "MAIN_ORCHESTRATOR_SERVICE_ID",
    "A2ANonceReplayCache",
    "a2a_body_sha256",
    "build_a2a_auth_headers",
    "capability_service_id",
    "canonical_a2a_body_bytes",
    "default_a2a_replay_cache",
    "department_service_id",
    "sign_a2a_request",
    "specialist_service_id",
    "verify_a2a_request_signature",
]
