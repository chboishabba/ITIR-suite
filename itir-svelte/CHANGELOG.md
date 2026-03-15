# Changelog (itir-svelte)

This changelog records user-visible behavior changes in the Svelte SB dashboard port.

## Unreleased
- Graphs/timeline ribbon: add `/graphs/timeline-ribbon` as a dedicated
  workbench over the SB dashboard timeline payload and upgrade the dashboard
  ribbon strip to a contract-aware conserved-allocation surface. The first
  slice derives hourly segments client-side from `payload.timeline`, exposes
  conservation badge + `data-testid` hooks (`ribbon-viewport`, `segment`,
  `conservation-badge`, `lens-switcher`, optional `compare-overlay`), and keeps
  thread/source callouts explicitly separate from mass-carrying segment widths.
- Graphs/workbench state contract: route loaders for `/arguments/thread/[threadId]`,
  `/graphs/narrative-compare`, and `/graphs/wiki-revision-contested` now emit
  explicit `stateReason` telemetry so page state is server-owned instead of
  inferred ad hoc by each route.
- Graphs/workbench selection contract: added a shared in-memory selection bridge
  (`src/lib/workbench/selectionBridge.ts`) and wired it through the arguments
  thread, narrative compare, and wiki contested routes for explicit
  `select|hover|sync|scope|clear` transitions.
- Graphs/narrative compare: reworked into a row-first review flow with
  selectable comparison rows, inspector tabs, bounded local graph drill-in, and
  explicit posture chips (`shared|disputed|source_only|corroboration|abstention`).
- Graphs/workbench persistence safety: added regression guards that these
  workbench routes do not persist UI selection state via `localStorage` or
  JSON string blobs.
- Graphs/narrative compare: the thread-derived FriendlyJordies fixture now
  surfaces two structured cross-source dispute families instead of leaving them
  as flat source-only rows. The workbench can inspect both the CPRS
  `contribute_to` vs `delay` consequence split and the Woolworths
  `direct grocery impacts` vs `direct cost pass-through` statement split via
  explicit `undermines` comparison links.
- Graphs/narrative compare: FriendlyJordies comparison now also lifts the
  majority-vs-minority government climate-policy argument into a structured
  dispute family, so governance-capacity claims appear as explicit comparison
  links instead of isolated source-only propositions.
- Graphs/narrative compare: add a third FriendlyJordies authority-wrapper
  fixture and surface cross-source comparison links, so the workbench can show
  nested `assert/report -> hold -> fact` attribution stacks and explicit
  `undermines` links for disputed causal propositions instead of only flat
  disagreement buckets.
- Graphs/narrative compare: add a second selectable FriendlyJordies
  chat-derived argument fixture so the workbench can inspect a richer
  archive-derived claim set in addition to the smaller public-media demo.
- Graphs/narrative compare: add `/graphs/narrative-compare` as a dedicated
  workbench for producer-owned public-media narrative comparison. The first
  slice loads the FriendlyJordies demo fixture and shows shared propositions,
  disputed propositions, attribution-link differences, corroboration refs, and
  abstentions without overloading the semantic report route.
- Docs: add follow-up workbench planning for public media/transcript ingress
  and competing-narratives comparison, so the current semantic review surfaces
  point toward a future URL-driven narrative-validation flow instead of staying
  purely fixture-first.
- Graphs/semantic report: the workbench correction seam is now DB-backed via
  `itir.sqlite` review tables instead of local JSONL, while preserving the same
  route-owned review UX and recent-correction history.
- Graphs/mission lens: add `/graphs/mission-lens` as a fused actual-vs-should
  workbench over ITIR mission planning plus SB dashboard data. The first slice
  renders a bipartite flow graph, layered mission hierarchy, deadline semantics,
  drift summary, and a bounded planning-node creation form.
- Graphs/mission lens: add reviewed actual-to-mission mapping controls and an
  observed-activity review panel, so concrete SB activity rows can be linked to
  the selected planning node and distinguished from lexical fallback/unmapped
  rows in the workbench.
- Graphs/semantic report: event/source document viewers can now push selection
  back into the token-arc inspector by clicking highlighted lines, so review
  can start from text as well as arcs.
- Graphs/semantic report: transcript/freeform mission/follow-up observer
  payloads are now surfaced in the workbench with compact summary cards and a
  JSON download action for SB-safe loose import.
- Graphs/semantic report: the semantic report loader now consumes producer-
  owned `text_debug` payloads emitted by SensibLaw report builders instead of
  re-deriving token anchors, relation families, and confidence opacity in TS.
