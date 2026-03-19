# Agent Test Loop

This is the default low-judgment test procedure for background agents working in
`ITIR-suite` or one of its subprojects.

Use it when the task is coverage-heavy and the agent should keep churning
without needing architectural judgment each cycle.

Machine-readable companion:

- `docs/planning/agent_surface_map.json`

## Primary Objective

Give every agent the same loop:

1. run the smallest relevant test slice
2. add or extend the nearest missing coverage
3. rerun the same slice until the new coverage is green or blocked
4. widen to the next gate
5. stop with a short findings report if blocked twice on the same issue

This procedure is intentionally conservative. It prefers bounded, repeatable
checks over cleverness.

Background agents are not general fixers. Their default role is:

- expand test, smoke, fixture, and benchmark coverage
- exercise more surfaces and seams
- report findings with reproductions
- avoid substantive implementation work unless it is trivial and tightly local

## Required Behavior

- Do not start with a full-repo test run unless the change is repo-wide.
- Start with the narrowest file-level or feature-level test slice that touches
  the edited code.
- Prefer adding a new narrow test or smoke check if the touched surface lacks
  direct coverage.
- Only widen scope after the current slice is green.
- Do not silently skip failing tests.
- Do not change tests just to make them pass unless the test is clearly wrong.
- If a command takes more than about 60 seconds, print or record progress.
- If a failure appears unrelated to the task, record it as an external blocker
  and move on only if the local slice is still meaningful.
- Do not default to implementation repair. Prefer reporting findings unless the
  required fix is mechanical, obvious, and local to the changed surface.

## Coverage Expansion Rule

When in doubt, expand coverage instead of expanding implementation.

Default expectations:

- If a touched surface has no direct test, add one.
- If a bug is found, add a reproducing regression or smoke test before
  considering a fix.
- If a new CLI path, fixture format, corpus, schema branch, or mode is added,
  add at least one smoke or regression test for it.
- If a producer/consumer seam changed, add or update a seam test on at least
  one side of the contract.
- If no sensible test can be added, report that gap explicitly.

Low-judgment agents should optimize for:

- missing test discovery
- fixture and corpus expansion
- smoke-test addition
- contract regression coverage
- benchmark surface coverage
- failure reproduction quality

Low-judgment agents should not optimize for:

- broad refactors
- architectural cleanups
- speculative fixes
- ontology redesign
- large code motion
- “while I’m here” implementation changes

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

- add or tighten the nearest reproducing coverage if it is still missing
- record the failure clearly
- only make a trivial local repair if required to unblock the new coverage
- rerun the same exact slice
- repeat until green or blocked

### Phase 2: Project Gate

After the local slice is green, run the project-level gate for that subproject.

Examples:

- package-level `pytest` subset
- `npm test` plus `npm run check`
- acceptance-wave command for the affected lane

If it fails:

- record the regression
- only fix if the repair is obvious, local, and needed to validate the new
  coverage
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

For these agents, "report" is a successful outcome if:

- coverage increased
- a missing seam was identified
- a failure was reproduced cleanly
- the next smarter pass has a clear starting point

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

## Surface Map

Background agents should not guess what a file means from its name alone. Use
this section to classify the touched path before choosing a test loop. If a
script or agent can read JSON, prefer `docs/planning/agent_surface_map.json`
for routing and use this section as the human-readable explanation.

Rule:

- if the path is in a listed surface, use that surface's local slice and gate
- if the path crosses two surfaces, treat it as cross-surface work
- if the path changes a contract, schema, read model, or CLI, run the
  cross-surface gate even if the local slice is green

### Repo Root: `ITIR-suite`

Core surfaces:

- `docs/planning/`
  - suite planning, interface contracts, orchestration policies
  - changes here are control-plane/documentation changes
- `scripts/`
  - root orchestration and context-sync helpers
  - changes here are cross-project by default
- `tests/`
  - root-only regression tests for suite glue
- `plan.md`, `status.json`, `TODO.md`, `COMPACTIFIED_CONTEXT.md`
  - orchestration state surfaces

Default interpretation:

- doc-only: no test required unless an example command or contract changed
- root script or root tests changed: run `pytest -q tests`

### `SensibLaw`

Primary surfaces:

- `src/fact_intake/`
  - canonical ingest, review workbench, semantic materialization, Zelph bridge
  - local slices:
    - `tests/test_fact_intake_read_model.py`
    - `tests/test_query_fact_review_script.py` if read/query changed
    - `tests/test_fact_review_acceptance_wave.py` if semantics changed
- `database/migrations/`
  - SQLite schema and migration surfaces
  - always run:
    - `tests/test_fact_intake_read_model.py`
    - `tests/test_query_fact_review_script.py`
- `scripts/query_fact_review.py`
  - operator query/read-model CLI
  - run:
    - `tests/test_query_fact_review_script.py`
- `scripts/run_fact_review_acceptance_wave.py`
  - canonical acceptance-wave runner
  - run:
    - `tests/test_fact_review_acceptance_wave.py`
- `scripts/benchmark_fact_semantics.py`
  - semantic benchmark surface
  - run:
    - `tests/test_fact_semantic_benchmark_script.py`
