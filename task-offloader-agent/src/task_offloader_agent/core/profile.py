"""Workspace profile, schema v1: validated once at startup, immutable afterwards.

A profile is data. It holds no code, imports or commands (I9). Every unknown key is rejected, because a
typo in a deny rule must not silently leave a path readable.
"""

from __future__ import annotations

import hashlib
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from ..prompts import PROMPT_NAMES
from .errors import ConfigError

SUPPORTED_SCHEMA_VERSIONS = (1,)
LOG_FORMAT_GROUPS = ("level", "ts", "msg")


@dataclass(frozen=True)
class PathRule:
    """A workspace-relative path rule. `**/a/b` matches the segments anywhere; `a/b` only at the root."""

    raw: str
    parts: tuple[str, ...]
    anywhere: bool

    def matches(self, parts: tuple[str, ...]) -> bool:
        """True if the path equals the rule or lies below it (`parts` are already lower-cased)."""
        n = len(self.parts)
        if not self.anywhere:
            return parts[:n] == self.parts
        return any(parts[i:i + n] == self.parts for i in range(len(parts) - n + 1))

    def contains(self, parts: tuple[str, ...]) -> bool:
        """True if the path lies strictly below the rule (the rule names a folder)."""
        return len(parts) > len(self.parts) and self.matches(parts)


@dataclass(frozen=True)
class RedactionRule:
    kind: str
    pattern: re.Pattern[str]
    keep_prefix: bool


@dataclass(frozen=True)
class LogFormat:
    name: str
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class Profile:
    name: str
    schema_version: int
    path: Path
    sha256: str
    deny_paths: tuple[PathRule, ...]
    deny_names: tuple[str, ...]
    redaction_rules: tuple[RedactionRule, ...]
    log_dirs: tuple[PathRule, ...]
    log_max_files: int
    log_formats: tuple[LogFormat, ...]
    prompts_dir: Path | None
    model: str
    num_ctx: int | None
    tokenizer: Path | None

    @property
    def log_dir_labels(self) -> str:
        return ", ".join(rule.raw.removeprefix("**/") + "/" for rule in self.log_dirs)


def parse_path_rule(raw: str) -> PathRule:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("path rule must be a non-empty string")
    text = raw.strip()
    anywhere = text.startswith("**/")
    body = text[3:] if anywhere else text
    if "\\" in body or body.startswith("/") or re.match(r"^[A-Za-z]:", body) or "\0" in body:
        raise ValueError(f"{raw!r}: use a workspace-relative path with '/' separators")
    parts = tuple(body.lower().split("/"))
    if any(p in ("", ".", "..") or "*" in p or "?" in p for p in parts):
        raise ValueError(f"{raw!r}: empty, '.', '..' and wildcard segments are not allowed")
    return PathRule(raw=text, parts=parts, anywhere=anywhere)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _Meta(_Strict):
    name: str = Field(pattern=r"^[a-z0-9-]{1,64}$")
    schema_version: int


class _Security(_Strict):
    deny_paths: list[str] = []
    deny_names: list[str] = []

    @field_validator("deny_paths")
    @classmethod
    def _paths(cls, value: list[str]) -> list[str]:
        for raw in value:
            parse_path_rule(raw)
        return value

    @field_validator("deny_names")
    @classmethod
    def _names(cls, value: list[str]) -> list[str]:
        for raw in value:
            if not raw.strip() or "/" in raw or "\\" in raw:
                raise ValueError(f"{raw!r}: give a file name or a glob without folders")
        return value


class _Rule(_Strict):
    kind: str = Field(pattern=r"^[a-z0-9-]+$")
    pattern: str
    keep_prefix: bool = False

    @model_validator(mode="after")
    def _compiles(self) -> "_Rule":
        try:
            compiled = re.compile(self.pattern)
        except re.error as exc:
            raise ValueError(f"pattern does not compile: {exc}") from None
        if self.keep_prefix and compiled.groups < 1:
            raise ValueError("keep_prefix = true needs a capture group 1 in the pattern")
        return self


class _Redaction(_Strict):
    rules: list[_Rule] = []


class _Format(_Strict):
    name: str = Field(pattern=r"^[A-Za-z0-9_-]{1,32}$")
    pattern: str

    @model_validator(mode="after")
    def _compiles(self) -> "_Format":
        try:
            compiled = re.compile(self.pattern)
        except re.error as exc:
            raise ValueError(f"pattern does not compile: {exc}") from None
        missing = [g for g in LOG_FORMAT_GROUPS if g not in compiled.groupindex]
        if missing:
            raise ValueError("pattern lacks the named group(s): " + ", ".join(missing))
        return self


