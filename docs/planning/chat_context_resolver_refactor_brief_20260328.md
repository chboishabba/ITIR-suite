# `scripts/chat_context_resolver.py` Refactor Brief

## Current surface

[`scripts/chat_context_resolver.py`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py)
currently mixes five concerns in one CLI entrypoint:

- selector parsing and sqlite lookup
- live-provider fallback
- transcript retrieval and stitching
- transcript analysis / cross-thread analysis
- output formatting and CLI orchestration

The main overload points are concentrated around:

- DB matching at `scripts/chat_context_resolver.py:320`
- live-provider execution at `scripts/chat_context_resolver.py:531`
- parser wiring at `scripts/chat_context_resolver.py:800`
- transcript analysis from `scripts/chat_context_resolver.py:1049`
- final CLI orchestration at `scripts/chat_context_resolver.py:1674`

## Reusable core to preserve or extract

- canonical selector -> thread resolution
- immutable sqlite read helpers
- transcript-building and transcript-window logic
- transcript term analysis and cross-thread comparison
- format-independent payload assembly

These are general chat-context capabilities and should not stay coupled to one
provider or one CLI surface.

## Specialized remainder that should stay explicit

- live-provider fallback and auth/token handling
- export download / export ingest wiring
- CLI flag grammar and terminal formatting

The `re_gpt` / web-fallback path is useful, but it is an adapter, not the core
resolver contract.

## Proposed modules after split

Implementation note:
the repo already contains the file
[`scripts/chat_context_resolver.py`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py),
so the extracted helper modules cannot live in a sibling
`scripts/chat_context_resolver/` package on disk. The first implementation
slices should therefore use a real helper package such as
`chat_context_resolver_lib/` at repo root while preserving the same logical
boundaries.

- `scripts/chat_context_resolver.py`
  thin CLI coordinator only
- `chat_context_resolver_lib/db_lookup.py`
  selector matching, FTS, canonical/online-thread resolution
- `chat_context_resolver_lib/live_provider.py`
  live fallback, command building, token/env handling
- `chat_context_resolver_lib/transcript.py`
  stitched transcript rows, windows, excerpts
- `chat_context_resolver_lib/analysis.py`
  term parsing, per-thread analysis, cross-thread analysis
- `chat_context_resolver_lib/formatters.py`
  JSON/text output
- `chat_context_resolver_lib/cli.py`
  parser construction and shared flag registration

## Acceptance checks

- existing CLI selectors still resolve the same canonical thread IDs
- DB-only flows still work without any live-provider dependency
- transcript-analysis outputs are byte-for-byte stable for fixed fixtures
- live fallback stays behind a neutral provider interface rather than
  hard-coding `re_gpt` as the contract name
- `main()` becomes a thin coordinator rather than another logic bucket

## First implemented slice

Completed on 2026-03-28:

- extracted transcript helpers to
  `chat_context_resolver_lib/transcript.py`
- extracted transcript-analysis helpers to
  `chat_context_resolver_lib/analysis.py`
- rewired `scripts/chat_context_resolver.py` to use those helpers for:
  transcript construction, transcript filtering, term parsing, range parsing,
  term analysis, top-term extraction, and recent-turn timestamp selection
- added focused regression coverage in
  `tests/test_chat_context_resolver_analysis.py`

Still pending from this brief:

- DB lookup extraction
- live-provider extraction
- formatter extraction
- CLI/parser extraction
