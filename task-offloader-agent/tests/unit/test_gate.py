import asyncio
import time

import pytest

from task_offloader_agent.application.gate import Gate
from task_offloader_agent.providers.base import ProviderBusy, ProviderTimeout


def run(coro):
    return asyncio.run(coro)


def _deadline(seconds: float = 5.0) -> float:
    return time.monotonic() + seconds


def test_fifo_order_and_queue_limit():
    async def scenario():
        gate = Gate(max_pending=2)
        order: list[str] = []
        release = asyncio.Event()

        async def holder():
            async with gate.slot(_deadline()):
                await release.wait()

        async def waiter(name):
            async with gate.slot(_deadline()):
                order.append(name)

        first = asyncio.create_task(holder())
        await asyncio.sleep(0)
        a = asyncio.create_task(waiter("a"))
        await asyncio.sleep(0)
        b = asyncio.create_task(waiter("b"))
        await asyncio.sleep(0)
        assert (gate.running, gate.queued) == (1, 2)
        with pytest.raises(ProviderBusy) as busy:
            async with gate.slot(_deadline()):
                pass
        assert busy.value.retryable
        release.set()
        await asyncio.gather(first, a, b)
        assert order == ["a", "b"] and (gate.running, gate.queued) == (0, 0)

    run(scenario())


def test_waiter_times_out_and_frees_its_place():
    async def scenario():
        gate = Gate(max_pending=1)
        release = asyncio.Event()

        async def holder():
            async with gate.slot(_deadline()):
                await release.wait()

        task = asyncio.create_task(holder())
        await asyncio.sleep(0)
        with pytest.raises(ProviderTimeout):
            async with gate.slot(time.monotonic() + 0.05):
                pass
        assert gate.queued == 0
        release.set()
        await task
        assert gate.running == 0

    run(scenario())


def test_cancelled_waiter_and_cancelled_holder_free_the_slot():
    async def scenario():
        gate = Gate(max_pending=2)
        release = asyncio.Event()

        async def hold():
            async with gate.slot(_deadline()):
                await release.wait()

        holder = asyncio.create_task(hold())
        await asyncio.sleep(0)
        waiter = asyncio.create_task(hold())
        await asyncio.sleep(0)
        waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiter
        assert gate.queued == 0
        holder.cancel()
        with pytest.raises(asyncio.CancelledError):
            await holder
        assert (gate.running, gate.queued) == (0, 0)
        async with gate.slot(_deadline()):
            assert gate.running == 1

    run(scenario())


def test_close_fails_waiters_and_new_calls():
    async def scenario():
        gate = Gate(max_pending=2)
        release = asyncio.Event()

        async def hold():
            async with gate.slot(_deadline()):
                await release.wait()

        holder = asyncio.create_task(hold())
        await asyncio.sleep(0)
        waiter = asyncio.create_task(hold())
        await asyncio.sleep(0)
        gate.close()
        with pytest.raises(ProviderBusy) as err:
            await waiter
        assert err.value.code == "shutting_down" and not err.value.retryable
        with pytest.raises(ProviderBusy):
            async with gate.slot(_deadline()):
                pass
        release.set()
        await holder

    run(scenario())
