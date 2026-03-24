# JMD Object Graph x SL Corpus Graph Contract (2026-03-19)

## Purpose
Define a read-safe, future-expandable boundary between:

- `JMD` object graphs:
  content-addressed artefacts, shards, links, provenance, publication, and
  execution surfaces
- `SL` corpus graphs:
  lexical compression, span anchors, equivalence classes, divergence overlays,
  verification overlays, and optimisation hints

The contract must preserve:

- JMD authority over canonical stored objects and execution surfaces
- SL authority over organisation, compression, crosslinking, and reasoning
  overlays
- reversibility and provenance
- explicit distinction between advisory and authoritative outputs

## Non-goals
- not a shipped Casey <-> JMD executor contract
- not a commitment to immediate ERDFA/IPFS runtime integration
- not a claim that SL may rewrite JMD canonical object state directly
- not a canonical shard schema for JMD execution
- not a replacement for existing Casey/fuzzymodo/SB authority boundaries

## Source Context
- resolved via `robust-context-fetch`
- title: `Full Stack Architecture`
- online UUID: `69bb70ca-19ac-83a0-a087-8d2416e8be07`
- canonical thread ID: `fe1aead0a943806609b767cf3c27e2eeef2e54f1`
- source used: `db` after direct UUID pull into `~/chat_archive.sqlite`
- key takeaways informing this contract:
  - Rabbit functions as the process/queue I/O fabric for agents and tools
  - pastebin/IPFS behaves like the persistent shared memory/state layer
  - ERDFA is better treated as canonical structural/shard substrate than as an
    embedding layer
  - in the adjacent local workspace, `kant-zk-pastebin` is the concrete
    paste/raw retrieval surface and `erdfa-publish-rs` is the concrete
    ERDFA-side shard publisher closest to this planning model
  - Rust is treated as a programmable transformation/execution layer via custom
    rust-driver/plugin tooling
  - this strengthens the split between shared identity substrate and separate
    planning/governance/execution control planes
  - later turns in the same archived thread extend the bridge from pure
    architecture into a concrete provenance bundle and post-entropy metric
    story:
    - typed shards should carry declared input refs, witnesses, cost, and score
    - post-entropy is meant to measure corpus-compression efficiency plus
      divergence from the existing corpus, not just local compression in
      isolation
    - the ZK target becomes proving that a shard/spore was derived from a
      declared corpus by a declared pipeline with honest summary metrics

## ZKP Framing
Let the bridge be:

`Z^B = (O, R, C, S, L, P, G, F)`

### O — Organization
- `JMD` owns canonical artefacts, content addressing, publication, and
  execution fabric.
- `SL` owns corpus organisation, lexical compression, span anchoring,
  crosslinking, and organisation overlays.
- `Casey` owns governed local decision state where competing reorganisations may
  coexist.
- `StatiBaker` owns observer receipts and overlay memory.
- `SL-reasoner` exposes machine/agent query surfaces over SL outputs.

### R — Requirement
Given one or more JMD artefacts, SL must be able to:

1. ingest them into a reversible corpus model,
2. emit stable anchors and organisation overlays,
3. propose optimisation and crosslinking hints back to JMD,
4. do so without mutating JMD canonical state directly.

### C — Code
The bridge is implemented as:

- JMD export surface
- SL ingest and corpus builder
- overlay and hint emitter
- optional Casey review surface for governed acceptance

Current architectural reading sharpened by the archived thread:

- Rabbit is the likely ephemeral execution/coordination transport
- pastebin/IPFS is the likely persistent object/state substrate
- the bridge should therefore target canonical object exposure and advisory
  overlay return, not assume SL owns the runtime execution fabric

### DASHI role in the bridge
The bridge needs one more layer made explicit so the repo does not drift into
"ERDFA already is the bridge" language.

- `ERDFA` / `DASL` is the representation, addressing, and execution substrate:
  it names, stores, transports, and links candidate artefacts or traces.
- `DASHI` is the selection/compression/invariance layer:
  it defines quotienting, admissible predictor families, and MDL-style collapse
  over the candidate space exposed by ERDFA/DASL.
