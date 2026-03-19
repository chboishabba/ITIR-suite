# Agent Test Loop

This is the default low-judgment test procedure for background agents working in
`ITIR-suite` or one of its subprojects.

Use it when the task is implementation-heavy and the agent should keep churning
without needing architectural judgment each cycle.

## Goal

Give every agent the same loop:

1. run the smallest relevant test slice
2. fix obvious failures
3. rerun the same slice until green
4. widen to the next gate
5. stop with a short report if blocked twice on the same issue

This procedure is intentionally conservative. It prefers bounded, repeatable
checks over cleverness.

## Required Behavior

- Do not start with a full-repo test run unless the change is repo-wide.
- Start with the narrowest file-level or feature-level test slice that touches
  the edited code.
- Only widen scope after the current slice is green.
- Do not silently skip failing tests.
- Do not change tests just to make them pass unless the test is clearly wrong.
- If a command takes more than about 60 seconds, print or record progress.
- If a failure appears unrelated to the task, record it as an external blocker
  and move on only if the local slice is still meaningful.

## Standard Loop

### Phase 0: Preflight

- Check `git status --short`.
- Identify the touched project and touched files.
- Pick the nearest test file or script first.

### Phase 1: Local Slice

Run the smallest meaningful test set.

Examples:

- one Python test file
- one Node test file
- one CLI smoke test
- one acceptance-wave subset
- one benchmark corpus tier

If it fails:

- fix code or fixture issues
- rerun the same exact slice
- repeat until green or blocked

### Phase 2: Project Gate

After the local slice is green, run the project-level gate for that subproject.

Examples:

- package-level `pytest` subset
- `npm test` plus `npm run check`
- acceptance-wave command for the affected lane

If it fails:

- fix regressions introduced by the change
- rerun the same project gate

### Phase 3: Cross-Surface Gate

Only run this if the change touched shared contracts, read models, schema,
interfaces, or orchestration scripts.

Examples:

- root `pytest -q tests`
- contract/query CLI smoke tests
- benchmark matrix smoke run

### Phase 4: Report

Every loop should end with a short machine-readable-style report:

- changed files
- commands run
- pass/fail status
- blocker if any
- next recommended command

## Stop Conditions

Stop and report instead of thrashing when:

- the same failure persists through 2 repair attempts
- the fix would require changing unrelated dirty files
- the command needs missing credentials, services, or network access
- runtime or memory explodes unexpectedly
- the correct expected behavior is ambiguous

## Command Matrix

These are the default gates for the main active subprojects.

### Repo Root: `ITIR-suite`

Use this only for root-level scripts, docs-linked tests, or cross-project glue.

Local slice:

```bash
cd /home/c/Documents/code/ITIR-suite
pytest -q tests
```

Use only when root `tests/` or root orchestration code changed.

### `SensibLaw`

Working directory:

```bash
cd /home/c/Documents/code/ITIR-suite/SensibLaw
```

Fast local slices:

```bash
../.venv/bin/python -m pytest -q tests/test_fact_intake_read_model.py
../.venv/bin/python -m pytest -q tests/test_query_fact_review_script.py
../.venv/bin/python -m pytest -q tests/test_fact_semantic_benchmark_script.py tests/test_fact_semantic_benchmark_matrix_script.py
```

Acceptance gate:

```bash
../.venv/bin/python -m pytest -q tests/test_fact_review_acceptance_wave.py
```

Benchmark gate:

```bash
../.venv/bin/python scripts/run_fact_semantic_benchmark_matrix.py --max-tier 100
```

Optional UI gate if UI/e2e files changed:

```bash
npm run test:e2e
```

### `itir-svelte`

Working directory:

```bash
cd /home/c/Documents/code/ITIR-suite/itir-svelte
```

Local slice:

```bash
npm test -- --test-name-pattern <pattern>
```

Project gate:

```bash
npm test
npm run check
npm run build
```

### `StatiBaker`

Working directory:

```bash
cd /home/c/Documents/code/ITIR-suite/StatiBaker
```

Default gate:

```bash
pytest -q
```

If a smaller file-level slice exists, prefer that first.

### `SL-reasoner`

Working directory:

```bash
cd /home/c/Documents/code/ITIR-suite/SL-reasoner
```

Default gate:

```bash
pytest -q tests
```

### `tircorder-JOBBIE`

Working directory:

```bash
cd /home/c/Documents/code/ITIR-suite/tircorder-JOBBIE
```

Default gate:

```bash
pytest -q tests
```

### `WhisperX-WebUI`

Working directory:

```bash
cd /home/c/Documents/code/ITIR-suite/WhisperX-WebUI
```

Default gate:

```bash
pytest -q tests backend/tests
```

Use the container-backed environment if the touched code depends on GPU or the
Whisper runtime.

### `openrecall`

Working directory:

```bash
cd /home/c/Documents/code/ITIR-suite/openrecall
```

Default gate:

```bash
pytest -q tests
```

### `chat-export-structurer`

This project is often exercised through CLI smoke tests rather than a local
Python test suite.

Working directory:

```bash
cd /home/c/Documents/code/ITIR-suite/chat-export-structurer
```

Default smoke pattern:

```bash
python -m ingest --help
```

If a dedicated test command is later added, update this document and use that
instead of the CLI-only smoke.

## SensibLaw Semantic Loop

Use this exact order for fact-intake or Zelph-related work:

1. nearest file-level `pytest` target
2. `tests/test_fact_intake_read_model.py`
3. `tests/test_query_fact_review_script.py` if read/query surfaces changed
4. `tests/test_fact_semantic_benchmark_script.py` and matrix smoke if benchmark code changed
5. `tests/test_fact_review_acceptance_wave.py`
6. optional benchmark matrix at `--max-tier 100`

If semantic refresh, ontology, or benchmark code changed, include in the report:

- refresh status
- assertion count
- relation count
- policy count
- elapsed ms or elapsed ms per doc if benchmarked

## Report Template

Use this exact shape in terminal output or commit notes:

```text
Scope: <project>/<feature>
Changed: <paths>
Slice: <first command>
Project gate: <second command>
Cross-surface gate: <third command or skipped>
Result: pass | fail | blocked
Blocker: <none or one line>
Next: <next command or handoff>
```

## Update Rule

When a project gains a better default test command, benchmark, or acceptance
gate, update this file in the same change. Do not let the test loop drift away
from reality.

## Active Agents

- **Antigravity**: SensibLaw Zelph/Wiki integration, benchmark parity, and test loop enforcement.
- **Antigravity-Flux**: StatiBaker observer-only governance memory, alignment judgment, and reliability probes.
