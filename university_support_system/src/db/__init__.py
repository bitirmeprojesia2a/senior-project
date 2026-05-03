"""Lazy exports for database helpers and services."""

from __future__ import annotations

from typing import Any

__all__ = [
    "AuthContext",
    "AuthService",
    "Base",
    "AnnouncementCandidate",
    "AnnouncementSourceRecord",
    "AnnouncementSyncStats",
    "ConversationContextService",
    "ConversationResolution",
    "ConversationStateData",
    "ConversationTurnData",
    "EventCandidate",
    "EventSourceRecord",
    "EventSyncStats",
    "OfficeContactRecord",
    "ProfileContextData",
    "ProfileContextService",
    "TelemetryService",
    "fetch_active_announcement_sources",
    "fetch_active_event_sources",
    "fetch_relevant_events",
    "fetch_relevant_announcements",
    "fetch_office_contacts",
    "format_office_contact",
    "get_or_create_announcement_source",
    "get_or_create_event_source",
    "extract_profile_from_text",
    "get_session",
    "check_db_health",
    "dispose_engine",
    "init_engine",
    "looks_like_profile_submission",
]


def __getattr__(name: str) -> Any:
    if name in {"AuthContext", "AuthService"}:
        from src.db.auth import AuthContext, AuthService

        return {"AuthContext": AuthContext, "AuthService": AuthService}[name]

    if name in {"check_db_health", "dispose_engine", "get_session", "init_engine"}:
        from src.db.connection import (
            check_db_health,
            dispose_engine,
            get_session,
            init_engine,
        )

        return {
            "check_db_health": check_db_health,
            "dispose_engine": dispose_engine,
            "get_session": get_session,
            "init_engine": init_engine,
        }[name]

    if name == "Base":
        from src.db.models import Base

        return Base

    if name in {"OfficeContactRecord", "fetch_office_contacts", "format_office_contact"}:
        from src.db.office_contacts import (
            OfficeContactRecord,
            fetch_office_contacts,
            format_office_contact,
        )

        return {
            "OfficeContactRecord": OfficeContactRecord,
            "fetch_office_contacts": fetch_office_contacts,
            "format_office_contact": format_office_contact,
        }[name]

    if name == "fetch_relevant_announcements":
        from src.db.announcements import fetch_relevant_announcements

        return fetch_relevant_announcements

    if name in {
        "AnnouncementCandidate",
        "AnnouncementSourceRecord",
        "AnnouncementSyncStats",
        "fetch_active_announcement_sources",
        "get_or_create_announcement_source",
    }:
        from src.db.announcement_sources import (
            AnnouncementCandidate,
            AnnouncementSourceRecord,
            AnnouncementSyncStats,
            fetch_active_announcement_sources,
            get_or_create_announcement_source,
        )

        return {
            "AnnouncementCandidate": AnnouncementCandidate,
            "AnnouncementSourceRecord": AnnouncementSourceRecord,
            "AnnouncementSyncStats": AnnouncementSyncStats,
            "fetch_active_announcement_sources": fetch_active_announcement_sources,
            "get_or_create_announcement_source": get_or_create_announcement_source,
        }[name]

    if name in {
        "EventCandidate",
        "EventSourceRecord",
        "EventSyncStats",
        "fetch_active_event_sources",
        "get_or_create_event_source",
    }:
        from src.db.event_sources import (
            EventCandidate,
            EventSourceRecord,
            EventSyncStats,
            fetch_active_event_sources,
            get_or_create_event_source,
        )

        return {
            "EventCandidate": EventCandidate,
            "EventSourceRecord": EventSourceRecord,
            "EventSyncStats": EventSyncStats,
            "fetch_active_event_sources": fetch_active_event_sources,
            "get_or_create_event_source": get_or_create_event_source,
        }[name]

    if name == "fetch_relevant_events":
        from src.db.events import fetch_relevant_events

        return fetch_relevant_events

    if name in {
        "ConversationContextService",
        "ConversationResolution",
        "ConversationStateData",
        "ConversationTurnData",
    }:
        from src.db.conversation_context import (
            ConversationContextService,
            ConversationResolution,
            ConversationStateData,
            ConversationTurnData,
        )

        return {
            "ConversationContextService": ConversationContextService,
            "ConversationResolution": ConversationResolution,
            "ConversationStateData": ConversationStateData,
            "ConversationTurnData": ConversationTurnData,
        }[name]

    if name in {
        "ProfileContextData",
        "ProfileContextService",
        "extract_profile_from_text",
        "looks_like_profile_submission",
    }:
        from src.db.profile_context import (
            ProfileContextData,
            ProfileContextService,
            extract_profile_from_text,
            looks_like_profile_submission,
        )

        return {
            "ProfileContextData": ProfileContextData,
            "ProfileContextService": ProfileContextService,
            "extract_profile_from_text": extract_profile_from_text,
            "looks_like_profile_submission": looks_like_profile_submission,
        }[name]

    if name == "TelemetryService":
        from src.db.telemetry import TelemetryService

        return TelemetryService

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
