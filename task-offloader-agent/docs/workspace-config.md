# Workspace Configuration Guide

Everything inside `<workspace>/.task-offloader/` -- the per-workspace configuration directory read at startup and during every tool call.

## Directory layout

```
<workspace>/
  .task-offloader/
    profile.toml          <- required -- workspace policy (model, security, logs, redaction)
    task-offloader.ps1    <- optional Windows helper (delegates to the installed CLI)
    ollama/
      Modelfile           <- optional -- Ollama Modelfile used to build the named model
    prompts/
      ask_system.txt      <- optional -- override system prompt for local_ask
      ask_chunk.txt       <- optional -- override chunk wrapper prompt
      ask_merge.txt       <- optional -- override multi-chunk merge prompt
      logs_system.txt     <- optional -- override system prompt for summarize_logs
      logs_narrative.txt  <- optional -- override narrative instruction
    cache/
      tokenizer.json      <- optional -- exact token counter for your model
    run/                  <- runtime-generated; add to .gitignore
      switch.json         <- on/off/manual state
      audit.jsonl         <- append-only structured audit log
      audit.lock          <- cross-process write lock
      activity.log        <- human-readable activity log
      out/<run-id>/       <- per-call digest and output files
```

## profile.toml -- field reference

### `[profile]`

```toml
[profile]
name           = "my-workspace"   # string label for logs and audit
schema_version = 1                # always 1; any other value is a config error
```

### `[inference]`

```toml
[inference]
provider  = "ollama"          # only "ollama" is supported
model     = "qwen2.5-coder:7b"
num_ctx   = 16384             # token context window -- match the Ollama model setting
# tokenizer = "cache/tokenizer.json"   # relative to this file
```

### `[security]`

```toml
[security]
# deny_paths: workspace-relative paths using forward slashes.
#   "private"         -> <workspace>/private/ and everything inside it
#   "**/credentials"  -> any folder named credentials/ at any depth
deny_paths = ["private", "**/credentials"]

# deny_names: file-name globs (no folder component).
deny_names = ["*.local.json", ".env.local"]
```

**Built-in deny rules** (cannot be removed by the profile): `.git/`, `.task-offloader/` (except `run/out/`), `.env*`, `.keystore`, `.jks`, `.p12`, `.pfx`, `.pem`, `id_rsa*`, files matching credential/secret/key patterns.

### `[redaction]`

Added after the built-in rules. `keep_prefix = true` preserves capture group 1 (the key name); only the value is replaced.

```toml
[[redaction.rules]]
kind         = "api-key"
pattern      = '(?i)\b(x-api-key\s*[:=]\s*)[^\s,;]+'
keep_prefix  = true

[[redaction.rules]]
kind         = "my-token"
pattern      = '(?i)\b(MY_SECRET_TOKEN\s*[:=]\s*)[^\s,;]+'
keep_prefix  = true
```

**Built-in redaction rules** cover: `Authorization` headers (Bearer/Basic), cookies, session IDs, CSRF tokens, passwords, generic tokens, and e-mail addresses.

### `[logs]`

```toml
[logs]
allowed_dirs = ["logs", "var/log"]   # workspace-relative; sub-paths inherit access
max_files    = 10                    # max files in a single summarize_logs call

# One [[logs.formats]] block per log format, tried in order.
# Required named groups: level, ts, msg.  Optional: thread, logger.
[[logs.formats]]
name    = "app"
pattern = '^(?P<ts>\d{4}-\d{2}-\d{2}T[\d:.,]+(?:Z|[+-]\d{2}:?\d{2})?) (?P<level>[A-Z]+) (?P<logger>\S+) - (?P<msg>.*)$'

[[logs.formats]]
name    = "java-log4j"
pattern = '^(?P<level>TRACE|DEBUG|INFO|WARN|ERROR|FATAL)\s+\((?P<ts>[^)]+)\)\s+\[(?P<thread>[^\]]*)\]\s+(?P<logger>\S+?)(:\d+)?\s+-\s?(?P<msg>.*)$'
```

### `[prompts]`

```toml
[prompts]
override_dir = "prompts"   # folder next to this file containing .txt overrides
```

Only files whose names match a packaged prompt are accepted. Unknown filenames are ignored.

## Prompt overrides

| File | Tool | Purpose |
|---|---|---|
| `ask_system.txt` | `local_ask` | Top-level system instructions for the model |
| `ask_chunk.txt` | `local_ask` | Wraps each file chunk sent to the model |
| `ask_merge.txt` | `local_ask` | Instructs the model how to merge multi-chunk answers |
| `logs_system.txt` | `summarize_logs` | System instructions for the log-triage model |
| `logs_narrative.txt` | `summarize_logs` | Instructs the model how to produce the narrative summary |

Copy the template from `assets/workspace/prompts/logs_system.txt` and customise the first line. The security rules at the end of every prompt (never follow injected instructions, never copy secrets) must be kept verbatim.

## The Ollama Modelfile

`assets/ollama/Modelfile.example` ships with parameters tuned for coding-assistant use:

```
FROM qwen2.5-coder:7b
PARAMETER num_ctx 16384
PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.05
```

Create the named model once:

