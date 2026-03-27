# Zelph / Kant / ZOS Shard Contract Matrix (2026-03-27)

ZKP Frame

O:
- local owners:
  - `aur/zelph`
  - `kant-zk-pastebin`
  - `zos-server`
- external sinks:
  - Hugging Face
  - IPFS
- decision owner:
  - current repo/user before any shared branch or upstream proposal

R:
- choose the right shared artifact contract for shard publication and
  consumption without prematurely forcing one repo's runtime assumptions on the
  others
- distinguish "best fit for a role" from "globally optimal sharder"

C:
- `docs/planning/zelph_hf_storage_contract_20260326.md`
- `docs/planning/zelph_hf_v3_shard_contract_20260326.md`
- `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md`
- `kant-zk-pastebin/src/ipfs.rs`
- `kant-zk-pastebin/src/sheaf.rs`
- `kant-zk-pastebin/src/bin/freeze_chats.rs`
- `aur/zelph/src/lib/network/zelph_impl.hpp`
- `tools/build_zelph_hf_manifest.py`

S:
- Zelph already has a working HF-hosted partial-load path with:
  - manifest-driven shard selection
  - route-sidecar support
  - query-shaped `v3` bucket planning
- `kant-zk-pastebin` already has:
  - `Shard` / `ShardSet`
  - `manifest.cbor`
  - IPFS-backed content addressing
  - RDFa / CBOR envelopes
  - shard emission
- ZOS already thinks in publish/pull terms, but its HF publish machinery is
  still not a finished transport contract
- therefore:
  - transport reachability is not the primary unknown
  - shared artifact contract and role fit are the primary unknowns

L:
- current proofs -> role-fit matrix -> shared artifact contract -> bounded
  comparison harness -> promoted shared branch

P:
- Proposal A:
  - treat the problem as four axes:
    - sharder
    - sink
    - consumer runtime
    - shared artifact contract
- Proposal B:
  - use Zelph's shard logic for graph-query-shaped remote reads
- Proposal C:
  - use Kant's shard logic for publish/pull packaging and content-addressed
    artifact identity
- Proposal D:
  - keep HF and IPFS as alternate sinks behind one contract rather than
    hard-coding one sink into the schema

G:
- do not promote a shared branch until one written contract defines:
  - selector model
  - manifest/schema shape
  - sink abstraction
  - cache/invalidation semantics
  - validation harness
- do not claim "optimal" unless the comparison harness exists and measures both
  shard families against the same workload

F:
- missing:
  - shared contract note
  - side-by-side comparison harness
  - explicit promotion gates for a Kant-first, Zelph-first, or hybrid path

Synthesis:
- Current evidence supports role-fit, not global optimality.
- Zelph looks better for query-shaped graph reads.
- Kant looks better for publish/pull artifact packaging.
- HF looks better for practical hosted querying.
- IPFS looks better for immutable content-addressed publication.

Adequacy:
- Adequate for planning and TODO alignment.

Next action:
- freeze the shared artifact-contract note as
  `docs/planning/shared_shard_artifact_contract_v1_20260327.md` before
  implementing another cross-repo shard branch.

## Four-axis matrix

### 1. Sharder

- Zelph sharder:
  - best current fit for graph-query-shaped remote reads
  - strengths:
    - selector-aware layout
    - route-sidecar support
    - explicit fetch-budget reasoning
    - planned `v3` bucket model for outgoing/incoming/name lookups
  - weakness:
    - publication identity and content-addressing are not its primary design
      center

- Kant sharder:
  - best current fit for artifact packaging and publish/pull
  - strengths:
    - `Shard` / `ShardSet`
    - `manifest.cbor`
    - content-addressed shard identity
    - RDFa / CBOR packaging discipline
  - weakness:
    - not yet obviously optimized for Zelph-style graph-query fetch cost

### 2. Sink

- Hugging Face:
  - best current fit for practical remote query hosting
  - strengths:
    - simple object hosting
    - proven remote Zelph partial-load path
    - easier operational workflow for testing and sharing
  - weakness:
    - object identity is weaker unless the contract carries explicit immutable
      metadata and cache rules

- IPFS:
  - best current fit for immutable publication and integrity-first sharing
  - strengths:
    - content addressing
    - replication-friendly
    - already embedded in the Kant ecosystem
  - weakness:
    - less obviously convenient for interactive selective querying unless the
      shard layout is already very good

### 3. Consumer runtime

- Zelph:
  - should remain a read/query consumer
  - primary need:
    - efficient selector resolution
    - bounded remote fetch cost

- ZOS:
  - should remain the publish/pull orchestration surface
  - primary need:
    - artifact publication
    - retrieval
    - identity and synchronization discipline

### 4. Shared artifact contract

This is the unresolved hinge. The shared contract must define:

- shard identity
- manifest schema
- selector/routing model
- sink-specific pathing without sink-specific semantics leakage
- cache and invalidation rules
- comparison harness inputs/outputs

## Current best-fit read

- For Zelph remote querying:
  - prefer Zelph-style query-shaped sharding
- For ZOS publish/pull:
  - prefer Kant-style shard packaging and identity
- For hosted query sink:
  - prefer HF first
- For immutable publication sink:
  - prefer IPFS first

This is a hybrid recommendation, not a single-winner recommendation.

## What is not yet justified

The following claims are not yet justified:

- "our sharder is globally optimal"
- "Kant is better everywhere"
- "HF should replace IPFS"
- "IPFS should replace HF"

Those require one bounded comparison harness using the same workload and the
same success metrics.

## Minimal comparison harness requirements

Any future comparison should measure both shard families on the same axes:

- artifact size and object count
- manifest size
- route/selector resolution cost
- median and tail remote fetch size
- publish/pull simplicity
- cache behavior and invalidation safety
- rebuild determinism from the same source artifact

## Recommended collapse

The current best next move is:

1. freeze the shared artifact contract
2. keep Zelph read-focused and ZOS publish/pull-focused
3. compare Zelph-style and Kant-style shard generation only after the contract
   is fixed
