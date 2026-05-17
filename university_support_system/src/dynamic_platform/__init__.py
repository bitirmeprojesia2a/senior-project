"""Profile-driven dynamic institution platform primitives.

This package is intentionally additive. Nothing in the existing OMU runtime
imports it by default; tenant profiles can be validated and planned without
changing the classic production flow.
"""

from src.dynamic_platform.loader import DynamicPlatformPaths, load_tenant_bundle
from src.dynamic_platform.models import (
    AgentPack,
    DomainPack,
    DynamicPlatformBundle,
    SourceCatalog,
    TenantProfile,
)
from src.dynamic_platform.validator import ValidationReport, validate_bundle

__all__ = [
    "AgentPack",
    "DomainPack",
    "DynamicPlatformBundle",
    "DynamicPlatformPaths",
    "SourceCatalog",
    "TenantProfile",
    "ValidationReport",
    "load_tenant_bundle",
    "validate_bundle",
]
