# Legal Principles Ingest Bootstrap (AU) (2026-02-11)

## Context
- Robust context fetch (live): `698c1cec-51c0-839a-a81b-c821aa4eabbb`
- Thread title (live): `Browne v Dunn Parsing`
- Load-bearing issue: sentence-local AAO extraction can capture syntax while missing legal procedure semantics (for example, "put to the witness" as a cross-examination speech act).

## Ratified posture from thread
- We do not need "all of law" to begin doctrinal extraction.
- We do need an explicit doctrinal layer (typed procedural primitives) to avoid treating legal idioms as literal actions.
- Bench books are useful as structured doctrine summaries, but not primary authority.
- Primary authorities (cases/statutes) remain the truth anchor for doctrinal primitives.
- Wiki/DBpedia/Wikidata are identity/disambiguation glue, not doctrinal evidence.

## Source set for this bootstrap
User-provided sources (reachability checked on 2026-02-11, all returned HTTP 200):

- Judicial College VIC bench books:
  - `https://judicialcollege.vic.edu.au/bench-books`
  - `https://resources.judicialcollege.vic.edu.au/article/1053858`
- AIJA bench books:
  - `https://aija.org.au/product-category/bench-books/`
  - `https://dfvbenchbook.aija.org.au/article/1085400`
- FWC bench books:
  - `https://www.fwc.gov.au/hearings-decisions/case-law-benchbooks`
  - `https://www.fwc.gov.au/benchbook/unfair-dismissals-benchbook`
  - `https://www.fwc.gov.au/documents/benchbooks/unfair-dismissals-benchbook.pdf`
- Legal corpus directories:
  - `https://www.austlii.edu.au/databases.html`
  - `https://jade.io/`

## Ingest tiers (truth vs support)
1. Primary authority (truth anchor):
- HCA/FCA/state judgments and statutes, preferably via official sources + AustLII links.

2. Structured doctrine guidance (support, non-authoritative):
- Judicial College / AIJA / FWC bench books.
- Use to propose doctrinal primitives and citation targets, not to settle doctrine.

3. Identity/disambiguation support:
- Wikipedia + wiki connector + DBpedia/Wikidata for entity IDs, aliases, and role disambiguation.

## Deterministic ingest contract for this source set
- Search adapters return references only.
- Fetch adapters return bytes + provenance only.
- Parser lanes produce structured artifacts (`document_json`, references, rule atoms).
- AAO/narrative adapters remain observer lanes unless promoted by explicit receipts.
- Citation follow remains bounded (`max_depth`, `max_new_docs`) and citation-driven (no open crawl).

## Pilot target: Browne v Dunn lane
- Build a small doctrinal primitive lane for cross-examination proposition handling:
  - `cross_examination_proposition`
  - `status`: `put` | `not_put`
  - `witness`
  - `proposition`
  - `doctrine_link` (for example `Browne_v_Dunn`)
- Seed from benchbook sections + linked primary authorities.
- Validate by replaying known problematic sentences from current HCA narrative extracts.

## Source integration plan (incremental)
1. Add machine-readable source pack with the exact URLs above and tier labels.
2. Add bounded index pull for benchbook pages:
- collect title, URL, content type, and outbound links to likely authority citations.
3. Feed extracted citation candidates into existing AustLII/JADE/source fetch contract.
4. Run parser lane on fetched artifacts, then emit:
- `citations[]` (hint lane)
- `sl_references[]` (parser-native lane with provenance)
- optional doctrinal primitive candidates.
5. Use wiki connector only for entity identity resolution on extracted actors/concepts.

## Non-goals for this pass
- No open-ended scraping/crawling.
- No model-based semantic inference as truth.
- No replacement of primary legal authority with wiki/benchbook summaries.
- No automatic doctrine promotion without provenance + review gate.
