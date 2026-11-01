import asyncio
import json
import threading

from task_offloader_agent.application import lifecycle, service
from task_offloader_agent.core import audit

from ..conftest import make_config


def run(coro):
    return asyncio.run(coro)


def test_audit_failure_is_fail_open(env_for, settings):
    env = env_for(["The answer is yes."])
    settings.run_dir.parent.mkdir(parents=True, exist_ok=True)
    settings.run_dir.write_text("not a folder", encoding="utf-8")  # makes every audit write fail
    result = run(service.ask(env, "Is it yes?", None, "some input text"))
    assert result["status"] in {"ok", "partial"}  # the audit failure itself must not turn it into `failed`
    assert any(w.startswith("audit: write failed") for w in result["warnings"])


def test_concurrent_audit_writes_stay_whole(settings):
    def writer(n):
        for i in range(25):
            audit.write(settings, {"event": "call", "writer": n, "i": i, "pad": "x" * 200})

    threads = [threading.Thread(target=writer, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    events = audit.read_all(settings)
    assert len(events) == 200
    assert {(e["writer"], e["i"]) for e in events} == {(n, i) for n in range(8) for i in range(25)}


def test_config_error_mode_answers_without_crashing(tmp_path):
    runtime = lifecycle.start(workspace=str(tmp_path), profile="missing.toml", environ={})
    assert runtime.env is None and runtime.failure is not None
    status = run(service.status(runtime.target))
    assert status["status"] == "config_error" and "missing.toml" in status["diagnostic"]
    result = run(service.ask(runtime.target, "x", None, "text"))
    assert result["status"] == "disabled" and result["error"]["code"] == "config_error"


def test_startup_event_is_audited(tmp_path, config):
    runtime = lifecycle.start(workspace=str(tmp_path), profile=".task-offloader/profile.toml", environ={},
                              provider=object())
    events = audit.read_all(runtime.env.settings)
    startup = [e for e in events if e.get("event") == "startup"]
    assert startup and startup[0]["profile"] == "fixture" and len(startup[0]["profile_sha256"]) == 64


def test_retention_removes_old_runs_only(env_for, settings):
    old = settings.out_dir / "20200101-000000-local_ask"
    new = settings.out_dir / "29990101-000000-local_ask"
    for folder in (old, new):
        folder.mkdir(parents=True)
        (folder / "x.md").write_text("x", encoding="utf-8")
    import os
    for target in (old, old / "x.md"):
        os.utime(target, (1_000_000_000, 1_000_000_000))
    lifecycle.run_retention_cleanup(env_for([]))
    assert not old.exists() and new.exists()


def test_status_reports_queue_fields(env_for):
    status = run(service.status(env_for([])))
    assert (status["running"], status["queued"], status["max_pending"]) == (0, 0, 3)
    assert json.dumps(status)
    assert make_config
