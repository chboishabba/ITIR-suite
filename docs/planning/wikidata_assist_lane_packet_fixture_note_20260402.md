# Assist Lane Packet Fixture Note

Date: 2026-04-02

The assist lane currently hosts reviewer packets that mimic Nat field names without running Nat’s migration or completion work. This note defines the smallest planned artifact that keeps reviewers honest about that reuse.

## Scope

- Record one reviewer-focused fixture per disjointness case, keeping the same `qualifier_reference_index` and `reviewer_prompt` semantics as Nat.
- Each fixture documents which Nat split-plan or migration-plan branch it would touch, but the assist lane simply flags the case as `promotion_guard: hold` until coverage broadens.
- Avoid adding completion or automation metadata; the fixture is purely for reviewer routing and future coverage tracking.

## Minimal Artifact Layout

1. Case identifier (e.g., `disjointness_p2738_mack_group`) and lane assigned (`assist-reviewer`).
2. Fields that reuse Nat grammar items: `case_list` with properties, `culprit_summary`, `qualifier_reference_index`, and `reviewer_prompt` text.
3. A short statement of why this case is disjoint (e.g., subsets of subclass or P2738-specific context) so reviewers can gauge coverage without claiming Nat parity.

## Next Review Steps

- Capture each new fixture in `tests/fixtures/wikidata` as a lightweight JSON or markdown summary so reviewers can see what data the packet uses and how it maps back to Nat’s grammar.
- Reference this note when evaluating whether a new packet moves the milestone beyond `5 / 7`, keeping the assist lane nonblocking.
- Log any qualifier/reference mapping gaps here so follow-up packets track them explicitly.
