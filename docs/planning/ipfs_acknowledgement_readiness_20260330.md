# IPFS Acknowledgement Readiness (2026-03-30)

## Purpose

Bring the IPFS lane up to the same bounded contract shape as the HF lane, while
recording the current environment blocker for live write/read-back verification.

## What is now implemented

The ITIR bridge now has bounded IPFS commands and provider helpers for the same
contract surfaces already used on HF:

- gateway acknowledgement probe:
  `python -m itir_jmd_bridge probe-ipfs-ack --ipfs-uri ...`
- gateway fetch/read-back:
  `python -m itir_jmd_bridge fetch-ipfs-object --ipfs-uri ...`
- local publish acknowledgement helper:
  `python -m itir_jmd_bridge publish-ipfs-ack --local-path ...`
- remote consumer rehearsal:
  `python -m itir_jmd_bridge rehearse-remote-ipfs-bundle --manifest-path ... --tar-path ... --ipfs-uri ... --selector ...`

These surfaces now support:

- `ipfs://...` URI parsing
- gateway acknowledgement metadata capture
- object fetch and digest computation
- bounded publish acknowledgement from `ipfs add` or Kubo API `/api/v0/add`
- selector -> shard id -> `objectRefs[]` -> remote IPFS fetch -> payload digest parity

## Live surface

The local IPFS Desktop / Kubo surface is now reachable in this environment.

Observed on 2026-03-30:

- local Kubo API:
  `http://127.0.0.1:5001/api/v0/version` returned `200`
- local gateway:
  `http://127.0.0.1:8080/ipfs/<cid>` returned `200` for the emitted tar bundle

The helper now uses the Kubo HTTP API by default when the local daemon is
reachable, even if no `ipfs` CLI binary is present on `PATH`.

## Current state

IPFS now matches HF at the contract/code level and the live local verification
level for:

- acknowledgement probe shape
- fetch/read-back shape
- publish acknowledgement payload shape
- remote consumer rehearsal shape
- local add/pin acknowledgement through the Kubo API
- gateway read-back digest parity

Concrete verified object:

- IPFS URI:
  `ipfs://QmR3Z8n2XFm8LPBcmNCc9d4W9tqMwDRBeUnUnXRGQy2eCa`
- local tar sha256:
  `4dcd386fb6323a76f934174db94deb9e528028d88c648607875c832941cb37b7`
- gateway read-back sha256:
  `4dcd386fb6323a76f934174db94deb9e528028d88c648607875c832941cb37b7`

Remote selector rehearsal now succeeds against that CID via the local gateway.

## Remaining gap

Before calling IPFS hosted completion fully generalized rather than local-live:

- keep the local Desktop/Kubo surface stable enough for repeatable runs
- optionally add a second non-local IPFS pinning surface
- bind the IPFS CID and gateway verification fields into the normal local
  publish substrate rather than bridge-side helpers alone
- keep remote JMD push/pull blocked until endpoint and acknowledgement
  semantics are declared
