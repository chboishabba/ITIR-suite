# Shared Shard Artifact Contract `v1` (2026-03-27)

## Goal

Freeze one transport-neutral artifact contract that can support:

- Zelph as a read/query consumer
- ZOS as a publish/pull orchestrator
- Hugging Face as a practical hosted-query sink
- IPFS as an immutable content-addressed publication sink

This contract is intended to answer:

- what a shard "is"
- how selectors resolve to shards
- how sinks are attached without changing shard meaning
- what consumers and publishers are required to do

It is not intended to answer:

- the final physical shard-generation algorithm
- which repo owns the runtime implementation
- whether JSON or CBOR is the only valid manifest encoding

## Core decision

The contract must be:

- logical first
- transport-neutral
- sink-pluggable
- serialization-neutral

That means:

- shard identity may not depend on HF path names
- shard identity may not depend on IPFS CIDs alone
- the same logical artifact may be projected to:
  - JSON for Zelph/HF-style consumption
  - CBOR for Kant/IPFS-style publication

## Contract identity

- `contractVersion`: `shared-shard-artifact/v1`
- canonical semantic model:
  - one logical artifact
  - one set of logical shard ids
  - one selector/routing model
  - zero or more sink-specific object refs

## Contract fields

### 1. Artifact identity

Required:

- `contractVersion`
- `artifactId`
- `artifactRevision`
- `artifactClass`
- `createdAtUtc`
- `buildProvenance`

Recommended semantics:

- `artifactId`
  - stable logical name across sink projections
- `artifactRevision`
  - immutable content revision for this emitted build
- `artifactClass`
  - examples:
    - `zelph-graph`
    - `erdfa-shard-set`
    - `chat-freeze`
    - `formal-evidence`
- `buildProvenance`
  - source inputs
  - builder identity
  - builder version
  - optional parent artifact refs

### 1A. Optional semantic/proof provenance attachments

A logical artifact may carry the following optional provenance joins:

- `da51Address`
- `formalDemandRef`
- `formalEvidenceRef`
- `statementDigest`

These are **attachments**, not artifact or shard identity fields.

Required semantics:

- `da51Address` is a cross-system semantic/reference join and never proof authority;
- `formalDemandRef` names an external formalisation/proof demand owned by its producer (for example SLR);
- `formalEvidenceRef` names an independently produced evidence receipt;
- `statementDigest` commits to the concrete formal statement associated with that demand/evidence;
- none of these fields may change `artifactId`, `shardId`, selector meaning, or sink choice merely by being present;
- if formal evidence changes the statement digest, the caller must supply an explicit transport/equivalence receipt or create a new demand. Symbol/DA51 reuse is not sufficient.

The companion contract is:

`docs/planning/da51_slr_formal_evidence_artifact_contract_v1_20261017.md`.

### 2. Logical shard catalog

Required:

- `shards[]`

Each shard entry must define:

- `shardId`
- `section`
- `logicalKind`
- `encoding`
- `sizeBytes`
- `contentDigest`
- `routingKeys`
- `objectRefs[]`

Required semantics:

- `shardId`
  - stable logical identifier
  - must not be derived from sink path alone
- `section`
  - examples:
    - `left`
    - `right`
    - `nameOfNode`
    - `nodeOfName`
    - `summary`
    - `turn`
- `logicalKind`
  - examples:
    - `adjacency-bucket`
    - `name-bucket`
    - `content-shard`
    - `manifest-sidecar`
    - `formal-evidence`
- `encoding`
  - examples:
    - `capnp-packed`
    - `cbor`
    - `json`
- `contentDigest`
  - immutable content identity for cache and cross-sink equivalence
- `routingKeys`
  - logical selectors this shard can satisfy
- `objectRefs[]`
  - sink-specific locations for the same shard payload

### 3. Sink abstraction

Each `objectRef` must contain:

- `sink`
- `uri`
- `sizeBytes`
- `contentDigest`
- optional `transportHints`

Allowed initial sink values:

- `hf`
- `ipfs`
- `file`

Initial URI shapes:

- `hf://datasets/...`
- `ipfs://<cid>`
- absolute local path for local-only rehearsal if needed

Important rule:

- sink refs are attachments to the logical shard
- they do not define shard identity
- a CID/URI does not inherit theorem/legal/security authority from a linked formal or runtime evidence object

## Manifest serialization

The semantic contract is one thing. Serialization may vary.

Allowed initial manifest projections:

- JSON manifest
  - best current fit for Zelph/HF
- CBOR manifest
  - best current fit for Kant/IPFS

Required rule:

- JSON and CBOR projections of the same artifact must preserve the same:
  - `artifactId`
  - `artifactRevision`
  - `shardId`
  - `contentDigest`
  - selector/routing meaning
  - optional DA51/formal-evidence provenance attachments when present

## Selector model

The selector model is logical and consumer-visible.

Initial required selector families:

- `direct-shard=<shardId>`
- `route-node=<id>`
- `route-left-node=<id>`
- `route-right-node=<id>`
- `route-name=<exact>`
- `route-lang=<lang>`

Required rule:

- selectors resolve to logical shard ids first
- only after that may the runtime choose a sink-specific `objectRef`

This prevents:

- HF path names from becoming the routing model
- IPFS CIDs from becoming the selector model

## Routing index

