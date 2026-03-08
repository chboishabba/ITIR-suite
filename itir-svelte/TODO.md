# TODO (itir-svelte)

## Purpose
Track SB dashboard module parity work and Svelte-specific componentization tasks.

Primary contract: SB dashboard JSON outputs (`dashboard*.json`) under `SB_RUNS_ROOT`.

## Near-Term (Parity)

- DONE (2026-02-11): lock parity baseline docs for migration decisions:
  - `docs/planning/sl_sb_web_component_inventory_20260210.md`
  - `docs/planning/itir_svelte_tool_use_parser_display_contract_20260211.md`
- Weekly HTML parity modules (from legacy SB HTML screenshots):
  - When You Work (Weekday x Hour) multi-lane heatmap:
    - data source: `dashboard_weekly_*.json` -> `weekday_hour_heatmaps`
    - controls: signal toggles, normalize(score), presets (all/none/intent set)
    - cell hover: per-signal breakdown + raw counts
    - add an optional per-day log view for selected ranges: render day-by-day hour strips
      grouped into 7-day segments below the aggregate weekday heatmap (for 14-day range,
      render 2 segments; for month, render ~4 segments).
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

## Reusable Viewers

- DONE (2026-02-12): add reusable viewer primitives under `src/lib/viewers/`:
  - `TranscriptViewer.svelte` (cue list + active highlighting + click/space seek hooks)
  - `DocumentViewer.svelte` (line-addressable text/markdown viewer with search)
  - `FolderListViewer.svelte` (generic file/folder picker lane)
  - `transcript.ts` (deterministic cue/timestamp parsing utilities ported from tircorder behavior)
- DONE (2026-02-12): add `/viewers/hca-case` workbench route to exercise transcript + document + folder viewers against `SensibLaw/demo/ingest/hca_case_s942025`.
- Keep the `workbench` concept documented and consistent:
  - workbenches are inspection/debug routes, not parity/dashboard modules
  - they may carry richer reviewer affordances, but no independent semantic authority
- Follow-up:
  - wire these viewers into SB thread/event detail surfaces where transcript/document artifacts are present.
  - define a shared span contract (`char_start/end`, `token span`, `source artifact id`) for graph <-> viewer cross-highlighting.
  - evaluate extracting a shared “transcript cue sync” store so audio time, selected cue, and graph node focus can synchronize across pages.

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

- DONE (2026-02-11): document display-layer parser contract and invariants in
  `docs/planning/itir_svelte_tool_use_parser_display_contract_20260211.md`
  (compound segmentation, directory context grouping, and special-case trunking).
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
- DONE (2026-02-12): `/graphs/wiki-fact-timeline` now has:
  - frame-scoped node->fact scope validator (`scope_validator`, leak samples),
  - view-only importance profile selector (`entropy_role_section_v1`),
  - bounded percentile sizing for subject/object nodes.

## Wiki Graph Surfaces

- AAO mini-graph: consider month-name rendering (`Jan 2010` vs `2010-01`) as a display-only toggle.
- Whole-article AAO view: add optional edge labels/weights and filters (by section, by action verb) without changing extraction artifacts.
- Whole-article AAO view: add a "show hidden counts" summary (subjects/objects dropped by display caps).
- Whole-article AAO view: add evidence overlay lane (`citations[]`, `sl_references[]`) with edge-kind toggle (`role|sequence|evidence`) and keep evidence edges out of layout-neighbor centering logic.

## Semantic Report Workbench

- Add a token-arc debug inspector to `/graphs/semantic-report` for text-rich
  semantic events:
  - render event text as hoverable tokens
  - draw SVG arcs on hover
  - color by relation family/type
  - opacity by confidence tier
  - visually distinguish promoted vs candidate-only rows
- Keep this surface debug-only:
  - derive anchors from existing mentions/receipts/label-text fallback
  - do not invent canonical spans or write back new semantic facts
- DONE (2026-03-08): extract a shared `text-debug` payload contract for
  token/text-local relation inspection instead of keeping semantic-report-
  specific arc types in the route loader.
- DONE (2026-03-08): prove the contract with a transcript/freeform semantic
  producer so the workbench is demonstrably reusable beyond legal-only lanes.