class _Logs(_Strict):
    allowed_dirs: list[str] = []
    max_files: int = Field(default=10, ge=1, le=50)
    formats: list[_Format] = []

    @field_validator("allowed_dirs")
    @classmethod
    def _dirs(cls, value: list[str]) -> list[str]:
        for raw in value:
            parse_path_rule(raw)
        return value

    @field_validator("formats")
    @classmethod
    def _unique(cls, value: list[_Format]) -> list[_Format]:
        names = [f.name for f in value]
        if len(set(names)) != len(names):
            raise ValueError("format names must be unique")
        return value


class _Prompts(_Strict):
    override_dir: str | None = None


class _Inference(_Strict):
    provider: Literal["ollama"]
    model: str = Field(min_length=1)
    num_ctx: int | None = Field(default=None, ge=4096, le=131072)
    tokenizer: str | None = None


class _ProfileFile(_Strict):
    profile: _Meta
    inference: _Inference
    security: _Security = _Security()
    redaction: _Redaction = _Redaction()
    logs: _Logs = _Logs()
    prompts: _Prompts = _Prompts()


def _describe(exc: ValidationError) -> str:
    items = []
    for err in exc.errors(include_input=False, include_url=False):
        where = ".".join(str(p) for p in err["loc"]) or "(top level)"
        items.append(f"{where}: {err['msg']}")
    return "; ".join(items)


def _prompts_dir(raw: str | None, base: Path, name: str) -> Path | None:
    if raw is None:
        return None
    rel = Path(raw)
    if rel.is_absolute() or ".." in rel.parts:
        raise ConfigError(f"profile {name}: prompts.override_dir must be a folder below the profile's folder")
    folder = (base / rel).resolve()
    if not folder.is_dir() or not folder.is_relative_to(base.resolve()):
        raise ConfigError(f"profile {name}: prompts.override_dir {raw!r} is not a folder below the profile's folder")
    allowed = {f"{n}.txt" for n in PROMPT_NAMES}
    unknown = sorted(p.name for p in folder.iterdir() if p.is_file() and p.name not in allowed)
    if unknown:
        raise ConfigError(f"profile {name}: prompts.override_dir has unknown file(s): {', '.join(unknown)}")
    return folder


def load_profile(path: Path) -> Profile:
    """Read, validate and compile a profile. Raises ConfigError naming the file, key and rule."""
    name = path.name
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ConfigError(f"profile {name}: cannot be read ({exc.__class__.__name__})") from None
    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise ConfigError(f"profile {name}: not valid TOML ({exc})") from None
    try:
        parsed = _ProfileFile.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"profile {name}: {_describe(exc)}") from None
    if parsed.profile.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ConfigError(f"profile {name}: profile.schema_version {parsed.profile.schema_version} is not "
                          f"supported (supported: {', '.join(map(str, SUPPORTED_SCHEMA_VERSIONS))})")

    base = path.resolve().parent
    tokenizer = None
    if parsed.inference.tokenizer:
        tokenizer = Path(parsed.inference.tokenizer)
        tokenizer = tokenizer if tokenizer.is_absolute() else base / tokenizer
    return Profile(
        name=parsed.profile.name,
        schema_version=parsed.profile.schema_version,
        path=path.resolve(),
        sha256=hashlib.sha256(raw).hexdigest(),
        deny_paths=tuple(parse_path_rule(p) for p in parsed.security.deny_paths),
        deny_names=tuple(n.lower() for n in parsed.security.deny_names),
        redaction_rules=tuple(RedactionRule(r.kind, re.compile(r.pattern), r.keep_prefix)
                              for r in parsed.redaction.rules),
        log_dirs=tuple(parse_path_rule(p) for p in parsed.logs.allowed_dirs),
        log_max_files=parsed.logs.max_files,
        log_formats=tuple(LogFormat(f.name, re.compile(f.pattern)) for f in parsed.logs.formats),
        prompts_dir=_prompts_dir(parsed.prompts.override_dir, base, name),
        model=parsed.inference.model,
        num_ctx=parsed.inference.num_ctx,
        tokenizer=tokenizer,
    )
