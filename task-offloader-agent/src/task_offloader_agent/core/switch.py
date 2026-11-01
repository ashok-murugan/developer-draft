"""On/off switch: mode plus one flag per tool.

The switch file is read on every tool call, so changes apply to the next call.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from .config import Settings

MODES = ("auto", "manual", "off")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    default: bool
    built: bool


# Drafting tools are not built.
TOOLS: dict[str, ToolSpec] = {
    spec.name: spec
    for spec in (
        ToolSpec("local_status",          True,  True),
        ToolSpec("local_ask",             True,  True),
        ToolSpec("summarize_logs",        True,  True),
        ToolSpec("workspace_context",     True,  True),
        ToolSpec("local_report",          True,  True),
        ToolSpec("local_rate",            True,  True),
        ToolSpec("local_pending_ratings", True,  True),
        ToolSpec("draft_tests",           False, False),
        ToolSpec("draft_docs",            False, False),
        ToolSpec("draft_text",            False, False),
        ToolSpec("draft_fixture",         False, False),
    )
}


@dataclass
class SwitchState:
    mode: str
    flags: dict[str, bool]
    explicit: set[str] = field(default_factory=set)
    source: str = "default"  # file | env | default
    error: str | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str | None = None  # mode | tool_flag | manual


def _defaults() -> dict[str, bool]:
    return {name: spec.default for name, spec in TOOLS.items()}


def _env_mode(settings: Settings) -> tuple[str, str | None]:
    if settings.default_mode in MODES:
        return settings.default_mode, None
    return "off", f"TASK_OFFLOADER_MODE={settings.default_mode!r} is not one of {', '.join(MODES)}"


def read_switch(settings: Settings) -> SwitchState:
    path = settings.switch_file
    if not path.exists():
        mode, error = _env_mode(settings)
        return SwitchState(mode=mode, flags=_defaults(), source="env", error=error)

    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("top level is not a JSON object")
        tools = data.get("tools", {})
        if not isinstance(tools, dict):
            raise ValueError('"tools" is not a JSON object')
    except (OSError, ValueError) as exc:
        # Fail safe (section 6.4): an unreadable switch file counts as off.
        return SwitchState(mode="off", flags=_defaults(), source="file",
                           error=f"{path.name} cannot be parsed: {exc}")

    state = SwitchState(mode="auto", flags=_defaults(), source="file")
    mode = data.get("mode")
    if mode is None:
        state.mode, state.error = _env_mode(settings)
    elif isinstance(mode, str) and mode.strip().lower() in MODES:
        state.mode = mode.strip().lower()
    else:
        state.mode = "off"
        state.error = f'"mode" is {mode!r}; expected one of {", ".join(MODES)}'

    for name, value in tools.items():
        if name not in TOOLS:
            state.warnings.append(f"unknown tool {name!r} in {path.name} (ignored)")
            continue
        state.explicit.add(name)
        if isinstance(value, bool):
            state.flags[name] = value
        else:
            state.flags[name] = False
            state.warnings.append(f"tools.{name} is {value!r}, not true/false; treated as false")
    return state


def decide(state: SwitchState, tool: str, requested_by_user: bool) -> Decision:
    """Precedence from section 6.4 (hard stop and #nolocal are handled outside the server)."""
    if tool != "local_status" and state.mode == "off":
        return Decision(False, "mode")
    if not state.flags.get(tool, False):
        return Decision(False, "tool_flag")
    if tool != "local_status" and state.mode == "manual" and not requested_by_user:
        return Decision(False, "manual")
    return Decision(True)


def effective(state: SwitchState, tool: str) -> str:
    """Human-readable effective state, for `task-offloader tools` and local_status."""
    spec = TOOLS[tool]
    if not spec.built:
        return "not built"
    decision = decide(state, tool, requested_by_user=False)
    if decision.allowed:
        return "on"
    if decision.reason == "manual":
        return "on when requested (#local)"
    return "off (mode=off)" if decision.reason == "mode" else "off (flag)"


def tool_rows(state: SwitchState) -> list[dict[str, Any]]:
    return [
        {
            "tool": name,
            "flag": state.flags[name],
            "default": spec.default,
            "set_in_file": name in state.explicit,
            "built": spec.built,
            "effective": effective(state, name),
        }
        for name, spec in TOOLS.items()
    ]


# --- writing (used by the CLI) ------------------------------------------------

def _load_raw(settings: Settings) -> dict[str, Any]:
    try:
        data = json.loads(settings.switch_file.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_raw(settings: Settings, data: dict[str, Any]) -> None:
    settings.run_dir.mkdir(parents=True, exist_ok=True)
    tmp = settings.switch_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, settings.switch_file)


def _tools_section(data: dict[str, Any]) -> dict[str, Any]:
    tools = data.get("tools")
    if not isinstance(tools, dict):
        tools = {}
        data["tools"] = tools
    return tools


def set_mode(settings: Settings, mode: str) -> None:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {', '.join(MODES)}")
    data = _load_raw(settings)
    data["mode"] = mode
    _tools_section(data)
    _save_raw(settings, data)


def set_tool(settings: Settings, tool: str, value: bool) -> None:
    if tool not in TOOLS:
        raise ValueError(f"unknown tool {tool!r}; known tools: {', '.join(TOOLS)}")
    data = _load_raw(settings)
    data.setdefault("mode", settings.default_mode if settings.default_mode in MODES else "auto")
    _tools_section(data)[tool] = value
    _save_raw(settings, data)


def reset_tool(settings: Settings, tool: str) -> None:
    if tool not in TOOLS:
        raise ValueError(f"unknown tool {tool!r}; known tools: {', '.join(TOOLS)}")
    data = _load_raw(settings)
    _tools_section(data).pop(tool, None)
    _save_raw(settings, data)
