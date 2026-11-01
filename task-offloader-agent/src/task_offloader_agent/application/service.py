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


# ---------------------------------------------------------------------------
# workspace_context
# ---------------------------------------------------------------------------

async def workspace_context(target: Target) -> dict[str, Any]:
    """Return a structured snapshot of workspace config for the cloud model to consume at session start."""
    if isinstance(target, ConfigFailure):
        return disabled_result("workspace_context", "config_error", target.message)
    env = target
    settings = env.settings
    state = read_switch(settings)
    decision = decide(state, "workspace_context", requested_by_user=False)
    if not decision.allowed:
        try_audit(settings, {"event": "call", "tool": "workspace_context",
                             "status": "disabled", "reason": decision.reason})
        return disabled_result("workspace_context", decision.reason or "tool_flag")

    tools = {name: effective(state, name) for name, spec in TOOLS.items()}
    deny_paths = [r.raw for r in env.profile.deny_paths]
    deny_names = list(env.profile.deny_names)
    log_dirs = [r.raw.removeprefix("**/") + "/" for r in env.profile.log_dirs]

    chunk_tokens = settings.chunk_tokens
    max_chunks = settings.max_chunks
    # Rough guidance: how many chars fit comfortably in one local_ask call
    approx_char_limit = chunk_tokens * 3 * max_chunks

    next_step = (
        f"Workspace ready. Use local_ask for files up to ~{approx_char_limit:,} chars. "
        + (f"Use summarize_logs for files in: {', '.join(log_dirs)}. " if log_dirs else "No log dirs configured. ")
        + ("Respect deny_paths and deny_names — do not pass those paths to any local tool." if deny_paths or deny_names else "")
    ).strip()

    try_audit(settings, {"event": "call", "tool": "workspace_context", "status": "ok"})
    return {
        "status": "ok",
        "for": "copilot-review",
        "profile": env.profile.name,
        "mode": state.mode,
        "tools": tools,
        "deny_paths": deny_paths,
        "deny_names": deny_names,
        "log_dirs": log_dirs,
        "model": settings.model,
        "num_ctx": settings.num_ctx,
        "chunk_tokens": chunk_tokens,
        "max_chunks": max_chunks,
        "approx_char_limit": approx_char_limit,
        "timeout_s": settings.timeout_s,
        "next_step": next_step,
    }


# ---------------------------------------------------------------------------
# local_report
# ---------------------------------------------------------------------------

async def local_report(target: Target) -> dict[str, Any]:
    """Return audit usage stats as structured JSON — no Ollama call."""
    if isinstance(target, ConfigFailure):
        return disabled_result("local_report", "config_error", target.message)
    env = target
    settings = env.settings
    state = read_switch(settings)
    decision = decide(state, "local_report", requested_by_user=False)
    if not decision.allowed:
        try_audit(settings, {"event": "call", "tool": "local_report",
                             "status": "disabled", "reason": decision.reason})
        return disabled_result("local_report", decision.reason or "tool_flag")

    from ..core import audit as _audit
    from collections import Counter, defaultdict
    events = _audit.read_all(settings)
    calls = [e for e in events if e.get("event") == "call" and e.get("tool") != "local_status"]
    ratings: dict[str, str] = {
        e.get("run_id", ""): e.get("rating", "")
        for e in events if e.get("event") == "rated"
    }

    by_tool: dict[str, dict[str, int]] = defaultdict(lambda: {"calls": 0, "ok": 0, "partial": 0,
                                                               "failed": 0, "refused": 0,
                                                               "disabled": 0, "good": 0, "bad": 0})
    total_chars = 0
    for e in calls:
        tool = e.get("tool", "?")
        by_tool[tool]["calls"] += 1
        st = e.get("status", "")
        if st in by_tool[tool]:
            by_tool[tool][st] += 1
        rating = ratings.get(e.get("run_id", ""))
        if rating in ("good", "bad"):
            by_tool[tool][rating] += 1
        if st in ("ok", "partial"):
            total_chars += e.get("input_chars", 0)

    _CHARS_PER_TOKEN = 3
    est_tokens = total_chars // _CHARS_PER_TOKEN

    unrated_ids = {
        e.get("run_id")
        for e in calls
        if e.get("status") in ("ok", "partial") and e.get("run_id") not in ratings
    }

    bad_rate_alert = [
        t for t, s in by_tool.items()
        if (n := s["good"] + s["bad"]) > 0 and s["bad"] * 2 > n
    ]

    period_start = calls[0].get("ts", "?") if calls else "?"
    period_end = calls[-1].get("ts", "?") if calls else "?"

    hints = []
    if unrated_ids:
        hints.append(f"{len(unrated_ids)} results unrated — call local_pending_ratings to review.")
    if bad_rate_alert:
        hints.append(f"High bad-rate tools: {', '.join(bad_rate_alert)} — consider `task-offloader off <tool>`.")
    next_step = " ".join(hints) if hints else "Usage looks healthy."

    try_audit(settings, {"event": "call", "tool": "local_report", "status": "ok"})
    return {
        "status": "ok",
        "for": "copilot-review",
        "period": f"{period_start} to {period_end}",
        "total_calls": len(calls),
        "by_tool": dict(by_tool),
        "estimated_chars_saved": total_chars,
        "estimated_tokens_saved": est_tokens,
        "unrated_count": len(unrated_ids),
        "bad_rate_alert": bad_rate_alert,
        "next_step": next_step,
    }