- DONE (2026-03-08): move token/anchor/relation-family shaping for the semantic
  workbench into Python report producers so `semanticReport.ts` consumes a
  producer-owned `text_debug` artifact instead of re-deriving anchors locally.
- DONE (2026-03-08): add a compact producer-owned semantic review summary
  (`review_summary`) so the workbench can compare predicate/cue/anchor coverage
  without depending on raw relation tables.
- DONE (2026-03-08): wire the semantic report workbench to use producer-owned
  `charStart/charEnd/sourceArtifactId` spans for event-local cross-highlighting
  in a document viewer, while keeping the source-document slot explicit about
  unavailable source text.
- DONE (2026-03-08): add append-only correction submission to the semantic
  report workbench, now backed by `itir.sqlite` review tables keyed by
  source/run/event/relation/anchor refs.
- DONE (2026-03-08): let event/source document viewers request selection back
  into the token-arc inspector by clicking highlighted lines, so review can
  start from text as well as arcs.
- DONE (2026-03-08): surface transcript/freeform `mission_observer` payloads in
  the semantic report workbench and provide a download/export surface for the
  SB-safe observer bundle.
- Follow-up:
  - revisit a shared graph <-> document span contract after this view is stable
  - add a replay/review surface over submitted DB-backed correction receipts
    rather than only a recent-submissions list
  - if mission observer review becomes regular, split it into a dedicated
    workbench route rather than overloading `/graphs/semantic-report`
- Follow-up:
  - add a future ingress-hub workbench for public media/transcript URLs so
    transcript/narrative validation can start from a dropped source rather than
    only checked-in fixtures
  - add a narrative-comparison workbench or panel for shared-vs-disputed
    facts/propositions across two source narratives
  - render widened proposition-layer output (attribution wrappers, cited
    holdings, proposition links) distinctly once the current bounded v1 grows
    beyond HCA-first idioms
- DONE (2026-03-08): add `/graphs/mission-lens` as a fused actual-vs-should
  workbench over ITIR mission planning + SB dashboard data using a bipartite
  flow graph, layered hierarchy graph, deadline panel, drift panel, and
  bounded planning-node authoring.
- DONE (2026-03-08): add reviewed actual-to-mission mapping controls to
  `/graphs/mission-lens`, so concrete SB activity rows can be linked to the
  selected planning node instead of relying only on lexical fallback.
- Follow-up:
  - add richer reviewed mapping management (unlink/reassign/status review)
    instead of only append-only linking
  - surface why a lexical mapping matched when no reviewed link exists

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
  - DB-first: missing days must be computed against the canonical dashboard DB, not `dashboard*.json` on disk.

## Reliability

- Home route (`/`): do not hard-500 when no dashboard payload exists on disk; render a
  load-error panel with instructions to set `SB_DASHBOARD_JSON` or `SB_RUNS_ROOT+SB_DATE`.
- DB-first: hydrate the home page from `SB_DASHBOARD_DB` / `SB_RUNS_ROOT/dashboard.sqlite`; keep `SB_DASHBOARD_JSON` as regression/debug only.
- DONE (2026-02-14): Missing days in a selected range auto-run a local catch-up job by default
  (disable via `ITIR_AUTO_BUILD_MISSING_DASHBOARDS=0`):
  - ingest Codex chats into `~/.chat_archive.sqlite` (best-effort)
  - run `StatiBaker/scripts/build_dashboard.py` for missing dates
  - show spinner + estimated % in the Missing Runs panel while running
- DONE (2026-02-14): Vite/Svelte SSR circular-init regression recovery tooling:
  - `npm run dev:clean` clears Vite prebundle cache + `.svelte-kit/output`
  - `npm run dev:stable` runs dev server with a larger Node heap
  - recovery steps documented in `README.md`
  - do not silently backfill with invented values

## Engineering Hygiene

- Keep domain logic in server loaders/adapters; keep components prop-driven.
- Maintain Zod contracts under `src/lib/sb-dashboard/contracts/` as the runtime gate.
- Avoid SSR/CSR hydration mismatches (defer browser-only reads like `localStorage` to `onMount`).

## Thread Viewer

- Extend tool-call “beautifiers”:
  - `apply_patch` payload summary (touched files/ops) when available
  - tool-specific iconography and copy-on-click affordances (session id, thread id)
