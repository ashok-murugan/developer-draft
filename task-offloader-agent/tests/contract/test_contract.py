"""Contract tests: the externally visible behaviour that the restructuring must not change.

Golden files live in tests/contract/golden. Regenerate them only for a deliberate contract change:
set UPDATE_GOLDEN=1, run this file, and review the diff.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import pytest

from task_offloader_agent.application import service
from task_offloader_agent.core import audit
from task_offloader_agent.core.redact import redactor_for
from task_offloader_agent.core.switch import MODES, TOOLS, SwitchState, decide, set_mode, set_tool
from task_offloader_agent.providers.base import ProviderUnavailable

GOLDEN = Path(__file__).parent / "golden"
UPDATE = os.environ.get("UPDATE_GOLDEN") == "1"
LOG_LINE = "ERROR  (2026-09-28T10:34:38,391+0530) [x]  A:1 - failed with Authorization: Bearer abcdefghijklmnop1234\n"


def check_golden(name: str, actual) -> None:
    path = GOLDEN / name
    text = actual if isinstance(actual, str) else json.dumps(actual, indent=2, ensure_ascii=False) + "\n"
    if UPDATE:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return
    assert path.exists(), f"missing golden file {name}; run once with UPDATE_GOLDEN=1"
    assert text == path.read_text(encoding="utf-8"), f"contract changed: {name}"


def normalize(result: dict) -> dict:
    """Replace the only volatile value, the run id, so results compare byte for byte."""
    text = json.dumps(result, ensure_ascii=False)
    if result.get("run_id"):
        text = text.replace(result["run_id"], "<RUN_ID>")
    return json.loads(text)


def run(coro):
    return asyncio.run(coro)


def test_local_status(env_for):
    check_golden("local_status.json", run(service.status(env_for([]))))


def test_local_status_mode_off(env_for, settings):
    set_mode(settings, "off")
    check_golden("local_status_off.json", run(service.status(env_for([]))))


def test_ask_ok(env_for, write):
    write("src/A.java", "class A {\n  int timeout = 30;\n}\n")
    env = env_for(["The timeout is 30 (src/A.java:L2) and (nope.java:L1)."])
    check_golden("ask_ok.json", normalize(run(service.ask(env, "What is the timeout?", ["src/A.java"]))))


def test_ask_partial_without_citation(env_for, write):
    write("src/A.java", "\n".join(f"line {i}" for i in range(1, 101)))
    env = env_for(["Something without a citation."])
    check_golden("ask_partial.json", normalize(run(service.ask(env, "Summarise", ["src/A.java:L40-L60"]))))


def test_ask_refused(env_for, write):
    write("big.txt", "\n".join("word " * 40 for _ in range(400)))
    env = env_for([], TASK_OFFLOADER_CHUNK_TOKENS="1000", TASK_OFFLOADER_MAX_CHUNKS="2")
    check_golden("ask_refused.json", normalize(run(service.ask(env, "Summarise", ["big.txt"]))))


def test_ask_denied_path(env_for, write):
    write(".env", "SECRET=1")
    check_golden("ask_denied.json", normalize(run(service.ask(env_for([]), "Read", [".env"]))))


def test_ask_chunked(env_for, write):
    write("big.txt", "\n".join(f"fact {i} " + "word " * 40 for i in range(1, 31)))

    def reply(user):
        if "Notes written from" in user:
            return "Merged: fact 1 (big.txt:L1) and 30 (big.txt:L30)."
        if "L1| fact 1 " in user:
            return "Fact 1 (big.txt:L1)"
        if "L30| fact 30 " in user:
            return "Fact 30 (big.txt:L30)"
        return "NOTHING RELEVANT"

    env = env_for(reply, TASK_OFFLOADER_CHUNK_TOKENS="1000", TASK_OFFLOADER_MAX_CHUNKS="10")
    check_golden("ask_chunked.json", normalize(run(service.ask(env, "List facts", ["big.txt"]))))


def test_logs_with_narrative(env_for, write):
    write("logs/rest.log", LOG_LINE)
    env = env_for(["A failed first (logs/rest.log:L1)."])
    result = run(service.summarize_logs(env, ["logs/rest.log"]))
    check_golden("logs_ok.json", normalize(result))
    check_golden("logs_ok_digest.md", (env.settings.root / result["files"][0]).read_text(encoding="utf-8"))


def test_logs_without_narrative(env_for, write):
    write("logs/rest.log", LOG_LINE)
    check_golden("logs_no_narrative.json",
                 normalize(run(service.summarize_logs(env_for([]), ["logs/rest.log"], narrate=False))))


def test_logs_provider_down(env_for, write):
    write("logs/rest.log", LOG_LINE)
    env = env_for([ProviderUnavailable("Ollama not reachable")])
    check_golden("logs_provider_down.json", normalize(run(service.summarize_logs(env, ["logs/rest.log"]))))


def test_logs_outside_logs_folder(env_for, write):
    write("src/x.log", LOG_LINE)
    check_golden("logs_not_under_logs.json",
                 normalize(run(service.summarize_logs(env_for([]), ["src/x.log"]))))


def test_disabled_results(env_for, write, settings):
    write("a.txt", "x")
    env = env_for([])
    set_mode(settings, "off")
    off = run(service.ask(env, "x", ["a.txt"], requested_by_user=True))
    set_mode(settings, "auto")
    set_tool(settings, "summarize_logs", False)
    flag = run(service.summarize_logs(env, ["logs/x.log"]))
    check_golden("disabled.json", {"mode_off": normalize(off), "tool_flag": normalize(flag)})


def test_audit_call_fields(env_for, write, settings):
    write("src/A.java", "class A {\n  int timeout = 30;\n}\n")
    write("logs/rest.log", LOG_LINE)
    run(service.ask(env_for(["The timeout is 30 (src/A.java:L2)."]), "q", ["src/A.java"]))
    run(service.summarize_logs(env_for(["A failed (logs/rest.log:L1)."]), ["logs/rest.log"]))
    run(service.status(env_for([])))
    fields = {}
    for event in audit.read_all(settings):
        fields[event["tool"]] = sorted(event)
    check_golden("audit_fields.json", fields)


def test_switch_precedence_table():
    rows = []
    for mode in MODES:
        for tool in TOOLS:
            for flag in (True, False):
                for by_user in (False, True):
                    state = SwitchState(mode=mode, flags={name: flag for name in TOOLS}, source="file")
                    d = decide(state, tool, by_user)
                    rows.append(f"{mode:7} {tool:14} flag={flag!s:5} by_user={by_user!s:5} "
                                f"-> allowed={d.allowed!s:5} reason={d.reason}")
    check_golden("switch_precedence.txt", "\n".join(rows) + "\n")


def test_redaction_corpus(profile):
    corpus = (GOLDEN / "redaction_input.txt").read_text(encoding="utf-8")
    redacted, counts = redactor_for(profile).redact(corpus)
    check_golden("redaction_output.txt", redacted)
    check_golden("redaction_counts.json", dict(sorted(counts.items())))
