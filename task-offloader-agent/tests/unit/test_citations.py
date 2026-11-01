from task_offloader_agent.postprocess.citations import REMOVED, CitedFile, check_citations

FILES = {
    "logs/rest.log": CitedFile(100, [10] * 100),
    ".github/copilot-instructions.md": CitedFile(20, [5] * 20),
    "src/A.java": CitedFile(50, [4] * 50),
}


def test_valid_and_canonical():
    report = check_citations("Fails at (rest.log:L5-L7) and src/A.java:L3; see ./.github/copilot-instructions.md:L2.",
                             FILES)
    assert report.citations == ["logs/rest.log:L5-L7", "src/A.java:L3", ".github/copilot-instructions.md:L2"]
    assert not report.invalid
    assert report.cited_chars == 3 * 10 + 4 + 5


def test_invalid_removed():
    answer = "a (logs/rest.log:L90-L140) b (other.log:L1) c (src/A.java:L60) d (src/A.java:L9-L3)"
    report = check_citations(answer, FILES)
    assert report.citations == []
    assert len(report.invalid) == 4
    assert report.answer.count(REMOVED) == 4


def test_windows_separators_and_dedupe():
    report = check_citations(r"x src\A.java:L1-L2 y src/A.java:L1-2", FILES)
    assert report.citations == ["src/A.java:L1-L2"]
    assert report.cited_chars == 8
