from datetime import datetime

from task_offloader_agent.core.paths import PathGuard
from task_offloader_agent.prefilter.logs import Filters, build_digest, compile_pattern, parse_ts, template

CID = "4fecc5f5-eb39-4981-ba50-4e53d7645c2d"

IWC = f"""#### Log file written by App Server version [@version_num@] ####
INFO   (2026-09-28T10:34:30,000+0530) [main]  Boot:10 - started
INFO   (2026-09-28T10:34:38,100+0530) [exec-1]  ApiController:50 - [{CID}] POST /api/chat
ERROR  (2026-09-28T10:34:38,391+0530) [chat-1]  PluginChatClient:98 - [{CID}] Error connecting to plugin: Connection refused
java.net.ConnectException: Connection refused: getsockopt
\tat java.base/sun.nio.ch.Net.pollConnect(Native Method)
\tat java.base/sun.nio.ch.Net.poll(Net.java:1)
\tat a.B.c(B.java:2)
Caused by: java.io.IOException: boom
\tat x.Y.z(Y.java:3)
\tat x.Y.w(Y.java:4)
\t... 12 more
WARN   (2026-09-28T10:34:50,000+0530) [chat-1]  EventRelay:20 - relay closed after 1200 ms for 10.0.0.5
WARN   (2026-09-28T10:34:51,000+0530) [chat-2]  EventRelay:20 - relay closed after 900 ms for 10.0.0.6
ERROR  (2026-09-28T12:00:00,000+0530) [other]  Far:1 - unrelated later error
INFO   (2026-09-28T10:34:52,000+0530) [exec-1]  ApiController:60 - Authorization: Bearer abcdefghijklmnop1234 for user a@b.com
"""

ERRORS = """ERROR  (2026-09-28T10:34:38,391+0530) [chat-1]  PluginChatClient:98 - [%s] Error connecting to plugin: Connection refused
java.net.ConnectException: Connection refused: getsockopt
""" % CID


def _digest(write, profile, settings, **filters):
    iwc = write("logs/iwc.log", IWC)
    err = write("logs/errors.log", ERRORS)
    guard = PathGuard(settings, profile)
    return build_digest([("logs/iwc.log", iwc), ("logs/errors.log", err)], Filters(**filters),
                        profile.log_formats, guard.open_checked)


def test_parse_ts_local_naive():
    ts = parse_ts("2026-09-28T10:34:38,391+0530")
    assert ts is not None and ts.tzinfo is None
    assert parse_ts("2026-09-28 10:34") == datetime(2026, 9, 28, 10, 34)
    assert parse_ts("yesterday") is None


def test_template():
    assert template("relay closed after 1200 ms for 10.0.0.5") == "relay closed after <n> ms for <ip>"
    assert template(f"[{CID}] x") == "[<uuid>] x"


def test_default_keeps_error_warn_dedupes_and_groups(write, profile, settings):
    d = _digest(write, profile, settings)
    assert d.entries == 4  # 2 ERROR + 2 WARN; the errors.log copy is a duplicate
    assert d.duplicates == 1
    assert d.groups == 3  # the two EventRelay WARN lines share a template
    md = d.markdown
    assert "logs/iwc.log:L4| ERROR  (2026-09-28T10:34:38,391+0530)" in md
    assert "logs/iwc.log:L5| java.net.ConnectException" in md
    assert "logs/iwc.log:L6| \tat java.base/sun.nio.ch.Net.pollConnect" in md  # first frame kept
    assert "Net.poll(Net.java:1)" not in md  # later frames collapsed
    assert "logs/iwc.log:L9| Caused by: java.io.IOException: boom" in md
    assert "logs/iwc.log:L10| \tat x.Y.z" in md
    assert "stack lines collapsed" in md
    assert "2 times" in md
    assert d.files["logs/iwc.log"].total_lines == 16


def test_correlation_window(write, profile, settings):
    d = _digest(write, profile, settings, correlation_id=CID)
    md = d.markdown
    assert d.timeline == 2
    assert "ApiController:50" in md  # INFO line with the id is kept
    assert "EventRelay:20" in md  # WARN within 30 s of the last id line
    assert "unrelated later error" not in md  # outside the window
    assert "Boot:10" not in md


def test_time_filter_and_pattern(write, profile, settings):
    d = _digest(write, profile, settings, since=parse_ts("2026-09-28T10:34:45+0530"),
                until=parse_ts("2026-09-28T11:00+0530"),
                pattern=compile_pattern("Bearer|relay"))
    md = d.markdown
    assert "EventRelay:20" in md and "ApiController:60" in md
    assert "PluginChatClient" not in md and "unrelated" not in md


def test_missing_correlation_id_warns(write, profile, settings):
    d = _digest(write, profile, settings, correlation_id="nope-123")
    assert d.entries == 0 and d.warnings
