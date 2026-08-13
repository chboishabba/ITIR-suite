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

Mary-parity fact-review local slices:

```bash
node --test tests/factReview_regressions.test.js
node --test tests/graph_ui_regressions.test.js
```

Preferred Mary real-path repro:

```bash
cd /home/c/Documents/code/ITIR-suite
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id transcript_acceptance_real_intake_v1 \
  --wave wave1_legal \
  --fixture-kind real
```

When the touched surface is `/graphs/fact-review`, prefer adding or extending
coverage for:

- source-centric reopen behavior
- canonical issue-filter usage from backend payload fields
- inspector classification rendering/fallback order
- chronology bucket rendering over persisted `wave1_legal`-style payloads
- real transcript Mary baseline story coverage for:
  - `SL-US-09`
  - `SL-US-10`
  - `SL-US-11`
  - `SL-US-12` to `SL-US-14`

Do not spend a low-judgment loop inventing new fact-review backend behavior in
`itir-svelte`; treat the route as a consumer of the persisted `SensibLaw`
contract and expand consumer-side coverage first.

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
- initial interpretation experiments should try **Lila** first (keep outputs explicitly
  labeled interpretive/hypothetical; never feed back into core)

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
- **Codex-Relay**: `chat-export-structurer` parser/ingest seam coverage expansion and reproducible smoke/fixture validation for cross-project export contracts.
- **Codex-Borealis**: `SL-reasoner` read-only boundary enforcement, output schema/disclaimer invariants, Lila-first experiment posture, and small local regression test expansion.
- **Codex-Kestrel**: `SL-reasoner` and `tircorder-JOBBIE` regression/smoke expansion, plus explicit `TiRC -> SensibLaw` envelope seam coverage.
- **Codex-Relay-Recall**: `openrecall` embedding dependency hardening, fallback path
  implementation, and lane docs/TODO alignment around optional sentence-transformer
- **Antigravity-Titan**: `SensibLaw` Read-Model hardening, Wikidata/Zelph integration coverage, and `StatiBaker` observed-ingest seam verification.
- **Antigravity-Omega**: `SensibLaw` `sl_zelph_demo` hardening, smoke-test parity for Zelph/Wikidata rules, and regression coverage for demo-loop CLI tools.
- **Antigravity-Zelph**: `SensibLaw` Zelph-driven semantic materialization and fixture-driven regression coverage for the `sl_zelph_demo` path.
- **Codex-Aster**: `itir-svelte` graph UI regression hardening, targeted node smoke slices for changed graph pages, and quick gate reports.
- **Antigravity-Warp**: `SensibLaw` query-script regression hardening and `StatiBaker` observed-signals contract verification.
- **Codex-Lumen**: `itir-svelte` graph/workbench a11y coverage expansion (DOM-visible labels, rendered route checks, keyboard + axe smoke), slice-first loop.
- **Antigravity-Apex**: `SensibLaw` database migration integrity, `StatiBaker` receipt emission validation, and root-level orchestration smoke tests.
- **Antigravity-Sentinel**: `SensibLaw` ASR/WhisperX ingest hardening, focusing on `test_asr_importer.py` and `test_whisperx_importer.py` for cross-surface pipeline consistency.
- **Antigravity-Orion**: `SensibLaw` Zelph-driven semantic materialization and fixture-driven regression coverage for the `sl_zelph_demo` path, plus cross-surface verification with `itir-svelte`.
- **Antigravity-Loom**: `StatiBaker` observed-signals contract expansion for `proc_stats` and `disk_io` signals, and `SensibLaw` query-script regression hardening for `--fixture-kind real`.
- **Antigravity-Pulse**: `SensibLaw` Zelph-demo tool repair and regression hardening, fixing `test_sl_zelph_demo_tools.py` assertions and aligning with new S-expression formats.
- **Antigravity-Nova**: `SensibLaw` Zelph-demo tool expansion and regression hardening, specifically adding new test cases for `wikidata_extract.py` with nested properties and verifying `compile_db.py` output with complex modalities.
- **Antigravity-Archive**: `chat-export-structurer` to `SensibLaw` intake contract verification, focusing on chat-thread mapping and metadata preservation benchmarks.
- **Antigravity-Flux-Wiki**: `SensibLaw` Wikipedia surface expansion, specifically focusing on `wiki_timeline` consistency, category-to-event mapping reliability, and cross-surface smoke tests for large-scale Wikipedia imports.
- **Antigravity-Prism**: `SensibLaw` Wikipedia-to-Zelph semantic derivation and fixture-driven regression coverage, specifically hardening the `wiki_timeline` to Zelph logic for complex events.
- **Antigravity-Aether**: `SensibLaw` Wikipedia canonical-state coverage, focusing on article-wide actor/action/object extraction, ordered timeline projection with explicit anchor status, one-hop follow manifest support, and unit-test-backed revision/state-diff correctness over arbitrary revision-locked pages.



---

### Agent Check-ins (completed loops only; append newest at end)

Only record completed loops here. Exploratory starts, lane claims, or "reading /
planning" states belong in `TODO.md` until they have exact commands and a
terminal result.

