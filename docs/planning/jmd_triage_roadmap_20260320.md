# JMD Triage Roadmap (2026-03-20)

## Purpose
Convert the current JMD-related notes into an explicit repo triage so the suite
does not treat "JMD" as a single undifferentiated integration target.

This note is planning-only. It does not introduce a new shipped runtime,
adapter, or authority boundary.

## Current Inputs
- `docs/planning/jmd_itir_intended_surface_20260319.md`
- `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md`
- `COMPACTIFIED_CONTEXT.md`
- `TODO.md`
- `plan.md`
- `status.json`

## Triage Summary
The current JMD material actually splits into two different tracks plus one
explicitly deferred lane:

1. `JMD/ERDFA shard graph -> Casey -> fuzzymodo -> StatiBaker`
   This is future-surface awareness only. Keep it out of active implementation
   until there is a pinned external schema and a concrete producer/consumer
   boundary.
2. `JMD canonical object graph -> SL corpus graph`
   This is the real near-term planning surface because it aligns with the
   suite's existing authority model: canonical objects on one side, read-only
   organisation/overlay outputs on the other.
3. `Proof / post-entropy / provenance-bundle semantics`
   These should shape boundary design now, but they are not a separate
   implementation milestone yet. Treat them as reserved fields and invariants
   for the bridge contract.

## Consistency Check Against Existing Repo Direction
### Already aligned
- `status.json` still points to Casey boundary seams rather than a JMD adapter
  milestone.
- `TODO.md` already keeps the shard-graph lane as future awareness only.
- `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md` already matches the
  repo's current separation of powers:
  JMD authoritative objects, SL advisory organisation, Casey governed proposal
  surface, StatiBaker receipts only.

### Missing before this note
- no single triage doc saying which JMD lane is near-term versus deferred
- no explicit phase order for JMD-related planning work
- no checkpoint list for when JMD work is allowed to move from docs to code

## Roadmap
### Phase JMD-0: Documentation freeze and naming discipline
Status: now

- keep "JMD integration" language split into:
  - `future external shard/task surface`
  - `read-only object-to-corpus bridge`
- do not describe Casey, fuzzymodo, or StatiBaker as already implementing a JMD
  runtime contract
- treat proof/post-entropy language as boundary-design input, not marketing

Exit criteria:
- planning docs use the same split consistently
- TODO and plan documents point at one named triage note

### Phase JMD-1: Read-only bridge contract closeout
Status: next planning/implementation candidate

Scope:
- define the first concrete JMD ingest payload for canonical objects
- define reversible SL anchor/group outputs over those objects
- define advisory overlay payloads that point back to JMD refs
- reserve provenance-bundle and metric-commitment fields without requiring a
  final proof stack

Explicitly in scope:
- object identity rules
- anchor/group/cluster identity rules
- provenance bundle member refs
- corpus-root / pipeline / metric / score commitment fields
- replay and reversibility constraints

Explicitly out of scope:
- direct task execution
- automatic canonical object rewrites
- JMD-native scheduling
- a Rabbit/IPFS-backed live adapter

Exit criteria:
- one ingest payload shape
- one overlay payload shape
- reversible anchor invariants
- conformance tests or fixture specs for payload stability
- fixture pack now pinned by:
  - `docs/planning/jmd_fixture_v1_20260320.md`
  - `docs/planning/jmd_fixtures/jmd_sl_ingest_v1.example.json`
  - `docs/planning/jmd_fixtures/sl_jmd_overlay_v1.example.json`

### Phase JMD-2: Governed proposal path
Status: deferred until JMD-1 invariants are proven

- route competing SL reorganisations through Casey
- keep promotion from advisory overlay to accepted structure explicit
- define what StatiBaker stores as receipts/digests/refs for bridge events

Exit criteria:
- acceptance path is explicit
- receipt shape is bounded
- no component silently becomes the canonical merge authority

### Phase JMD-3: External shard/task surface evaluation
Status: explicitly deferred

Only start when all of the following are true:
- concrete JMD-side repo or adapter target exists
- shard schema is pinned
- producer/consumer contract is named
- there is a reason to integrate execution state rather than only object/corpus
  structure

## Immediate Repo Actions
- Keep current implementation priority on existing Casey boundary seams.
- Treat the JMD object-to-corpus bridge as the only JMD lane that may graduate
  into near-term implementation planning.
- Keep provenance-bundle and metric-commitment fields in docs/TODOs so the
  bridge boundary does not need a second redesign later.

## Implementation Gate
Do not start bridge code until the repo has:
- a fixture-backed JMD ingest example
- a fixture-backed SL anchor/overlay example
- explicit acceptance criteria for reversibility and provenance retention
- named ownership for Casey review and StatiBaker receipt surfaces

## Result
The roadmap answer is:
- near-term: JMD object graph -> SL corpus bridge
- deferred: JMD/ERDFA task scheduling surface
- reserved-design concern: provenance bundles and corpus-relative proof/metric
  commitments
