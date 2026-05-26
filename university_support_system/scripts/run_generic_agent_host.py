"""Run one generic dynamic agent host."""

from __future__ import annotations

import os

import uvicorn

from src.dynamic_platform.agent_api import create_generic_agent_app


def main() -> None:
    tenant_key = os.getenv("TENANT_KEY", "acme_demo")
    agent_id = os.getenv("AGENT_ID", "")
    if not agent_id:
        raise SystemExit("AGENT_ID is required for generic dynamic agent host.")
    config_root = os.getenv("TENANT_CONFIG_ROOT", "configs/dynamic_platform")
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8090"))
    app = create_generic_agent_app(tenant_key=tenant_key, agent_id=agent_id, config_root=config_root)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
