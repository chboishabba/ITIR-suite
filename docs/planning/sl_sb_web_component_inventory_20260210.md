# SL + SB Web Component Inventory (For Svelte Transition)

Date: 2026-02-10

## Purpose

Document the current user-visible Streamlit/HTML/web UI modules in:
- `SensibLaw/` (SL)
- `StatiBaker/` (SB)

This inventory is the baseline for the ongoing Svelte transition in `itir-svelte/`.

Transition baseline set (for migration decisions):
- Module parity matrix (this file): legacy SL/SB UI surfaces vs `itir-svelte` status.
- Parser/display contract: `docs/planning/itir_svelte_tool_use_parser_display_contract_20260211.md`
  (Tool Use Summary grouping semantics and invariants).

Scope note:
- This is an inventory of **UI surfaces and their contracts**, not an implementation guide.
- UI surfaces are **projection-only**: read-only views over frozen payloads. They do not mutate SL/SB
  canonical state.

## SensibLaw (SL): Streamlit UI Surfaces

### Surface 1: Operations Console (Streamlit)

Launch:
- `cd SensibLaw && streamlit run streamlit_app.py`

Entrypoints:
- `SensibLaw/streamlit_app.py` (shim, delegates to `sensiblaw_streamlit.app:main`)
- `SensibLaw/sensiblaw_streamlit/app.py` (page setup + tab router)

Tab modules:
- `SensibLaw/sensiblaw_streamlit/tabs/*.py`

Current tabs (names are user-visible; each tab is a deterministic read-only projection):
- Documents
- Collections
- Text & Concepts
- Knowledge Graph
- Case Comparison
- Obligations
- Ribbon (demo)
- Utilities (labs/read-only; must banner that it is not covered by invariants)

Tab feature summary (current implementation; see `SensibLaw/docs/ui_tab_contracts.md` for the strict rules):
- Documents:
  - PDF ingestion (fixture/sample selection + upload)
  - Metadata entry (title/jurisdiction/citation/flags)
  - Snapshot lookup (read-only JSON)
  - Document preview (embedded HTML)
  - Citations list (read-only) + bounded "follow citation" action (adds at most one doc)
  - Ingestion debugger (stepper-style, still projection-only over bounded state)
- Collections:
  - Read-only collection diffs/manifests/exports (structural, deterministic)
- Text & Concepts:
  - Input text + concept match list + concept cloud/counts (fixture-driven in tests)
- Knowledge Graph:
  - Node/edge counts + edge list (each edge must carry a citation field) (fixture-driven in tests)
- Case Comparison:
  - Added/removed/unchanged obligation IDs (fixture-driven in tests)
- Obligations:
  - Read-only obligation payloads + span inspector; optional receipts sections if present
- Ribbon:
  - Conserved allocation ribbon demo surface (read-only)
- Utilities:
  - Labs surface; must show banner that it is not covered by invariants; no mutations

Key shared UI helpers:
- Fixture selection + forbidden-term scanning + download helpers:
  `SensibLaw/sensiblaw_streamlit/shared.py`
- Document preview helpers (includes embedded HTML via Streamlit components):
  `SensibLaw/sensiblaw_streamlit/document_preview.py`

Contracts:
- Read-only projection discipline: `SensibLaw/docs/ui_tab_contracts.md`
- Module map (entrypoints + tabs): `SensibLaw/docs/web_module_map.md`

UI regression checks:
- E2E tests exist under `SensibLaw/playwright/tests/*.spec.ts` (fixture-mode behavior).

### Surface 2: Review UI (Streamlit, read-only bundle inspector)

Launch:
- `cd SensibLaw && streamlit run ui/app.py`

Entrypoint:
- `SensibLaw/ui/app.py` (loads a review bundle JSON and renders read-only panels)

Panels:
- `SensibLaw/ui/panels/obligations.py`
- `SensibLaw/ui/panels/activation.py`
- `SensibLaw/ui/panels/topology.py`
- `SensibLaw/ui/panels/audit.py`

## StatiBaker (SB): Static HTML Dashboard Surfaces

