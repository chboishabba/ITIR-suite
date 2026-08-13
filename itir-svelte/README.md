# itir-svelte

SvelteKit + Tailwind implementation workspace for ITIR-suite UIs.

Initial focus: StatiBaker dashboard componentization.

## Ribbon Ownership

`itir-svelte` is the active UI/dev front for ribbon work.

- `itir-ribbon/` remains the contract/spec package:
  invariants, lens DSL, phase-regime packs, and UI-test selectors.
- `itir-svelte/` is where richer ribbon surfaces should be implemented and
  iterated.
- The existing `step-ribbon` wiki graph mode is a deterministic AAO layout
  transform, not the full conserved-allocation ribbon UI.

When implementing or extending ribbon views here, align with:
- `SensibLaw/docs/timeline_ribbon.md`
- `itir-ribbon/docs/interfaces.md`
- `itir-ribbon/ui_contract.md`

## Migration Docs

Use these as the current docs baseline for SB legacy -> Svelte transition:

- Module inventory + parity matrix:
  `docs/planning/sl_sb_web_component_inventory_20260210.md`
- Tool Use Summary display/parser contract:
  `docs/planning/itir_svelte_tool_use_parser_display_contract_20260211.md`
- Chat archive pull/ingest benchmark + runbook (canonical DB workflow):
  `docs/planning/chat_archive_pull_ingest_results_20260213.md`
- Legacy transcript-browser parity pass:
  `docs/planning/itir_svelte_transcript_browser_parity_20260319.md`

## Dev

```bash
cd itir-svelte
npm install
npm run dev
```

If you see a `.svelte-kit/tsconfig.json` warning, run:

```bash
npx svelte-kit sync
```

## Troubleshooting

### Vite SSR circular dependency: "module is not yet fully initialized"

Symptom (SSR/dev):
- Vite logs an error similar to:
  `The dependency module is not yet fully initialized due to circular dependency`
  while importing Svelte store internals (e.g. `svelte/src/internal/client/reactivity/store.js`).

Fix (repo-local):
- `vite.config.ts` pins SSR resolution conditions to avoid the `browser` export:
  `resolve.conditions = ['node', 'default', 'development']` and
  `ssr.resolve.conditions = ['node', 'default', 'development']`, plus
  `ssr.noExternal = ['svelte']`.
  This prevents SSR from accidentally selecting Svelte's browser/client entrypoints.

If it reappears:
- Check whether any plugin/config reintroduced a `browser`-biased SSR condition.
- If the dev server has been running a while (or memory is constrained), Vite can end
  up in a bad partial-initialization state. The reliable recovery sequence is:
  1) stop `npm run dev`
  2) `rm -rf node_modules/.vite .svelte-kit/output`
  3) restart with `npm run dev:stable` (higher Node heap)

### Home page 500 on `/` after a brief flash

Cause:
- The home route expects a StatiBaker dashboard payload to be queryable. If nothing is
  available (no DB, no env vars, no dashboards built), the server load can fail.

Fix:
- Provide a dashboard source via one of:
  - `SB_DASHBOARD_DB=/abs/path/to/dashboard.sqlite` (preferred)
  - `SB_RUNS_ROOT=/abs/path/to/StatiBaker/runs_local` (so `SB_RUNS_ROOT/dashboard.sqlite` exists) and `SB_DATE=YYYY-MM-DD`
  - Legacy fallback (regression/debug only): `SB_DASHBOARD_JSON=/abs/path/to/dashboard_all.json`

### Auto-build missing days in a selected range

Default behavior:
- When a date range is explicitly selected (query params or env) and some days are
  missing dashboards in the DB, the UI will auto-run a local “catch-up” job:
  1) ingest newer Codex chats into the chat archive (best-effort, local-only)
  2) run `StatiBaker/scripts/build_dashboard.py` for the missing days

Progress:
- The Missing Runs panel shows a spinner + estimated % during ingest/build.

Disable (restore manual-only behavior):
- Set `ITIR_AUTO_BUILD_MISSING_DASHBOARDS=0`.

