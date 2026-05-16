from __future__ import annotations

from src.llm.api_key_pool import (
    api_key_fingerprint,
    get_api_key_pool,
    org_fingerprint_from_message,
    reset_api_key_pools,
)


def test_api_key_pool_rotates_process_wide_for_same_provider() -> None:
    reset_api_key_pools()
    pool_a = get_api_key_pool("groq:https://api.groq.com/openai/v1", "key-a,key-b")
    pool_b = get_api_key_pool("groq:https://api.groq.com/openai/v1", "key-a,key-b")

    assert pool_a is pool_b
    assert pool_a.next_key().key == "key-a"
    assert pool_b.next_key().key == "key-b"
    assert pool_a.next_key().key == "key-a"


def test_api_key_pool_cools_down_rate_limited_key() -> None:
    reset_api_key_pools()
    pool = get_api_key_pool("groq:test", "key-a,key-b")
    first = pool.next_key()

    pool.mark_error(
        fingerprint=first.fingerprint,
        reason="rate_limit",
        cooldown_seconds=60,
    )

    second = pool.next_key()
    assert second.key == "key-b"
    assert second.fingerprint != first.fingerprint


def test_api_key_pool_cools_down_known_org_keys_together() -> None:
    reset_api_key_pools()
    pool = get_api_key_pool("groq:test", "key-a,key-b,key-c")
    first = pool.next_key()
    pool.mark_error(
        fingerprint=first.fingerprint,
        reason="rate_limit",
        cooldown_seconds=60,
        provider_org_fingerprint="org-a",
    )

    second = pool.next_key()
    assert second.key == "key-b"
    pool.mark_error(
        fingerprint=second.fingerprint,
        reason="rate_limit",
        cooldown_seconds=60,
        provider_org_fingerprint="org-a",
    )

    third = pool.next_key()
    assert third.key == "key-c"
    diagnostics = pool.diagnostics()
    org_entries = [
        entry
        for entry in diagnostics["entries"]
        if entry["provider_org_fingerprint"] == "org-a"
    ]
    assert len(org_entries) == 2
    assert all(entry["org_cooldown_active"] for entry in org_entries)
    assert diagnostics["org_cooldowns"] == {"org-a": True}


def test_api_key_fingerprint_does_not_expose_secret() -> None:
    fingerprint = api_key_fingerprint("gsk_real_secret")

    assert fingerprint
    assert "gsk" not in fingerprint
    assert "secret" not in fingerprint


def test_org_fingerprint_from_provider_error_message() -> None:
    fingerprint = org_fingerprint_from_message(
        "Rate limit reached in organization `org_01abcXYZ` service tier"
    )

    assert fingerprint
    assert "org_" not in fingerprint
