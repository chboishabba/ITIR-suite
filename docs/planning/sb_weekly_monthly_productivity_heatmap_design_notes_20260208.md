# Design Notes: Weekly/Monthly Productivity Heatmaps + Rollups (2026-02-08)

## Prompt / intent
We want GitHub-style cues for answering:
- "When do I work?" across multi-day windows (weekly, monthly-ish).
- "Which days and hours are above/below baseline?"

Hourly resolution is important because day totals hide "what time it happens."
We also want this to be *multi-signal*, not "git only": user input volume,
calendar density, etc. should be selectable.

## Constraints / non-goals
- Do not reimplement Grafana inside ITIR-suite.
  - This work is strictly within StatiBaker's static HTML dashboards.
  - Grafana remains the intended surface for system observability dashboards and alerting.
- Do not build an interactive dashboard editor/query builder.
  - Keep the output as deterministic JSON + static HTML render.
- Do not emit or visualize PHI.

## What changed (implementation summary)
We extended the existing SB daily/weekly/lifetime dashboards to support:
1. **Hourly bins that include additional activity lanes**
   - `frequency_by_hour` now includes `git` (commit events) and `activity` (activity ledger sessions).
   - This fixes a prior blind spot where daily hour charts omitted important "work" indicators even though the events were present in the timeline.

2. **GitHub-inspired weekly/lifetime heatmaps**
   - New rollup payload field: `weekday_hour_heatmaps`.
   - Weekly and lifetime HTML now render a GitHub-style weekday x hour grid with
     signal toggles (tick/untick) so the same visualization can answer:
     - “Show me the composite score across selected signals”
     - “Show me just calendar”
     - “Show me just input”
     - “Show me just git”

3. **Rollups that explicitly answer “which days/hours are above baseline?”**
   - New "Above / Below (Rollups)" section renders:
     - By weekday (avg/day) with +/- % vs baseline.
     - By hour (avg/day) with +/- % vs baseline.
     - Top weekday-hours (avg/day) table.

Code references:
- `StatiBaker/sb/dashboard.py`:
  - Added `git` + `activity` to daily `frequency_by_hour`.
  - Added `weekday_hour_heatmaps` aggregation for weekly/lifetime payloads.
  - Added heatmap + rollup renderers to weekly/lifetime HTML.
- `StatiBaker/tests/test_dashboard.py`: assertions for new bins and rendered sections.

## Data model / “score across all” (with toggles)
We expose lanes for selection (tick/untick) and compute a composite by default.

Key idea:
- The composite is a **score**, not a raw count, when normalization is enabled.
- This avoids the classic failure mode where high-volume lanes (e.g. `input`)
  swamp lower-volume lanes (e.g. `git`).

Defaults:
- **Selected lanes:** all lanes that have data in the window ("score across all").
- Quick narrowing: an "Intent set" button to jump back to a smaller subset when desired.

We still allow raw counts by turning normalization off (useful when selecting a
single lane, or when you explicitly want “volume”).

## Normalization choices (critical)
Per-lane computations are built from **avg/day per weekday-hour** (not raw totals).

Why:
- A 30-day window would otherwise look “more intense” than a 7-day window purely due to longer accumulation.
- Avg/day lets us compare patterns between windows without conflating “more days” with “more intensity.”

Then, if normalization is enabled, each selected lane is scaled by its own
max avg/day (within the window) before combining into the composite score.

This makes “score across all” behave sensibly across heterogeneous lanes.

## Baseline / “above vs below”
For rollups we define baseline as:
- weekday baseline: overall avg/day (total work / total days)
- hour baseline: overall avg/hour (overall avg/day / 24)

Then we compute `delta_pct` per weekday/hour relative to its baseline and display it inline.

This gives you:
- “Mondays are +32% above baseline”
- “08:00 is +55% above baseline”

## Monthly view semantics (current)
SB does not have a calendar-month boundary view yet.

Current supported "monthly-ish" view is a trailing N-day window using weekly machinery:
`python scripts/build_dashboard.py --date YYYY-MM-DD --weekly --weekly-days 30`

This is a deliberate choice to keep semantics simple and avoid calendar logic creeping into dashboards prematurely.

## Known limitations / next follow-ups
1. **Agent exec commands are counted, but not timestamp-binned**
   - `shell_commands_agent_exec` is computed from tool-use SQLite messages, but those messages are not converted into hourly `shell` events.
   - Result: Shell totals include agent execs, but `Shell/hour` does not.
   - This is tracked separately under “Tool Use Summary view follow-up” in `TODO.md`.

2. **“Work” is a heuristic**
   - Now represented as selectable lane sets + a composite score.
   - We can tune default selections and add new lanes (e.g., calendar density by duration, not just event counts).
   - If we add more lanes, keep semantics explicit and privacy constraints intact.

## Why this is consistent with “don’t reimplement Grafana”
Grafana is for:
- live time series, alerting, drilldown across infra/app metrics (Prometheus/Loki/Tempo, etc.)

SB dashboards are for:
- deterministic personal/agent activity summaries from local event lanes
- static “pattern of work” visualization tied to the same canonical SB run artifacts

This work adds a GitHub-inspired *pattern visualization* to SB, not an observability platform.