- 2026-03-20 / revalidated 2026-03-21 — **Codex-Aster** — `itir-svelte` graph UI gate rerun:
  `npm test -- --test-name-pattern graph_ui_regressions` (6 pass),
  `npm run check` (pass), `npm run build` (pass).
- 2026-03-20 / revalidated 2026-03-21 — **Antigravity-Zelph** — `SensibLaw`
  Zelph-demo fixture/tool loop:
  `../.venv/bin/python -m pytest -q tests/test_sl_zelph_demo_tools.py`
  (13 pass).
- 2026-03-20 / revalidated 2026-03-21 — **Antigravity-Warp** — query + observed-signals slices:
  `../.venv/bin/python -m pytest -q tests/test_query_fact_review_script.py`
  (8 pass) and
  `../.venv/bin/python -m pytest -q tests/test_observed_signals_contract.py`
  in `StatiBaker` (17 pass).
- 2026-03-20 / verified 2026-03-21 — **Antigravity-Apex** — migration/schema integrity slices:
  `../.venv/bin/python -m pytest -q tests/test_migration_integrity.py`
  in `SensibLaw` (2 pass) and
  `../.venv/bin/python -m pytest -q tests/test_apex_schema_validation.py`
  in `StatiBaker` (2 pass).
- 2026-03-20 / revalidated 2026-03-21 — **Antigravity-Sentinel** — ASR/WhisperX ingest slices:
  `../.venv/bin/python -m pytest -q tests/test_asr_importer.py tests/test_whisperx_importer.py`
  (6 pass) plus
  `../.venv/bin/python -m pytest -q tests/test_fact_intake_read_model.py`
  (15 pass).
- 2026-03-20 / revalidated 2026-03-21 — **Antigravity-Orion** — Zelph cross-surface slice:
  `../.venv/bin/python -m pytest -q tests/test_sl_zelph_demo_tools.py`
  (13 pass) and
  `node --test tests/zelph_integration.test.js` in `itir-svelte` (1 pass).
- 2026-03-22 — **Antigravity-Titan** — benchmark matrix parity and Zelph reconciliation:
  `../.venv/bin/python scripts/run_fact_semantic_benchmark_matrix.py --max-tier 100`
  (wiki_revision: 344/0/11, au_legal: 303/0/0). Zero-relation results for `wiki_revision` and `au_legal`
  reconciled as **Zelph environment failure** due to empty `zelph_invariants.zlp`. Corrected
  baselines verified locally with healthy rules (wiki: 636/188/291, au_legal: 1500/2244/486).
- 2026-03-22 — **Antigravity-Aether** — Wikipedia revision ingest slice:
  `../.venv/bin/python -m pytest -q tests/test_wiki_revision_harness.py tests/test_wiki_revision_pack_runner.py`
  (10 pass).
- 2026-03-22 — **Antigravity-Aether** — Wikipedia random article-ingest slice:
  `../.venv/bin/python -m pytest -q tests/test_wiki_random_article_ingest_coverage.py tests/test_wiki_random_page_samples.py tests/test_wiki_random_timeline_readiness.py tests/test_wiki_random_lexer_coverage.py`
  (13 pass).
- 2026-03-22 — **Antigravity-Helios** — Wikipedia random article-ingest slice expansion:
  `../.venv/bin/python --noconftest -m pytest -q tests/test_wiki_random_article_ingest_coverage.py`
  (6 pass). Project gate blocked by existing regression in `test_zelph_wiki_volatility_integration.py` (StopIteration).
- 2026-03-22 — **Antigravity-Aether** — Wikipedia canonical-state split:
  `../.venv/bin/python -m pytest -q tests/test_wiki_article_state.py tests/test_wiki_random_article_ingest_coverage.py tests/test_wiki_random_page_samples.py tests/test_wiki_random_timeline_readiness.py tests/test_wiki_random_lexer_coverage.py tests/test_wiki_revision_harness.py tests/test_wiki_revision_pack_runner.py`
  (29 pass).


### Pending / Incomplete Lanes

These were noted in working docs but do not currently have retained completed
loop evidence:

- 2026-03-20 — **Codex-Lumen** — a11y coverage expansion intent recorded, but no distinct completed command log was retained beyond the shared `itir-svelte` gate reruns above.
- 2026-03-20 — **Antigravity-Loom** — initialization only; no completed real-fixture regression command retained.
- 2026-03-20 — **Antigravity-Pulse** — initialization only; no completed repair/test rerun retained.
- 2026-03-20 — **Antigravity-Nova** — initialization only; no completed expansion/test rerun retained.
- 2026-03-20 — **Antigravity-Archive** — research/claim only; no retained `chat-export-structurer` smoke or parser test command.
- 2026-03-20 / revalidated 2026-03-22 — **Antigravity-Flux-Wiki** — `SensibLaw` Wikipedia surface expansion:
  `PYTHONPATH=. ../.venv/bin/pytest -q tests/test_wiki_timeline_requester_extraction.py tests/test_wiki_expansion_smoke.py tests/test_wiki_timeline_category_mapping.py`
  (17 pass).
- 2026-03-20 / verified 2026-03-22 — **Antigravity-Prism** — Wikipedia-to-Zelph semantic derivation:
  `env PYTHONPATH=. ../.venv/bin/pytest -q tests/test_zelph_wiki_volatility_integration.py`
  (4 pass).
