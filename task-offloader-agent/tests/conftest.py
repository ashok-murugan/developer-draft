from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from task_offloader_agent.application.lifecycle import build_env
from task_offloader_agent.core.config import Config, load_config

from .support import FakeProvider

FIXTURE_PROFILE = Path(__file__).parent / "fixtures" / "profile.toml"
PROFILE_REL = ".task-offloader/profile.toml"


def make_workspace(root: Path, profile: Path = FIXTURE_PROFILE) -> Path:
    target = root / PROFILE_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(profile, target)
    return root


def make_config(root: Path, **env: str) -> Config:
    return load_config(workspace=str(root), profile=PROFILE_REL, env=env)


@pytest.fixture
def config(tmp_path: Path) -> Config:
    make_workspace(tmp_path)
    return make_config(tmp_path)


@pytest.fixture
def settings(config: Config):
    return config.settings


@pytest.fixture
def profile(config: Config):
    return config.profile


@pytest.fixture
def write(tmp_path: Path):
    def _write(rel: str, text: str) -> Path:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path
    return _write


@pytest.fixture
def env_for(config: Config, tmp_path: Path):
    def _make(replies, hold=None, **overrides):
        cfg = make_config(tmp_path, **overrides) if overrides else config
        return build_env(cfg, FakeProvider(replies, hold))
    return _make