# ---------------------------------------------------------------------------
# local_rate
# ---------------------------------------------------------------------------

async def local_rate(target: Target, run_id: str, rating: str) -> dict[str, Any]:
    """Rate a task-offloader result good or bad — no Ollama call."""
    if isinstance(target, ConfigFailure):
        return disabled_result("local_rate", "config_error", target.message)
    env = target
    settings = env.settings
    state = read_switch(settings)
    decision = decide(state, "local_rate", requested_by_user=False)
    if not decision.allowed:
        try_audit(settings, {"event": "call", "tool": "local_rate",
                             "status": "disabled", "reason": decision.reason})
        return disabled_result("local_rate", decision.reason or "tool_flag")

    if rating not in ("good", "bad"):
        return {"status": "error", "for": "copilot-review",
                "error": f"rating must be 'good' or 'bad', got {rating!r}"}

    from ..core import audit as _audit
    events = _audit.read_all(settings)
    known = {e.get("run_id") for e in events if e.get("event") == "call"}
    if run_id not in known:
        return {"status": "error", "for": "copilot-review",
                "error": f"unknown run_id {run_id!r} — check local_pending_ratings for valid IDs"}

    _audit.write(settings, {"event": "rated", "run_id": run_id, "rating": rating})
    try_audit(settings, {"event": "call", "tool": "local_rate", "status": "ok",
                         "run_id": run_id, "rating": rating})
    return {"status": "ok", "for": "copilot-review", "run_id": run_id, "rating": rating}


# ---------------------------------------------------------------------------
# local_pending_ratings
# ---------------------------------------------------------------------------

async def local_pending_ratings(target: Target) -> dict[str, Any]:
    """Return unrated ok/partial results so the cloud model can prompt the developer to rate them."""
    if isinstance(target, ConfigFailure):
        return disabled_result("local_pending_ratings", "config_error", target.message)
    env = target
    settings = env.settings
    state = read_switch(settings)
    decision = decide(state, "local_pending_ratings", requested_by_user=False)
    if not decision.allowed:
        try_audit(settings, {"event": "call", "tool": "local_pending_ratings",
                             "status": "disabled", "reason": decision.reason})
        return disabled_result("local_pending_ratings", decision.reason or "tool_flag")

    from ..application import report as _report
    pending = _report.pending_ratings(settings)
    items = [
        {
            "run_id": e.get("run_id", "?"),
            "tool": e.get("tool", "?"),
            "ts": e.get("ts", "?"),
            "summary": e.get("summary", "(no summary)"),
        }
        for e in pending
    ]

    next_step = (
        f"Call local_rate with each run_id and 'good' or 'bad'. {len(items)} result(s) awaiting rating."
        if items else "All results are rated. Nothing to do."
    )

    try_audit(settings, {"event": "call", "tool": "local_pending_ratings", "status": "ok"})
    return {
        "status": "ok",
        "for": "copilot-review",
        "count": len(items),
        "pending": items,
        "next_step": next_step,
    }
