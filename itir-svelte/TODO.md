# TODO (itir-svelte)

## Purpose
Track SB dashboard module parity work and Svelte-specific componentization tasks.

Primary contract: SB dashboard JSON outputs (`dashboard*.json`) under `SB_RUNS_ROOT`.

## Near-Term (Parity)

- Artifacts: keep full-width section and scroll-contained list.
- Artifacts: group by folder; display filename only; consider surfacing git-derived edit frequency (currently `seen_count` is "days referenced in range").
- Frequency by hour: support `all` (sum) view and consider multi-lane selection/stacked rendering.
- Weekly/lifetime parity modules (from legacy SB HTML):
  - rollups / totals grid
  - NotebookLM lifecycle (`notes_meta_summary`)
  - per-day summary table (daily rows across selected range)
- Routing:
  - add dedicated `weekly` and `lifetime` routes that load
    `dashboard_weekly_*.json` and `dashboard_lifetime*.json` directly when present.

## Timeline Surfaces

- Ribbon: align richer ribbon implementation to the existing ribbon contract docs:
  - `SensibLaw/docs/timeline_ribbon.md`
  - `itir-ribbon/docs/interfaces.md`
- Timeline list: keep "accounting surface" posture (compact rows, full ISO on hover).

## Range Handling

- Decide aggregation source of truth:
  - load precomputed weekly JSON when it exists (preferred for parity), else
    aggregate from daily payloads.
- Define explicit behavior for missing days inside a range:
  - display missing dates
  - offer a "build missing" action
  - do not silently backfill with invented values

## Engineering Hygiene

- Keep domain logic in server loaders/adapters; keep components prop-driven.
- Maintain Zod contracts under `src/lib/sb-dashboard/contracts/` as the runtime gate.
- Avoid SSR/CSR hydration mismatches (defer browser-only reads like `localStorage` to `onMount`).
