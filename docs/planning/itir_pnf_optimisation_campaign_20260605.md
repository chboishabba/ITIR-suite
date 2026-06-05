# ITIR / PNF Optimisation Campaign Plan

Date: 2026-06-05

## Purpose

Define the optimisation campaign for the ITIR / PNF stack before more speed
work lands. This is a staging and gating note: it records what is already
measurable, what is merely suspected, and where optimisation should start.

The short answers are:

- the repo has partial performance matrices, not one unified ITIR / PNF
  regression matrix
- Tree-sitter is the right kind of tool for bounded code-structure evidence,
  but not for semantic promotion and not yet as a new dependency or submodule
- regex is a last-resort lexical and ingestion tool only; regex-derived rows
  may emit `lexical_hint_v1` hints, never direct semantic observers or direct
  `PredicatePNF` carriers
- `../dashiCORE` / Vulkan is a P0 lane once there is a stable adapter ABI,
  CPU parity, and timing attribution; the first integration should be by path
  adapter, not by submodule
- Wikidata should connect to PNF at review and change boundaries, not inside
  raw graph projection

## Evidence Base

This plan is grounded in the current repo and adjacent mathematical substrate:

- `SensibLaw/docs/pnf_itir_primer.md`
- `SensibLaw/docs/planning/pnf_itir_concise_flow_20260521.puml`
- `SensibLaw/docs/planning/tree_sitter_code_pnf_observer_contract_20260605.md`
- `scripts/chat_archive_batch.py`
- `SensibLaw/src/sensiblaw/conversation_vm/reducer.py`
- `SensibLaw/src/text/residual_lattice.py`
- `SensibLaw/scripts/run_fact_semantic_benchmark_matrix.py`
- `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md`
- `docs/planning/wikidata_disjointness_report_contract_v1_20260325.md`
- `SensibLaw/docs/planning/wikidata_temporal_pnf_constraint_contract_20260502.md`
- `/home/c/Documents/20260604_070337_allm_20260604_070337.txt`
- `../dashiCORE/README.md`
- `../dashiCORE/benchmarks/README.md`

The allm note is treated as formal background: balanced trits, carrier/support
factorisation, kernels, defects, admissibility quotients, hierarchy, and
Base369-style periodic structure. It should guide what is worth optimising:
carriers, kernels, defects, receipts, and admissibility-preserving transforms,
not arbitrary text throughput divorced from the formal surface.

## Control Card

- Objects: archive messages, message slices, `PredicatePNF` atoms, residual
  states, Wikidata entities, code observation rows, dashi carriers, Vulkan
  parity hashes
- Requirements: durable partial progress, semantic parity, reproducible
  baselines, receipt preservation, explicit backend attribution
- Code and artifacts: batch SQLite rows, benchmark JSONL, residual comparison
  outputs, Wikidata review packs, code-observation JSONL, dashi benchmark rows
- State: resumable archive runs, Conversation VM state, residual indexes,
  Wikidata projection caches, CPU/GPU benchmark baselines
- Lattice: residual levels, defect reduction, admissibility gates, exact vs
  partial vs contradiction routing
- Proposals: staged optimisation lanes with measured gates
- Governance: no semantic promotion from parser output, GPU hashes, or timing
  alone
- Gaps: unified matrix, per-stage telemetry, code-PNF fact contract, PNF
  numeric ABI, resident GPU benchmark, Wikidata temporal-family index

## Authority Ladder

The repo-wide evidence ladder is:

```text
raw source -> lexical_hint_v1/parser observation -> structured carrier/receipt
  -> PredicatePNF -> residual review -> promoted artifact
```

Regex-derived matches stop at `lexical_hint_v1`. They can help locate spans,
normalize ingestion, or route a later parser, but they cannot directly construct
semantic observers, code observers, `PredicatePNF`, bounded absence claims, task
identity, lifecycle state, or Kanban mutation. Any semantic `PredicatePNF`
candidate must cite a non-regex structured source: tokenizer/parser span,
spaCy/fallback parser bundle, `utterance_latent_fibre` index artifact, Tree-sitter
row, DB/schema receipt, runtime/test receipt, or human review receipt.