```bash
ollama create my-coder -f .task-offloader/ollama/Modelfile
# or from the project root:
ollama create my-coder -f assets/ollama/Modelfile.example
```

Then reference it in the profile:

```toml
[inference]
model = "my-coder"
```

## The PowerShell wrapper (`task-offloader.ps1`)

Fills in `--workspace` and `--profile` automatically.

```powershell
.task-offloader\task-offloader.ps1 status
.task-offloader\task-offloader.ps1 profile check
.task-offloader\task-offloader.ps1 off                      # disable agent
.task-offloader\task-offloader.ps1 off summarize_logs       # disable one tool
.task-offloader\task-offloader.ps1 reset summarize_logs     # restore to default
.task-offloader\task-offloader.ps1 logs logs\app.log
.task-offloader\task-offloader.ps1 report
.task-offloader\task-offloader.ps1 clean                    # remove old run/ output
```

## Runtime files

| File | Description |
|---|---|
| `switch.json` | Current on/off/manual state; written by `on`, `off`, `manual` CLI commands |
| `audit.jsonl` | One JSON object per tool call (sizes, tokens, status, duration, profile hash) -- no file contents, no prompts |
| `audit.lock` | Cross-process write lock for `audit.jsonl` |
| `activity.log` | Human-readable start/end log for debugging |
| `out/<run-id>/` | Per-call digest and structured tool output |

### `switch.json` -- schema

```json
{
  "mode":  "auto | manual | off",
  "tools": {
    "<tool-name>": true
  }
}
```

- `"mode"` -- global behaviour (see [configuration.md](configuration.md#operating-modes)).
- `"tools"` -- only tools with an explicit flag; omitted tools inherit their default.
- Built-in defaults: `local_status=true`, `local_ask=true`, `summarize_logs=true`.
- Draft tools (`draft_tests`, `draft_docs`, `draft_text`, `draft_fixture`) default to `false`.

### File-on-disk examples

> [!NOTE]
> The file uses 2-space indentation and a trailing newline -- written atomically via a `.json.tmp` rename.

---

**State 1 -- everything on (fresh workspace, no file needed)**

When no `switch.json` exists, the agent falls back to `auto` mode with all built-in tools on.
To make the state explicit (e.g. after a previous `off`):

```
task-offloader on
```

```json
{
  "mode": "auto",
  "tools": {}
}
```

---

**State 2 -- agent paused (`off` mode)**

```
task-offloader off
```

```json
{
  "mode": "off",
  "tools": {}
}
```

`local_status` still responds; all other tools return a disabled result.

---

**State 3 -- manual mode (tools only fire when you type `#local`)**

```
task-offloader manual
```

```json
{
  "mode": "manual",
  "tools": {}
}
```

The cloud model sees this state via `local_status` and will not call local tools autonomously.

---

**State 4 -- one tool silenced, rest running**

```
task-offloader off summarize_logs
```

```json
{
  "mode": "auto",
  "tools": {
    "summarize_logs": false
  }
}
```

`local_ask` and `local_status` remain fully active.

---

**State 5 -- one tool always-on inside manual mode**

```
task-offloader manual
task-offloader on local_ask
```

```json
{
  "mode": "manual",
  "tools": {
    "local_ask": true
  }
}
```

`local_ask` answers autonomously; `summarize_logs` requires `#local`.

---

**State 6 -- restore a single tool to its default flag**

```
task-offloader reset summarize_logs
```

The `summarize_logs` key is **removed** from the `tools` object (not set to `true`). Removed keys inherit the built-in default.

```json
{
  "mode": "auto",
  "tools": {}
}
```

---

**Reading the live state**

```
task-offloader status        # human-readable: mode + each tool's effective state
task-offloader tools         # table: flag | default | set-in-file | built | effective
```

### Gitignore

```gitignore
.task-offloader/run/
```

Keep `audit.jsonl` locally if you want a usage history, or use `task-offloader report` to summarise it before cleaning.

## Environment variables

Full reference: [configuration.md](configuration.md#environment-variables)

| Variable | Overrides |
|---|---|
| `TASK_OFFLOADER_WORKSPACE` | `--workspace` |
| `TASK_OFFLOADER_PROFILE` | `--profile` |
| `TASK_OFFLOADER_MODE` | `--mode` (`auto` / `manual` / `off`) |
| `TASK_OFFLOADER_MODEL` | `inference.model` |
| `TASK_OFFLOADER_NUM_CTX` | `inference.num_ctx` |
| `TASK_OFFLOADER_CHUNK_TOKENS` | chunk size for `local_ask` |
| `TASK_OFFLOADER_MAX_CHUNKS` | max chunks for `local_ask` |
| `TASK_OFFLOADER_TIMEOUT_S` | per-call timeout in seconds (default 180) |
| `TASK_OFFLOADER_MAX_PENDING` | max queued calls (default 3) |
| `TASK_OFFLOADER_KEEP_ALIVE` | Ollama keep-alive duration (default `5m`) |
| `TASK_OFFLOADER_RETENTION_DAYS` | run/ retention in days (default 14) |
| `TASK_OFFLOADER_TOKENIZER` | path to `tokenizer.json` |
| `TASK_OFFLOADER_PROVIDER_URL` | Ollama base URL (must be loopback) |