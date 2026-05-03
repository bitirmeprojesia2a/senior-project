"""Shared AgentCard security metadata for A2A JSON-RPC endpoints."""

from __future__ import annotations

from a2a.types import APIKeySecurityScheme, In, SecurityScheme

from src.a2a.service_identity import (
    A2A_BODY_SHA256_HEADER,
    A2A_CALLER_ID_HEADER,
    A2A_NONCE_HEADER,
    A2A_SIGNATURE_HEADER,
    A2A_TARGET_ID_HEADER,
    A2A_TIMESTAMP_HEADER,
)


def _api_key_header_scheme(name: str, description: str) -> SecurityScheme:
    return SecurityScheme(
        root=APIKeySecurityScheme.model_validate(
            {
                "in": In.header.value,
                "name": name,
                "description": description,
            }
        )
    )


def a2a_hmac_security_schemes() -> dict[str, SecurityScheme]:
    """Return header-based security schemes advertised in AgentCards."""
    return {
        "a2aCallerId": _api_key_header_scheme(
            A2A_CALLER_ID_HEADER,
            "Calling A2A service identity.",
        ),
        "a2aTargetId": _api_key_header_scheme(
            A2A_TARGET_ID_HEADER,
            "Expected target A2A service identity.",
        ),
        "a2aTimestamp": _api_key_header_scheme(
            A2A_TIMESTAMP_HEADER,
            "Signed request timestamp.",
        ),
        "a2aNonce": _api_key_header_scheme(
            A2A_NONCE_HEADER,
            "Signed request nonce.",
        ),
        "a2aBodySha256": _api_key_header_scheme(
            A2A_BODY_SHA256_HEADER,
            "Canonical JSON body SHA-256 hash.",
        ),
        "a2aSignature": _api_key_header_scheme(
            A2A_SIGNATURE_HEADER,
            "HMAC-SHA256 signature over caller, target, timestamp, nonce, and body hash.",
        ),
    }


def a2a_hmac_security_requirement() -> list[dict[str, list[str]]]:
    """Return the advertised AgentCard security requirement."""
    return [
        {
            scheme_name: []
            for scheme_name in a2a_hmac_security_schemes()
        }
    ]


__all__ = [
    "a2a_hmac_security_requirement",
    "a2a_hmac_security_schemes",
]
