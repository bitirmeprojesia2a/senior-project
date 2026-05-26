"""FastAPI surface for the isolated dynamic pilot runtime."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.dynamic_platform.loader import DynamicPlatformLoadError
from src.dynamic_platform.runtime import DynamicRuntimeOrchestrator, DynamicRuntimeQuery


class DynamicQueryRequest(BaseModel):
    query: str
    conversation_id: str = "dynamic-api"
    user_id: str = "anonymous"
    requested_capabilities: list[str] = Field(default_factory=list)


def create_dynamic_app(
    *,
    tenant_key: str,
    config_root: str = "configs/dynamic_platform",
    project_root: str = ".",
) -> FastAPI:
    app = FastAPI(
        title=f"{tenant_key} Dynamic Support Runtime",
        description="Tenant-scoped dynamic support runtime. Does not use the protected classic router.",
    )

    @lru_cache(maxsize=1)
    def orchestrator() -> DynamicRuntimeOrchestrator:
        return DynamicRuntimeOrchestrator.from_tenant(
            tenant_key,
            config_root=config_root,
            project_root=project_root,
        )

    @app.get("/dynamic/health")
    async def dynamic_health() -> dict[str, Any]:
        try:
            return orchestrator().health()
        except DynamicPlatformLoadError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/dynamic/topology")
    async def dynamic_topology() -> dict[str, Any]:
        try:
            return orchestrator().topology()
        except DynamicPlatformLoadError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/dynamic/agents")
    async def dynamic_agents() -> list[dict[str, Any]]:
        return list(orchestrator().topology()["agents"])

    @app.get("/dynamic/capabilities")
    async def dynamic_capabilities() -> list[dict[str, Any]]:
        return list(orchestrator().topology()["capabilities"])

    @app.post("/dynamic/query")
    async def dynamic_query(payload: DynamicQueryRequest) -> dict[str, Any]:
        answer = orchestrator().answer(
            DynamicRuntimeQuery(
                tenant_key=tenant_key,
                query=payload.query,
                conversation_id=payload.conversation_id,
                user_id=payload.user_id,
                requested_capabilities=payload.requested_capabilities,
            )
        )
        return answer.to_dict()

    return app


app = create_dynamic_app(tenant_key="acme_demo")
