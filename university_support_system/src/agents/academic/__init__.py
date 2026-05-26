"""Academic agent exports.

Avoid eager agent imports so utility modules can be imported without
initializing the full agent graph during startup.
"""

from __future__ import annotations

from importlib import import_module

__all__ = ["CurriculumAgent", "RegulationAgent", "InternationalAgent"]

_EXPORT_MAP = {
    "CurriculumAgent": ("src.agents.academic.curriculum_agent", "CurriculumAgent"),
    "RegulationAgent": ("src.agents.academic.regulation_agent", "RegulationAgent"),
    "InternationalAgent": ("src.agents.academic.international_agent", "InternationalAgent"),
}


def __getattr__(name: str):
    try:
        module_name, attr_name = _EXPORT_MAP[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)
