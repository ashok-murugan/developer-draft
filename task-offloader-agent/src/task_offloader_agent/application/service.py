"""Tool entry points shared by the MCP server and the CLI.

Every function accepts the runtime target: a ready `Env`, or a `ConfigFailure` when startup validation
failed. In that case the tools answer `disabled` with `config_error` and nothing runs (I7).
"""

from __future__ import annotations

from typing import Any

from ..core import audit
from ..core.errors import ConfigFailure
from ..core.result import disabled_result
from ..core.switch import TOOLS, decide, effective, read_switch
from ..tasks.ask import REVIEW as ASK_REVIEW
from ..tasks.ask import run_ask
from ..tasks.logs import REVIEW as LOGS_REVIEW
from ..tasks.logs import run_logs
from .runner import Env, Progress, no_progress, run_tool, try_audit

Target = Env | ConfigFailure


async def status(target: Target) -> dict[str, Any]:
    if isinstance(target, ConfigFailure):
        return {
            "status": "config_error",
            "for": "copilot-review",
            "diagnostic": target.message,
            "next_step": ("TaskOffloaderAgent is not configured correctly. Do every task yourself; do not call "
                          "its other tools. The developer can run `task-offloader profile check`."),
        }
    env = target
    settings = env.settings
    state = read_switch(settings)
    decision = decide(state, "local_status", requested_by_user=False)
    if not decision.allowed:
        try_audit(settings, {"event": "call", "tool": "local_status", "status": "disabled",
                             "reason": decision.reason})
        return disabled_result("local_status", decision.reason or "tool_flag")

    health = await env.provider.health()
    ready = health["reachable"] and health["model_present"]
    if state.mode == "off":
        next_step = "TaskOffloaderAgent is off. Do every task yourself; do not call its other tools."
    elif not ready:
        next_step = "Ollama or the model is not ready. Do every task yourself; do not call the other tools."
    elif state.mode == "manual":
        next_step = ("Manual mode: call a task-offloader tool only when the developer asks for local help "
                     "(#local), and pass requested_by_user: true.")
    else:
        next_step = "Delegate by the rules in copilot-instructions.md, only to tools whose state is `on`."
    tools = {name: effective(state, name) for name, spec in TOOLS.items() if spec.built}
    try_audit(settings, {"event": "call", "tool": "local_status", "status": "ok"})
    return {
        "status": "ok",
        "for": "copilot-review",
        "mode": state.mode,
        "switch": {"source": state.source, "error": state.error, "warnings": state.warnings},
        "tools": tools,
        "ollama": {"reachable": health["reachable"], "model": health["model"],
                   "model_present": health["model_present"]},
        "profile": env.profile.name,
        "num_ctx": settings.num_ctx,
        "timeout_s": settings.timeout_s,
        "tokenizer": env.counter.kind,
        "running": env.gate.running,
        "queued": env.gate.queued,
        "max_pending": env.gate.max_pending,
        "queue_length": env.gate.running + env.gate.queued,
        "next_step": next_step,
    }


async def ask(target: Target, instruction: str, paths: list[str] | None = None, text: str | None = None,
              max_words: int = 200, requested_by_user: bool = False,
              progress: Progress = no_progress) -> dict[str, Any]:
    if isinstance(target, ConfigFailure):
        return disabled_result("local_ask", "config_error", target.message)
    return await run_tool(
        target, "local_ask", requested_by_user, ASK_REVIEW,
        lambda ctx: run_ask(ctx, instruction, paths, text, max_words), progress)


async def summarize_logs(target: Target, files: list[str], since: str | None = None, until: str | None = None,
                         pattern: str | None = None, correlation_id: str | None = None, narrate: bool = True,
                         requested_by_user: bool = False, progress: Progress = no_progress) -> dict[str, Any]:
    if isinstance(target, ConfigFailure):
        return disabled_result("summarize_logs", "config_error", target.message)
    if not target.profile.log_dirs:
        return disabled_result("summarize_logs", "unavailable", "the profile defines no log folders")
    return await run_tool(
        target, "summarize_logs", requested_by_user, LOGS_REVIEW,
        lambda ctx: run_logs(ctx, files, since, until, pattern, correlation_id, narrate), progress)
