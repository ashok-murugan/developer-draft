"""Deterministic log prefilter for summarize_logs.

Selects lines by code, never by the model: time window, correlation id, pattern,
ERROR/WARN level. Stack traces are collapsed, duplicates (errors.log repeats
iwc.log) are dropped, repeated messages are grouped by template. Every line in
the digest is verbatim (cut at MAX_LINE_CHARS) with its `path:Ln` reference.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from io import TextIOWrapper
from pathlib import Path
from typing import BinaryIO

from ..core.budget import MAX_LINE_CHARS
from ..core.profile import LogFormat
from ..postprocess.citations import CitedFile

# Built-in fallback: 2026-05-11 08:55:41.906 [ERROR] message  /  2026-05-11T08:55:41Z ERROR message
# Workspace-specific formats come from the profile ([[logs.formats]]) and are tried first.
GENERIC_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+"
    r"\[?(?P<level>TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|SEVERE)\]?:?\s+(?P<msg>.*)$"
)
FRAME_RE = re.compile(r"^\s+at\s")
MORE_RE = re.compile(r"^\s*\.\.\.\s*\d+\s+(more|common frames omitted)")

PROBLEM_LEVELS = {"WARN", "WARNING", "ERROR", "FATAL", "SEVERE"}
CORRELATION_SLACK = timedelta(seconds=30)
MAX_STACK_LINES = 20
MAX_TIMELINE = 150
MAX_GROUPS = 50
MAX_REFS = 5

TEMPLATE_SUBS = [
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"), "<uuid>"),
    (re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b"), "<ip>"),
    (re.compile(r"\b(?=[0-9a-fA-F]*\d)[0-9a-fA-F]{8,}\b"), "<hex>"),
    (re.compile(r"\d+"), "<n>"),
]


def parse_ts(raw: str) -> datetime | None:
    """Parse an ISO-like timestamp; aware values become local naive time."""
    text = raw.strip().replace(",", ".").replace(" ", "T", 1)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    text = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", text)
    try:
        value = datetime.fromisoformat(text)
    except ValueError:
        return None
    if value.tzinfo is not None:
        value = value.astimezone().replace(tzinfo=None)
    return value


def template(msg: str) -> str:
    for pattern, repl in TEMPLATE_SUBS:
        msg = pattern.sub(repl, msg)
    return msg


def cut(line: str) -> str:
    return line if len(line) <= MAX_LINE_CHARS else line[:MAX_LINE_CHARS] + " ...[line cut]"


@dataclass
class Entry:
    label: str
    line_no: int
    header: str
    level: str
    ts_raw: str
    ts: datetime | None
    logger: str
    msg: str
    cont: list[tuple[int, str]] = field(default_factory=list)  # continuation lines (number, text)
    kept: list[tuple[int, str]] = field(default_factory=list)  # after stack collapse
    collapsed: int = 0
    correlated: bool = False

    @property
    def ref(self) -> str:
        return f"{self.label}:L{self.line_no}"

    def text(self) -> str:
        return "\n".join([self.header, *(t for _, t in self.cont)])

    def collapse(self) -> None:
        """Keep exception and `Caused by` lines plus the first frame after each."""
        kept: list[tuple[int, str]] = []
        want_frame = False
        for n, line in self.cont:
            if FRAME_RE.match(line):
                if want_frame and len(kept) < MAX_STACK_LINES:
                    kept.append((n, line))
                else:
                    self.collapsed += 1
                want_frame = False
            elif MORE_RE.match(line):
                self.collapsed += 1
            elif len(kept) < MAX_STACK_LINES:
                kept.append((n, line))
                want_frame = True
            else:
                self.collapsed += 1
        self.kept = kept
        self.cont = []  # free memory; only the collapsed form is used from here on

    def render(self) -> list[str]:
        lines = [f"{self.ref}| {cut(self.header)}"]
        lines += [f"{self.label}:L{n}| {cut(t)}" for n, t in self.kept]
        if self.collapsed:
            lines.append(f"    ... {self.collapsed} stack lines collapsed")
        return lines


@dataclass
class Filters:
    since: datetime | None = None
    until: datetime | None = None
    pattern: re.Pattern[str] | None = None
    correlation_id: str | None = None


@dataclass
class Group:
    level: str
    logger: str
    key: str
    count: int = 0
    first: Entry | None = None
    last_ts: str = ""
    refs: list[str] = field(default_factory=list)


@dataclass
class Digest:
    markdown: str
    files: dict[str, CitedFile]
    entries: int = 0
    levels: dict[str, int] = field(default_factory=dict)
    groups: int = 0
    timeline: int = 0
    duplicates: int = 0
    collapsed: int = 0
    input_chars: int = 0
    warnings: list[str] = field(default_factory=list)


def compile_pattern(raw: str | None) -> re.Pattern[str] | None:
    if not raw:
        return None
    try:
        return re.compile(raw, re.IGNORECASE)
    except re.error:
        return re.compile(re.escape(raw), re.IGNORECASE)


def read_entries(label: str, lines: Iterable[str], line_chars: list[int],
                 formats: Sequence[LogFormat] = ()) -> Iterable[Entry]:
    """Split a log into entries; a line that is not a header continues the previous entry."""
    patterns = [f.pattern for f in formats] + [GENERIC_RE]
    current: Entry | None = None
    for n, raw in enumerate(lines, start=1):
        line = raw.rstrip("\r\n")
        line_chars.append(len(line))
        m = next((hit for hit in (p.match(line) for p in patterns) if hit), None)
        if m:
            if current:
                yield current
            fields = m.groupdict()
            current = Entry(label=label, line_no=n, header=line, level=m.group("level").upper(),
                            ts_raw=m.group("ts"), ts=parse_ts(m.group("ts")), logger=fields.get("logger") or "",
                            msg=m.group("msg"))
        elif current is not None and line.strip():
            current.cont.append((n, line))
        # lines before the first header (e.g. "#### Log file written by ...") are skipped
    if current:
        yield current


def build_digest(paths: list[tuple[str, Path]], filters: Filters, formats: Sequence[LogFormat],
                 opener: Callable[[Path], BinaryIO]) -> Digest:
    files: dict[str, CitedFile] = {}
    corr = filters.correlation_id.lower() if filters.correlation_id else None
    correlated: list[Entry] = []
    problems: list[Entry] = []
    seen: set[tuple[str, str, str, str]] = set()
    duplicates = 0
    input_chars = 0

    for label, path in paths:
        line_chars: list[int] = []
        with opener(path) as raw_handle, TextIOWrapper(raw_handle, encoding="utf-8", errors="replace",
                                                       newline=None) as handle:
            for entry in read_entries(label, handle, line_chars, formats):
                if entry.ts is None and (filters.since or filters.until):
                    continue
                if entry.ts is not None:
                    if filters.since and entry.ts < filters.since:
                        continue
                    if filters.until and entry.ts > filters.until:
                        continue
                text = None
                if corr:
                    text = entry.text()
                    entry.correlated = corr in text.lower()
                if filters.pattern:
                    text = text or entry.text()
                    is_problem = bool(filters.pattern.search(text))
                else:
                    is_problem = entry.level in PROBLEM_LEVELS
                if not (entry.correlated or is_problem):
                    continue
                key = (entry.ts_raw, entry.level, entry.logger, entry.msg)
                if key in seen:
                    duplicates += 1
                    continue
                seen.add(key)
                entry.collapse()
                (correlated if entry.correlated else problems).append(entry)
        files[label] = CitedFile(total_lines=len(line_chars), line_chars=line_chars)
        input_chars += sum(line_chars) + len(line_chars)

    warnings: list[str] = []
    if corr:
        if correlated and not (filters.since or filters.until):
            times = [e.ts for e in correlated if e.ts]
            if times:
                lo, hi = min(times) - CORRELATION_SLACK, max(times) + CORRELATION_SLACK
                problems = [e for e in problems if e.ts and lo <= e.ts <= hi]
        elif not correlated:
            warnings.append(f"no line contains correlation id {filters.correlation_id!r}")
            problems = [] if not (filters.since or filters.until) else problems

    digest = Digest(markdown="", files=files, duplicates=duplicates, input_chars=input_chars,
                    warnings=warnings)
    order = {label: i for i, (label, _) in enumerate(paths)}

    def sort_key(e: Entry):
        return (e.ts or datetime.min, order[e.label], e.line_no)

    correlated.sort(key=sort_key)
    problems.sort(key=sort_key)

    groups: dict[tuple[str, str, str], Group] = {}
    for entry in problems:
        gkey = (entry.level, entry.logger, template(entry.msg))
        group = groups.get(gkey)
        if group is None:
            group = groups[gkey] = Group(level=entry.level, logger=entry.logger, key=gkey[2], first=entry)
        group.count += 1
        group.last_ts = entry.ts_raw
        if len(group.refs) < MAX_REFS:
            group.refs.append(entry.ref)

    all_kept = correlated + problems
    for e in all_kept:
        digest.levels[e.level] = digest.levels.get(e.level, 0) + 1
    digest.entries = len(all_kept)
    digest.collapsed = sum(e.collapsed for e in all_kept)
    digest.timeline = len(correlated)
    digest.groups = len(groups)

    ranked = sorted(groups.values(), key=lambda g: (g.level not in ("ERROR", "FATAL", "SEVERE"), -g.count))
    digest.markdown = _render(paths, files, filters, digest, correlated, ranked)
    if len(correlated) > MAX_TIMELINE:
        digest.warnings.append(f"timeline cut to {len(cap_timeline(correlated))} of {len(correlated)} entries "
                               "(every ERROR/WARN entry kept)")
    if len(ranked) > MAX_GROUPS:
        digest.warnings.append(f"only the top {MAX_GROUPS} of {len(ranked)} message groups are listed")
    return digest


def cap_timeline(timeline: list[Entry]) -> list[Entry]:
    """At most MAX_TIMELINE entries; ERROR/WARN entries are always kept, INFO fills the rest."""
    if len(timeline) <= MAX_TIMELINE:
        return timeline
    problems = sum(1 for e in timeline if e.level in PROBLEM_LEVELS)
    room = max(MAX_TIMELINE - problems, 0)
    shown = []
    for entry in timeline:
        if entry.level in PROBLEM_LEVELS:
            shown.append(entry)
        elif room:
            shown.append(entry)
            room -= 1
    return shown


def _render(paths, files, filters: Filters, digest: Digest, timeline: list[Entry], groups: list[Group]) -> str:
    out = ["# Log digest", ""]
    out.append("Lines below are verbatim from the log files (selected by code, not by a model). "
               "Each line starts with `path:Ln|`. Secrets are replaced with `<redacted:kind>`.")
    out.append("")
    out.append("- files: " + ", ".join(f"{label} ({files[label].total_lines} lines)" for label, _ in paths))
    shown = {
        "since": filters.since.isoformat(sep=" ") if filters.since else None,
        "until": filters.until.isoformat(sep=" ") if filters.until else None,
        "pattern": filters.pattern.pattern if filters.pattern else None,
        "correlation_id": filters.correlation_id,
    }
    out.append("- filters: " + (", ".join(f"{k}={v}" for k, v in shown.items() if v) or "none"))
    levels = ", ".join(f"{n} {lvl}" for lvl, n in sorted(digest.levels.items()))
    out.append(f"- kept: {digest.entries} entries ({levels or 'none'}); {digest.groups} message groups; "
               f"{digest.duplicates} duplicate entries dropped; {digest.collapsed} stack lines collapsed")
    if filters.correlation_id and not (filters.since or filters.until) and timeline:
        out.append("- ERROR/WARN entries are limited to the correlation window "
                   "(first to last line with the id, plus 30 s on each side)")
    out.append("")

    if filters.correlation_id:
        out.append(f"## Timeline for correlation id `{filters.correlation_id}` ({len(timeline)} entries)")
        out.append("")
        if timeline:
            out.append("```text")
            for entry in cap_timeline(timeline):
                out += entry.render()
            out.append("```")
        else:
            out.append("No line contains this correlation id.")
        out.append("")

    title = "pattern matches" if filters.pattern else "ERROR/WARN messages"
    out.append(f"## {title} grouped by template ({len(groups)} groups)")
    out.append("")
    if not groups:
        out.append("None.")
    for i, group in enumerate(groups[:MAX_GROUPS], start=1):
        first = group.first
        assert first is not None
        name = group.logger or "(no logger)"
        out.append(f"### {i}. {group.level} {name} - {group.count} times, "
                   f"first {first.ts_raw}, last {group.last_ts}")
        more = f" (+{group.count - len(group.refs)} more)" if group.count > len(group.refs) else ""
        out.append("Lines: " + ", ".join(group.refs) + more)
        out.append("")
        out.append("```text")
        out += first.render()
        out.append("```")
        out.append("")
    return "\n".join(out).rstrip() + "\n"
