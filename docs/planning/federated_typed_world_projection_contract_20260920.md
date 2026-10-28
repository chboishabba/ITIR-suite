# Federated Typed World + Source-Addressable Projection Contract (2026-09-20)

## Purpose

Freeze the current ITIR/SensibLaw cross-suite architecture before further SLR
Sprint-3 implementation. This is an interface/ownership contract, not a new
runtime or replacement ontology.

The suite already contains the required ingredients. New work should compose
them rather than create parallel world/evidence models.

## Canonical separation of state authorities

The word "state" is overloaded. The suite intentionally keeps these authorities
orthogonal:

```text
WorldMonitor / SL / formal world
    epistemic / semantic world state
    observations, occurrences, reports, alternatives, derivations,
    evidence health, review/admission and residuals

StatiBaker
    temporal observer state
    event ordering, activity segmentation, carryover, observer history,
    receipts, gaps and deterministic replay

casey-git-clone
    live possibility/workspace state
    candidate lattices, explicit selection/collapse and immutable builds

SensibLaw / SLR
    semantic/legal admission and legal consumer projection
    reviewed evidence -> legal interpretation; not a replacement world store

itir-ribbon / Streamline
    projection-only visualisation
    timelines/ribbons/Sankey/flow views; never canonical truth
```

No component may infer authority merely because another component materialised,
observed, replicated, selected or displayed an object.

## Federated world coordinates

A useful world representation retains distinct object roles rather than one bag
of facts:

```text
observations
occurrences
assertions / reports
entity hypotheses
clusters
forecasts
alerts
rolling / baseline states
candidate alternatives
derived patterns / formal results
source-health state
review / admission state
residuals / gaps
```

Important non-collapse laws include:

```text
observation != occurrence
report != occurrence
multiple reports != independent genealogy
no visible observation != observed absence
stale evidence != false
cross-stream convergence != identity
anomaly != threat/legal authority
```

WorldMonitor-style freshness, genealogy, diversity, coverage-gap and baseline
coordinates are consumer-relevant state, not display metadata.

## Materialisation is orthogonal

Retain the existing federated materialisation distinction:

```text
semantic identity
materialised bytes
local availability
replica availability
candidate/workspace membership
observer receipt/history
semantic authority/payment
```

None factors automatically through another.

Examples:

```text
PDF local != claim admitted
CID available != Casey candidate selected
StatiBaker retrieval receipt != SensibLaw proposition paid
many mirrors != truth
formal checker success != external-world truth
```

## Source-addressable semantic node

Every meaningful derived/displayed value should preserve one semantic identity
plus enough linkage to answer:

```text
Where did this come from?
Why is it here?
What does it depend on?
What depends on it?
What was transformed?
What source revision/span/coordinate supports it?
What remains unresolved?
What changed between revisions?
```

The same node may be projected through Explain / Why / Source / Context / Graph
without being copied into separate truth objects.

Examples:

```text
n = 500
  -> reported-sample-size observation
  -> Methods paragraph/token span
  -> exact PDF revision

$9,850 B -> C
  -> transaction/flow observation
  -> bank row/API object
  -> exact source revision
  -> optional candidate flow-continuity derivation receipt

HCA paragraph [73]
  -> source-realised legal proposition
  -> exact authority revision/span

Wikidata P279 statement
  -> statement coordinate
  -> rank/qualifiers/references
  -> exact Wikidata revision
  -> optional typechecker/proof receipt

HR = 112 bpm
  -> sensor observation
  -> device/source timestamp
  -> exact health-source provenance
```

## Typed refinements, not giant universal records

Do not make every observation pretend to be a scientific study, transaction or
legal source. Canonical observations retain generic source/revision/anchor
identity; domain-specific coordinates attach only when meaningful.

For example, study-design coordinates such as population, sampling frame,
sample size, comparator, effect estimate, uncertainty interval, attrition and
external-validity domain are typed refinements over source-addressed study
observations.

Likewise transaction, testimonial, judicial, Wikidata, sensor and formal-proof
coordinates remain specialised fibres/roles over the shared provenance fabric.

## Flow / Sankey doctrine

Financial and conserved-allocation ribbons are projections, not the data model.

```text
source transaction observations
    -> candidate/reconciled flow relations
    -> reviewed semantic/legal interpretation where needed
    -> timeline / ribbon / Sankey projection
```

Distinguish:

```text
observed transfer
reconciled transfer
inferred continuity
candidate source-of-funds relation
unresolved destination
```

A candidate pattern such as rapid pass-through, layering or structuring does not
itself establish money laundering, intent, beneficial ownership or any legal
element.

Flow projections must expose evidence-health/coverage state so absence of an
edge is not mistaken for observed absence.

## Temporal/cross-stream composition

Streams such as finance, conversation/legal pressure, sensors/health, social
activity and user-defined measures may be aligned in time while preserving
their separate provenance.

Example:

```text
health stream change
legal correspondence
financial-flow disruption
    -> bounded temporal alignment candidate
```

The alignment is not by itself causation, diagnosis or legal finding.

StatiBaker may retain the temporal/observer history of such events but does not
inherit semantic authority over the underlying source domains.

## Alternatives and collapse

Casey is the implementation precedent for coexistence-first candidate state:

```text
candidate lattice
  -> explicit selection
  -> deliberate collapse
  -> immutable chosen projection
```

World/legal alternatives should adopt the discipline without transferring
Casey's workspace authority. Competing interpretations remain explicit until
consumer-relevant evidence/review legitimately refines or collapses them.

Aristotle/DASHI proof-search/discriminator machinery may select the next
observation needed to separate consumer-relevant alternatives.

## Formal/reference and runtime roles

Current intended direction:

```text
dashi_agda
    exploratory/golden/reference corpus

dashi_lean4
    progressively consolidated/sorted formal world/reference implementation
    plus executable checker/prover/worker programs and generated artifacts

SLR
    production SensibLaw runtime
    acquisition, persistence, review/payment, residual scheduling,
    legal admission/projection

StatiBaker
    temporal observer compiler / replay memory

casey-git-clone
    candidate/workspace/collapse/build authority

itir-ribbon
    projection-only visual surface
```

Lean execution, typechecking, theorem proving and artifact generation must remain
distinct receipt classes. A generated file is not a proof; a formal proof over
declared premises is not automatically an external-world fact.

## Sprint consequence for SLR

SLR Sprint 3 should not invent another world/evidence ontology. It should
compose the existing formal legal machinery into production:

```text
M3.A reviewed world -> WrongType issue state
M3.B source-realised legal evaluator parity
M3.C adaptive persisted Australian legal capstone
```

Existing Mabo, Pabai, Cullen/NSW CLA and GLJ lanes are the preferred calibration
suite.

Digital-ESD is a large-corpus/application regression workload. New PDF/document
requirements belong to generic ingestion unless a concrete fixture demonstrates
a missing capability.

## Product invariant

A timeline, proof tree, Sankey/ribbon, citation graph and source pane are
different projections over linked semantic/provenance objects, not separate
truth stores.

The universal operator interaction should converge on:

```text
hover       -> bounded local source preview
open        -> exact source/revision/anchor
why         -> dependency/evidence path
cites       -> outgoing citation/source edges
cited where -> incoming citation/source edges
used where  -> downstream consumers
missing     -> residuals
changed     -> revision/supersession lineage
```

## Boundary law

```text
world representability != local materialisation
observation != interpretation
interpretation != admission
formal verification != external-world authority
temporal observation != semantic ownership
possibility selection != truth
visual projection != canonical state
missing evidence != negative evidence
```
