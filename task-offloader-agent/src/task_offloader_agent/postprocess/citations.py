"""Citation gate: every `path:Lx-Ly` must exist and span at most 40 lines."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath

MAX_SPAN = 40
REMOVED = "[invalid citation removed]"

CITATION_RE = re.compile(
    r"(?P<path>[A-Za-z0-9_.\-/\\]+?):L(?P<start>\d+)(?:\s*-\s*L?(?P<end>\d+))?\b"
)


@dataclass
class CitedFile:
    total_lines: int
    line_chars: list[int]


@dataclass
class CitationReport:
    answer: str
    citations: list[str] = field(default_factory=list)
    invalid: list[str] = field(default_factory=list)
    cited_chars: int = 0


def _resolve_label(raw: str, files: dict[str, CitedFile]) -> str | None:
    label = raw.replace("\\", "/").removeprefix("./")
    if label in files:
        return label
    # Accept a unique suffix such as "rest.log" for "logs/rest.log". The citation regex stops
    # at spaces, so a path with spaces in a folder name arrives as its tail after the space.
    matches = [f for f in files
               if f.endswith(("/" + label, " " + label)) or PurePosixPath(f).name == label]
    return matches[0] if len(matches) == 1 else None


def check_citations(answer: str, files: dict[str, CitedFile]) -> CitationReport:
    report = CitationReport(answer=answer)
    cited_lines: set[tuple[str, int]] = set()
    seen: set[str] = set()

    def _sub(match: re.Match[str]) -> str:
        raw = match.group(0)
        label = _resolve_label(match.group("path"), files)
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        info = files.get(label) if label else None
        if (info is None or start < 1 or end < start or end > info.total_lines
                or end - start + 1 > MAX_SPAN):
            report.invalid.append(raw)
            return REMOVED
        canonical = f"{label}:L{start}" if start == end else f"{label}:L{start}-L{end}"
        if canonical not in seen:
            seen.add(canonical)
            report.citations.append(canonical)
        for n in range(start, end + 1):
            cited_lines.add((label, n))
        return canonical

    report.answer = CITATION_RE.sub(_sub, answer)
    report.cited_chars = sum(files[label].line_chars[n - 1] for label, n in cited_lines
                             if n - 1 < len(files[label].line_chars))
    return report
