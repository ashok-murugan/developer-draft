# Integration Guide -- Wiring with Workspace Skills and Rules

Explains how to write the rules, skills, and instruction files that tell the primary agent when and how to delegate to TaskOffloaderAgent. MCP server registration is covered in [setup.md](setup.md).

## Copilot instructions (`.github/copilot-instructions.md`)

```markdown
## TaskOffloaderAgent

A local MCP tool that handles bounded, data-heavy subtasks.
Use it to avoid burning context on large files or log triage.

### When to use `local_ask`

- A file or set of files exceeds ~200 lines and the question is self-contained.
- You need a first-pass summary of an unfamiliar module before reading it yourself.
- The user asks about a specific file you have not yet read.

**How to call it:** pass the relevant files and a precise question.
Check the `review` field -- if non-empty, verify the point it raises before presenting.
Citations are code-verified line-range references to the files you passed.

### When to use `summarize_logs`

- The user mentions a log file, a crash, or an error you have not seen yet.
- The user asks "what went wrong?" without specifying a specific error.

**How to call it:** pass the log file paths. Use `summary` for the digest; `answer` for the full analysis.

### When to use `local_status`

- Before any other tool call, to confirm the agent is running and the model is reachable.
- If a previous call returned `provider_unavailable`.

### When NOT to use TaskOffloaderAgent

- The task requires writing, moving, or deleting files -- the agent is read-only.
- The question spans the entire codebase and cannot be answered from a bounded file set.
- The user explicitly asks you to read the file yourself.
- `local_status` reports `mode: off` or the model is unreachable.
```

## Claude project instructions (`CLAUDE.md`)

```markdown
## Tools: TaskOffloaderAgent (MCP)

Available MCP tools: `local_status`, `local_ask`, `summarize_logs`.

**Delegation rules:**

| Condition | Action |
|---|---|
| File > 200 lines, question is self-contained | Use `local_ask` |
| Log file(s) mentioned or crash reported | Use `summarize_logs` |
| Previous call failed with `provider_unavailable` | Use `local_status` first |
| Task needs file writes or whole-repo understanding | Handle yourself |

**Always:**
- Read the `review` field. If non-empty, verify the flagged point before proceeding.
- Trust citations (`path:Lstart-Lend`) -- they are code-verified, not model-generated.
- Pass the `run_id` to the user if they want to audit the call later.
```

## Antigravity / Gemini workspace rules

Add `rules/task-offloader.md`:

```markdown
# TaskOffloaderAgent delegation rules

## Triggers

Use `local_ask` when:
- You are about to read a file larger than ~200 lines.
- A question is about a specific file's internals and is self-contained.

Use `summarize_logs` when:
- The user mentions a log, error, crash, or asks "what went wrong?".
- A log path is given or inferable from workspace conventions.

Use `local_status` when:
- You are about to call any other task-offloader tool for the first time in a session.
- A tool call returned status `provider_unavailable` or `failed`.

## Result handling

- `status: ok` -> use the `answer`. Check `review` before presenting.
- `status: partial` -> answer is best-effort; note confidence in your response.
- `status: refused` -> input exceeded budget; split the files and retry.
- `status: disabled` -> agent is off; handle the task yourself.
- `status: failed` or `provider_unavailable` -> handle yourself; optionally inform the user.

## Model limitations (communicate when relevant)

- The local model has no internet access.
- It only sees the files you pass -- no memory of previous calls.
- It cannot execute code. All results are read-only analysis.
```

## Cursor (`.cursorrules`)

Add a `TaskOffloaderAgent` section with the same trigger and result-handling rules as above, adapted to Cursor's rule format.

## `next_step` handling

| `next_step` value | Meaning |
|---|---|
| `"present_to_user"` | Answer is ready; show it to the user |
| `"verify_and_present"` | Check `review` before presenting |
| `"split_input_and_retry"` | Input was too large; break files into smaller sets |
| `"check_status"` | Something failed; call `local_status` before retrying |
| `"fallback_to_primary"` | Agent is off or unavailable; handle the task yourself |

Reference in rules:

```markdown
After every TaskOffloaderAgent call:
1. If `next_step` is `"verify_and_present"`, read `review` and address it first.
2. If `next_step` is `"split_input_and_retry"`, divide the file list in half and retry each half.
3. If `next_step` is `"fallback_to_primary"`, proceed without TaskOffloaderAgent.
```

## SKILL.md example (Antigravity / skill-based agents)

```markdown
---
name: task-offloader-delegation
description: >
  Decides when and how to delegate read-heavy subtasks to TaskOffloaderAgent via MCP.
  Use when the primary agent would otherwise read files larger than ~200 lines or triage logs.
---

# TaskOffloaderAgent delegation skill

## Prerequisites

- TaskOffloaderAgent MCP server is registered and running (see setup.md).
- `local_status` returns `mode: auto` and `ollama: reachable`.

## Steps

1. **Before reading any large file:** call `local_ask` with the file path and a precise question.
2. **Before reading any log:** call `summarize_logs` with the log path(s).
3. **After every call:** read `status`, `review`, and `next_step`. Act accordingly.
4. **If the agent is off (`mode: off`):** proceed without it; do not retry in the same session.

## Quality checks

- Every citation (`path:Lstart-Lend`) is code-verified -- you can trust it.
- Never pass credentials, tokens, or API keys as part of the question or file paths.
```

## Compatible frameworks

| Framework | Integration point |
|---|---|
| VS Code GitHub Copilot | `.github/copilot-instructions.md` + `.vscode/mcp.json` (see [setup.md](setup.md)) |
| Claude (Claude.ai / API) | `CLAUDE.md` project file or system prompt |
| Gemini / Antigravity | workspace rules file + MCP server registration |
| Cursor | `.cursorrules` + MCP server config |
| Any MCP stdio client | System prompt or agent instructions + MCP server config |