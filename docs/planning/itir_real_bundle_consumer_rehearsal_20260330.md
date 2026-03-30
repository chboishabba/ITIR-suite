# ITIR Real Bundle Consumer Rehearsal (2026-03-30)

## Goal

Prove a real local consumer-side resolution path from an emitted
`erdfa-publish-rs` bundle, not just static JSON fixtures.

## Inputs

- real promoted manifest emitted by:
  - `cargo run --example demo` in `/home/c/Documents/code/erdfa-publish-rs`
  - output: `/tmp/erdfa-promoted-manifest.json`
- real tar archive emitted by:
  - output: `/tmp/erdfa-demo.tar`

## Implemented consumer path

The rehearsal path now supports:

`selector -> shard id -> objectRefs[] -> sink fetch -> payload digest`

with local sink selection order and sink-specific URI mapping.

### Local-first sink handling

- `file` sink: reads directly from `file://...` tar object refs
- `hf` sink: maps `hf://...` URI to a local mirrored tar path for rehearsal
- `ipfs` sink: maps `ipfs://...` URI/CID to a local mirrored tar path for rehearsal

This keeps sink semantics transport-only and does not alter shard identity.

## Container/index and objectRef stitching

Given a real manifest + tar:

- build a container index from tar member discovery and member digests
- attach per-shard `objectRefs[]` from configured sink refs
- resolve selector against the normalized manifest
- fetch and extract the selected member payload from the chosen sink object

## Validation status

Targeted tests prove:

- stable shard id parity across manifest and derived container index
- selector resolution from real promoted manifest output
- objectRef sink selection (`file`, `hf`, `ipfs`) over the same emitted bundle
- payload digest/size consistency between extracted payloads and container index metadata
- CLI rehearsal against real emitted outputs

## Hosted HF followthrough

This note started as a local rehearsal only. It now also has a bounded remote
HF followthrough:

- `publish-hf-ack` uploads a local tar and emits a verified HF acknowledgement
  receipt
- `rehearse-remote-hf-bundle` fetches the acknowledged HF tar by revision and
  extracts the selected member payload remotely

That followthrough is pinned in:

- `docs/planning/hf_receipt_binding_and_remote_bundle_rehearsal_20260330.md`

## Boundary note

This is still a bounded contract check, not a generalized hosted publisher.

It does not claim remote JMD transport semantics, HF upload orchestration, or
IPFS publication acknowledgements.
