# Configuration Reference

Config priority (highest first):

```
CLI flags  >  environment variables  >  profile.toml  >  built-in defaults
```

An invalid value at any layer is a hard **configuration error** Ã¢â‚¬â€ the server reports `config_error` on the status tool until fixed.

---

## CLI flags

| Flag | Description |
|---|---|
| `--workspace <path>` | Absolute path to the workspace root. Required for most commands (not `init`). |
| `--profile <path>` | Path to `profile.toml`. Must be inside the workspace. Required for most commands. |
| `--mode auto\|manual\|off` | Override the initial operating mode. |
| `--version` | Print version and exit. |

> [!TIP]
> If `.task-offloader/profile.toml` exists in the current directory, `--workspace` and `--profile` are auto-detected. You don't need to pass them when running from the workspace directory.

> [!TIP]
> `init` creates `.task-offloader/task-offloader.ps1` in the workspace. That wrapper fills in `--workspace` and `--profile` automatically so you don't need to type them for every command.

---

## Environment variables

| Variable | Equivalent | Default |
|---|---|---|
| `TASK_OFFLOADER_WORKSPACE` | `--workspace` | Ã¢â‚¬â€ |
| `TASK_OFFLOADER_PROFILE` | `--profile` | Ã¢â‚¬â€ |
| `TASK_OFFLOADER_MODE` | `--mode` | `auto` |
| `TASK_OFFLOADER_MODEL` | `inference.model` | Ã¢â‚¬â€ |
| `TASK_OFFLOADER_NUM_CTX` | `inference.num_ctx` | `16384` |
| `TASK_OFFLOADER_CHUNK_TOKENS` | chunk size for `local_ask` | `min(12000, num_ctx - 2000)` |
| `TASK_OFFLOADER_MAX_CHUNKS` | max chunks for `local_ask` | `4` |
| `TASK_OFFLOADER_TIMEOUT_S` | per-call timeout (seconds) | `180` |
| `TASK_OFFLOADER_MAX_PENDING` | queued calls before `busy` | `3` |
| `TASK_OFFLOADER_KEEP_ALIVE` | Ollama keep-alive duration | `5m` |
| `TASK_OFFLOADER_RETENTION_DAYS` | `run/` cleanup period (days) | `14` |
| `TASK_OFFLOADER_TOKENIZER` | path to `tokenizer.json` | Ã¢â‚¬â€ |
| `TASK_OFFLOADER_PROVIDER_URL` | Ollama base URL | `http://127.0.0.1:11434` |

---

## profile.toml Ã¢â‚¬â€ full reference

Annotated template: [`assets/workspace/profile.toml`](../assets/workspace/profile.toml).  
Extended layout guide: [Workspace Config](workspace-config.md).

### `[profile]`

| Key | Type | Description |
|---|---|---|
| `name` | string | Human-readable workspace label for logs and audit |
| `schema_version` | integer | Must be `1` |

### `[inference]`

| Key | Type | Description |
|---|---|---|
| `provider` | string | Only `"ollama"` is supported |
| `model` | string | Ollama model name or tag |
| `num_ctx` | integer | Context window in tokens (4096Ã¢â‚¬â€œ131072) |
| `tokenizer` | string | Path to `tokenizer.json`, relative to the profile file |

### `[security]`

| Key | Type | Description |
|---|---|---|
| `deny_paths` | list of strings | Workspace-relative paths to block. Use `/` separators. Prefix `**/` to match at any depth. A rule covers all descendants. |
| `deny_names` | list of strings | File-name globs (no folder component) |

### `[[redaction.rules]]`

Each entry is a TOML array-of-tables item:

| Key | Type | Description |
|---|---|---|
| `kind` | string | Label used in `<redacted:kind>` placeholders |
| `pattern` | string | Python `re` pattern. Use literal strings (`'...'`) in TOML. |
| `keep_prefix` | bool | When `true`, capture group 1 is kept; only the rest is replaced |

### `[logs]`

| Key | Type | Description |
|---|---|---|
| `allowed_dirs` | list of strings | Workspace-relative directories `summarize_logs` may read |
| `max_files` | integer | Maximum files in a single call |

#### `[[logs.formats]]`

| Key | Type | Description |
|---|---|---|
| `name` | string | Format identifier (used in error messages) |
| `pattern` | string | Python `re` pattern with named groups `level`, `ts`, `msg`. Optional: `thread`, `logger`. |

### `[prompts]`

| Key | Type | Description |
|---|---|---|
| `override_dir` | string | Folder next to the profile file containing `.txt` overrides for packaged prompts |

---

## Token budget

```
input_limit = num_ctx - num_predict - 1500
```

| Tool | `num_predict` |
|---|---|
| `local_ask` (chunk pass) | 768 |
| `local_ask` (merge pass) | 1024 |
| `summarize_logs` (narrative) | 768 |

`local_ask` splits input into chunks of `chunk_tokens` (default: `min(12000, num_ctx - 2000)`) with at most `max_chunks` (default: 4). If the input exceeds `max_chunks Ãƒâ€” chunk_tokens` the call is **refused** Ã¢â‚¬â€ input is never silently truncated.

The log digest is capped at 8000 tokens. Without a tokenizer file, counts are estimated at 3 characters per token (conservative).

---

## Operating modes

| Mode | Behaviour |
|---|---|
| `auto` | All enabled tools run automatically when called by the primary agent |
| `manual` | Tools run only when the call carries `requested_by_user = true` |
| `off` | All tools except `local_status` return `{"status":"disabled"}` |

Set via `--mode` / `TASK_OFFLOADER_MODE` or the CLI commands `on`, `off`, `manual`. The current mode persists in `.task-offloader/run/switch.json` across restarts.

