# Profile Contracts

Status: draft (2026-03-04).

Profile contracts define **admissibility boundaries** for a shared compression
engine. Profiles may only accept/reject overlays; they must not alter the
canonical token stream or span anchoring.

Profiles:
- `SL`: legal/norm admissibility boundaries
- `SB`: state/lifecycle/adapter admissibility boundaries
- `infra`: systems/ops admissibility boundaries

References:
- `docs/planning/compression_engine.md`
- `docs/planning/cross_profile_safety_tests.md`

## Invariants (All Profiles)
1. Canonical text is immutable.
2. Tokenization is deterministic and profile-independent.
3. Spans are identical across profiles for a given input.
4. Profiles may only filter overlays/groups/axes.

## Admissibility Scope (High-Level)
Profiles may define:
- Allowed group IDs
- Allowed axis IDs + values
- Allowed overlay IDs and labels
- Lint rules for rejections or warnings

Profiles may not define:
- Alternative tokenization rules
- Alternative span anchoring
- Profile-specific overlay generation that is not span-anchored

## Open Items (To Be Filled)
- SL allow/deny sets (groups, axes, overlays)
- SB allow/deny sets
- infra allow/deny sets
- Shared lint severity thresholds
