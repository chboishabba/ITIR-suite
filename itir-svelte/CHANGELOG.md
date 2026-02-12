# Changelog (itir-svelte)

This changelog records user-visible behavior changes in the Svelte SB dashboard port.

## Unreleased
- Graphs/AAO + AAO-all: add dedicated numeric lane wiring (`numeric_objects`)
  across loader, graph layers, and context panels so quantitative mentions are
  shown separately from entity object lanes.
- Graphs/AAO loader: preserve extractor action canonicalization metadata
  (`action_meta`, optional `action_surface`) from wiki AAO payloads so views can
  render canonical lemma keys while still exposing inflection/surface context.
- Graphs/AAO + AAO-all: default object lanes/context to `entity_objects` (with
  fallback to legacy `objects`) so modifier-heavy noun phrases stay in truth
  but do not flood default graph/context output.
- Graphs/AAO-all: add optional Evidence lane sourced from event-local
  `citations[]` + `sl_references[]`, with action->evidence overlay edges and
  configurable evidence display cap.
- Graph UI: extend `LayeredEdge` with edge kinds (`role`, `sequence`,
  `evidence`, `context`) and render evidence edges as dashed overlays; evidence
  edges are excluded from neighbor-centering logic so they do not perturb
  layout behavior.
- Graphs: `/graphs/wiki-fact-timeline` now includes a deterministic scope
  validator for node->fact projections (subject/object/party/time/fact lanes),
  surfacing leak counts and samples in-page for frame-scope debugging.
- Graphs: `/graphs/wiki-fact-timeline` now supports a view-only importance
  profile (`entropy_role_section_v1`) with bounded percentile node sizing for
  subjects/objects (truth artifacts unchanged).
- Graphs: `/graphs/wiki-timeline-aoo-all` now prefers step-scoped object sets
  (fallback to event-level objects only when steps are absent), reducing
  whole-event object union bleed.
- Graphs/AAO contract: negation is now modeled as structured metadata
  (`negation.kind=not`) while canonical `action` remains base verb.
  Loaders preserve backward compatibility for legacy `not_*` artifacts,
  and AAO/Fact Timeline views render negated actions without storing
  proliferating `not_*` action variants.
- Viewers: added reusable transcript/document/folder primitives under
  `src/lib/viewers/`:
  - `TranscriptViewer.svelte` (cue rendering, active cue highlight, seek hook)
  - `DocumentViewer.svelte` (line-addressable plain/markdown text viewer with search)
  - `FolderListViewer.svelte` (artifact list/picker lane)
  - `transcript.ts` deterministic cue/timestamp parser helpers
- Viewers: added `/viewers/hca-case` workbench route that loads existing HCA
  ingest artifacts (`segments.json`, transcript markdown/text, `.document.json`)
  to validate shared viewer behavior outside graph routes.
- Media: added `/api/hca-media/video` byte-range endpoint to stream the local
  HCA demo MP4 into transcript viewers for cue/audio synchronization.
- Dashboard: added a home-link card to open the new viewer workbench.
- Graphs: `/graphs/wiki-timeline-aoo-all` context rows now surface
  `check_next` provider chips derived from `citations[]`/`sl_references[]`
  follow metadata (with legal defaults when hints are present but sparse), so
  HCA/legal rows can explicitly point reviewers to `austlii`, `jade`,
  `wikipedia`, and source artifacts.

- Graphs: `/graphs/wiki-fact-timeline` now guarantees rows for AAO payloads that
  lack `fact_timeline[]` by deterministically falling back to nested
  `events[].timeline_facts[]`, then to synthesized rows from `events[].steps[]`.
  The page also surfaces loader diagnostics (`fact_row_source`, raw/output row
  counts) for quick payload-shape debugging.
- Graphs: `/graphs/wiki-fact-timeline` context rows now include step crosslink
  metadata (`prev_fact_ids`, `next_fact_ids`, `chain_kinds`) synthesized from
  AAO event `chains[]`, making clause/step progression explicit in-node.
