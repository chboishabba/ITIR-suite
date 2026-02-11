# TODO (itir-svelte)

## Purpose
Track SB dashboard module parity work and Svelte-specific componentization tasks.

Primary contract: SB dashboard JSON outputs (`dashboard*.json`) under `SB_RUNS_ROOT`.

## Near-Term (Parity)

- Weekly HTML parity modules (from legacy SB HTML screenshots):
  - When You Work (Weekday x Hour) multi-lane heatmap:
    - data source: `dashboard_weekly_*.json` -> `weekday_hour_heatmaps`
    - controls: signal toggles, normalize(score), presets (all/none/intent set)
    - cell hover: per-signal breakdown + raw counts
  - Above/Below rollups (weekday/hour + top weekday-hours table)
  - Totals grid cards
  - NotebookLM lifecycle (`notes_meta_summary`)
  - Per-day summary table (daily rows across selected range)
- Daily HTML parity modules (from `dashboard_all.html`):
  - Context Overlays (Selected)
  - Chat Context Usage (Estimated) (window sweep + thread usage table)
  - Media Consumption
  - Agent Edit Activity
  - Warnings module (daily + weekly)
- Routing:
  - add dedicated `weekly` and `lifetime` routes that load `dashboard_weekly_*.json` and
    `dashboard_lifetime*.json` directly when present
  - range mode should prefer precomputed weekly JSON when available, else aggregate from dailies

## Chat Threads

- DONE (2026-02-11): add a source selector (multi-toggle) in Chat Threads so
  thread rows can be enabled/disabled by source without changing date range.
- DONE (2026-02-11): include `notebooklm (meta-only)` in the Chat Threads source
  selector when NotebookLM lifecycle metadata exists in the selected payload.
- DONE (2026-02-11): map `notebooklm (meta-only)` to metadata-backed rows by
  parsing `runs/<date>/logs/notes/<date>.jsonl` (grouped by `notebook_id_hash`,
  with an unscoped bucket for notebookless events).
- DONE (2026-02-11): route NotebookLM rows into `/thread/<id>` and render
  NotebookLM lifecycle cards (event/source/artifact/title/snippet fields).
- DONE (2026-02-11): in NotebookLM thread view, render a source index panel
  (numbered source list + type badges) and show per-event source refs as
  compact number ranges (`1-3,7`) instead of repeating long source titles.
- DONE (2026-02-11): render NotebookLM source snippets via Markdown-lite so
  headings/lists/code formatting survives.
- Keep source derivation consistent:
  - prefer per-thread `source_ids` when present
  - fallback to thread `origin`
- Follow-up: add a dashboard-level global source scope (shared picker) that can
  drive chat-source and metadata-source filtering across modules.
- Follow-up: add a privacy mode toggle for NotebookLM thread rendering
  (local full snippets vs strict metadata-only redaction).

## Tool Use Summary (Parser)

- Implement a generic shell-line parser for compound commands:
  - recognize `&&`, `||`, `;`, and `|`
  - treat leading `cd <dir>` (and `pushd <dir>`) as a directory context for subsequent segments
  - group commands by directory context (Artifacts-style) when present
  - show "real" subcommands (post-`cd`) rather than the `cd` wrapper
- Important constraint:
  - keep SB-native family counts/labels from the JSON payload; the parser is for *display grouping*
    within a family, not for reclassifying families.
- Keep special-case trunking:
  - heredocs: `python - <<'PY'` grouped under `'PY'` with subvariants derived from the body
  - patches: `apply_patch` grouped under `'PATCH'` with subvariants derived from touched paths/ops

## Timeline Surfaces

- Ribbon: align richer ribbon implementation to the existing ribbon contract docs:
  - `SensibLaw/docs/timeline_ribbon.md`
  - `itir-ribbon/docs/interfaces.md`
- Timeline list: keep "accounting surface" posture (compact rows, full ISO on hover).

## Wiki Graph Surfaces

- AAO mini-graph: consider month-name rendering (`Jan 2010` vs `2010-01`) as a display-only toggle.
- Whole-article AAO view: add optional edge labels/weights and filters (by section, by action verb) without changing extraction artifacts.
- Whole-article AAO view: add a "show hidden counts" summary (subjects/objects dropped by display caps).

## Chat Flow Waterfall (Semantics)

- Decide desired default semantics for Chat Flow visualization:
  - legacy HTML: per-message linear strip (gap-to-next as width) + optional multi-lane waterfall
  - Svelte port: hour+thread grouped segments (time vs messages width mode)
- Hover details: show thread title + representative message snippet for the hovered segment:
  - option A: extend SB payload to include message previews per `chat_flow.waterfall` item
  - option B: on-demand local archive lookup by `canonical_thread_id + ts` (cache + debounce)
- Visual cue for message volume inside a segment (if keeping hour+thread grouping):
  - ticks/texture, opacity by log(messageCount), or height modulation

## Range Handling

- Define explicit behavior for missing days inside a range:
  - display missing dates
  - offer a "build missing" action
  - do not silently backfill with invented values

## Engineering Hygiene

- Keep domain logic in server loaders/adapters; keep components prop-driven.
- Maintain Zod contracts under `src/lib/sb-dashboard/contracts/` as the runtime gate.
- Avoid SSR/CSR hydration mismatches (defer browser-only reads like `localStorage` to `onMount`).

## Thread Viewer

- Extend tool-call “beautifiers”:
  - `apply_patch` payload summary (touched files/ops) when available
  - tool-specific iconography and copy-on-click affordances (session id, thread id)
