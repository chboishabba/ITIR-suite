# Changelog (itir-svelte)

This changelog records user-visible behavior changes in the Svelte SB dashboard port.

## Unreleased

- Graphs: added a generic bipartite graph viewer and a page at `/graphs/wiki-candidates` to visualize
  the wiki candidate substrate (seed page -> candidate evidence edges), including an aggregate-by-kind
  mode that makes event-heavy extraction immediately visible.
- Graphs: added `/graphs/wiki-timeline` which renders a date-anchored timeline substrate extracted
  from the main `George W. Bush` Wikipedia snapshot (month/year buckets -> event candidates).
- Graphs: added `/graphs/wiki-timeline-aoo` which expands a selected timeline event into a small
  actor/action/object mini-graph (sentence-local, non-causal, non-authoritative).
- Graphs: `/graphs/wiki-timeline-aoo` now supports a time rendering toggle (`auto|year|month|day`)
  that can split time into separate nodes (Year -> Month -> Day) for AAO mini-graphs.
- Graphs: added `/graphs/wiki-timeline-aoo-all` to render an event-heavy whole-article combined AAO
  view (union graph across many events), with simple caps to keep the display responsive.
- Graphs: layered graph nodes are now clickable to expand full text in-place; layout centers columns
  and prioritizes spacing around the expanded node by giving it more vertical room.
- Docs/TODO: refreshed SL/SB web surface inventory for the Svelte transition and added an explicit
  Tool Use Summary parsing task (compound shell lines, directory grouping).
- Tool Use Summary: derive command families from compound shell lines (e.g. `cd … && pytest …`)
  and group variants by directory context when a leading `cd <dir>` is present.
- Thread viewer: tool-like messages that look like `exec_command { ... }` render as a structured
  tool call card (badges for `sandbox_permissions`, `justification`, `prefix_rule`, plus copy buttons).
- Chat Flow Waterfall: hover infobar moved below the waterfall so hover does not cause layout shifts
  that "kick" the cursor off the hovered segment.
- Layout: widened dashboard content on large screens (targets ~80vw with a max width cap) to reduce
  excessive side whitespace.
- Tool Use Summary: improved compound shell parsing so `cd … && <cmd>` is attributed to the real tool
  without inflating counts for `&&` chains; directory-grouped variants now display compact `in <dir>`
  labels (full dir path in tooltip) and the plain list excludes entries already covered by a dir group.
- Tool Use Summary: restored SB-native family counts/labels (matches legacy HTML), and now renders the
  `cd` family grouped by directory with the post-`cd` subcommand shown as the variant label.
- Chat Flow Waterfall: hover details now include a representative message snippet (on-demand local
  archive lookup by `threadId + ts`, cached + debounced).
- NotebookLM Lifecycle: added a dedicated module that renders `notes_meta_summary` totals and lifecycle
  counts (notebook/file) for daily and range payloads.
- Thread viewer: tool-call blocks now render tool-specific summaries (including `update_plan`), and
  the raw JSON payload is hidden by default behind an expander to reduce vertical whitespace.
- Thread viewer: progressively mounts a tail-window of messages and prepends more as you scroll up,
  keeping long threads responsive without loading thousands of DOM nodes at once.
- Timeline: expanded rows now reuse the thread viewer tool-call beautifier for chat previews (so
  `update_plan`, `write_stdin`, etc render compactly), and adds an "Open thread" link to jump to the
  thread viewer in a new tab. Long preview/detail blocks are scroll-contained.
- Chat Flow Waterfall: hover/pinned detail panel now reuses the same tool-call beautifier as the
  thread viewer (tool messages render compact cards instead of raw JSON blobs), and includes an
  "Open thread" action that attempts to focus the pinned message in the thread viewer.
- Chat Flow Waterfall: hover/pinned details now prefer the last non-empty message within the segment
  time range (falls back to showing an explicit `(empty message)` placeholder when no text exists).
- Thread viewer: empty messages render an explicit `(empty message)` placeholder instead of a blank
  bubble, since empty text can represent non-text chat events (images/files) or capture artifacts.

## 2026-02-10

- Added `itir-svelte/` SvelteKit dashboard surface that reads SB dashboard JSON outputs.
- Added query-param date range selection (`?start=YYYY-MM-DD&end=YYYY-MM-DD`) and server-side
  aggregation over daily payloads.
- Added missing-run detection for selected ranges and a server action to build missing daily dashboards
  by invoking `StatiBaker/scripts/build_dashboard.py` (requires writable `SB_RUNS_ROOT`).
- Added "When You Work (Weekday x Hour)" heatmap (GitHub contribution-calendar cue) computed from
  daily `frequency_by_hour`.
- Ported core daily modules into reusable components: summary cards, frequency bars, artifacts list,
  chat threads table, chat flow waterfall, tool-use summary, timeline ribbon (lite), and timeline
  accounting list.
- Updated layout so Artifacts render full width (separate from Frequency bars) and remain
  scroll-contained.
- Updated "When You Work (Weekday x Hour)" heatmap so the grid fills available width (responsive
  columns; squares derived from column width).
- Added `all (sum)` lane option to "Frequency By Hour".
- Tightened Chat Threads row height: hide full thread IDs by default; show short ID on hover with
  full ID in tooltip.
- Updated Chat Flow Waterfall rendering: each hour strip now fills full width (relative thread shares),
  with a separate per-hour volume bar.
- Chat Flow Waterfall hover now shows thread title and thread ID; added width mode toggle (`time` vs
  `messages`) where time mode uses gap-to-next-message/hour-boundary as span weight.
- Chat Threads table: force single-line rows (truncate long titles, widen Thread column via
  `table-fixed`), and show full thread ID as an overlay on hover with click-to-copy.
- Tool Use: heredoc invocations (e.g. `<<'PY' ... PY`) are now trunked as `'PY'`, with different
  script bodies grouped underneath as separate sub-variants (derived from the heredoc body).
- Tool Use: `apply_patch` payloads are now trunked as `'PATCH'`, with sub-variants labeled by
  affected file(s) (Add/Update/Delete/Move) instead of showing raw `*** Begin Patch` content.
- Chat Threads: clicking the thread title opens a new-tab thread viewer at `/thread/<thread_id>`,
  rendered with a reusable messenger-style bubble component.
- Timeline: clicking a row expands a detail panel showing full preview/detail and available context.
- Fixed missing-days builder to resolve `SB_RUNS_ROOT` to an absolute path (prevents building
  dashboards into the wrong directory when env var is relative). Also surfaces build results/errors in
  the Missing Runs panel.
- Added reusable `Panel.svelte` for consistent non-section boxes (errors/notices) and used it for the
  page load error block.
- Added reusable sparkline component `Sparkline.svelte` and embedded it into summary stat cards for
  key lanes.
- Artifacts UI: group by folder, display filename only, and add saturation hint based on `seen_count`
  within the selected range (avoids redundant absolute-path repetition).
- Added reusable `ColorBarByTime.svelte` (24-hour distribution bar). Artifacts now show a time-of-day
  bar: bins come from per-day sightings (daily dashboard `generated_at` hour), with a ring marker for
  current file `mtime` (UTC).
- Timeline list is now vertically scroll-contained (max height + internal scroll) to avoid expanding
  the whole page.
