# Workspace instructions for GitHub Copilot

<!--
  TEMPLATE — copy this file to: <your-workspace>/.github/copilot-instructions.md
  Edit the sections marked ← to match your project.
  Copilot reads this file automatically for every chat session in this workspace.
-->

## TaskOffloaderAgent

A local MCP tool that handles bounded, data-heavy subtasks.
Use it to avoid burning context on large files or log triage.
The agent is read-only — it never writes, moves, or deletes files.

### When to use `local_ask`

- A file or set of files exceeds ~200 lines and the question is self-contained
  (does not require understanding the entire codebase in one pass).
- You need a first-pass summary of an unfamiliar module before reading it yourself.
- The user asks about a specific file and you have not yet read it.

**How to call it:** pass the relevant file paths and a precise question.
- `answer` — the model's full response.
- `review` — if non-empty, verify the point it raises before presenting to the user.
- `citations` — line-range references verified by code, not the model; you can trust them.

### When to use `summarize_logs`

- The user mentions a log file, a crash, or an error you have not seen yet.
- A log directory contains more lines than you can read directly.
- The user asks "what went wrong?" without specifying a specific error.

**How to call it:** pass the log file paths.
- `summary` — one-sentence digest.
- `answer` — full analysis: error patterns, counts, timeline.

### When to use `local_status`

- Before the first tool call in a session, to confirm the agent is reachable.
- After any call returns `provider_unavailable` — check status before retrying.

### When NOT to use TaskOffloaderAgent

- Task requires writing, moving, or deleting files.
- Question spans the entire codebase and cannot be answered from a bounded file set.
- The user explicitly asks you to read the file yourself.
- `local_status` reports `mode: off` or the model is unreachable — handle the task yourself.

### Handling results

After every TaskOffloaderAgent call, check `next_step`:

| `next_step` | Action |
|---|---|
| `"present_to_user"` | Answer is ready — show it |
| `"verify_and_present"` | Read `review` and address it first |
| `"split_input_and_retry"` | Input too large — split files in half and retry each |
| `"check_status"` | Call `local_status` before retrying |
| `"fallback_to_primary"` | Agent off or unavailable — handle yourself |

### Controlling the agent

If the user says "pause the offloader" or "stop using the local model":
- Run: `task-offloader --workspace . off`
- Windows: `.task-offloader\task-offloader.ps1 off`

If the user says "resume":
- Run: `task-offloader --workspace . on`

