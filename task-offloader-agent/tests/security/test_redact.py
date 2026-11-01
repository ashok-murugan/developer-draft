import pytest

from pathlib import Path

from task_offloader_agent.core.profile import load_profile
from task_offloader_agent.core.redact import redactor_for

_REDACTOR = redactor_for(load_profile(Path(__file__).resolve().parents[1] / "fixtures" / "profile.toml"))


def redact(text):
    return _REDACTOR.redact(text)

SECRET = "abcDEF123456ghiJKL789"


@pytest.mark.parametrize("text, kind", [
    (f"Authorization: Bearer {SECRET}", "bearer"),
    (f"authorization=Basic {SECRET}", "authorization"),
    (f"Cookie: JSESSIONID={SECRET}; other=1", "cookie"),
    (f"url;JSESSIONID={SECRET}", "jsessionid"),
    (f"X-CSRF-TOKEN: {SECRET}", "csrf"),
    (f"MY_APP_API_KEY={SECRET}", "api-key"),
    (f'"app_token": "{SECRET}"', "app-token"),
    ("token eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.sig_part-123", "token"),
    (f"jdbc:sqlserver://h;user=sa;password={SECRET};db=x", "password"),
    (f"password: {SECRET}", "password"),
    ("contact user@example.com now", "email"),
])
def test_redacts(text, kind):
    out, counts = redact(text)
    assert counts[kind] >= 1, out
    assert SECRET not in out and "user@example.com" not in out
    assert f"<redacted:{kind}>" in out


def test_keeps_normal_text():
    text = "ERROR (2026-05-11T08:55:58,985+0530) [main] Foo:19 - Connection refused: getsockopt"
    assert redact(text) == (text, {})


def test_idempotent():
    once, _ = redact(f"Authorization: Bearer {SECRET}")
    twice, counts = redact(once)
    assert once == twice and not counts
