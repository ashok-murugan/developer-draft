"""Ollama provider: /api/chat on loopback. One call per request; queueing lives in the service gate."""

from __future__ import annotations

import time
from typing import Any

import httpx

from ..core.config import Settings
from .base import (ChatRequest, ChatResult, ProviderBadResponse, ProviderTimeout, ProviderUnavailable)

BASE_OPTIONS = {"temperature": 0.2, "top_p": 0.9, "repeat_penalty": 1.05}
HEALTH_TIMEOUT_S = 3.0
CONNECT_TIMEOUT_S = 5.0


class OllamaProvider:
    def __init__(self, settings: Settings):
        self.url = settings.provider_url
        self.model = settings.model
        self.keep_alive = settings.keep_alive

    async def chat(self, request: ChatRequest) -> ChatResult:
        """Run one chat call. `request.deadline` is a time.monotonic() value."""
        remaining = request.deadline - time.monotonic()
        if remaining < 1:
            raise ProviderTimeout("timed out before the model call started")
        body: dict[str, Any] = {
            "model": self.model,
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {**BASE_OPTIONS, "num_ctx": request.num_ctx, "num_predict": request.num_predict},
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.user},
            ],
        }
        started = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(remaining, connect=CONNECT_TIMEOUT_S)) as client:
                response = await client.post(f"{self.url}/api/chat", json=body)
        except httpx.TimeoutException:
            raise ProviderTimeout(f"model did not answer within {remaining:.0f} s") from None
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(f"Ollama not reachable at {self.url}: {exc.__class__.__name__}") from None
        if response.status_code != 200:
            raise ProviderBadResponse(f"Ollama returned HTTP {response.status_code}: {response.text[:200]}")
        try:
            data = response.json()
            message = data["message"]
            text = message["content"]
            if not isinstance(text, str):
                raise TypeError("content is not text")
            return ChatResult(
                text=text,
                prompt_eval_count=int(data.get("prompt_eval_count") or 0),
                eval_count=int(data.get("eval_count") or 0),
                done_reason=str(data.get("done_reason") or ""),
                duration_ms=int((time.monotonic() - started) * 1000),
            )
        except (ValueError, KeyError, TypeError, AttributeError):
            raise ProviderBadResponse("Ollama returned a response in an unexpected format") from None

    async def health(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=HEALTH_TIMEOUT_S) as client:
                response = await client.get(f"{self.url}/api/tags")
            names = [m.get("name", "") for m in response.json().get("models", [])]
        except (httpx.HTTPError, ValueError, AttributeError) as exc:
            return {"reachable": False, "error": exc.__class__.__name__, "model": self.model,
                    "model_present": False}
        present = self.model in names or f"{self.model}:latest" in names
        return {"reachable": True, "model": self.model, "model_present": present, "installed": names}