Notes:
- Auto-build requires `SB_RUNS_ROOT` to be writable. If it is not writable, the
  Missing Runs panel will list missing days and you can fix permissions or point
  `SB_RUNS_ROOT` at a writable directory.

## Loading SB dashboard Data (DB-first)

The dev page hydrates dashboard payloads from the canonical dashboard DB.

Priority order:
1. `SB_DASHBOARD_DB=/abs/path/to/dashboard.sqlite`
2. `SB_RUNS_ROOT=/abs/path/to/StatiBaker/runs_local` (DB defaults to `SB_RUNS_ROOT/dashboard.sqlite`) + `SB_DATE=YYYY-MM-DD`
3. Legacy fallback (regression/debug only): `SB_DASHBOARD_JSON=/abs/path/to/dashboard_all.json`

Example:

```bash
cd itir-svelte
SB_RUNS_ROOT=../StatiBaker/runs SB_DATE=2026-02-03 npm run dev
```

## Thread Viewer (Chat Archive)

The `/thread/<canonical_thread_id>` route renders messages from the local chat archive.

Tool messages:
- Structured tool calls like `exec_command`, `write_stdin`, and `update_plan` are rendered in a compact, “beautified” block.
- The **raw JSON payload is hidden by default**; expand `raw payload` to view/copy it.
- `update_plan` shows the plan items (status + step) instead of dumping the full JSON.
- `write_stdin` shows `session_id`, `yield_ms`, and a `chars=(empty|N)` summary to avoid wasting vertical space on empty payloads.
- `notebooklm_meta_event` renders NotebookLM lifecycle cards (event, notebook/source/artifact fields, snippet/keywords when present) with raw payload still behind an expander.
- NotebookLM summary snippets render through the same Markdown-lite renderer used by chat bubbles.
- NotebookLM thread view builds a per-thread source index (numbered list + type badges) and event cards reference those source numbers/ranges instead of repeating long source titles on every row.
- Non-tool messages render a small Markdown subset (headings, bold, lists, fenced code) so formatting matches the original chat better.

Performance:
- The thread viewer progressively mounts a tail-window of messages and prepends more as you scroll upward, to keep DOM size reasonable for long threads.

## Corpus Browser

`/corpora` is the new read-only landing surface for the main local ITIR corpora:

- chat archive threads from `~/chat_archive.sqlite` or `~/.chat_archive.sqlite`
- Messenger test DB rows from the bounded ingest store
- OpenRecall captures from the canonical ITIR DB

Route family:
- `/corpora`
- `/corpora/chat-archive`
- `/corpora/messenger`
- `/corpora/openrecall`
- `/corpora/processed`
- `/corpora/processed/personal`
- `/corpora/processed/broader`

This is meant to make it easy to inspect what has actually been ingested before
dropping into more specialized workbenches.

## Normalized Artifact Surface

`/graphs/normalized-artifacts` is the first suite-level read-only consumer for
the root normalized artifact contract.

Current bounded scope:

- one review/promotion artifact from `SensibLaw`
- one compiled-state artifact from `StatiBaker`
- optionally one producer-owned archive artifact from
  `chat-export-structurer` when an explicit normalized-artifact path is
  provided
- optionally one producer-owned source artifact from `tircorder-JOBBIE` when
  an explicit normalized sidecar path is provided
- optionally one producer-owned retrieval/follow artifact from
  `notebooklm-py` when an explicit normalized-artifact path is provided

The route reads producer-owned normalized artifacts directly. It does not turn
`StatiBaker` into a review engine and it does not turn `SensibLaw` into a
state reducer. It also does not invent archive semantics locally for
chat/archive producers.

Additional behavior:

- Contract-conformance visibility is explicit:
  - root schema-version match
  - required-field coverage
  - authority/derived consistency hints
  - follow-obligation consistency hints
  - flat contract issues when the payload drifts from the root shape
- `tircorder-JOBBIE` source sidecars stay source-shaped and do not get a local
  state drill-in.
- `notebooklm-py` retrieval/follow artifacts stay derived-only and
  non-authoritative.

The current operator questions are explicit on the page:

- what this artifact is
- why it exists
- what supports it
- what remains unresolved