`utterance_latent_fibre` index artifacts are an accepted semantic support tier
for utterance carriers. Runtime selection is currently opt-in and resolves in this
order: explicit override, `SENSIBLAW_UTTERANCE_LATENT_FIBRE_INDEX_PATH`,
`SENSIBLAW_UTTERANCE_LATENT_FIBRE_INDEX_CONFIG`, legacy
`SENSIBLAW_UTTERANCE_LATENT_FIBRE_INDEX`, then checked-in default.
It only enriches `PredicatePNF` carriers when explicitly enabled.

Code-related `PredicatePNF` candidates must cite `code_observation_v1`
provenance. Bounded absence requires an explicit observer scan scope such as a
Tree-sitter scan or typed DB/query receipt; it must not be regex-derived.

## Current Performance Matrix State

There is no single performance regression matrix for ITIR / PNF today.

There are useful partial surfaces:

- `SensibLaw/scripts/run_fact_semantic_benchmark_matrix.py` records semantic
  extraction/report drift and elapsed time by corpus/tier
- Wikidata hotspot and disjointness planning docs define reproducible
  structural benchmark lanes
- the archive PNF batch runner now has durable partial outputs and progress
  tables, which can become run-level telemetry
- `../dashiCORE/benchmarks/` emits JSONL rows for CPU/PQ/Vulkan paths with
  timing and parity fields

The missing surface is a unified registry that compares the same run across:

- archive thread selection and chunk planning
- per-message and per-slice compile
- Conversation VM reduction
- residual lattice comparison
- MCP / StatiBaker PNF helpers
- Wikidata projection and review lanes
- code-PNF extraction
- dashiCORE / Vulkan adapter experiments

The campaign should add that matrix before any broad optimisation pass. Without
it, improvements in one lane can hide regressions in semantic parity,
durability, receipts, or backend attribution.

## Target Regression Matrix

The target matrix should be JSONL-first and script-friendly. The initial output
location should be documented as `.cache_local/itir_pnf_perf_matrix/`, with
fixtures or summarized reports promoted later only when stable.

Required row fields:

- `suite`
- `case_id`
- `stage`
- `backend`
- `input_units`
- `input_chars`
- `message_slices`
- `atoms_in`
- `atoms_out`
- `state_bytes`
- `delta_bytes`
- `wall_ms`
- `cpu_user_ms`
- `cpu_sys_ms`
- `rss_peak_mb`
- `sqlite_commits`
- `sqlite_wal_bytes`
- `cache_hits`
- `cache_misses`
- `network_requests`
- `semantic_drift`
- `parity_hash`
- `receipt_count`
- `status`

Initial suites:

- `archive_pnf_batch`
- `conversation_vm_compile`
- `conversation_vm_reduce`
- `residual_lattice`
- `mcp_pnf_tools`
- `statibaker_task_pnf`
- `wikidata_projection`
- `wikidata_review`
- `wikidata_live_cached`
- `code_pnf_extraction`
- `dashi_vulkan_adapter`

The matrix must treat semantic drift, residual outcome changes, missing
receipts, and parity mismatches as regressions even when wall time improves.

## Ranked Optimisation Matrix

