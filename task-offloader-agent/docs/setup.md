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

## Multiple workspaces

Each workspace needs its own `.task-offloader/`; the agent binary is shared.

```bash
cd <workspace-B>
task-offloader init
```

Set a distinct `profile.name` in each `profile.toml` so audit logs identify the workspace. Full layout reference: [Workspace Config](workspace-config.md).
