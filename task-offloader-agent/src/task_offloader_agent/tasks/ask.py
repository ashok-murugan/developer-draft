"""local_ask: one short task over files or text, answered with citations."""

from __future__ import annotations

import asyncio
import re

from ..application.runner import Env, Outcome, RunContext
from ..core.budget import NUM_PREDICT, Source, input_limit, make_chunks
from ..core.paths import PathError
from ..core.result import failed_result, make_result, refused_result
from ..postprocess.citations import CitedFile, check_citations
from ..providers.base import ProviderError
from .common import CHAT_OVERHEAD, CallStats, call_model, cap_words

REVIEW = "spot-check-citations"
RANGE_RE = re.compile(r"^(?P<path>.+?):L(?P<start>\d+)(?:\s*-\s*L?(?P<end>\d+))?$")
MAX_FILE_BYTES = 5_000_000
MAX_PATHS = 10
MAX_INSTRUCTION_CHARS = 2000
NOTHING = "NOTHING RELEVANT"
SAFETY = 100  # tokens kept free for the retry note


def load_sources(env: Env, paths: list[str], text: str | None) -> list[Source]:
    sources: list[Source] = []
    for raw in paths:
        raw = raw.strip()
        match = RANGE_RE.match(raw)
        path_part = match.group("path") if match else raw
        real = env.guard.resolve_read(path_part)
        label = env.guard.label(real)
        with env.guard.open_checked(real) as handle:
            data = handle.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise PathError(f"{label} is larger than {MAX_FILE_BYTES // 1_000_000} MB; pass a line range")
        if b"\0" in data[:8192]:
            raise PathError(f"{label} looks like a binary file")
        lines = data.decode("utf-8", errors="replace").splitlines()
        total = len(lines)
        start, end = 1, total
        if match:
            start = int(match.group("start"))
            end = min(int(match.group("end") or start), total)
            if start < 1 or start > total or end < start:
                raise PathError(f"line range in {raw!r} is outside {label} ({total} lines)")
        sources.append(Source(label, start, lines[start - 1:end], total, [len(x) for x in lines]))
    if text:
        lines = text.splitlines()
        sources.append(Source("text", 1, lines, len(lines), [len(x) for x in lines]))
    return sources


