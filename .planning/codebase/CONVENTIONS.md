# Coding Conventions

**Analysis Date:** 2026-03-06

## Naming Patterns

**Files:**
- Python tests: `tests/test_*.py` (examples: `SensibLaw/tests/test_cli_smoke.py`, `SeaMeInIt/tests/test_measurement_schema_parity.py`)
- Python e2e tests: `tests/e2e/test_*.py` (example: `SensibLaw/tests/e2e/test_collections_ui.py`)
- Playwright tests: `*.spec.ts` (examples: `SensibLaw/playwright/tests/knowledge_graph.spec.ts`, `SensibLaw/playwright/tests/ingest.spec.ts`)
- Node tests: `*.test.js` under `test/` or `tests/` (examples: `JesusCrust/packages/js-host/test/apply.test.js`, `tircorder-JOBBIE/tests/node/test_transcript_browser_scripts.test.js`)
- Rust: conventional `src/main.rs` and integration tests under `crates/<crate>/tests/*.rs` (example: `JesusCrust/crates/core/tests/engine.rs`)

**Functions:**
- Python: `snake_case` (general convention; examples in `SensibLaw/tests/test_cli_smoke.py`)
- JS/TS: `camelCase` in tests and configs (example: `JesusCrust/packages/js-host/test/apply.test.js`)
- Rust: `snake_case` for functions/tests (example: `JesusCrust/crates/core/tests/engine.rs`)

**Variables:**
- Python: `snake_case` (general convention)
- JS/TS: `camelCase` (general convention)

**Types:**
- Python: uses type checking in some subprojects (MyPy config in `SensibLaw/pyproject.toml`)
- TS: types in `*.ts` files per subproject (examples: `SensibLaw/playwright.config.ts`)

## Code Style

**Formatting:**
- Python: Ruff is recommended in contributor docs: `SensibLaw/CONTRIBUTING.md`, `SeaMeInIt/CONTRIBUTING.md`
- Mixed JS/TS formatting across subprojects (not uniform):
  - Semicolons + single quotes in `SensibLaw/playwright.config.ts`
  - No semicolons + single quotes in `moltbook-api-client/eslint.config.js`
  - 4-space indent + double quotes in `tircorder-JOBBIE/tests/node/test_transcript_browser_scripts.test.js`

**Linting:**
- Python: Ruff (recommended) in `SensibLaw/CONTRIBUTING.md`, `SeaMeInIt/CONTRIBUTING.md`
- JS: ESLint flat config present in `moltbook-api-client/eslint.config.js`

## Import Organization

**Order:**
- Not detected as a single repo-wide standard; follow local subproject conventions.

**Grouping:**
- Not detected

**Path Aliases:**
- Not detected

## Error Handling

**Patterns:**
- Not detected as a single repo-wide standard

**Error Types:**
- Not detected

## Logging

**Framework:**
- Not detected as a single repo-wide standard

**Patterns:**
- Not detected

## Comments

**When to Comment:**
- Contributor docs emphasize tooling + correctness rather than heavy inline commentary: `SensibLaw/CONTRIBUTING.md`, `SeaMeInIt/CONTRIBUTING.md`

**JSDoc/TSDoc:**
- Not detected

**TODO Comments:**
- Present in multiple Python modules (examples: `whisper_streaming/line_packet.py`, `openrecall/openrecall/screenshot.py`)

## Function Design

**Size:**
- Not detected

**Parameters:**
- Not detected

**Return Values:**
- Not detected

## Module Design

**Exports:**
- Not detected (varies across Python/TS/Rust)

**Barrel Files:**
- Not detected

---

*Convention analysis: 2026-03-06*
*Update when patterns change*
