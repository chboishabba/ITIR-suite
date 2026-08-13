# Bush Investigation Context: SL I/O + Graph Taxonomy (2026-02-10)

## Canonical Thread (online ID)
- ChatGPT conversation UUID: `698ac6a3-c56c-839a-b855-47822ac1a901`
- Title (from web fallback): `Investigations into Bush Presidency`

This thread is relevant because it spells out (a) what an "investigation"
means in ITIR terms, (b) strict SL ingest boundaries, and (c) the types of
graphs we should expect to build as derived views.

## Investigation, ITIR-native (high-level)
An ITIR investigation is not "write an argument"; it is:
- ingest heterogeneous artifacts
- preserve provenance + time + jurisdiction
- separate `fact` vs `assertion` vs `interpretation` vs `norm`
- allow multiple downstream lenses without rewriting history

Suite flow (conceptual):
`RAW MATERIALS -> SL (norm/authority surfaces) -> SB (event/temporal distillation) -> derived views`

## SL Ingest Boundaries (critical)
SL should directly ingest:
- primary legal texts (statutes, treaties, executive instruments)
- official interpretations (OLC/DOJ opinions), court rulings, IG reports
- authority/delegation mappings (office -> authority -> time)

SL should not ingest as authoritative truth:
- news articles (secondary indices/pointers)
- testimony transcripts (ingest as *assertions*, not facts)
- motive speculation / psychological claims
- casual internal comms unless policy/authority-bearing

Operational consequence for Wikipedia:
- Wikipedia pages are **not** SL sources.
- They are seed surfaces for:
  - discovery (what to fetch next)
  - candidate entities (actors/concepts)
  - pointer trails (citations, named documents, timelines)

Candidate entity extraction (curation-time helper):
- `SensibLaw/scripts/wiki_candidates_extract.py` ranks snapshot `links` into a reviewable candidate list.
- Output: `SensibLaw/.cache_local/wiki_candidates_gwb.json` (gitignored).

## Graphs We Should Expect (and where they live)
SL-native (authoritative structure):
- Normative graph (rules + relationships: `supersedes`, `narrows`, `conflicts_with`)
- Interpretation lattice (competing interpretations preserved, time-scoped)
- Authority/delegation graph (who could authorize what, when)

SB / evidence layer (non-normative substrate):
- Event/action graph (what happened, as asserted/confirmed/disputed)
- Evidence provenance graph (artifact lineage, authentication status)
- Claim/assertion graph (who said what, where/when, under what forum)

Derived overlays (views, not stored as truth):
- Cross-layer constraint graph: SL constraints overlaid on SB events ("under which regime")
- Narrative graph: editorial arrangement declared explicitly (never authoritative)
- Financial graph: flows of value (intent stays hypothesis unless proven elsewhere)

## How This Updates The Bush Wikipedia Intake Plan
We should keep the current plan focused on:
- revision-locked pulls + category traversal for discovery
- actor + concept seeding with provenance
- emitting reviewable "fact tree" drafts

But we should treat the "fact tree" as upstream substrate for the graph family above:
- Wikipedia intake populates candidate nodes + pointer edges.
- A later pass ingests primary sources into SL to build the normative/authority graphs.
- SB consumes SL outputs as constraints (not verdicts) and builds time-scoped event views.
