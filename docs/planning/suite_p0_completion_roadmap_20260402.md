# Suite P0 Completion Roadmap

Date: 2026-04-02

## Purpose

Turn the new suite-level P0 moonshot into a completion roadmap.

The current legal/compiler, state, capture, archive, and operator plans remain
valid, but they are subordinate to one broader suite target:

- normalized source artifacts in
- normalized observed/reviewed/promoted/derived products out
- bounded union and operator inspection above that

## Constraints, Invariants, Preconditions, Postconditions

The canonical suite-level statement now lives in:

- [README.md](/home/c/Documents/code/ITIR-suite/README.md)
- [suite_smart_journal_moonshot_and_invariants_20260402.md](/home/c/Documents/code/ITIR-suite/docs/planning/suite_smart_journal_moonshot_and_invariants_20260402.md)
- [suite_p0_moonshot_normalized_concepts_20260402.md](/home/c/Documents/code/ITIR-suite/docs/planning/suite_p0_moonshot_normalized_concepts_20260402.md)

That is where the hard constraints, invariants, preconditions, and
postconditions now live explicitly.

## Priority Order

1. Freeze one machine-readable suite-level normalized artifact contract.
2. Align one real adopter in each product-stack family to that contract.
3. Keep context-envelope and promotion-receipt invariants executable.
4. Expand operator surfaces only where the normalized contract is already real.
5. Expand bounded follow and union lanes only when triggers, scope, and stop
   conditions are explicit.

Product-stack adoption was the correct previous phase.

The next phase is proving-ground moonshot lift over that now-real substrate.

Existing AU, GWB, Wikidata/Nat, Brexit, and large-corpus archive/retrieval
lanes now return to priority-driver status because they are the best places to
pressure-test:

- bounded search determination
- uncertainty collapse
- authority-sensitive source selection
- graph and product completeness
- suite-wide quality under scale

The stack segments below remain mandatory constraints, but they are now
infrastructure supporting the proving-ground lift:

- capture and archive producers
- state reducers
- review and promotion reducers
- operator and integration surfaces
- retrieval and bounded follow adapters
- domain-specific proving grounds as the next quality and capability driver
  once those stack segments are real

## Completion Roadmap

### Phase A: Shared Suite Contract

Definition of done:

- one machine-readable normalized artifact contract exists at the root
- it distinguishes:
  - source artifact
  - observed signal
  - compiled state
  - reviewable claim
  - promoted record
  - derived product
  - bounded union surface
- it makes promotion and derived-only boundaries executable
- it encodes bounded follow obligations explicitly rather than implicitly

### Phase B: First Adopter Alignment

Definition of done:

- one capture/archive family can emit the shared normalized artifact shape
- one state family can emit the shared normalized artifact shape
- one review/promotion family can emit the shared normalized artifact shape
- one operator surface can consume that shape without local metaphysics

The first likely adopters are:

- capture/archive:
  - `tircorder-JOBBIE`
  - `WhisperX-WebUI`
  - `chat-export-structurer`
- state:
  - `StatiBaker`
- review/promotion:
  - `SensibLaw`
- operator:
  - `itir-svelte`

Status:

- DONE first bounded review/promotion adopter:
  - `SensibLaw` AU fact-review bundle now emits one
    `semantic_context.suite_normalized_artifact` payload aligned to the root
    `itir.normalized.artifact.v1` schema
  - the adopter stays derived-only and is built from the existing
    `compiler_contract` and `promotion_gate` surfaces rather than inventing a
    second reducer
- DONE first bounded state adopter:
  - `StatiBaker` bundle export now emits `suite_normalized_artifact.json`
    alongside `state.json`
  - that payload is a `compiled_state` artifact aligned to the root
    `itir.normalized.artifact.v1` schema
  - the adopter is built from the existing `state.json` output rather than a
    second state reducer
- DONE first bounded operator adopter:
  - `itir-svelte` now exposes `/graphs/normalized-artifacts`
  - that route reads normalized artifacts directly from the producing repos:
    one current `SensibLaw` review/promotion artifact and one current
    `StatiBaker` compiled-state artifact
  - the route stays read-only and does not reinterpret compiled state as
    review output or review output as state
- DONE first bounded capture/archive adopter:
  - `chat-export-structurer` ingest now supports
    `--normalized-artifact-out`
  - that sidecar is a producer-owned archive/source artifact aligned to the
    root `itir.normalized.artifact.v1` schema
  - it describes the archive batch without replacing the canonical SQLite
    archive

- DONE second bounded capture/archive adopter:
  - `tircorder-JOBBIE` now has
    `tircorder/normalized_source_sidecar.py`
  - that helper emits one producer-owned `source_artifact` sidecar aligned to
    the root `itir.normalized.artifact.v1` schema
  - it describes a captured source path without replacing canonical capture
    storage

