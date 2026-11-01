"""Shared call path for every tool: switch check, deadline, error mapping, audit."""

from __future__ import annotations

import asyncio
import json
import sys
import time
import traceback
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core import audit
from ..core.budget import TokenCounter
from ..core.config import Settings
from ..core.paths import PathGuard
from ..core.profile import Profile
from ..core.redact import Redactor
from ..core.result import disabled_result, failed_result
from ..core.switch import decide, read_switch
from ..prompts import PromptSet
from ..providers.base import InferenceProvider
from .gate import Gate

# progress(done, total, message); a no-op when the client sent no progress token.
Progress = Callable[[float, float, str], Awaitable[None]]


async def no_progress(done: float, total: float, message: str) -> None:
    return None


@dataclass
class Env:
    settings: Settings
    profile: Profile
    guard: PathGuard
    provider: InferenceProvider
    gate: Gate
    counter: TokenCounter
    prompts: PromptSet
    redactor: Redactor


@dataclass
class Outcome:
    result: dict[str, Any]
    metrics: dict[str, Any] = field(default_factory=dict)  # audit fields; sizes and counts only


@dataclass
class RunContext:
    env: Env
    run_id: str
    deadline: float  # time.monotonic() value
    progress: Progress

    @property
    def run_dir(self) -> Path:
        return self.env.settings.out_dir / self.run_id


_issued: set[str] = set()


def new_run_id(settings: Settings, tool: str) -> str:
    base = f"{datetime.now():%Y%m%d-%H%M%S}-{tool}"
    run_id, n = base, 1
    while run_id in _issued or (settings.out_dir / run_id).exists():
        n += 1
        run_id = f"{base}-{n}"
    _issued.add(run_id)
    return run_id


def try_audit(settings: Settings, event: dict[str, Any]) -> str | None:
    """Write an audit event. A failure is reported as a warning text, never raised: read-only tools
    must keep working when the audit file is unwritable."""
    try:
        audit.write(settings, event)
        return None
    except OSError as exc:
        message = f"audit: write failed ({exc.__class__.__name__})"
        audit.log(settings, message)
        return message


async def run_tool(
    env: Env,
    tool: str,
    requested_by_user: bool,
    review: str,
    task: Callable[[RunContext], Awaitable[Outcome]],
    progress: Progress = no_progress,
) -> dict[str, Any]:
    settings = env.settings
    state = read_switch(settings)
    decision = decide(state, tool, requested_by_user)
    if not decision.allowed:
        try_audit(settings, {"event": "call", "tool": tool, "status": "disabled", "reason": decision.reason})
        return disabled_result(tool, decision.reason or "mode")

    run_id = new_run_id(settings, tool)
    audit.log(settings, f"START {tool} run_id={run_id} requested_by_user={requested_by_user}")
    started = time.monotonic()
    ctx = RunContext(env=env, run_id=run_id, deadline=started + settings.timeout_s, progress=progress)
    base = {"event": "call", "run_id": run_id, "tool": tool, "model": settings.model, "num_ctx": settings.num_ctx}

    def elapsed_ms() -> int:
        return int((time.monotonic() - started) * 1000)

    try:
        outcome = await task(ctx)
    except asyncio.CancelledError:
        try_audit(settings, {**base, "status": "cancelled", "duration_ms": elapsed_ms()})
        raise
    except Exception as exc:  # noqa: BLE001 - every failure becomes a `failed` result (rule R5)
        code, retryable = _classify(exc)
        if code == "internal":
            traceback.print_exc(file=sys.stderr)
            reason = f"internal error ({exc.__class__.__name__}: {exc})"
        else:
            reason = str(exc)
        outcome = Outcome(failed_result(run_id, env.redactor.redact_text(reason), review,
                                        code=code, retryable=retryable))

    result = outcome.result
    problem = try_audit(settings, {
        **base,
        "status": result.get("status"),
        "duration_ms": elapsed_ms(),
        "result_chars": len(json.dumps(result, ensure_ascii=False)),
        **outcome.metrics,
    })
    if problem:
        result.setdefault("warnings", []).append(problem)
    return result


def _classify(exc: Exception) -> tuple[str, bool]:
    code = getattr(exc, "code", None)
    if isinstance(code, str) and hasattr(exc, "retryable"):
        return code, bool(exc.retryable)
    if isinstance(exc, OSError):
        return "storage", False
    return "internal", False
