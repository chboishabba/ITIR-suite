# `n00b` Corroborating Surfaces (2026-03-29)

## Goal

Record what `n00b/` does and does not add to the current ITIR read around
proof-first publication, HF-hosted shards, and related source repos.

## Current finding

`n00b/` is useful as corroborating ecosystem evidence.

It supports:

- a proof/publish/Nix-oriented development posture
- HF-hosted sharded deployment as a real operational pattern
- `erdfa-publish` as part of the intended source stack

It does **not** by itself settle:

- the ITIR shared logical artifact contract
- Zelph consumer routing semantics
- JMD host endpoint/replay/receipt semantics

So `n00b/` is evidence of direction and surrounding ecosystem shape, not a new
authoritative contract source.

## Concrete corroborating signals

From `n00b/DEPLOYMENTS.md`:

- one app is described as a "71-shard" WASM deployment
- Hugging Face Spaces is listed as an active deployment target
- the source stack explicitly includes:
  - `source/erdfa-publish`
  - `source/pick-up-nix`
  - `source/solfunmeme-dioxus`
  - `source/solfunmeme-introspector`

From `n00b/README.md`:

- HF is presented as a live deployment surface in that ecosystem

## Submodule/source mapping

`n00b/.gitmodules` declares these source repos:

- `mcp_server`
  - `https://github.com/awslabs/mcp`
- `source/solfunmeme-dioxus`
  - `https://github.com/meta-introspector/solfunmeme-dioxus.git`
- `source/erdfa-publish`
  - `https://github.com/meta-introspector/erdfa-publish.git`
- `source/solfunmeme-introspector`
  - `https://github.com/jmikedupont2/solfunmeme-introspector.git`
- `source/pick-up-nix`
  - `https://github.com/meta-introspector/pick-up-nix.git`
- `source/wrangler-action`
  - `https://github.com/cloudflare/wrangler-action.git`

This confirms that `n00b/` is intentionally wired to:

- HF-hosted frontend deployment
- Nix-backed development
- `erdfa-publish` as a named source dependency

## Practical ITIR reading

Use `n00b/` as support for these current repo positions:

- proof-first / Nix-backed posture is real in the surrounding ecosystem
- HF-hosted sharded artifacts are not just hypothetical
- `erdfa-publish` belongs on the publish-side reference list

Do not use `n00b/` as proof of:

- the final Zelph selector/routing contract
- a complete JMD push/pull API
- a stable receipt/replay/on-wire remote contract
