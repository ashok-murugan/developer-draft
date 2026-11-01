"""Error types shared by all layers. Each carries a stable `code` for the `error` field of a result."""

from __future__ import annotations

from dataclasses import dataclass


class ServiceError(Exception):
    """A failure the service understands. `code` and `retryable` reach the primary agent."""

    code = "internal"
    retryable = False

    def __init__(self, message: str, *, code: str | None = None, retryable: bool | None = None):
        super().__init__(message)
        if code is not None:
            self.code = code
        if retryable is not None:
            self.retryable = retryable

    @property
    def error(self) -> dict[str, object]:
        return {"code": self.code, "retryable": self.retryable}


class StorageError(ServiceError):
    code = "storage"


class ConfigError(Exception):
    """Invalid profile or runtime configuration. No task runs (invariant I7)."""


@dataclass(frozen=True)
class ConfigFailure:
    """Stands in for the runtime environment when startup validation failed (config-error mode)."""

    message: str
