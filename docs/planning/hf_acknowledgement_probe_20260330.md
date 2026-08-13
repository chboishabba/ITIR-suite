# HF Acknowledgement Probe (2026-03-30)

## Purpose

Pin one concrete public HF resolve surface that exposes enough read-side
metadata to qualify as the first hosted acknowledgement target.

## Probe target

- HF URI:
  `hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json`
- resolve URL:
  `https://huggingface.co/datasets/chbwa/zelph-sharded/resolve/main/minimal-proof/manifest.json`

## Observed public behaviour

Public HEAD/GET against that object now shows:

- initial `307` redirect from `resolve/main/...`
- redirect target under `/api/resolve-cache/...`
- `x-repo-commit` header present
- `etag` header present
- `x-linked-etag` present on the redirecting response
- final `200` response exposes:
  - `etag`
  - `x-repo-commit`
  - `content-length`
  - `accept-ranges`
  - `content-disposition`

Observed values during the probe:

- `x-repo-commit`:
  `059c578f2bd0f068e46a73b61205d39190e7dc92`
- final `etag`:
  `"b1ac026a5ef46d88a4a498e8e54bb3f41aedcdb0"`

## ITIR reading

This is enough to pin a read-side HF acknowledgement shape as:

- repo id
- object path
- resolve URL
- final URL
- status code
- `x-repo-commit`
- `etag`
- optional redirect-chain metadata

This is not yet a write acknowledgement.

It is only the first concrete hosted read/verification surface.

## Implemented seam

ITIR now has a bounded probe for this:

- provider:
  `itir_jmd_bridge/providers/hf.py`
- CLI:
  `python -m itir_jmd_bridge probe-hf-ack --hf-uri hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json`
- tests:
  `tests/test_hf_acknowledgement_probe.py`

## What this solves

- HF is no longer just hypothetical for hosted acknowledgement metadata
- the repo now has one concrete public object whose resolve surface exposes:
  revision, etag, and stable read URL information

## What this does not solve

- no write acknowledgement yet
- no upload confirmation semantics
- no JMD-specific hosted acknowledgement object
- no replay/cache contract beyond what HF resolve currently exposes

## Next HF gate

The next hosted HF step should be:

1. publish to a controlled HF target
2. capture the resulting revision / acknowledgement object
3. read back the exact object via the acknowledged revision
4. verify digest parity against local publish receipts