Optional but strongly recommended:

- `routingIndex`

Required semantics when present:

- maps selector-space to logical shard ids
- does not map directly to sink paths

Suggested initial families:

- node routes:
  - node -> `left` shard ids
  - node -> `right` shard ids
  - node -> `nameOfNode` shard ids
- exact name routes:
  - `(lang, normalized_name_hash)` -> `nodeOfName` shard ids

Allowed initial encodings:

- JSON for proof/debug
- sqlite or binary table for denser durable use

## Cache and invalidation rules

Required cache key components:

- `contractVersion`
- `artifactId`
- `artifactRevision`
- `shardId`
- `contentDigest`
- sink-specific `uri`

Required invalidation rule:

- cached payload is invalid if any of the above identity fields change

Recommended consumer rule:

- prefer digest-validated reuse across sinks when the same logical shard is
  mirrored to both HF and IPFS

## Zelph consumer obligations

Zelph must:

- treat the contract as read-only
- resolve selectors to logical shard ids before sink fetch
- prefer query-shaped fetch policy over full artifact hydration
- keep sink choice additive:
  - HF first when configured for hosted query
  - local/file or IPFS when explicitly configured
- avoid relying on sink path structure as part of semantic routing
- display optional DA51/formal-evidence provenance as provenance, not as query/promotion authority

Zelph may:

- use JSON projection as its primary manifest encoding
- use denser routing indexes later

Zelph may not:

- redefine shard identity around local chunk numbering once the shared contract
  is adopted
- infer proof from DA51 status, route metadata, or a sink URI

## ZOS publisher/puller obligations

ZOS must:

- publish immutable artifact revisions
- preserve logical shard ids across sink publication
- attach sink refs for every published shard it materializes
- keep publication and retrieval separate from selector semantics
- record which sinks were successfully published for a given artifact revision
- preserve optional DA51/formal-evidence provenance without reinterpreting it

ZOS may:

- publish HF-only
- publish IPFS-only
- mirror both sinks for the same artifact revision

ZOS may not:

- rewrite logical shard ids per sink
- let publish transport change the contract meaning
- treat publication acknowledgement as proof or semantic promotion

## Current repo-fit read under this contract

- Zelph:
  - best current fit for consumer/query behavior
- Kant:
  - best current fit for packaging/content identity discipline
- HF:
  - best current fit for hosted query transport
- IPFS:
  - best current fit for immutable publication transport

This contract is therefore intentionally hybrid.

## First implemented tooling

The first bounded implementation slice now exists in-tree:

- builder:
  - `tools/build_shared_shard_artifact_contract.py`
- regression test:
  - `tests/test_build_shared_shard_artifact_contract.py`

Current emitted behavior:

- lifts an existing Zelph HF manifest into the shared logical contract
- computes stable logical shard ids
- computes per-shard digests from the local source `.bin` when available
- emits a JSON projection
- emits a CBOR projection of the same semantic artifact
- can attach optional `ipfs://` object refs from a supplied mapping file

The 2026-10-17 formal-evidence cross-repo fixture additionally proves at the contract level that one logical shard may carry both HF and IPFS refs with one content digest while the DA51/demand/evidence attachments remain separate from sink identity.

## Minimal example shape

```json
{
  "contractVersion": "shared-shard-artifact/v1",
  "artifactId": "formal-evidence-smith",
  "artifactRevision": "rev:formal-evidence-smith:1",
  "artifactClass": "formal-evidence",
  "createdAtUtc": "2026-10-17T00:00:00Z",
  "da51Address": "0xDA51831100800000",
  "formalDemandRef": "formal-demand:smith:1",
  "formalEvidenceRef": "formal-evidence:smith:1",
  "statementDigest": "sha256:statement-smith-direct-assistance",
  "shards": [
    {
      "shardId": "formal-evidence-smith-proof",
      "section": "proof",
      "logicalKind": "formal-evidence",
      "encoding": "cbor",
      "sizeBytes": 512,
      "contentDigest": "sha256:artifact-smith-proof",
      "routingKeys": ["formal-evidence:smith:1"],
      "objectRefs": [
        {
          "sink": "hf",
          "uri": "hf://datasets/example/formal-evidence-smith/proof.cbor",
          "sizeBytes": 512,
          "contentDigest": "sha256:artifact-smith-proof"
        },
        {
          "sink": "ipfs",
          "uri": "ipfs://bafyexampleformalevidencesmith",
          "sizeBytes": 512,
          "contentDigest": "sha256:artifact-smith-proof"
        }
      ]
    }
  ]
}
```

## Promotion gates

Do not promote this contract beyond planning until:

1. one emitted artifact can be projected to both:
   - JSON/HF
   - CBOR/IPFS
2. Zelph can consume the logical selector model without sink-specific hacks
3. ZOS can publish/pull by logical shard id rather than path-only conventions
4. one bounded harness compares:
   - Zelph-style shard generation
   - Kant-style shard generation
   under this same contract
5. formal-evidence consumers preserve exact `demandRef + obligationRef + statementDigest` matching rather than treating provenance attachments as proof authority

## Immediate next step

Use this note as the canonical schema/obligation source for bounded publication/query integration. The DA51/SLR formal-evidence fixture is the regression shape for proof-linked artifacts; it does not replace existing Zelph/Kant fixture families.
