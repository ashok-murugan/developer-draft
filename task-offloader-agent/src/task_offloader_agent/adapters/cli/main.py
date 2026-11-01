"""Command line `task-offloader`: the MCP server, switch commands, CLI versions of the tools, profile check."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from ... import __version__
from ...application import lifecycle, report, service
from ...core import audit, retention, switch
from ...core.config import Config, load_config
from ...core.errors import ConfigError

EXIT_CONFIG = 2


def _print_tools(state: switch.SwitchState) -> None:
    print(f"{'tool':<16} {'flag':<6} {'source':<8} effective")
    for row in switch.tool_rows(state):
        source = "file" if row["set_in_file"] else "default"
        print(f"{row['tool']:<16} {str(row['flag']).lower():<6} {source:<8} {row['effective']}")


def _print_state(config: Config) -> None:
    settings = config.settings
    env = lifecycle.build_env(config)
    state = switch.read_switch(settings)
    print(f"profile: {config.profile.name} ({settings.profile_path})")
    print(f"mode: {state.mode}  (from {state.source}: "
          f"{settings.switch_file if state.source == 'file' else 'TASK_OFFLOADER_MODE'})")
    if state.error:
        print(f"ERROR: {state.error} -> treated as off")
    for warning in state.warnings:
        print(f"warning: {warning}")
    health = asyncio.run(env.provider.health())
    if not health["reachable"]:
        print(f"ollama: NOT reachable at {settings.provider_url} ({health.get('error')})")
    else:
        print(f"ollama: reachable; model {health['model']}: {'present' if health['model_present'] else 'MISSING'}")
    print(f"num_ctx {settings.num_ctx}, timeout {settings.timeout_s:.0f} s, tokenizer: {env.counter.kind}")
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
    sub.add_parser("report", help="measurement report from the audit log")
    p = sub.add_parser("clean", help="delete run folders older than the retention period")
    p.add_argument("--days", type=int)
    p = sub.add_parser("apply", help="copy a draft into place (not available yet)")
    p.add_argument("run_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = _parser().parse_args(argv)

    if args.cmd == "mcp":
        from ..mcp import server  # imported here: the CLI commands do not need the MCP SDK

        return server.run(args.workspace, args.profile, args.mode)

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
            print(report.build(settings), end="")
        elif args.cmd == "clean":
            removed, errors = retention.clean(settings, args.days)
            days = settings.retention_days if args.days is None else args.days
            print(f"removed {len(removed)} run(s) older than {days} days from {settings.out_dir}"
                  + (f"; {errors} could not be removed" if errors else ""))
        elif args.cmd == "apply":
            print("apply is not available: drafting tools are not built.", file=sys.stderr)
            return 2
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
