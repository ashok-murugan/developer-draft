"""Inference provider contract. The service depends on this, never on a vendor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from ..core.errors import ServiceError


class ProviderError(ServiceError):
    code = "provider_error"


class ProviderUnavailable(ProviderError):
    code = "provider_unavailable"


class ProviderTimeout(ProviderError):
    code = "timeout"


class ProviderBadResponse(ProviderError):
    code = "provider_error"


class ProviderBusy(ProviderError):
    code = "busy"
    retryable = True


@dataclass(frozen=True)
class ChatRequest:
    system: str
    user: str
    num_predict: int
    num_ctx: int
    deadline: float  # time.monotonic() value


@dataclass
class ChatResult:
    text: str
    prompt_eval_count: int
    eval_count: int
    done_reason: str
    duration_ms: int
    queue_ms: int = 0


class InferenceProvider(Protocol):
    async def chat(self, request: ChatRequest) -> ChatResult: ...

    async def health(self) -> dict[str, Any]: ...
