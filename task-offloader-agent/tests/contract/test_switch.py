import json

import pytest

from task_offloader_agent.adapters.cli import main as cli
from task_offloader_agent.core.switch import decide, read_switch, reset_tool, set_mode, set_tool


def test_defaults_without_file(settings):
    state = read_switch(settings)
    assert state.mode == "auto" and state.source == "env"
    assert state.flags["local_ask"] is True and state.flags["draft_tests"] is False
    assert decide(state, "local_ask", False).allowed


def test_mode_off_blocks_all_but_status(settings):
    set_mode(settings, "off")
    state = read_switch(settings)
    assert decide(state, "local_ask", True).reason == "mode"
    assert decide(state, "local_status", False).allowed


def test_tool_flag_overrides_requested_by_user(settings):
    set_tool(settings, "summarize_logs", False)
    state = read_switch(settings)
    assert decide(state, "summarize_logs", True).reason == "tool_flag"
    assert decide(state, "local_ask", False).allowed
    reset_tool(settings, "summarize_logs")
    assert decide(read_switch(settings), "summarize_logs", False).allowed


def test_manual_needs_requested_by_user(settings):
    set_mode(settings, "manual")
    state = read_switch(settings)
    assert decide(state, "local_ask", False).reason == "manual"
    assert decide(state, "local_ask", True).allowed


def test_status_flag_false_disables_status(settings):
    set_tool(settings, "local_status", False)
    assert decide(read_switch(settings), "local_status", False).reason == "tool_flag"


def test_unparseable_file_is_off(settings):
    settings.run_dir.mkdir(parents=True)
    settings.switch_file.write_text("{not json", encoding="utf-8")
    state = read_switch(settings)
    assert state.mode == "off" and state.error


def test_bad_values_fail_safe(settings):
    settings.run_dir.mkdir(parents=True)
    settings.switch_file.write_text(json.dumps(
        {"mode": "sometimes", "tools": {"local_ask": "yes", "draft_test": True}}), encoding="utf-8")
    state = read_switch(settings)
    assert state.mode == "off" and state.error
    assert state.flags["local_ask"] is False
    assert any("draft_test" in w for w in state.warnings)
    assert any("local_ask" in w for w in state.warnings)


def test_set_tool_rejects_unknown(settings):
    with pytest.raises(ValueError):
        set_tool(settings, "draft_test", True)


def test_cli_switch_commands(settings, capsys):
    base = ["--workspace", str(settings.root), "--profile", ".task-offloader/profile.toml"]
    assert cli.main([*base, "off", "summarize_logs"]) == 0
    assert cli.main([*base, "manual"]) == 0
    data = json.loads(settings.switch_file.read_text(encoding="utf-8"))
    assert data == {"mode": "manual", "tools": {"summarize_logs": False}}
    assert cli.main([*base, "reset", "summarize_logs"]) == 0
    assert cli.main([*base, "on"]) == 0
    assert json.loads(settings.switch_file.read_text(encoding="utf-8")) == {"mode": "auto", "tools": {}}
    assert cli.main([*base, "on", "draft_test"]) == 1
    assert cli.main([*base, "apply", "x"]) == 2
    out = capsys.readouterr().out
    assert "summarize_logs   false" in out
