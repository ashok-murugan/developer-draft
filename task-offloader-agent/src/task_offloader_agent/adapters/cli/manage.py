"""upgrade and uninstall commands for task-offloader."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _find_repo_root() -> Path | None:
    """
    Infer the task-offloader-agent repo root from the running Python executable.

    Layout assumed by pip install -e .:
        <repo>/
            .git  (or parent has .git for sub-repo like developer-draft)
            .venv/
                Scripts/ or bin/
                    python.exe  <- sys.executable
    """
    venv_dir = Path(sys.executable).parent.parent  # .venv/
    repo_dir = venv_dir.parent                      # task-offloader-agent/

    # .git may be in repo_dir itself or in its parent (monorepo case)
    for candidate in (repo_dir, repo_dir.parent):
        if (candidate / ".git").exists():
            return repo_dir   # always return the package dir, not the git root
    return None


def _find_git_root(repo_dir: Path) -> Path | None:
    for candidate in (repo_dir, repo_dir.parent):
        if (candidate / ".git").exists():
            return candidate
    return None


# ---------------------------------------------------------------------------
# stop service
# ---------------------------------------------------------------------------

def _stop_service() -> None:
    """Kill any running task-offloader MCP server processes."""
    system = platform.system()
    print("Stopping task-offloader service...")

    if system == "Windows":
        # taskkill finds processes by image name; /F = force, /T = include children
        result = subprocess.run(
            ["taskkill", "/F", "/T", "/IM", "task-offloader.exe"],
            capture_output=True, text=True,
        )
        if "not found" in result.stderr.lower() or "no tasks" in result.stdout.lower():
            print("  (no running service found)")
        else:
            print(f"  {result.stdout.strip() or result.stderr.strip()}")
    else:
        # POSIX: pkill matches the script/entry-point name
        result = subprocess.run(
            ["pkill", "-f", "task-offloader.*mcp"],
            capture_output=True, text=True,
        )
        if result.returncode == 1:
            print("  (no running service found)")
        else:
            print("  stopped.")

    print()


# ---------------------------------------------------------------------------
# upgrade
# ---------------------------------------------------------------------------

def run_upgrade() -> int:
    """Stop service, git pull, then reinstall."""
    repo_dir = _find_repo_root()
    if repo_dir is None:
        print(
            "error: cannot locate the task-offloader-agent repo from the running binary.\n"
            "Manually run: git -C <repo> pull && pip install -e <repo>",
            file=sys.stderr,
        )
        return 2

    git_root = _find_git_root(repo_dir)
    if git_root is None:
        print(
            f"error: no .git directory found at {repo_dir} or {repo_dir.parent}.\n"
            f"Manually run: git -C {repo_dir} pull",
            file=sys.stderr,
        )
        return 2

    print(f"Repo:   {repo_dir}")
    print(f"Git at: {git_root}")
    print()

    # --- stop service ---
    _stop_service()

    # --- git pull ---
    print("Pulling latest changes...")
    result = subprocess.run(["git", "-C", str(git_root), "pull"])
    if result.returncode != 0:
        print("error: git pull failed.", file=sys.stderr)
        return result.returncode

    print()

    # --- pip install -e . ---
    # On Windows the running .exe is locked by the OS, so pip cannot replace it
    # while this process is alive.  Print manual instructions instead.
    if platform.system() == "Windows":
        print()
        print("Windows: the running executable is locked and cannot replace itself.")
        print("Open a NEW terminal and run:")
        print(f'  pip install -e "{repo_dir}"')
        print()
        print("Then restart your AI client to pick up any MCP protocol changes.")
        return 0

    print("Reinstalling package...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", str(repo_dir)],
        capture_output=False,
    )
    if result.returncode != 0:
        print("error: pip install failed.", file=sys.stderr)
        return result.returncode

    # Show new version
    print()
    result = subprocess.run(
        [sys.executable, "-m", "task_offloader_agent", "--version"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"Upgraded to: {result.stdout.strip()}")

    print("\nDone. Restart your AI client to pick up any MCP protocol changes.")
    return 0


# ---------------------------------------------------------------------------
# uninstall
# ---------------------------------------------------------------------------

def run_uninstall() -> int:
    """Stop service, uninstall the package, and delete the clone directory."""
    repo_dir = _find_repo_root()

    print("This will:")
    print("  1. Stop any running task-offloader MCP service")
    print("  2. Uninstall task-offloader-agent from the current virtual environment")
    if repo_dir:
        print(f"  3. Delete the clone directory: {repo_dir}")
    print()
    print("What will NOT be removed:")
    print("  - Workspace configs (.task-offloader/ inside your projects)")
    print("  - Ollama and its models")
    print()

    try:
        confirm = input("Type 'yes' to continue, anything else to abort: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return 0

    if confirm != "yes":
        print("Aborted.")
        return 0

    print()

    # --- stop service ---
    _stop_service()

    # --- pip uninstall ---
    print("Uninstalling package...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "task-offloader-agent", "-y"],
    )
    if result.returncode != 0:
        print("error: pip uninstall failed.", file=sys.stderr)
        return result.returncode

    print("Package uninstalled.")
    print()

    # --- delete clone directory ---
    if repo_dir and repo_dir.exists():
        print(f"Deleting clone: {repo_dir} ...")
        try:
            shutil.rmtree(repo_dir)
            print("Clone deleted.")
        except OSError as exc:
            print(f"warning: could not fully delete {repo_dir}: {exc}", file=sys.stderr)
            print("You may need to delete it manually.")
    print()

    print("Uninstalled successfully.")
    print("The 'task-offloader' command is no longer available.")
    print()
    print("To clean up workspace configs in each project:")
    print("  Remove-Item -Recurse -Force .task-offloader  (Windows)")
    print("  rm -rf .task-offloader                       (macOS/Linux)")
    return 0