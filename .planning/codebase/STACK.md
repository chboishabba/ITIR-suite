# Technology Stack

**Analysis Date:** 2026-03-06

## Languages

**Primary:**
- TypeScript/JavaScript - SvelteKit app and server hooks in `itir-svelte/package.json`, `itir-svelte/src/hooks.server.ts`
- Python 3 - CLIs, scripts, backend services across multiple subprojects (examples: `scripts/chat_context_resolver.py`, `SensibLaw/cli/__main__.py`, `WhisperX-WebUI/app.py`)
- Rust - Multiple binaries and crates (examples: `tircorder-JOBBIE/src/main.rs`, `JesusCrust/Cargo.toml`, `JesusCrust/crates/core/src/engine.rs`)

**Secondary:**
- SQL - Local schema/migrations (example: `database/migrations/20260206_context_fields.sql`)
- CSS - Tailwind/PostCSS toolchain in `itir-svelte/package.json`
- Vendored Python package snapshot present (piecash) in `piecash-1.2.1/setup.py`

## Runtime

**Environment:**
- Node.js - SvelteKit server runtime and scripts (see `itir-svelte/package.json`, `itir-svelte/src/hooks.server.ts`)
- Python 3 - scripts invoked via `python3` and shebangs (examples: `scripts/chat_context_resolver.py`, `itir-svelte/src/lib/server/buildMissingDashboardsJob.ts`)
- Rust - native binaries / tooling (examples: `tircorder-JOBBIE/src/bin/scan_cli.rs`, `JesusCrust/crates/*`)

**Package Manager:**
- npm - for `itir-svelte/` (see `itir-svelte/package-lock.json`)
- Python pip-style requirements - repo-wide `requirements.txt`
- Lockfile: `itir-svelte/package-lock.json` present

## Frameworks

**Core:**
- SvelteKit - web app (see `itir-svelte/package.json`)
- FastAPI - Python services (examples: `SensibLaw/fastapi.py`, `doctr/api/pyproject.toml`, `WhisperX-WebUI/backend/main.py`)
- Gradio/Streamlit appear in Whisper tooling and other subprojects (examples: `WhisperX-WebUI/requirements.txt`, `requirements.txt`)

**Testing:**
- Node built-in test runner (`node --test`) in `itir-svelte/package.json`
- pytest - Python tests across subprojects (examples: `SensibLaw/tests/test_cli_smoke.py`, `SeaMeInIt/tests/conftest.py`)
- Playwright - browser/e2e in SensibLaw (see `SensibLaw/playwright.config.ts`)
- Rust `#[test]` integration tests (see `JesusCrust/crates/core/tests/engine.rs`)

**Build/Dev:**
- Vite - SvelteKit build tooling (see `itir-svelte/vite.config.ts`)
- TypeScript - strict mode in `itir-svelte/tsconfig.json`
- TailwindCSS + PostCSS + Autoprefixer in `itir-svelte/package.json`

## Key Dependencies

**Critical:**
- `@sveltejs/kit`, `svelte`, `vite` - SvelteKit web app foundation in `itir-svelte/package.json`
- `tailwindcss` - UI styling pipeline in `itir-svelte/package.json`
- `zod` - runtime validation/schemas in `itir-svelte/package.json`
- Cross-runtime orchestration (Node shelling out to Python for dashboard queries/build) in `itir-svelte/src/routes/+page.server.ts`, `itir-svelte/src/lib/server/buildMissingDashboardsJob.ts`

**Infrastructure:**
- SQLite is a core local persistence layer (queried via Python from Node services) in `itir-svelte/src/routes/+page.server.ts`, `itir-svelte/src/lib/server/wikiTimelineAoo.ts`
- ML/STT stack appears in Python dependency superset (likely driven by Whisper tooling): `torch`, `transformers`, `openai-whisper`, `whisperx` in `requirements.txt`

## Configuration

**Environment:**
- Configuration is primarily per-subproject. Some components rely on raw environment variables (e.g. itir-svelte), while others provide `.env.example` templates (e.g. `notebooklm-py/.env.example`, `WhisperX-WebUI/backend/configs/.env.example`).
- Examples:
  - Tracing toggle: `ITIR_TRACE_MEM` in `itir-svelte/src/hooks.server.ts`
  - Dashboard build/query: `SB_DASHBOARD_DB`, `SB_RUNS_ROOT`, `SB_DATE`, `SB_DASHBOARD_JSON`, `ITIR_AUTO_BUILD_MISSING_DASHBOARDS` in `itir-svelte/src/routes/+page.server.ts`
  - Wiki timeline DB: `SL_WIKI_TIMELINE_AOO_DB` in `itir-svelte/src/lib/server/wikiTimelineAoo.ts`
  - Ingest paths/account: `CODEX_HISTORY_PATH`, `CODEX_LOG_PATH`, `CODEX_SHELL_SNAPSHOTS_DIR`, `CODEX_ACCOUNT_ID` in `itir-svelte/src/lib/server/buildMissingDashboardsJob.ts`

**Build:**
- SvelteKit/Vite config: `itir-svelte/vite.config.ts`, `itir-svelte/tsconfig.json`

## Platform Requirements

**Development:**
- Linux/macOS likely fine; requires at least Node + Python, and Rust for Rust subprojects.
- Docker is used for a GPU-compat environment in the suite docs: `README.md`

**Production:**
- Varies by subproject:
  - SvelteKit app deployment per `itir-svelte/` setup (adapter-auto) in `itir-svelte/package.json`
  - Python services/CLIs deployed/run per their own projects (examples: `WhisperX-WebUI/app.py`, `SensibLaw/cli/__main__.py`)

---

*Stack analysis: 2026-03-06*
*Update after major dependency changes*
