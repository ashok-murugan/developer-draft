"""summarize_logs: deterministic digest first, then a short model narrative over the digest only."""

from __future__ import annotations

import asyncio
from datetime import datetime

from ..application.runner import Outcome, RunContext
from ..core.budget import DIGEST_NARRATIVE_CAP, NUM_PREDICT, input_limit
from ..core.paths import PathError
from ..core.result import NEXT_STEPS, failed_result, make_result
from ..postprocess.citations import check_citations
from ..prefilter.logs import Filters, build_digest, compile_pattern, parse_ts
from ..providers.base import ProviderError
from .common import CallStats, call_model, cap_words

REVIEW = "narrative-only"
NARRATIVE_WORDS = 150


def parse_when(raw: str | None, name: str) -> datetime | None:
    if not raw or not raw.strip():
        return None
    value = parse_ts(raw)
    if value is None:
        raise ValueError(f"`{name}` is not an ISO date/time: {raw!r} (example: 2026-05-11T09:24:00)")
    return value


def cap_tokens(text: str, counter, cap: int) -> tuple[str, int, bool]:
    """Keep whole lines of `text` up to `cap` tokens."""
    lines = text.splitlines()
    counts = counter.count_many(lines) if lines else []
    total = sum(counts) + len(counts)
    if total <= cap:
        return text, total, False
    kept, used = [], 0
    for line, n in zip(lines, counts):
        if used + n + 1 > cap - 20:
            break
        kept.append(line)
        used += n + 1
    kept.append("[digest cut here for the narrative]")
    return "\n".join(kept), used, True


async def run_logs(ctx: RunContext, files: list[str], since: str | None, until: str | None,
                   pattern: str | None, correlation_id: str | None, narrate: bool) -> Outcome:
    settings, counter, guard = ctx.env.settings, ctx.env.counter, ctx.env.guard
    profile, redactor = ctx.env.profile, ctx.env.redactor
    run_id = ctx.run_id
    files = [f for f in (files or []) if f and f.strip()]
    metrics: dict = {"files_in": len(files)}
    if not files:
        return Outcome(failed_result(run_id, "`files` is empty.", REVIEW, code="invalid_input"), metrics)
    if len(files) > profile.log_max_files:
        return Outcome(failed_result(run_id, f"at most {profile.log_max_files} log files per call.", REVIEW,
                                     code="invalid_input"), metrics)
    try:
        pairs = []
        for raw in files:
            real = guard.resolve_read(raw, under=profile.log_dirs, under_label=profile.log_dir_labels)
            label = guard.label(real)
            if label not in (p[0] for p in pairs):
                pairs.append((label, real))
        filters = Filters(since=parse_when(since, "since"), until=parse_when(until, "until"),
                          pattern=compile_pattern(pattern),
                          correlation_id=(correlation_id or "").strip() or None)
    except (PathError, ValueError) as exc:
        return Outcome(failed_result(run_id, f"{exc}.", REVIEW, code="invalid_input"), metrics)

    steps = 2 if narrate else 1
    await ctx.progress(0, steps, "filtering the logs")
    digest = await asyncio.to_thread(build_digest, pairs, filters, profile.log_formats, guard.open_checked)
    markdown, redacted = redactor.redact(digest.markdown)
    run_dir = guard.ensure_run_path(ctx.run_dir)
    run_dir.mkdir(parents=True, exist_ok=False)
    digest_path = run_dir / "digest.md"
    digest_path.write_text(markdown, encoding="utf-8")
    digest_label = guard.label(digest_path)
    digest_tokens = counter.count(markdown)
    await ctx.progress(1, steps, "digest written")

    warnings = list(digest.warnings)
    if redacted:
        warnings.append("redacted in digest: " + ", ".join(f"{k} x{n}" for k, n in sorted(redacted.items())))
    metrics.update(input_chars=digest.input_chars, digest_chars=len(markdown),
                   entries=digest.entries, lines_read=digest.lines_read)
    if digest.lines_read > 0 and digest.entries == 0:
        warnings.append(f"0 of {digest.lines_read:,} lines matched — check your pattern or time range")
    elif digest.lines_read > 0 and digest.entries < digest.lines_read // 100:
        warnings.append(f"{digest.entries} of {digest.lines_read:,} lines matched "
                        f"({digest.entries * 100 // digest.lines_read}%)")
    num_predict = NUM_PREDICT["logs_narrative"]
    budget = {"digest_tokens": digest_tokens, "narrative_cap": DIGEST_NARRATIVE_CAP,
              "input_limit": input_limit(settings.num_ctx, num_predict), "tokenizer": counter.kind}

    answer = None
    citations: list[str] = []
    partial = False
    narrative = "skipped (narrate=false)"
    if narrate and digest.entries == 0:
        narrative = "skipped (no matching lines)"
    elif narrate:
        text, used, was_cut = cap_tokens(markdown, counter, DIGEST_NARRATIVE_CAP)
        budget["input_tokens"] = used
        if was_cut:
            warnings.append(f"the narrative saw only the first {used:,} tokens of the digest")
        focus = (f"The developer is tracing correlation id {filters.correlation_id}."
                 if filters.correlation_id else "The developer wants a first pass over these logs.")
        stats = CallStats()

        def build(note: str) -> str:
            return ctx.env.prompts.get("logs_narrative").substitute(
                focus=focus, max_words=NARRATIVE_WORDS, retry_note=note, digest=text)
        try:
            reply = await call_model(ctx, stats, ctx.env.prompts.get("logs_system").template, build,
                                     num_predict, NARRATIVE_WORDS // 2)
        except ProviderError as exc:
            narrative = f"not_run ({exc})"
            warnings.append(f"narrative not run: {exc}; the digest is complete without it")
            partial = True
        else:
            text_out, cut = cap_words(reply.text, NARRATIVE_WORDS)
            if cut:
                warnings.append(f"narrative cut at {NARRATIVE_WORDS} words")
            report = check_citations(text_out, digest.files)
            if report.invalid:
                warnings.append(f"{len(report.invalid)} invalid citation(s) removed")
            if not report.citations:
                warnings.append("the narrative has no valid citation; treat it as unverified")
                partial = True
            answer, red = redactor.redact(report.answer)
            if red:
                warnings.append("redacted in narrative: " + ", ".join(f"{k} x{n}" for k, n in sorted(red.items())))
            citations = report.citations
            metrics["cited_chars"] = report.cited_chars
            narrative = "ok"
            warnings += stats.warnings
            partial = partial or bool(stats.warnings)
        metrics.update(stats.metrics(num_predict))
        budget.update(output_tokens=stats.output_tokens, output_limit=num_predict,
                      done_reason=stats.done_reason)
        await ctx.progress(2, steps, "narrative done")

    levels = ", ".join(f"{n} {lvl}" for lvl, n in sorted(digest.levels.items())) or "none"
    timeline = f"{digest.timeline} on the correlation timeline, " if filters.correlation_id else ""
    summary = (f"Digest of {digest.entries} entries ({levels}) from {len(pairs)} file(s): {timeline}"
               f"{digest.groups} message groups. Narrative: {narrative.split(' (')[0]}.")
    result = make_result(
        run_id, "partial" if partial else "ok", summary, review=REVIEW,
        answer=answer, citations=citations, files=[digest_label],
        checks={"digest": "deterministic", "narrative": narrative,
                "citations": f"{len(citations)} valid" if answer is not None else "not_run",
                "redaction": "applied"},
        budget=budget, warnings=warnings,
        next_step=NEXT_STEPS[REVIEW].format(digest=digest_label))
    return Outcome(result, metrics)
