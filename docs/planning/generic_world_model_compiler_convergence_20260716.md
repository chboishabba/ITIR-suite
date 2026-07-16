# Generic World-Model Compiler Convergence

Date: 2026-07-16

## Decision

The programme is one generic compiler/reviewer with several proving tranches;
it is not a Wikidata product plus separate GWB, AU, Brexit, Affidavit, Nat, or
assist products.  A tranche supplies source adapters, fixture material,
profile constraints, and compatibility wrappers.  It does not own a parallel
semantic method.

```text
bounded source/evidence
-> generic source adapters
-> canonical document/span/PNF units
-> candidate world model
-> typed joins
-> bounded inherited-type closure
-> comparison cohorts
-> domain structural signatures
-> internal + external pressure
-> review / promote / abstain
-> projections + receipts
-> optional checked export
```

The product boundary remains:

```python
world = build_world_model(data)
review = project_review_surface(world)
case = project_linkage_case(world)
receipt = attach_receipt(case)
```

Named lane functions may remain as thin compatibility wrappers, but callers
must not need lane identity to use this boundary.

## Target carrier

`WorldModelCase` will converge on receipt-free candidate state containing:

```text
source artifacts; anchors and spans; PNF units
entity/event/claim/relation candidates; candidate clusters
join hypotheses and decisions

type closure; comparison cohorts; domain structural signatures; view projections
external bridge candidates; pressure results; residuals and conflicts
review decisions; promotion state; export receipts at the boundary
```

The generic core owns the carriers, comparison/closure/pressure operations,
projections, audits, and receipt grammar.  GWB, AU, Brexit, Affidavit, Nat,
and assist work only prefill source anchors, workflow metadata, profile
defaults, and outward compatibility labels.

## Current baseline

Implemented now:

- revision-pinned supplied Wikibase entity-export validation;
- generic external graph views, bridge candidates/decisions, direct `P31` and
  supplied one-hop `P279` diagnostic pressure;
- candidate-only incomplete coverage and fail-closed completeness validation;
- generic world-model, review, linkage-case, and receipt projections;
- a real `Q1785637@2443793937` Apoteket observation with bounded
  organisation-compatible pressure via `Q4830453 -> Q43229`;
- remote manifest planning and an explicit four-section 57.9 MiB Zelph slice.
- DASHI formal boundary modules (currently uncommitted in `dashi_agda`) for
  partial finite spectral pressure and external-context safety. They prove
  candidate-only identity, coverage abstention, no pressure consequence without
  explicit policy authority, and no automatic truth/repair/edit authority.

This proves external evidence can travel safely through the generic carrier.
It does **not** yet provide a pharmacy-chain signature, query-shaped QID
retrieval, general closure, automatic cohorts, or a general WD type checker.

The historical synthetic/incomplete `Q1785637` missing-`P31` fixture remains a
regression test for abstention.  It is distinct from the current live pinned
observation, which positively observes `P31`.

## Sequenced delivery

### 1. Stabilise the real WD slice

Isolate the existing Apoteket work in a narrow commit or dedicated worktree;
do not commit, stash, or rewrite unrelated user work.  Record exact fixture
revisions, commands, focused test counts, and lint/format results.  Reconcile
only directly stale docs: entity-export status, the synthetic/live Q1785637
distinction, and obsolete chunk-0 examples.

### 2. Prove generic replay symmetry

Add one shared `apply_external_graph_context(...)`-style operation.  It owns
external observation validation, bridge creation, pressure execution,
review-state propagation, generic projections, and rebuildability receipt. It
does not retrieve sources, infer domain-local roles, assign authority, mutate
local state, or decide promotion policy.

Replay the same observation through GWB, AU, Brexit, and Affidavit fixtures.
Wrappers contribute only a local candidate reference, source anchors,
workflow/tranche metadata, and outward receipt context.  A normalized parity
test must agree after removing only local IDs, anchors, workflow labels, and
wrapper receipt metadata.  Every wrapper remains valid without WD input.

### 3. Productise supplied observations and bounded closure

Adopt provider-neutral request/observation contracts:

