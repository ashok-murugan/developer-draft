"""Measurement report and daily summary from audit.jsonl.

Draft outcomes (kept / edited / rejected, copied / retyped) arrive with the
drafting tools in phase 4.
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ..core import audit
from ..core.config import Settings

# Conservative: 3 chars per token estimate (no tokenizer available at report time).
_CHARS_PER_TOKEN = 3


def _load(settings: Settings, audit_file: Path | None) -> list[dict[str, Any]]:
    """Read events from *audit_file* when given, otherwise from settings."""
    if audit_file is not None:
        if not audit_file.exists():
            return []
        import json
        events: list[dict[str, Any]] = []
        for line in audit_file.read_text(encoding="utf-8").splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                continue
        return events
    return audit.read_all(settings)


def _task_calls(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [e for e in events if e.get("event") == "call" and e.get("tool") != "local_status"]


def _ratings(events: list[dict[str, Any]]) -> dict[str, str]:
    r: dict[str, str] = {}
    for e in events:
        if e.get("event") == "rated":
            r[e.get("run_id", "")] = e.get("rating", "")
    return r


def _savings_footer(calls: list[dict[str, Any]]) -> list[str]:
    """S3: estimated cloud tokens saved + rough cost reference."""
    total_chars = sum(e.get("input_chars", 0) for e in calls if e.get("status") in ("ok", "partial"))
    if total_chars == 0:
        return []
    est_tokens = total_chars // _CHARS_PER_TOKEN
    # Claude Sonnet 3.7 input: $3 / 1M tokens (reference only — adjust to your actual model)
    ref_cost = est_tokens * 3.0 / 1_000_000
    return [
        "",
        "## Estimated primary-agent context savings",
        f"- Input chars pre-processed locally: {total_chars:,}",
        f"- Estimated tokens not sent to cloud model: ~{est_tokens:,}",
        f"  (at Claude Sonnet $3/M input tokens ≈ ${ref_cost:.2f}; adjust for your actual model)",
        "- Actual savings depend on your tokenizer and which calls you would have made manually.",
    ]


def _tool_table(
    by_tool: dict[str, list[dict]],
    ratings: dict[str, str],
) -> list[str]:
    out: list[str] = []
    out.append(
        "| Tool | Calls | ok | partial | failed | refused | disabled |"
        " Median s | p90 s | Chars not read | Good | Bad |"
    )
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for tool, rows in sorted(by_tool.items()):
        status = Counter(r.get("status") for r in rows)
        times = sorted(
            r["duration_ms"] / 1000
            for r in rows
            if "duration_ms" in r and r.get("status") != "disabled"
        )
        median = f"{statistics.median(times):.0f}" if times else "-"
        p90 = f"{times[min(len(times) - 1, int(len(times) * 0.9))]:.0f}" if times else "-"
        not_read = sum(
            max(0, r.get("input_chars", 0) - r.get("result_chars", 0)
                - r.get("cited_chars", 0) - r.get("digest_chars", 0))
            for r in rows
            if r.get("status") in ("ok", "partial")
        )
        rated = Counter(ratings.get(r.get("run_id", "")) for r in rows)
        out.append(
            f"| {tool} | {len(rows)} | {status['ok']} | {status['partial']} |"
            f" {status['failed']} | {status['refused']} | {status['disabled']} |"
            f" {median} | {p90} | {not_read:,} | {rated['good']} | {rated['bad']} |"
        )
    return out


def build(
    settings: Settings,
    *,
    audit_file: Path | None = None,
    fail_on_bad_rate: bool = False,
) -> tuple[str, int]:
    """Return (report_text, exit_code).

    exit_code is non-zero only when fail_on_bad_rate=True and the bad-rate
    threshold is exceeded for at least one tool.
    """
    events = _load(settings, audit_file)
    calls = _task_calls(events)
    ratings = _ratings(events)

    if not calls:
        source = str(audit_file) if audit_file else ".task-offloader/run/audit.jsonl"
        return f"No task-offloader task calls recorded yet in {source}.\n", 0

    by_tool: dict[str, list[dict]] = defaultdict(list)
    for e in calls:
        by_tool[e.get("tool", "?")].append(e)

    out = [
        "# TaskOffloaderAgent report",
        "",
        f"Calls: {len(calls)}  ({calls[0].get('ts', '?')} → {calls[-1].get('ts', '?')})",
        "",
    ]
    out.extend(_tool_table(by_tool, ratings))
    out.append("")

    length = sum(1 for e in calls if e.get("done_reason") == "length")
    retries = sum(e.get("retries", 0) for e in calls)
    queue = [e["queue_ms"] for e in calls if e.get("queue_ms")]
    out.append(f"- done_reason length (after retry): {length}; retries: {retries}")
    out.append(
        f"- calls that waited in the queue: {len(queue)}"
        + (f", longest {max(queue) / 1000:.0f} s" if queue else "")
    )
    out.append(
        "- Chars not read = input chars - result chars - cited chars - digest chars"
        " (upper bound of raw input the primary agent did not read)."
    )

    bad_tools = [
        t
        for t, rows in by_tool.items()
        if (n := sum(1 for r in rows if ratings.get(r.get("run_id", "")) in ("good", "bad")))
        and sum(1 for r in rows if ratings.get(r.get("run_id", "")) == "bad") * 2 > n
    ]
    if bad_tools:
        out.append(
            f"- ⚠ More than half of rated results are bad for: {', '.join(bad_tools)}."
            " Consider `task-offloader off <tool>`."
        )

    out.extend(_savings_footer(calls))

    exit_code = 1 if (fail_on_bad_rate and bad_tools) else 0
    return "\n".join(out) + "\n", exit_code


def summary(
    settings: Settings,
    *,
    days: int = 7,
    audit_file: Path | None = None,
) -> str:
    """S1: daily breakdown for the last *days* days."""
    events = _load(settings, audit_file)
    calls = _task_calls(events)

    if not calls:
        source = str(audit_file) if audit_file else ".task-offloader/run/audit.jsonl"
        return f"No task-offloader task calls recorded yet in {source}.\n"

    ratings = _ratings(events)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)

    # Group by ISO date string (YYYY-MM-DD)
    by_day: dict[str, list[dict]] = defaultdict(list)
    for e in calls:
        ts_str = e.get("ts", "")
        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if ts >= cutoff:
            by_day[ts.strftime("%Y-%m-%d")].append(e)

    if not by_day:
        return f"No calls in the last {days} days.\n"

    out = [
        f"# TaskOffloaderAgent daily summary (last {days} days)",
        "",
        "| Date | Calls | ok | failed | Input tokens | Saved chars | Good | Bad | Task types |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for day in sorted(by_day):
        rows = by_day[day]
        status = Counter(r.get("status") for r in rows)
        input_tokens = sum(r.get("input_tokens", 0) for r in rows)
        saved_chars = sum(
            max(0, r.get("input_chars", 0) - r.get("result_chars", 0)
                - r.get("cited_chars", 0) - r.get("digest_chars", 0))
            for r in rows
            if r.get("status") in ("ok", "partial")
        )
        rated = Counter(ratings.get(r.get("run_id", "")) for r in rows)
        task_types = Counter(r.get("task_type") for r in rows if r.get("task_type"))
        type_str = " ".join(f"{t}:{n}" for t, n in task_types.most_common(3)) or "-"
        out.append(
            f"| {day} | {len(rows)} | {status['ok']} | {status['failed']} |"
            f" {input_tokens:,} | {saved_chars:,} | {rated['good']} | {rated['bad']} | {type_str} |"
        )

    out.append("")
    out.extend(_savings_footer([e for rows in by_day.values() for e in rows]))
    return "\n".join(out) + "\n"


def pending_ratings(settings: Settings, *, audit_file: Path | None = None) -> list[dict[str, Any]]:
    """S4: returns unrated ok/partial calls with their run_id and summary field."""
    events = _load(settings, audit_file)
    rated_ids = {e.get("run_id") for e in events if e.get("event") == "rated"}
    pending = []
    for e in events:
        if (
            e.get("event") == "call"
            and e.get("tool") != "local_status"
            and e.get("status") in ("ok", "partial")
            and e.get("run_id") not in rated_ids
        ):
            pending.append(e)
    return pending