### Primary outputs (UI contract)

The primary UI contract for all SB dashboard renderers is the JSON payload:
- `<runs-root>/<YYYY-MM-DD>/outputs/dashboard*.json`

The legacy HTML renderers write portable local views:
- `<runs-root>/<YYYY-MM-DD>/outputs/dashboard*.html`

Reference docs:
- `StatiBaker/docs/activity_dashboard.md` (what outputs exist)
- `StatiBaker/docs/dashboard_implementation_notes.md` (layout contract + renderer notes)
- `StatiBaker/docs/web_module_map.md` (safe edit zones + contract assumptions)

Build entrypoint:
- `StatiBaker/scripts/build_dashboard.py` (loads compiler/renderer code in `StatiBaker/sb/dashboard.py`)

### Daily dashboards: legacy HTML modules (`dashboard.html` / `dashboard_all.html`)

Daily outputs exist in two main variants:
- `dashboard.html`: *scoped* (chat scope filter applied)
- `dashboard_all.html`: *all* (debug-style; chat scope filter disabled)

Reference file (example):
- `StatiBaker/runs/2026-02-06/outputs/dashboard_all.html`

User-visible module order (`dashboard_all.html` headings):
1. Summary (metric grid + selected computed ratios/notes)
2. Context Overlays (Selected)
3. Per-hour bar views:
   - Messages/hour
   - Shell/hour
   - Commits/hour
   - Activity/hour
   - Media/hour
   - Input/hour
   - Window/hour
   - Branch/hour
   - PR/hour
4. Process Artifacts (links + local paths; read-only)
5. Chat Threads (table)
6. Chat Context Usage (Estimated)
7. Chat Flow Visualizations (controls + render surface)
8. Media Consumption
9. NotebookLM Lifecycle (Metadata)
10. Tool Use Summary (command families + variants + top dirs)
11. Agent Edit Activity (parsed from assistant/tool message text)
12. Timeline (filters + scroll list; accounting posture)
13. Warnings

Important UI behavior notes (daily legacy HTML):
- Some modules include embedded client JS for local filtering and palette selection (persisted via
  `localStorage`).
- Truncation is explicit in-page when it occurs, e.g.:
  - timeline truncated (commonly newest 600 events retained)
  - chat flow render limited (commonly newest 480 messages retained)
- The machine-readable contract is the JSON; HTML is a best-effort portable view over that payload.

#### Chat Flow Visualizations: current semantics (legacy HTML)

Data source:
- `dashboard*.json` -> `chat_flow.waterfall[]`

Legacy UI modes:
- "Legacy / Linear": a 1D strip of the newest `waterfall_render_limit` chat messages.
  - Each message becomes a tiny segment.
  - Segment width encodes **elapsed time until next message** (gap), clamped.
  - Colors are computed by a palette + "color by" algorithm (thread/hour/role/switch).
- "Actual Waterfall": a multi-lane thread timeline. This can be unavailable for high-volume days.

Important behavior:
- `chat_flow.waterfall` is **truncated** to a render limit (commonly 480). For example, on
  2026-02-06 `message_count=2194` but `waterfall_render_limit=480` (newest retained).
- When the render-blockers trigger (e.g. message count exceeds a threshold), the actual waterfall is
  disabled and the page shows the linear strip plus a "Why unavailable" block.

### Weekly dashboards: legacy HTML modules (`dashboard_weekly_*.html`)

Weekly outputs vary by window length and scope mode. Two concrete examples under the same run:
- Minimal weekly view (no heatmap/rollups):
  - `StatiBaker/runs/2026-02-08/outputs/dashboard_weekly_14d_all.html`
- Full weekly view (includes heatmap + rollups):
  - `StatiBaker/runs/2026-02-08/outputs/dashboard_weekly_30d.html`