Per-tool flags override the mode: a tool set to `false` is always off regardless of mode.

### switch.json schema

```json
{ "mode": "auto",   "tools": {} }                          // everything on (default)
{ "mode": "off",    "tools": {} }                          // everything paused
{ "mode": "manual", "tools": {} }                          // manual only
{ "mode": "auto",   "tools": { "summarize_logs": false } } // log triage off only
```

Full examples: [workspace-config.md Ã¢â€ â€™ switch.json](workspace-config.md#switchjson--onoff-state-reference)

---

## CLI commands

```
task-offloader [global options] <command> [command options]
```

**Global options:** `--workspace`, `--profile`, `--mode`, `--version`

### Setup

| Command | Description |
|---|---|
| `init` | Set up `.task-offloader/` in the current directory and wire AI clients |
| `profile check` | Validate the profile and print any errors |
| `upgrade` | Pull latest code from the git clone and reinstall |
| `restart` | Stop the running MCP server (AI client restarts it automatically) |
| `uninstall` | Remove `task-offloader-agent` from the current venv and delete the clone directory |

**`init` flags:** `--model <tag>`, `--client <N...>`, `--force`, `--dry-run`

> [!NOTE]
> **Windows — `upgrade`:** the running executable is locked by the OS and cannot replace itself.
> After `task-offloader upgrade` completes the git pull, open a **new** terminal and run:
> ```powershell
> cd "$env:USERPROFILE\developer-draft\task-offloader-agent"
> .venv\Scripts\Activate.ps1     # activate the venv
> pip install -e .
> ```
> Use the **venv pip**, not the system pip — otherwise the installed command won't update.

### MCP server

| Command | Description |
|---|---|
| `mcp` | Start the MCP stdio server |

### Inspection

| Command | Description |
|---|---|
| `status` | Print current status: profile, model, mode, tool states, tokenizer |
| `tools` | List all tools and their current state |

### Switch

| Command | Description |
|---|---|
| `on [tool]` | Enable the agent or a specific tool |
| `off [tool]` | Disable the agent or a specific tool |
| `manual [tool]` | Switch to manual mode |
| `reset [tool]` | Reset a tool flag to inherit from the global mode |

### CLI tool runner

| Command | Description |
|---|---|
| `ask <instruction> [paths...]` | Run `local_ask` directly from the terminal |
| `logs <files...>` | Run `summarize_logs` directly from the terminal |

### MCP tools (exposed to AI clients)

| Tool | Default | Description |
|---|---|---|
| `local_status` | on | Service health, mode, per-tool state, Ollama readiness |
| `local_ask` | on | Send a question + workspace files to the local model |
| `summarize_logs` | on | Deterministic log digest + local model narrative |
| `workspace_context` | on | Full workspace snapshot: tools, deny paths, log dirs, token budget â€” call once at session start |
| `local_report` | on | Usage stats from audit log as JSON: call counts, savings, ratings, alerts |
| `local_rate` | on | Rate a result `good` or `bad` immediately after using it |
| `local_pending_ratings` | on | List unrated results so the AI client can prompt the developer |
| `draft_tests` | off | *(not built)* |
| `draft_docs` | off | *(not built)* |
| `draft_text` | off | *(not built)* |
| `draft_fixture` | off | *(not built)* |

All built tools are on by default. Turn any off with `task-offloader off <tool>`.

**`ask` flags:** `--text <string>`, `--max-words <N>`  
**`logs` flags:** `--since`, `--until`, `--pattern`, `--correlation-id`, `--no-narrate`

### Audit and reporting

| Command | Description |
|---|---|
| `report` | Aggregated usage report from `audit.jsonl` |
| `summary` | Daily call breakdown for the last N days |
| `rate <run_id> good\|bad` | Rate a specific call result |
| `rate-pending` | Interactively rate all unrated `ok`/`partial` results |

**`report` flags:** `--audit-file <path>`, `--fail-on-bad-rate` (exit 1 if >50% rated bad for any tool)  
**`summary` flags:** `--days <N>` (default 7), `--audit-file <path>`

### Maintenance

| Command | Description |
|---|---|
| `clean` | Delete `run/` output older than `retention_days` |

**`clean` flags:** `--days <N>` (override retention period)

**Exit codes:** `0` = success, `1` = task or I/O error (also when `--fail-on-bad-rate` triggers), `2` = configuration or usage error.

---

## MCP tools

| Tool | Description |
|---|---|
| `local_status` | Returns the current agent status and configuration summary |
| `local_ask` | Sends workspace files to the local model with a question |
| `summarize_logs` | Reads, digests, and summarises server log files |

### Result contract

Every tool result shares this shape:

```json
{
  "run_id":    "<timestamp>-<tool>",
  "status":    "ok | partial | refused | failed | disabled | config_error",
  "for":       "<the original question or request>",
  "summary":   "<one-sentence summary>",
  "answer":    "<full model answer>",
  "citations": ["path:L10-L25", "..."],
  "files":     ["path/to/file.txt", "..."],
  "apply":     null,
  "checks":    { "citations_verified": 3, "citations_removed": 0 },
  "budget":    { "input_tokens": 597, "output_tokens": 37 },
  "warnings":  [],
  "review":    "<anything the primary agent should double-check>",
  "next_step": "<suggested next action>"
}
```

On non-`ok` status, an `error` object is appended:

```json
"error": { "code": "provider_unavailable", "retryable": true }
```

### Error codes

`invalid_input`, `provider_unavailable`, `provider_error`, `timeout`, `busy`, `shutting_down`, `switched_off`, `tool_off`, `manual_mode`, `config_error`, `unavailable`, `internal`
