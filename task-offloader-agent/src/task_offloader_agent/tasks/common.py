"""Helpers shared by the task tools: prompts, model calls with one retry, word caps."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from ..application.runner import RunContext
from ..core.budget import input_limit
from ..providers.base import ChatRequest, ChatResult

CHAT_OVERHEAD = 64  # role markers of the chat template
RETRY_NOTE = "Your previous answer was cut at the output limit. Answer again, shorter: at most {words} words.\n"


def cap_words(text: str, max_words: int) -> tuple[str, bool]:
    """Cut `text` after `max_words` words, keeping its line breaks."""
    words = list(re.finditer(r"\S+", text))
    if len(words) <= max_words:
        return text.strip(), False
    return text[: words[max_words - 1].end()].rstrip() + f" ...[cut at {max_words} words]", True


@dataclass
class CallStats:
    """Summed over every model call in one run; written to the audit log."""

    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    prompt_eval_count: int = 0
    queue_ms: int = 0
    retries: int = 0
    done_reason: str = ""
    max_input_limit: int = 0
    warnings: list[str] = field(default_factory=list)

    def metrics(self, num_predict: int) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "input_limit": self.max_input_limit,
            "output_tokens": self.output_tokens,
            "num_predict": num_predict,
            "prompt_eval_count": self.prompt_eval_count,
            "done_reason": self.done_reason,
            "queue_ms": self.queue_ms,
            "retries": self.retries,
            "model_calls": self.calls,
        }


async def call_model(
    ctx: RunContext,
    stats: CallStats,
    system: str,
    build_user: Callable[[str], str],
    num_predict: int,
    retry_words: int,
) -> ChatResult:
    """One model call; on done_reason "length" retry once with a shorter-answer note.

    `build_user(retry_note)` renders the user prompt. Raises ProviderError (busy, timeout, unavailable, ...).
    The gate slot is held only while the model call runs, and released on error and on cancellation.
    """
    env = ctx.env
    limit = input_limit(env.settings.num_ctx, num_predict)
    stats.max_input_limit = max(stats.max_input_limit, limit)
    retry_note = ""
    for attempt in range(2):
        user = build_user(retry_note)
        tokens = env.counter.count(system) + env.counter.count(user)
        # Last guard; callers already keep the content under `limit`. Ollama would otherwise
        # silently drop the start of the prompt.
        if tokens + num_predict + CHAT_OVERHEAD > env.settings.num_ctx:
            raise ValueError(f"prompt is {tokens} tokens; with num_predict {num_predict} it does not fit "
                             f"num_ctx {env.settings.num_ctx}")
        async with env.gate.slot(ctx.deadline) as ticket:
            result = await env.provider.chat(ChatRequest(system, user, num_predict, env.settings.num_ctx,
                                                         ctx.deadline))
        result.queue_ms = ticket.queue_ms
        stats.calls += 1
        stats.input_tokens += tokens
        stats.output_tokens += result.eval_count
        stats.prompt_eval_count += result.prompt_eval_count
        stats.queue_ms += result.queue_ms
        stats.done_reason = result.done_reason
        if result.done_reason != "length" or attempt == 1:
            if result.done_reason == "length":
                stats.warnings.append("the answer reached the output limit twice and may be cut")
            return result
        stats.retries += 1
        retry_note = RETRY_NOTE.format(words=retry_words)
    raise AssertionError("unreachable")
