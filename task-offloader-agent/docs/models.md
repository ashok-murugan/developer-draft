# Model Recommendation Guide

Works with any instruction-following model available in Ollama. No single recommended model -- start small and graduate only if needed.

## Comparison table

| Model tag | VRAM / RAM | Speed (7B machine) | Strengths | Weaknesses |
|---|---|---|---|---|
| `phi3:mini` | ~2 GB | Very fast | Ultra-low footprint, good for quick status checks | Lower reasoning depth on complex code |
| `codellama:7b` | ~4 GB | Fast | Compact, wide OS support | Older training cut; sometimes verbose |
| `deepseek-coder:6.7b` | ~4 GB | Fast | Strong at code understanding and explanation | Slightly weaker on plain prose / log summaries |
| `qwen2.5-coder:7b` | ~5 GB | Fast | Good all-rounder for both code and logs | -- |
| `codellama:13b` | ~8 GB | Moderate | Better reasoning than 7B; good for architectural questions | Needs more RAM |
| `qwen2.5-coder:14b` | ~9 GB | Moderate | Noticeably better on multi-file analysis | Slower on CPU-only machines |
| `deepseek-coder:33b` | ~20 GB | Slow (CPU) | Highest quality code reasoning | Requires GPU |
| `qwen2.5-coder:32b` | ~20 GB | Slow (CPU) | Best overall quality | Requires GPU |

## Choose by task type

### Log triage (`summarize_logs`)

Pre-digested, highly structured input rarely exceeds a few thousand tokens. Any 4-9 GB model works. `phi3:mini` or `codellama:7b` if speed matters more than depth.

### Code / file questions (`local_ask`)

Longer context and better reasoning matter. Use 7B-14B for typical class or module questions; 14B+ if answers on complex multi-file problems are consistently missing detail.

### Quick status (`local_status`)

Does not call the model -- model choice is irrelevant.

## Choose by hardware

| Available VRAM / RAM | Suggested starting point |
|---|---|
| < 4 GB | Not recommended -- model will swap to disk |
| 4-6 GB | `phi3:mini`, `codellama:7b`, `deepseek-coder:6.7b` |
| 6-10 GB | `qwen2.5-coder:7b` (default suggestion) |
| 10-16 GB | `qwen2.5-coder:14b` or `codellama:13b` |
| 16+ GB (or GPU) | Any 33B / 32B model |

> **Tip:** `ollama ps` shows what is already loaded and how much VRAM it is using.

## Using multiple models in one workspace

Create multiple profile files:

```
.task-offloader/
  profile.toml            <- default: 7B model, all tools
  profile-large.toml      <- 14B model for deeper code analysis
  profile-fast.toml       <- phi3:mini for quick log checks only
```

Select at startup:

```bash
task-offloader --workspace . --profile .task-offloader/profile-large.toml mcp
```

Or register multiple named MCP servers so the primary agent picks the right one per task type. Example: two servers in `.vscode/mcp.json` (see [setup.md](setup.md)):

```json
{
  "servers": {
    "task-offloader-fast": {
      "type": "stdio",
      "command": "<venv>/Scripts/task-offloader.exe",
      "args": ["--workspace", "${workspaceFolder}",
               "--profile",   "${workspaceFolder}/.task-offloader/profile-fast.toml",
               "mcp"]
    },
    "task-offloader-large": {
      "type": "stdio",
      "command": "<venv>/Scripts/task-offloader.exe",
      "args": ["--workspace", "${workspaceFolder}",
               "--profile",   "${workspaceFolder}/.task-offloader/profile-large.toml",
               "mcp"]
    }
  }
}
```

## Benchmarking

```bash
# Log summary
task-offloader \
  --workspace <your-workspace> \
  --profile   <your-workspace>/.task-offloader/profile.toml \
  logs logs/app.log

# Code question
task-offloader \
  --workspace <your-workspace> \
  --profile   <your-workspace>/.task-offloader/profile.toml \
  ask src/core/engine.py --question "What are the main failure modes?"
```

Check the `budget` field for token counts and latency; `review` and `citations` for answer quality.

## How to switch models

1. Open `.task-offloader/profile.toml`.
2. Update `model` to any tag from `ollama list`.
3. Update `num_ctx` to match the model's context window.
4. Restart the MCP server.

```toml
[inference]
model   = "qwen2.5-coder:14b"   # <- change this
num_ctx = 32768                  # <- match the model's context window
```

Validate before restarting:

```bash
task-offloader --workspace . --profile .task-offloader/profile.toml profile check
```

## Optional: tuned parameters via Modelfile

Copy [`assets/ollama/Modelfile.example`](../assets/ollama/Modelfile.example) into your workspace at `.task-offloader/ollama/Modelfile`, then:

```bash
ollama create <your-chosen-name> -f .task-offloader/ollama/Modelfile
# Reference in profile.toml: model = "<your-chosen-name>"
```

See [workspace-config.md](workspace-config.md#the-ollama-modelfile) for Modelfile placement details and [configuration.md](configuration.md) for all `[inference]` keys.