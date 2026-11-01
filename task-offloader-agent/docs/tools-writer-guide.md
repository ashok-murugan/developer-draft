# Tools Writer Guide

This guide explains how to add a new MCP tool to TaskOffloaderAgent.

The three built-in tools — `local_status`, `local_ask`, and `summarize_logs` — are called by
the **cloud model** (Claude, Copilot, Gemini, etc.) via the MCP protocol.
TaskOffloaderAgent handles security, redaction, and routing to the local Ollama model,
then returns a structured result the cloud model uses to continue its plan.

```
Cloud model  ──MCP call──►  TaskOffloaderAgent  ──►  local Ollama model
                                 │
                                 │  path guard + redaction (always)
                                 │  gate (concurrency)
                                 │  switch check (on/off/manual)
                                 │  audit log
                                 │
             ◄── result ─────────┘
```

Adding a new tool means plugging into this pipeline. You do **not** re-implement security,
auditing, or concurrency — the shared `run_tool()` call path does all of that for you.

---

## Anatomy of a tool (5 files)

| File | Your job |
|---|---|
| `src/.../tasks/<name>.py` | The task function — reads files, calls model, returns `Outcome` |
| `src/.../application/service.py` | Thin entry point — calls `run_tool()` with your task |
| `src/.../adapters/mcp/server.py` | MCP registration — defines the tool signature and docstring |
| `src/.../adapters/cli/main.py` | CLI sub-command (optional but expected) |
| `tests/` | Unit + contract + security tests |

---

## Step 1 — Write the task function

Create `src/task_offloader_agent/tasks/<your_tool>.py`.

```python
"""<your_tool>: one sentence describing what this tool does."""

from __future__ import annotations

from ..application.runner import Env, Outcome, RunContext
from ..core.paths import PathError
from ..core.result import failed_result, make_result
from .common import CallStats, call_model

REVIEW = "spot-check-citations"   # or "narrative-only" or "none" — see result.py


async def run_<your_tool>(ctx: RunContext, <your_args>) -> Outcome:
    run_id = ctx.run_id
    env    = ctx.env

    # ── 1. Validate inputs ────────────────────────────────────────────────────
    if not <required_arg>:
        return Outcome(failed_result(run_id, "`<required_arg>` is empty.", REVIEW))

    # ── 2. Read files through the path guard ──────────────────────────────────
    #   NEVER open files directly. Always use env.guard.
    try:
        real = env.guard.resolve_read(<path_str>)
        with env.guard.open_checked(real) as fh:
            raw = fh.read()
    except PathError as exc:
        return Outcome(failed_result(run_id, str(exc), REVIEW, code="invalid_input"))

    # ── 3. Redact before the model sees anything ──────────────────────────────
    #   Built-in rules cover tokens, cookies, emails. Add project rules in profile.toml.
    #   For text you build yourself (not yet sent to model), redact explicitly:
    text_for_model, _ = env.redactor.redact(<assembled_text>)

    # ── 4. Call the model ─────────────────────────────────────────────────────
    system = env.prompts.get("ask_system").template   # or your own prompt
    stats  = CallStats()
    try:
        reply = await call_model(
            ctx, stats,
            system,
            build_user=lambda note: f"{text_for_model}\n{note}",
            num_predict=512,    # how many output tokens to reserve
            retry_words=100,    # word cap for the retry attempt
        )
    except Exception as exc:
        return Outcome(failed_result(run_id, str(exc), REVIEW))

    # ── 5. Post-process the model output ──────────────────────────────────────
    #   Redact model output before it leaves the tool (defence in depth).
    answer, redacted = ctx.env.redactor.redact(reply.text.strip())

    # ── 6. Build the result ───────────────────────────────────────────────────
    budget = {"input_tokens": stats.input_tokens, "output_tokens": stats.output_tokens}
    warnings = list(stats.warnings)
    if redacted:
        warnings.append("redacted: " + ", ".join(f"{k} x{n}" for k, n in sorted(redacted.items())))

    result = make_result(
        run_id, "ok",
        summary="One sentence describing what was done.",
        review=REVIEW,
        answer=answer,
        citations=[],       # list of "path:Lstart-Lend" strings
        budget=budget,
        warnings=warnings,
    )
    metrics = stats.metrics(num_predict=512)   # written to audit log only
    return Outcome(result, metrics)
```

