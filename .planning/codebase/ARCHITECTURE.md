# Architecture

**Analysis Date:** 2026-03-06

## Pattern Overview

**Overall:** Multi-project suite repo (multiple independent apps/tools) with some cross-runtime orchestration

**Key Characteristics:**
- Multiple distinct subprojects (Python, Rust, Node/SvelteKit) under one repo root: `README.md`
- Mixed execution models: CLIs, web apps, Python backends, Rust native tools
- Cross-runtime orchestration exists (Node server code shells out to Python for dashboard building/querying) in `itir-svelte/src/routes/+page.server.ts`, `itir-svelte/src/lib/server/buildMissingDashboardsJob.ts`

## Layers

**Web/UI Layer (per project):**
- Purpose: user-facing UI and server hooks
- Contains: SvelteKit server routes, hooks
- Examples: `itir-svelte/src/routes/+page.server.ts`, `itir-svelte/src/hooks.server.ts`

**Service/Backend Layer (per project):**
- Purpose: domain logic exposed as CLIs/services
- Contains: FastAPI modules, Python service code
- Examples: `SensibLaw/fastapi.py`, `WhisperX-WebUI/backend/main.py`

**Core/Engine Layer (Rust crates):**
- Purpose: reusable engine/scheduler/store/graph primitives
- Contains: engine + scheduler + store + graph modules
- Examples: `JesusCrust/crates/core/src/engine.rs`, `JesusCrust/crates/core/src/scheduler.rs`, `JesusCrust/crates/core/src/store.rs`, `JesusCrust/crates/core/src/graph.rs`

**Harness/Runner Layer (Rust):**
- Purpose: test harness / replay / transaction runner
- Examples: `JesusCrust/crates/harness/src/runner.rs`, `JesusCrust/crates/harness/src/replay.rs`, `JesusCrust/crates/harness/src/transaction.rs`

## Data Flow

**Dashboard request/build (SvelteKit -> Python -> SQLite):**
1. Request hits server-side route in `itir-svelte/src/routes/+page.server.ts`
2. Server code reads env configuration for dashboard DB and runs-root (e.g. `SB_DASHBOARD_DB`, `SB_RUNS_ROOT`)
3. Server code invokes Python helpers/jobs (build/query) in `itir-svelte/src/lib/server/buildMissingDashboardsJob.ts`
4. Python reads/writes SQLite db(s) and outputs dashboard artifacts consumed by the UI

**State Management:**
- Primarily file/SQLite based (local DBs, caches), configured via environment variables in `itir-svelte/src/routes/+page.server.ts`, `itir-svelte/src/lib/server/wikiTimelineAoo.ts`

## Key Abstractions

**Rust engine/store/graph primitives:**
- Purpose: core runtime model for one Rust subsystem
- Examples: `JesusCrust/crates/core/src/engine.rs`, `JesusCrust/crates/core/src/store.rs`, `JesusCrust/crates/core/src/graph.rs`
- Pattern: module-based (Rust crate) architecture

**Subproject entrypoints:**
- Purpose: define top-level execution boundaries per tool
- Examples:
  - CLI: `SensibLaw/cli/__main__.py`
  - Web UI: `WhisperX-WebUI/app.py`
  - Rust binaries: `tircorder-JOBBIE/src/main.rs`, `tircorder-JOBBIE/src/bin/scan_cli.rs`

## Entry Points

**Python CLI Entry:**
- Location: `SensibLaw/cli/__main__.py`
- Triggers: `python -m SensibLaw.cli` (or equivalent packaging invocation)
- Responsibilities: CLI command routing (details per subproject)

**Python Web App / Service:**
- Location: `WhisperX-WebUI/app.py`, `WhisperX-WebUI/backend/main.py`
- Triggers: app/server startup
- Responsibilities: web UI + backend API/service

**Rust CLI / Binaries:**
- Location: `tircorder-JOBBIE/src/main.rs`, `tircorder-JOBBIE/src/bin/scan_cli.rs`
- Triggers: compiled binaries
- Responsibilities: scanning/conversion/visualisation tooling

## Error Handling

**Strategy:** Not uniform across repo; per-subproject conventions apply.

**Patterns:**
- Not detected in this scan (needs per-subproject deep dive)

## Cross-Cutting Concerns

**Logging:**
- Not detected as a single shared framework; likely per-subproject.

**Validation:**
- Zod used in SvelteKit project dependencies: `itir-svelte/package.json`

**Authentication:**
- Not detected at suite-level

---

*Architecture analysis: 2026-03-06*
*Update when major patterns change*
