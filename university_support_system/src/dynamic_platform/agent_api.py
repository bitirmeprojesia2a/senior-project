"""HTTP surface for one generic dynamic agent host."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.dynamic_platform.generic_agent_host import GenericAgentHost
from src.dynamic_platform.loader import DynamicPlatformLoadError, load_tenant_bundle


class GenericAgentQueryRequest(BaseModel):
    query: str
    selected_capabilities: list[str] = Field(default_factory=list)


def create_generic_agent_app(
    *,
    tenant_key: str,
    agent_id: str,
    config_root: str = "configs/dynamic_platform",
    project_root: str = ".",
) -> FastAPI:
    app = FastAPI(
        title=f"{tenant_key}/{agent_id} Generic Dynamic Agent",
        description="Profile-driven dynamic agent host.",
    )

    @lru_cache(maxsize=1)
    def host() -> GenericAgentHost:
        bundle = load_tenant_bundle(tenant_key, config_root=config_root)
        agents = {agent.agent_id: agent for agent in bundle.agent_pack.agents}
        agent = agents.get(agent_id)
        if agent is None:
            raise DynamicPlatformLoadError(f"Agent {agent_id!r} is not defined for tenant {tenant_key!r}.")
        return GenericAgentHost(bundle, agent, project_root=project_root)

    @app.get("/health")
    async def health() -> dict[str, Any]:
        try:
            active = host()
        except DynamicPlatformLoadError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return {
            "status": "healthy",
            "tenant_key": tenant_key,
            "agent_id": active.agent.agent_id,
            "capabilities": active.agent.capabilities,
            "source_families": active.agent.source_families,
        }

    @app.post("/agent/query")
    async def query(payload: GenericAgentQueryRequest) -> dict[str, Any]:
        return host().handle(
            query=payload.query,
            selected_capabilities=payload.selected_capabilities,
        ).to_dict()

    return app
