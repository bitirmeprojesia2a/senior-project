"""Standalone department agent service runner."""

from __future__ import annotations

import logging

import uvicorn

from src.api.agent_service import create_agent_service_app, resolve_agent_target
from src.core.config import settings
from src.db.connection import init_engine


def main() -> None:
    """Start a single A2A agent service."""
    logging.basicConfig(level=getattr(logging, settings.server.log_level.upper(), logging.INFO))
    target = resolve_agent_target()
    init_engine()
    app = create_agent_service_app(target=target)
    uvicorn.run(
        app,
        host=settings.server.host,
        port=settings.server.port,
        log_level=settings.server.log_level.lower(),
    )


if __name__ == "__main__":
    main()