- Graphs: timeline route loaders now resolve repo root robustly across cwd
  variants by checking both `.` and `..` for `SensibLaw/`, preventing
  environment-dependent empty graph loads.
- Graphs: `/graphs/wiki-timeline` context now surfaces per-event `links[]`
  chips/counts so link breadth is inspectable in-place.
- Graphs: node click context behavior is now consistent across timeline views:
  `BipartiteGraph` emits `nodeSelect`, `/graphs/wiki-timeline` renders a
  context panel for selected `time:*` and `ev:*` nodes, and
  `/graphs/wiki-timeline-aoo` now renders a context panel (highlighted sentence
  + connected node summary) for clicked graph nodes.
- Graphs: `/graphs/wiki-fact-timeline` context matching now uses a deterministic
  node->fact index (instead of prefix parsing), so clicking `time|party|subject|
  fact|object` nodes reliably hydrates context rows; context auto-scrolls to the
  first matched row.
- Graphs: `/graphs/wiki-fact-timeline` now keeps mention-anchor chronology as
  primary for fact rows (so historical references like `1954`/`1966` remain
  visible in timeline order) and surfaces `event_anchor` as context metadata.
- Graphs: `/graphs/wiki-timeline-aoo` now includes a deterministic `step-ribbon`
  layout mode as a first-class view type (`?view=step-ribbon|roles`) with
  shareable URLs/bookmarks. `step-ribbon` renders per-step columns in sentence
  order with explicit `then` continuation edges (linearization only; non-causal)
  and scales viewport width by step count for readability.
- Docs: established migration baseline set for current Svelte transition:
  - module parity matrix + assessed status (`docs/planning/sl_sb_web_component_inventory_20260210.md`)
  - display-layer tool-use parser contract (`docs/planning/itir_svelte_tool_use_parser_display_contract_20260211.md`)
- Thread viewer (NotebookLM meta): loader now aggregates in a streaming pass
  instead of retaining full parsed row objects, reducing server memory pressure
  on long date ranges; defaults/caps are tightened (`tail` default 200, cap
  400 for NotebookLM meta threads).
- NotebookLM batch payload shaping: source summary fields are bounded
  (per-item char cap + truncated flag) while preserving counts/references.
- Dev server: added Vite watch ignores for high-churn data paths
  (`StatiBaker/runs`, raw chat export drops, sqlite sidecars) to reduce
  unnecessary dev-process memory churn.
- Added `dev:profile` script (GC traces + near-limit heap snapshots) and
  request-level memory tracing via `ITIR_TRACE_MEM=1` in `src/hooks.server.ts`
  for diagnosing Node/Vite OOM.
- Tool call expanders now support lazy body mounting, and heavy sections
  (`raw payload`, batched notebook details/source IDs) are lazy-mounted to
  reduce initial thread-view memory footprint.
- Thread viewer route SSR restored (was client-only) so Notebook/thread content
  is visible immediately even when client hydration/runtime has transient issues.
- NotebookLM thread viewer: source snippets now render with the shared
  Markdown-lite renderer (headings/lists/code formatting preserved).
- NotebookLM thread viewer: added a per-thread Source Index panel (numbered
  sources + type badges + mentions), and NotebookLM event cards now show
  compact `refs=<ranges>` pointers (e.g. `1-3,7`) instead of repeating long
  source names per event.
- NotebookLM event cards: removed duplicate in-card timestamp (time is already
  shown in bubble meta), emphasize notebook title, and show clearer event
  phrasing for artifact outputs (type/status-first wording).
- NotebookLM thread payload shaping: reduced batch event payload size (removed
  duplicate full-record embeddings and capped in-event source-id arrays) to
  avoid server OOM on large NotebookLM snapshots.
- NotebookLM loader memory hardening: switched notes-log reads to streaming,
  capped NotebookLM thread tail at 800 events, and only materializes message
  objects for the selected tail window (instead of all matched events).
