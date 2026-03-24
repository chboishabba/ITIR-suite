# JMD Triage Roadmap (2026-03-20)

## Purpose
Convert the current JMD-related notes into an explicit repo triage so the suite
does not treat "JMD" as a single undifferentiated integration target.

This note is planning-only. It does not introduce a new shipped runtime,
adapter, or authority boundary.

## Current Inputs
- `docs/planning/jmd_itir_intended_surface_20260319.md`
- `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md`
- `docs/planning/jmd_casey_mdl_contract_20260322.md`
- `COMPACTIFIED_CONTEXT.md`
- `TODO.md`
- `plan.md`
- `status.json`

## Current Status Snapshot (2026-03-23)
Implemented locally:
- `itir_jmd_bridge` now ships read-only runtime object/graph/receipt contracts
  plus provider handling for paste/raw, ERDFA descriptors or tar archives, and
  optional IPFS verification.
- latest-post ingest exists and uses conservative adaptive fetch settings rather
  than fixed parallel scraping behavior.
- a local Casey/SL-side MDL-style prototype exists for:
  runtime bundle projection, motif discovery, one-step normalization, and proof
  object emission.
- a latest-post prototype inspection path exists for summarizing candidate
  counts, transform counts, and proof gain over resolved runtime bundles.

Still uncertain or unstable:
- host capability discovery still observes `/raw/{id}` and `/ipfs/{cid}` as
  runtime-useful surfaces, but not as reliable declared API contract.
- live `/browse` and `/raw/example-probe` availability is still variable enough
  that latest-post inspection cannot yet be treated as a strong CI-grade
  online check.
- the prototype proof lane is shape-valid but still intentionally heuristic; it
  is not yet a serious graph canonicalizer.
- there is no local cache/replay layer yet for:
  latest index snapshots or resolved runtime bundles.

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

The bridge lane also needs one explicit internal split:

- `ERDFA` / `DASL`: representation, addressing, and execution substrate
- `DASHI`: quotient / invariance / MDL selection layer over that substrate
- `SL bridge`: reversible anchors, organisation overlays, and future proof
  surfaces over the DASHI-collapsed reading

One additional lesson now sharpened by the local Dashifine/TextGraphs bridge
work:

- do not score bridge progress by graph richness alone
- first prove the bridge is conservative:
  canonical state -> reversible serialization -> graph projection without
  losing identity/order/provenance
- only then evaluate informative graph variants:
  non-local edges, similarity graphs, or corpus overlays that make graph
  observables move with the underlying semantic state
- this means the JMD lane should explicitly distinguish:
  - canonical object/corpus state
  - reversible token/anchor serialization
  - derived graph/overlay observables
  rather than collapsing them into one "graph integration" bucket

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
- make the DASHI role explicit so provenance bundles are interpreted as
  candidate families plus minimal representatives, not just file attachments

Explicitly in scope:
- object identity rules
- anchor/group/cluster identity rules
- provenance bundle member refs
- quotient / invariance terminology for DASHI-backed collapse
- conservative bridge criteria:
  reversibility, source-ref preservation, stable ordering/identity where
  applicable
- informative graph criteria:
  graph/overlay scoring should prefer semantic alignment over raw density or
  connectivity lift
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
- explicit naming for substrate vs selection vs overlay responsibilities
- conformance tests or fixture specs for payload stability
- fixture pack now pinned by:
  - `docs/planning/jmd_fixture_v1_20260320.md`
  - `docs/planning/jmd_fixtures/jmd_sl_ingest_v1.example.json`
  - `docs/planning/jmd_fixtures/sl_jmd_overlay_v1.example.json`
 - a local Casey/SL-side normalization + proof prototype exists before any
   upstream JMD PR is attempted

### Phase JMD-1.5: Local proof-carrying normalization prototype
Status: local prototype now exists; still pre-contract-hardening

Scope:
- keep the prototype entirely on the ITIR/SL side
- ingest graph-like JMD-facing objects
- emit:
  - normalized graph
  - dictionary or motif table
  - transform plan
  - MDL proof object
- prove the shape of phase-2 proof-carrying interop without changing JMD

Explicitly out of scope:
- mandatory upstream JMD changes
- JMD-native proof verification
- Rabbit/event semantics redesign

Exit criteria:
- one local prototype module
- one focused test slice
- one planning note for the future minimal upstream field extension

Current checkpoint:
- met:
  - local prototype module exists
  - focused test slice exists
  - planning note exists
- not yet met:
  - replayable latest-post inspection corpus
  - documented fallback policy when browse/raw surfaces are unavailable
  - serious graph-level canonicalization beyond motif-style proof shape

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
- add replay-oriented resilience before treating live latest-post inspection as
  a dependable ongoing signal

## Implementation Gate
Do not start bridge code until the repo has:
- a fixture-backed JMD ingest example
- a fixture-backed SL anchor/overlay example
- explicit acceptance criteria for reversibility and provenance retention
- named ownership for Casey review and StatiBaker receipt surfaces

That gate is now partially satisfied:
- met:
  - fixture-backed JMD ingest example
  - fixture-backed SL overlay example
  - local Casey/SL-side prototype proof lane
- still open:
  - explicit replay policy for unstable host surfaces
  - named local retention policy for latest-index and resolved-bundle caches

## Result
The roadmap answer is:
- near-term: JMD object graph -> SL corpus bridge
- deferred: JMD/ERDFA task scheduling surface
- reserved-design concern: provenance bundles and corpus-relative proof/metric
  commitments
