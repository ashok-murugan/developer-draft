"""Path guard: read only inside the workspace, never denylisted files.

Every file a task reads goes through `resolve_read` and then `open_checked`. Both are needed:
resolving checks the path, opening re-checks that the opened file is the one that was checked (I2).
"""

from __future__ import annotations

import fnmatch
import os
import stat
from pathlib import Path, PurePath
from typing import BinaryIO

from .config import Settings
from .profile import PathRule, Profile

# `*secret*` / `*credential*` apply only to configuration and data files, so
# source files such as SecretRedactor.java stay readable.
CONFIG_SUFFIXES = {".properties", ".yml", ".yaml", ".json", ".env", ".txt", ".xml"}
KEY_SUFFIXES = (".keystore", ".jks", ".p12", ".pfx", ".pem")
KEY_PREFIXES = ("id_rsa", "id_dsa", "id_ecdsa", "id_ed25519")
WRAPPER_DIR = ".task-offloader"
READABLE_WRAPPER = (WRAPPER_DIR, "run", "out")
DEVICE_NAMES = {"con", "prn", "aux", "nul", "conin$", "conout$",
                *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}


class PathError(ValueError):
    pass


class PathGuard:
    def __init__(self, settings: Settings, profile: Profile):
        self.settings = settings
        self.profile = profile
        self.root = settings.root

    def denied_reason(self, rel: PurePath) -> str | None:
        parts = tuple(p.lower() for p in rel.parts)
        if not parts:
            return "workspace root"
        name = parts[-1]
        if ".git" in parts:
            return ".git"
        if parts[0] == WRAPPER_DIR and parts[:3] != READABLE_WRAPPER:
            return WRAPPER_DIR
        if name == ".env" or name.startswith(".env."):
            return ".env"
        if name.endswith(KEY_SUFFIXES):
            return "key or keystore file"
        if name.startswith(KEY_PREFIXES):
            return "private key file"
        if ("secret" in name or "credential" in name) and (
            PurePath(name).suffix in CONFIG_SUFFIXES or name.startswith(".env")
        ):
            return "secret/credential file"
        for rule in self.profile.deny_paths:
            if rule.matches(parts):
                return rule.raw
        for pattern in self.profile.deny_names:
            if fnmatch.fnmatchcase(name, pattern):
                return pattern
        return None

    def resolve_read(self, raw: str, under: tuple[PathRule, ...] | None = None,
                     under_label: str = "") -> Path:
        """Resolve a path from the primary agent (workspace-relative or absolute) for reading.

        With `under`, the file must also lie below one of those folders (the logs scope).
        """
        raw = raw.strip().strip('"')
        if not raw:
            raise PathError("empty path")
        if "\0" in raw:
            raise PathError("invalid path")
        self._reject_special(raw)
        path = Path(raw)
        if not path.is_absolute():
            path = self.root / path
        try:
            real = path.resolve(strict=True)  # follows links and removes ".."
        except (OSError, RuntimeError):
            raise PathError(f"not found: {raw}") from None
        if not real.is_relative_to(self.root):
            raise PathError(f"outside the workspace: {raw}")
        rel = real.relative_to(self.root)
        reason = self.denied_reason(rel)
        if reason:
            raise PathError(f"denied ({reason}): {rel.as_posix()}")
        if under is not None:
            lowered = tuple(p.lower() for p in rel.parts)
            if not any(rule.contains(lowered) for rule in under):
                raise PathError(f"only files under {under_label} are accepted: {rel.as_posix()}")
        if not real.is_file():
            raise PathError(f"not a file: {rel.as_posix()}")
        return real

    def open_checked(self, real: Path) -> BinaryIO:
        """Open a path returned by resolve_read and confirm it is still the same, allowed, regular file."""
        try:
            before = os.stat(real)
            handle = open(real, "rb")
        except OSError:
            raise PathError(f"cannot open: {self.label(real)}") from None
        try:
            after = os.fstat(handle.fileno())
            same_file = after.st_ino == 0 or (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
            if not stat.S_ISREG(after.st_mode) or not same_file:
                raise PathError(f"file changed while opening: {self.label(real)}")
            try:
                again = real.resolve(strict=True)
            except (OSError, RuntimeError):
                raise PathError(f"file changed while opening: {self.label(real)}") from None
            if again != real or self.denied_reason(again.relative_to(self.root)):
                raise PathError(f"file changed while opening: {self.label(real)}")
        except BaseException:
            handle.close()
            raise
        return handle

    def label(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.name

    def ensure_run_path(self, path: Path) -> Path:
        """Write allowlist: the service writes only under .task-offloader/run/."""
        real = path.resolve()
        if not real.is_relative_to(self.settings.run_dir.resolve()):
            raise PathError(f"write outside .task-offloader/run/ refused: {path}")
        return real

    @staticmethod
    def _reject_special(raw: str) -> None:
        if os.name == "nt":
            body = raw[2:] if len(raw) > 1 and raw[1] == ":" else raw
            if ":" in body:
                raise PathError(f"invalid path: {raw}")  # alternate data stream
            if raw.startswith(("\\\\.\\", "\\\\?\\GLOBALROOT")):
                raise PathError(f"invalid path: {raw}")
        for part in raw.replace("\\", "/").split("/"):
            stem = part.split(".", 1)[0].strip().lower()
            if stem in DEVICE_NAMES:
                raise PathError(f"invalid path: {raw}")
