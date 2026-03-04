# Cross-Profile Safety Tests

Status: draft (2026-03-04).

These tests ensure upgrades do not regress determinism, reversibility, or
profile isolation while the compression engine evolves.

References:
- `docs/planning/compression_engine.md`
- `docs/planning/profile_contracts.md`

## Test Fixtures (Shared Inputs)
1. **Basic text**: ASCII sentence with punctuation.
2. **Mixed unicode**: non-ASCII letters + punctuation + symbols.
3. **Numeric-heavy**: digits + separators + units.
4. **Ambiguous spans**: repeated substrings to validate span anchoring.

## Required Tests (All Profiles)
1. **Deterministic tokens**
   - Same input bytes + same engine version => identical token stream and spans.
2. **Span integrity**
   - All spans map to non-empty slices of the original text.
3. **Reversibility**
   - Removing overlays yields byte-equal canonical text.
4. **Overlay non-inventive**
   - Overlays do not introduce characters not present in source.
5. **Stable ordering**
   - Overlay ordering is stable across runs.

## Profile Isolation Tests
1. **Token stream invariance**
   - SL/SB/infra must produce identical tokens for the same input.
2. **Span invariance**
   - Spans are identical across profiles for the same input.
3. **Overlay admissibility deltas only**
   - Differences are limited to overlay acceptance/rejection.

## Allowed Differences (Explicit)
- Profiles may reject overlays/groups/axes based on admissibility.
- Profiles may add profile-specific lint warnings.

## Forbidden Differences
- Tokenization differences across profiles.
- Span changes across profiles.
- Unanchored or generated content.