| Rank | Subsystem | Stage / function | Need | Readiness | First measurement | First optimisation | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Archive PNF batch | chunk claim, per-message/slice processing, progress rows | Very high | High | stage timings, rows/sec, chars/sec, commit count, WAL bytes | reduce repeated full-thread loads, replace repeated progress `COUNT(*)` with cached counters, batch low-risk progress writes | partial outputs still survive interruption and resume deterministically |
| 2 | Conversation VM compile | `compile_turn`, sentence segmentation, atom IDs, optional projector path | High | Medium | compile wall time per char/sentence, import/probe cost, atom count | cache optional projector availability, avoid repeated parsing work for slices, record per-slice compile stats | no changed small-fixture PNF output |
| 3 | Conversation VM reduce | `step_state`, residual derivation, blocker/contested scans | High | Medium | reducer wall time by atoms/state size, residual comparisons, state bytes | extend indexed reducer fast path, derive residuals from touched atoms, persist deltas where safe | exact parity with current VM tests and representative fixtures |
| 4 | Residual lattice | typed meet, structural signature comparison, role joins | Medium | Medium | comparisons/sec, no-meet rate, contradiction rate, signature cardinality | add fixture-driven indexes by domain/signature/role signature | same residual levels and provenance |
| 5 | MCP / StatiBaker PNF | grounding lookup, task PNF, project context meet | Medium | Medium-low | grounding rows scanned, candidate count, atom count, latency | pre-index grounding rows and context phrases, add receipt-preserving caches | no task promotion or Kanban mutation from cache-only evidence |
| 6 | Wikidata projection | entity payload projection, qualifier drift, migration pack, disjointness | High | Medium | entities/sec, statements/sec, qualifier slots/sec, network/cache counts | cache fetched entity exports, optimize deterministic loops and after-state lookups | same QID/PID provenance and review disposition |
| 7 | Wikidata PNF boundary | temporal family and review-change carriers | High | Medium-low | PNF rows per review pack, residual outcomes, review drift | add temporal-family index at review/change boundary only | raw projection remains graph-local and non-promotional |
| 8 | Code-PNF | source spans to code facts to evidence-only PNF | Medium | Medium | files/sec, facts/sec, parse errors, bounded absence rows | Tree-sitter observer as evidence-only syntax lane via Python bindings | parser output stays evidence-only |
| 9 | dashiCORE / Vulkan | PNF numeric ABI, GEMV, VkFFT, resident-buffer benchmark | High strategic, low immediate | Low-medium | CPU parity hash, submit-to-fence, wall time, fence waits, readback count | path adapter to dashiCORE GEMV/VkFFT; resident buffers; hash-only readback | parity, stable ABI, explicit fallback/perf flags |

## Stage Roadmap

### Stage 0: Baseline And Observability

Implement the unified matrix and add timing around the already-durable archive
runner before further optimisation. The first matrix does not need a dashboard;
JSONL plus a small summarizer is enough.

Acceptance:

- each suite emits stable JSONL rows
- long archive runs show first useful output quickly
- status can identify the dominant stage
- semantic drift and missing receipts are visible alongside timing

### Stage 1: Archive PNF Runner

Optimise the runner because it is the most ready and has the highest operational
impact. The recent durability work makes this safe to measure.

Targets:

- avoid reloading the full thread for every chunk where a run can hold or cache
  thread payloads safely
- avoid `_progress_counts`-style full table counts in hot heartbeat paths
- tune `partial_flush_messages` from a durability default into a benchmarked
  knob
- record per-stage timings for selection, claim, load, compile, reduce, flush,
  and final persist

Do not weaken partial durability to gain speed. The hard gate is resumability
after timeout or interruption.

### Stage 2: Conversation VM CPU Path

Continue the reducer fast path, but only with fixture parity. Compile and
reduce should be measured separately.

Targets:

- cache optional projector import/probe results
- profile segmentation and stable ID hashing before replacing them
- keep reducer indexes warm across ordered thread state
- derive residual and blocker changes from touched atoms where possible
- serialize deltas for chunk outputs when the downstream contract permits it

The reducer must remain sequential per conversation unless a compile-only
parallel stage is introduced before ordered reduction.

### Stage 3: Residual Lattice, MCP, And StatiBaker PNF

Optimise repeated scans, not the authority model.

Targets:

- pre-index atoms by domain, structural signature, predicate, polarity, and
  role signature
- pre-index grounding rows and project-context phrases used by task PNF
- add timing and cache metadata to helper outputs
- keep every cached or accelerated row receipt-bearing

No cache hit may promote a fact, task, or workflow state by itself.

### Stage 4: Wikidata Integration

Wikidata needs optimisation, but raw projection should stay graph-local.
PNF belongs at review, change, and temporal-family boundaries where a bounded
carrier can preserve evidence and residual state.

Targets:

- baseline `project_wikidata_payload`, qualifier drift, migration pack,
  disjointness, and Nat live/acquisition lanes
- cache live fetches and parsed entity exports behind explicit provenance
- optimize deterministic loops: signature generation, qualifier slot
  aggregation, ancestor closure, SCC/parthood scans, and after-state lookup
- add a temporal-family PNF index such as `TempFam(P,I)` only after deterministic
  baselines exist

The gate is unchanged review packet meaning: same QIDs/PIDs, same provenance,
same disposition, and explicit abstention when no typed meet exists.

### Stage 5: Code-PNF And Tree-sitter

Tree-sitter Python bindings are now available in `.venv` from the ITIR-suite
root. The system CLI may also exist, but runtime code should use the Python
bindings so parser behavior is controlled by the project environment.

