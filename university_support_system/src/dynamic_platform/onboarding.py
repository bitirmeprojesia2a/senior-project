"""Offline tenant onboarding text preview.

This module does not wire Slack events. It only renders a tenant-specific
capability summary that can later feed Slack onboarding safely.
"""

from __future__ import annotations

from src.dynamic_platform.models import DynamicPlatformBundle


def build_onboarding_preview(bundle: DynamicPlatformBundle) -> str:
    tenant = bundle.tenant
    capabilities = {item.capability_id: item for item in bundle.domain_pack.capabilities}
    agents = bundle.agent_pack.agents
    source_count = len([source for source in bundle.source_catalog.sources if source.enabled])
    lines = [
        f"# {tenant.bot_name} Onboarding Preview",
        "",
        "Bu dosya offline onizlemedir; Slack'e otomatik mesaj gondermez.",
        "",
        f"Merhaba, ben {tenant.bot_name}. {tenant.display_name} icin hazirlanan destek profilindeki konularda yardimci olurum.",
        "",
        "## Aktif Yetenekler",
        "",
    ]
    for capability_id in sorted(capabilities):
        capability = capabilities[capability_id]
        owners = sorted(
            agent.display_name
            for agent in agents
            if capability_id in agent.capabilities
        )
        owner_text = ", ".join(owners) if owners else "Atanmamis"
        lines.append(f"- {capability.display_name}: {owner_text}")

    lines.extend(
        [
            "",
            "## Aktif Ajanlar",
            "",
        ]
    )
    for agent in agents:
        specialist_count = len(agent.specialists)
        capability_names = [
            capabilities.get(capability_id).display_name if capabilities.get(capability_id) else capability_id
            for capability_id in agent.capabilities
        ]
        lines.append(
            f"- {agent.display_name}: {', '.join(capability_names) or 'Yetenek yok'}"
            + (f" ({specialist_count} uzman)" if specialist_count else "")
        )

    entity_groups = tenant.entities.groups or {}
    non_empty_groups = {key: value for key, value in entity_groups.items() if value}
    lines.extend(["", "## Kurum Varliklari", ""])
    if not non_empty_groups:
        lines.append("- Bu tenant profilinde henuz entity kaydi yok.")
    else:
        for group, entities in sorted(non_empty_groups.items()):
            names = ", ".join(str(item.get("display_name") or item.get("id")) for item in entities[:8])
            suffix = "" if len(entities) <= 8 else f" (+{len(entities) - 8} daha)"
            lines.append(f"- {group}: {names}{suffix}")

    lines.extend(
        [
            "",
            "## Kaynak Durumu",
            "",
            f"- Enabled source count: {source_count}",
            f"- Runtime strategy: {tenant.runtime_strategy}",
            "",
            "## Guvenli Kullanim Notu",
            "",
            "- Bu onizleme runtime'a bagli degildir.",
            "- Hesap dogrulama, giris/cikis ve Slack mesaj davranisi ilgili tenant entegrasyonu baglaninca ayrica dogrulanmalidir.",
            "- Dynamic runtime aktif edilmeden once quality-gates, readiness ve replay gecmelidir.",
            "",
        ]
    )
    return "\n".join(lines)
