from pathlib import Path

from task_offloader_agent.core.budget import MAX_LINE_CHARS, Source, TokenCounter, input_limit, make_chunks, numbered

WORKSPACE_TOKENIZER = Path(__file__).resolve().parents[3] / ".task-offloader" / "cache" / "tokenizer.json"


def _source(n: int, label: str = "a.txt") -> Source:
    lines = [f"line {i} " + "x" * 50 for i in range(1, n + 1)]
    return Source(label, 1, lines, n, [len(x) for x in lines])


def test_input_limit():
    assert input_limit(16384, 768) == 14116


def test_numbered_and_cut():
    src = Source("a", 10, ["x", "y" * (MAX_LINE_CHARS + 5)], 11, [1, MAX_LINE_CHARS + 5])
    out = numbered(src)
    assert out[0] == "L10| x"
    assert out[1].startswith("L11| ") and out[1].endswith("...[line cut]")


def test_chunks_respect_limit_and_lines():
    counter = TokenCounter(None)
    chunks, total = make_chunks([_source(300), _source(50, "b.txt")], counter, 2000)
    assert len(chunks) > 1
    assert all(counter.count(c) <= 2000 + 50 for c in chunks)  # small slack: count of joined text
    assert all(c.startswith("=== FILE: ") for c in chunks)
    joined = "\n".join(chunks)
    assert "L300| line 300" in joined and "=== FILE: b.txt ===" in joined
    assert total >= sum(counter.count(x) for x in numbered(_source(300)))


def test_exact_tokenizer_if_present():
    counter = TokenCounter(WORKSPACE_TOKENIZER)
    if WORKSPACE_TOKENIZER.exists():
        assert counter.kind.startswith("exact")
        assert 0 < counter.count("public class Foo { }") < 10
    else:
        assert counter.kind.startswith("estimate")
