# itir-svelte

SvelteKit + Tailwind implementation workspace for ITIR-suite UIs.

Initial focus: StatiBaker dashboard componentization.

## Migration Docs

Use these as the current docs baseline for SB legacy -> Svelte transition:

- Module inventory + parity matrix:
  `docs/planning/sl_sb_web_component_inventory_20260210.md`
- Tool Use Summary display/parser contract:
  `docs/planning/itir_svelte_tool_use_parser_display_contract_20260211.md`
- Chat archive pull/ingest benchmark + runbook (canonical DB workflow):
  `docs/planning/chat_archive_pull_ingest_results_20260213.md`

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

## Loading SB dashboard JSON

The dev page reads a dashboard payload from disk on the server.

Priority order:
1. `SB_DASHBOARD_JSON=/abs/path/to/dashboard_all.json`
2. `SB_RUNS_ROOT=/abs/path/to/StatiBaker/runs_local` + `SB_DATE=YYYY-MM-DD`
3. Fallback: `../StatiBaker/runs/2026-02-03/outputs/dashboard_all.json` (if present)

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
