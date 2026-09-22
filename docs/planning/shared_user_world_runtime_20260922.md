# Shared User/World Runtime — Cross-Suite Contract

Date: 2026-09-22
Status: canonical suite-level design contract

## SensibLaw repository identity

Within this suite contract, **SensibLaw** denotes one system. Its production
runtime is the Rust `slr` repository; the older `SensibLaw` repository
contains Python/prototype, product, user-story and historical surfaces. They
must not be modelled as independent consumer families or competing semantic
authorities.

Related: Smart Journal moonshot, Mary parity, federated world materialisation, OpenRecall observer integration, mission lens, SensibLaw legal proof search.

## Purpose

The suite is not a single legal-case engine.  Its top-level role is a compiler
stack for difficult reality:

```text
bounded world inputs
  -> provenance/context preserving canonicalisation
  -> reviewable observations/events/claims/hypotheses
  -> reviewed shared world
  -> consumer-specific dependency slice
  -> shared-world reuse before new acquisition
  -> residual-sensitive producer
  -> reviewed world delta
  -> recompute affected consumers
```

Legal reasoning is one major consumer.  Personal journal reconstruction,
chronology, mission/accounting, professional handoff, advocacy, research and
comparative views are sibling consumers over the same provenance-bearing world.

## Input lanes

Admissible source lanes include, without collapsing their authority classes:

- journal and personal notes;
- chat/archive material;
- audio/transcript capture;
- OpenRecall/browser/app observer traces;
- documents and other artifacts;
- public sources;
- primary legal materials;
- calendar/task/mission records;
- professional/support records;
- external evidence.

Observer/capture ingestion is never itself promotion.

## Shared-world coordinates

The shared world may contain reviewed or explicitly unresolved coordinates for:

- evidence/source manifestations;
- observations;
- events;
- claims;
- hypotheses;
- legal atoms;
- authorities;
- missions;
- commitments;
- absences;
- conflicts/contestation;
- residuals;
- provenance.

A common coordinate identity does not mean that two consumers share one
ontology or one conclusion.

## Consumer dependency slices

Every consumer must expose a dependency slice rather than reading the whole
world implicitly.

Examples:

```text
personal journal reconstruction
personal timeline
mission actual-vs-should
lawyer matter
doctor/support handoff
advocacy chronology
regulator/ombuds complaint
journalistic investigation
legal proof graph
historical/colonisation research
comparative projection
report/export
```

The consumer slice owns:

- the question/query reference;
- required coordinate references or coordinate classes;
- scope/privacy requirements;
- unresolved coordinates;
- projection profile.

## Canonical recurrence

```text
Consumer Q
    |
    v
dependency slice / residual
    |
    v
shared-world lookup
   / \
paid missing
 |      |
reuse  residual-sensitive producer
        |
        v
  bounded acquisition
        |
        v
 explicit review/payment
        |
        v
 reviewed Delta W
        |
        v
affected-consumer index
  /       |       \
 v        v        v
Q1       Q2       Q3
recompute recompute recompute
```

Already-reviewed coordinates are quotient/reused.  They do not create fresh
work merely because another consumer discovers them.

## Join semantics

A cross-consumer join is not established by:

- graph adjacency;
- citation co-occurrence;
- same QID;
- same keyword;
- ontology similarity.

Those are proposal/navigation signals only.

A join is admitted when a reviewed world coordinate is also in another
consumer's dependency slice and its scope permits reuse.

Thus:

```text
shared coordinate
!= merged consumer
!= merged issue graph
!= legal applicability
!= claim truth
```

## Privacy and scope

Scope is a semantic gate, not presentation metadata.

A private hypothesis may remain available to a personal journal consumer while
being unavailable to a lawyer, doctor, regulator or public export.

Selective handoff must preserve:

- included coordinates;
- explicit exclusions;
- uncertainty/abstention;
- source provenance;
- redaction/share-scope receipts.

No personal note or hypothesis is automatically upgraded to evidence merely
because a professional consumer exists.

## Legal specialization

