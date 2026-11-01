"""MCP stdio spike: a cancelled tool call must free the gate slot."""

import asyncio
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

from ..conftest import PROFILE_REL, make_workspace  # noqa: E402

CHAT_DELAY_S = 20.0


class _SlowOllama(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def _send(self, payload):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send({"models": [{"name": "my-coder"}]})

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        time.sleep(CHAT_DELAY_S)
        try:
            self._send({"message": {"content": "late answer"}, "done": True, "done_reason": "stop",
                        "prompt_eval_count": 1, "eval_count": 1})
        except OSError:
            pass


@pytest.fixture
def slow_ollama():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _SlowOllama)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def test_cancelled_call_frees_the_slot(tmp_path, slow_ollama):
    make_workspace(tmp_path)
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "task_offloader_agent", "--workspace", str(tmp_path), "--profile", PROFILE_REL, "mcp"],
        env={"TASK_OFFLOADER_PROVIDER_URL": slow_ollama, "SYSTEMROOT": "C:\\Windows", "PATH": ""},
    )

    async def scenario():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                with pytest.raises(Exception):  # noqa: B017 - the read timeout abandons the request
                    await session.call_tool("local_ask", {"instruction": "q", "text": "some text"},
                                            read_timeout_seconds=1)
                for _ in range(25):  # far below CHAT_DELAY_S: only cancellation can free the slot in time
                    status = await session.call_tool("local_status", {})
                    data = json.loads(status.content[0].text)
                    if data["running"] == 0 and data["queued"] == 0:
                        return data
                    await asyncio.sleep(0.2)
                return data

    data = asyncio.run(asyncio.wait_for(scenario(), 40))
    assert data["running"] == 0 and data["queued"] == 0
