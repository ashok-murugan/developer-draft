from pathlib import PurePath

import pytest

from task_offloader_agent.core.paths import PathError, PathGuard


@pytest.fixture
def guard(settings, profile):
    return PathGuard(settings, profile)


@pytest.mark.parametrize("rel", [
    ".env", "sub/.env.local", "projects/x/app-config/security/keys.txt", "a/b.keystore", "c.jks",
    "config.local.json", "private/lic.txt", ".git/config", "repo/.git/HEAD",
    "conf/db-secret.properties", "app/credentials.json",
])
def test_denylist(guard, rel):
    assert guard.denied_reason(PurePath(rel)) is not None


@pytest.mark.parametrize("rel", ["src/SecretRedactor.java", "logs/rest.log", "docs/credentials.md"])
def test_allowed(guard, rel):
    assert guard.denied_reason(PurePath(rel)) is None


def test_resolve_read(guard, write):
    write("src/A.java", "class A {}")
    write(".env", "X=1")
    assert guard.resolve_read("src/A.java").name == "A.java"
    assert guard.resolve_read("./src/../src/A.java").name == "A.java"
    with pytest.raises(PathError, match="denied"):
        guard.resolve_read(".env")
    with pytest.raises(PathError, match="not found"):
        guard.resolve_read("missing.txt")
    with pytest.raises(PathError, match="not a file"):
        guard.resolve_read("src")


def test_resolve_read_outside(guard, tmp_path_factory):
    other = tmp_path_factory.mktemp("other") / "x.txt"
    other.write_text("x")
    with pytest.raises(PathError, match="outside"):
        guard.resolve_read(str(other))
    with pytest.raises(PathError):
        guard.resolve_read("../" + other.parent.name + "/x.txt")


def test_write_allowlist(guard, settings):
    assert guard.ensure_run_path(settings.out_dir / "run" / "digest.md")
    with pytest.raises(PathError):
        guard.ensure_run_path(settings.root / "src" / "x.md")
    with pytest.raises(PathError):
        guard.ensure_run_path(settings.run_dir / ".." / "x.md")


@pytest.mark.parametrize("raw", ["NUL", "logs/CON.log", "a\x00b", "file.txt:stream"])
def test_special_names_rejected(guard, raw):
    with pytest.raises(PathError):
        guard.resolve_read(raw)


def test_denied_by_profile_beats_anywhere_rule(guard, write):
    write("deep/app-config/security/k.txt", "x")
    write("app-config/security/ok.txt", "x")
    with pytest.raises(PathError, match="denied"):
        guard.resolve_read("deep/app-config/security/k.txt")


def test_task_offloader_folder_denied_except_run_out(guard, write):
    write(".task-offloader/profile.toml", "x")
    with pytest.raises(PathError, match="denied"):
        guard.resolve_read(".task-offloader/profile.toml")