For review-backed artifacts, the route also surfaces the existing fact-review
workflow context already emitted by the producer path:

- promotion-gate decision and reason
- recommended next review view/filter
- direct drill-in to the persisted fact-review workbench

For compiled-state artifacts, the route stays state-shaped and offers a bounded
drill-in to the timeline ribbon instead of inventing a local review workflow.

For archive artifacts, the route is explicit-path only for now and offers a
bounded drill-in to `/corpora/chat-archive`.

For `tircorder-JOBBIE` source sidecars, the route keeps the artifact
source-shaped and does not invent a local state or review drill-in.

For `notebooklm-py` retrieval/follow artifacts, the route keeps them explicitly
derived and non-authoritative rather than treating them as archive, state, or
promoted truth.

`/corpora/processed` is the matching browse layer for extracted outputs such as
semantic relation counts, abstentions, semantic basis counts, and top
predicates per corpus, with links through to the full semantic-report
workbench.

`/corpora/processed/personal` is the personal-results layer over the user's
actual persisted corpora/results, including:
- live `:real_` fact-review runs from the canonical ITIR DB, hydrated
  DB-first through the persisted fact-review workbench/acceptance paths
- persisted contested affidavit-review runs from the canonical ITIR DB when
  available
- bounded feedback-receipt capture/review over the canonical ITIR DB:
  - one-receipt form
  - JSONL paste/import form
  - recent receipt cards
  - provenance-first drill-ins back to canonical internal objects/routes when
    the receipt already carries a stable ref (`target_surface`, thread id,
    fact-review selector)
  - explicit capture fields for canonical thread ids and fact-review selector
    refs so those drill-ins can be recorded deliberately at collection time
- artifact fallback cards, including the latest live contested Google Docs
  review when present under `/tmp`

The fact-review part of this page is runtime DB-first. The affidavit section now
prefers the persisted contested-review receiver and only falls back to artifact
cards when no persisted run is available.

`/corpora/processed/broader` and its detail pages expose wider diagnostic
artifacts such as `public_bios_timeline` vs `corpus_book_timeline`,
mention-heavy events, unresolved-surface pressure, seed diagnostics, workflow
pressure inventories, and raw-source backlog summaries.

## Graph Rendering Notes (LayeredGraph)

The interactive graph views (`/graphs/*`) use `itir-svelte/src/lib/ui/LayeredGraph.svelte`.

Edge kinds + default styling:
- `sequence`: solid neutral stroke (time chain + primary flow)
- `role`: solid neutral stroke (subject/object/requester connections)
- `context`: indigo/blue dashed Bezier (`stroke-dasharray: 2 5`) used for cross-lane context links, notably Source/Lens -> action
- `evidence`: blue dashed Bezier (`stroke-dasharray: 3 4`) used for action -> evidence

Performance note (important):
- SVG `stroke-dasharray` on hundreds/thousands of Bezier `<path>` elements is expensive and can tank pan/zoom FPS.
- Policy: keep dashed edges for small graphs; for dense graphs we only show dashed styling on "hot" edges when a node is expanded, and fall back to solid strokes otherwise.
- If we add new lanes that connect broadly (like Source/Lens), prefer solid strokes by default and reserve dashed for focused/filtered interactions.

## Workbench Surfaces

`itir-svelte` uses the term `workbench` for routes that are intentionally more
inspection-heavy than the main dashboard surfaces.

Workbench characteristics:
- built for debugging, review, and interaction with a bounded payload or artifact
- may expose richer controls, overlays, provenance, and temporary diagnostics
- can use stronger developer/reviewer affordances than the main user-facing
  dashboard modules
- remain display-layer tools; they do not gain independent semantic authority

Current examples:
- `/viewers/hca-case`: transcript + document viewer workbench
- `/graphs/timeline-ribbon`: conserved-allocation ribbon workbench over SB
  dashboard timeline payloads
- `/graphs/fact-review`: persisted fact-review workbench, now including the
  first shared follow/review control-plane queues:
  - AU `authority_follow`
  - generic fact-review `intake_triage`
  - generic fact-review `contested_items`
  rendered from shared `control_plane` / `queue` metadata
