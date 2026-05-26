"""Offline compose launch template drafts for tenant packages.

The generated files are intentionally draft artifacts. They explain how a
future side-by-side tenant deployment could be isolated without editing the
current OMU compose files, but they must not be treated as a validated rollout
command.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from src.dynamic_platform.docker_plan import DEFAULT_COMPOSE_FILES
from src.dynamic_platform.models import DynamicPlatformBundle

DRAFT_OVERRIDE_NAME = "docker-compose.tenant.override.draft.yml"
LAUNCH_MANIFEST_NAME = "compose_launch_manifest.json"
COMPOSE_NOTES_NAME = "COMPOSE_NOTES.md"


class _ComposeOverrideList(list):
    """YAML list that replaces, rather than appends to, base compose lists."""


class _ComposeDraftDumper(yaml.SafeDumper):
    pass


def _represent_override_list(dumper: yaml.SafeDumper, data: _ComposeOverrideList):
    return dumper.represent_sequence("!override", list(data))


_ComposeDraftDumper.add_representer(_ComposeOverrideList, _represent_override_list)


@dataclass(frozen=True)
class ComposeLaunchTemplate:
    tenant_key: str
    safety_status: str
    package_dir: str
    base_compose_files: list[str]
    draft_override_file: str
    notes_file: str
    env_file: str
    compose_project_name: str
    container_prefix: str
    network_name: str
    volume_prefix: str
    generated_services: list[str] = field(default_factory=list)
    generated_volumes: list[str] = field(default_factory=list)
    generated_networks: list[str] = field(default_factory=list)
    service_profiles: dict[str, list[str]] = field(default_factory=dict)
    suggested_env_overrides: dict[str, str] = field(default_factory=dict)
    validation_commands: list[str] = field(default_factory=list)
    unresolved_risks: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "safety_status": self.safety_status,
            "package_dir": self.package_dir,
            "base_compose_files": self.base_compose_files,
            "draft_override_file": self.draft_override_file,
            "notes_file": self.notes_file,
            "env_file": self.env_file,
            "compose_project_name": self.compose_project_name,
            "container_prefix": self.container_prefix,
            "network_name": self.network_name,
            "volume_prefix": self.volume_prefix,
            "generated_services": self.generated_services,
            "generated_volumes": self.generated_volumes,
            "generated_networks": self.generated_networks,
            "service_profiles": self.service_profiles,
            "suggested_env_overrides": self.suggested_env_overrides,
            "validation_commands": self.validation_commands,
            "unresolved_risks": self.unresolved_risks,
            "notes": self.notes,
        }


def build_compose_launch_template_files(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    package_dir: str | Path,
    compose_files: Iterable[str | Path] = DEFAULT_COMPOSE_FILES,
) -> dict[str, str]:
    """Build draft compose artifacts without touching Docker or live files."""

    package_path = Path(package_dir)
    template, override_payload = build_compose_launch_template(
        bundle,
        config_root=config_root,
        package_dir=package_path,
        compose_files=compose_files,
    )
    return {
        LAUNCH_MANIFEST_NAME: json.dumps(template.to_dict(), ensure_ascii=False, indent=2) + "\n",
        DRAFT_OVERRIDE_NAME: yaml.dump(
            override_payload,
            Dumper=_ComposeDraftDumper,
            sort_keys=False,
            allow_unicode=True,
        ),
        COMPOSE_NOTES_NAME: _compose_notes(template),
    }


def build_compose_launch_template(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    package_dir: str | Path,
    compose_files: Iterable[str | Path] = DEFAULT_COMPOSE_FILES,
) -> tuple[ComposeLaunchTemplate, dict[str, Any]]:
    tenant = bundle.tenant
    package_path = Path(package_dir)
    tenant_env_path = (package_path / "tenant.env").as_posix()
    compose_paths = [Path(path) for path in compose_files]
    tenant_key = tenant.tenant_key
    env_prefix = tenant_key.upper()
    container_prefix = tenant_key
    compose_project_name = f"{tenant_key}_support"
    network_name = f"{tenant_key}_a2a_infra"
    volume_prefix = f"{tenant_key}_"
    port_offset = _tenant_port_offset(bundle)
    services: dict[str, Any] = {}
    volumes: dict[str, Any] = {}
    networks: dict[str, Any] = {}
    generated_services: list[str] = []
    service_profiles: dict[str, list[str]] = {}
    suggested_env_overrides: dict[str, str] = {
        "COMPOSE_PROJECT_NAME": compose_project_name,
        "A2A_IMAGE_REF": "university_support_system-app:latest",
        "MODEL_CACHE_HOST_DIR": "./data/models",
        f"{env_prefix}_A2A_INFRA_NETWORK": network_name,
    }

    for compose_path in compose_paths:
        if not compose_path.exists():
            continue
        payload = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
        for service_name, service in (payload.get("services") or {}).items():
            if not isinstance(service, dict):
                continue
            if tenant.runtime_strategy != "classic_protected" and _is_classic_runtime_service(str(service_name)):
                generated_services.append(str(service_name))
                services[str(service_name)] = _disabled_classic_service_override(
                    bundle,
                    service_name=str(service_name),
                    service=service,
                    tenant_env_path=tenant_env_path,
                    config_root=config_root,
                    container_prefix=container_prefix,
                )
                service_profiles[str(service_name)] = ["disabled-classic-runtime"]
                continue
            generated_services.append(str(service_name))
            service_override: dict[str, Any] = {
                "container_name": f"{container_prefix}_{_slug_service(service_name)}",
                "labels": {
                    "dynamic-platform.tenant": tenant_key,
                    "dynamic-platform.compose-template": "draft",
                },
                "environment": _tenant_environment_defaults(bundle, config_root=config_root),
            }
            if service.get("env_file") is not None:
                service_override["env_file"] = _ComposeOverrideList([tenant_env_path])
            rewritten_ports = _rewrite_ports_for_tenant(
                service_name,
                service.get("ports"),
                env_prefix,
                port_offset=port_offset,
            )
            if rewritten_ports:
                service_override["ports"] = _ComposeOverrideList([item["compose_port"] for item in rewritten_ports])
                for item in rewritten_ports:
                    suggested_env_overrides[item["env_var"]] = item["suggested_default"]
            profiles = _service_profiles(service_name)
            if profiles:
                service_override["profiles"] = profiles
                service_profiles[str(service_name)] = profiles
            if service_name == "api" and tenant.runtime_strategy != "classic_protected":
                service_override["image"] = "${A2A_IMAGE_REF:-university_support_system-app:latest}"
                service_override["command"] = [
                    "python",
                    "-m",
                    "scripts.run_dynamic_runtime",
                ]
                service_override["depends_on"] = _ComposeOverrideList(
                    [
                        "postgres",
                        "redis",
                        "chromadb",
                    ]
                )
            services[str(service_name)] = service_override

        for volume_name in (payload.get("volumes") or {}):
            volume_key = str(volume_name)
            volumes[volume_key] = {"name": f"{volume_prefix}{volume_key}"}

        for network_name_key, network in (payload.get("networks") or {}).items():
            network_key = str(network_name_key)
            if isinstance(network, dict) and network.get("external"):
                networks[network_key] = {
                    "external": True,
                    "name": f"${{{env_prefix}_{network_key.upper()}_NETWORK:-{network_name}}}",
                }

    if tenant.runtime_strategy != "classic_protected":
        for agent in bundle.agent_pack.agents:
            service_name = f"dynamic-agent-{agent.agent_id.replace('_', '-')}"
            generated_services.append(service_name)
            services[service_name] = _generic_agent_service_override(
                bundle,
                agent_id=agent.agent_id,
                tenant_env_path=tenant_env_path,
                config_root=config_root,
                container_prefix=container_prefix,
            )

    override_payload: dict[str, Any] = {
        "x-draft-warning": [
            "DRAFT ONLY - do not run this compose override before validation.",
            "Generated offline for tenant handoff; current OMU compose files were not modified.",
        ],
        "name": f"${{COMPOSE_PROJECT_NAME:-{compose_project_name}}}",
        "services": services,
    }
    if volumes:
        override_payload["volumes"] = volumes
    if networks:
        override_payload["networks"] = networks

    base_files = [str(path) for path in compose_paths]
    package_override = str(package_path / DRAFT_OVERRIDE_NAME)
    package_env = str(package_path / "tenant.env")
    validation_commands = [
        "# Validate only; do not start services:",
        (
            "$env:COMPOSE_DISABLE_ENV_FILE='1'; "
            "docker compose "
            f"--env-file {package_env} "
            + " ".join(f"-f {path}" for path in base_files)
            + f" -f {package_override} config --services"
        ),
    ]
    unresolved_risks = [
        "Compose merge semantics for env_file and ports must be validated with `docker compose config` before use.",
        "The draft uses Docker Compose `!override` tags for env_file and ports; validate with a Compose version that supports them.",
        "Dynamic pilot services are generated from the tenant agent pack, but live Slack binding still requires a separate approval gate.",
        "Port defaults are suggested placeholders; choose free host ports per machine before any live run.",
        "Slack app credentials and external callbacks still require separate tenant-specific configuration.",
        "Non-classic tenant drafts put classic agent/Slack services behind a disabled profile; a dynamic Slack adapter must be approved separately.",
        "Use the existing local image/model cache when possible; this draft does not require pull/build/model download.",
    ]
    notes = [
        "This artifact is offline and additive; it does not edit docker-compose.yml or .env.",
        "Service names are preserved so internal Docker DNS references can keep working inside one compose project.",
        "Container names, volume names, project name, and external network name are tenant-prefixed in the draft.",
    ]
    template = ComposeLaunchTemplate(
        tenant_key=tenant_key,
        safety_status="draft_do_not_run",
        package_dir=str(package_path),
        base_compose_files=base_files,
        draft_override_file=package_override,
        notes_file=str(package_path / COMPOSE_NOTES_NAME),
        env_file=package_env,
        compose_project_name=compose_project_name,
        container_prefix=container_prefix,
        network_name=network_name,
        volume_prefix=volume_prefix,
        generated_services=sorted(set(generated_services)),
        generated_volumes=sorted(volumes),
        generated_networks=sorted(networks),
        service_profiles={key: service_profiles[key] for key in sorted(service_profiles)},
        suggested_env_overrides=suggested_env_overrides,
        validation_commands=validation_commands,
        unresolved_risks=unresolved_risks,
        notes=notes,
    )
    return template, override_payload


def _is_classic_runtime_service(service_name: str) -> bool:
    """Return true for services that belong to the existing classic runtime."""

    return service_name.startswith("agent-") or service_name.startswith("slack-bot")


def _disabled_classic_service_override(
    bundle: DynamicPlatformBundle,
    *,
    service_name: str,
    service: dict[str, Any],
    tenant_env_path: str,
    config_root: str | Path,
    container_prefix: str,
) -> dict[str, Any]:
    service_override: dict[str, Any] = {
        "container_name": f"{container_prefix}_{_slug_service(service_name)}",
        "labels": {
            "dynamic-platform.tenant": bundle.tenant.tenant_key,
            "dynamic-platform.compose-template": "draft",
            "dynamic-platform.classic-service-disabled": "true",
        },
        "environment": _tenant_environment_defaults(bundle, config_root=config_root),
        "profiles": ["disabled-classic-runtime"],
        "ports": _ComposeOverrideList([]),
    }
    if service.get("env_file") is not None:
        service_override["env_file"] = _ComposeOverrideList([tenant_env_path])
    return service_override


def _tenant_environment_defaults(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
) -> dict[str, str]:
    tenant = bundle.tenant
    runtime_flag = "disabled" if tenant.runtime_strategy == "classic_protected" else "shadow"
    config_root_text = Path(config_root).as_posix()
    return {
        "TENANT_KEY": f"${{TENANT_KEY:-{tenant.tenant_key}}}",
        "TENANT_CONFIG_ROOT": f"${{TENANT_CONFIG_ROOT:-{config_root_text}}}",
        "TENANT_RUNTIME_STRATEGY": f"${{TENANT_RUNTIME_STRATEGY:-{tenant.runtime_strategy}}}",
        "TENANT_DOMAIN_PACK": f"${{TENANT_DOMAIN_PACK:-{tenant.domain_pack}}}",
        "TENANT_AGENT_PACK": f"${{TENANT_AGENT_PACK:-{tenant.agent_pack}}}",
        "TENANT_SOURCE_CATALOG": f"${{TENANT_SOURCE_CATALOG:-{tenant.source_catalog}}}",
        "DYNAMIC_PLATFORM_RUNTIME": f"${{DYNAMIC_PLATFORM_RUNTIME:-{runtime_flag}}}",
    }


def _generic_agent_service_override(
    bundle: DynamicPlatformBundle,
    *,
    agent_id: str,
    tenant_env_path: str,
    config_root: str | Path,
    container_prefix: str,
) -> dict[str, Any]:
    agent = next(agent for agent in bundle.agent_pack.agents if agent.agent_id == agent_id)
    return {
        "image": "${A2A_IMAGE_REF:-university_support_system-app:latest}",
        "container_name": f"{container_prefix}_agent_{_slug_service(agent_id)}",
        "labels": {
            "dynamic-platform.tenant": bundle.tenant.tenant_key,
            "dynamic-platform.agent": agent_id,
            "dynamic-platform.compose-template": "draft",
            "dynamic-platform.generic-agent-host": "true",
        },
        "env_file": _ComposeOverrideList([tenant_env_path]),
        "environment": {
            **_tenant_environment_defaults(bundle, config_root=config_root),
            "AGENT_ID": agent_id,
            "AGENT_DISPLAY_NAME": agent.display_name,
            "AGENT_CAPABILITIES": ",".join(agent.capabilities),
            "AGENT_SOURCE_FAMILIES": ",".join(agent.source_families),
            "SERVER_HOST": "0.0.0.0",
            "SERVER_PORT": "8090",
        },
        "command": [
            "python",
            "-m",
            "scripts.run_generic_agent_host",
        ],
        "profiles": ["tenant-dynamic-agents"],
    }


def _rewrite_ports_for_tenant(
    service_name: str,
    ports: Any,
    env_prefix: str,
    *,
    port_offset: int,
) -> list[dict[str, str]]:
    rewritten: list[dict[str, str]] = []
    for port in _as_list(ports):
        if not isinstance(port, str):
            continue
        if ":" not in port:
            continue
        host_part, container_part = port.rsplit(":", 1)
        env_var = _host_port_env_var(service_name, host_part, env_prefix)
        default_host = _host_port_default(host_part)
        suggested_default = str(int(default_host) + port_offset) if default_host and default_host.isdigit() else ""
        if not suggested_default:
            suggested_default = _fallback_port_default(service_name, container_part, port_offset=port_offset)
        rewritten.append(
            {
                "env_var": env_var,
                "suggested_default": suggested_default,
                "compose_port": f"${{{env_var}:-{suggested_default}}}:{container_part}",
            }
        )
    return rewritten


def _host_port_env_var(service_name: str, host_part: str, env_prefix: str) -> str:
    match = re.match(r"^\$\{(?P<name>[A-Za-z0-9_]+)", host_part)
    if match:
        original = match.group("name")
    else:
        original = f"{_slug_service(service_name).upper()}_PORT"
    return f"{env_prefix}_{original}"


def _host_port_default(host_part: str) -> str | None:
    match = re.match(r"^\$\{[A-Za-z0-9_]+:-(?P<default>[0-9]+)\}$", host_part)
    if match:
        return match.group("default")
    if host_part.isdigit():
        return host_part
    return None


def _fallback_port_default(service_name: str, container_part: str, *, port_offset: int) -> str:
    container_port = container_part.split("/", 1)[0]
    if container_port.isdigit():
        return str(int(container_port) + port_offset)
    service_hash = sum(ord(ch) for ch in service_name) % 1000
    return str(19000 + service_hash)


def _tenant_port_offset(bundle: DynamicPlatformBundle) -> int:
    configured = bundle.tenant.metadata.get("compose_port_offset")
    if isinstance(configured, int) and 1000 <= configured <= 50000:
        return configured
    if isinstance(configured, str) and configured.isdigit():
        value = int(configured)
        if 1000 <= value <= 50000:
            return value
    tenant_hash = sum(ord(ch) for ch in bundle.tenant.tenant_key)
    return 10000 + (tenant_hash % 20) * 1000


def _service_profiles(service_name: str) -> list[str]:
    if service_name == "slack-bot-a2a":
        return ["tenant-slack-a2a"]
    if service_name == "slack-bot-inprocess":
        return ["manual-inprocess-slack"]
    return []


def _slug_service(service_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", service_name).strip("_").lower()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _compose_notes(template: ComposeLaunchTemplate) -> str:
    env_lines = "\n".join(
        f"- `{key}={value}`" for key, value in sorted(template.suggested_env_overrides.items())
    )
    command_lines = "\n".join(template.validation_commands)
    risk_lines = "\n".join(f"- {risk}" for risk in template.unresolved_risks)
    note_lines = "\n".join(f"- {note}" for note in template.notes)
    profile_values = {item for profiles in template.service_profiles.values() for item in profiles}
    if profile_values == {"disabled-classic-runtime"}:
        slack_lines = (
            "- Classic Slack servisleri non-classic tenant taslaklarinda `disabled-classic-runtime` profiline baglidir.\n"
            "- Dynamic Slack adapter ayri bir onay ve replay fazi olmadan baglanmamalidir."
        )
    elif template.service_profiles:
        slack_lines = (
            "- `slack-bot-a2a` servisi `tenant-slack-a2a` profiline baglidir.\n"
            "- `slack-bot-inprocess` servisi `manual-inprocess-slack` profiline baglidir.\n"
            "- Gelecekte canli deneme onaylanirsa ayni anda yalniz bir Slack profili secilmelidir."
        )
    else:
        slack_lines = (
            "- Bu non-classic tenant taslagi classic Slack servislerini icermez.\n"
            "- Dynamic Slack adapter ayri bir onay ve replay fazi olmadan baglanmamalidir."
        )
    return (
        f"# {template.tenant_key} Compose Launch Draft\n\n"
        "Bu dosya yalniz offline taslak dokumandir. Docker build/pull yapmaz, servis baslatmaz.\n"
        "Mevcut OMU compose dosyalari degistirilmedi.\n\n"
        "## Guvenlik Durumu\n\n"
        f"- Safety status: `{template.safety_status}`\n"
        "- Bu override dosyasini dogrudan calistirmayin; once config validasyonu ve replay gerekir.\n\n"
        "## Uretilen Dosyalar\n\n"
        f"- Manifest: `{LAUNCH_MANIFEST_NAME}`\n"
        f"- Draft override: `{DRAFT_OVERRIDE_NAME}`\n"
        f"- Tenant env: `tenant.env`\n\n"
        "## Onerilen Env Override Degerleri\n\n"
        f"{env_lines or '- Yok'}\n\n"
        "## Sadece Validasyon Icin Komut Taslagi\n\n"
        "```powershell\n"
        f"{command_lines}\n"
        "```\n\n"
        "## Cozulmeden Calistirilmamasi Gereken Riskler\n\n"
        f"{risk_lines}\n\n"
        "## Slack Profil Guvenligi\n\n"
        f"{slack_lines}\n\n"
        "## Cache ve Internet Kullanimi\n\n"
        "- `A2A_IMAGE_REF` varsayilan olarak mevcut `university_support_system-app:latest` image'ini isaret eder.\n"
        "- `MODEL_CACHE_HOST_DIR` varsayilan olarak `./data/models` kullanir; model cache paylasimi internet kullanimini azaltir.\n"
        "- Bu taslak Docker build/pull veya model indirme komutu icermez.\n\n"
        "## Compose Merge Notu\n\n"
        "- Draft override `env_file` ve `ports` icin `!override` kullanir; bu, base `.env` ve default portlarin yan yana tenant config'ine sizmamasini hedefler.\n"
        "- Validasyon komutu `COMPOSE_DISABLE_ENV_FILE=1` ile root `.env` dosyasinin otomatik okunmasini kapatir.\n\n"
        "- Paylasim icin tam `docker compose config` ciktisini kullanmayin; gercek tenant secret'lari varsa resolved config icinde gorunebilir.\n\n"
        "## Notlar\n\n"
        f"{note_lines}\n"
    )