The repo already has a Tree-sitter observer contract; Stage 5 is now to
implement the Tree-sitter observer as an evidence-only syntax lane, not to
defer Tree-sitter adoption.

Targets:

- define or ratify `code.fact.bundle.v0_1`
- include source artifact, commit/ref, language, parser receipt, facts, spans,
  and optional evidence-only `PredicatePNF` carriers
- use Python Tree-sitter bindings for Python, JavaScript, TypeScript, and TSX
  syntax observations
- keep observations evidence-only, non-authoritative, and bounded by explicit
  scan scope

Tree-sitter facts are syntax evidence only. Compiler/typechecker output is the
stronger source for semantics. Semgrep, ast-grep, and Joern are complementary
rule or graph evidence, not primary formal authority.

### Requisite 3: Regex Migration

Aggressive regex migration is required before semantic extraction lanes are
treated as implementation-complete. Transition-target semantic regex paths must
be replaced with tokenizer, parser, or Tree-sitter-backed carriers, or narrowed
to `lexical_hint_v1` ingestion hints with no PNF construction authority. This
is a documented requisite for the next migration stage, not part of the current
implementation patch.

### Stage 6: dashiCORE / Vulkan P0

Vulkan is strategically P0 once the campaign can tell whether it is helping the
right workload. The existing dashiCORE benchmark notes already warn that simple
Vulkan sign-flip kernels are overhead-dominated, while parity remains the
priority.

Targets:

- define a stable numeric ABI for PNF-adjacent kernels: `z`, `A`, optional `b`,
  shape, dtype, carrier encoding, and receipt IDs
- build a path adapter to `../dashiCORE` before considering a submodule
- start with CPU parity and hash witnesses
- trial GEMV and VkFFT where the workload has enough arithmetic intensity
- measure resident-buffer mode, submit-to-fence timing, fence waits, dispatches
  per run, readback count, and wall time separately
- expose `intent_gpu`, `active_backend`, `operator_device`, `fft_device`,
  fallback reason, and dominant stage in rows

Submodule gate:

- stable adapter API
- reproducible setup without fragile local ABI assumptions
- CPU/GPU parity on pinned fixtures
- measured speedup or measured strategic value on the intended workload
- no use of GPU fingerprints as semantic evidence

Until that gate is met, keep dashiCORE as an adjacent dependency reached by
explicit path configuration.

## Implementation Backlog

1. Add matrix schema and JSONL writer helpers.
2. Add archive batch stage timers and SQLite write metrics.
3. Add Conversation VM compile/reduce microbench fixtures.
4. Add residual lattice comparison fixtures with parity checks.
5. Add Wikidata projection/review benchmark wrappers over existing bounded
   fixtures.
6. Add Tree-sitter code observer fixture and evidence-only JSONL surface.
7. Add dashiCORE path adapter smoke with CPU parity only.
8. Add optional Vulkan GEMV/VkFFT benchmark rows behind explicit availability
   checks.

## Verification Strategy

Every optimisation PR should report:

- performance row diff against the pinned baseline
- semantic drift diff
- receipt count diff
- residual outcome diff
- memory and SQLite write metrics where relevant
- CPU/GPU parity hashes where relevant

Core test commands expected during the campaign:

```bash
pytest tests/test_chat_archive_batch.py
.venv/bin/python -m pytest SensibLaw/tests/test_conversation_vm.py
python -m py_compile scripts/chat_archive_batch.py SensibLaw/src/sensiblaw/conversation_vm/reducer.py
```

Additional benchmark and Wikidata commands should be promoted into this section
only after their output contracts are stable.

## Non-Goals

- Do not add Tree-sitter as a submodule merely to begin code-PNF work.
- Do not add dashiCORE as a submodule until the adapter gate is met.
- Do not treat parse output, Wikidata labels, benchmark speedups, or GPU hashes
  as truth authority.
- Do not trade away archive partial durability for throughput.
- Do not optimize live Wikidata calls before separating network, cache, and
  deterministic projection costs.

## Immediate Next Step

The next implementation step should be Stage 0: a small unified matrix contract
and JSONL emitter that can wrap the archive PNF runner and Conversation VM
without changing PNF semantics. That creates the measurement surface needed to
decide whether the next concrete patch should target SQLite write amplification,
compile cost, reducer state growth, or Wikidata projection loops.
