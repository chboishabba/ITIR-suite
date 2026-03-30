# HF Write Acknowledgement Probe (2026-03-30)

## Purpose

Record the first successful write-side HF acknowledgement probe from this
environment.

## Controlled target

- dataset repo:
  `chbwa/itir-zos-ack-probe`
- uploaded object:
  `ack-probe/ack-probe.json`

Local source artifact:

- `/tmp/hf-ack-probe/ack-probe.json`
- local sha256:
  `52a02d3502cc39411dab1c291e7d6f9789f3a72aef77417a4b11637cdd4c3dfb`

## Write-side acknowledgement

The upload returned a concrete commit acknowledgement URL:

- `https://huggingface.co/datasets/chbwa/itir-zos-ack-probe/commit/0c56f0d5b090f447d35a5525a1a8e01df10ee284`

This is the first write-side acknowledgement object pinned by this repo for
HF.

## Read-back verification

The repo now has a public read-back seam:

- CLI acknowledgement probe:
  `python -m itir_jmd_bridge probe-hf-ack --hf-uri hf://datasets/chbwa/itir-zos-ack-probe/ack-probe/ack-probe.json`
- CLI fetch probe:
  `python -m itir_jmd_bridge fetch-hf-object --hf-uri hf://datasets/chbwa/itir-zos-ack-probe/ack-probe/ack-probe.json --revision 0c56f0d5b090f447d35a5525a1a8e01df10ee284`

The required completion condition for this probe is:

- commit acknowledgement exists
- read-back by the acknowledged revision succeeds
- fetched digest matches local digest

Observed read-back result:

- revision:
  `0c56f0d5b090f447d35a5525a1a8e01df10ee284`
- fetched sha256:
  `52a02d3502cc39411dab1c291e7d6f9789f3a72aef77417a4b11637cdd4c3dfb`
- status:
  `200`

This matches the local probe artifact digest exactly.

## Emitted bundle tar followthrough

A real emitted bundle artifact from `erdfa-publish-rs` is now also pinned on
the same dataset:

- object:
  `bundle-demo/erdfa-demo.tar`
- acknowledged commit:
  `dccdb582947b0ccdc7be03db5b1caa879c56d187`
- local sha256:
  `4dcd386fb6323a76f934174db94deb9e528028d88c648607875c832941cb37b7`
- fetched sha256 by acknowledged revision:
  `4dcd386fb6323a76f934174db94deb9e528028d88c648607875c832941cb37b7`

HF exposes the commit metadata for this tar object on the redirect chain:

- redirect response carries:
  - `x-repo-commit`
  - `x-linked-etag`
- final object response comes from CAS/Xet storage

So the read-back seam must preserve redirect-chain metadata, not just final
headers.

## Current state

Write acknowledgement is now no longer hypothetical for HF.

The repo has:

- a concrete writable HF dataset target
- a concrete commit acknowledgement URL
- a code path for revision-anchored read-back verification
- successful digest-parity verification on the committed object

## Remaining gap

This is still a bounded probe, not a generalized publication service.

What remains before calling HF integration fully complete:

- move from a one-off controlled probe to a repeatable publisher path
- bind the HF commit acknowledgement back into local publish receipts
- promote the same write/read-back verification from this emitted tar probe
  into the normal emitted bundle publisher path

## Followthrough now landed

The repo now has the first bounded bridge-side implementation of that next
step:

- upload-and-verify receipt path:
  `python -m itir_jmd_bridge publish-hf-ack --local-path ... --hf-uri ...`
- revision-bound remote consumer rehearsal:
  `python -m itir_jmd_bridge rehearse-remote-hf-bundle --manifest-path ... --tar-path ... --hf-uri ... --hf-revision ... --selector ...`

That followthrough is recorded in:

- `docs/planning/hf_receipt_binding_and_remote_bundle_rehearsal_20260330.md`
