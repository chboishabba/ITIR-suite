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
  - Rust is treated as a programmable transformation/execution layer via custom
    rust-driver/plugin tooling
  - this strengthens the split between shared identity substrate and separate
    planning/governance/execution control planes

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

### S — State
Two coupled but distinct states:

- `JMD state`: canonical object graph
- `SL state`: corpus graph over lexical spans, groups, equivalence clusters,
  and overlays

### L — Lattice
- JMD graph: object/link structure
- SL graph: span/group/cluster/divergence structure
- bridge mappings preserve one-to-many and many-to-one correspondences
  explicitly

### P — Proposal
SL may propose:

- equivalence links
- divergence flags
- canonical cluster candidates
- shard-boundary optimisation hints
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
### JMD -> SL ingest payload

```json
{
  "bridge_version": "jmd.sl.ingest.v1",
  "objects": [
    {
      "object_id": "cid:abc",
      "object_type": "paste",
      "content_type": "text/plain",
      "text": "raw content here",
      "link_refs": ["cid:def"],
      "provenance": {
        "source": "pastebin",
        "captured_at": "2026-03-19T10:00:00Z"
      }
    }
  ]
}
```

### SL -> JMD overlay payload

```json
{
  "bridge_version": "sl.jmd.overlay.v1",
  "source_object_id": "cid:abc",
  "anchors": [
    {
      "anchor_id": "sl:anchor:1",
      "byte_start": 0,
      "byte_end": 42,
      "token_start": 0,
      "token_end": 9
    }
  ],
  "overlays": [
    {
      "overlay_id": "sl:overlay:eq:7",
      "overlay_kind": "equivalence_cluster",
      "detail": {
        "cluster_id": "sl:cluster:7",
        "confidence": "advisory"
      }
    },
    {
      "overlay_id": "sl:overlay:div:4",
      "overlay_kind": "divergence_summary",
      "detail": {
        "reason": "lexical conflict across near-duplicate objects"
      }
    }
  ],
  "optimization_hints": [
    {
      "hint_id": "sl:hint:1",
      "hint_kind": "shared_fragment_candidate",
      "detail": {
        "group_id": "sl:group:19"
      }
    }
  ]
}
```

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
