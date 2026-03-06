# SL LCE/Profile Followthrough (2026-02-08)

Thread:
- `6986d38e-4b5c-839b-813a-608aa0de88d5` (`ADR language vs SensibLaw`)
- Latest assistant timestamp: `2026-02-07T06:01:41.279462Z`

## 0. Thread Synthesis (Flow / Blockers / Progress)

### 0.1 Flow
- Started with ADR language vs SensibLaw ingest comparison.
- Converged on a three-layer model:
  1. domain-neutral lexical compression engine
  2. domain profile (SL/SB/infra admissibility constraints)
  3. application usage layer
- Shifted from "decision" language to "invariant/constraint/classification"
  wording to keep ingest non-inventive.
- Extended compression model from declared lexical groups to declared lexical
  axes (for orthogonal distinctions like cloud/local, hosted/non-hosted).

### 0.2 Blockers
- ADR-style narratives introduce intent/authority semantics not admissible at
  ingest.
- Profile boundaries are easy to blur unless constraints are codified and linted.
- Axis/group overlays can become implicit inference if reversibility and
  span-anchoring are not enforced.

### 0.3 Progress
- Live thread context validated against the latest assistant message and
  timestamp.
- Reuse framing is now explicit: "reuse the engine, not legal semantics."
- Implementation backlog was translated into docs/TODO tasks for
  contracts/lint/tests.

## 1. Architecture Followthrough

### 1.1 Core cut
- Treat SensibLaw as a law/norm profile over a shared lexical compression
  engine.
- Keep compression mechanics identical across profiles.

### 1.2 Engine primitives (profile-independent)
- Canonical token stream
- Span anchoring
- Declared group membership
- Declared lexical axes
- Non-inventive overlays
- Provenance and deterministic ordering

### 1.3 Profile contracts (profile-dependent)
- `SL` profile: legal/norm admissibility only.
- `SB` profile: state/lifecycle/adapter admissibility only.
- `infra` profile: systems/ops admissibility only.
- Rule: profiles may restrict accepted declarations; they must not change
  compression behavior.

### 1.4 Ingest-safe expression pattern
- Prefer: `Invariant`, `Constraint`, `Classification`, `Authority Boundary`.
- Avoid in Layer 0 docs: `Decision`, rationale narratives, alternatives,
  predictive/evaluative claims.

### 1.5 Safety checks to enforce
- Reversibility check: deleting an overlay must not change source truth.
- Span-anchor check: every group/axis assignment maps to explicit spans.
- Non-inference check: no auto-assignment from embeddings/similarity.
- Cross-profile behavior check: same text compression output shape, profile-only
  admissibility differences.

## 2. Planned Artifacts
- `docs/planning/compression_engine.md` (domain-neutral engine spec)
- `docs/planning/profile_contracts.md` (SL/SB/infra profile boundaries)
- `docs/planning/profile_lint_rules.md` (forbidden axes/groups per profile)
- `docs/planning/cross_profile_safety_tests.md` (determinism + admissibility)
