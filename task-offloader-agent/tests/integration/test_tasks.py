import asyncio
import json

from task_offloader_agent.application import service
from task_offloader_agent.application.lifecycle import build_env
from task_offloader_agent.core import audit
from task_offloader_agent.core.switch import set_mode, set_tool
from task_offloader_agent.providers.base import ProviderUnavailable

from ..conftest import make_config
from ..support import FakeProvider


def _env(settings, replies, **env_overrides):
    return build_env(make_config(settings.root, **env_overrides), FakeProvider(replies))


def run(coro):
    return asyncio.run(coro)


def test_ask_ok_with_citations_and_audit(settings, write):
    write("src/A.java", "class A {\n  int timeout = 30;\n}\n")
    env = _env(settings, ["The timeout is 30 (src/A.java:L2) and (nope.java:L1)."])
    result = run(service.ask(env, "What is the timeout?", ["src/A.java"]))
    assert result["status"] == "ok"
    assert result["citations"] == ["src/A.java:L2"]
    assert "[invalid citation removed]" in result["answer"]
    assert "1 invalid citation(s) removed" in result["warnings"]
    assert list(result) == ["run_id", "status", "for", "summary", "answer", "citations", "files", "apply",
                            "checks", "budget", "warnings", "review", "next_step"]
    event = audit.read_all(settings)[-1]
    assert event["tool"] == "local_ask" and event["status"] == "ok" and event["cited_chars"] > 0
    assert "answer" not in event and "timeout" not in json.dumps(event)


def test_ask_line_range_and_no_citation_is_partial(settings, write):
    write("src/A.java", "\n".join(f"line {i}" for i in range(1, 101)))
    env = _env(settings, ["Something without a citation."])
    result = run(service.ask(env, "Summarise", ["src/A.java:L40-L60"]))
    assert result["status"] == "partial"
    assert "L40| line 40" in env.provider.prompts[0] and "L61|" not in env.provider.prompts[0]


def test_ask_length_retry(settings, write):
    write("a.txt", "alpha\nbeta\n")
    env = _env(settings, [("long...", "length"), "Alpha is first (a.txt:L1)."])
    result = run(service.ask(env, "What is first?", ["a.txt"]))
    assert result["status"] == "ok"
    assert "previous answer was cut" in env.provider.prompts[1]
    assert audit.read_all(settings)[-1]["retries"] == 1


def test_ask_refused_over_budget(settings, write):
    write("big.txt", "\n".join("word " * 40 for _ in range(400)))
    env = _env(settings, [], TASK_OFFLOADER_CHUNK_TOKENS="1000", TASK_OFFLOADER_MAX_CHUNKS="2")
    result = run(service.ask(env, "Summarise", ["big.txt"]))
    assert result["status"] == "refused"
    assert "line ranges" in result["next_step"]


def test_ask_multi_chunk_merge(settings, write):
    write("big.txt", "\n".join(f"fact {i} " + "word " * 40 for i in range(1, 31)))

    def reply(user):
        if "Notes written from" in user:
            return "Merged: fact 1 (big.txt:L1) and 30 (big.txt:L30)."
        if "L1| fact 1 " in user:
            return "Fact 1 (big.txt:L1)"
        if "L30| fact 30 " in user:
            return "Fact 30 (big.txt:L30)"
        return "NOTHING RELEVANT"

    env = _env(settings, reply, TASK_OFFLOADER_CHUNK_TOKENS="1000", TASK_OFFLOADER_MAX_CHUNKS="10")
    result = run(service.ask(env, "List facts", ["big.txt"]))
    assert result["status"] == "ok", result
    assert result["budget"]["chunks"] >= 2
    assert result["citations"] == ["big.txt:L1", "big.txt:L30"]
    assert env.provider.prompts[-1].count("Note from part") == 2  # NOTHING RELEVANT parts are dropped


def test_ask_denied_path_fails(settings, write):
    write(".env", "SECRET=1")
    result = run(service.ask(_env(settings, []), "Read", [".env"]))
    assert result["status"] == "failed" and "denied" in result["summary"]


def test_disabled_by_mode_and_flag(settings, write):
    write("a.txt", "x")
    env = _env(settings, [])
    set_mode(settings, "off")
    result = run(service.ask(env, "x", ["a.txt"], requested_by_user=True))
    assert result["status"] == "disabled" and "mode=off" in result["summary"]
    assert result["error"] == {"code": "switched_off", "retryable": False}
    assert run(service.status(env))["mode"] == "off"
    set_mode(settings, "auto")
    set_tool(settings, "summarize_logs", False)
    result = run(service.summarize_logs(env, ["logs/x.log"]))
    assert result["status"] == "disabled" and "tools.summarize_logs=false" in result["summary"]
    assert audit.read_all(settings)[-1]["reason"] == "tool_flag"


def test_logs_ollama_down_returns_digest(settings, write):
    write("logs/rest.log",
          "ERROR  (2026-09-28T10:34:38,391+0530) [x]  A:1 - failed with Authorization: Bearer abcdefghijklmnop1234\n")
    env = _env(settings, [ProviderUnavailable("Ollama not reachable")])
    result = run(service.summarize_logs(env, ["logs/rest.log"]))
    assert result["status"] == "partial"
    assert result["checks"]["narrative"].startswith("not_run")
    digest = (settings.root / result["files"][0]).read_text(encoding="utf-8")
    assert "logs/rest.log:L1|" in digest and "abcdefghijklmnop1234" not in digest
    assert "<redacted:bearer>" in digest


def test_logs_narrative_ok(settings, write):
    write("logs/rest.log", "ERROR  (2026-09-28T10:34:38,391+0530) [x]  A:1 - failed\n")
    env = _env(settings, ["A failed first (logs/rest.log:L1)."])
    result = run(service.summarize_logs(env, ["logs/rest.log"]))
    assert result["status"] == "ok" and result["citations"] == ["logs/rest.log:L1"]
    assert result["files"][0] in result["next_step"]


def test_logs_only_under_logs(settings, write):
    write("src/x.log", "ERROR  (2026-09-28T10:34:38,391+0530) [x]  A:1 - failed\n")
    result = run(service.summarize_logs(_env(settings, []), ["src/x.log"]))
    assert result["status"] == "failed" and "logs/" in result["summary"]
