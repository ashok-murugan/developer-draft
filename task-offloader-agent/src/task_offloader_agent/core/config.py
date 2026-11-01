"""Runtime settings and configuration precedence.

For each overridable setting the first source wins: CLI argument, environment variable
`TASK_OFFLOADER_*`, profile value (only for keys a profile may set), built-in default.
An invalid value raises ConfigError; it is never replaced silently by the default (I7).
"""

from __future__ import annotations

import ipaddress
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .errors import ConfigError
from .profile import Profile, load_profile

PREFIX = "TASK_OFFLOADER_"
RUN_SUBDIR = Path(".task-offloader") / "run"
DEFAULT_PROVIDER_URL = "http://127.0.0.1:11434"
DEFAULT_NUM_CTX = 16384
MODES = ("auto", "manual", "off")


@dataclass(frozen=True)
class Settings:
    root: Path
    profile_path: Path
    default_mode: str
    model: str
    num_ctx: int
    tokenizer_file: Path | None
    provider_url: str
    timeout_s: float
    max_pending: int
    keep_alive: str
    chunk_tokens: int
    max_chunks: int
    retention_days: int

    @property
    def run_dir(self) -> Path:
        return self.root / RUN_SUBDIR

    @property
    def out_dir(self) -> Path:
        return self.run_dir / "out"

    @property
    def switch_file(self) -> Path:
        return self.run_dir / "switch.json"

    @property
    def audit_file(self) -> Path:
        return self.run_dir / "audit.jsonl"

    @property
    def lock_file(self) -> Path:
        return self.run_dir / "audit.lock"

    @property
    def log_file(self) -> Path:
        return self.run_dir / "activity.log"


@dataclass(frozen=True)
class Config:
    settings: Settings
    profile: Profile


def _number(env: Mapping[str, str], name: str, default: int, low: int, high: int) -> int:
    raw = env.get(PREFIX + name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw.strip())
    except ValueError:
        raise ConfigError(f"{PREFIX}{name}={raw!r} is not an integer") from None
    if not low <= value <= high:
        raise ConfigError(f"{PREFIX}{name}={value} is outside {low}-{high}")
    return value


def check_loopback(url: str) -> str:
    """The inference endpoint must be loopback (I6): the provider API has no authentication."""
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    try:
        loopback = host == "localhost" or ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = False
    if parts.scheme != "http" or not loopback:
        raise ConfigError(f"{PREFIX}PROVIDER_URL must be an http URL on a loopback address, got {url!r}")
    return url.rstrip("/")


def _workspace(raw: str | None) -> Path:
    if not raw:
        raise ConfigError("no workspace: pass --workspace or set TASK_OFFLOADER_WORKSPACE")
    try:
        root = Path(raw).resolve(strict=True)
    except (OSError, RuntimeError):
        raise ConfigError(f"workspace {raw!r} does not exist") from None
    if not root.is_dir():
        raise ConfigError(f"workspace {raw!r} is not a directory")
    return root


def _profile_path(raw: str | None, root: Path) -> Path:
    if not raw:
        raise ConfigError("no profile: pass --profile or set TASK_OFFLOADER_PROFILE")
    path = Path(raw)
    path = path if path.is_absolute() else root / path
    try:
        real = path.resolve(strict=True)
    except (OSError, RuntimeError):
        raise ConfigError(f"profile {raw!r} does not exist") from None
    if not real.is_file():
        raise ConfigError(f"profile {raw!r} is not a file")
    if not real.is_relative_to(root):
        raise ConfigError(f"profile {raw!r} is outside the workspace")
    return real


def load_config(*, workspace: str | None = None, profile: str | None = None, mode: str | None = None,
                env: Mapping[str, str] | None = None) -> Config:
    """Resolve every setting once. Raises ConfigError; the result is immutable."""
    env = os.environ if env is None else env
    root = _workspace(workspace or env.get(PREFIX + "WORKSPACE"))
    profile_file = _profile_path(profile or env.get(PREFIX + "PROFILE"), root)
    prof = load_profile(profile_file)

    model = (env.get(PREFIX + "MODEL") or "").strip() or prof.model
    num_ctx = _number(env, "NUM_CTX", prof.num_ctx or DEFAULT_NUM_CTX, 4096, 131072)
    chunk_tokens = _number(env, "CHUNK_TOKENS", min(12000, num_ctx - 2000), 500, 131072)
    if chunk_tokens > num_ctx - 2000:
        raise ConfigError(f"{PREFIX}CHUNK_TOKENS={chunk_tokens} does not fit num_ctx {num_ctx}")

    tokenizer = prof.tokenizer
    if env.get(PREFIX + "TOKENIZER"):
        tokenizer = Path(env[PREFIX + "TOKENIZER"])
        tokenizer = tokenizer if tokenizer.is_absolute() else profile_file.parent / tokenizer

    raw_mode = mode if mode is not None else env.get(PREFIX + "MODE", "auto")

    return Config(
        settings=Settings(
            root=root,
            profile_path=profile_file,
            default_mode=(raw_mode or "auto").strip().lower(),  # an unknown value means `off` (switch.py)
            model=model,
            num_ctx=num_ctx,
            tokenizer_file=tokenizer,
            provider_url=check_loopback(env.get(PREFIX + "PROVIDER_URL") or DEFAULT_PROVIDER_URL),
            timeout_s=float(_number(env, "TIMEOUT_S", 180, 10, 1800)),
            max_pending=_number(env, "MAX_PENDING", 3, 0, 16),
            keep_alive=(env.get(PREFIX + "KEEP_ALIVE") or "5m").strip(),
            chunk_tokens=chunk_tokens,
            max_chunks=_number(env, "MAX_CHUNKS", 4, 1, 20),
            retention_days=_number(env, "RETENTION_DAYS", 14, 1, 365),
        ),
        profile=prof,
    )
