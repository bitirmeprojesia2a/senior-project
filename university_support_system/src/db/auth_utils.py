"""Utility helpers for auth and OTP flows."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def ensure_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if len(local) <= 2:
        masked_local = local[:1] + "*"
    else:
        masked_local = local[:2] + "*" * max(1, len(local) - 2)
    return f"{masked_local}@{domain}" if domain else masked_local


def hash_otp(code: str) -> str:
    return sha256(code.encode("utf-8")).hexdigest()
