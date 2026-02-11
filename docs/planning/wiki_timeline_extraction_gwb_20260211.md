# Wikipedia -> Event Timeline Extraction (GWB) (2026-02-11)

## Goal
Extract a reviewable, non-authoritative **event timeline** from the main Wikipedia page
(`George W. Bush`) as upstream substrate for SB-style event graphs and later derived overlays.

This addresses the "wide net" issue (many irrelevant links/categories) by switching from:
- "all outgoing links" (broad discovery)
to:
- "date-anchored event candidates from prose" (timeline scaffolding)

Operational note:
- Category links (and bottom-of-page nav categories) are useful for discovery but frequently introduce
  low-relevance historical neighbors (e.g., older conventions/figures referenced in one-off context
  paragraphs). Treat category-derived candidates as a separate/lower-weight lane than prose-derived
  timeline candidates.

## Inputs
Revision-locked snapshot JSON (gitignored):
- `SensibLaw/.cache_local/wiki_snapshots_pywikibot/enwiki__George_W._Bush__revid_*.json`

## Output artifact (gitignored)
Timeline candidate set:
- `SensibLaw/.cache_local/wiki_timeline_gwb.json`

This file is **not** an investigation graph. It is a curation-time artifact that captures:
- event candidate text
- extracted date anchors (year/month/day when explicit)
- wikilinks present in that candidate (identity glue)
- section label (best-effort)
- provenance: source_url + revid + snapshot_path

## Known extraction pitfalls (and fixes)
- **Sentence splitting vs abbreviations:** naive splitting on punctuation+whitespace can truncate event
  text at abbreviations (e.g. `U.S.`, `George W. Bush`). Fix: protect common abbreviations and
  middle-initial name forms during splitting (or use a small state-machine splitter).
- **Citation tails surviving strip:** some sentence tails retain citation-style fragments (e.g.
  `projects,Bush, George W.` or `exam.Rutenberg, Jim (May 17, 2004)`). Fix: apply deterministic
  sentence cleanup before anchor parsing:
  - recover missing punctuation spacing (`exam.Rutenberg` -> `exam. Rutenberg`)
  - strip trailing author/date citation tails
- **Template separators:** some Wikipedia templates are semantic separators (e.g. `{{snd}}`) and
  should be rendered as punctuation/whitespace before stripping templates; otherwise tokens can
  collapse (`Cheney{{snd}}a` -> `Cheneya`). Fix: pre-replace a small allowlist of separator templates
  with `" - "` (or similar) before `strip_code()`.
- **AAO purpose extraction:** a naive `"to ..."` purpose rule misfires for phrases like "gave birth
  to ...". Fix: treat purpose only when `"to"` is the marker of an *infinitival verb clause* (i.e.
  `"to" -> VERB` attachment), not a preposition attaching a noun phrase. This is implemented as a
  deterministic dependency-parse gate (structure only; no NER/meaning), not a noun allowlist.
- **AAO action coverage:** an explicit verb-pattern allowlist will miss many common event verbs
  (`nominated`, `urged`, `intensified`, etc.). Fix: expand the allowlist and add a deterministic
  fallback that chooses a verb-like token when no explicit pattern matches; label this with a warning
  (`fallback_action`) so it stays reviewable.
- **AAO subject overreach:** treating all person-like mentions as sentence subjects causes false
  co-subjects (`Jenna Bush Hager` on birth events, `Joe Biden` in vote objects). Fix: per-step
  subject refinement from dependency attachments (`nsubj`/`nsubjpass`) with deterministic fallback.
- **AAO chain/nesting visibility:** purpose clauses and multi-verb sentences need explicit sequence
  structure for graph traversal. Fix: emit event-local `chains[]` metadata and optional derived
  purpose steps (e.g. `suspended -> take physical exam`) without causal claims.
- **Root surname collisions:** mapping `Bush` -> root actor should only fire for standalone surname
  references, not for `Laura Bush`/`Barbara Bush` mentions. Fix: suppress root mapping when the
  surname is part of a two-token name pattern in the same sentence.

## AAO expansion view (sentence-local, non-causal)
After the timeline substrate exists, we generate a second artifact that expands each event into a
small actor/action/object mini-graph:
- Tool: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
- Output: `SensibLaw/.cache_local/wiki_timeline_gwb_aoo.json`

Notes:
- Wikilinks are used as object/identity glue where present.
- A small deterministic surface-object lane may add unlinked load-bearing phrases (e.g. `the war`,
  `Taliban and al-Qaeda leaders`) so event-heavy AAO views are less lossy.
- A deterministic dependency-object fallback lane may add unlinked object phrases (e.g. `a scheduled
  physical exam`, `a Taurus .38 Special revolver`) when wikilinks are absent.
- Non-wikilink objects may carry resolver hints (`exact`/`near`) against sentence links, paragraph
  links, and candidate titles for quick curation checks.
- Actor resolution is heuristic and explicitly labeled (root surname, alias map, request pattern).
- Step subjects are dependency-refined and may differ from the event actor inventory.
- This does not assert causality; it is sentence-local structure for later curation.
- Object admissibility + truth/view boundary is governed by:
  - `docs/planning/oac_object_admissibility_contract_v1_20260211.md`

Rendering:
- `itir-svelte` route: `/graphs/wiki-timeline-aoo`
- `itir-svelte` route: `/graphs/wiki-timeline-aoo-all` (whole-article combined view)

## Non-goals
- No causal claims ("therefore", "because") beyond sentence-local extraction.
- No authority claims (Wikipedia is index + disambiguation aid).
- No auto-expansion via categories or citation graphs.
- No promotion into SL normative/authority graphs.

## Rendering
We render the timeline in `itir-svelte` as a graph view:
- route: `/graphs/wiki-timeline`
- it reads `SensibLaw/.cache_local/wiki_timeline_gwb.json`
- view is explicitly "pre-graph substrate" (no SL/SB commitments).

## AAO rendering variants (UI, not extraction)
The AAO view is meant to support multiple *rendering* variants without changing the underlying
extraction artifact.

Planned / in-progress variants:
- **Time granularity split nodes:** render time as a chain of nodes (`Year -> Month -> Day`) and connect
  the most-specific available node to the event action. This should be a UI toggle:
  - `auto` (use anchor precision)
  - `year`
  - `month`
  - `day`

Notes:
- This is explicitly a visualization choice. It does not change meaning or add causality.
- It answers the concrete “January -> 2010 -> …” view request while keeping extraction sentence-local.

## Whole-article combined graph (UI)
In addition to the per-event AAO mini-graph, we want a whole-article combined visualization that can be
event-heavy without pre-trimming.

Intended characteristics:
- Uses `wiki_timeline_gwb_aoo.json` as-is (no new extraction pass).
- Builds a combined graph across many events (default: first ~80).
- Prioritizes inspectability over “perfect layout”: pan/zoom + optional caps.
- Remains non-causal and non-authoritative.

Implementation note:
- Prefer the existing in-app Svelte renderers (no Graphviz dependency) so the view works in the same UI
  surface as SB and doesn’t require external tooling.

## Status note (hardcoding)
Nothing in the UI is hardcoded to GWB-specific content; what looks “hand-authored” is generated from
the JSON artifact, with the only fixed part being the extraction heuristics (e.g., requester patterns,
alias resolution, and verb/purpose matching).
