"""upgrade and uninstall commands for task-offloader."""

from __future__ import annotations

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
                    python.exe  ← sys.executable
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
# upgrade
# ---------------------------------------------------------------------------

def run_upgrade() -> int:
    """git pull + pip install -e ."""
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
    import platform as _platform
    if _platform.system() == "Windows":
        print()
        print("Windows: the running executable is locked and cannot replace itself.")
        print("Open a NEW terminal and run:")
        print(f"  pip install -e \"{repo_dir}\"")
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
    """Uninstall the package from the current venv."""
    repo_dir = _find_repo_root()

    print("This will uninstall task-offloader-agent from the current virtual environment.")
    print()
    print("What will NOT be removed:")
    print("  - The git clone (developer-draft/ folder)")
    print("  - Workspace configs (.task-offloader/ in your projects)")
    print("  - Ollama and its models")
    print()
    if repo_dir:
        print(f"Clone location:  {repo_dir}")
        print( "To also remove the clone:  Remove-Item -Recurse -Force <clone>  (Windows)")
        print( "                           rm -rf <clone>                        (macOS/Linux)")
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
    print("Uninstalling...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "task-offloader-agent", "-y"],
    )

    if result.returncode == 0:
        print()
        print("Uninstalled successfully.")
        print("The 'task-offloader' command is no longer available in this venv.")
        print()
        print("To clean up workspace configs in each project:")
        print("  Remove-Item -Recurse -Force .task-offloader  (Windows)")
        print("  rm -rf .task-offloader                       (macOS/Linux)")

    return result.returncode

