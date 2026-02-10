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
