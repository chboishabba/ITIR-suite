# Cross-Lane Reusable Surface Priority (2026-04-01)

## Context

Several recent lanes have been productive in isolation:

- wiki revision monitor SQLite/store contraction
- wiki timeline runtime migration to Python
- affidavit normalization
- transcript/AU fact-intake normalization
- Wikidata checked/dense geometry normalization
- reporting/importer normalization

The remaining risk is not just "finish each lane." It is failing to use those
disparate lanes to build the most reusable and generalized suite surfaces.

## Decision

Promote the following as the top architecture execution rule:

- highest-priority work should favor cross-lane reusable, normalized,
  generalized surfaces over lane-local cleanup

This sits above ordinary feature sequencing and should be treated as a
`P-1` / meta-priority governing how `P0` work is chosen.

## Requirement

When multiple candidate tasks exist, prefer the one that:

1. removes duplicated policy across lanes
2. creates one reusable Python-owned owner for canonical behavior
3. reduces the number of separate truth surfaces
4. improves parity across adopters
5. leaves wrappers, routes, and adapters thinner

Do not let local cleanup outrank reusable substrate work unless the local task:

- fixes a correctness bug
- unblocks an operator workflow
- or exposes a hidden canonical rule still in the wrong layer

## Implication

The suite should be steered by a hierarchy like this:

- `P-1`: choose work that builds shared normalized substrate across lanes
- `P0`: execute the highest-leverage canonical Python/store/runtime moves
- `P3`: keep presentation-only cleanup and similar polish as opportunistic work

## Examples

Promote:

- shared read-model owners over blob or artifact-local convenience surfaces
- shared runtime/query owners over route-local resolver policy
- shared policy modules over builder-local duplicated heuristics
- shared cross-lane geometry over per-lane reimplementation

Demote:

- route-shell splitting once semantics have already moved
- local file cleanup that does not improve shared ownership
- lane-specific rearrangement with no generalized contract

## Governance

- ITIL:
  choose changes by service-level leverage, not by nearest editable file
- ISO 9000:
  give canonical behavior one owner and make reuse/promotion criteria explicit
- Six Sigma:
  prioritize reduction of cross-lane variation and duplicated process logic
- C4:
  keep canonical behavior in reusable components/containers and leave
  presentation/adapters as thin shells

## Promotion Rule

Before promoting a task, ask:

- does this create or strengthen a reusable shared owner?
- does it collapse duplicate lane logic?
- does it reduce the number of authority surfaces?

If not, it should not outrank current cross-lane normalization work.
