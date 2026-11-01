"""Command line `task-offloader`: the MCP server, switch commands, CLI versions of the tools, profile check."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from ... import __version__
from ...application import lifecycle, report, service
from ...core import audit, retention, switch
from ...core.config import Config, load_config
from ...core.errors import ConfigError

EXIT_CONFIG = 2


# ---------------------------------------------------------------------------
# colour helpers  (ANSI SGR; disabled by NO_COLOR env var or non-tty stdout)
# ---------------------------------------------------------------------------
_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


_DIM    = "2"
_GREEN  = "32"
_YELLOW = "33"
_RED    = "31"
_CYAN   = "36"


def _print_tools(state: switch.SwitchState) -> None:
    rows = switch.tool_rows(state)
    # dynamic column width — never truncate long tool names
    name_w = max(len(r["tool"]) for r in rows) + 2

    header = f"{'tool':<{name_w}} {'flag':<6} {'source':<8} effective"
    print(_c(_DIM, header))

    for row in rows:
        source    = "file" if row["set_in_file"] else "default"
        flag_str  = str(row["flag"]).lower()
        eff       = row["effective"]

        # pad *before* colourising so ANSI bytes don't shift column widths
        name_p   = f"{row['tool']:<{name_w}}"
        flag_p   = f"{flag_str:<6}"
        source_p = f"{source:<8}"

        name_col = _c(_DIM, name_p)   if not row["built"] else name_p
        flag_col = _c(_GREEN, flag_p) if row["flag"]      else _c(_DIM, flag_p)

        if eff == "on":
            eff_col = _c(_GREEN, eff)
        elif eff == "not built":
            eff_col = _c(_DIM, eff)
        elif eff.startswith("off"):
            eff_col = _c(_YELLOW, eff)
        else:
            eff_col = eff

        print(f"{name_col}{flag_col}{source_p}{eff_col}")


def _print_state(config: Config) -> None:
    settings = config.settings
    env = lifecycle.build_env(config)
    state = switch.read_switch(settings)

    mode_col = (
        _c(_GREEN,  state.mode) if state.mode == "auto"   else
        _c(_YELLOW, state.mode) if state.mode == "manual" else
        _c(_RED,    state.mode)
    )
    print(f"{_c(_DIM, 'profile:')} {config.profile.name}  {_c(_DIM, str(settings.profile_path))}")
    src_label = settings.switch_file if state.source == "file" else "TASK_OFFLOADER_MODE"
    print(f"{_c(_DIM, 'mode:')}    {mode_col}  {_c(_DIM, f'(from {state.source}: {src_label})')}")

    if state.error:
        print(_c(_RED, f"ERROR: {state.error} -> treated as off"))
    for warning in state.warnings:
        print(_c(_YELLOW, f"warning: {warning}"))

    health = asyncio.run(env.provider.health())
    if not health["reachable"]:
        print(f"{_c(_DIM, 'ollama:')} {_c(_RED, 'NOT reachable')} at {settings.provider_url}"
              f"  ({health.get('error')})")
    else:
        model_state = _c(_GREEN, "present") if health["model_present"] else _c(_RED, "MISSING")
        print(f"{_c(_DIM, 'ollama:')} reachable  model {_c(_CYAN, health['model'])} {model_state}")

    print(_c(_DIM, f"num_ctx {settings.num_ctx}, timeout {settings.timeout_s:.0f} s,"
             f" tokenizer: {env.counter.kind}"))
    print()
    _print_tools(state)


def _print_profile(config: Config) -> None:
    profile, settings = config.profile, config.settings
    tokenizer = settings.tokenizer_file
    print(f"profile OK: {profile.name} (schema {profile.schema_version}, sha256 {profile.sha256[:12]})")
    print(f"  file:       {profile.path}")
    print(f"  model:      {settings.model}, num_ctx {settings.num_ctx}")
    print(f"  tokenizer:  {tokenizer if tokenizer else 'none (estimate)'}"
          + ("" if tokenizer is None or tokenizer.exists() else "  (file missing: token counts are estimates)"))
    print(f"  deny:       {len(profile.deny_paths)} path rule(s), {len(profile.deny_names)} name rule(s)")
    print(f"  redaction:  {len(profile.redaction_rules)} extra rule(s)")
    print(f"  logs:       {profile.log_dir_labels or 'none'}; {len(profile.log_formats)} format(s); "
          f"max {profile.log_max_files} file(s)")
    print(f"  prompts:    {profile.prompts_dir if profile.prompts_dir else 'packaged defaults'}")


async def _stderr_progress(done: float, total: float, message: str) -> None:
    print(f"[{done:.0f}/{total:.0f}] {message}", file=sys.stderr)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="task-offloader", description="TaskOffloaderAgent: switch and tools")
    parser.add_argument("--version", action="version", version=f"task-offloader {__version__}")
    parser.add_argument("--workspace", help="workspace folder (or TASK_OFFLOADER_WORKSPACE)")
    parser.add_argument("--profile", help="profile file inside the workspace (or TASK_OFFLOADER_PROFILE)")
    parser.add_argument("--mode", help="default mode when no switch file exists: auto, manual or off")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("mcp", help="run the MCP server on stdio")
    p = sub.add_parser("profile", help="profile commands")
    p.add_argument("action", choices=("check",))

    for mode in ("on", "off"):
        p = sub.add_parser(mode, help=f"switch the agent {mode}, or one tool with `{mode} <tool>`")
        p.add_argument("tool", nargs="?")
    sub.add_parser("manual", help="tools run only when the developer asks (#local)")
    sub.add_parser("status", help="mode, provider, every tool")
    sub.add_parser("tools", help="every tool with its flag and effective state")
    p = sub.add_parser("reset", help="remove a tool's entry so its default applies")
    p.add_argument("tool")

    p = sub.add_parser("ask", help="local_ask from the terminal")
    p.add_argument("instruction")
    p.add_argument("paths", nargs="*", help="files, optionally path:L120-L300")
    p.add_argument("--text")
    p.add_argument("--max-words", type=int, default=200)

    p = sub.add_parser("logs", help="summarize_logs from the terminal")
    p.add_argument("files", nargs="+")
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--pattern")
    p.add_argument("--correlation-id")
    p.add_argument("--no-narrate", action="store_true")

    p = sub.add_parser("rate", help="rate a local_ask/summarize_logs result")
    p.add_argument("run_id")
    p.add_argument("rating", choices=("good", "bad"))
    p = sub.add_parser("report", help="measurement report from the audit log")
    p.add_argument("--audit-file", help="path to an audit.jsonl file (cross-workspace)")
    p.add_argument("--fail-on-bad-rate", action="store_true",
                   help="exit 1 when more than half of rated results are bad for any tool")
    p = sub.add_parser("summary", help="daily call breakdown for the last N days")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--audit-file", help="path to an audit.jsonl file (cross-workspace)")
    sub.add_parser("rate-pending", help="interactively rate unrated ok/partial results")
    p = sub.add_parser("clean", help="delete run folders older than the retention period")
    p.add_argument("--days", type=int)
    p = sub.add_parser("apply", help="copy a draft into place (not available yet)")
    p.add_argument("run_id")

    p = sub.add_parser("init", help="set up TaskOffloaderAgent in the current workspace")
    p.add_argument("--model", help="Ollama model tag (skips model prompt)")
    p.add_argument("--client", nargs="*", type=int, metavar="N",
                   help="client number(s): 1=copilot 2=claude 3=cursor 4=antigravity 5=all")
    p.add_argument("--force", action="store_true",
                   help="overwrite existing client config files")
    p.add_argument("--dry-run", action="store_true",
                   help="print actions without writing")
    sub.add_parser("upgrade", help="pull latest code and reinstall")
    sub.add_parser("uninstall", help="remove task-offloader-agent from the current venv")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = _parser().parse_args(argv)

    if args.cmd == "mcp":
        from ..mcp import server  # imported here: the CLI commands do not need the MCP SDK

        return server.run(args.workspace, args.profile, args.mode)

    if args.cmd == "init":
        from .init import run_init  # lazy import - init does not need config

        return run_init(
            model_flag=getattr(args, "model", None),
            client_flag=getattr(args, "client", None),
            force=getattr(args, "force", False),
            dry_run=getattr(args, "dry_run", False),
        )
    if args.cmd == "upgrade":
        from .manage import run_upgrade
        return run_upgrade()
    if args.cmd == "uninstall":
        from .manage import run_uninstall
        return run_uninstall()
    try:
        config = load_config(workspace=args.workspace, profile=args.profile, mode=args.mode)
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    settings = config.settings

    try:
        if args.cmd == "profile":
            _print_profile(config)
        elif args.cmd in ("on", "off"):
            if args.tool:
                switch.set_tool(settings, args.tool, args.cmd == "on")
                spec = switch.TOOLS[args.tool]
                print(f"tools.{args.tool} = {str(args.cmd == 'on').lower()}"
                      + ("" if spec.built else "  (note: this tool is not built yet)"))
            else:
                switch.set_mode(settings, "auto" if args.cmd == "on" else "off")
                print(f"mode = {'auto' if args.cmd == 'on' else 'off'}")
            _print_tools(switch.read_switch(settings))
        elif args.cmd == "manual":
            switch.set_mode(settings, "manual")
            print("mode = manual")
            _print_tools(switch.read_switch(settings))
        elif args.cmd == "reset":
            switch.reset_tool(settings, args.tool)
            print(f"tools.{args.tool} reset to its default "
                  f"({str(switch.TOOLS[args.tool].default).lower()})")
            _print_tools(switch.read_switch(settings))
        elif args.cmd == "tools":
            _print_tools(switch.read_switch(settings))
        elif args.cmd == "status":
            _print_state(config)
        elif args.cmd == "ask":
            env = lifecycle.build_env(config)
            result = asyncio.run(service.ask(env, args.instruction, args.paths, args.text, args.max_words,
                                             requested_by_user=True, progress=_stderr_progress))
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.cmd == "logs":
            env = lifecycle.build_env(config)
            result = asyncio.run(service.summarize_logs(
                env, args.files, args.since, args.until, args.pattern, args.correlation_id,
                narrate=not args.no_narrate, requested_by_user=True, progress=_stderr_progress))
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.cmd == "rate":
            known = {e.get("run_id") for e in audit.read_all(settings) if e.get("event") == "call"}
            if args.run_id not in known:
                print(f"unknown run id: {args.run_id}", file=sys.stderr)
                return 1
            audit.write(settings, {"event": "rated", "run_id": args.run_id, "rating": args.rating})
            print(f"{args.run_id}: {args.rating}")
        elif args.cmd == "report":
            text, code = report.build(
                settings,
                audit_file=Path(args.audit_file) if getattr(args, "audit_file", None) else None,
                fail_on_bad_rate=getattr(args, "fail_on_bad_rate", False),
            )
            print(text, end="")
            if code:
                return code
        elif args.cmd == "summary":
            text = report.summary(
                settings,
                days=args.days,
                audit_file=Path(args.audit_file) if getattr(args, "audit_file", None) else None,
            )
            print(text, end="")
        elif args.cmd == "rate-pending":
            pending = report.pending_ratings(settings)
            if not pending:
                print("No unrated results.")
            else:
                for e in pending:
                    run_id = e.get("run_id", "?")
                    summ = e.get("summary", "(no summary)")
                    print(f"\n{run_id}: {summ}")
                    raw = input("  Rate (good/bad/skip) [skip]: ").strip() or "skip"
                    if raw in ("good", "bad"):
                        audit.write(settings, {"event": "rated", "run_id": run_id, "rating": raw})
                        print(f"  saved: {raw}")
        elif args.cmd == "clean":
            removed, errors = retention.clean(settings, args.days)
            days = settings.retention_days if args.days is None else args.days
            print(f"removed {len(removed)} run(s) older than {days} days from {settings.out_dir}"
                  + (f"; {errors} could not be removed" if errors else ""))
        elif args.cmd == "apply":
            print("apply is not available: drafting tools are not built.", file=sys.stderr)
            return 2
        elif args.cmd == "init":
            pass  # handled before config load
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
