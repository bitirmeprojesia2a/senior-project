"""A2A service identity and request-signature tests."""

from src.a2a.service_identity import (
    A2ANonceReplayCache,
    A2A_BODY_SHA256_HEADER,
    A2A_NONCE_HEADER,
    A2A_SIGNATURE_HEADER,
    A2A_TIMESTAMP_HEADER,
    sign_a2a_request,
    verify_a2a_request_signature,
)


def test_a2a_request_signature_roundtrip_accepts_canonical_body():
    body = {
        "jsonrpc": "2.0",
        "id": "req-1",
        "method": "message/send",
        "params": {"metadata": {"b": 2, "a": 1}},
    }

    headers = sign_a2a_request(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp="1800000000",
        nonce="nonce-1",
    )

    ok, detail = verify_a2a_request_signature(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp=headers[A2A_TIMESTAMP_HEADER],
        nonce=headers[A2A_NONCE_HEADER],
        body_sha256=headers[A2A_BODY_SHA256_HEADER],
        signature=headers[A2A_SIGNATURE_HEADER],
        ttl_seconds=300,
        now=1800000001,
    )

    assert ok is True
    assert detail == "ok"


def test_a2a_request_signature_rejects_body_tampering():
    body = {"department": "finance", "query": "Harc odemesi nasil yapilir?"}
    headers = sign_a2a_request(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp="1800000000",
        nonce="nonce-1",
    )

    ok, detail = verify_a2a_request_signature(
        body={**body, "query": "Degistirilmis soru"},
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp=headers[A2A_TIMESTAMP_HEADER],
        nonce=headers[A2A_NONCE_HEADER],
        body_sha256=headers[A2A_BODY_SHA256_HEADER],
        signature=headers[A2A_SIGNATURE_HEADER],
        ttl_seconds=300,
        now=1800000001,
    )

    assert ok is False
    assert "body hash" in detail


def test_a2a_request_signature_rejects_expired_timestamp():
    body = {"department": "finance", "query": "Harc odemesi nasil yapilir?"}
    headers = sign_a2a_request(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp="1800000000",
        nonce="nonce-1",
    )

    ok, detail = verify_a2a_request_signature(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp=headers[A2A_TIMESTAMP_HEADER],
        nonce=headers[A2A_NONCE_HEADER],
        body_sha256=headers[A2A_BODY_SHA256_HEADER],
        signature=headers[A2A_SIGNATURE_HEADER],
        ttl_seconds=300,
        now=1800001000,
    )

    assert ok is False
    assert "zaman" in detail


def test_a2a_request_signature_rejects_replayed_nonce_with_cache():
    body = {"department": "finance", "query": "Harc odemesi nasil yapilir?"}
    headers = sign_a2a_request(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp="1800000000",
        nonce="nonce-replay",
    )
    replay_cache = A2ANonceReplayCache()

    first_ok, first_detail = verify_a2a_request_signature(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp=headers[A2A_TIMESTAMP_HEADER],
        nonce=headers[A2A_NONCE_HEADER],
        body_sha256=headers[A2A_BODY_SHA256_HEADER],
        signature=headers[A2A_SIGNATURE_HEADER],
        ttl_seconds=300,
        now=1800000001,
        replay_cache=replay_cache,
    )
    second_ok, second_detail = verify_a2a_request_signature(
        body=body,
        secret="signing-secret",
        caller_id="main_orchestrator",
        target_id="agent-finance",
        timestamp=headers[A2A_TIMESTAMP_HEADER],
        nonce=headers[A2A_NONCE_HEADER],
        body_sha256=headers[A2A_BODY_SHA256_HEADER],
        signature=headers[A2A_SIGNATURE_HEADER],
        ttl_seconds=300,
        now=1800000002,
        replay_cache=replay_cache,
    )

    assert first_ok is True
    assert first_detail == "ok"
    assert second_ok is False
    assert "nonce" in second_detail


def test_a2a_replay_cache_expires_nonce_after_ttl():
    replay_cache = A2ANonceReplayCache()

    assert replay_cache.record_once(
        caller_id="main_orchestrator",
        target_id="agent-finance",
        nonce="nonce-expiring",
        now=10,
        ttl_seconds=2,
    ) is True
    assert replay_cache.record_once(
        caller_id="main_orchestrator",
        target_id="agent-finance",
        nonce="nonce-expiring",
        now=11,
        ttl_seconds=2,
    ) is False
    assert replay_cache.record_once(
        caller_id="main_orchestrator",
        target_id="agent-finance",
        nonce="nonce-expiring",
        now=12,
        ttl_seconds=2,
    ) is True
