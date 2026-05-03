"""AgentCard builders for published A2A services."""

from __future__ import annotations

from typing import Any

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentProvider,
    AgentSkill,
)

from src.a2a.agent_card_security import a2a_hmac_security_requirement, a2a_hmac_security_schemes
from src.a2a.schemas import AGENT_RESPONSE_SCHEMA, DEPARTMENT_RESPONSE_SCHEMA
from src.a2a.targets import AgentServiceTarget, SpecialistTarget, agent_target_kind
from src.core.config import settings
from src.core.constants import Capability, Department


def _unique_service_agents(service_handler: Any) -> list[Any]:
    if hasattr(service_handler, "definition") and hasattr(service_handler, "agent_id"):
        return [service_handler]

    unique = {}
    for agent in [
        *getattr(service_handler, "agents", {}).values(),
        getattr(service_handler, "fallback_agent", None),
        *getattr(service_handler, "agents_by_id", {}).values(),
    ]:
        if agent is not None:
            unique[getattr(agent, "agent_id", id(agent))] = agent
    return list(unique.values())


def _target_agent_name(target_display_name: str) -> str:
    suffix = "" if target_display_name.casefold().endswith("agent") else " Agent"
    return f"OMU {target_display_name}{suffix}"


def build_agent_card_payload(
    *,
    target: AgentServiceTarget,
    service_handler: Any,
) -> dict[str, Any]:
    """Build a lightweight service card for discovery and smoke tests."""
    agents = _unique_service_agents(service_handler)
    target_value = target.value
    target_display_name = target.display_name
    target_kind = agent_target_kind(target)
    payload = {
        "service_id": settings.agent.service_id,
        "name": f"{_target_agent_name(target_display_name)} Service",
        "url": settings.agent.public_url.rstrip("/"),
        "version": settings.server.app_version,
        "build": settings.server.build_metadata(),
        "capabilities": {
            "a2a_dispatch": True,
            "a2a_jsonrpc": True,
            "a2a_transport_protocol": settings.a2a.transport_protocol,
            "agent_response_schema": AGENT_RESPONSE_SCHEMA,
            "department_response_schema": DEPARTMENT_RESPONSE_SCHEMA,
            "service_build": settings.server.build_metadata(),
            "service_runtime_label": settings.server.runtime_label,
            "service_target_kind": target_kind,
            "service_target": target_value,
            "agent_card_path": "/.well-known/agent.json",
            "jsonrpc_path": "/a2a",
        },
        "agents": [
            {
                "agent_id": agent.agent_id,
                "name": agent.definition.name,
                "description": agent.definition.description,
                "task_types": [task_type.value for task_type in agent.definition.task_types],
            }
            for agent in agents
        ],
    }
    if isinstance(target, Department):
        payload["department"] = target_value
    elif isinstance(target, Capability):
        payload["capability"] = target_value
    else:
        payload["department"] = target.department.value
        payload["specialist_id"] = target.agent_id
    return payload


def build_standard_agent_card(
    *,
    target: AgentServiceTarget,
    service_handler: Any,
) -> AgentCard:
    """Build a protocol-shaped A2A AgentCard for external discovery."""
    target_value = target.value
    target_display_name = target.display_name
    target_kind = agent_target_kind(target)
    skills = []
    for agent in _unique_service_agents(service_handler):
        task_types = [task_type.value for task_type in agent.definition.task_types]
        skills.append(
            AgentSkill(
                id=agent.agent_id,
                name=agent.definition.name,
                description=agent.definition.description,
                tags=[target_kind, target_value, *task_types],
                inputModes=["text/plain", "application/json"],
                outputModes=["text/plain", "application/json"],
            )
        )
    if not skills:
        skills.append(
            AgentSkill(
                id=target_value,
                name=f"{target_display_name} Dispatch",
                description=f"{target_display_name} agent dispatch capability.",
                tags=[target_kind, target_value],
                inputModes=["text/plain", "application/json"],
                outputModes=["text/plain", "application/json"],
            )
        )
    return AgentCard(
        name=_target_agent_name(target_display_name),
        description=f"{target_display_name} icin A2A uyumlu agent servisi.",
        url=f"{settings.agent.public_url.rstrip('/')}/a2a",
        version=settings.server.app_version,
        provider=AgentProvider(
            organization="Ondokuz Mayis Universitesi",
            url="https://www.omu.edu.tr",
        ),
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,
            stateTransitionHistory=True,
        ),
        security=a2a_hmac_security_requirement(),
        securitySchemes=a2a_hmac_security_schemes(),
        defaultInputModes=["text/plain", "application/json"],
        defaultOutputModes=["text/plain", "application/json"],
        skills=skills,
    )


__all__ = [
    "build_agent_card_payload",
    "build_standard_agent_card",
]
