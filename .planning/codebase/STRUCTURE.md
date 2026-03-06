# Codebase Structure

**Analysis Date:** 2026-03-06

## Directory Layout

```
ITIR-suite/
├── itir-svelte/              # SvelteKit UI + server-side routes for dashboards
├── SensibLaw/                # Python project (CLI + FastAPI + tests + Playwright)
├── WhisperX-WebUI/            # Python web UI + backend service
├── JesusCrust/                # Rust workspace (core engine + harness + JS host)
├── tircorder-JOBBIE/          # Rust project (CLI + tests + Bevy visualisation)
├── StatiBaker/                # Python project with scripts + tests + runs outputs
├── reverse-engineered-chatgpt/ # Submodule/tooling with tests + scripts
├── notebooklm-py/             # Submodule/tooling (has `.env.example`)
├── scripts/                   # Repo-level helper scripts
├── database/                  # Migrations / DB-related artifacts
└── requirements.txt           # Python dependency superset for the suite
```

## Directory Purposes

**itir-svelte/**
- Purpose: SvelteKit web UI + server routes
- Contains: `package.json`, `vite.config.ts`, server hooks and routes
- Key files: `itir-svelte/src/routes/+page.server.ts`, `itir-svelte/src/hooks.server.ts`

**SensibLaw/**
- Purpose: Python app with CLI and FastAPI + browser tests
- Contains: CLI entrypoint, FastAPI module, pytest suite, Playwright suite
- Key files: `SensibLaw/cli/__main__.py`, `SensibLaw/fastapi.py`, `SensibLaw/playwright.config.ts`

**WhisperX-WebUI/**
- Purpose: Python web UI and backend service
- Contains: app + backend main
- Key files: `WhisperX-WebUI/app.py`, `WhisperX-WebUI/backend/main.py`

**JesusCrust/**
- Purpose: Rust workspace and related packages
- Contains: core crate + harness crate + JS host tests
- Key files: `JesusCrust/Cargo.toml`, `JesusCrust/crates/core/src/engine.rs`, `JesusCrust/crates/harness/src/runner.rs`

**tircorder-JOBBIE/**
- Purpose: Rust binaries + tests + visualisation
- Contains: multiple Rust mains, tests, Bevy visualisation
- Key files: `tircorder-JOBBIE/src/main.rs`, `tircorder-JOBBIE/src/bin/scan_cli.rs`, `tircorder-JOBBIE/src/tests/scanner.rs`

**scripts/**
- Purpose: repo-level scripting utilities
- Key files: `scripts/chat_context_resolver.py`

**database/**
- Purpose: SQL migrations/schema changes
- Key files: `database/migrations/20260206_context_fields.sql`

## Key File Locations

**Entry Points:**
- `itir-svelte/src/routes/+page.server.ts` - server-side route handler
- `SensibLaw/cli/__main__.py` - Python CLI entry
- `WhisperX-WebUI/app.py` - Python UI app entry
- `WhisperX-WebUI/backend/main.py` - Python backend entry
- `tircorder-JOBBIE/src/main.rs` - Rust CLI entry
- `tircorder-JOBBIE/src/bin/scan_cli.rs` - Rust secondary CLI entry

**Configuration:**
- `itir-svelte/package.json` - Node scripts/deps
- `itir-svelte/tsconfig.json` - TypeScript config
- `SensibLaw/pyproject.toml` - Python tooling config (typechecking/coverage etc.)
- `requirements.txt` - Python dependency superset

**Core Logic:**
- `JesusCrust/crates/core/src/engine.rs` - Rust core engine module
- `JesusCrust/crates/core/src/store.rs` - Rust store module

**Testing:**
- `SensibLaw/tests/test_cli_smoke.py` - pytest example
- `SensibLaw/playwright/tests/knowledge_graph.spec.ts` - Playwright example
- `JesusCrust/crates/core/tests/engine.rs` - Rust test example
- `tircorder-JOBBIE/src/tests/scanner.rs` - Rust test example

**Documentation:**
- `README.md` - suite overview
- `SensibLaw/README.md` - project docs
- `WhisperX-WebUI/README.md` - project docs
- `StatiBaker/README.md` - project docs

## Naming Conventions

**Files:**
- Python: `tests/test_*.py` and `tests/e2e/test_*.py` in `SensibLaw/tests/`
- Playwright: `*.spec.ts` in `SensibLaw/playwright/tests/`
- Rust: `src/main.rs`, `src/bin/*.rs`, `crates/*/src/*.rs`

**Directories:**
- Subproject roots use distinct names (not a uniform monorepo package layout).

**Special Patterns:**
- Rust workspaces under `JesusCrust/` with `crates/` for internal libraries.

## Where to Add New Code

**New Feature:**
- Primary code: in the relevant subproject root (e.g., `itir-svelte/src/`, `SensibLaw/`, `JesusCrust/crates/`)
- Tests: follow that subproject’s test layout (e.g., `SensibLaw/tests/`, `JesusCrust/crates/*/tests/`)
- Config if needed: `itir-svelte/package.json` or `SensibLaw/pyproject.toml` depending on language

**New Component/Module:**
- SvelteKit: `itir-svelte/src/lib/` or `itir-svelte/src/routes/`
- Python: subproject package modules + `tests/`
- Rust: `JesusCrust/crates/<crate>/src/`

**New Route/Command:**
- SvelteKit route: `itir-svelte/src/routes/`
- Python CLI: `SensibLaw/cli/__main__.py` (or its internal command modules)

**Utilities:**
- Repo-level scripts: `scripts/`

## Special Directories

**.claude/**
- Purpose: Claude Code agent artifacts/worktrees
- Committed: should generally be ignored/ephemeral

---

*Structure analysis: 2026-03-06*
*Update when directory structure changes*
