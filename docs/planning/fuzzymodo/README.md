# Fuzzymodo Planning Pack

This folder contains the implementation-ready planning artifacts for the
Fuzzymodo selector DSL and norm-constraint workflow.

## Files
- `selector_dsl_spec.md`: syntax, operators, graph-layer field conventions.
- `norm_constraint_spec.md`: norm object model and effect semantics.
- `canonical_hashing.md`: deterministic serialization/hash rules.
- `speculation_policy.md`: speculative branch + normative retirement policy.
- `selector_dsl.schema.json`: structural contract for selector payloads.
- `norm_constraint.schema.json`: structural contract for norm constraints.
- `conversation_step_map.md`: conversation steps mapped to concrete artifacts.
- `fixtures/`: sample selector and norm payloads.

## Intended Build Order
1. Lock schemas.
2. Implement parser + canonicalizer against fixtures.
3. Implement evaluator with graph-scoped clause semantics.
4. Implement norm-constraint invalidation and replay checks.