- DONE first bounded retrieval/research posture adopter:
  - `notebooklm-py` now exposes `notebooklm research follow`
  - that command emits one bounded non-authoritative derived follow artifact
    over completed NotebookLM research output
  - it stays advisory and follow-oriented rather than claiming canonical truth

- DONE second bounded retrieval/follow adopter:
  - `openrecall` now emits one bounded non-authoritative derived search-follow
    artifact over search results plus a normalized `derived_product` wrapper
  - the retrieval posture stays advisory, carries explicit trigger/scope/stop
    semantics, and does not promote local search results into canonical truth

- DONE third bounded retrieval/follow adopter:
  - `pyThunderbird` now emits one bounded non-authoritative retrieval-follow
    artifact for `--mailid-like` searches plus a normalized `derived_product`
    wrapper
  - the retrieval posture stays advisory, carries explicit trigger/scope/stop
    semantics, and can optionally write the suite-normalized artifact to disk
    without promoting local search results into canonical truth

- DONE second bounded retrieval/capture-family adopter:
  - `openrecall` now has `openrecall/normalized_artifact.py`
  - that helper emits one producer-owned `source_artifact` sidecar aligned to
    the root `itir.normalized.artifact.v1` schema for captured screenshot
    artifacts
  - it preserves producer ownership and canonical capture storage while making
    the capture lineage/context surface reusable across the suite

- DONE state-core hardening follow-through:
  - `StatiBaker` now guarantees that the canonical compiled-state artifact ID
    is retained in `lineage.upstream_artifact_ids`
  - bundle exporters may also pin an explicit `context_envelope_ref` without
    introducing a second reducer or changing compiled-state authority class

- DONE provenance/context-envelope convergence slice:
  - `chat-export-structurer` now has `src/context_envelope.py`
  - archive exports now build `context_envelope_ref` through one producer-owned
    helper instead of hardcoded strings
  - this improves cross-family handoff compatibility without changing archive
    authority class or canonical storage

- DONE first bounded union/join seam:
  - root now has `normalized_artifact_join.py` plus
    `schemas/itir.normalized.artifact.join.v1.schema.json`
  - the join stays read-only and preserves artifact role, authority class,
    lineage, and unresolved-pressure signals while surfacing compatibility
    flags instead of collapsing producer semantics

- DONE join/state/retrieval refinement round:
  - root join/composition now emits clearer compatibility/incompatibility
    signals without collapsing producer roles
  - `StatiBaker` now treats `context_envelope_ref` as a stricter exported
    requirement while keeping the canonical compiled-state artifact first in
    lineage
  - `openrecall` now exposes a dedicated producer-owned retrieval/follow
    helper that reuses its existing normalized search-follow contract instead
    of inventing a parallel derived shape
  - `SensibLaw` authority-core and domain-adopter widening both correctly
    stayed no-op because no real low-churn gap justified churn

- DONE named incompatibility + next retrieval-family round:
  - root join/composition now emits `named_incompatibilities` records with
    explicit `code`, `severity`, `artifacts`, `reason`, and `disposition`
  - `reverse-engineered-chatgpt` now has a producer-owned bounded
    conversation-list follow helper plus a suite-normalized `derived_product`
    wrapper for opt-in catalog retrieval flows
  - root governance now covers that `reverse-engineered-chatgpt`
    retrieval/follow wrapper as another real producer family

- DONE archive-search family + join policy-summary round:
  - `chat-export-structurer` now has a producer-owned archive-search follow
    helper plus a suite-normalized `derived_product` wrapper over bounded FTS
    search results
  - archive-search products now also expose `search_bounds_status` plus a
    bounded `recommended_next_bound` so large local result sets can tell the
    suite whether the current bound is already reviewable or should be
    narrowed locally
  - root join/composition now also emits a small `policy_summary` above named
    incompatibility records so disposition counts are visible without
    introducing resolver behavior
  - root governance now covers the new `chat-export-structurer`
    archive-search retrieval/follow family
  - root governance now also asserts the archive bounded-search pressure
    signal so local result sets cannot silently lose the distinction between
    reviewable bounds and narrower-query-needed cases

- DONE TIRC chat-history family + join policy-guidance round:
  - `tircorder-JOBBIE` now has a producer-owned chat-history follow helper
    plus a suite-normalized `derived_product` wrapper over bounded
    conversation discovery results
  - root join/composition now also emits per-code `policy_guidance` strings
    above named incompatibility records and disposition counts
  - root governance now covers the new TIRC chat-history retrieval/follow
    family