- `SL` is the canonical reversible overlay surface:
  it exposes anchors, groups, clusters, divergence overlays, and future proof
  surfaces over the DASHI-collapsed reading of the JMD evidence.

That gives the bridge composition as:

`ERDFA/DASL substrate -> DASHI quotient / MDL collapse -> SL reversible corpus overlays`

This matters because the bridge is not only "read a shard and expose text". It
is also the place where the suite should eventually prove that a selected
representation is the minimal canonical explanation over declared evidence.

### Conservative bridge lesson from the Dashifine/TextGraphs prototype
The local Dashifine/TextGraphs bridge sharpened one practical rule that also
applies here:

- a bridge should first be conservative before it tries to be rich
- conservative means:
  - one canonical shared state
  - one reversible serialization from that state
  - one derived graph or overlay surface that can be traced back to the source
    state without ambiguity
- only after that should the bridge add richer graph constructions
  (similarity/non-local edges, cluster overlays, recurrence links)
- those richer graph surfaces should be judged by whether they track useful
  semantic or provenance-relevant changes, not merely by making the graph more
  connected or visually interesting

Maintainer reading for this contract:

- `JMD` object state remains the authority surface
- `SL` token/span/group layers remain reversible derived structure
- graph/overlay views are measurement and organisation layers over that
  reversible state, not replacement authority
- future bridge scoring should therefore separate:
  - conservation/replay correctness
  - semantic usefulness of derived graph/overlay observables

### S — State
Two coupled but distinct states:

- `JMD state`: canonical object graph
- `SL state`: corpus graph over lexical spans, groups, equivalence clusters,
  and overlays
- `DASHI selection state`: the admissible hypothesis family and its current
  minimal representative over the declared evidence bundle

### L — Lattice
- JMD graph: object/link structure
- DASHI graph: quotient/equivalence classes over candidate representations
- SL graph: span/group/cluster/divergence structure
- bridge mappings preserve one-to-many and many-to-one correspondences
  explicitly

### P — Proposal
SL may propose:

- equivalence links
- divergence flags
- canonical cluster candidates
- shard-boundary optimisation hints
- DASHI-backed canonicalisation hints over provenance bundles
- verification and provenance overlays

SL may not directly publish, collapse, or rewrite JMD objects.

### G — Governance
- JMD objects remain source-of-truth for canonical stored content.
- SL outputs are advisory unless explicitly promoted.
- Casey may host competing SL-derived proposals before acceptance.
- StatiBaker records receipts and refs, not raw mutable corpus state.

### F — Gap Function
The bridge optimises for:

- organisation gain
- redundancy reduction
- provenance clarity
- divergence explainability
- shard-boundary quality
- corpus accessibility for agents

For the post-entropy lane specifically, the archived thread sharpens the score
surface into:

- corpus-relative compression efficiency
- divergence/novelty relative to the current corpus model
- completeness/coverage so compression alone does not reward noise
- replayability as a hard admissibility condition

For the DASHI layer specifically, this means:

- `mdl_gain` alone is insufficient
- the bridge must separate local compression, corpus-relative novelty,
  completeness/coverage, and proof admissibility
- the minimal representative should be described as a named quotient/collapse
  result over declared evidence, not as an opaque score

## Core Contract Principle
The bridge is not object replacement.

It is:

> JMD stores objects; SL organises views over objects.

So every SL object must either:

- reference JMD object(s), or
- be derivable from referenced JMD object(s)

## Object Model
### 1. JMD-side ingest unit
A JMD object exposed to SL should have at minimum:

```json
{
  "jmd_ref": {
    "object_id": "cid-or-stable-id",
    "object_type": "paste|doc|shard|artifact|thread|blob",
    "content_ref": "cid-or-url-or-local-ref",
    "parent_refs": ["..."],
    "link_refs": ["..."],
    "provenance": {
      "source": "pastebin|ipfs|archive|repo|chat",
      "author": "optional",
      "created_at": "optional",
      "captured_at": "optional"
    }
  },
  "content": {
    "mime_type": "text/plain",
    "text": "..."
  }
}
```

Required rules:

