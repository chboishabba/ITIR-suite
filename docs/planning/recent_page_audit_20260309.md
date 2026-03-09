# Recent Page Audit (2026-03-09)

## Summary
- Added a repeatable audit runner at `scripts/check_recent_pages.py` to verify the recent `itir-svelte` routes against localhost plus their backing data sources.
- Live pass against `http://localhost:4173` now shows the recent routes rendering correctly, including the arguments workbench and the graph-enabled contested wiki lane.
- One known failing sample remains:
  - `/graphs/wiki-revision-contested?pack=wiki_revision_monitor_v1&run=run:wiki_revision_monitor_v1:2026-03-08T16:32:32+00:00:1af5177b&article=stress_high_german`
  - this is an error-only producer run, not a route/load failure

## Commands
- Full audit:
  - `python scripts/check_recent_pages.py`
- JSON output for machine inspection:
  - `python scripts/check_recent_pages.py --format json`
- Verify the arguments workbench route directly:
  - `curl -sS -o /dev/null -w '%{http_code}\n' 'http://localhost:4173/arguments/thread/69ac40e0-0cfc-839b-b2a8-0de3019379a9'`
- Focused contested-page producer check:
  - `python SensibLaw/scripts/query_wiki_revision_monitor.py --db-path SensibLaw/.cache_local/wiki_revision_harness.sqlite --pack-id wiki_revision_monitor_v1 --run-id 'run:wiki_revision_monitor_v1:2026-03-08T16:32:32+00:00:1af5177b' --article-id stress_high_german`
  - `python SensibLaw/scripts/query_wiki_revision_monitor.py --db-path SensibLaw/.cache_local/wiki_revision_harness.sqlite --pack-id wiki_revision_contested_v2 --run-id 'run:wiki_revision_contested_v2:2026-03-09T12:37:58+00:00:ab17b3eb' --article-id contest_donald_trump`

## Findings
### Route status
- `pass`:
  - `/threads`
  - `/thread/<latest canonical thread>`
  - `/arguments/thread/69ac40e0-0cfc-839b-b2a8-0de3019379a9`
  - `/graphs/narrative-compare?fixture=friendlyjordies_thread_extract`
  - `/graphs/semantic-report?source=gwb`
  - `/graphs/wiki-candidates`
  - `/graphs/wiki-fact-timeline?source=gwb`
  - `/graphs/wiki-revision-contested?pack=wiki_revision_contested_v2&run=run:wiki_revision_contested_v2:2026-03-09T12:37:58+00:00:ab17b3eb&article=contest_donald_trump`
  - `/graphs/wiki-timeline?source=gwb`
  - `/graphs/wiki-timeline-aoo?source=gwb`
  - `/graphs/wiki-timeline-aoo-all?source=gwb`
  - `/graphs/mission-lens`
- `failing`:
  - `/graphs/wiki-revision-contested?pack=wiki_revision_monitor_v1&run=run:wiki_revision_monitor_v1:2026-03-08T16:32:32+00:00:1af5177b&article=stress_high_german`
    - classification: `UI rendered but no meaningful payload`
    - observed: route renders, but the selected article is an error row from an error-only producer run and therefore has no contested graph payload

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
- `wiki_revision_contested_v2` sample changed run:
  - run: `run:wiki_revision_contested_v2:2026-03-09T12:37:58+00:00:ab17b3eb`
  - article: `contest_donald_trump`
  - counts: `changed=12`, `error=0`
  - selected article status: `changed`
  - selected graph: populated
  - summary includes `contested_graph_counts`
  - selected graph payload includes `regions=3` and `cycles=1`
  - route now hydrates contested graph detail from the graph-enabled v2 artifact/DB path

## Implementation Followthrough
- DONE: fix the arguments workbench `500` for the FriendlyJordies proving thread and keep it in the audit matrix.
- DONE: tighten the contested-graph read path so a changed graph-enabled contested run yields a non-null `selected_graph` when graph rows or artifact-backed payloads exist.
- Distinguish three UI states on `/graphs/wiki-revision-contested`:
  - producer run error
  - changed run with missing graph payload
  - valid run with populated contested graph