- DONE join dominant-disposition + ownership-audit checkpoint:
  - root join/composition now also emits a small
    `dominant_disposition` summary above `policy_summary` so downstream
    consumers can read the most common current disposition without resolver
    behavior
  - `StatiBaker` correctly stayed no-op because no additional low-churn
    context-envelope or lineage invariant was justified
  - `SensibLaw` correctly stayed no-op because no new authority-core gap was
    found
  - `tircorder-JOBBIE` chat-history normalization is now treated as an
    ownership-alignment surface, not a priority deepening lane, because the
    underlying ChatGPT retrieval seam remains more naturally owned by
    `reverse-engineered-chatgpt`
  - retrieval/archive family expansion also correctly held because no further
    distinct producer-owned business-logic seam was found without duplication

- DONE join severity-rollup refinement:
  - root join/composition now also emits `severity_summary` and
    `highest_severity` above the existing named incompatibility policy
    surfaces
  - this keeps incompatibility handling read-only while making it easier to
    distinguish informational joins from warning-heavy or blocking-heavy joins
    without adding resolver behavior

- DONE bounded-search planning + state-pressure refinement:
  - root join/composition now also emits
    `compatibility.uncertainty_surface` so downstream planning can see:
    - dominant unresolved-pressure status
    - priority rank
    - whether bounded search is currently recommended
  - root governance now explicitly checks that bounded follow artifacts stay
    local-first, authority-limited, and bounded by trigger/scope/stop
  - `StatiBaker` drift now emits a read-only `context_dominance` signal so
    large-corpus compiled-state review can detect when one thread is
    swallowing the visible context surface without changing reducer behavior

- DONE GWB/Brexit bounded follow bridge:
  - `SensibLaw` GWB legal-follow operator view now emits a bounded
    `follow.control.v1` plane plus queue items over followed legal sources
    instead of stopping at graph inspection only
  - Brexit-relevant legal follows now route through explicit bounded targets
    such as `uk_legislation_follow` and `eur_lex_follow`
  - the queue is now ranked using `priority_score`, `priority_rank`, and
    likely `authority_yield` so Brexit/legal follow work can collapse
    uncertainty in a better order
  - GWB public and broader review payloads now also expose a read-only
    `workflow_summary` so bounded review consumers can see the next
    recommended operator view directly on the payload
  - this gives the GWB/Brexit proving ground its first AU-style control-plane
    bridge for bounded uncertainty-collapse work without introducing a second
    reducer or external-search default

- DONE Wikidata/Nat grounding priority surface:
  - `SensibLaw` Wikidata grounding-depth helpers now emit a ranked
    `grounding_depth_priority_surface`
  - incomplete packets expose:
    - missing grounding fields
    - priority score
    - bounded-follow recommendation
    - recommended target `revision_locked_evidence`
    - `grounding_gap_class`
    - `recommended_follow_scope`
  - this gives the Nat proving ground an explicit "what should we ground
    next?" surface rather than only aggregate grounding summaries
  - Nat cohort-D operator report and control-index surfaces now also expose a
    read-only `workflow_summary` so bounded packet consumers can see whether
    the next move is unresolved-reference cleanup, queued typing review, or
    simple record-state capture without reconstructing that from queue stats
  - a first bounded live-follow campaign is now pinned across several Nat
    uncertainty classes so the next live execution round can exercise:
    - hard grounding packets
    - split-heavy business-family rows
    - reconciled non-business variance
    - policy-risk live-preview rows
    - missing-instance typing deficit cases
    - unreconciled-instance split-axis cases
  - the campaign remains local-first, source-bounded, and capped at two hops
    from named packet sources
  - the campaign now also has a callable execution-plan surface via
    `sensiblaw wikidata nat-live-follow-campaign` so the next Nat run can emit
    one normalized per-target plan before any live fetch occurs

- DONE AU legal-follow operator bridge:
  - `SensibLaw` AU legal-follow operator view now emits a bounded
    `follow.control.v1` plane plus queue items over derived follow targets
  - cross-jurisdiction derived targets, including the UK/British legal follow
    target, now surface as actionable bounded follow items rather than
    graph-only metadata
  - AU authority-follow queueing is now also ranked using `priority_score`,
    `priority_rank`, and likely `authority_yield` so authority-resolution work
    can collapse uncertainty in a better order
  - shared AU fact-review bundles now also expose a read-only
    `workflow_summary` so bounded packet consumers can see the recommended
    next operator view without opening the full fact-review workbench
  - this extends AU’s proving-ground posture from authority-follow only into
    explicit legal-follow operator guidance under the uncertainty-collapse
    control read

- DONE widened operator/integration adoption:
  - `itir-svelte` normalized-artifacts route now consumes:
    - `SensibLaw` review/promotion artifacts
    - `StatiBaker` compiled-state artifacts
    - `chat-export-structurer` archive/source artifacts by explicit path
    - `tircorder-JOBBIE` capture/source artifacts by explicit path
    - `notebooklm-py` retrieval/research normalized artifacts by explicit path
    - `reverse-engineered-chatgpt` live-conversation/source artifacts by
      explicit path
  - the route keeps each producer family in its own role and does not
    reinterpret capture as archive, state, or review output