- `object_id` is stable in JMD space
- `content` is the exact payload or a dereferenceable ref
- provenance is preserved, even if sparse

If the object is a provenance bundle rather than a single text shard, the
bridge should treat:

- `binaries` as decoder/predictor family members,
- `source` and debug symbols as the declared hypothesis space,
- `traces` as observed signal,
- `models` as selected representatives,
- `events` as the causal filtration over that signal.

That is the intended DASHI reading of the JMD evidence bundle.

### 2. SL-side ingest unit
SL transforms that into a corpus object:

```json
{
  "sl_ref": {
    "corpus_object_id": "sl:obj:...",
    "source_object_ids": ["jmd-object-id"]
  },
  "normalization": {
    "profile": "sl.default.v1",
    "tokenization_version": "sl.token.v1",
    "reversible": true
  },
  "anchors": [
    {
      "anchor_id": "sl:anchor:...",
      "source_object_id": "jmd-object-id",
      "byte_start": 120,
      "byte_end": 240,
      "token_start": 18,
      "token_end": 41
    }
  ],
  "groups": [
    {
      "group_id": "sl:group:...",
      "kind": "lexeme|phrase|boilerplate|template|claim-fragment",
      "anchor_refs": ["sl:anchor:..."]
    }
  ]
}
```

Required rules:

- all SL anchors must trace back to JMD object refs
- normalization must be versioned
- reversibility must be explicit per profile

## Bridge Mappings
### JMD object -> SL corpus object
One JMD object may produce:

- one SL corpus object
- many anchors
- many groups
- zero or more cluster memberships

### Multiple JMD objects -> one SL cluster
SL may detect:

- duplicates
- near-duplicates
- lexical variants
- same claim re-expressed
- same code fragment repeated

These become advisory clusters, not canonical JMD merges.

### SL output -> JMD overlay
SL may emit overlays attached to JMD refs, such as:

- equivalence cluster membership
- divergence/contestation
- verification/provenance concern
- shard optimisation hint

## Output Classes From SL
### 1. Anchors
Stable reversible references into source content:

- token span
- byte span
- paragraph span
- segment boundary

These are foundational and low-risk.

### 2. Organisation overlays
Read-only semantic structure over JMD content:

- equivalence class
- boilerplate family
- repeated fragment set
- canonical cluster candidate

### 3. Divergence / verification overlays
Explain unresolved differences or provenance issues:

- same source event, conflicting lexical claims
- unverified repeated quote
- near-duplicate with altered wording
- provenance gap

### 4. Optimisation hints
Advisory suggestions for future JMD structuring:

- shard boundary should move here
- fragments compress better as a shared basis
- objects are strong reuse candidates
- a cluster should be materialized as a reusable unit

These are explicitly non-authoritative until accepted.

## Provenance Bundle Interpretation
The archived `Full Stack Architecture` thread adds a concrete maintainers'
reading for the bridge: some JMD-side artefacts should be treated as replayable
provenance bundles, not just standalone shards.

Normalized bundle shape:

```text
bundle = {
  binaries,
  source,
  debug_symbols,
  traces,
  models,
  prior_events
}
```

Mapped onto the bridge:

- `binaries`: execution artefact emitted or referenced from JMD space
- `source + debug_symbols`: explanatory and structural context for replay
- `traces`: runtime evidence
- `models`: compressed or derived representation
- `prior_events`: causal chain into the current artefact

Maintainer implication:

- the bridge should be able to ingest not only bare text objects but also
  replayable provenance bundles whose parts remain linked by source refs
- SL overlays should be able to reference bundle components independently
  without flattening them into one opaque blob
- Casey proposals may later compare alternative bundle interpretations or
  alternative organisation plans without mutating the canonical JMD bundle

## Public Statement / Metric Commitment Pattern
For post-entropy- and scoring-related shards, the thread now gives a clearer
public statement pattern:

```text
corpus_root
pipeline_id
params_hash
output_hash
metric_commitment
score_commitment
```

Maintainer reading:

