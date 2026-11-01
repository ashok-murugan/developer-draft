"""Context budget: exact token counts, limits, chunking."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

TEMPLATE_RESERVE = 1500
MAX_LINE_CHARS = 2000  # one minified line must not fill a chunk on its own

# Output limit (num_predict) per call kind.
NUM_PREDICT = {
    "ask_chunk": 768,
    "ask_merge": 1024,
    "logs_narrative": 768,
}
DIGEST_NARRATIVE_CAP = 8000


def input_limit(num_ctx: int, num_predict: int) -> int:
    return num_ctx - num_predict - TEMPLATE_RESERVE


class TokenCounter:
    """Counts with the model's tokenizer; falls back to a conservative 3 chars/token."""

    def __init__(self, tokenizer_file: Path | None):
        self._tok = None
        self.kind = "estimate (3 chars per token)"
        if tokenizer_file and tokenizer_file.exists():
            try:
                from tokenizers import Tokenizer

                self._tok = Tokenizer.from_file(str(tokenizer_file))
                self.kind = f"exact ({tokenizer_file.name})"
            except Exception:  # noqa: BLE001 - any load failure means "estimate"
                self._tok = None

    def count(self, text: str) -> int:
        if self._tok is None:
            return math.ceil(len(text) / 3)
        return len(self._tok.encode(text, add_special_tokens=False).ids)

    def count_many(self, texts: list[str]) -> list[int]:
        if self._tok is None:
            return [math.ceil(len(t) / 3) for t in texts]
        return [len(e.ids) for e in self._tok.encode_batch(texts, add_special_tokens=False)]


@dataclass
class Source:
    """Input text for local_ask: a file (or part of it) or inline text."""

    label: str           # workspace-relative path, or "text"
    start: int           # number of the first line in `lines`
    lines: list[str]
    total_lines: int     # lines in the whole file, for citation checks
    line_chars: list[int]  # length of every line in the whole file, for cited_chars


def numbered(source: Source) -> list[str]:
    out = []
    for i, line in enumerate(source.lines):
        if len(line) > MAX_LINE_CHARS:
            line = line[:MAX_LINE_CHARS] + " ...[line cut]"
        out.append(f"L{source.start + i}| {line}")
    return out


def make_chunks(sources: list[Source], counter: TokenCounter, chunk_tokens: int) -> tuple[list[str], int]:
    """Split numbered lines into chunks of at most `chunk_tokens`, on line boundaries.

    Returns the chunks and the total token count of the numbered input.
    """
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    total = 0
    for source in sources:
        header = f"=== FILE: {source.label} ==="
        header_tokens = counter.count(header) + 1
        lines = numbered(source)
        counts = counter.count_many(lines) if lines else []
        need_header = True
        for line, tokens in zip(lines, counts):
            tokens += 1  # newline
            total += tokens
            extra = header_tokens if need_header else 0
            if current and current_tokens + tokens + extra > chunk_tokens:
                chunks.append("\n".join(current))
                current, current_tokens, need_header = [], 0, True
                extra = header_tokens
            if need_header:
                current.append(header)
                current_tokens += header_tokens
                need_header = False
            current.append(line)
            current_tokens += tokens
    if current:
        chunks.append("\n".join(current))
    return chunks, total
