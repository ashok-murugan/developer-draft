"""Prompt templates: generic defaults shipped as package data, optionally overridden by a profile."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from string import Template

PROMPT_NAMES = ("ask_system", "ask_chunk", "ask_merge", "logs_system", "logs_narrative")


class PromptSet:
    def __init__(self, override_dir: Path | None = None):
        self._override = override_dir
        self._cache: dict[str, Template] = {}

    def get(self, name: str) -> Template:
        if name not in PROMPT_NAMES:
            raise KeyError(name)
        if name not in self._cache:
            text = None
            if self._override is not None:
                candidate = self._override / f"{name}.txt"
                if candidate.is_file():
                    text = candidate.read_text(encoding="utf-8")
            if text is None:
                text = resources.files(__package__).joinpath(f"{name}.txt").read_text(encoding="utf-8")
            self._cache[name] = Template(text)
        return self._cache[name]
