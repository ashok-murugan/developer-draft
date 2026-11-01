"""Interactive `task-offloader init` flow: prompts, Ollama probe, client detection."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from ...application.init_workspace import CLIENTS, InitResult, find_venv_bin, init_workspace

_DEFAULT_MODEL = "qwen2.5-coder:7b"
_OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"


# ---------------------------------------------------------------------------
# Ollama probe
# ---------------------------------------------------------------------------

def _probe_ollama() -> list[str]:
    """Return sorted list of pulled model tags, or [] if Ollama is unreachable."""
    try:
        with urllib.request.urlopen(_OLLAMA_TAGS_URL, timeout=2) as resp:
            data = json.loads(resp.read())
        return sorted(m["name"] for m in data.get("models", []))
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------------------
# Client detection
# ---------------------------------------------------------------------------

def _detect_clients(workspace: Path) -> list[int]:
    """Return client numbers whose config directories already exist."""
    detected = []
    checks = {
        1: workspace / ".vscode",
        2: workspace / "CLAUDE.md",
        3: workspace / ".cursor",
        4: workspace / "rules",
    }
    for n, path in checks.items():
        if path.exists():
            detected.append(n)
    return detected


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

def _ask(prompt: str, default: str) -> str:
    try:
        answer = input(f"{prompt} [{default}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return answer if answer else default


def _print_client_menu(detected: list[int]) -> None:
    print("\nWhich AI client(s) to wire?")
    print("Enter numbers space-separated, or Enter to skip.\n")
    for c in CLIENTS:
        marker = " (detected)" if c["n"] in detected else ""
        print(f"  {c['n']}  {c['label']:<30}  {c['hint']}{marker}")
    print(f"  5  All of the above")


def _parse_client_input(raw: str) -> list[int]:
    chosen = []
    for tok in raw.split():
        try:
            n = int(tok)
            if 1 <= n <= 5:
                chosen.append(n)
        except ValueError:
            pass
    return list(dict.fromkeys(chosen))  # deduplicate, preserve order


# ---------------------------------------------------------------------------
# Result printer
# ---------------------------------------------------------------------------

def _action_symbol(action: str) -> str:
    return {
        "created":      "  created ",
        "merged":       "  merged  ",
        "skipped":      "  skipped ",
        "would-create": "  [dry]   ",
        "would-merge":  "  [dry]   ",
        "would-skip":   "  [skip]  ",
    }.get(action, "  ?       ")


def print_results(results: list[InitResult], workspace: Path) -> None:
    for r in results:
        try:
            rel = r.path.relative_to(workspace)
        except ValueError:
            rel = r.path
        note = f"  ({r.note})" if r.note else ""
        print(f"{_action_symbol(r.action)}{rel}{note}")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_init(
    *,
    model_flag: str | None,
    client_flag: list[int] | None,
    force: bool,
    dry_run: bool,
) -> int:
    """Run the init flow. Returns CLI exit code."""
    workspace = Path.cwd().resolve()
    name = workspace.name

    print(f"\nWorkspace:  {workspace}  (name: {name!r})")
    print(f"Config dir: .task-offloader/  (fixed)")

    # --- venv binary ---
    venv_bin = find_venv_bin(workspace)
    if venv_bin is None:
        raw = _ask("Path to task-offloader binary", "").strip()
        if not raw:
            print("error: cannot find task-offloader binary.", file=sys.stderr)
            return 2
        venv_bin = Path(raw).expanduser().resolve()
        if not venv_bin.exists():
            print(f"error: {venv_bin} does not exist.", file=sys.stderr)
            return 2
    print(f"Agent bin:  {venv_bin}")

    # --- model ---
    if model_flag:
        model = model_flag
    else:
        models = _probe_ollama()
        if models:
            model_list = "  ".join(models[:5])
            print(f"\nOllama models: {model_list}")
            model = _ask("Model", models[0])
        else:
            print("\nOllama not reachable — using default model placeholder.")
            model = _DEFAULT_MODEL

    print(f"Model:      {model}\n")

    # --- clients ---
    if client_flag is not None:
        clients = client_flag
    else:
        detected = _detect_clients(workspace)
        _print_client_menu(detected)
        raw = _ask("Client(s)", "1")
        clients = _parse_client_input(raw)
        if not clients:
            print("No client selected — skipping client wiring.")

    # --- run ---
    if dry_run:
        print("\n[dry-run] No files will be written.\n")

    results = init_workspace(
        workspace=workspace,
        model=model,
        venv_bin=venv_bin,
        clients=clients,
        force=force,
        dry_run=dry_run,
    )

    print()
    print_results(results, workspace)
    print()

    if not dry_run:
        profile_path = workspace / ".task-offloader" / "profile.toml"
        cmd_path     = workspace / ".task-offloader" / "task-offloader.cmd"
        print("Next steps:")
        print(f"  1. Review {profile_path.relative_to(workspace)} — add deny_paths for sensitive folders")
        print( "  2. Restart your AI client to pick up the new MCP server")
        print( "  3. Validate — choose one:")
        print(f"       Windows:  .task-offloader\\task-offloader.cmd profile check")
        print( "       Any shell: task-offloader --workspace . --profile .task-offloader\\profile.toml profile check")
    return 0