- `corpus_root`: CID set root / Merkle root of the declared source corpus
- `pipeline_id`: named transform pipeline responsible for the output
- `params_hash`: commitment to parameterization without exposing everything
- `output_hash`: commitment to the output artefact/bundle
- `metric_commitment`: commitment to published summary metrics
- `score_commitment`: commitment to the derived score used for evaluation

This does not force a concrete proof system yet. It does mean the bridge should
reserve room for:

- declared corpus roots
- declared pipeline identifiers
- replay-verifiable metric claims
- score claims that are separable from raw execution cost

## Minimal Scoring Interpretation
The same thread provides a first practical scoring model for typed shards:

```text
cost_steps(S)
mdl_gain(S)
coverage_gain(S)
replay_ok(S)
novelty(S)
```

With maintainer-level interpretation:

- `cost_steps`: provable execution cost or bounded proxy
- `mdl_gain`: compression gain against a declared before/after representation
- `coverage_gain`: useful new coverage added to corpus/shard graph
- `replay_ok`: deterministic replay passes
- `novelty`: distance from existing corpus/shard set

Bridge implication:

- cost and value must remain distinct; raw execution cost is not the whole score
- novelty must eventually become corpus-relative rather than a local heuristic
- replayability is a hard guard, not just a ranking bonus
- any bridge implementation that emits optimisation hints should keep metrics
  separately named so maintainers can evolve them without confusing cost, value,
  and admissibility

## Authority Rules
### JMD authoritative
Authoritative in:

- canonical object storage
- object identity
- content publication
- execution/orchestration
- accepted shard graph
- queue/topic routing and process I/O fabric where Rabbit is the active
  transport layer

### SL authoritative
Authoritative in:

- tokenisation under a named profile
- span anchor derivation
- lexical group construction
- compression metrics under a named profile
- organisation overlays as SL outputs

### Advisory only
Advisory only:

- cluster-as-canonical suggestions
- shard boundary optimisation hints
- merge/reuse proposals
- verification judgments requiring governance review

## Casey Role In The Bridge
Casey is where proposals can remain live without premature collapse.

If SL emits multiple competing structures, for example:

- cluster A vs cluster B
- shard-boundary proposal 1 vs 2
- canonical fragment choice X vs Y

Casey may hold these as coexisting candidates until explicitly resolved.

That makes Casey the governed proposal surface between SL and JMD.

## StatiBaker Role In The Bridge
StatiBaker should store:

- refs to source JMD objects
- refs to SL overlays, cluster ids, and anchor ids
- receipts for accepted or rejected proposals
- digests of optimisation runs

StatiBaker should not store:

- mutable canonical JMD graph state
- full raw SL working corpus as truth
- hidden collapse decisions

## Minimal Wire Formats
Canonical fixture pack:

- `docs/planning/jmd_fixture_v1_20260320.md`
- `docs/planning/jmd_fixtures/jmd_sl_ingest_v1.example.json`
- `docs/planning/jmd_fixtures/sl_jmd_overlay_v1.example.json`

### JMD -> SL ingest payload

```json
{
  "bridge_version": "jmd.sl.ingest.v1",
  "objects": [
    {
      "object_id": "jmd:erdfa:shard:note-0001",
      "object_type": "shard",
      "content_type": "text/plain; charset=utf-8",
      "text": "Alice paid Bob on 2026-03-19. Receipt hash: abc123.",
      "content_ref": {
        "paste_ref": {
          "provider": "kant-zk-pastebin",
          "paste_id": "note-0001",
          "raw_url": "https://example.invalid/pastebin/raw/note-0001"
        },
        "cid_ref": {
          "provider": "ipfs",
          "cid": "bafkreigh2akiscaildcjexample000000000000000000000000000000"
        }
      },
      "erdfa": {
        "shard_id": "note-0001",
        "cid": "bafkreigh2akiscaildcjexample000000000000000000000000000000",
        "component_kind": "text",
        "parent_refs": [],
        "link_refs": ["jmd:erdfa:shard:receipt-0001"]
      },
      "provenance": {
        "source": "pastebin",
        "captured_at": "2026-03-20T00:00:00Z"
      },
      "reserved_commitments": {
        "corpus_root": null,
        "pipeline_id": null,
        "params_hash": null,
        "metric_commitment": null,
        "score_commitment": null
      }
    }
  ]
}
```