```text
WikibaseEntityObservationRequest
  requested_qid; requested_revision; source_payload_ref
  inspected_properties; coverage_policy; retrieval_receipt_ref

WikibaseEntityObservation
  qid; revision; labels; aliases; property observations; statement refs
  entity-valued refs; inspected/excluded properties; coverage boundary; source receipt
```

The semantic adapter validates caller-supplied evidence and never silently
refetches.  Local exports, captured API responses, checked fixtures, routed
Zelph graph views, and other Wikibase exports must normalize to this contract.

Then add `TypeClosureRequest` (seed entities, property families, bounded depth,
node/edge limits, revision policy, stop conditions, profile) and
`ObservedTypeClosure` (visited revision-pinned entities, `P31`/`P279` edges,
paths, frontier, blocked fetches, unresolved requirements, and rebuilding
inputs).  Results use only:

```text
compatible_within_observed_closure
contradictory_within_observed_closure
closure_incomplete
profile_not_applicable
invalid_observation
```

A path missing beyond the frontier is `closure_incomplete`, never a global
negative claim.  `NO_TYPED_MEET` remains inspection-relative.

### 4. Evaluate domain structural pressure, then refine it with cohorts

Domain-specific pressure (DSP) is the difference between a candidate's
observed structure and the domain-conditioned admissible region. A cohort is
one evidence source for that region, not the definition of DSP.

```text
documented domain model + migration/review policy + subject typing
+ statement value/qualifiers/references/time/scope
+ comparable observed statements where available
-> expected statement shape -> residual pressure
```

Nat is therefore already the first operational DSP tranche. Its climate/GHG
domain model evaluates a `P5991` statement against the intended `P14143`
statement shape and maps the residual to the A--E migration disposition:

```text
model-aligned predicate-only mismatch -> checked-safe migration candidate
multi-year or multi-scope collapse -> split pressure
required model detail absent -> repair-and-migrate pressure
product/non-organisation subject mismatch -> review-only typed hold
```

The receipt must keep `target_model_pressure`, `subject_type_pressure`,
`qualifier/reference_pressure`, `temporal_split_pressure`, and
`peer_cohort_pressure` separate. Peer frequency never overrides the documented
target model or reviewer policy.

The existing five-item `P5991 -> P14143` climate pilot is a policy-anchored
migration pack, not a generic organisation cohort: Handelsbanken, Swedish
Inspectorate of Auditors, Swedish Agency for Government Employers, Akademiska
Hus, and Atrium Ljungberg were selected to test statement-model alignment,
qualifier/reference preservation, temporal and multi-value ambiguity, and
split necessity. Apoteket is a separate external identity/type-bridge proving
item; it may later participate in a broader organisation cohort but does not
define one.

After closure, induce rather than hand-define expected shape:

```text
observed comparable members + P31/P279 relationships + coverage evidence
-> ComparisonCohort -> DomainStructuralSignature -> pressure
```

`ComparisonCohort` records focal/inherited classes, members, inclusion and
exclusion evidence, stratification keys, coverage, and revision set.
Stratification includes jurisdiction, period, administrative level,
organisation form, combined-versus-split modelling, completeness, and revision
epoch.

`DomainStructuralSignature` records field/relation/qualifier/cardinality and
temporal expectations, positive/negative/conditional features, exceptions,
evidence counts, and support distributions.  A field state distinguishes
`observed_present`, `observed_absent`, `not_inspected`, `not_supplied`,
`inapplicable`, `exceptional`, and `contradictory`.  Only genuinely inspected
absence may create missing-field pressure; unsupplied data abstains.

Pressure is reciprocal: member residuals can revise a signature; persistent
subgroups can propose a cohort split, narrower class, or exception cluster.
The first generic cohort-derived DSP proving pack should use city/capital
structure (Brisbane, Melbourne, Sydney, and New York City only as a broader
control), because it exercises inheritance, overlapping cohorts, jurisdiction,
and settlement-versus-jurisdiction modelling without treating the climate pilot
as a generic ontology sample. Pharmacy chain remains one possible later
cohort/member outcome, not a hand-authored semantic definition.

### 5. Keep pressure, policy, and formal interpretation separate

