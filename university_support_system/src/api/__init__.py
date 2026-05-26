"""API package.

Keep this module side-effect free. Importing submodules such as
``src.api.a2a_dispatch`` must not eagerly import the FastAPI app, otherwise
orchestrator and A2A helper imports can form circular dependencies.
"""

from __future__ import annotations

from typing import Any

__all__ = ["app", "create_app"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from src.api.main import app, create_app

        return {"app": app, "create_app": create_app}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
