# FriendlyJordies Narrative Validation And Competing Narratives (2026-03-09)

## Purpose
Define the next bounded transcript/narrative proving case for ITIR + SensibLaw:

- public-media narrative validation from a dropped URL or transcript source
- comparison of two competing narratives without collapsing them into one story
- explicit followthrough from the current bounded proposition-layer v1 into
  cited holdings, attribution wrappers, and proposition-to-proposition
  comparison

## Public Test Case
Use **FriendlyJordies** as the named public-figure/media-source proving case.

Why this case is useful:
- the source is public and reproducible
- the user story is not "is he trustworthy?" in the abstract
- the user wants to know whether a media narrative is internally consistent,
  externally corroborated, selectively framed, contradicted, or still
  unresolved

Boundary:
- this is a public-figure test case and can be named in repo docs
- private chat-derived examples should stay generalized or local-only

## User Story A: Media Narrative Validation
Future flow:
1. user drops a media URL into the ingress hub
2. ITIR ingests transcript/media text and source metadata
3. the normal narrative pipeline extracts facts, propositions, and narrative
   flow
4. SensibLaw shows:
   - sourced propositions
   - unsupported rhetoric
   - internal consistency issues
   - externally corroborated or contradicted claims
   - explicit abstentions where support is insufficient

Review posture:
- no truth score
- no hidden verdict
- no web material treated as canonical truth
- external sources are corroboration lanes with explicit receipts

## User Story B: Competing Narratives
Target SL use case:
- a lawyer, reviewer, or investigator has two competing narratives
- they want to see where the narratives overlap, where they diverge, and what
  each claim is resting on

Required comparison output:
- shared facts/propositions
- source-only facts/propositions
- conflicting predicates or targets
- chain / reasoning-flow differences
- source-local receipts for every compared item

Non-goal:
- do not silently merge narrative variants into one canonical story
- do not collapse disagreement into a premature verdict

## Corroboration Posture
Wiki, Wikidata, and later web search should be used as downstream
corroboration/support lanes, not as canonical truth sources.

This means:
- they may strengthen or weaken confidence in extracted propositions
- they may supply candidate entities, authorities, and follow-up sources
- they must remain explicitly cited and reviewable

Future `sl-reasoner` posture:
- may suggest search terms or candidate external authorities
- may propose which parts of a narrative need checking
- must not silently author canonical facts or canonical propositions

## Immediate Corpus / Fixture Direction
The next bounded corpus fixture should be:
- URL or transcript based
- reproducible
- public
- suitable for proposition extraction, attribution, and comparison

FriendlyJordies is the first named public case for this lane.

Current first slice now implemented:
- checked-in public demo fixture:
  `SensibLaw/demo/narrative/friendlyjordies_demo.json`
- producer-owned comparison entrypoint:
  `SensibLaw/scripts/narrative_compare.py`
- dedicated review surface:
  `/graphs/narrative-compare`

Current boundary:
- fixture-first, not URL-ingress-first
- read-only comparison workbench
- external corroboration remains explicit and bounded

## Proposition Graph Followthrough
The current proposition-layer v1 is additive, HCA-first, and strongest for:
- factual proposition scaffolding
- `... against ...` reasoning idioms
- proposition-scoped negation rendered as `does_not_negate`

The next widening step should add:
- cited holdings such as `X held that ...`
- attribution wrappers such as `appellant submits that ...`
- current-speaker vs cited-authority separation
- proposition links like:
  - `asserts`
  - `attributes_to`
  - `supports`
  - `undermines`
  - `cites`

Canonical storage decision remains:
- `predicate_key`
- scoped negation / stance metadata
- typed proposition arguments and proposition links

Operator syntax like `!negate` can still exist as display sugar, but it should
not become canonical storage.

Implemented bounded widening in the first slice:
- attribution wrappers for `said/argued/submitted/reported/held/showed that`
- proposition link `attributes_to`
- shared-vs-disputed proposition comparison over the same source-agnostic
  report path

Still pending:
- richer cited-authority subgroup handling such as `majority in Lepore`
- broader proposition-link families beyond `attributes_to`
- ingress-hub URL/media fetch and transcript normalization

## Privacy Rule
- public-figure and public-media examples may be named
- private or family-style chat examples should not become concrete repo-facing
  examples with identifying detail
- local archive material can still inform planning and local experiments where
  retention/redaction rules allow it

## Archive Notes
Relevant thread metadata used for this planning pass:
- `Climate Change Politics AU`
  - online UUID: `69ac40e0-0cfc-839b-b2a8-0de3019379a9`
  - source used: `web`
  - planning takeaway: public-media narrative validation and framing/corroboration
- `Uncle's Conviction Inquiry`
  - online UUID: `6949fb78-4688-8320-9ca9-03a65efaf711`
  - source used: `web`
  - planning takeaway: disputed-record narrative design pressure; keep repo
    examples generalized
- `Bondi shooter neo-Nazi link`
  - online UUID: `6940997c-0784-8324-94ae-2de2f0c34947`
  - source used: `web`
  - planning takeaway: attribution, correction loops, and proposition-layer
    comparison matter more than rhetorical summary

Operational note:
- broad local archive FTS analysis is currently degraded because the chat
  archive reports `sqlite3.DatabaseError: database disk image is malformed`
  in cross-thread analysis mode; exact lookups and direct web-thread viewing
  were still usable for this pass