V1 payload decisions:

- first canonical example is one ERDFA-backed text shard
- both `paste_ref` and `cid_ref` are present in the canonical fixture
- pastebin/IPFS are the ingest surfaces; ERDFA is the structural shard model
- current concrete repo mapping:
  - `kant-zk-pastebin` for `paste_ref`
  - `erdfa-publish-rs` for ERDFA shard production/serialization
- `zos-server`/Rabbit/libp2p remain future infrastructure, not normative payload
  fields

### SL -> JMD overlay payload

```json
{
  "bridge_version": "sl.jmd.overlay.v1",
  "source_object_id": "jmd:erdfa:shard:note-0001",
  "anchors": [
    {
      "anchor_id": "sl:anchor:note-0001:payment-sentence",
      "source_object_id": "jmd:erdfa:shard:note-0001",
      "byte_start": 0,
      "byte_end": 33,
      "token_start": 0,
      "token_end": 6,
      "anchored_text": "Alice paid Bob on 2026-03-19."
    }
  ],
  "groups": [
    {
      "group_id": "sl:group:payment-event",
      "kind": "claim-fragment",
      "anchor_refs": ["sl:anchor:note-0001:payment-sentence"]
    }
  ],
  "overlays": [
    {
      "overlay_id": "sl:overlay:claim:payment-event",
      "overlay_kind": "organization_hint",
      "source_object_ids": ["jmd:erdfa:shard:note-0001"],
      "anchor_refs": ["sl:anchor:note-0001:payment-sentence"],
      "detail": {
        "group_id": "sl:group:payment-event",
        "reason": "payment sentence extracted as a reusable event fragment",
        "confidence": "advisory"
      }
    }
  ],
  "optimization_hints": [
    {
      "hint_id": "sl:hint:shared-fragment:payment-event",
      "hint_kind": "shared_fragment_candidate",
      "source_object_ids": ["jmd:erdfa:shard:note-0001"],
      "detail": {
        "group_id": "sl:group:payment-event"
      }
    }
  ]
}
```

Reversibility for v1 means:

- the JMD object carries exact source text inline
- `byte_start`/`byte_end` are the normative source trace
- token offsets are secondary metadata only
- the anchored slice must be recoverable exactly from source bytes alone

## Acceptance Checks
A good v1 bridge should satisfy:

1. reversibility:
   from SL anchor back to exact source bytes/tokens
2. provenance preservation:
   every SL overlay points to one or more JMD source refs
3. no authority theft:
   SL output cannot rewrite JMD canonical object state without an explicit
   accept path
4. profile isolation:
   different SL profiles may produce different overlays without corrupting
   source identity
5. stable IDs:
   named anchors/groups/clusters remain stable enough for downstream references
   under a fixed profile/version
6. advisory clarity:
   optimisation hints are marked advisory and separable from canonical
   structure
7. dual-ref clarity:
   the canonical JMD example includes both paste retrieval and CID integrity
   refs without ambiguity about object identity

## Implementation Phases
### Phase 1
Read-only ingest and anchor generation.

### Phase 2
Equivalence clusters and divergence overlays.

### Phase 3
Optimisation hints for shard/corpus organisation.

### Phase 4
Casey-mediated proposal review for accepted reorganisations.

### Phase 5
Agent-facing `SL-reasoner` API over JMD-backed corpus.

## Glossary
- `JMD object graph`: the canonical JMD-side graph of stored artefacts, links,
  and provenance
- `SL corpus graph`: the SL-side organisation layer over source text, spans,
  groups, clusters, and overlays
- `anchor`: a reversible, versioned reference into source bytes/tokens
- `overlay`: an advisory structure emitted over source refs without rewriting
  canonical source state
- `optimisation hint`: a non-authoritative suggestion about reuse, boundaries,
  or organisation
- `canonical object`: the source-of-truth stored artefact owned by JMD

## One-sentence summary
JMD provides canonical content objects; SL provides reversible corpus
organisation, overlays, and optimisation hints over those objects.