User-visible module order (`dashboard_weekly_30d.html` headings):
1. When You Work (Weekday x Hour)
   - Design cue: GitHub contribution calendar.
   - Signal lane toggles + "Normalize (score)" toggle.
   - Presets: All / None / Intent set.
   - Hover cells show per-signal breakdown.
   - Data contract: `dashboard_weekly_*.json` -> `weekday_hour_heatmaps`:
     - `lanes[]`, `lane_labels{}`, `lane_totals{}`
     - `series{lane -> 7x24 ints}`
     - `weekday_names[]`, `weekday_day_counts[]`, `default_selected[]`
2. Above / Below (Rollups)
   - By weekday (avg/day)
   - By hour (avg/day)
   - Top weekday-hours (table)
   - Note: rollups are computed client-side from the selected lanes (not a separate JSON block).
3. Totals (grid)
4. NotebookLM Lifecycle (Metadata)
5. Per-Day Summary (table; rows are `daily[]`, columns are a selected subset of `daily[].summary`)
6. Warnings

### Lifetime dashboards

Weekly/lifetime outputs extend daily with aggregate blocks (examples, not exhaustive):
- period header (`period_start`, `period_end`)
- totals + averages blocks
- day list (linking each day to its daily HTML)
- weekday x hour heatmap aggregates (`weekday_hour_heatmaps`) when present
- lifetime-only: state-volume blocks (`state_totals`, `state_averages_per_day`, ratios/definitions)

## Svelte Transition: `itir-svelte/` (Current Port)

### What exists now (projection-only)

`itir-svelte/` is a working SvelteKit port that reads SB dashboard JSON outputs and renders
modular, prop-driven UI components.

Current implemented modules include:
- Date range selector (`?start=YYYY-MM-DD&end=YYYY-MM-DD`)
- Missing-runs detection + action to build missing days via `StatiBaker/scripts/build_dashboard.py`
  (server action; writes dashboards into `SB_RUNS_ROOT`)
- Summary cards (first-pass subset of daily `summary`)
- Frequency-by-hour bars (lane selector; includes `all` = sum across lanes)
- Artifacts list (read-only paths with copy; grouped by folder; scroll-contained)
- Chat Threads table (compact; ID on hover; timestamps shown)
- Chat Flow Waterfall (Svelte port): hour strips always fill width; segments are grouped by
  hour+thread; width can encode `time` (sum gap seconds) or `messages` (messageCount); per-hour volume
  shown separately; hover shows thread title/ID, counts, and span.
- Tool Use Summary (trunking for heredoc + patch; should also parse compound shell lines such as
  `cd ... && pytest ...` to group by directory and show the real subcommand)
- Timeline ribbon (lite) + accounting list (scroll-contained; hover = full ISO timestamp)
- Thread viewer route (`/thread/<id>`) opens in a new tab
- NotebookLM Lifecycle (Metadata) (range view aggregates daily/weekly shapes into a common surface)

Open questions for migration (chat flow semantics):
- Should the Svelte surface match legacy "linear strip" semantics (per-message, gap-weighted), or is
  the hour+thread grouped view the desired default?
- If we keep hour+thread grouping, do we want additional visual cues for message volume within a
  segment (ticks/texture/opacity/height), beyond showing `messageCount` in hover?
- For hover details, do we want a representative **message snippet** (requires either adding message
  previews to the SB payload or doing an on-demand lookup in the local archive by `thread_id + ts`)?

### Known parity gaps versus legacy SB weekly HTML

Modules still missing or partial in `itir-svelte/` (as of 2026-02-10):
- Weekly "When You Work (Weekday x Hour)" multi-lane heatmap (`weekday_hour_heatmaps`)
- Weekly rollups (Above/Below) computed from the heatmap lane selection
- Weekly totals grid (as rendered by the weekly HTML)
- Weekly per-day summary table (daily rows across the selected range)
- Daily-only modules not yet ported:
  - Context Overlays (Selected)
  - Chat Context Usage (Estimated)
  - Media Consumption
  - Agent Edit Activity
  - Warnings (as a structured module, not just console logs)
- Dedicated weekly/lifetime routes that load `dashboard_weekly_*.json` and `dashboard_lifetime*.json`
  directly (current range mode aggregates from daily payloads)

## Related: Timeline Ribbon Contract

