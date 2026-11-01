"""Admission gate: one model call at a time, a bounded FIFO queue, deadline-aware.

A slot is handed from the finishing call to the oldest waiter, so the order is strictly first in,
first out and a cancelled or timed-out waiter can never leave the slot locked.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from ..providers.base import ProviderBusy, ProviderTimeout


@dataclass(frozen=True)
class Ticket:
    queue_ms: int


class Gate:
    def __init__(self, max_pending: int):
        self.max_pending = max_pending
        self._busy = False
        self._closed = False
        self._waiters: deque[asyncio.Future[None]] = deque()

    @property
    def running(self) -> int:
        return 1 if self._busy else 0

    @property
    def queued(self) -> int:
        return len(self._waiters)

    def close(self) -> None:
        """Refuse new calls and fail every waiting call; a running call finishes on its own."""
        self._closed = True
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_exception(ProviderBusy("TaskOffloaderAgent is shutting down", code="shutting_down",
                                                  retryable=False))

    def _release(self) -> None:
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)  # the slot stays busy and now belongs to the waiter
                return
        self._busy = False

    def _abandon(self, waiter: asyncio.Future[None]) -> None:
        """A waiter stops waiting. If it was already granted the slot, pass the slot on."""
        if waiter.done() and not waiter.cancelled() and waiter.exception() is None:
            self._release()
            return
        waiter.cancel()
        try:
            self._waiters.remove(waiter)
        except ValueError:
            pass

    @asynccontextmanager
    async def slot(self, deadline: float) -> AsyncIterator[Ticket]:
        started = time.monotonic()
        if self._closed:
            raise ProviderBusy("TaskOffloaderAgent is shutting down", code="shutting_down", retryable=False)
        if self._busy:
            if len(self._waiters) >= self.max_pending:
                raise ProviderBusy(f"TaskOffloaderAgent is busy: {len(self._waiters)} call(s) already queued "
                                   f"(limit {self.max_pending})")
            waiter: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            self._waiters.append(waiter)
            remaining = deadline - time.monotonic()
            try:
                if remaining <= 0:
                    raise TimeoutError
                await asyncio.wait_for(waiter, remaining)
            except TimeoutError:
                self._abandon(waiter)
                raise ProviderTimeout("timed out waiting for an earlier TaskOffloaderAgent call") from None
            except BaseException:
                self._abandon(waiter)
                raise
        else:
            self._busy = True
        try:
            yield Ticket(queue_ms=int((time.monotonic() - started) * 1000))
        finally:
            self._release()
