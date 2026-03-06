# Receipts Pack Automation Contract (2026-02-08)

## Purpose
Formalize the investigative "Receipts Pack" automation pattern for ITIR/SensibLaw
so high-level claims can be expanded into verifiable evidence bundles.

This artifact is contract/planning only.

## Current state vs target state

### Current implemented surfaces (confirmed)
- `SensibLaw/cli/receipts.py` provides:
  - `receipts build`
  - `receipts verify`
  - `receipts diff`
- `SensibLaw/src/receipts/__init__.py` provides simple pack generation:
  - `data.txt`
  - `SHA256SUMS`
  - `verify.sh`
- `SensibLaw/tests/receipts/test_pack.py` verifies tamper detection behavior.

### Target state (this contract)
- Graph-seeded receipts pack generation for investigative/legal claims.
- Deterministic reproducibility panel with command/version/hash evidence.
- Optional signature workflows and publishable "click-to-verify" fragments.
- Pack structure optimized for human verification and machine replay.

## Core automation interface (target)

### Proposed command contract
`sensiblaw receipts pack --seed <node_id> --hops <n> --out <path>`

Notes:
- This command is proposed target behavior; it is not yet the currently shipped
  CLI surface.
- Existing `receipts build/verify/diff` remain foundational primitives.

### Seed traversal contract
- Start from an explicit seed node (concept/case/provision/claim ID).
- Traverse graph neighborhood up to `hops`.
- Emit deterministic graph slice and evidence index.

## Pack contents (target minimum)
- `index.html`:
  human-readable entry with references to all bundle artifacts.
- `graph/`:
  graph slice outputs (`.dot`, `.svg`, optional `.json` adjacency).
- `tables/`:
  treatment/checklist tables with source pointers.
- `evidence/`:
  source excerpts/pinpoints and provenance references.
- `repro/`:
  reproducibility metadata (commands, versions, hashes, environment summary).
- `SHA256SUMS` + `verify.sh`:
  hash verification utilities (baseline invariant).
- `manifest.json`:
  canonical machine-readable index of all files + provenance fields.

## Manifest contract (target fields)
- `pack_id`
- `seed_id`
- `hops`
- `generated_at`
- `tool_versions`
- `commands`
- `inputs` (IDs/hashes)
- `outputs` (paths/hashes)
- `policy_receipts`
- `idempotency_key`
- `payload_hash`
- `correlation_id`
- `causation_id`
- `authority_class`

## Verification and integrity contract

### Baseline (mandatory)
- Hash manifest verification must succeed offline (`verify.sh`).
- Any file mutation after pack generation must fail verification.

### Extended (planned)
- Signed evidence packs and optional public fragment verification workflows.
- Explicit verification status surfaced in `index.html`.
- Optional cryptographic posture enhancements (TARGET):
  - signature over `manifest.json` (e.g., Ed25519 signature workflow) so the
    bundle can be authenticated in addition to integrity-checked.
  - optional timestamping receipts (e.g., RFC-3161-class timestamping or
    Roughtime-style anchoring) for stronger chain-of-custody narratives.

## Authority-crossing rules for pack generation
- Pack generation is non-authoritative by default (projection/export lane).
- Any attempt to promote pack-derived interpretation into canonical state must
  produce promotion receipts.
- Local heuristics in bundle annotations remain non-canonical unless promoted.

## Conflict-resolution behavior
- Same `idempotency_key` + same `payload_hash`: no-op replay.
- Same `idempotency_key` + different `payload_hash`: hard conflict.
- `Q6` governs whether reinterpretations share or separate collision domains by
  authority/layer scope.

## Expansion Invariant (formalization for packs)

Invariant:

> It must remain computationally and cognitively cheaper to expand pack claims
> to raw event IDs/provenance than to re-summarize original raw inputs.

Contract implications:
- Pack summaries are indexes over evidence, not replacements for evidence.
- Expansion path is deterministic pointer traversal (no probabilistic expand).
- Loss profile must be declared where detail is folded/omitted.
- Human correction writes new events/annotations; no silent rewrite.

## Acceptance criteria (target)
- AC1: deterministic pack regeneration (same inputs -> same manifest hashes).
- AC2: verify script catches tampering for any artifact in `manifest.json`.
- AC3: each claim/table row expands to raw IDs/provenance pointers in <= 2 hops.
- AC4: reproducibility panel includes exact CLI and version metadata.
- AC5: authority promotion requires receipts and leaves audit trail.

## Related contracts
- `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
- `docs/planning/reducer_ownership_contract_20260208.md`
- `docs/planning/itir_consumption_matrix_20260208.md`
