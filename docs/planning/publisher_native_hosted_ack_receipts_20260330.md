# Publisher-Native Hosted Acknowledgement Receipts (2026-03-30)

## Purpose

Move hosted acknowledgement fields into the normal publish substrate, not only
bridge-side helper commands.

## What changed

The sibling publisher repo `/home/c/Documents/code/erdfa-publish-rs` now carries
hosted acknowledgement fields natively in the publish receipt model.

Additive changes:

- `PublishReceipt` now includes:
  - `container_ref`
  - optional `hosted_acknowledgement`
- new type:
  - `HostedAcknowledgement`
- new validation path:
  - `PublishReceipt::bind_hosted_acknowledgement(...)`
  - `PublishOutcome::bind_hosted_acknowledgement(...)`

The bind step validates:

- sink matches the receipt sink
- locator URI matches the projected container object ref
- content digest matches the projected container digest
- size matches the projected container size

So hosted acknowledgement stays transport-level and receipt-level. It does not
mutate shard identity or semantic content.

## Why this matters

Before this change:

- ITIR bridge helpers could prove live HF/IPFS acknowledgement and read-back
- but the normal Rust publish substrate still only emitted projected receipts

After this change:

- the normal publisher receipt type can carry the hosted acknowledgement object
- bridge-side live verification can now be folded back into the publisher's
  native receipt model
- HF and IPFS live verification are no longer structurally outside the publish
  substrate

## Current state

The stack is now split cleanly:

- publisher projects sink refs and container refs
- hosted verifier obtains commit/CID acknowledgement and read-back parity
- publisher-native receipt binds that acknowledgement if and only if the
  transport-level facts match the projected container ref

## Live native workflow result

The sibling publisher example now executes this path directly:

- command:
  `ERDFA_HF_DATASET_ROOT=hf://datasets/chbwa/itir-zos-ack-probe ERDFA_IPFS_API=http://127.0.0.1:5001 ERDFA_IPFS_GATEWAY=http://127.0.0.1:8080 cargo run --example publish_hosted`
- observed HF acknowledgement:
  `a0e5eca8f37373bd2ed87e0e1b119c8d7a45e95d`
- observed IPFS acknowledgement:
  `QmYmZz89Q4viSn1CvsSYpMmK4c1FSbfpQB2aqurjP3k4hj`
- both bound into native publisher receipts with `verified=true`
- first-class emitted artifacts now written per sink:
  - `manifest.json`
  - `container-index.json`
  - `receipt.json`
- example output roots:
  - `/tmp/erdfa-publish-hosted/hf/artifact-demo/rev-a`
  - `/tmp/erdfa-publish-hosted/ipfs/artifact-demo/rev-a`

## Remaining gap

The remaining work is integration glue, not missing receipt structure:

- decide whether IPFS per-shard refs should remain projected placeholders or be
  upgraded to real hosted shard refs in a later adapter refactor
- keep remote JMD push/pull blocked until endpoint/replay/ack semantics are
  declared
