# JMD Fixture V1 (2026-03-20)

## Purpose
Freeze the first concrete JMD -> SL bridge example so later implementation work
does not reopen the same boundary questions.

This fixture is intentionally minimal. It is not a live adapter, fetch policy,
or runtime integration.

## V1 Decision
The first canonical bridge example is:

- one ERDFA-backed text shard
- with dual ingest references:
  - `kant-zk-pastebin` raw retrieval surface
  - IPFS CID integrity surface
- with `erdfa-publish-rs` treated as the concrete ERDFA shard producer closest
  to the fixture's structural model
- plus one SL overlay payload using byte-addressable anchors

## Why This Shape
- pastebin/IPFS already matches the current JMD-side storage reading in the
  planning docs
- `kant-zk-pastebin` and `erdfa-publish-rs` make that split more concrete:
  raw retrieval plus CID on one side, ERDFA shard structure on the other
- ERDFA remains the structural shard/object model rather than an embedding lane
- one text shard is enough to lock identity, provenance, and reversibility
  before bundle or thread-level complexity is added
- `zos-server` remains future infrastructure, not part of the v1 payload

## Reversibility Rule
For v1, `reversible` means:

- the JMD fixture carries the exact source text used for anchoring
- every SL anchor identifies an exact byte slice in that source text
- the bridge can recover the exact anchored substring from source bytes alone
- token offsets may be emitted, but byte offsets are the normative source trace

It does not mean every future transform is lossless. It means no SL anchor is
allowed to become a fuzzy or guess-based pointer back into JMD content.

## Normative Payload Choices
- canonical JMD identity remains `object_id`
- dual retrieval refs are mandatory in the canonical example:
  - `paste_ref`
  - `cid_ref`
- `object_type` is `shard`
- ERDFA metadata is explicit:
  - producer
  - shard id
  - CID
  - component kind
  - optional parent/link refs
- `text` is present inline in v1 to make traceability unambiguous
- bundle/proof fields are reserved but optional:
  - `corpus_root`
  - `pipeline_id`
  - `params_hash`
  - `metric_commitment`
  - `score_commitment`

## Explicit Non-Goals
- no ZOS transport fields in the normative payload
- no Rabbit/libp2p endpoint assumptions in the fixture
- no direct Casey execution or promotion state
- no provenance bundle requirement in v1
- no thread/container-level object as the first example

## Fixture Files
- `docs/planning/jmd_fixtures/jmd_sl_ingest_v1.example.json`
- `docs/planning/jmd_fixtures/sl_jmd_overlay_v1.example.json`

## Acceptance Meaning
The fixture is acceptable only if:

- both paste and CID refs are present
- SL anchors resolve back to exact source substrings
- every overlay points back to explicit JMD source refs
- ERDFA structure is represented without requiring live ERDFA runtime ingestion