- Graphs/semantic report: the workbench now also consumes producer-owned
  `review_summary` payloads so predicate counts, cue surfaces, and excluded
  token-arc rows are visible in a compact review panel.
- Graphs/semantic report: token-arc anchors now include producer-owned char
  spans and `sourceArtifactId` values in addition to token ranges, tightening
  the shared span contract for future document cross-highlighting.
- Graphs/semantic report: when a token/anchor is active, the token field now
  lightly echoes other anchors sharing the same role and relation family within
  the event text, using the active family color with opacity scaled by source
  relation strength.
- Graphs/semantic report: the workbench now also renders an event-local
  document viewer driven by producer-owned `charStart/charEnd` anchor spans, so
  token-arc selection cross-highlights the selected event text. A separate
  source-document panel is shown but remains explicitly unavailable unless a
  real source text payload exists.
- Graphs/semantic report: transcript/freeform semantic reports can now drive a
  real source-document viewer via producer-owned grouped source texts and
  source-level event spans, so anchor selection can be projected from the
  event-local viewer into the original source text without TS offset
  re-derivation.
- Graphs/semantic report: GWB/AU semantic reports now also drive the
  source-document viewer using grouped timeline-source text from the normalized
  wiki timeline store, so the legal lanes no longer fall back to an
  unavailable source panel just because the viewer is not transcript-based.
- Graphs/semantic report: the token-arc side panel now supports direct
  relation-level pin/freeze and shows compact provenance-strength summaries, so
  reviewers can lock a specific relation and quickly see whether it is
  mention-backed, receipt-anchored, or fallback-heavy.
- Graphs/semantic report: event/source document viewers now carry provenance-
  aware highlight styling plus an active anchor-quality strip, so mention,
  receipt, and fallback spans communicate different certainty levels where the
  text is actually being reviewed.
- Docs: define `workbench` explicitly in the `itir-svelte` README as the label
  for inspection-heavy debug/review routes (for example `/viewers/hca-case` and
  `/graphs/semantic-report`), distinct from parity/dashboard modules.
- Graphs/semantic report: add a token-arc debugger workbench to
  `/graphs/semantic-report` for text-rich semantic events. The new view renders
  hoverable event tokens, draws SVG relation arcs colored by semantic
  family/type and faded by confidence tier, and lists the hovered
  subject/predicate/object anchors for debug/review. This is a display-only
  semantic debugging surface; it does not write canonical spans or alter
  extraction/promotion behavior.
- Graphs/semantic report: extend the token-arc debugger with click-to-pin /
  clear-pin behavior so arc sets stay visible during inspection, and expose
  anchor provenance (`mention`, `receipt`, `label_fallback`) in the side panel.
  The provenance model is intentionally generic so the same component can later
  be reused beyond legal-only semantic lanes.
- Graphs/semantic report: extract the token-arc payload into a shared
  `textDebug` contract and make the inspector consume that generic event/text /
  relation / anchor shape directly instead of semantic-report-local types.
- Graphs/semantic report: add a transcript/freeform semantic producer as a
  third selectable corpus so the token-arc workbench is proven against a real
  non-legal source rather than only GWB/HCA legal report payloads.
- Graphs/semantic report: transcript/freeform token arcs now also recognize a
  social relation family (`sibling_of`, `parent_of`, `child_of`, `spouse_of`,
  `friend_of`, `guardian_of`, `caregiver_of`) and render it with a dedicated
  social/teal family color instead of collapsing it into the generic fallback
  lane.
- Dev/SSR: work around intermittent Vite SSR resolution selecting Svelte's browser/client
  entrypoints by pinning `ssr.resolve.conditions = ['node','default','development']`
  (intentionally omits `browser`) in `vite.config.ts`, avoiding the
  "dependency module is not yet fully initialized" circular-init failure.
- Dev/SSR: also pin non-SSR `resolve.conditions = ['node','default','development']` and force SSR bundling for Svelte (`ssr.noExternal = ['svelte']`) to reduce recurrence.
- Dev/SSR: add recovery tooling for the above:
  - `npm run dev:clean` clears Vite prebundle cache + `.svelte-kit/output`
  - `npm run dev:stable` runs dev server with a larger Node heap
- Home (`/`): when no dashboard payload exists on disk (no env vars, no runs),
  return a load error payload for in-page display instead of hard-500ing the
  server route.
