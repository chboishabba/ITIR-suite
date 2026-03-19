# Casey Git Clone SQLite Runtime Decision (2026-03-19)

## Decision
Use a Casey-owned SQLite runtime store as the first mutable-state backend for
the local Casey testbed.

## Why
- Casey now needs a small but durable state backend for:
  - current tree head
  - file-version/blob references
  - workspace selections
  - build snapshots
- The testbed goal is to make Casey's superposition model inspectable and
  replayable without inventing a network protocol or filesystem object store
  first.
- SQLite is sufficient for:
  - deterministic local state
  - simple temp-db tests
  - CLI-driven end-to-end walkthroughs
  - additive persistence without changing git workflows for this repo

## Boundaries
- This runtime is Casey-owned mutable state.
- It is distinct from the observer ledgers used for downstream overlays/refs.
- It does not imply that Casey should become SQL-first for every future
  deployment shape; it is the first bounded runtime decision for the local
  prototype.

## What this enables now
- local `init / workspace create / publish / sync / collapse / build`
- two-workspace divergence walkthroughs
- deterministic runtime reloads in tests

## What remains out of scope
- git-backed persistence
- networked multi-user sync protocol
- direct StatiBaker ownership of Casey runtime state
