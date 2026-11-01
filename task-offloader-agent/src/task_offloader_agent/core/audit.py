"""Audit log: one JSON line per call, apply or rating. Never prompt or response text.

Appends are serialised in-process by a lock and across processes by a lock file, and each event is
written with a single `write`, so concurrent servers and CLI calls cannot interleave lines (I8).
`write` raises OSError; callers decide whether that is fatal (read-only tools continue).
"""

from __future__ import annotations

import json
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import Settings

try:
    import msvcrt
except ImportError:  # POSIX
    msvcrt = None
    import fcntl

_thread_lock = threading.Lock()
LOCK_TIMEOUT_S = 5.0


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@contextmanager
def _file_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+b") as handle:
        fd = handle.fileno()
        if msvcrt is not None:
            deadline = time.monotonic() + LOCK_TIMEOUT_S
            while True:
                handle.seek(0)
                try:
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.02)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)


def log(settings: Settings, message: str) -> None:
    """One readable line in activity.log and on stderr (shown in VS Code's MCP output).
    Best effort and never stdout, which carries the MCP protocol."""
    line = f"{now_iso()} {message}"
    print(f"task-offloader: {line}", file=sys.stderr, flush=True)
    try:
        settings.run_dir.mkdir(parents=True, exist_ok=True)
        _rotate_if_needed(settings.log_file, _LOG_MAX_BYTES)
        with _thread_lock, open(settings.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def _summary(event: dict[str, Any]) -> str:
    parts = [str(event.get("tool", event.get("event"))), str(event.get("status", ""))]
    for key in ("reason", "run_id", "duration_ms", "files_in", "input_tokens", "output_tokens"):
        if key in event:
            parts.append(f"{key}={event[key]}")
    return " ".join(p for p in parts if p)


_AUDIT_MAX_BYTES  = 10 * 1024 * 1024   # 10 MB
_LOG_MAX_BYTES    =  5 * 1024 * 1024   #  5 MB


def _rotate_if_needed(path: Path, max_bytes: int) -> None:
    """Rename path -> path.1 when it exceeds max_bytes. Best effort; never raises."""
    try:
        if path.exists() and path.stat().st_size > max_bytes:
            backup = path.with_suffix(path.suffix + ".1")
            if backup.exists():
                backup.unlink(missing_ok=True)
            path.rename(backup)
    except OSError:
        pass

def write(settings: Settings, event: dict[str, Any]) -> None:
    """Append one event. Raises OSError if the audit file cannot be written."""
    line = json.dumps({"ts": now_iso(), **event}, ensure_ascii=False) + "\n"
    data = line.encode("utf-8")
    settings.run_dir.mkdir(parents=True, exist_ok=True)
    _rotate_if_needed(settings.audit_file, _AUDIT_MAX_BYTES)
    with _thread_lock, _file_lock(settings.lock_file):
        with open(settings.audit_file, "ab", buffering=0) as f:
            f.write(data)
    if event.get("event") == "call":
        log(settings, "END   " + _summary(event))


def read_all(settings: Settings) -> list[dict[str, Any]]:
    if not settings.audit_file.exists():
        return []
    events = []
    for line in settings.audit_file.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events
