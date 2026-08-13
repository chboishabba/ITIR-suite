# Norm Constraint Specification (Draft v0.1)

## Object Model
A norm constraint binds a selector to a human-authored assertion and effect.

```yaml
norm_constraint:
  id: NC-parse-text-binary
  dsl_version: "0.1"
  selector: { ... }
  assertion:
    kind: design_intent
    statement: Binary output is intentional in non-network contexts.
  effect:
    mode: prune
    bug_classes: [type_mismatch, encoding_violation]
  provenance:
    decided_by: alice@example.com
    decided_at: 2026-02-07T00:00:00Z
    rationale: Legacy CLI compatibility.
```

## Required Sections
- `id`
- `dsl_version`
- `selector`
- `assertion`
- `effect`
- `provenance`

## Effect Modes (initial)
- `prune`: remove matching candidate branches from review queue.
- `downgrade`: reduce severity by configured level.
- `escalate`: require explicit human approval gate.

## Invalidation Rule
If selector no longer matches current graph facts, constraint is inactive and
must be surfaced as `stale_constraint` in review output.