- `/graphs/semantic-report`: semantic report workbench for graph + token-arc
  debugging
- `/graphs/mission-lens`: fused actual-vs-should mission workbench over ITIR
  planning artifacts and SB dashboard data

Why the term matters:
- it separates exploratory/debug UI from parity/dashboard UI
- it gives us one stable label for routes that are intentionally more “lab
  bench” than “finished report”

Transcript-browser migration note:
- treat `/viewers/hca-case` plus the shared viewer primitives as the current
  migration target for retained transcript-browser behavior from legacy
  `Pelican/`
- do not add new product-facing transcript UI work to Pelican/Zola

## Semantic Report Debug Surface

The semantic report route (`/graphs/semantic-report`) is also the current
workbench for text-local semantic debugging.

Current intended direction:
- keep the corpus summary + predicate graph
- add an event-local token arc inspector for text-rich semantic events
- on token hover, draw relation arcs colored by semantic family/type and faded
  by confidence tier
- support click-to-pin debugging so arcs stay visible while receipts/anchors are
  inspected
- when an anchor is active, lightly echo other same-role anchors in the same
  relation family within the event text so local structure is easier to debug
- surface anchor provenance (`mention`, `receipt`, `label_fallback`) so weak
  fallback anchoring is visible rather than hidden
- consume a shared text-debug payload contract so the same workbench primitive
  can be fed by multiple producers instead of only the legal semantic-report
  loader
- prove that contract against transcript/freeform semantic payloads as the
  first non-legal producer
- keep semantic anchor/token shaping out of TS where possible; report producers
  should emit `text_debug`, and the Svelte layer should stay a thin renderer
- pair the arc view with a compact producer-owned review summary so predicate
  counts, cue surfaces, and excluded arc rows are visible without opening raw
  report JSON
- move the workbench span contract toward producer-owned char spans plus source
  artifact ids; token spans should remain render helpers, not the only anchor
  contract
- use those char spans in an event-local document viewer inside
  `/graphs/semantic-report`; keep any source-document panel explicit about
  unavailable source text rather than faking it from event-local content
- transcript/freeform is the first lane expected to provide a real source
  document payload for that second viewer; timeline-driven legal lanes should
  emit grouped timeline-source text from normalized payloads rather than fake
  full documents in TS
- keep the workbench as a real review surface:
  - document/source viewers can push selection back into the token-arc panel
  - reviewers can submit append-only correction records keyed by
    event/relation/anchor refs
  - recent correction submissions should stay visible for the active corpus/run
- surface producer-owned mission/follow-up observer artifacts when present so
  SB-facing overlays can be inspected before export/import

Important boundary:
- this is a display/debug layer over report payloads and receipts
- it may emit append-only review/correction artifacts, but it does not rewrite
  semantic extraction, promotion, or canonical spans in place

## Chat Threads (Dashboard)

The Chat Threads table supports source-based filtering so you can enable/disable
thread sources without changing the selected date range.

- Source options are derived from per-thread `source_ids` when available.
- Fallback source uses thread `origin` when `source_ids` is missing.
- Default behavior enables all discovered sources.
- A thread row is shown when at least one of its sources is enabled.
- If NotebookLM lifecycle metadata is present for the selected range, the source
  selector also shows `notebooklm (meta-only)` to make that provenance visible.
  NotebookLM rows are derived from `runs/<date>/logs/notes/<date>.jsonl`
  (grouped by `notebook_id_hash`, with an unscoped bucket when missing).
- NotebookLM thread rows open in the same thread viewer route, where lifecycle
  events are shown with display fields/snippets rather than raw-only JSON.

## Future: Global Source Scope (Option 2)

Current source filtering is local to Chat Threads. A future global source scope
would apply one shared source selection across multiple modules.

Planned semantics:
- One shared source picker near the top of the dashboard.
- Chat panels (threads/flow/timeline) filtered by chat sources.
- Metadata-only modules (NotebookLM lifecycle) filtered by metadata sources.
- Modules with no source mapping keep rendering and show their effective scope.
