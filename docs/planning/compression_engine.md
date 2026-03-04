# Compression Engine (Domain-Neutral)

Status: draft (2026-03-04).

This document defines the domain-neutral lexical compression engine referenced by:
- `docs/planning/sl_lce_profile_followthrough_20260208.md`

It is a **shared** engine. Profiles (SL/SB/infra) must not alter its mechanics.

## Purpose
Provide deterministic, reversible, non-inventive compression of text into a
token stream plus declared overlays (groups and axes) that remain traceable to
explicit spans.

## Non-goals
- No interpretation or inference.
- No profile-specific admissibility decisions (see `docs/planning/profile_contracts.md`).
- No semantic normalization beyond deterministic tokenization.

## Core Concepts

### 1) Canonical Token Stream
Inputs:
- `source_text` (string)
- optional `source_language` (string)

Outputs:
- ordered list of canonical tokens with stable offsets into the original text.

Rules:
- Tokenization is deterministic for a given engine version and input bytes.
- Token offsets map to original text, not a normalized copy.
- All further overlays must reference these offsets.

### 2) Span Anchoring
Every annotation (group/axis) must link to explicit text spans.

Rules:
- A span is `[start_char, end_char)` in the original string.
- Multi-span annotations are allowed but must preserve order.
- Deleting overlays must not change the canonical token stream.

### 3) Declared Groups
Groups are user or rule-declared buckets for compression and retrieval.

Rules:
- Group membership must be explicit, never inferred.
- Each group entry references one or more spans.
- Groups carry provenance of the declarer and rule or source.

### 4) Declared Lexical Axes
Axes express orthogonal distinctions (example: `hosted/non_hosted`).

Rules:
- Axis values are enumerated and explicit.
- Axis assignment must be span-anchored.
- Axes cannot alter tokenization.

### 5) Non-Inventive Overlays
Overlays are optional annotations that compress or label text, but do not add
new facts or claims.

Rules:
- Overlays may only restate or label existing spans.
- Overlay removal must be lossless to the original text.

## Determinism and Reversibility
Invariants:
- Same input bytes + same engine version => identical token stream.
- Overlays are additive only; removing overlays restores raw text without loss.
- Ordering of tokens and overlays is stable and deterministic.

## Engine Invariants (Non-Negotiable)
1. **Canonical text is immutable**: all spans point to the original input bytes.
2. **Deterministic tokenization**: same engine version + same bytes => identical tokens.
3. **Span anchoring required**: every group/axis/overlay must reference spans.
4. **Non-inventive overlays**: overlays may label but never add new facts/tokens.
5. **Reversibility**: removing overlays returns a lossless view of canonical text.
6. **Profile isolation**: profiles can accept/reject overlays, not alter tokens.

## Provenance Requirements
Each output artifact must include:
- `engine_id` and `engine_version`
- `source_id` (document or artifact identifier)
- `source_hash` (hash of raw input bytes)
- `created_at` (UTC timestamp)
- `declared_by` for each overlay (human, rule id, or tool id)

## Minimal Data Shape (Illustrative)
```json
{
  "engine_id": "lce_v1",
  "engine_version": "1.0.0",
  "source_id": "artifact:example",
  "source_hash": "sha256:...",
  "created_at": "2026-03-04T00:00:00Z",
  "tokens": [
    {"t":"George","start":0,"end":6},
    {"t":"W.","start":7,"end":9},
    {"t":"Bush","start":10,"end":14}
  ],
  "groups": [
    {
      "group_id":"actor_root",
      "spans":[{"start":0,"end":14}],
      "declared_by":"rule:actor_root_v1"
    }
  ],
  "axes": [
    {
      "axis_id":"hosting",
      "value":"non_hosted",
      "spans":[{"start":0,"end":14}],
      "declared_by":"human:curator"
    }
  ],
  "overlays": [
    {
      "overlay_id":"label",
      "label":"Person",
      "spans":[{"start":0,"end":14}],
      "declared_by":"rule:labeler_v1"
    }
  ]
}
```

## Validation Rules (Engine-Level)
- Every span must be within `source_text` bounds.
- Overlaps are permitted but must be explicit and ordered.
- No overlay may introduce tokens absent from the canonical stream.
- An overlay with empty spans is invalid.
 - Overlay ordering must be deterministic and stable across runs.

## Profile Interface (Boundary Only)
Profiles may only:
- accept or reject overlays/groups/axes based on admissibility rules.
- add profile-specific lint checks.

Profiles may not:
- change tokenization.
- re-order tokens or spans.
- introduce unanchored text.

## Conformance Tests (Engine-Level)
These tests are required and must remain green across upgrades.

1. **Determinism**: identical input bytes produce identical tokens and span maps.
2. **Span integrity**: every recorded span points to non-empty `source_text[start:end]`.
3. **Overlay reversibility**: removing overlays yields exact canonical text (byte-equal).
4. **Overlay non-inventive**: no overlay introduces characters not present in the source.
5. **Stable ordering**: overlay ordering is deterministic across runs.
6. **Profile isolation**: profiles do not alter token stream or spans.

See also:
- `docs/planning/cross_profile_safety_tests.md`

## Open Questions
- Do we need a normalized token form for search, separate from canonical tokens?
- How do we store multi-language tokenization without drifting offsets?
- Should group and axis IDs be centrally registered or per-profile?
