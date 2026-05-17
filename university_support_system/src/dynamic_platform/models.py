"""Typed schemas for dynamic institution profiles.

The schemas describe a tenant-specific support architecture without mutating
the existing OMU classic runtime. They are deliberately generic: university
concepts belong to the education domain pack, not to this core module.
"""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)?$")

SourceAdapter = Literal[
    "pdf_document",
    "docx_document",
    "web_page",
    "announcement_page",
    "calendar_pdf",
    "structured_csv",
    "sql_table",
    "api_endpoint",
    "slack_uploaded_file",
    "ocr_document",
]

AuthorityLevel = Literal[
    "official_policy",
    "official_structured",
    "official_announcement",
    "department_document",
    "uploaded_user_context",
    "external_reference",
]

RuntimeStrategy = Literal["classic_protected", "dynamic_shadow", "dynamic_pilot", "dynamic_on"]


class DynamicBaseModel(BaseModel):
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
    }


def _validate_id(value: str, field_name: str) -> str:
    if not _ID_RE.match(value):
        raise ValueError(f"{field_name} must be lowercase snake_case or dotted capability id: {value!r}")
    return value


class CapabilityDefinition(DynamicBaseModel):
    capability_id: str
    display_name: str
    description: str = ""
    core_capability: str | None = None
    answer_mode: Literal["rag", "structured", "hybrid", "uploaded_context"] = "rag"

    @field_validator("capability_id", "core_capability")
    @classmethod
    def _ids(cls, value: str | None, info) -> str | None:
        if value is None:
            return value
        return _validate_id(value, info.field_name)


class DomainPack(DynamicBaseModel):
    schema_version: int = 1
    domain_pack: str
    display_name: str
    description: str = ""
    capabilities: list[CapabilityDefinition] = Field(default_factory=list)

    @field_validator("domain_pack")
    @classmethod
    def _domain_id(cls, value: str) -> str:
        return _validate_id(value, "domain_pack")


class SpecialistDefinition(DynamicBaseModel):
    specialist_id: str
    display_name: str
    capabilities: list[str] = Field(default_factory=list)
    llm_allowed: bool = True
    deterministic_allowed: bool = True

    @field_validator("specialist_id")
    @classmethod
    def _specialist_id(cls, value: str) -> str:
        return _validate_id(value, "specialist_id")

    @field_validator("capabilities")
    @classmethod
    def _capability_ids(cls, value: list[str]) -> list[str]:
        return [_validate_id(item, "capability") for item in value]


class AgentDefinition(DynamicBaseModel):
    agent_id: str
    display_name: str
    role: Literal["department_agent", "specialist_agent", "capability_agent", "service_agent"] = "department_agent"
    capabilities: list[str] = Field(default_factory=list)
    specialists: list[SpecialistDefinition] = Field(default_factory=list)
    source_families: list[str] = Field(default_factory=list)
    final_owner_for: list[str] = Field(default_factory=list)
    llm_allowed: bool = True
    deterministic_allowed: bool = True

    @field_validator("agent_id")
    @classmethod
    def _agent_id(cls, value: str) -> str:
        return _validate_id(value, "agent_id")

    @field_validator("capabilities")
    @classmethod
    def _capability_ids(cls, value: list[str]) -> list[str]:
        return [_validate_id(item, "capability") for item in value]

    @model_validator(mode="after")
    def _unique_specialists(self) -> "AgentDefinition":
        seen: set[str] = set()
        duplicates: set[str] = set()
        for specialist in self.specialists:
            if specialist.specialist_id in seen:
                duplicates.add(specialist.specialist_id)
            seen.add(specialist.specialist_id)
        if duplicates:
            raise ValueError(f"duplicate specialists in agent {self.agent_id}: {sorted(duplicates)}")
        return self


class AgentPack(DynamicBaseModel):
    schema_version: int = 1
    agent_pack: str
    display_name: str
    domain_pack: str
    agents: list[AgentDefinition] = Field(default_factory=list)

    @field_validator("agent_pack", "domain_pack")
    @classmethod
    def _ids(cls, value: str, info) -> str:
        return _validate_id(value, info.field_name)

    @model_validator(mode="after")
    def _unique_agents(self) -> "AgentPack":
        seen: set[str] = set()
        duplicates: set[str] = set()
        for agent in self.agents:
            if agent.agent_id in seen:
                duplicates.add(agent.agent_id)
            seen.add(agent.agent_id)
        if duplicates:
            raise ValueError(f"duplicate agents in pack {self.agent_pack}: {sorted(duplicates)}")
        return self


class EntityRegistry(DynamicBaseModel):
    """Flexible tenant entity registry.

    Different tenants may use departments, programs, teams, products, units,
    districts, or services. Core does not require any one of them.
    """

    groups: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)


class TenantProfile(DynamicBaseModel):
    schema_version: int = 1
    tenant_key: str
    display_name: str
    bot_name: str
    locale: str = "tr-TR"
    timezone: str = "Europe/Istanbul"
    runtime_strategy: RuntimeStrategy = "classic_protected"
    domain_pack: str
    agent_pack: str
    source_catalog: str
    replay_suite: str | None = None
    entities: EntityRegistry = Field(default_factory=EntityRegistry)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tenant_key", "domain_pack", "agent_pack", "source_catalog")
    @classmethod
    def _ids(cls, value: str, info) -> str:
        return _validate_id(value, info.field_name)


class EntityScope(DynamicBaseModel):
    type: Literal["global", "entity", "tenant", "uploaded_user_context"] = "global"
    entity_group: str | None = None
    entity_ids: list[str] = Field(default_factory=list)


class SourceCatalogEntry(DynamicBaseModel):
    source_id: str
    adapter: SourceAdapter
    domain: str
    owner_agent: str
    source_family: str
    capabilities: list[str] = Field(default_factory=list)
    entity_scope: EntityScope = Field(default_factory=EntityScope)
    authority_level: AuthorityLevel
    path: str | None = None
    url: str | None = None
    collection: str | None = None
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_id", "domain", "owner_agent")
    @classmethod
    def _ids(cls, value: str, info) -> str:
        return _validate_id(value, info.field_name)

    @field_validator("capabilities")
    @classmethod
    def _capability_ids(cls, value: list[str]) -> list[str]:
        return [_validate_id(item, "capability") for item in value]


class SourceCatalog(DynamicBaseModel):
    schema_version: int = 1
    source_catalog: str
    tenant_key: str
    sources: list[SourceCatalogEntry] = Field(default_factory=list)

    @field_validator("source_catalog", "tenant_key")
    @classmethod
    def _ids(cls, value: str, info) -> str:
        return _validate_id(value, info.field_name)

    @model_validator(mode="after")
    def _unique_sources(self) -> "SourceCatalog":
        seen: set[str] = set()
        duplicates: set[str] = set()
        for source in self.sources:
            if source.source_id in seen:
                duplicates.add(source.source_id)
            seen.add(source.source_id)
        if duplicates:
            raise ValueError(f"duplicate sources in catalog {self.source_catalog}: {sorted(duplicates)}")
        return self


class DynamicPlatformBundle(DynamicBaseModel):
    tenant: TenantProfile
    domain_pack: DomainPack
    agent_pack: AgentPack
    source_catalog: SourceCatalog

    def capability_ids(self) -> set[str]:
        return {capability.capability_id for capability in self.domain_pack.capabilities}

    def agent_ids(self) -> set[str]:
        return {agent.agent_id for agent in self.agent_pack.agents}