When porting richer timeline surfaces, align with the existing ribbon contract docs and schemas:
- `SensibLaw/docs/timeline_ribbon.md`
- `SensibLaw/schemas/timeline.ribbon.v1.schema.json`
- `itir-ribbon/docs/interfaces.md`

## Legacy SB: Feature Lists (Concrete Examples)

These examples are intended to make the legacy surfaces concrete for Svelte parity decisions.

### Weekly example: `dashboard_weekly_14d_all.html` (2026-01-26 to 2026-02-08)

File:
- `StatiBaker/runs/2026-02-08/outputs/dashboard_weekly_14d_all.html`

Header:
- Window start/end + days + chat scope (`all`)

Totals (card grid):
- Chat messages
- Chat threads
- Chat switches
- Shell commands
- Input events
- Window focus events
- Activity events
- Git commits
- Git branch events
- PR events

Daily averages (inline line):
- chat/day, switches/day, switch_rate, switches/hour, messages/chat, top-thread-share, shell/day,
  commits/day, prs/day

NotebookLM Lifecycle (Metadata):
- Notes meta events
- NotebookLM meta events
- Notebooks created/modified/moved/deleted/seen
- Files created/modified/moved/deleted/seen
- Daily averages: notes_meta/day, notebooklm/day

Per-Day Summary table columns:
- Date, Chat Source, Scope, Chat Msg, Chat Threads, Switches, Switch Rate, Switch/hr, Msg/chat,
  Top Thread, Shell, Commits, Branch, PR, Warnings, Daily (link)

Warnings:
- Count of days with warnings
- Notes about debug/scope mode (e.g. chat scope filter disabled)

JSON keys (weekly):
- `totals`, `averages_per_day`, `daily[]`, `warnings[]`, `notes_meta_totals`, `notes_meta_averages_per_day`,
  `notebooklm_lifecycle_totals`

### Daily example: `dashboard_all.html` (Date: 2026-02-06)

File:
- `StatiBaker/runs/2026-02-06/outputs/dashboard_all.html`

Summary module (high-signal fields shown):
- Chat: messages, threads, switches, switch rate, messages/hour (active), active hours, messages/chat,
  switches/hour (active), top-thread share
- Chat context usage (estimated): chars/tokens/input/output and overflow (threads + overflow tokens)
- Shell: shell commands (host vs agent_exec)
- Agent edit activity: edit blocks, files touched, line deltas (+/-)
- Media: events, items observed, consumed time, completion/churn ratios
- iNaturalist: insects/events + phase labels (observer-class overlay)
- Mood: latest + label
- Overlaps: chat-media, concurrent chat, voice/transcribe overlap, chat-input/activity overlap
- Input/window/activity: input events, window focus events, activity events
- Notes: notes meta events, NotebookLM meta events
- Git/PR: commits, branch events, PR events (+ merged/commented/received)
- Trailing avg summary line (7-day trailing averages where available)

Context Overlays (Selected):
- iNaturalist phase + stability label (heuristic)
- Mood latest
- Other overlays are observer-class only (no inference)

Per-hour bar panels:
- Messages/hour, Shell/hour, Commits/hour, Activity/hour, Media/hour, Input/hour, Window/hour,
  Branch/hour, PR/hour

Process Artifacts:
- A list of links to local artifacts with explicit local paths (read-only)

Chat Threads:
- Thread ID (short, full in hover/title)
- Title (single-line preview)
- Origin
- Message count
- First/last timestamp
- Roles breakdown (e.g. `tool:1224, user:125`)

Chat Context Usage (Estimated):
- Totals line: chars/tokens and overflow summary
- Window sweep list (e.g. 32k/128k/200k windows)
- Thread table: messages/chars/tokens/usage/overflow/token-share

Chat Flow Visualizations:
- Inline stats: message/thread/switch counts + window ts span
- Controls: view mode (linear vs actual waterfall), palette, color-by algo, custom colors, apply/reset
- Linear strip semantics: newest `waterfall_render_limit` messages; width encodes time-to-next-message
- Optional: actual waterfall mode (may be disabled when a render blocker triggers)

