# Archive-Derived Actor / Semantic Spine Notes (2026-03-08)

## Purpose
Capture the highest-signal architectural conclusions recovered from the local
chat archive so actor/role/semantic-spine decisions do not remain trapped in
thread history.

This note is descriptive and archival. It does not widen current code scope by
itself.

## Source Threads
- `Actor table design`
  - thread: `21f55daa80206517e38f8c0fa56ee9bb2db8a9a0`
  - archive signal: actor-table boundaries, identity modeling, early
    `event_role` framing
- `Actor Model Feedback`
  - thread: `691d79376cb653e7170ea6c200a0a1d0a34bec6b`
  - archive signal: deterministic semantic spine, unified entity model,
    `mention_resolution -> event_role -> relation_candidate ->
    semantic_relation`
- `Milestone Slice Feedback`
  - thread: `1802fc3d13a0ad01ad95cef07eeaae9c16c22bed`
  - archive signal: read-only/non-reasoning surfaces, “surface conflict without
    deciding,” semantic vs normative boundary
- `Taxonomising legal wrongs`
  - thread: `74f6d0e08de82556df95c6ab1edb51557fede4fa`
  - archive signal: broader ontology/taxonomy framing, strong `subject` /
    `object` traffic, streams + actor/relationship context
- `SENSIBLAW`
  - thread: `4d535d3f33f54b1040ab38ec67f8f550a0f69dce`
  - archive signal: broad SL/ITIR/TiRCorder planning context; useful but less
    canonical than the focused actor/semantic threads above

## Recovered Decisions

### 1. Actor identity must remain clean and small
Recovered from:
- `Actor table design`
- `Actor Model Feedback`

Stable direction:
- canonical identity should sit in a small shared spine
- mutable, interpretive, narrative, or multi-source details do not belong in
  the canonical actor row
- role labels and participation/context markers must not be treated as actor
  ontology kinds

Current repo alignment:
- the semantic layer already uses a unified shared `entity` spine plus subtype
  tables
- `event_role` is already the participation/context lane

Practical implication:
- transcript/freeform work should keep source-local actors small and clean
- future enrichment belongs in subtype/detail tables or later overlays, not in
  transcript-local role labels or inflated actor rows

### 2. Mention resolution is its own first-class layer
Recovered from:
- `Actor Model Feedback`

Stable direction:
- actor ontology and mention resolution are not the same thing
- text mentions may resolve, abstain, or stay candidate-like without mutating
  canonical identity
- deterministic receipts matter as much as the resolved result

Current repo alignment:
- `semantic_mention_clusters`
- `semantic_mention_resolutions`
- `semantic_mention_resolution_receipts`

Practical implication:
- transcript/freeform pressure-testing should continue to treat ambiguous
  speaker/entity cases as mention-resolution problems, not actor-table
  shortcuts

### 3. Event-role evidence and promoted relations must stay separate
Recovered from:
- `Actor Model Feedback`
- `Milestone Slice Feedback`

Stable direction:
- event-local participation/context structure belongs in `event_role`
- relation output should move through a conservative promotion pipeline:
  - `event_role`
  - `relation_candidate`
  - `semantic_relation`
- descriptive semantic surfacing is acceptable; normative decision or
  “which interpretation prevails” logic is out of scope for the core semantic
  layer

Current repo alignment:
- this is already the frozen semantic v1.1 shape

Practical implication:
- transcript/freeform expansion should prefer richer event-role coverage before
  any new relation promotion
- future semantic diffs or interpretive-position surfaces belong in review or
  overlay layers, not core extraction/promotion

### 4. Shared role/slot language is more stable than transcript-specific role labels
Recovered from:
- `Actor table design`
- `Actor Model Feedback`
- `Taxonomising legal wrongs`

Stable direction:
- the prior archive language is consistently around shared structural lanes
  such as:
  - `subject`
  - `object`
  - `requester`
  - `speaker`
  - `event_role`
- the archive does not provide a settled canonical transcript-specific role set
  like `addressee` / `recipient` / `companion` / `location_context`

Practical implication:
- transcript/freeform planning should align to the shared role/slot contracts
  already present in the repo
- any narrower non-legal role additions should be treated as reviewed,
  subordinate extensions, not as a new canonical taxonomy

### 5. Read-only / non-reasoning boundaries are part of the semantic posture
Recovered from:
- `Milestone Slice Feedback`

Stable direction:
- the system may surface structured disagreement, semantic contrast, and
  competing positions
- it should not collapse that into an authoritative verdict in the core layer

Practical implication:
- for transcript/freeform and legal lanes alike, the next useful move is richer
  descriptive structure, not a leap to interpretation or correctness judgments

## What Still Needs Mining
- `SENSIBLAW` is broad and high-volume; it likely contains additional
  architectural material but needs targeted extraction rather than another raw
  term scan.
- the untitled high-hit archive threads
  `dbcfb20d67213216c7aa02ed8493ae21fd39730d` and
  `dff2e608e358fe5ed5cf1d0376a36ff8a87a6f2d` should be inspected later because
  they mention `SensibLaw` heavily but were not interpretable from the bounded
  pass used here.

## Repo Follow-Through
- Keep transcript/freeform planning aligned with the shared actor/event-role
  architecture, not with ad hoc role inventions.
- Use this note as the archive-backed reference when future work touches:
  - actor identity boundaries
  - mention resolution
  - event-role expansion
  - relation promotion boundaries
- Use `docs/planning/actor_semantic_db_design_from_archive_20260308.md` for
  the narrower DB/table comparison against the current semantic schema.
