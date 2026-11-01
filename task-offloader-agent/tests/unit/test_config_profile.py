from pathlib import Path

import pytest

from task_offloader_agent.core.errors import ConfigError
from task_offloader_agent.core.profile import load_profile

from ..conftest import FIXTURE_PROFILE, PROFILE_REL, make_config, make_workspace

EXAMPLE_PROFILE = Path(__file__).resolve().parents[2] / "profiles" / "example" / "profile.toml"


INFERENCE = '[inference]\nprovider = "ollama"\nmodel = "m"\n'


def _profile(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "p.toml"
    path.write_text('[profile]\nname = "t"\nschema_version = 1\n' + INFERENCE + body, encoding="utf-8")
    return path


def test_defaults(config):
    s = config.settings
    assert (s.num_ctx, s.chunk_tokens, s.max_chunks, s.max_pending, s.retention_days) == (16384, 12000, 4, 3, 14)
    assert s.provider_url == "http://127.0.0.1:11434"
    assert s.run_dir == s.root / ".task-offloader" / "run"


def test_env_overrides_profile(tmp_path):
    make_workspace(tmp_path)
    s = make_config(tmp_path, TASK_OFFLOADER_MODEL="other", TASK_OFFLOADER_NUM_CTX="8192").settings
    assert s.model == "other" and s.num_ctx == 8192 and s.chunk_tokens == 6192


@pytest.mark.parametrize("name, value", [
    ("NUM_CTX", "100"), ("NUM_CTX", "abc"), ("CHUNK_TOKENS", "16000"), ("MAX_CHUNKS", "0"),
    ("TIMEOUT_S", "5"), ("MAX_PENDING", "99"), ("PROVIDER_URL", "http://example.com:11434"),
    ("PROVIDER_URL", "https://127.0.0.1:11434"),
])
def test_invalid_values_are_rejected_not_defaulted(tmp_path, name, value):
    make_workspace(tmp_path)
    with pytest.raises(ConfigError):
        make_config(tmp_path, **{f"TASK_OFFLOADER_{name}": value})


@pytest.mark.parametrize("url", ["http://localhost:11434", "http://[::1]:11434", "http://127.0.0.2:1"])
def test_loopback_urls_accepted(tmp_path, url):
    make_workspace(tmp_path)
    assert make_config(tmp_path, TASK_OFFLOADER_PROVIDER_URL=url).settings.provider_url == url


def test_workspace_and_profile_required(tmp_path):
    with pytest.raises(ConfigError, match="no workspace"):
        load_config_none()
    with pytest.raises(ConfigError, match="no profile"):
        from task_offloader_agent.core.config import load_config
        load_config(workspace=str(tmp_path), env={})


def load_config_none():
    from task_offloader_agent.core.config import load_config
    return load_config(env={})


def test_profile_must_be_inside_workspace(tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "profile.toml"
    outside.write_text(FIXTURE_PROFILE.read_text(encoding="utf-8"), encoding="utf-8")
    workspace = tmp_path_factory.mktemp("ws")
    from task_offloader_agent.core.config import load_config
    with pytest.raises(ConfigError, match="outside the workspace"):
        load_config(workspace=str(workspace), profile=str(outside), env={})


def test_example_profile_loads(tmp_path):
    make_workspace(tmp_path, EXAMPLE_PROFILE)
    config = make_config(tmp_path)
    assert config.profile.name == "example"


def test_profile_hash_changes_with_content(tmp_path):
    a = load_profile(_profile(tmp_path, ""))
    b = load_profile(_profile(tmp_path, "[security]\ndeny_paths = [\"x\"]\n"))
    assert a.sha256 != b.sha256 and len(a.sha256) == 64


@pytest.mark.parametrize("body, text", [
    ("[unknown]\nx = 1\n", "unknown"),
    ("[security]\ndeny_paths = [\"../x\"]\n", "not allowed"),
    ("[security]\ndeny_paths = [\"a/*\"]\n", "wildcard"),
    ("[security]\ndeny_names = [\"a/b\"]\n", "folders"),
    ('[redaction]\nrules = [{ kind = "k", pattern = "(" }]\n', "compile"),
    ('[redaction]\nrules = [{ kind = "k", pattern = "x", keep_prefix = true }]\n', "capture group 1"),
    ('[logs]\nallowed_dirs = ["logs"]\n[[logs.formats]]\nname = "f"\npattern = "(?P<level>x)"\n', "named group"),
])
def test_invalid_profiles(tmp_path, body, text):
    with pytest.raises(ConfigError, match=text):
        load_profile(_profile(tmp_path, body))


def test_future_schema_rejected(tmp_path):
    path = tmp_path / "p.toml"
    path.write_text('[profile]\nname = "t"\nschema_version = 99\n' + INFERENCE, encoding="utf-8")
    with pytest.raises(ConfigError, match="schema_version"):
        load_profile(path)


def test_anywhere_rule_anchoring(profile):
    rule = next(r for r in profile.deny_paths if r.raw.endswith("app-config/security"))
    assert rule.matches(("a", "b", "app-config", "security", "k"))
    assert rule.matches(("app-config", "security"))
    root_rule = next(r for r in profile.deny_paths if r.raw == "private")
    assert root_rule.matches(("private", "x"))
    assert not root_rule.matches(("sub", "private", "x"))


def test_prompt_override_unknown_file(tmp_path):
    folder = tmp_path / "prompts"
    folder.mkdir()
    (folder / "nonsense.txt").write_text("x", encoding="utf-8")
    path = _profile(tmp_path, '[prompts]\noverride_dir = "prompts"\n')
    with pytest.raises(ConfigError, match="unknown file"):
        load_profile(path)


def test_prompt_override_must_stay_below_profile(tmp_path):
    path = _profile(tmp_path, '[prompts]\noverride_dir = "../x"\n')
    with pytest.raises(ConfigError, match="below the profile"):
        load_profile(path)


def test_profile_rel_constant():
    assert PROFILE_REL == ".task-offloader/profile.toml"


def test_every_prompt_name_has_a_packaged_file():
    from task_offloader_agent.prompts import PROMPT_NAMES, PromptSet
    prompts = PromptSet(None)
    for name in PROMPT_NAMES:
        assert prompts.get(name).template
