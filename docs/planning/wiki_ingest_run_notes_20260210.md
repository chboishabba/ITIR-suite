# Wikipedia Ingest Run Notes (2026-02-10)

## Scope
This note documents what actually happened during the first “Wikipedia -> snapshot -> ontology anchor”
pass for the George W. Bush seed set, including uncertainties and fixes required to make the workflow
reliable and auditable.

This is intentionally operational: what broke, what we changed, what still needs decisions.

## What we pulled (revision-locked snapshots)
Tool: `SensibLaw/scripts/wiki_pull_api.py`

Outputs (gitignored) were written to:
- `SensibLaw/.cache_local/wiki_snapshots/`
- `SensibLaw/.cache_local/wiki_snapshots_pywikibot/` (same titles/revids; pywikibot driver; avoids overwriting earlier root-owned files)

Seed pages:
- enwiki:
  - `George W. Bush`
  - `Presidency of George W. Bush`
  - `Early life of George W. Bush`
  - `Public image of George W. Bush`
- simplewiki:
  - `George W. Bush`

Each snapshot JSON includes `title`, `revid`, `rev_timestamp`, `source_url`, `api_url`/driver marker, and
`fetched_at`. Wikitext is optionally included (we kept it enabled for now because extraction is the next
step).

## Category traversal (discovery)
We ran a capped 1-hop traversal (discovery-only) producing:
- `SensibLaw/.cache_local/wiki_snapshots/enwiki__George_W._Bush__categories.json`

Uncertainty: Wikipedia category graphs can explode. Even “1 hop” produces many categories and each
category can have a huge member set. The traversal is therefore hard-capped and the result is treated
as a suggestion list for the next ingestion batch, not an automated crawl.

Operational fix: we had to add default excludes for obvious maintenance/meta categories (eg `Category:All ...`,
`Category:Wikipedia ...`, `Category:CS1...`) because they are high-volume and low-signal for ontology intake.

## Network/DNS constraint (non-deterministic environment behavior)
We encountered `Temporary failure in name resolution` during MediaWiki API fetches in the default execution
mode. The same commands succeeded only after allowing network access (escalated execution).

Impact:
- The connector must surface clear failure modes for `dns`/`egress` and not silently produce partial artifacts.
- “No network” is a normal deployment mode for us; the workflow must support offline cache replay once a
snapshot exists.

Operational note:
- The pull tool currently emits results only at the end (stdout JSON). When a pull requires network and takes
  ~20-60s, it can look like a hang. We should emit per-title progress to stderr while keeping stdout machine-readable.

Update (2026-02-10):
- `SensibLaw/scripts/wiki_pull_api.py` now emits per-title progress to stderr and includes `python`,
  `driver_requested`, and `drivers_used` in the stdout JSON payload.

## Driver uncertainty (pywikibot vs API)
Intent: prefer `pywikibot` long-term because it has better category traversal ergonomics.

Observed uncertainty:
- In our active `.venv`, `pywikibot` was not importable at least once (`ModuleNotFoundError`), while the user
reported it as installed. This suggests a mismatch between “what is installed” and “which python is running”
or a multi-venv/container boundary.

Mitigation implemented:
- `SensibLaw/scripts/wiki_pull_api.py` supports `--driver auto|api|pywikibot`.
  - `auto`: try importing `pywikibot`; fall back to API if missing.
  - `pywikibot`: fail closed if not importable.

Follow-up (2026-02-10):
- We installed `pywikibot` (and its parser dependency `mwparserfromhell`) into the repo `.venv`
  so `--driver pywikibot` is usable from `.venv/bin/python`.
- The dominant failure mode is still environment egress/DNS: in default sandboxed execution,
  name resolution to `en.wikipedia.org` failed; the same pull succeeded only when outbound
  network access was allowed.

Remaining decision:
- Decide whether we want a pinned dependency policy (single repo-wide `.venv`) or allow per-submodule envs.
  The ingestion tools should not be ambiguous about interpreter selection.

## DBpedia emit-batch cache semantics (bug found + fixed)
During DBpedia curation we discovered a workflow break:
- `SensibLaw/scripts/dbpedia_lookup_api.py` returned early on cache hits and did not honor `--emit-batch`.

Fix implemented:
- `--emit-batch` now works both on cache hits and fresh fetches.

This matters because curation workflows should be repeatable without needing live network calls.

## Actor identification posture (root anchor)
We created a minimal ontology actor row:
- DB: `SensibLaw/.cache_local/sensiblaw_ontology.sqlite` (gitignored)
- Actor: `kind=person`, `label=George W. Bush`

Uncertainty:
- The ontology DB has no uniqueness constraint on `(kind,label)`. For now, we use a conservative “lookup then insert”
policy and treat this as a curation tool, not an extractor.

## External IDs posture (advisory links)
We generated a curated external refs batch (gitignored) anchoring the actor to DBpedia:
- `provider=dbpedia`
- `external_id` stored as full URI (Option 1), e.g. `http://dbpedia.org/resource/George_W._Bush`

Review posture:
- Notes include `curation=UNREVIEWED`; batch should be reviewed before upsert into a shared DB.

## Artifact hygiene (do not commit data)
We confirmed gitignore coverage:
- repo root `.gitignore` ignores `*.sqlite`, `*.db`, etc.
- `SensibLaw/.gitignore` ignores `.cache_local/` (includes our snapshot and batch files)

Operational uncertainty:
- Some generated artifacts were owned by different OS users (`root` vs `ubuntu`) depending on which execution
mode produced them. This can create friction later (eg inability to overwrite a cache file).
We should standardize who writes under `.cache_local/` in our normal workflow.

## Next planned step (not done yet)
Extraction pass: transform wikitext snapshots into a reviewable, provenance-carrying “fact tree” seed envelope
(no normative claims), likely under:
- `data/concepts/wiki_gwb_v1.json` (planned output; not yet created; or a gitignored draft before promotion)

## Candidate distribution sanity check (new)
We added a small heuristic report tool:
- `SensibLaw/scripts/wiki_candidates_distribution_report.py`

Observed for the initial GWB seed extraction (162 candidates):
- heavy skew toward `event` titles (e.g. elections/conventions) because Wikipedia link structure is event-rich
- this is expected; downstream queueing for DBpedia/authority work should downsample events aggressively

This report is exploratory-only and should not be treated as authoritative typing.
