"""Redaction before anything is returned to the primary agent."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable

from .profile import Profile

_VALUE = r"[^\s,;\"'<>]+"

# (kind, pattern, keep_prefix). Order matters: Bearer before the generic Authorization rule.
_RULES: list[tuple[str, re.Pattern[str], bool]] = [
    ("bearer", re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9\-._~+/]{8,}=*"), True),
    ("authorization", re.compile(
        r"(?i)\b(authorization[\"']?\s*[:=]\s*[\"']?)(?!bearer\s)(?!<redacted)(?:basic\s+)?" + _VALUE), True),
    ("cookie", re.compile(r"(?i)\b((?:set-)?cookie[\"']?\s*[:=]\s*)[^\r\n]+"), True),
    ("jsessionid", re.compile(r"(?i)\b(JSESSIONID=)[^;\s\"',]+"), True),
    ("csrf", re.compile(r"(?i)\b(x-csrf-token[\"']?\s*[:=]\s*[\"']?)" + _VALUE), True),
    ("token", re.compile(r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]*"), False),
    ("password", re.compile(r"(?i)([;?&]password=)[^;&\s\"']+"), True),
    ("password", re.compile(r"(?i)\b((?:password|passwd|pwd)[\"']?\s*[:=]\s*[\"']?)" + _VALUE), True),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), False),
]


class Redactor:
    """Built-in rules first, then the profile's rules (a profile can add rules, never remove one)."""

    def __init__(self, extra: Iterable[tuple[str, re.Pattern[str], bool]] = ()):
        self._rules = [*_RULES, *extra]

    def redact(self, text: str) -> tuple[str, Counter[str]]:
        counts: Counter[str] = Counter()
        for kind, pattern, keep_prefix in self._rules:
            placeholder = f"<redacted:{kind}>"

            def _sub(match: re.Match[str], kind: str = kind, placeholder: str = placeholder,
                     keep_prefix: bool = keep_prefix) -> str:
                if placeholder in match.group(0):
                    return match.group(0)
                counts[kind] += 1
                return (match.group(1) if keep_prefix else "") + placeholder

            text = pattern.sub(_sub, text)
        return text, counts

    def redact_text(self, text: str) -> str:
        return self.redact(text)[0]


def redactor_for(profile: Profile) -> Redactor:
    return Redactor((r.kind, r.pattern, r.keep_prefix) for r in profile.redaction_rules)
