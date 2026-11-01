# Setup Guide

## Prerequisites

| Requirement | Notes |
|---|---|
| Python >= 3.12 | `python --version` |
| [Ollama](https://ollama.com) running | `ollama serve` or system service |
| At least one model pulled | `ollama list` |
| A workspace directory | Any project folder |

---

## Step 1 -- Pull a model

```bash
ollama pull qwen2.5-coder:7b
ollama list                     # confirm it appears
```

For model comparisons and hardware requirements, see [Model Guide](models.md).

---

## Step 2 -- Install the agent

```powershell
# PowerShell
cd task-offloader-agent
python -m venv .venv
.venv\Scripts\activate
pip install -e .
task-offloader --version
```

```bash
# bash
cd task-offloader-agent
python -m venv .venv
source .venv/bin/activate
pip install -e .
task-offloader --version
```

---

## Step 3 -- Create workspace config

`.task-offloader/` lives inside **your workspace**, not this repo.

```powershell
# PowerShell
mkdir <workspace>\.task-offloader
copy assets\workspace\profile.toml <workspace>\.task-offloader\
copy assets\workspace\task-offloader.ps1 <workspace>\.task-offloader\
```

```bash
# bash
mkdir -p <workspace>/.task-offloader
cp assets/workspace/profile.toml <workspace>/.task-offloader/
```

Open `<workspace>/.task-offloader/profile.toml` and set at minimum:

```toml
[inference]
model   = "qwen2.5-coder:7b"
num_ctx = 16384
```

Full profile key reference: [Configuration Reference -- profile.toml](configuration.md#profiletoml--full-reference).

---

## Step 4 -- Validate profile

```bash
task-offloader \
  --workspace <workspace> \
  --profile <workspace>/.task-offloader/profile.toml \
  profile check
```

Fix any reported errors before proceeding.

---

## Step 5 -- Wire to your AI client

Replace `<venv>` with the absolute path to your `.venv` and `<workspace>` with the absolute path to your workspace.

---

### VS Code / GitHub Copilot

Copy the template:

```powershell
# PowerShell
mkdir <workspace>\.vscode -ErrorAction SilentlyContinue
copy assets\workspace\.vscode\mcp.json <workspace>\.vscode\mcp.json
```

```bash
# bash
mkdir -p <workspace>/.vscode
cp assets/workspace/.vscode/mcp.json <workspace>/.vscode/mcp.json
```

Edit `<workspace>/.vscode/mcp.json`:

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

> **Windows:** use `<venv>\Scripts\task-offloader.exe` as the command value.

Reload VS Code. The MCP server appears under **GitHub Copilot > MCP Servers**.

---

### Claude Desktop

Config file locations:

| OS | Path |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/claude/claude_desktop_config.json` |

Add to `claude_desktop_config.json`:

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

Copy the delegation rules template:

```powershell
# PowerShell
copy assets\workspace\CLAUDE.md <workspace>\CLAUDE.md
```

```bash
# bash
cp assets/workspace/CLAUDE.md <workspace>/CLAUDE.md
```

Edit `CLAUDE.md` to fill in the project overview and workspace conventions sections.

---

### Cursor

Copy the MCP config and rules:

```powershell
# PowerShell
mkdir <workspace>\.cursor\rules -ErrorAction SilentlyContinue
copy assets\workspace\.cursor\mcp.json <workspace>\.cursor\mcp.json
copy assets\workspace\.cursor\rules\task-offloader.mdc <workspace>\.cursor\rules\task-offloader.mdc
```

```bash
# bash
mkdir -p <workspace>/.cursor/rules
cp assets/workspace/.cursor/mcp.json <workspace>/.cursor/mcp.json
cp assets/workspace/.cursor/rules/task-offloader.mdc <workspace>/.cursor/rules/task-offloader.mdc
```

Edit `<workspace>/.cursor/mcp.json`:

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

`task-offloader.mdc` has `alwaysApply: true` in its frontmatter — Cursor loads it automatically.

---

### Antigravity / Gemini

Copy the rules and skill:

```powershell
# PowerShell
mkdir <workspace>\rules -ErrorAction SilentlyContinue
mkdir <workspace>\skills\task-offloader -ErrorAction SilentlyContinue
copy assets\workspace\rules\task-offloader.md <workspace>\rules\task-offloader.md
copy assets\workspace\skills\task-offloader\SKILL.md <workspace>\skills\task-offloader\SKILL.md
```

```bash
# bash
mkdir -p <workspace>/rules
mkdir -p <workspace>/skills/task-offloader
cp assets/workspace/rules/task-offloader.md <workspace>/rules/task-offloader.md
cp assets/workspace/skills/task-offloader/SKILL.md <workspace>/skills/task-offloader/SKILL.md
```

Antigravity loads `rules/*.md` automatically. The skill is invoked when the agent sees large files or log paths.

For wiring the MCP server into Antigravity's agent config, see [Integration Guide](integration.md).

---

## Multiple workspaces

Each workspace needs its own `.task-offloader/` config; the agent binary is shared.

```powershell
# PowerShell
mkdir <workspace-B>\.task-offloader
copy assets\workspace\profile.toml <workspace-B>\.task-offloader\
```

```bash
# bash
mkdir -p <workspace-B>/.task-offloader
cp assets/workspace/profile.toml <workspace-B>/.task-offloader/
```

Set a distinct `profile.name` in each `profile.toml` so audit logs identify the workspace. Full layout reference: [Workspace Config](workspace-config.md).