SensibLaw legal consumers may reuse reviewed world coordinates as factual,
source, identity or authority prerequisites, but must separately establish:

- exact legal type;
- authority role;
- applicability;
- jurisdiction/time;
- elements/rules;
- exceptions;
- defeaters;
- burdens/remedies where relevant.

Legal proof search is adversarial and bidirectional:

```text
forward: facts + rules -> reachable routes
backward: target -> missing legal atoms / minimal cuts
adversarial: route -> defeaters / contradictions / comparators
counter-adversarial: defeater -> distinctions / exceptions / counter-defeaters
```

Route reachability is not a prediction of judicial outcome.

## Smart Journal and personal world

Personal/private users are first-class, not merely evidence suppliers to legal
matters.

The personal-world path is:

```text
journal / notes / chats / captures / schedule / documents
  -> provenance-preserving personal world
  -> fragmented chronology and coexisting accounts permitted
  -> review/promote selected coordinates only
  -> optional scoped handoff to lawyer/doctor/advocate/regulator/journalist
```

"unknown / not ready" may be terminal for a personal consumer.  The system
must not force narrative coherence.

## Mission / actual-vs-should

OpenRecall, chat, shell/git and other activity receipts may feed mission
consumers as observer-class evidence.

```text
observed activity != mission truth
reviewed mapping   != normative judgment
```

Mission consumers share the same world/dependency infrastructure and must not
create a second canonical store.

## Revision/replay role

Revision handling is supporting maintenance:

```text
source/revision change
  -> invalidate affected coordinate/receipt
  -> SAME affected-consumer index
  -> recompute/re-review
```

It is not the primary discovery recurrence.

## Roadmap capability families

### S19 — Shared User/World Runtime
- canonical shared-world coordinates;
- consumer dependency slices;
- shared-world lookup before acquisition;
- scope/privacy admission;
- reviewed join witness;
- affected-consumer index;
- quotient/reuse;
- personal -> professional handoff capstone;
- legal cross-matter reuse capstone.

### S20 — Adversarial Legal Proof Search
- legal atom graph;
- support/defeat/counter-defeat;
- WrongType;
- minimal-cut search;
- comparator/authority search;
- Pareto proof-gap scheduling;
- explicit supported/defeated/contested/unresolved/budget states.

### S21 — Real Legal Case Battery
- Pabai support -> defeat -> repair regression;
- Yindjibarndi/Yunupingu/Mabo shared-doctrine reuse;
- Munkara/Tipakalippa partial overlap without doctrinal collapse;
- Murujuga open-discovery/no-forced-join control;
- colonisation consumer spanning historical, statutory and modern legal state.

### S22 — Personal World / Smart Journal
- personal capture;
- chronology reconstruction;
- coexisting accounts;
- privacy/scope;
- selective promotion;
- no forced coherence.

### S23 — Role-Safe Handoff
- lawyer;
- doctor/psychologist;
- advocate/community service;
- regulator/ombuds;
- journalist/watchdog.

### S24 — Mission / Activity
- actual-vs-should;
- reviewed mappings;
- continuity/drift;
- no mission-truth promotion from observer traces.

### S25 — Workbench
One projection surface over Journal, Timeline, Matter, Claim, Proof, Mission,
Research, Handoff, Source and Comparative views.

### S26 — Comparative / Multi-world
Compare accounts, parties, jurisdictions, dates, route states and before/after
worlds without flattening differences.

### S27 — Reproducible Publication / Federation
Export bounded world slices with provenance, review state, residuals, proof
routes, exclusions and replay coordinates.

## Suite invariants

- context is mandatory;
- provenance is mandatory;
- interpretation remains explicit;
- promotion is receipt-bearing;
- privacy/scope is enforced before reuse;
- derived graphs and rankings remain derived;
- consumer joins do not collapse consumer semantics;
- revision maintenance uses the same dependency machinery as new knowledge;
- no hidden person-risk scoring or panopticon drift;
- no consumer may infer authority or truth merely from world availability.
