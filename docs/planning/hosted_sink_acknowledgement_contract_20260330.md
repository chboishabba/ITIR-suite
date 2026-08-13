# Hosted Sink Acknowledgement Contract (2026-03-30)

## Purpose

Pin the smallest remote acknowledgement contract needed before this repo can
honestly claim hosted HF/IPFS integration rather than local-first projection
and rehearsal only.

This note does not declare that JMD currently provides this contract.

## Problem

The repo now has:

- a local publish substrate
- explicit sink refs and per-sink receipts
- a real local consumer rehearsal path

What it still lacks is a deterministic remote acknowledgement surface.

Without that surface, hosted integration can only be described as:

- local projection
- local mirror rehearsal
- best-effort read probes

not as stable hosted publish/pull completion.

## Boundary

This contract is about transport acknowledgement only.

It does not decide:

- truth or promotion
- selector semantics
- shard identity
- `SL` / `ZOS` authority

## Required acknowledgement object

For a hosted publish action to count as acknowledged, the remote side must
return or expose a stable acknowledgement object with at least:

- `sink`
- `artifactId`
- `artifactRevision`
- `publishedAt`
- `publishStatus`
- `containerObjectRef`
- `contentDigest`
- `memberCount`
- `receiptId` or equivalent stable acknowledgement id

Optional but strongly preferred:

- `etag` or object version
- `commitSha` / dataset revision / pin record
- byte size
- replay token or monotonic publish sequence

## Sink-specific minimums

### HF

Minimum hosted acknowledgement should include:

- deterministic object URI
- revision/commit identifier
- content digest or reproducible hash
- success status that is not merely a local projected URI

Examples of acceptable acknowledgement evidence:

- dataset commit SHA plus object path
- API response carrying a stable revision
- later read-back proving exact digest under that revision

### IPFS

Minimum hosted acknowledgement should include:

- CID
- gateway or pinning acknowledgement source
- content digest parity
- success state that is stronger than "we can locally derive a CID"

Examples of acceptable acknowledgement evidence:

- pin/add acknowledgement from a real pinning endpoint
- read-back from a stable gateway proving the expected CID content

## Read-after-write rule

Hosted acknowledgement is only strong enough if this repo can also prove a
bounded read-after-write check:

1. publish
2. obtain acknowledgement
3. fetch by the acknowledged remote ref
4. verify digest and expected member payload

If step 3 or 4 is not deterministic, the publish is not yet promotable as a
stable hosted integration result.

## Replay / cache rule

Hosted acknowledgement is incomplete without one replay rule.

At least one of these must be true:

- the hosted sink exposes immutable revisioned reads
- the hosted sink returns a replay token that can be re-used deterministically
- this repo persists a local acknowledgement object that can be verified later
  against a stable remote read surface

Without that, receipt evidence degrades to best-effort observability rather
than reproducible publication.

## JMD-specific implication

This is the missing contract slice before remote JMD push/pull can be
implemented honestly.

For JMD, the repo still lacks declared semantics for:

- where acknowledgement lives
- whether `/raw/{id}`, `/browse`, or `/ipfs/{cid}` are authoritative replayable reads
- whether a publish action has a stable acknowledgement id
- whether the acknowledgement object is:
  - an API response
  - a persisted receipt artifact
  - a browse/raw-visible object
  - a zkperf-linked execution receipt

## Current repo reading

Current completion status is therefore:

- local/file publish + consume: complete
- projected HF/IPFS refs + receipts: complete
- hosted HF/IPFS acknowledgement contract: not yet pinned
- remote JMD push/pull: still blocked

## Release gate

Treat hosted integration as complete only when the repo can show all of:

1. remote acknowledgement object exists
2. acknowledgement object carries stable artifact/container identity
3. read-after-write verification passes against the acknowledged remote ref
4. replay or cache semantics are explicit enough to reproduce later

Until then, hosted sink work remains:

- provisional
- local-first
- non-authoritative for completion claims
