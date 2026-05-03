"""Standalone central retrieval/reranker service runner."""

from __future__ import annotations

import logging

import uvicorn

from src.api.retrieval_service import create_retrieval_service_app
from src.core.config import settings
from src.db.connection import init_engine


def main() -> None:
    logging.basicConfig(level=getattr(logging, settings.server.log_level.upper(), logging.INFO))
    init_engine()
    app = create_retrieval_service_app()
    uvicorn.run(
        app,
        host=settings.server.host,
        port=settings.server.port,
        log_level=settings.server.log_level.lower(),
    )


if __name__ == "__main__":
    main()
