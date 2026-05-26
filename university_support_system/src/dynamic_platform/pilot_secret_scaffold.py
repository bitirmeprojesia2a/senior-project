"""Create blank, gitignored pilot secret env scaffolds.

The scaffold is intentionally value-free. It helps operators prepare the file
that `secret-readiness` and `pilot-readiness` should read for pilot/live modes
without copying production `.env` or generated tenant package values.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.secrets_contract import build_tenant_secrets_contract


@dataclass(frozen=True)
class PilotSecretScaffoldResult:
    tenant_key: str
    output_dir: str
    env_path: str
    manifest_path: str
    readme_path: str
    include_slack: bool
    mode: str
    ok: bool
    checks: dict[str, bool]
    files: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "output_dir": self.output_dir,
            "env_path": self.env_path,
            "manifest_path": self.manifest_path,
            "readme_path": self.readme_path,
            "include_slack": self.include_slack,
            "mode": self.mode,
            "ok": self.ok,
            "checks": self.checks,
            "files": self.files,
            "notes": self.notes,
        }


def build_tenant_pilot_secret_scaffold_files(
    bundle: DynamicPlatformBundle,
    *,
    output_dir: str | Path = "tmp/dynamic_platform_runtime_secrets",
    mode: str = "dynamic_pilot",
    include_slack: bool = False,
) -> dict[str, str]:
    if mode != "dynamic_pilot":
        raise ValueError("Only dynamic_pilot scaffold mode is currently supported.")
    contract = build_tenant_secrets_contract(bundle)
    env_name = _env_filename(bundle.tenant.tenant_key, mode)
    manifest_name = _manifest_filename(bundle.tenant.tenant_key, mode)
    required_categories = {"llm_provider", "a2a_internal_auth"}
    if include_slack:
        required_categories.add("slack_socket_mode")

    env_lines = [
        f"# {bundle.tenant.display_name} dynamic pilot secret env scaffold",
        "# Fill this local file only after an explicit pilot/live approval.",
        "# Do not commit real values. Do not copy production .env into this file.",
        "# Keep this file outside tmp/tenant_packages/<tenant>.",
        "",
    ]
    for requirement in contract.requirements:
        required = requirement.category in required_categories
        marker = "required" if required else "optional"
        env_lines.append(f"# {marker}: {requirement.category} - {requirement.purpose}")
        env_lines.append(f"{requirement.key}=")
        env_lines.append("")

    manifest = {
        "tenant_key": bundle.tenant.tenant_key,
        "runtime_strategy": bundle.tenant.runtime_strategy,
        "mode": mode,
        "include_slack": include_slack,
        "env_file": str(Path(output_dir) / env_name),
        "secret_values_written": False,
        "required_categories": sorted(required_categories),
        "safe_readiness_commands": [
            (
                f"python -m scripts.tenant secret-readiness --tenant {bundle.tenant.tenant_key} "
                f"--mode dynamic_pilot --env-file {Path(output_dir) / env_name}"
                + (" --include-slack" if include_slack else "")
            ),
            (
                f"python -m scripts.tenant pilot-readiness --tenant {bundle.tenant.tenant_key} "
                f"--mode dynamic_pilot --package-root tmp\\tenant_packages "
                f"--secrets-env-file {Path(output_dir) / env_name}"
                + (" --include-slack" if include_slack else "")
                + " --allow-missing-shadow"
            ),
        ],
        "forbidden_actions": contract.forbidden_actions,
        "notes": [
            "This scaffold intentionally contains blank values only.",
            "A blank scaffold should fail dynamic_pilot readiness until real secrets are supplied outside git.",
            "Do not place pilot/live secret files under tmp/tenant_packages.",
        ],
    }
    readme = _readme(bundle, env_name=env_name, manifest_name=manifest_name, include_slack=include_slack)
    return {
        env_name: "\n".join(env_lines).rstrip() + "\n",
        manifest_name: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        "README.md": readme,
    }


def write_tenant_pilot_secret_scaffold(
    bundle: DynamicPlatformBundle,
    *,
    output_dir: str | Path = "tmp/dynamic_platform_runtime_secrets",
    mode: str = "dynamic_pilot",
    include_slack: bool = False,
    force: bool = False,
) -> PilotSecretScaffoldResult:
    target_dir = Path(output_dir)
    files = build_tenant_pilot_secret_scaffold_files(
        bundle,
        output_dir=target_dir,
        mode=mode,
        include_slack=include_slack,
    )
    existing = [target_dir / name for name in files if (target_dir / name).exists()]
    if existing and not force:
        names = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"Pilot secret scaffold files already exist. Use --force to overwrite: {names}")

    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, content in files.items():
        path = target_dir / name
        path.write_text(content, encoding="utf-8")
        written.append(str(path))

    env_path = target_dir / _env_filename(bundle.tenant.tenant_key, mode)
    manifest_path = target_dir / _manifest_filename(bundle.tenant.tenant_key, mode)
    readme_path = target_dir / "README.md"
    checks = {
        "output_outside_tenant_package": "tmp/tenant_packages" not in target_dir.as_posix().lower(),
        "output_under_tmp": target_dir.as_posix().lower().startswith("tmp/"),
        "secret_values_written": False,
        "env_file_exists": env_path.exists(),
        "manifest_exists": manifest_path.exists(),
    }
    ok = (
        checks["output_outside_tenant_package"]
        and checks["output_under_tmp"]
        and not checks["secret_values_written"]
        and checks["env_file_exists"]
        and checks["manifest_exists"]
    )
    return PilotSecretScaffoldResult(
        tenant_key=bundle.tenant.tenant_key,
        output_dir=str(target_dir),
        env_path=str(env_path),
        manifest_path=str(manifest_path),
        readme_path=str(readme_path),
        include_slack=include_slack,
        mode=mode,
        ok=ok,
        checks=checks,
        files=written,
        notes=[
            "Scaffold generation is offline and writes blank values only.",
            "Because this lives under tmp by default, it is covered by the repository gitignore.",
            "The blank file should fail dynamic_pilot readiness until real values are provided outside git.",
        ],
    )


def _env_filename(tenant_key: str, mode: str) -> str:
    return f"{tenant_key}.{mode}.secrets.env"


def _manifest_filename(tenant_key: str, mode: str) -> str:
    return f"{tenant_key}.{mode}.secrets_manifest.json"


def _readme(
    bundle: DynamicPlatformBundle,
    *,
    env_name: str,
    manifest_name: str,
    include_slack: bool,
) -> str:
    slack_flag = " --include-slack" if include_slack else ""
    return "\n".join(
        [
            f"# {bundle.display_name if hasattr(bundle, 'display_name') else bundle.tenant.display_name} Pilot Secret Scaffold",
            "",
            "This directory is a local, value-free scaffold for future dynamic pilot secret injection.",
            "",
            "Files:",
            f"- `{env_name}`: blank env keys to fill only after explicit approval.",
            f"- `{manifest_name}`: machine-readable safe commands and forbidden actions.",
            "",
            "Validation after filling real values locally:",
            "",
            "```powershell",
            (
                f".\\venv\\Scripts\\python.exe -m scripts.tenant secret-readiness "
                f"--tenant {bundle.tenant.tenant_key} --mode dynamic_pilot --env-file <this-dir>\\{env_name}{slack_flag}"
            ),
            (
                f".\\venv\\Scripts\\python.exe -m scripts.tenant pilot-readiness "
                f"--tenant {bundle.tenant.tenant_key} --mode dynamic_pilot --package-root tmp\\tenant_packages "
                f"--secrets-env-file <this-dir>\\{env_name}{slack_flag} --allow-missing-shadow"
            ),
            "```",
            "",
            "Safety:",
            "- Do not commit real values.",
            "- Do not copy production `.env` into this file.",
            "- Do not put this file under `tmp/tenant_packages/<tenant>`.",
            "- A blank scaffold is expected to fail dynamic pilot readiness.",
            "",
        ]
    )
