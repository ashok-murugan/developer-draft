# Setup Guide

## Prerequisites

| Requirement | Notes |
|---|---|
| Python >= 3.12 | `python --version` |
| Git | `git --version` |
| [Ollama](https://ollama.com) running | `ollama serve` or system service |
| At least one model pulled | `ollama list` |
| A workspace directory | Any project folder |

---

## Step 1 — Clone the repo

The agent is installed **once** in a central location and shared across all workspaces. Pick a location outside your projects.

**Recommended locations by OS:**

| OS | Suggested path |
|---|---|
| Windows | `%USERPROFILE%\developer-draft\task-offloader-agent` |
| macOS | `~/developer-draft/task-offloader-agent` |
| Linux | `~/developer-draft/task-offloader-agent` |

```powershell
# Windows (PowerShell)
git clone https://github.com/ashok-murugan/developer-draft.git "$env:USERPROFILE\developer-draft"
cd "$env:USERPROFILE\developer-draft\task-offloader-agent"
```

```bash
# macOS / Linux
git clone https://github.com/ashok-murugan/developer-draft.git ~/developer-draft
cd ~/developer-draft/task-offloader-agent
```

> [!NOTE]
> `developer-draft` is a multi-project repo. `task-offloader-agent/` is the subdirectory you work from.
> Any path works — update `--workspace` / `TASK_OFFLOADER_WORKSPACE` accordingly.

---

## Step 2 — Pull a model

```bash
ollama pull qwen2.5-coder:7b
ollama list                     # confirm it appears
```

Not sure which model to pick? See the [Model Recommendation Guide](models.md) for a comparison table, hardware requirements, and task-specific suggestions (log triage vs code Q&A).

---

## Step 3 — Install the agent

```powershell
# PowerShell — from the cloned directory
python -m venv .venv
.venv\Scripts\activate
pip install -e .
task-offloader --version
```

> [!NOTE]
> The venv activation (`activate`) only applies to the **current terminal session**.
> To use `task-offloader` from any workspace without activating each time, add the venv bin to your user PATH once:
> ```powershell
> $binPath = "$env:USERPROFILE\developer-draft\task-offloader-agent\.venv\Scripts"
> [Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$binPath", "User")
> $env:PATH += ";$binPath"   # also applies to the current session immediately
> ```
> After this, `task-offloader` works in every new terminal without activation.
> Alternatively, use the `.task-offloader\task-offloader.cmd` wrapper that `init` creates in each workspace — it works without any PATH change and without PowerShell execution policy issues.

```bash
# bash — from the cloned directory
python -m venv .venv
source .venv/bin/activate
pip install -e .
task-offloader --version
```

---

## Step 4 — Initialise a workspace

`cd` into your project directory, then:

```bash
task-offloader init
```

The interactive flow:

```
Workspace:  /home/you/my-project  (name: 'my-project')
Config dir: .task-offloader/  (fixed)
Agent bin:  /home/you/task-offloader-agent/.venv/bin/task-offloader

Ollama models: qwen2.5-coder:7b  llama3:8b
Model [qwen2.5-coder:7b]:

Which AI client(s) to wire?
Enter numbers space-separated, or Enter to skip.

  1  VS Code / GitHub Copilot        .vscode/mcp.json + .github/copilot-instructions.md (detected)
  2  Claude Desktop                  CLAUDE.md
  3  Cursor                          .cursor/mcp.json + .cursor/rules/task-offloader.mdc (detected)
  4  Antigravity / Gemini            rules/task-offloader.md + skills/task-offloader/SKILL.md
  5  All of the above
Client(s) [1]:

  created  .task-offloader/profile.toml
  created  .task-offloader/task-offloader.ps1
  created  .vscode/mcp.json
  merged   .github/copilot-instructions.md
  skipped  .cursor/mcp.json  (already exists — use --force to overwrite)

Next steps:
  1. Review .task-offloader/profile.toml — add deny_paths for sensitive folders
  2. Restart your AI client to pick up the new MCP server
  3. task-offloader profile check
```

**Flags:**

| Flag | Purpose |
|---|---|
| `--model <tag>` | Skip the model prompt |
| `--client <N...>` | Wire specific clients by number (`1`=Copilot `2`=Claude `3`=Cursor `4`=Antigravity `5`=All) |
| `--force` | Overwrite existing client config files |
| `--dry-run` | Preview all actions without writing |

> [!NOTE]
> `.task-offloader/` is created inside **your workspace**, not inside this repo.
> Add `.task-offloader/run/` to your workspace `.gitignore`.

For a second workspace, just `cd` there and run `task-offloader init` again. Each workspace gets its own `profile.toml`; the agent binary is shared.

---

## Step 5 — Validate profile

```bash
task-offloader profile check
```

Fix any reported errors before starting the MCP server.

The check also warns about:
- deny paths configured in `profile.toml` that don't exist in the workspace
- log `allowed_dirs` that overlap with `deny_paths`
---

## Upgrading

```bash
task-offloader upgrade
```

Stops the running MCP server, pulls the latest code from the git clone, then prints the reinstall command.

> [!NOTE]
> **Windows:** the running executable is locked by the OS and cannot replace itself while it runs.
> After `upgrade` completes the git pull, open a **new** terminal and run:
> ```powershell
> cd "$env:USERPROFILE\developer-draft\task-offloader-agent"
> .venv\Scripts\Activate.ps1        # activate the venv
> pip install -e .
> ```
> Or without activating:
> ```powershell
> .venv\Scripts\pip install -e "path\to\task-offloader-agent"
> ```
> Use the **venv pip**, not the system pip — otherwise the installed command won't update.

After reinstalling, restart your AI client to pick up any MCP protocol changes.

---

## Uninstalling

```bash
task-offloader uninstall
```

Prompts for confirmation, then:
1. Stops the running MCP server
2. Uninstalls `task-offloader-agent` from the venv
3. Deletes the git clone directory

Workspace configs (`.task-offloader/` in each project) are **not** removed. Clean them up manually if needed:
```powershell
# Windows
Remove-Item -Recurse -Force .task-offloader
```
```bash
# macOS / Linux
rm -rf .task-offloader
```

---

## Manual client wiring (reference)

`init` handles wiring automatically. Use this section only if you need to re-wire manually or add a client that `init` did not detect.

Replace `<venv>` with the absolute path to your `.venv` and `<workspace>` with the absolute path to your workspace.

---

### VS Code / GitHub Copilot

`<workspace>/.vscode/mcp.json`:

```json
{
  "servers": {
    "task-offloader": {
      "type": "stdio",
      "command": "<venv>/Scripts/task-offloader",
      "args": [
        "--workspace", "<workspace>",
        "--profile",   "<workspace>/.task-offloader/profile.toml",
        "mcp"
      ]
    }
  }
}
```

> **Windows:** command value is `<venv>\Scripts\task-offloader.exe`.

Reload VS Code. The server appears under **GitHub Copilot → MCP Servers**.

---

### Claude Desktop

Config file locations:

| OS | Path |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/claude/claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "task-offloader": {
      "type": "stdio",
      "command": "<venv>/bin/task-offloader",
      "args": [
        "--workspace", "<workspace>",
        "--profile",   "<workspace>/.task-offloader/profile.toml",
        "mcp"
      ]
    }
  }
}
```

`init --client 2` also copies `CLAUDE.md` delegation rules into the workspace root.

---

### Cursor

`<workspace>/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "task-offloader": {
      "type": "stdio",
      "command": "<venv>/bin/task-offloader",
      "args": [
        "--workspace", "<workspace>",
        "--profile",   "<workspace>/.task-offloader/profile.toml",
        "mcp"
      ]
    }
  }
}
```

`init --client 3` also copies `.cursor/rules/task-offloader.mdc` (has `alwaysApply: true`).

---

### Antigravity / Gemini

`init --client 4` copies:
- `rules/task-offloader.md` — loaded automatically by Antigravity
- `skills/task-offloader/SKILL.md` — invoked when the agent sees large files or log paths

For MCP server registration in Antigravity's agent config, see [Integration Guide](integration.md).


---

## Restarting the MCP server

```bash
task-offloader restart
```

Stops the running MCP server. Your AI client will automatically reconnect and restart it on the next tool call. Use this after editing `profile.toml` or changing the switch state, when a full `upgrade` isn't needed.

---

## Multiple workspaces

Each workspace needs its own `.task-offloader/`; the agent binary is shared.

```bash
cd <workspace-B>
task-offloader init
```

Set a distinct `profile.name` in each `profile.toml` so audit logs identify the workspace. Full layout reference: [Workspace Config](workspace-config.md).
