# Phase 16: Fuzzymodo Selector DSL - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<vision>
## How This Should Work

Fuzzymodo treats odd behavior as potentially intentional, then classifies whether
that behavior is safe, needs guardrails, or is weaponizable. The selector DSL is
the executable scope layer that binds structural facts, runtime evidence,
attacker model, and human policy decisions without inventing meaning.
</vision>

<essential>
## What Must Be Nailed

- Selector evaluation is deterministic and graph-scoped.
- Normative decisions remain human-authored and diffable.
- Quirk handling defaults to containment, not destructive behavior rewrites.
</essential>

<boundaries>
## What's Out of Scope

- Free-form natural-language selectors.
- Auto-generated policy decisions from model guesses.
- Silent scope widening or implicit OR semantics.
</boundaries>

<specifics>
## Specific Ideas

- Selector shape: `all_of` default, explicit `any_of` and `not`.
- Fixed field catalogs per graph layer (structural, execution, build, threat,
  ecosystem, normative, timeline).
- NormConstraint objects pair selector + assertion + effect + provenance.
- Canonical serialization and hashing for replay-safe evaluations.
</specifics>

<notes>
## Additional Context

Source conversation: `698686e2-6e48-839e-ad0f-91e6fa4697f8`
(`OSS-Fuzz Bug Detection`), latest assistant timestamp
`2026-02-07T02:27:40.229711Z`.
</notes>

---

*Phase: 16-fuzzymodo-selector-dsl*
*Context gathered: 2026-02-07*
