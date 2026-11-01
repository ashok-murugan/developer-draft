# Project instructions for Claude

<!--
  TEMPLATE — copy this file to: <your-workspace>/CLAUDE.md
  Claude reads this file automatically at the start of every project session.
  Edit the sections marked ← to match your project.
-->

## Project overview

<!-- ← Describe your project here -->

---

## Tools: TaskOffloaderAgent (MCP)

Available MCP tools: `local_status`, `local_ask`, `summarize_logs`.
The agent is **read-only** — it never writes, moves, or deletes files.

### Delegation rules

| Condition | Action |
|---|---|
| File > 200 lines, question is self-contained | Use `local_ask` |
| Log file(s) mentioned or crash reported | Use `summarize_logs` |
| First tool call of the session | Call `local_status` first to confirm reachable |
| Previous call failed with `provider_unavailable` | Call `local_status` before retrying |
| Task needs file writes or whole-repo understanding | Handle yourself |
| `local_status` reports `mode: off` | Skip offloader; handle task yourself |

### After every call

- Read `review` — if non-empty, verify the flagged point before presenting to the user.
- Trust `citations` (`path:Lstart-Lend`) — they are code-verified, not model-generated.
- Check `next_step` and act accordingly:
  - `"verify_and_present"` → address `review` first
  - `"split_input_and_retry"` → divide file list in half and retry each half
  - `"fallback_to_primary"` → proceed without the offloader

### Controlling the agent

User says "pause the offloader":
  → Run `task-offloader --workspace . off`

User says "resume":
  → Run `task-offloader --workspace . on`

---

## Workspace conventions

<!-- ← Add your project-specific conventions here -->
<!-- Examples: branch naming, test commands, code style, file layout -->