- CLARIFIED canonical live-context path:
  - ChatGPT live-context recovery and verification should route through the
    `robust-context-fetch` / `scripts/chat_context_resolver.py` DB-first
    contract
  - direct `reverse-engineered-chatgpt` pull repair remains an implementation
    concern beneath that contract, not an independent moonshot lane unless the
    resolver surface itself is missing required capabilities
  - this keeps the business-logic lane focused on canonical archive truth,
    resolver-based fallback, and normalized downstream artifacts rather than
    raw fetch plumbing in isolation

### Phase C: Reducer and Authority Hardening

Definition of done:

- no side system introduces a second canonical reducer
- promotion receipts are required at authority-crossing boundaries
- context-envelope and provenance-anchor requirements are testable
- derived layers cannot silently present as truth

### Phase D: Follow and Union Expansion

Definition of done:

- follow obligations carry explicit trigger, scope, and stop condition
- bounded cross-system follow works in at least two domains
- bounded union surfaces exist without silent semantic collapse
- mismatch, incompatibility, and abstention remain visible

### Phase E: Operator Completion

Definition of done:

- operators can inspect:
  - what this artifact is
  - why it exists
  - what supports it
  - what remains unresolved
- operator surfaces stay read-only or review-first
- anti-panopticon posture remains explicit in product behavior

## Worker Lanes

One nonblocking lane per worker:

- Huygens
  - lane: state reducer adoption
  - target: `StatiBaker`, `sb`
  - scope: make compiled-state outputs line up with the shared normalized
    contract without semantic drift

- Dirac
  - lane: bounded union / join semantics
  - target: root contracts/tests and producer-owned join helpers where needed
  - scope: compose multiple normalized artifacts without local metaphysics,
    role collapse, or authority drift

- Epicurus
  - lane: contract validation and governance tests
  - target: root schemas/tests plus adapter conformance tests
  - scope: schema validation, promotion/derived invariants, no-second-reducer
    guards, and bounded-follow checks

- Dalton
  - lane: provenance/context-envelope convergence
  - target: acquisition/archive producers such as `chat-export-structurer`,
    `tircorder-JOBBIE`, `reverse-engineered-chatgpt`, `openrecall`
  - scope: stabilize provenance/context-envelope/lineage semantics across
    producer handoffs without changing authority class or canonical storage

- Meitner
  - lane: retrieval/research adapter posture
  - target: `notebooklm-py`, `openrecall`, `reverse-engineered-chatgpt`,
    `pyThunderbird`
  - scope: keep retrieval/advisory adapters inside bounded follow and derived
    artifact posture rather than canonical truth posture

- Mill
  - lane: review/promotion adoption
  - target: `SensibLaw`, `SL-reasoner`
  - scope: align reviewable claim, promoted record, derived product, and
    follow-obligation surfaces to the shared suite contract, while keeping
    `SL-reasoner` explicitly low-priority and scaffold-level until the core
    engine is stable enough that a real split reduces complexity instead of
    adding it
  - current landed seam:
    - `SensibLaw` may export a producer-owned `reasoner_input_artifact`
      payload
    - `SL-reasoner` may validate and consume that payload read-only and emit
      derived reasoning artifacts only
    - no deterministic engine extraction is required yet

- Ohm
  - lane: bounded domain-adopter parity
  - target: existing AU/GWB/Wikidata/Nat and similar proving grounds
  - scope: keep older adopters moving only when the product-stack contract for
    their family is already real

## Sidecars

- docs worker
  - activate at state-change checkpoints
- UML worker
  - activate only if the suite metasystem shape changes materially
- commit worker
  - activate only at a publish boundary

## Promotion Order

1. Huygens
2. Dirac
3. Dalton
4. Meitner
5. Mill
6. Epicurus
7. Ohm

That order is intentional:

- the shared contract is already frozen
- state adoption comes first because it is central to the original
  smart-journal arc and belongs in `StatiBaker`, not in legal proving grounds
- operator consumption follows so the stack can read a real state adopter
- capture/archive and retrieval adapters then align to the same contract
- review/promotion adopters continue, but they no longer control suite
  priority just because they landed early
- within that family, `SensibLaw` remains the active engine and
  `SL-reasoner` remains cordoned until a real complexity threshold justifies
  extraction
- contract/governance hardening stays continuous, but it should now validate
  multiple adopter families rather than only one early adopter

## Immediate Next Slice

The next honest implementation slice is:

- widen operator/integration consumption to more producer families without
  local reinterpretation
- then keep hardening cross-family governance tests and producer-owned
  context-envelope posture before pushing more domain adopters