- Home (`/`): hydrate dashboard payloads from the canonical dashboard DB (`SB_DASHBOARD_DB` or `SB_RUNS_ROOT/dashboard.sqlite`) via `StatiBaker/scripts/query_dashboard_db.py`; keep `SB_DASHBOARD_JSON` as a legacy regression/debug override.
- Wiki graphs: hydrate wiki timeline AAO payloads from the canonical SQLite store (`SensibLaw/.cache_local/wiki_timeline_aoo.sqlite`) via `SensibLaw/scripts/query_wiki_timeline_aoo_db.py`; keep `wiki_timeline_*_aoo.json` as fallback fixtures.
- Missing Runs: when a date range is explicitly selected and dashboards are
  missing on disk, auto-run a local catch-up job (disable via
  `ITIR_AUTO_BUILD_MISSING_DASHBOARDS=0`) that:
  1) ingests newer Codex chats into `~/.chat_archive.sqlite`
     (best-effort, local-only)
  2) runs `StatiBaker/scripts/build_dashboard.py` for missing days
  The Missing Runs panel shows a spinner + estimated % while the job runs.
- When You Work: added an optional per-day hour log view for selected ranges. When enabled,
  the page renders day-by-day hour strips grouped into 7-day segments below the aggregate
  weekday x hour heatmap (e.g. 14-day range -> 2 segments).
- Graphs/AAO (`/graphs/wiki-timeline-aoo`): widen role-layout lane spacing
  (`colGap`, `leftPad`) and keep intrinsic-width + horizontal scroll in the
  viewer to prevent stacked/squished lane labels in dense selections.
- Graphs/fact timeline loader: add deterministic event-local fact coalescing
  keyed on anchor + action + subject/object sets + negation + chain kind, with
  canonical ID rewiring for `prev_fact_ids`/`next_fact_ids` so duplicate rows
  are collapsed without merging clause-linked distinct facts.
- Graph UI: `GraphViewport` now supports intrinsic-width rendering with
  horizontal scroll (`fitToWidth=false`, `scrollWhenOverflow=true`) and
  reset-key driven transform reset so timeline graphs do not remain visually
  collapsed/squished across event/layout switches.
- Graphs: `/graphs/wiki-fact-timeline` now uses a wider canvas and explicit
  horizontal lane spacing (`colGap`, `leftPad`) so `Time -> Party -> Subjects ->
  Facts -> Objects` columns are materially farther apart for readability.
- Graphs/AAO + AAO-all numeric lane ordering now sorts by parsed numeric
  magnitude (largest first) instead of key lexicographic order, so values are
  ranked by actual size in the lane.
- Graphs/AAO-all: added dedicated `Source` and `Lens` lanes with context edges
  (`kind=context`) so provenance/profile overlays stay separate from AAO role
  lanes. Source labels are built from source entity/provider/parser hints; lens
  labels are built from extraction profile + event lens tags
  (claim-bearing/SL-lane markers).
- Graph UI: `context` edges now render as low-weight dashed overlays and are
  excluded from neighbor-centering, matching the non-spine overlay behavior.
- Graphs/AAO-all requester lane: `req:none` is now a first-class diagnostics
  node when requester gaps exist in the current event window, and selecting it
  shows extractor-level `requester_coverage` counters plus window-level
  request-signal vs requester-match checks (including missing event IDs) in the
  context panel.
- Graphs/AAO + AAO-all: numeric node keying now matches extractor scientific
  currency normalization (`$5.6trillion` -> `5.6e12|usd`) instead of legacy
  composite scale-currency tags (`trillion_usd`).
- Graphs/AAO-all context: rows now render extractor `numeric_claims` summaries
  (key, role, `time_years`, and compact `time_anchor`) so date attribution and
  canonical numeric normalization are inspectable directly from the panel.
- Graphs/AAO-all context: numeric claim summaries now also expose expression and
  surface hints (`scale`, derived exponent, spacing pattern) from extractor
  payloads to keep identity/expression/format layers visible.
- Graphs/AAO-all context: row time now renders from each event's own anchor
  precision (day/month/year) instead of downcasting to the active timeline
  bucket granularity.
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

## 2026-02-13

- Wiki graphs: `LayeredGraph` now respects requested `colGap` when `scrollWhenOverflow` is enabled (lanes no longer compress into each other; wider horizontal separation with scroll).
- Wiki graphs: added deterministic SSR smoke script (`npm run ssr:smoke`) to catch SSR module-load regressions without binding a port.
- SB Dashboard: removed `svelte/store` dependency from `waterfallColors` hook by switching to a minimal store-compatible `writable` implementation (SSR/import-cycle hardening).
- Wiki graphs: added dataset selector wiring for `gwb_public_bios_v1` (source pack timeline + AAO output).
