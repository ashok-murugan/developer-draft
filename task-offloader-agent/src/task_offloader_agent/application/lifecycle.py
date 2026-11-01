"""Startup and shutdown: configuration, runtime objects, audit, retention."""

from __future__ import annotations

import sys
from collections.abc import Mapping
from dataclasses import dataclass

from .. import __version__
from ..core import audit, retention
from ..core.budget import TokenCounter
from ..core.config import Config, load_config
from ..core.errors import ConfigError, ConfigFailure
from ..core.paths import PathGuard
from ..core.redact import redactor_for
from ..prompts import PromptSet
from ..providers.base import InferenceProvider
from ..providers.ollama import OllamaProvider
from .gate import Gate
from .runner import Env, try_audit


@dataclass
class Runtime:
    """Either a ready environment or the reason there is none (config-error mode)."""

    env: Env | None = None
    failure: ConfigFailure | None = None

    @property
    def target(self) -> Env | ConfigFailure:
        assert self.env is not None or self.failure is not None
        return self.env if self.env is not None else self.failure  # type: ignore[return-value]


def build_env(config: Config, provider: InferenceProvider | None = None) -> Env:
    settings, profile = config.settings, config.profile
    return Env(
        settings=settings,
        profile=profile,
        guard=PathGuard(settings, profile),
        provider=provider or OllamaProvider(settings),
        gate=Gate(settings.max_pending),
        counter=TokenCounter(settings.tokenizer_file),
        prompts=PromptSet(profile.prompts_dir),
        redactor=redactor_for(profile),
    )


def start(*, workspace: str | None = None, profile: str | None = None, mode: str | None = None,
          environ: Mapping[str, str] | None = None, provider: InferenceProvider | None = None,
          run_retention: bool = True) -> Runtime:
    """Load and validate the configuration. A failure does not raise: the server stays up and every tool
    reports `config_error` (invariant I7), so the developer sees the cause instead of a dead server."""
    try:
        config = load_config(workspace=workspace, profile=profile, mode=mode, env=environ)
    except ConfigError as exc:
        print(f"task-offloader: configuration error: {exc}", file=sys.stderr, flush=True)
        return Runtime(failure=ConfigFailure(str(exc)))

    env = build_env(config, provider)
    settings = env.settings
    try_audit(settings, {"event": "startup", "profile": env.profile.name, "schema_version": env.profile.schema_version,
                         "profile_sha256": env.profile.sha256, "version": __version__})
    audit.log(settings, f"START server profile={env.profile.name} model={settings.model} "
                        f"tokenizer={env.counter.kind}")
    if run_retention:
        run_retention_cleanup(env)
    return Runtime(env=env)


def run_retention_cleanup(env: Env) -> None:
    """Never blocks startup: any failure is logged and the server carries on."""
    try:
        removed, errors = retention.clean(env.settings)
    except Exception as exc:  # noqa: BLE001
        audit.log(env.settings, f"retention failed: {exc.__class__.__name__}")
        return
    if removed or errors:
        try_audit(env.settings, {"event": "retention", "removed": len(removed), "errors": errors})
        audit.log(env.settings, f"retention removed {len(removed)} old run(s), {errors} error(s)")


def shutdown(runtime: Runtime) -> None:
    if runtime.env is not None:
        runtime.env.gate.close()
