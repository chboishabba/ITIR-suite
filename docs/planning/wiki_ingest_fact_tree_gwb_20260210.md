# Wikipedia → Fact Tree Intake (George W. Bush) — Plan (2026-02-10)

## Goal
Turn a small set of Wikipedia pages into a reviewable “fact tree” for SensibLaw/ITIR without introducing normative claims. Start with:
- https://en.wikipedia.org/wiki/Presidency_of_George_W._Bush
- https://en.wikipedia.org/wiki/Early_life_of_George_W._Bush
- https://en.wikipedia.org/wiki/Public_image_of_George_W._Bush
- https://simple.wikipedia.org/wiki/George_W._Bush

## Store targets
- **External refs**: anchor the subject to DBpedia `external_id` (full URI) via `actor_external_refs` (or concept if treating the office as a concept). Provider `dbpedia`; URI e.g. `http://dbpedia.org/resource/George_W._Bush`.
- **Content facts**: ingest as structured statements in the *seed envelope* (`{"concepts": [...], "relations": []}`) for later load into core storage / graph export. Prefer `data/concepts/wiki_gwb_*.json`.
- **Provenance**: keep page URL + revision id + access timestamp on each fact node so we can re-extract deterministically.

## How This Connects To Investigation Graphs
This intake is upstream substrate, not "the investigation":
- seed candidate actors/concepts
- preserve provenance (page, revision ID, section)
- generate pointer trails for what to ingest next (primary sources)

SL ingest boundaries for investigations (norm/authority vs pointers) and a working
graph taxonomy are captured in:
- `docs/planning/bush_investigation_graphs_sl_io_context_20260210.md`

## Extraction shape (fact tree)
Root: `George W. Bush` (actor).
- Branches by page/topic: `Early life`, `Presidency`, `Public image`, `Overview (Simple)`.
- Leaves are factual claims distilled to subject–predicate–object with light typing:
  - Subject: either the root actor or a subnode (e.g., `Bush administration`, `Iraq War` policy decision).
  - Predicate: controlled verbs (e.g., `held_office`, `initiated`, `signed`, `approval_rating`, `born_in`, `educated_at`).
  - Object: text or normalized entity; if Wikipedia link resolves to a DBpedia URI, attach `external_id`.
- Each fact carries: `source_url`, `rev_id`, `page_section`, `confidence` (human/edit review placeholder), `extracted_at`.

## Minimal pipeline (phase 1 — manual review friendly)
1) **Fetch content**: pull via pywikibot when available; otherwise use MediaWiki API.
   Store `revid` + provenance alongside the content so extraction is revision-locked.
2) **Chunk & filter**: split by sections/paragraphs; drop boxes/nav; keep lead + main content.
3) **Claim extraction**: rule-based heuristics first (sentences with dates, verbs indicating office/action), optionally LLM-assisted summarization with *no tool calls*; produce candidate triples.
4) **Normalize entities**: for linked titles, derive DBpedia URI (`http://dbpedia.org/resource/<Title_with_spaces_as_underscores>`); fall back to label text if unresolved.
5) **Assemble seed envelope**: write `data/concepts/wiki_gwb_v1.json` with `concepts` (nodes) + `relations` (edges/facts) and provenance metadata.
   - planned output; not yet created
6) **External ref batch**: emit `data/external_refs/wiki_gwb_dbpedia.json` with `actor_external_refs` rows (provider `dbpedia`, full URI, notes).
   - planned output; not yet created
7) **Upsert**: use `python -m cli ontology external-refs-upsert --db <path> --file data/external_refs/wiki_gwb_dbpedia.json` after curator review.
8) **Review loop**: load seed into graph/CLI inspector; mark low-confidence facts for human edit; re-export graph.

## Candidate entities (new: title ranking stage)
Before doing any claim extraction, we should rank the snapshot’s already-captured `links` into a
curation-friendly candidate list:
- Tool: `SensibLaw/scripts/wiki_candidates_extract.py`
- Inputs: snapshot JSONs under `SensibLaw/.cache_local/wiki_snapshots*/`
- Output: `SensibLaw/.cache_local/wiki_candidates_gwb.json` (gitignored)

This list is upstream substrate for:
- actor identification (who should exist as `actors(kind,label)` now)
- external ID anchoring (which candidates get DBpedia lookup + curated `actor_external_refs`)
- graph views: candidate nodes that later get typed/linked as norms/authority/events/claims in derived graphs

## Visual graph (pre-trim, pre-commit)
Before trimming or queueing DBpedia lookups, render a visual graph of the raw candidate set
(including event-heavy skew) so we can reason about what the extraction is actually doing.

- Tool: `SensibLaw/scripts/wiki_candidates_graphviz.py`
- Input: `SensibLaw/.cache_local/wiki_candidates_gwb.json`
- Output (gitignored):
  - `SensibLaw/.cache_local/wiki_candidates_gwb.dot`
  - `SensibLaw/.cache_local/wiki_candidates_gwb.svg` (if Graphviz `dot` is available)

Fallback (when Graphviz `dot` is not available in the runtime environment):
- `itir-svelte` renders an in-app bipartite visualization from the same artifact:
  `itir-svelte/src/routes/graphs/wiki-candidates/+page.svelte`

## Guardrails
- External sources are *advisory only*; do not create/override duties/values.
- Keep extraction deterministic: inputs are page + rev_id; store both.
- No live SPARQL dependency at runtime; cache lookups if used.
- Avoid bulk HTML dumps in git; store only structured JSON and small provenance.

## Open questions / choices
- Actor vs concept split: keep `George W. Bush` as `actor`; create concepts for offices/policies (e.g., `PRESIDENCY_GWB_2001_2009`).
- Fact schema: reuse `concepts/relations` seed envelope vs a dedicated “fact tree” table. Proposal: stick to seed envelope to avoid a new schema.
- Confidence/curation: add `confidence` + `review_status` fields to relations? (Requires schema tweak.)
- Derived graph support: decide which "investigation views" we target first (constraint overlay vs narrative vs finance), but keep them as derived outputs over:
  - SL normative/authority graphs (primary sources)
  - SB event/provenance/claim substrates (non-normative)

## Next actions (if we proceed)
- Implement `scripts/wiki_ingest.py` to fetch page + rev_id, chunk, and emit a draft seed + external_ref batch for a given Wikipedia title list (planned script; not yet implemented).
- Add fixtures + tests for deterministic expansion of DBpedia URIs from page titles (spaces/parentheses/Unicode) and provenance capture.
- Wire a small CLI wrapper: `python -m cli wiki ingest --titles <...> --out data/concepts/wiki_gwb_v1.json --rev-lock`.
- Add a curation checklist doc for reviewing extracted facts before upsert.
