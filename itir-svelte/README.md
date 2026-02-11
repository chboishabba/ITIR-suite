# itir-svelte

SvelteKit + Tailwind implementation workspace for ITIR-suite UIs.

Initial focus: StatiBaker dashboard componentization.

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

Performance:
- The thread viewer progressively mounts a tail-window of messages and prepends more as you scroll upward, to keep DOM size reasonable for long threads.
