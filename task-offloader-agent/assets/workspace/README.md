# Workspace Template

This directory is the **template for your workspace's `.task-offloader/` config directory**.

Copy its contents into any project workspace where you want TaskOffloaderAgent to run.

### Step 1 — Copy the core config

```powershell
# Windows (PowerShell)
$ws = "C:\path\to\your-workspace"
New-Item -ItemType Directory "$ws\.task-offloader" -Force
Copy-Item "assets\workspace\profile.toml"        "$ws\.task-offloader\"
Copy-Item "assets\workspace\task-offloader.ps1"  "$ws\.task-offloader\"
```

```bash
# macOS / Linux
ws="/path/to/your-workspace"
mkdir -p "$ws/.task-offloader"
cp assets/workspace/profile.toml "$ws/.task-offloader/"
```

Edit `profile.toml` in your workspace — set your model tag, deny paths, and log formats.

### Step 2 — Copy your AI client's config

Pick the folder that matches your AI client and copy it into the workspace root (not into `.task-offloader/`):

**VS Code Copilot:**
```powershell
# Windows
Copy-Item -Recurse "assets\workspace\.vscode"  "$ws\.vscode"
Copy-Item -Recurse "assets\workspace\.github"  "$ws\.github"
```
```bash
# macOS / Linux
cp -r assets/workspace/.vscode  "$ws/.vscode"
cp -r assets/workspace/.github  "$ws/.github"
```

**Claude:**
```powershell
Copy-Item "assets\workspace\CLAUDE.md"  "$ws\CLAUDE.md"
```
```bash
cp assets/workspace/CLAUDE.md  "$ws/CLAUDE.md"
```

**Cursor:**
```powershell
Copy-Item -Recurse "assets\workspace\.cursor"  "$ws\.cursor"
```
```bash
cp -r assets/workspace/.cursor  "$ws/.cursor"
```

**Antigravity / Gemini:**
```powershell
New-Item -ItemType Directory "$ws\rules" -Force
Copy-Item "assets\workspace\rules\task-offloader.md"  "$ws\rules\"
# Optional skill file:
New-Item -ItemType Directory "$ws\skills\task-offloader" -Force
Copy-Item "assets\workspace\skills\task-offloader\SKILL.md"  "$ws\skills\task-offloader\"
```
```bash
mkdir -p "$ws/rules" "$ws/skills/task-offloader"
cp assets/workspace/rules/task-offloader.md          "$ws/rules/"
cp assets/workspace/skills/task-offloader/SKILL.md   "$ws/skills/task-offloader/"
```

> After copying, edit the `<venv>` and `<workspace>` placeholders in any `.json` MCP config files.
> See [docs/setup.md — Step 5](../../docs/setup.md#step-5--register-the-mcp-server-in-your-ai-client) for full per-client instructions.

---

## What's in this directory

### Core config (all users)

| File | Purpose | Required? |
|---|---|---|
| `profile.toml` | Main workspace config — model, security rules, log formats | **Yes** |
| `task-offloader.ps1` | Windows convenience wrapper — shorthand for the full CLI | Optional |
| `prompts/logs_system.txt` | Override the packaged log summary system prompt | Optional |
| `cache/README.txt` | Instructions for downloading a tokenizer file | Optional |

### AI client rules & MCP registration (copy for your client)

| File / folder | Client | Purpose |
|---|---|---|
| `.github/copilot-instructions.md` | VS Code Copilot | Rules — when and how to delegate |
| `.vscode/mcp.json` | VS Code Copilot | Registers the MCP server |
| `.vscode/settings.json` | VS Code Copilot | Enables MCP in VS Code |
| `CLAUDE.md` | Claude Desktop | Project instructions — when and how to delegate |
| `.cursor/mcp.json` | Cursor | Registers the MCP server |
| `.cursor/rules/task-offloader.mdc` | Cursor | Rules — when and how to delegate |
| `rules/task-offloader.md` | Gemini / Antigravity | Rules — when and how to delegate |

> All rule files contain the same delegation logic adapted to each client's format.
> Edit `<venv>` and `<workspace>` placeholders in the MCP config files before use.

---

## What goes in `.task-offloader/` after setup

```
<your-workspace>/
  .task-offloader/           ← created by you, NOT part of this repo
    profile.toml             ← copied from here, edited for your workspace
    task-offloader.ps1       ← optional Windows wrapper
    prompts/                 ← optional prompt overrides
      logs_system.txt
    cache/                   ← optional tokenizer file
      tokenizer.json
    ollama/                  ← optional Modelfile for tuned inference params
      Modelfile
    run/                     ← created automatically at runtime
      switch.json            ← on/off state (persists across restarts)
      audit.jsonl            ← call audit log
      <run-id>/              ← per-call output (cleaned up after retention_days)
```

> **Add `run/` and `cache/` to your workspace's `.gitignore`** so runtime files
> are not committed:
>
> ```gitignore
> .task-offloader/run/
> .task-offloader/cache/
> ```

---

## Multiple profiles

You can have more than one profile file to use different models for different tasks:

```
.task-offloader/
  profile.toml           ← default (all tools, general model)
  profile-fast.toml      ← small model for quick log triage
  profile-large.toml     ← larger model for deep code analysis
```

Select a profile:

```bash
task-offloader --workspace . --profile .task-offloader/profile-large.toml mcp
```

---

## Full reference

- [Setup Guide](../../docs/setup.md) — step-by-step walkthrough
- [Workspace Config Guide](../../docs/workspace-config.md) — complete directory reference
- [Configuration Reference](../../docs/configuration.md) — every profile key explained
- [Model Recommendation Guide](../../docs/models.md) — which model for which task

