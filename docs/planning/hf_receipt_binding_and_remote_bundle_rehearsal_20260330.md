# HF Receipt Binding and Remote Bundle Rehearsal (2026-03-30)

## Purpose

Move the HF lane from manual acknowledgement probes to a repeatable receipt-
bearing publisher path plus a real revision-bound consumer read-back path.

## What is now implemented

### Publisher-side receipt binding

The ITIR bridge now has a bounded CLI command:

- `python -m itir_jmd_bridge publish-hf-ack --local-path ... --hf-uri ...`

This command:

- uploads a local artifact with `hf upload`
- parses the acknowledged HF commit revision from the upload result
- fetches the uploaded object back by the acknowledged revision
- computes local sha256 and compares it against the fetched object
- emits one verified HF acknowledgement receipt payload

Receipt payload fields include:

- `sink`
- `repoType`
- `repoId`
- `objectPath`
- `hfUri`
- `localPath`
- `acknowledgedRevision`
- `localSha256`
- `localSizeBytes`
- `fetch`
- `verified`

### Consumer-side revision-bound remote fetch

The ITIR bridge now also has a bounded CLI command:

- `python -m itir_jmd_bridge rehearse-remote-hf-bundle --manifest-path ... --tar-path ... --hf-uri ... --hf-revision ... --selector ...`

This path proves:

- selector -> shard id
- shard id -> `objectRefs[]`
- HF object ref -> remote fetch by acknowledged revision
- tar member extraction from fetched remote bytes
- payload digest parity against the manifest/container-derived member digest

## Concrete verified object

The current concrete target is:

- HF object:
  `hf://datasets/chbwa/itir-zos-ack-probe/bundle-demo/erdfa-demo.tar`
- acknowledged revision:
  `dccdb582947b0ccdc7be03db5b1caa879c56d187`
- tar sha256:
  `4dcd386fb6323a76f934174db94deb9e528028d88c648607875c832941cb37b7`

Remote rehearsal now succeeds against that exact acknowledged revision.

## Why this matters

This closes the local-only gap for the HF consumer lane.

The repo now has:

- a repeatable HF upload-and-verify receipt path
- a revision-bound remote consumer fetch path over a real emitted tar bundle
- explicit evidence that HF revision acknowledgement can be folded back into a
  bounded local receipt without changing shard semantics

## Remaining gap

This is still HF-specific and still bounded.

What remains before claiming broader hosted completion:

- promote the same receipt binding into the normal local publish substrate,
  rather than a bridge-side helper command
- add equivalent hosted acknowledgement treatment for IPFS
- pin remote replay/cache expectations as a stable contract, not just observed
  behavior
- keep remote JMD push/pull blocked until endpoint and acknowledgement
  semantics are declared