async def run_ask(ctx: RunContext, instruction: str, paths: list[str] | None, text: str | None,
                  max_words: int) -> Outcome:
    settings, counter, prompts = ctx.env.settings, ctx.env.counter, ctx.env.prompts
    run_id = ctx.run_id
    instruction = (instruction or "").strip()
    paths = [p for p in (paths or []) if p and p.strip()]
    max_words = max(20, min(int(max_words or 200), 600))

    if not instruction:
        return Outcome(failed_result(run_id, "`instruction` is empty.", REVIEW))
    if len(instruction) > MAX_INSTRUCTION_CHARS:
        return Outcome(failed_result(run_id, f"`instruction` is over {MAX_INSTRUCTION_CHARS} characters; "
                                     "keep it to one short task.", REVIEW))
    if not paths and not text:
        return Outcome(failed_result(run_id, "give `paths` or `text`.", REVIEW))
    if len(paths) > MAX_PATHS:
        return Outcome(failed_result(run_id, f"at most {MAX_PATHS} paths per call.", REVIEW))
    try:
        sources = await asyncio.to_thread(load_sources, ctx.env, paths, text)
    except PathError as exc:
        return Outcome(failed_result(run_id, f"{exc}.", REVIEW, code="invalid_input"), {"files_in": len(paths)})

    files = {s.label: CitedFile(s.total_lines, s.line_chars) for s in sources}
    input_chars = sum(sum(len(x) + 1 for x in s.lines) for s in sources)
    metrics = {"files_in": len(paths), "input_chars": input_chars}

    system = prompts.get("ask_system").template
    chunk_prompt = prompts.get("ask_chunk")
    first = sources[0]
    example = f"{first.label}:L{first.start}-L{first.start + 2}"
    overhead = counter.count(system) + counter.count(chunk_prompt.substitute(
        instruction=instruction, part=1, parts=1, max_words=max_words, retry_note="", chunk="",
        example=example))
    num_predict = NUM_PREDICT["ask_chunk"]
    room = settings.num_ctx - num_predict - overhead - CHAT_OVERHEAD - SAFETY
    chunk_tokens = min(settings.chunk_tokens, room)
    if chunk_tokens < 500:
        return Outcome(failed_result(run_id, "the instruction leaves no room for input in the context window.",
                                     REVIEW), metrics)

    chunks, total_tokens = make_chunks(sources, counter, chunk_tokens)
    budget = {"input_tokens": total_tokens, "input_limit": input_limit(settings.num_ctx, num_predict),
              "chunk_tokens": chunk_tokens, "chunks": len(chunks), "tokenizer": counter.kind}
    metrics["chunks"] = len(chunks)
    if len(chunks) > settings.max_chunks:
        result = refused_result(
            run_id, total_tokens, settings.max_chunks * chunk_tokens, REVIEW,
            f"Narrow the input: pass line ranges (path:L120-L300) or fewer files; at most "
            f"{settings.max_chunks} parts of {chunk_tokens:,} tokens fit one call.")
        return Outcome(result, {**metrics, "input_tokens": total_tokens})

    stats = CallStats()
    warnings: list[str] = []
    steps = len(chunks) + (1 if len(chunks) > 1 else 0)
    notes: list[tuple[int, str]] = []
    failure: ProviderError | None = None
    for i, chunk in enumerate(chunks, start=1):
        def build(note: str, i: int = i, chunk: str = chunk) -> str:
            return chunk_prompt.substitute(instruction=instruction, part=i, parts=len(chunks),
                                           max_words=max_words, retry_note=note, chunk=chunk,
                                           example=example)
        try:
            reply = await call_model(ctx, stats, system, build, num_predict, max_words // 2)
        except ProviderError as exc:
            failure = exc
            break
        notes.append((i, reply.text.strip()))
        await ctx.progress(i, steps, f"read part {i} of {len(chunks)}")

    metrics.update(stats.metrics(num_predict))
    budget.update(output_tokens=stats.output_tokens, output_limit=num_predict, done_reason=stats.done_reason)
    if not notes:
        return Outcome(failed_result(run_id, f"{failure}.", REVIEW, budget=budget,
                                     code=failure.code, retryable=failure.retryable), metrics)

    relevant = [(i, t) for i, t in notes if not t.upper().startswith(NOTHING)]
    partial = False
    if failure:
        warnings.append(f"stopped after part {len(notes)} of {len(chunks)}: {failure}")
        answer = "\n\n".join(t for _, t in relevant) or NOTHING
        partial = True
    elif len(relevant) <= 1:
        answer = relevant[0][1] if relevant else NOTHING
    else:
        merge_prompt = prompts.get("ask_merge")
        joined = "\n\n".join(f"Note from part {i}:\n{t}" for i, t in relevant)

        def build_merge(note: str) -> str:
            return merge_prompt.substitute(instruction=instruction, parts=len(chunks), max_words=max_words,
                                           retry_note=note, notes=joined)
        try:
            reply = await call_model(ctx, stats, system, build_merge, NUM_PREDICT["ask_merge"], max_words // 2)
            answer = reply.text.strip()
            await ctx.progress(steps, steps, "merged the parts")
        except ProviderError as exc:
            warnings.append(f"merge step failed ({exc}); the answer is the unmerged notes")
            answer = joined
            partial = True
        metrics.update(stats.metrics(num_predict))
        metrics["num_predict_merge"] = NUM_PREDICT["ask_merge"]
        budget.update(output_tokens=stats.output_tokens, done_reason=stats.done_reason)

    warnings += stats.warnings
    if answer.upper().startswith(NOTHING):
        answer = "The input has nothing relevant to the task."
        warnings.append("the model found nothing relevant in the input")
    answer, was_cut = cap_words(answer, max_words)
    if was_cut:
        warnings.append(f"answer cut at {max_words} words")
    report = check_citations(answer, files)
    if report.invalid:
        warnings.append(f"{len(report.invalid)} invalid citation(s) removed")
    if not report.citations:
        warnings.append("the answer has no valid citation; treat it as unverified")
        partial = True
    answer, redacted = ctx.env.redactor.redact(report.answer)
    if redacted:
        warnings.append("redacted: " + ", ".join(f"{k} x{n}" for k, n in sorted(redacted.items())))
    metrics["cited_chars"] = report.cited_chars

    labels = sorted({s.label for s in sources})
    summary = (f"Answer from {len(labels)} input(s), {total_tokens:,} tokens in {len(chunks)} part(s); "
               f"{len(report.citations)} citation(s) validated.")
    result = make_result(
        run_id, "partial" if partial or stats.warnings else "ok", summary, review=REVIEW,
        answer=answer, citations=report.citations,
        checks={"citations": f"{len(report.citations)} valid, {len(report.invalid)} removed",
                "redaction": "applied"},
        budget=budget, warnings=warnings)
    return Outcome(result, metrics)
