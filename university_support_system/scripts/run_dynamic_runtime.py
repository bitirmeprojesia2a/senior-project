"""Run an isolated dynamic tenant API."""

from __future__ import annotations

import os

import uvicorn

from src.dynamic_platform.api import create_dynamic_app


def main() -> None:
    tenant_key = os.getenv("TENANT_KEY", "acme_demo")
    config_root = os.getenv("TENANT_CONFIG_ROOT", "configs/dynamic_platform")
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    app = create_dynamic_app(tenant_key=tenant_key, config_root=config_root)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
