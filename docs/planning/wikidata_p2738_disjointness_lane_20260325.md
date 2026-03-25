# Wikidata `P2738` Disjointness Lane (2026-03-25)

## Purpose
Design the smallest bounded implementation slice that creates real parity
pressure against Ege Doğan / Peter Patel-Schneider's disjointness-violation
work without derailing the existing hotspot lane.

This is a design note only. No implementation is implied by this document.

## ZKP Frame

O:
- Decision-maker: repo maintainer.
- Execution surface: SensibLaw Wikidata diagnostics and planning lane.
- Comparison audience: Wikidata Ontology Working Group, especially Ege/Peter.
- Downstream audience: future implementation agents and Zelph-facing reviewers.

R:
- The repo needs one bounded disjointness lane that is concrete enough to claim
  substantive parity work has started.
- The lane must stay deterministic, review-oriented, and compatible with the
  existing hotspot/report contracts.

C:
- likely future code surface:
  - `SensibLaw/src/ontology/wikidata_disjointness.py`
  - `sensiblaw wikidata disjointness-report`
- likely fixture surface:
  - `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_*`
- primary planning/status surfaces:
  - `SensibLaw/docs/wikidata_working_group_status.md`
  - `docs/planning/wikidata_parity_gap_note_rosario_ege_20260325.md`
  - this note

S:
- current repo state:
  - strong `P31` / `P279` structural diagnostics
  - qualifier drift
  - parthood
  - hotspot benchmark lane
  - no dedicated disjointness extractor or culprit miner
- current comparison state:
  - low parity with Ege/Peter on their paper's specific method
  - strong complementarity because the repo already has downstream reviewed
    export surfaces

L:
- adjacency
- bounded disjointness fixture
- deterministic disjointness report
- culprit mining
- working-group review usefulness
- later integration into hotspot selection if warranted

P:
- Proposal A:
  build only a bounded disjointness reporting lane over one pinned fixture pack.
- Proposal B:
  do not merge disjointness into the current hotspot lane first; keep it as a
  sibling diagnostic lane.
- Proposal C:
  only after the standalone lane is useful should disjointness become a hotspot
  family candidate.

G:
- no live-query-only implementation
- fixture-backed or dump-backed reproducibility first
- no auto-fix generation
- no silent mixing of disjointness counts with current mixed-order/SCC reports
- acceptance requires deterministic tests plus a reviewer-readable report

F:
- missing extractor for `P2738` + `P11260`
- missing fixture pack
- missing violation/candidate/culprit report contract
- missing tests

Synthesis:
- The next parity move is clear: a bounded standalone disjointness lane.
- It should be narrow enough to implement quickly and strong enough to discuss
  with Ege/Peter without overstating current coverage.

Adequacy:
- Adequate for execution planning.

Next action:
- define the first fixture/report contract and keep the slice small.

## Design stance
Do not start with "all disjointness in Wikidata."

Start with one bounded fixture-backed lane that proves the report shape and the
culprit logic.

## Minimal bounded scope

### Inputs
One pinned pack containing:

- one or more classes carrying `disjoint union of` (`P2738`)
- the `list item` (`P11260`) qualifiers that define pairwise disjoint classes
- enough subclass and instance assertions to produce:
  - at least one subclass violation
  - at least one instance violation
  - at least one culprit class

### First deterministic outputs
The first report should include:

- `schema_version`
- `disjoint_pairs[]`
- `subclass_violation_count`
- `instance_violation_count`
- `subclass_violations[]`
- `instance_violations[]`
- `culprit_classes[]`
- `culprit_items[]`
- `review_summary`

## Required logic

### 1. Pair extraction
Extract pairwise disjoint class pairs from:

- `P2738` statements
- non-deprecated rank only
- `P11260` qualifiers

This is the first parity-critical step, because it matches the paper's core
input surface.

### 2. Subclass violations
For each pair `(class1, class2)`, report classes such that:

- `class ⊆ class1`
- `class ⊆ class2`

Bound the first version to the local fixture graph only. Do not attempt full
Wikidata closure in `v0`.

### 3. Instance violations
For each pair `(class1, class2)`, report items such that:

- `item ∈ class1`
- `item ∈ class2`

Again, bound this to the local fixture graph.

### 4. Culprits
Define culprit classes as subclass-violation classes that are minimal with
respect to the local subclass graph:

- the class is itself a violation
- none of its violating parents inside the bounded fixture are more primary for
  the same downstream set

For `v0`, keep culprit logic simple and explicit. It does not need to reproduce
the paper's full operational heuristics to be useful.

## Suggested fixture shape
Use a repo-local JSON pack similar in spirit to existing Wikidata slices, but
keep it focused on disjointness semantics.

Suggested contents:

- class statements:
  - `P2738`
  - `P11260`
  - `P279`
  - `P31`
- local label map
- explicit expected report JSON

Suggested directory:

- `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_pilot_pack_v1/`

Files:

- `slice.json`
- `projection.json` or `report.json`
- optional source note

## CLI/API shape
First CLI should be:

- `sensiblaw wikidata disjointness-report --input ...`

Avoid adding build/import/search variants at first.

The point is to freeze:

- report shape
- parity semantics
- testability

## Relationship to the hotspot lane
Do not make `disjointness` a hotspot family immediately.

First prove:

- pair extraction
- violation counting
- culprit surfacing

Only then decide whether disjointness should later become:

- a new hotspot family, or
- a separate diagnostic lane that can feed hotspot selection indirectly

## Why this is the right next move
This slice would let the repo say, honestly:

- we now have a bounded deterministic `P2738` disjointness lane
- we can surface subclass/instance violations and culprits
- we are no longer only adjacent to Ege/Peter's method

That is the minimum threshold for substantive parity discussion.
