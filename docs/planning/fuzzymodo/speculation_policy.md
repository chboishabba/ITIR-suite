# Fuzzymodo Speculation Policy (Draft v0.1)

## Purpose
Define how Fuzzymodo explores risk hypotheses without treating speculative
results as committed truth.

## Core Rules
- Explore one dominant hypothesis deeply before opening broad alternates.
- Keep speculative outcomes in a normative buffer until explicit approval.
- Support rollback/flush when evidence invalidates a branch.
- Preserve branch artifacts for audit, even when rejected.

## Decision Lifecycle
1. `proposed`: branch created with score/cost metadata.
2. `running`: branch is under active evaluation.
3. `buffered`: branch completed; waiting for human retirement decision.
4. `approved`: branch can produce normative effects.
5. `rejected`: branch is flushed from active path but remains inspectable.

## Determinism Constraints
- Dominant branch selection is stable for identical score/cost inputs.
- Branch IDs and decision records use canonical payload hashing.
- State transitions are explicit and monotonic (`approved`/`rejected` terminal).

## Non-goals
- Automatic normative commits without human approval.
- Exhaustive exploration of all branch combinations.
