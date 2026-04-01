# Wiki Revision Monitor Provenance Path Boundary 2026-04-01

## Purpose

Resolve the last revision-monitor contract ambiguity after the SQLite-first and
no-routine-JSON contraction work.

The question is not whether the lane still has data. It is whether any
remaining local path fields should still be treated as canonical operational
state.

## Decision

Revision-monitor truth remains:

- SQLite read models
- logical query payloads derived from those read models

Local artifact paths are not truth.

If a field exists only to point at a local snapshot, timeline, or other
artifact file, it should be treated as one of:

- transient build input
- provenance-only metadata
- explicit export metadata

It should not be treated as semantic identity or canonical operational state.

## Provenance posture

The trusted sharing shape is:

- logical artifact identity
- artifact revision
- content digest
- sink refs
- acknowledgement / receipt

This follows the existing cross-repo contract notes:

- sink refs attach to a logical artifact and do not define identity
- hosted HF/IPFS claims require stable acknowledgement plus read-after-write
  verification
- `ZOS` is not the owner of truth, mutable workspace state, or observer memory

So for revision-monitor outputs:

- keep truth in SQLite
- keep query surfaces logical
- keep human-facing artifacts on-demand rather than routine sidecars
- allow optional HF/IPFS/ERDFA/ZOS persistence outside the canonical local
  store when another system wants to publish or persist

## Anti-gaming note

Content-addressing alone is not the full trust model.

In particular:

- IPFS CID alone is not sufficient semantic identity
- sink path or hosted location alone is not sufficient semantic identity
- digest/cid without artifact revision and acknowledgement semantics is too weak
  for the full provenance claim

This is why the canonical posture remains:

- logical artifact id/revision first
- sink refs second
- receipts / acknowledgements for hosted claims

## Revision-monitor implication

The remaining local path fields such as:

- `snapshot_path`
- `timeline_path`
- `aoo_path`
- `out_dir`

should not survive as ordinary runtime contract unless a concrete downstream
consumer truly needs them.

If they survive temporarily, they should be documented as provenance-only or
transient implementation residue, not truth.

## Next implementation slice

Do not widen the lane again.

The next safe implementation slice is only:

- remove any remaining local path fields that still masquerade as canonical
  state
- or explicitly relabel the unavoidable ones as provenance-only / temporary

No new routine JSON report/export path should be introduced.
