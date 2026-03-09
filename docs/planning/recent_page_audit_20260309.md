# Recent Page Audit (2026-03-09)

## Summary
- Added a repeatable audit runner at `scripts/check_recent_pages.py` to verify the recent `itir-svelte` routes against localhost plus their backing data sources.
- Live pass against `http://localhost:4173` shows most recent routes rendering correctly.
- Two concrete failures remain:
  - `/arguments/thread/69ac40e0-0cfc-839b-b2a8-0de3019379a9` returns `500 Internal Server Error`.
  - `/graphs/wiki-revision-contested` renders its shell, but the checked `wiki_revision_monitor_v1` sample run is an error-only producer run and the checked `wiki_revision_contested_v1` sample run still yields `selected_graph = null`.

## Commands
- Full audit:
  - `python scripts/check_recent_pages.py`
- JSON output for machine inspection:
  - `python scripts/check_recent_pages.py --format json`
- Focused contested-page producer check:
  - `python SensibLaw/scripts/query_wiki_revision_monitor.py --db-path SensibLaw/.cache_local/wiki_revision_harness.sqlite --pack-id wiki_revision_monitor_v1 --run-id 'run:wiki_revision_monitor_v1:2026-03-08T16:32:32+00:00:1af5177b' --article-id stress_high_german`
  - `python SensibLaw/scripts/query_wiki_revision_monitor.py --db-path SensibLaw/.cache_local/wiki_revision_harness.sqlite --pack-id wiki_revision_contested_v1 --run-id 'run:wiki_revision_contested_v1:2026-03-09T07:46:59+00:00:05900d8c' --article-id contest_donald_trump`

## Findings
### Route status
- `pass`:
  - `/threads`
  - `/thread/<latest canonical thread>`
  - `/graphs/narrative-compare?fixture=friendlyjordies_thread_extract`
  - `/graphs/semantic-report?source=gwb`
  - `/graphs/wiki-candidates`
  - `/graphs/wiki-fact-timeline?source=gwb`
  - `/graphs/wiki-timeline?source=gwb`
  - `/graphs/wiki-timeline-aoo?source=gwb`
  - `/graphs/wiki-timeline-aoo-all?source=gwb`
  - `/graphs/mission-lens`
- `failing`:
  - `/arguments/thread/69ac40e0-0cfc-839b-b2a8-0de3019379a9`
    - classification: `route/load failure`
    - observed: HTTP `500`
  - `/graphs/wiki-revision-contested?pack=wiki_revision_monitor_v1&run=run:wiki_revision_monitor_v1:2026-03-08T16:32:32+00:00:1af5177b&article=stress_high_german`
    - classification: `UI rendered but no meaningful payload`
    - observed: route renders, selected article shows no pair and no contested graph
  - `/graphs/wiki-revision-contested?pack=wiki_revision_contested_v1&run=run:wiki_revision_contested_v1:2026-03-09T07:46:59+00:00:05900d8c&article=contest_donald_trump`
    - classification: `UI rendered but no meaningful payload`
    - observed: route renders, selected article shows pair reports, but contested graph detail still collapses to no graph payload

### Backing data
- Canonical chat archive is present and populated:
  - `~/chat_archive.sqlite`
  - `115351` messages
  - `1859` distinct threads
- Wiki revision harness DB is present and includes contested graph tables:
  - `SensibLaw/.cache_local/wiki_revision_harness.sqlite`
  - contested tables present:
    - `wiki_revision_monitor_contested_graphs`
    - `wiki_revision_monitor_contested_regions`
    - `wiki_revision_monitor_contested_cycles`
    - `wiki_revision_monitor_contested_edges`

### Wiki revision contested lane
- `wiki_revision_monitor_v1` sample error run:
  - run: `run:wiki_revision_monitor_v1:2026-03-08T16:32:32+00:00:1af5177b`
  - article: `stress_high_german`
  - counts: `changed=0`, `error=7`
  - selected article status: `error`
  - selected graph: `null`
  - root cause at producer level: `wiki_pull_api.py` failed during that run
- `wiki_revision_contested_v1` sample changed run:
  - run: `run:wiki_revision_contested_v1:2026-03-09T07:46:59+00:00:05900d8c`
  - article: `contest_donald_trump`
  - counts: `changed=8`, `error=0`
  - selected article status: `changed`
  - selected graph: `null`
  - summary omits `contested_graph_counts`
  - implication: producer/read-model contract is still incomplete or the query layer is not locating the persisted graph payload for the selected article

## Implementation Followthrough
- Fix the arguments workbench `500` for the FriendlyJordies proving thread and keep it in the audit matrix.
- Tighten the contested-graph read path so a changed contested run yields a non-null `selected_graph` when graph rows exist.
- Distinguish three UI states on `/graphs/wiki-revision-contested`:
  - producer run error
  - changed run with missing graph payload
  - valid run with populated contested graph
