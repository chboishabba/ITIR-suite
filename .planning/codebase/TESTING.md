# Testing Patterns

**Analysis Date:** 2026-03-06

## Test Framework

**Runner:**
- pytest - Python tests across multiple subprojects (examples: `SensibLaw/tests/test_cli_smoke.py`, `SeaMeInIt/tests/conftest.py`)
- Playwright - browser/e2e tests in SensibLaw (see `SensibLaw/playwright.config.ts`)
- Rust `cargo test` - integration tests in crates (example: `JesusCrust/crates/core/tests/engine.rs`)
- Node tests exist in some subprojects (example: `JesusCrust/packages/js-host/test/apply.test.js`)

**Assertion Library:**
- pytest built-in asserts (Python) in `SensibLaw/tests/test_cli_smoke.py`
- Playwright expect (TS) in `SensibLaw/playwright/tests/knowledge_graph.spec.ts`
- Rust `assert!` patterns in `JesusCrust/crates/core/tests/engine.rs`

**Run Commands:**
```bash
pytest                                  # Python tests (per-subproject)
python -m pytest                         # Alternate pytest invocation
cargo test                               # Rust tests (per Rust subproject)
node --test                              # Node built-in test runner (where configured)
```

## Test File Organization

**Location:**
- Python: `tests/` directory per subproject (e.g., `SensibLaw/tests/`, `SeaMeInIt/tests/`)
- Python e2e: `SensibLaw/tests/e2e/`
- Playwright: `SensibLaw/playwright/tests/`
- Rust: `crates/<crate>/tests/` (e.g., `JesusCrust/crates/core/tests/`)

**Naming:**
- Python unit/smoke: `test_*.py` (example: `SensibLaw/tests/test_cli_smoke.py`)
- Python e2e: `tests/e2e/test_*.py` (example: `SensibLaw/tests/e2e/test_collections_ui.py`)
- Playwright: `*.spec.ts` (example: `SensibLaw/playwright/tests/ingest.spec.ts`)
- JS: `*.test.js` (example: `JesusCrust/packages/js-host/test/apply.test.js`)

**Structure:**
```
SensibLaw/
  tests/
    test_cli_smoke.py
    e2e/
      test_collections_ui.py
  playwright/
    tests/
      knowledge_graph.spec.ts
SeaMeInIt/
  tests/
    conftest.py
    test_measurement_schema_parity.py
JesusCrust/
  crates/
    core/
      tests/
        engine.rs
  packages/
    js-host/
      test/
        apply.test.js
```

## Test Structure

**Suite Organization:**
```python
# pytest style
import pytest

def test_smoke():
    assert True
```

**Patterns:**
- SensibLaw’s CLI smoke tests prioritize isolation (avoid importing heavy deps in tests): `SensibLaw/tests/test_cli_smoke.py`
- SensibLaw Playwright suite uses a web server config to run UI tests: `SensibLaw/playwright.config.ts`

## Mocking

**Framework:**
- Not detected as a single repo-wide standard (varies by language/subproject)

**Patterns:**
- Not detected

**What to Mock:**
- Not detected

**What NOT to Mock:**
- Not detected

## Fixtures and Factories

**Test Data:**
- pytest fixtures are used (example: `SeaMeInIt/tests/conftest.py`)
- Fixtures documented in project docs (example: `SeaMeInIt/tests/fixtures/afflec/README.md`)

**Location:**
- Python: `tests/conftest.py` and `tests/fixtures/`

## Coverage

**Requirements:**
- SensibLaw enforces coverage threshold (agent reported `fail_under = 80`): `SensibLaw/pyproject.toml`

**Configuration:**
- Coverage settings in `SensibLaw/pyproject.toml`

**View Coverage:**
```bash
pytest --cov                             # if coverage configured in that subproject
```

## Test Types

**Unit Tests:**
- Python: standard pytest tests (example: `SensibLaw/tests/test_cli_smoke.py`)

**Integration Tests:**
- Rust: crate integration tests (example: `JesusCrust/crates/core/tests/engine.rs`)

**E2E Tests:**
- Browser/e2e: Playwright in `SensibLaw/playwright/tests/`
- Python e2e suite: `SensibLaw/tests/e2e/test_collections_ui.py`

## Common Patterns

**Async Testing:**
- Not detected

**Error Testing:**
- Not detected

**Snapshot Testing:**
- Not detected

---

*Testing analysis: 2026-03-06*
*Update when test patterns change*