Runtime produces evidence-rich `ComparableResidualReceipt` and
`DomainPressureResult`: focal candidate, cohort, inherited path, observed and
expected shapes, anomalies, coverage limits, severity, and
`authority = diagnostic_only`.  Pressure does not itself decide validity or
promotion.

The DASHI boundary formalizes only admitted residual interpretation. The new
`DASHI.Interop.WikidataSpectralPressureBridge` and
`DASHI.Interop.ExternalContextSafetyBoundary` are formal safety interfaces, not
runtime graph algorithms:

```text
exact -> 0
partial -> 1
no_typed_meet -> 3
join -> maximum admitted spectral value
```

`scope_exceeded` and `unresolved` remain typed spectral abstentions, not high
eigenvalues.  A future runtime `SpectralPressureProjection` and join receipt
must be reconstructable against that law and prove no role, truth, authority,
edit permission, automatic repair, or promotion effect follows. Incomplete,
uninspected, and invalid observations abstain. Promotion consequences require
an explicit `PressureConsequencePolicy` with authority, evidence, workflow,
and allowed-consequence fields.

### 6. Extend governed ontology diagnostics

Nat continues as the operational change-review proving tranche.  Its existing
`ChangeReviewPacket` harness and A--E action taxonomy inform reviewed change
work; they do not bypass the generic carrier or grant blind automation.

Peter/Ege work extends the same machinery with revision-pinned
`P2738`/`P11260` disjointness extraction, subclass/instance contradiction
diagnostics, coverage-aware abstention, and `CulpritCandidate` explanations
(incorrect `P31`/`P279`, over-broad superclass, disjointness issue,
class/item conflation, modelling split, drift, or qualifier omission).  Repair
remains review-only.

Rosario work is the reproducibility/evaluation tranche: pinned pathology packs,
question definitions, scoring for edge recovery, contradiction detection,
culprit ranking, abstention correctness, coverage honesty, and deterministic
replay.  It reports exact/partial/non-comparable parity honestly rather than
claiming method reproduction.

### 7. Add multi-view pressure and scalable transport

The same candidate may accumulate `ViewProjection`s from WD, Wikipedia, Simple
Wikipedia, Abstract Wikipedia, translation, local PNF, and domain corpora.
Views retain their source/version, feature and role/predicate shapes, omitted
or added structure, authority class, and rebuildability receipt.  Cross-view
comparisons produce diagnostic residuals only.

Zelph later replaces observation transport, not semantics:

```text
QID -> route indexes -> exact node/name/adjacency chunks
-> BoundedZelphGraphView -> unchanged observation/closure/DSP pipeline
```

Until routes exist, the planner exposes physical shard cost before fetching.
Every selected object remains revision/receipt addressable.

### 8. Converge the compiler and operator surface

Maintain a machine-readable ownership audit for bridge attachment, identity
review, closure, cohorts, DSP, contradiction, review/promotion state,
projections, and receipts.  It records canonical owner, legacy duplicates,
adopters, migration state, removal condition, and tests.

The operator surface must show candidate, source/revision evidence, proposed
joins, observed type paths, cohort/signature basis, pressure features, missing
coverage, alternatives, policy consequences, and rebuildability.  Exports carry
all source, graph, profile, cohort, policy, performed/omitted-check, and
disposition receipts.

## Formal/runtime boundary

DASHI regression-checks candidate-only external semantics, no role/authority
inheritance, inspection-relative `NO_TYPED_MEET`, conservative finite pressure
joins, and review-before-commit boundaries.  It does not claim live revision
validation, `P31`/`P279` traversal, cohort induction, `P2738` diagnosis, Zelph
routing performance, or an `O(k)` WD lookup theorem.  Those are runtime
algorithms and benchmark obligations.

## Completion criteria

The programme is complete when all supported sources can emit common candidate
carriers; external structure attaches without creating local role/authority or
truth; closure and DSP are revision/coverage explicit; pressure has no effect
without policy; all proving tranches share carriers, review states, and
receipts; Zelph supplies interchangeable bounded observations; and every
outcome is deterministic, reconstructable, receipt-backed, and free of a
lane-owned parallel semantic universe.