### Rules you must follow in the task function

| Rule | What it means |
|---|---|
| **R1** Always use `env.guard.resolve_read()` | Never open a file with `open()` directly |
| **R2** Always use `env.guard.open_checked()` | Re-verifies path on open (TOCTOU-safe) |
| **R3** Redact before model | Call `env.redactor.redact()` on any text before `call_model()` |
| **R4** Redact model output | Call `env.redactor.redact()` on `reply.text` before returning |
| **R5** Never raise from a tool | Catch exceptions and return `failed_result()` — `run_tool()` is a last resort |
| **R6** Write only to `ctx.run_dir` | Never write outside `.task-offloader/run/<run_id>/` |
| **R7** Never print to stdout | stdout is the MCP protocol wire — use `sys.stderr` for debug |
| **R8** Model text only in `answer`/`citations` | Never put model output in `summary`, `review`, or `next_step` |

---

## Step 2 — Add a service entry point

In `src/task_offloader_agent/application/service.py`, add a function that calls `run_tool()`:

```python
from ..tasks.<your_tool> import run_<your_tool>

async def <your_tool>(
    env: Env,
    <your_args>,
    requested_by_user: bool,
    progress: Progress = no_progress,
) -> dict:
    return await run_tool(
        env,
        tool="<your_tool>",          # must match the switch key
        requested_by_user=requested_by_user,
        review="spot-check-citations",
        task=lambda ctx: run_<your_tool>(ctx, <your_args>),
        progress=progress,
    )
```

`run_tool()` automatically handles:
- Switch check (`auto` / `manual` / `off`)
- `run_id` generation
- Deadline calculation
- Audit log (`START`, status, duration, sizes)
- Exception → `failed_result` fallback

---

## Step 3 — Register the MCP tool

In `src/task_offloader_agent/adapters/mcp/server.py`, inside `build_server()`:

```python
@mcp.tool()
async def <your_tool>(
    <required_arg>: str,
    ctx: Context,
    <optional_arg>: str | None = None,
    requested_by_user: bool = False,
) -> dict[str, Any]:
    """One sentence — the cloud model reads this to decide whether to call the tool.
    <required_arg>: what it is and the expected format.
    requested_by_user: true only if the developer asked for local help (#local)."""
    return await service.<your_tool>(
        runtime.target, <required_arg>, <optional_arg>, requested_by_user, _progress(ctx)
    )
```

> **Docstring is the tool description** — the cloud model reads it to decide when to call your tool.
> Keep it one or two sentences. Be explicit about input format and size limits.

---

## Step 4 — Add a CLI sub-command (optional but expected)

In `src/task_offloader_agent/adapters/cli/main.py`, add a subparser so users can
test the tool directly without an MCP client:

```python
p = sub.add_parser("<your_tool>", help="<one line description>")
p.add_argument("<required_arg>")
p.set_defaults(func=lambda args, env: asyncio.run(service.<your_tool>(
    env, args.<required_arg>, requested_by_user=True
)))
```

Test it:

```bash
task-offloader --workspace . --profile .task-offloader/profile.toml <your_tool> <args>
```

---

## Step 5 — Prompts (if your tool calls the model)

Prompts live in `src/task_offloader_agent/prompts/` as `.txt` files bundled with the package.

Create `src/task_offloader_agent/prompts/<your_tool>_system.txt`:

```
You are a precise assistant. You read the provided text and answer the question.
Rules:
- Cite every claim with a line reference: path:Lstart-Lend
- Answer in at most {max_words} words.
- If nothing is relevant, reply: NOTHING RELEVANT
```

Load it in your task:

```python
system = env.prompts.get("<your_tool>_system").template
```

Users can override the prompt by placing a file with the same name in
`.task-offloader/prompts/` (see `[prompts] override_dir` in `profile.toml`).

---

## Step 6 — Tests