- NotebookLM thread viewer: `notebooklm_meta_event` cards now surface
  notebook/source/artifact display fields (titles, type/status, URLs) and
  optional source-guide snippets/keywords when present, while keeping raw JSON
  collapsed by default.
- NotebookLM thread summary card now includes artifact-row and snippet counts
  alongside source/event totals.
- Chat Threads: added a source selector (multi-toggle) in the table header so
  rows can be enabled/disabled by source without changing the date range.
  Source options derive from per-thread `source_ids` with `origin` fallback.
- Chat Threads: selector now includes `notebooklm (meta-only)` when NotebookLM
  lifecycle metadata exists in the selected payload, with metadata-backed rows
  grouped by `notebook_id_hash` from `runs/<date>/logs/notes/<date>.jsonl`
  (plus an unscoped bucket), rendered as clickable `meta` rows that open in the
  thread viewer.
- NotebookLM thread viewer: `source_observed` metadata rows sharing the same
  timestamp are batched into one event (`source_observed_batch`) with count +
  expandable source-id list, reducing repetitive vertical spam.
- NotebookLM thread viewer: raw JSON is now hidden by default behind the shared
  tool-call expander (`raw payload`) while keeping key metadata in a compact
  summary block.
- NotebookLM thread viewer: added a top summary card (notebook hash/unscoped,
  event count, grouped message count, source-observed count, unique source IDs,
  first/last timestamp).
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
- Graphs: `/graphs/wiki-timeline-aoo-all` context panel now supports full chronological expansion for
  high-degree nodes (`all rows` toggle), and each row surfaces connected-node tags plus `citations` /
  `sl_refs` snippets for cross-event traceability.
- Graphs: `/graphs/wiki-timeline-aoo-all` context panel now renders HCA parser lanes (`party`,
  `toc_context`, `legal_markers`, `timeline_facts`) and supports `Fact-date order` sorting for
  out-of-order evidence narratives.
- Graphs: added `/graphs/wiki-fact-timeline` for linearized fact chronology rendering (time ->
  party/subject -> action -> object) using `fact_timeline[]` when present.
- Graphs: `/graphs/wiki-timeline` source selector now includes `hca` and can render timeline
  buckets from HCA AAO payload events.
- Graphs: `wiki-timeline`, `wiki-timeline-aoo`, and `wiki-timeline-aoo-all` now support dataset source
  switching via `?source=` (`gwb`, `hca`, `legal`, `legal_follow` as available), so source-pack timelines
  can be viewed in the same Bush-style surfaces.
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
- Thread viewer: message bodies render a small Markdown subset (headings, bold, lists, fenced code)
  to better reflect ChatGPT-style formatting, while keeping code blocks scroll-contained.
- Thread viewer: supports deep-link focusing via query params:
  - `focus_mid=<message_id>` (exact)
  - `focus_source_message_id=<source_message_id>` (when present)
  - `focus_ts=...` (fallback, second-level match)
- Thread viewer: user bubbles are now light (similar lightness to assistant bubbles) while keeping a distinct hue.
- Added `/threads` route to browse/search the local archive and open threads in the viewer.
- Thread viewer route now accepts online/source conversation UUIDs (when `source_thread_id` exists in the archive) and maps them to canonical thread ids.
- Chat archive: improved ChatGPT export parsing to preserve non-text `content.parts` items as stable placeholder lines (e.g. images/files) instead of dropping them to empty text, and added an ingest flag to upsert empty-text rows when re-ingesting improved parses.

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
- Wiki AAO views now prioritize step-level subjects/objects (from `steps[]`) over raw actor inventory
  for context rows and subject edges, which removes false co-subject displays in multi-actor sentences.
- Wiki AAO per-event view now surfaces `chains[]` metadata emitted by the extractor (sequence/purpose
  links) as a first nesting/chain lane.
- Wiki AAO per-event view now includes an "Object resolver hints" panel for quick curation checks on
  non-wikilink objects (exact/near matches from extraction hints).
