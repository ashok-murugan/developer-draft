"""Deletes run folders older than the retention period."""

from __future__ import annotations

import shutil
import time

from .config import Settings


def clean(settings: Settings, days: int | None = None) -> tuple[list[str], int]:
    """Remove run folders whose last change is older than `days`.

    Returns the removed run ids and the number of folders that could not be removed.
    Folders that are links are never followed or removed.
    """
    days = settings.retention_days if days is None else days
    out = settings.out_dir
    if not out.is_dir():
        return [], 0
    out_real = out.resolve()
    cutoff = time.time() - days * 86400
    removed: list[str] = []
    errors = 0
    for run in sorted(out.iterdir()):
        try:
            if not run.is_dir() or run.is_symlink():
                continue
            real = run.resolve()
            if real.parent != out_real:
                continue
            newest = max([real.stat().st_mtime] + [p.stat().st_mtime for p in real.rglob("*")])
            if newest < cutoff:
                shutil.rmtree(real)
                removed.append(run.name)
        except OSError:
            errors += 1
    return removed, errors
