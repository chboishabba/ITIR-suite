# Wikipedia Connector (Structured Pull + Category Traversal) (2026-02-10)

## Purpose
We want **structured, revision-locked access** to Wikipedia content so we can:
- build *reviewable* “fact tree” drafts (not freeform dumps)
- attach stable provenance (page URL + `revid` + `fetched_at`)
- use **category traversal** as a discovery tool (what else should we ingest?)

This is ingestion scaffolding for SL/ITIR ontology enrichment, not SB.

## Non-goals / guardrails
- Do not treat Wikipedia/DBpedia as normative truth.
- Do not store bulk HTML dumps in git.
- Do not introduce runtime dependencies on flaky public endpoints (SPARQL, etc.).
- Keep everything auditable: pull → snapshot → curate → upsert.

## Connector options
We prefer **pywikibot** long-term (more ergonomic + supports category walking),
but we keep a **MediaWiki API fallback** so ingestion works even when
dependencies are unavailable in the current `.venv`.

### MediaWiki API (baseline)
- Endpoint: `https://<host>/w/api.php` (e.g. `en.wikipedia.org`)
- Fetch:
  - `revisions` (wikitext + `revid` + timestamp)
  - `categories` (page categories)
  - `links` (internal link titles, capped)
- Category traversal:
  - `list=categorymembers` for each category title, with continuation support
  - strict caps (depth, members-per-category, namespaces) to prevent explosion

### pywikibot (preferred driver)
Use when available in the active environment:
- Simple `Page.text` access (wikitext)
- `Page.latest_revision_id` and timestamps
- Category traversal via category pages and members

Login/account is **not required** for read-only pulls; it is only needed for
edits or to negotiate higher rate limits.

Implementation note: the pull helper supports `--driver auto|api|pywikibot` so
we can prefer pywikibot without making ingestion brittle when the dependency is
missing in a given `.venv`.

Operational note:
- `SensibLaw/scripts/wiki_pull_api.py` keeps stdout machine-readable JSON, but now emits
  per-title progress to stderr so 20-60s network pulls do not look like a hang.
- The stdout payload includes environment sanity metadata: `python`, `driver_requested`,
  and `drivers_used`.
- HCA adapter events (`citations[]` and `sl_references[]`) now emit `wiki_connector`
  follow hints that point to this script with preferred `pywikibot` driver; this keeps
  citation follow-up deterministic and scriptable.

## Artifact policy (avoid committing data)
All raw pulls land under a gitignored local cache:
- `SensibLaw/.cache_local/wiki_snapshots/`

Snapshots are JSON and include the full provenance and (optionally) wikitext.

## George W. Bush intake (seed set)
Initial URLs:
- `https://en.wikipedia.org/wiki/Presidency_of_George_W._Bush`
- `https://en.wikipedia.org/wiki/Early_life_of_George_W._Bush`
- `https://en.wikipedia.org/wiki/Public_image_of_George_W._Bush`
- `https://simple.wikipedia.org/wiki/George_W._Bush`

We also likely want the English biography page as the *root anchor*:
- `https://en.wikipedia.org/wiki/George_W._Bush`

## Actor identification + external IDs
Target identity posture:
- Create a canonical internal actor row (ontology DB): `kind=person`, `label=George W. Bush`.
- Attach external IDs as *advisory links*:
  - DBpedia: `provider=dbpedia`, `external_id` stored as **full URI** (Option 1).
  - (Optional) Wikidata later as `Q...`.

Storage target:
- ontology DB: `actor_external_refs` in `SensibLaw/.cache_local/sensiblaw_ontology.sqlite`
  (or whichever SQLite path is designated for the environment).

## Output shape (what the connector produces)
1. **Snapshot JSONs** (gitignored)
   - `wiki`: `enwiki` / `simplewiki`
   - `title`, `pageid`, `revid`, `rev_timestamp`
   - `source_url`, `api_url`, `fetched_at`
   - `wikitext` (optional)
   - `categories` (list of category titles)
   - `links` (list of link titles; capped)
2. **Curatable external-ref batches** (review then upsert)
   - `actor_external_refs` payload compatible with `ontology external-refs-upsert`
3. **(Later) fact-tree seed envelope**
   - `data/concepts/wiki_gwb_v1.json` with extracted claims + provenance

## Next steps
- Implement a minimal pull tool (`SensibLaw/scripts/wiki_pull_api.py`) that:
  - pulls the seed pages
  - records `revid` and metadata
  - optionally performs 1-hop category traversal with strict caps
- Implement a small helper to upsert the root actor into the ontology DB
  (or document the manual SQL/CLI workflow).
- Only after the above: add claim extraction and fact-tree shaping.

## Downstream: Candidate List -> DBpedia Queue (bounded)
After snapshots exist, generate bounded curation artifacts (still pre-graph):
- Candidate extraction: `SensibLaw/scripts/wiki_candidates_extract.py`
- Distribution sanity check: `SensibLaw/scripts/wiki_candidates_distribution_report.py`
- DBpedia lookup queue (bounded, declarative; no recursion): `SensibLaw/scripts/wiki_dbpedia_lookup_queue.py`

DBpedia resolution is identity glue, not evidence, and does not imply inclusion in any investigative graph.

## Visual graph (pre-trim sanity)
Render the raw candidate set as a graph before trimming:
- `SensibLaw/scripts/wiki_candidates_graphviz.py` emits a `.dot` + optional `.svg`
  from the candidate artifact (gitignored outputs).
