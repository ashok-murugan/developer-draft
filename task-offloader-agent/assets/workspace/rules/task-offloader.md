# TaskOffloaderAgent delegation rules

<!--
  TEMPLATE — copy this file to: <your-workspace>/rules/task-offloader.md
  Used by Gemini / Antigravity and any agent framework that loads rules from a rules/ directory.
-->

## Overview

TaskOffloaderAgent is a local MCP tool for bounded, data-heavy subtasks.
It is **read-only** — it never writes, moves, or deletes files.
Tools: `local_status`, `local_ask`, `summarize_logs`.

## Triggers

Use `local_ask` when:
- You are about to read a file larger than ~200 lines and the question is self-contained.
- A question is about a specific file's internals and does not need whole-repo context.

Use `summarize_logs` when:
- The user mentions a log, error, crash, or asks "what went wrong?".
- A log path is given or inferable from workspace conventions.

Use `local_status` when:
- You are about to call any other task-offloader tool for the first time in a session.
- A tool call returned status `provider_unavailable` or `failed`.

Do NOT use TaskOffloaderAgent when:
- The task requires writing, moving, or deleting files.
- The question requires understanding the entire codebase in one pass.
- `local_status` reports `mode: off` — handle the task yourself.

## Result handling

- `status: ok` → use the `answer`. Check `review` before presenting to the user.
- `status: partial` → answer is best-effort; note uncertainty in your response.
- `status: refused` → input exceeded budget; split the files and retry.
- `status: disabled` → agent is off; handle the task yourself.
- `status: failed` or `provider_unavailable` → handle yourself; optionally inform the user.

After every call, check `next_step`:
- `"present_to_user"` → answer is ready
- `"verify_and_present"` → address `review` first
- `"split_input_and_retry"` → divide file list in half and retry each half
- `"check_status"` → call `local_status` before retrying
- `"fallback_to_primary"` → proceed without the offloader

## Model limitations

Communicate these to the user when relevant:
- The local model has no internet access.
- It only sees the files passed to it — no memory of previous calls.
- It cannot execute code. All results are read-only analysis.

## Controlling the agent

If the user says "pause the offloader":
- Run: `task-offloader --workspace . off`
- Windows shorthand: `.task-offloader\task-offloader.ps1 off`

If the user says "resume":
- Run: `task-offloader --workspace . on`

