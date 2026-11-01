# Configuration Reference

Config priority (highest first):

```
CLI flags  >  environment variables  >  profile.toml  >  built-in defaults
```

An invalid value at any layer is a hard **configuration error** -- the server reports `config_error` on the status tool until fixed.

---

## CLI flags

| Flag | Description |
|---|---|
| `--workspace <path>` | Absolute path to the workspace root. **Required.** |
| `--profile <path>` | Path to `profile.toml`. Must be inside the workspace. **Required.** |
| `--mode auto|manual|off` | Override the initial operating mode. |
| `--version` | Print version and exit. |

---

## Environment variables

| Variable | Equivalent | Default |
|---|---|---|
| `TASK_OFFLOADER_WORKSPACE` | `--workspace` | -- |
| `TASK_OFFLOADER_PROFILE` | `--profile` | -- |
| `TASK_OFFLOADER_MODE` | `--mode` | `auto` |
| `TASK_OFFLOADER_MODEL` | `inference.model` | -- |
| `TASK_OFFLOADER_NUM_CTX` | `inference.num_ctx` | `16384` |
| `TASK_OFFLOADER_CHUNK_TOKENS` | chunk size for `local_ask` | `min(12000, num_ctx - 2000)` |
| `TASK_OFFLOADER_MAX_CHUNKS` | max chunks for `local_ask` | `4` |
| `TASK_OFFLOADER_TIMEOUT_S` | per-call timeout (seconds) | `180` |
| `TASK_OFFLOADER_MAX_PENDING` | queued calls before `busy` | `3` |
| `TASK_OFFLOADER_KEEP_ALIVE` | Ollama keep-alive duration | `5m` |
| `TASK_OFFLOADER_RETENTION_DAYS` | `run/` cleanup period (days) | `14` |
| `TASK_OFFLOADER_TOKENIZER` | path to `tokenizer.json` | -- |
| `TASK_OFFLOADER_PROVIDER_URL` | Ollama base URL | `http://127.0.0.1:11434` |

---

## profile.toml -- full reference

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
| `num_ctx` | integer | Context window in tokens (4096--131072) |
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

`local_ask` splits input into chunks of `chunk_tokens` (default: `min(12000, num_ctx - 2000)`) with at most `max_chunks` (default: 4). If the input exceeds `max_chunks x chunk_tokens` the call is **refused** -- input is never silently truncated.

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

Full examples: [workspace-config.md -- switch.json](workspace-config.md#switchjson--onoff-state-reference)

---

## CLI commands

```
task-offloader [global options] <command> [command options]
```

**Global options:** `--workspace`, `--profile`, `--mode`, `--version`

| Command | Description |
|---|---|
| `mcp` | Start the MCP stdio server |
| `status` | Print current status: profile, model, mode, tool states, tokenizer |
| `profile check` | Validate the profile and print any errors |
| `on [tool]` | Enable the agent or a specific tool |
| `off [tool]` | Disable the agent or a specific tool |
| `manual [tool]` | Switch to manual mode |
| `reset [tool]` | Reset a tool flag to inherit from the global mode |
| `tools` | List all tools and their current state |
| `ask <files..>` | Run `local_ask` directly from the CLI |
| `logs <files..>` | Run `summarize_logs` directly from the CLI |
| `rate` | Print the rolling call rate |
| `report` | Print an aggregated usage report from `audit.jsonl` |
| `clean` | Delete `run/` output older than `retention_days` |

**Exit codes:** `0` = success, `1` = task or I/O error, `2` = configuration or usage error.

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