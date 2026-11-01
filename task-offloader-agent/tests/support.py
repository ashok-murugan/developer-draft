"""Shared test doubles."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from task_offloader_agent.providers.base import ChatRequest, ChatResult


class FakeProvider:
    """Replays scripted replies. A reply may be text, (text, done_reason) or an exception to raise.

    `hold` (an asyncio.Event) makes every call wait until it is set, to test queueing and cancellation.
    """

    def __init__(self, replies: Callable[[str], Any] | list[Any], hold: asyncio.Event | None = None):
        self.replies = replies if callable(replies) else list(replies)
        self.prompts: list[str] = []
        self.requests: list[ChatRequest] = []
        self.hold = hold
        self.started = 0
        self.finished = 0
        self.cancelled = 0

    async def chat(self, request: ChatRequest) -> ChatResult:
        self.requests.append(request)
        self.prompts.append(request.user)
        self.started += 1
        try:
            if self.hold is not None:
                await self.hold.wait()
            reply = self.replies(request.user) if callable(self.replies) else self.replies.pop(0)
            if isinstance(reply, Exception):
                raise reply
            text, reason = reply if isinstance(reply, tuple) else (reply, "stop")
            self.finished += 1
            return ChatResult(text, 100, 20, reason, 10, 0)
        except asyncio.CancelledError:
            self.cancelled += 1
            raise

    async def health(self) -> dict[str, Any]:
        return {"reachable": True, "model": "my-coder", "model_present": True}