Media Consumption:
- Summary for media events/items/durations; platform breakdown when present

NotebookLM Lifecycle (Metadata):
- Notebooks/files created/modified/moved/deleted/seen, plus warnings if any

Tool Use Summary:
- Header counts (tool messages scanned, exec_command breakdown, unique commands)
- Top dirs touched list (when present)
- Command-family table:
  - family name, calls, unique variants, dirs touched, and variant list
  - special rendering for heredocs and patch blocks

Agent Edit Activity:
- Summary counts + mode
- File table (blocks/delta/share/line refs), or an explicit "none parsed" row
- Warnings list when patterns are absent

Timeline:
- Filter controls: search, kinds, sources, chat roles
- Scroll list (accounting posture)

Warnings:
- Array of warning strings (rendered as a list)

JSON keys (daily):
- `summary`, `frequency_by_hour`, `artifact_links`, `chat_threads`, `chat_context_usage`, `chat_flow`,
  `media_summary`, `notes_meta_summary`, `tool_use_summary`, `agent_edit_summary`, `timeline`, `warnings`,
  plus `inaturalist_trend`, `mood_latest`, and other observer-class overlays when present

## Legacy SB -> `itir-svelte` Parity Matrix (Module Level)

Status meanings:
- **present**: module exists with roughly correct data + interaction posture
- **partial**: module exists but missing major fields/controls/semantics
- **missing**: no module yet

Assessment timestamp:
- 2026-02-11 (based on legacy HTML references:
  `StatiBaker/runs/2026-02-08/outputs/dashboard_weekly_14d_all.html`,
  `StatiBaker/runs/2026-02-06/outputs/dashboard_all.html`)

| Legacy module | Legacy HTML | JSON contract | `itir-svelte` status | Notes |
|---|---|---|---|---|
| Weekly "When You Work" heatmap | `dashboard_weekly_30d.html` | `weekday_hour_heatmaps` | missing | Needs multi-lane toggle UX + normalize + hover breakdown |
| Weekly rollups | `dashboard_weekly_30d.html` | derived from heatmap | missing | Computed client-side from selected lanes |
| Weekly totals grid | `dashboard_weekly_*.html` | `totals`, `averages_per_day` | missing | Range view currently shows a different summary surface |
| Weekly per-day summary | `dashboard_weekly_*.html` | `daily[]` (+ `daily[].summary`) | missing | Also useful as range-mode table |
| Daily summary | `dashboard_all.html` | `summary` | partial | Current cards are a subset |
| Context overlays | `dashboard_all.html` | `mood_latest`, `inaturalist_trend`, etc | missing | Observer-only posture; no inference |
| Per-hour bars | `dashboard_all.html` | `frequency_by_hour` | present | Legacy shows multiple lanes; Svelte uses lane selector + all |
| Process artifacts | `dashboard_all.html` | `artifact_links` | present | Legacy is links+paths; Svelte is read-only + copy |
| Chat threads | `dashboard_all.html` | `chat_threads` | present | Needs further compaction/hover behaviors for ID/title |
| Chat context usage | `dashboard_all.html` | `chat_context_usage` | missing | Window sweep + thread usage table |
| Chat flow viz | `dashboard_all.html` | `chat_flow` | partial | Semantics differ (legacy linear-strip vs grouped segments) |
| Media consumption | `dashboard_all.html` | `media_summary` | missing | Needs platform breakdown + churn/completion |
| NotebookLM lifecycle | daily+weekly | `notes_meta_summary` / `notes_meta_totals` | present | Verify parity for created/modified/moved/deleted/seen counts |
| Tool use summary | `dashboard_all.html` | `tool_use_summary` | partial | Needs top-dirs + legacy layout parity; keep SB family counts |
| Agent edit activity | `dashboard_all.html` | `agent_edit_summary` | missing | Simple when nonzero, but still a stable module |
| Timeline | `dashboard_all.html` | `timeline` | present | Needs filter parity + strict scroll containment |
| Warnings | daily+weekly | `warnings[]` | missing | Should be visible as a dedicated module |
