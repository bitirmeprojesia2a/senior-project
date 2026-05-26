"""Load dynamic platform YAML profiles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from src.dynamic_platform.models import AgentPack, DomainPack, DynamicPlatformBundle, SourceCatalog, TenantProfile

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class DynamicPlatformPaths:
    root: Path

    @classmethod
    def from_root(cls, root: str | Path) -> "DynamicPlatformPaths":
        return cls(root=Path(root).resolve())

    @property
    def tenants_dir(self) -> Path:
        return self.root / "tenants"

    @property
    def domain_packs_dir(self) -> Path:
        return self.root / "domain_packs"

    @property
    def agent_packs_dir(self) -> Path:
        return self.root / "agent_packs"

    @property
    def source_catalogs_dir(self) -> Path:
        return self.root / "source_catalogs"

    def tenant_path(self, tenant_key: str) -> Path:
        return self.tenants_dir / f"{tenant_key}.yaml"

    def domain_pack_path(self, domain_pack: str) -> Path:
        return self.domain_packs_dir / f"{domain_pack}.yaml"

    def agent_pack_path(self, agent_pack: str) -> Path:
        return self.agent_packs_dir / f"{agent_pack}.yaml"

    def source_catalog_path(self, source_catalog: str) -> Path:
        return self.source_catalogs_dir / f"{source_catalog}.yaml"


class DynamicPlatformLoadError(RuntimeError):
    """Raised when a dynamic platform profile cannot be loaded."""


def load_yaml_model(path: Path, model_type: type[T]) -> T:
    if not path.exists():
        raise DynamicPlatformLoadError(f"Config file not found: {path}")
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise DynamicPlatformLoadError(f"YAML parse error in {path}: {exc}") from exc
    except OSError as exc:
        raise DynamicPlatformLoadError(f"Could not read {path}: {exc}") from exc

    try:
        return model_type.model_validate(payload)
    except ValidationError as exc:
        raise DynamicPlatformLoadError(f"Schema validation error in {path}: {exc}") from exc


def load_tenant_bundle(
    tenant_key: str,
    *,
    config_root: str | Path = "configs/dynamic_platform",
) -> DynamicPlatformBundle:
    paths = DynamicPlatformPaths.from_root(config_root)
    tenant = load_yaml_model(paths.tenant_path(tenant_key), TenantProfile)
    domain_pack = load_yaml_model(paths.domain_pack_path(tenant.domain_pack), DomainPack)
    agent_pack = load_yaml_model(paths.agent_pack_path(tenant.agent_pack), AgentPack)
    source_catalog = load_yaml_model(paths.source_catalog_path(tenant.source_catalog), SourceCatalog)
    return DynamicPlatformBundle(
        tenant=tenant,
        domain_pack=domain_pack,
        agent_pack=agent_pack,
        source_catalog=source_catalog,
    )
