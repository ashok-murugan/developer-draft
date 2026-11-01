"""Measurement report from audit.jsonl, condense tools only.

Draft outcomes (kept / edited / rejected, copied / retyped) arrive with the
drafting tools in phase 4.
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict

from ..core import audit
from ..core.config import Settings


def build(settings: Settings) -> str:
    events = audit.read_all(settings)
    calls = [e for e in events if e.get("event") == "call" and e.get("tool") != "local_status"]
    ratings: dict[str, str] = {}
    for e in events:
        if e.get("event") == "rated":
            ratings[e.get("run_id", "")] = e.get("rating", "")

    if not calls:
        return "No task-offloader task calls recorded yet in .task-offloader/run/audit.jsonl.\n"

    by_tool: dict[str, list[dict]] = defaultdict(list)
    for e in calls:
        by_tool[e.get("tool", "?")].append(e)

    out = ["# TaskOffloaderAgent report", "",
           f"Calls: {len(calls)} (from {calls[0].get('ts', '?')} to {calls[-1].get('ts', '?')})", ""]
    out.append("| Tool | Calls | ok | partial | failed | refused | disabled | Median s | p90 s | "
               "Chars not read | Good | Bad |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for tool, rows in sorted(by_tool.items()):
        status = Counter(r.get("status") for r in rows)
        times = sorted(r["duration_ms"] / 1000 for r in rows if "duration_ms" in r and r.get("status") != "disabled")
        median = f"{statistics.median(times):.0f}" if times else "-"
        p90 = f"{times[min(len(times) - 1, int(len(times) * 0.9))]:.0f}" if times else "-"
        not_read = sum(max(0, r.get("input_chars", 0) - r.get("result_chars", 0) - r.get("cited_chars", 0)
                           - r.get("digest_chars", 0))
                       for r in rows if r.get("status") in ("ok", "partial"))
        rated = Counter(ratings.get(r.get("run_id", "")) for r in rows)
        out.append(f"| {tool} | {len(rows)} | {status['ok']} | {status['partial']} | {status['failed']} | "
                   f"{status['refused']} | {status['disabled']} | {median} | {p90} | {not_read:,} | "
                   f"{rated['good']} | {rated['bad']} |")
    out.append("")

    length = sum(1 for e in calls if e.get("done_reason") == "length")
    retries = sum(e.get("retries", 0) for e in calls)
    queue = [e["queue_ms"] for e in calls if e.get("queue_ms")]
    out.append(f"- done_reason length (after retry): {length}; retries: {retries}")
    out.append(f"- calls that waited in the queue: {len(queue)}"
               + (f", longest {max(queue) / 1000:.0f} s" if queue else ""))
    out.append("- Chars not read = input chars - result chars - cited chars - digest chars "
               "(upper bound of raw input the primary agent did not read).")
    bad = [t for t, rows in by_tool.items()
           if (n := sum(1 for r in rows if ratings.get(r.get("run_id", "")) in ("good", "bad")))
           and sum(1 for r in rows if ratings.get(r.get("run_id", "")) == "bad") * 2 > n]
    if bad:
        out.append(f"- More than half of the rated results are bad for: {', '.join(bad)}. "
                   "Section 11 says: stop delegating these (`task-offloader off <tool>`).")
    return "\n".join(out) + "\n"