Every new tool needs tests in three suites:

### Unit tests — `tests/unit/test_<your_tool>.py`

```python
def test_empty_input_returns_failed():
    # build a minimal Env with a mock provider
    ...
    result = asyncio.run(run_<your_tool>(ctx, instruction=""))
    assert result.result["status"] == "failed"
```

### Security tests — `tests/security/test_<your_tool>_security.py`

```python
def test_path_traversal_blocked(env):
    result = asyncio.run(run_<your_tool>(ctx, paths=["../../etc/passwd"]))
    assert result.result["status"] == "failed"
    assert result.result["error"]["code"] == "invalid_input"

def test_denied_path_blocked(env):
    result = asyncio.run(run_<your_tool>(ctx, paths=[".task-offloader/profile.toml"]))
    assert result.result["status"] == "failed"
```

### Contract tests — `tests/contract/test_<your_tool>_contract.py`

```python
UPDATE_GOLDEN = os.getenv("UPDATE_GOLDEN") == "1"

def test_result_shape(golden_result):
    required = {"run_id", "status", "summary", "answer", "citations",
                "files", "apply", "checks", "budget", "warnings", "review", "next_step"}
    assert required.issubset(golden_result.keys())
```

Regenerate golden files after intentional contract changes:

```bash
UPDATE_GOLDEN=1 python -m pytest tests/contract/
git diff tests/contract/golden/    # review before committing
```

---

## The result contract

Every tool result must have this exact shape. All fields are **required** (use `None` or `[]` for empty):

```json
{
  "run_id":    "<timestamp>-<tool>",
  "status":    "ok | partial | refused | failed | disabled | config_error",
  "for":       "copilot-review",
  "summary":   "<one sentence — no model text>",
  "answer":    "<model text or null>",
  "citations": ["path:Lstart-Lend", ...],
  "files":     ["path/to/output.md", ...],
  "apply":     null,
  "checks":    { "citations": "3 valid, 0 removed", "redaction": "applied" },
  "budget":    { "input_tokens": 597, "output_tokens": 37 },
  "warnings":  [],
  "review":    "<what the cloud model should verify>",
  "next_step": "<what the cloud model should do next>"
}
```

Use `make_result()`, `failed_result()`, `refused_result()`, or `disabled_result()` from
`core/result.py` — never construct the dict manually.

> **`summary`, `review`, `next_step` must never contain model output.**
> Model text goes only into `answer`, `citations`, and files under `run_dir`.

---

## How `run_tool()` wraps your task

```
cloud model call
    │
    ▼
run_tool()  ← you never call this directly; service.py calls it
    │
    ├── read switch.json → is the tool on/off/manual?
    │       └── if off → disabled_result() (no task called)
    │
    ├── generate run_id
    ├── write audit START
    ├── set deadline = now + timeout_s
    │
    ├── await task(ctx)  ← YOUR task function runs here
    │       └── any unhandled exception → failed_result()
    │
    ├── write audit (status, duration, sizes)
    └── return result dict to MCP server → cloud model
```

---

## Checklist before opening a PR

- [ ] Task function uses `env.guard.resolve_read()` and `env.guard.open_checked()` for all file reads
- [ ] Model input is redacted with `env.redactor.redact()` before `call_model()`
- [ ] Model output is redacted with `env.redactor.redact()` before `make_result()`
- [ ] Tool writes only to `ctx.run_dir` (inside `.task-offloader/run/<run_id>/`)
- [ ] Nothing printed to `stdout`
- [ ] `make_result()` / `failed_result()` used — no manual dict construction
- [ ] `summary`, `review`, `next_step` contain no model text
- [ ] Unit tests cover empty input, oversized input, model failure
- [ ] Security tests cover path traversal and denied paths
- [ ] Contract test verifies result shape
- [ ] Docstring in `server.py` clearly tells the cloud model when to call this tool

---

## Related docs

- [Architecture](architecture.md) — layer diagram and call path
- [Security Model](security.md) — path guard, redaction, trust boundary details
- [Configuration Reference](configuration.md) — result contract, error codes, operating modes

