# Phase 13: SensibLaw S7–S9 - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

<vision>
## How This Should Work

The next three sprints decide what SensibLaw becomes. S7 makes interpretive
artifacts span-traceable and regeneration-safe. S8 exposes cross-document
relationships without asserting meaning or precedence. S9 makes the system
legible to humans via read-only interfaces that reinforce provenance and
boundaries. Reasoning remains gated and explicitly deferred.
</vision>

<essential>
## What Must Be Nailed

- Every interpretive artifact is traceable to canonical text via TextSpan.
- Cross-document topology is descriptive only and span-derived.
- Human interfaces are read-only and trust-first.
</essential>

<boundaries>
## What's Out of Scope

- Any reasoning or compliance judgments.
- Ontology expansion or identity mutation.
- UI controls that can mutate meaning or payloads.
</boundaries>

<specifics>
## Specific Ideas

- TextSpan contract: `revision_id + start/end offsets` with CST slice equality.
- Promotion gates require spans and block on SpanSignalHypotheses.
- Graph projections with typed edges and deterministic ordering.
- UI span inspector and obligation explorer with fixture-mode tests.
</specifics>

<notes>
## Additional Context

Keep exploratory human cognition explicitly marked and non-authoritative. The
system should be inspectable without being prescriptive.
</notes>

---

*Phase: 13-sensiblaw-s7-9*
*Context gathered: 2026-02-06*