- `scripts/run_fact_semantic_benchmark_matrix.py`
  - benchmark-matrix orchestration surface
  - run:
    - `tests/test_fact_semantic_benchmark_matrix_script.py`
- `tests/fixtures/fact_semantic_bench/`
  - benchmark corpora and baseline examples
  - run:
    - `tests/test_fact_semantic_benchmark_script.py`
    - `tests/test_fact_semantic_benchmark_matrix_script.py`
- `src/wiki_timeline/`, `src/behavior_projection/`, `src/gwb_us_law/`
  - wiki/public-knowledge ingestion and behavior surfaces
  - usually pair with:
    - `tests/test_fact_review_acceptance_wave.py`
- `src/transcript_semantic/`, `src/au_semantic/`
  - transcript and AU semantic surfaces
  - pair with:
    - `tests/test_fact_intake_read_model.py`
    - affected feature tests
- `sensiblaw_streamlit/`, `ui/`, `playwright/tests/`
  - UI surfaces
  - pair with:
    - `npm run test:e2e`

Contract signals:

- if `src/fact_intake/`, `database/migrations/`, or `scripts/query_fact_review.py`
  changed, treat as shared read-model surface
- if a `.zlp` file changed, treat as semantic/rules surface and run acceptance
- if both Python ingest code and fixtures changed, include the benchmark or
  acceptance gate, not only unit tests

### `itir-svelte`

Primary surfaces:

- `src/lib/server/`
  - server adapters into `SensibLaw` and other backends
  - run:
    - `npm test`
    - `npm run check`
- `src/routes/graphs/`
  - graph and review UI surfaces
  - run:
    - `npm test`
    - `npm run build`
- `src/lib/workbench/`, `src/lib/semantic/`, `src/lib/viewers/`
  - client data-model and rendering surfaces
  - run:
    - `npm test`
    - `npm run check`
- `tests/`
  - direct node test surfaces

Contract signals:

- if a route consumes `SensibLaw/scripts/query_fact_review.py` outputs, treat as
  cross-project surface and note the linked `SensibLaw` contract in the report

### `StatiBaker`

Primary surfaces:

- `tests/`
  - primary regression surface
- dashboard/read-model code and receipt emitters
  - treat as observer/reporting surfaces

Contract signals:

- if work touches receipts, overlays, or cross-project summaries, mention the
  producing project and the expected receipt/input seam

### `SL-reasoner`

Primary surfaces:

- `tests/`
  - main local gate
- reasoning/IR code
  - interpretive layer only, not canonical source-authority storage

Contract signals:

- if work changes import or output posture, preserve the “read-only /
  non-authoritative” boundary in the report

### `tircorder-JOBBIE`

Primary surfaces:

- `tests/`, `src/tests/`
  - local regression surfaces
- capture/transcription/handoff utilities
  - ingestion-adjacent but not canonical fact authority

Contract signals:

- if changes affect reducer or envelope handoff into `SensibLaw`, note the
  `TiRC -> SL` seam explicitly

### `WhisperX-WebUI`

Primary surfaces:

- `backend/tests`
  - API/backend surface
- `tests/`
  - UI/pipeline surface
- `backend/`
  - service/API surface
- `modules/`
  - transcription and processing surface

Contract signals:

- if GPU/runtime-specific code changed, mark the loop as container-backed

### `openrecall`

Primary surfaces:

- `tests/`
  - local gate
- OCR/capture/import code
  - observer/capture surface, not authority-upgrading by itself

Contract signals:

- if changes affect text imported into `SensibLaw`, preserve the
  `observer-not-authority` boundary in the report

### `chat-export-structurer`

Primary surfaces:

- CLI/import surfaces
- archive SQLite write/read logic

Contract signals:

- this project often exposes seam quality through smoke commands rather than a
  large test suite
- if changed output feeds `SensibLaw` or `StatiBaker`, name the downstream seam
  in the report

## Cross-Surface Triggers

Treat the change as cross-surface if any of these are true:

- a schema/migration file changed
- a CLI output contract changed
- a fixture format changed
- a `docs/interfaces.md` or `docs/planning/*contract*` file changed
- a root orchestration file changed
- a `SensibLaw` read-model or benchmark script changed
- an `itir-svelte` server adapter changed

Minimum cross-surface report fields:

- producer surface
- consumer surface
- contract or script touched
- local gate run
- wider gate run

## Active Agents

- **Antigravity**: SensibLaw Zelph/Wiki integration, benchmark parity, and test loop enforcement.
- **Antigravity-Flux**: StatiBaker observer-only governance memory, alignment judgment, and reliability probes.
- **Antigravity-Delta**: SensibLaw fact-review acceptance wave expansion, Zelph-driven semantic materialization, and cross-surface contract verification for ingest pipelines.
- **Antigravity-Sigma**: `itir-svelte` server-adapter contract hardening, `WhisperX-WebUI` transcription-to-ingest seam quality, and root-level orchestration regression coverage.
- **Codex-Atlas**: `openrecall` and `chat-export-structurer` seam coverage, cross-project fixture/smoke expansion, and reproducible gate-reporting for low-judgment test loop lanes.
