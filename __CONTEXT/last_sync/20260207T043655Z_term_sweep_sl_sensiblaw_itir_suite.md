# Term Sweep: `SL` (Whole Word), `sensiblaw`, `itir`, `suite`

## Scope
- Date: 2026-02-07
- Source DB: `chat-export-structurer/my_archive.sqlite`
- Query scope: `messages.role IN ('user','assistant')`
- Match rules:
  - `SL` must be a whole word (`(?<![A-Za-z0-9_])SL(?![A-Za-z0-9_])`)
  - `sensiblaw`, `itir`, `suite` are case-insensitive substring matches
- Raw artifact: `__CONTEXT/last_sync/20260207T043655Z_term_sweep_sl_sensiblaw_itir_suite.json`

## Headline Counts
- Total messages in DB: `76950`
- Matched messages (deduped by message): `1744`
- Term counts (message-level, non-exclusive):
  - `sensiblaw`: `1055`
  - `suite`: `552`
  - `itir`: `439`
  - `SL` (whole word): `246`

## Most Relevant Titled Threads
- `SENSIBLAW` (`4d535d3f33f54b1040ab38ec67f8f550a0f69dce`): `443` matched messages
- `Branch · Branch · Cross-comparison of SL ITIR TIRC` (`d368629d32111762fee2a415839a53ee398cb2df`): `100`
- `Branch · Cross-comparison of SL ITIR TIRC` (`0baa733624372fdcdf4c7e624a5b0401a38a3fe7`): `85`
- `Milestone Slice Feedback` (`1802fc3d13a0ad01ad95cef07eeaae9c16c22bed`): `75`
- `Feature timeline visualization` (`f8170d36e0b2c28b2bb0366a7dc35a433e26ca00`): `66`

## Update: Explicit Sweep + Repo Tracking Comparison (2026-02-07)
- Alignment is strong between archive signal and current suite priorities:
  - `TODO.md` already tracks orchestrator/channel/test tasks spanning `SensibLaw`, `SL`, and `ITIR-suite`.
  - `README.md` already documents `ITIR-suite` as orchestration/control plane and references archive-driven context sync.
- Gap areas not yet represented as explicit TODOs before this update:
  - Formalize a repeatable term-sweep runbook (query scope, regex rules, artifacts).
  - Promote highest-signal thread IDs/titles into maintained context index notes.
  - Add a false-positive control pass for overloaded term `suite` during triage.

## Recommended Next Prompt
- "Run the same sweep for `tircorder` and `statibaker`, keep whole-word boundaries where relevant, and produce a delta vs `20260207T043655Z`."
