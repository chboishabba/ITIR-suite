# Changelog (itir-svelte)

## 2026-02-10
- Added `itir-svelte/` SvelteKit dashboard surface that reads SB dashboard JSON outputs.
- Added query-param date range selection (`?start=YYYY-MM-DD&end=YYYY-MM-DD`) and server-side aggregation over daily payloads.
- Added missing-run detection for selected ranges and a server action to build missing daily dashboards by invoking `StatiBaker/scripts/build_dashboard.py` (requires writable `SB_RUNS_ROOT`).
- Added "When You Work (Weekday x Hour)" heatmap (GitHub contribution calendar cue) computed from daily `frequency_by_hour`.
- Ported core daily modules into reusable components: summary cards, frequency bars, artifacts list, chat threads table, chat flow waterfall, tool-use summary, timeline ribbon (lite), and timeline accounting list.
- Updated layout so Artifacts render full width (separate from Frequency bars) and remain scroll-contained.
- Updated "When You Work (Weekday x Hour)" heatmap so the grid fills available width (responsive columns; squares derived from column width).
- Added `all (sum)` lane option to "Frequency By Hour".
- Tightened Chat Threads row height: hide full thread IDs by default; show short ID on hover with full ID in tooltip.
- Updated Chat Flow Waterfall rendering: each hour strip now fills full width (relative thread shares), with a separate per-hour volume bar.
- Chat Flow Waterfall hover now shows thread title and thread ID; added width mode toggle (`time` vs `messages`) where time mode uses gap-to-next-message/hour-boundary as span weight.
- Chat Threads table: force single-line rows (truncate long titles, widen Thread column via `table-fixed`), and show full thread ID as an overlay on hover with click-to-copy.
- Updated Tool Use variants rendering to collapse Python heredoc invocations (e.g. `<<'PY' ... PY`) into a single `'PY'` variant bucket.
- Timeline: clicking a row now expands a detail panel showing full preview/detail and available context (cmd/pwd when present; parsed fields; raw meta).
- Fixed missing-days builder to resolve `SB_RUNS_ROOT` to an absolute path (prevents building dashboards into the wrong directory when env var is relative). Also surfaces build results/errors in the Missing Runs panel.
- Added reusable UI container `Panel.svelte` for consistent non-section boxes (errors/notices) and used it for the page load error block.
- Added reusable sparkline component `Sparkline.svelte` (GitHub-contrib "heartbeat" cue) and embedded it into summary stat cards for key lanes.
- Artifacts UI: group by folder, display filename only, and add saturation hint based on `seen_count` within the selected range (avoids redundant absolute-path repetition).
