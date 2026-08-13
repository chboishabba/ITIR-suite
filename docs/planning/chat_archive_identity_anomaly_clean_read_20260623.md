# Chat Archive Identity Anomaly Clean Read Notes

Date: 2026-06-23

## Working Position

The archive identity anomaly is contained for new pulls, but historical rows still need snapshot-scoped reads. A `source_thread_id` with multiple `source_id` snapshots is a warning, not proof of contamination. The stronger diagnostic is low overlap across both raw `source_message_id` and normalized role/text content.

For normal refetches, high dedupe should be expected. If message IDs differ but content overlaps, treat it as likely ID-derivation drift. If content is disjoint or near-disjoint, treat the snapshots as separate reads until reviewed.

## Target Thread

URL:

`https://chatgpt.com/g/g-p-69c0bc292b008191b85fede13fde4f88/c/6a39089d-f298-83ec-830e-bac91f29a424`

Archive resolution:

- title: `Formalising in DASHI`
- source_thread_id: `6a39089d-f298-83ec-830e-bac91f29a424`
- canonical_thread_id: `cbf80c8bc7911e2aef1e8a236e49e2efdadf0153`
- snapshots:
  - `pull_20260622T133637Z`: 152 raw rows, 148 non-system rows, latest `2026-06-22T13:31:38+00:00`
  - `pull_20260622T151914Z`: 109 raw rows, 98 non-system rows, latest `2026-06-22T14:45:16+00:00`

The resolver defaults to the latest snapshot, `pull_20260622T151914Z`, and warns that multiple snapshots exist. For this thread, the older and newer snapshots should be read as separate segments/reference surfaces, not silently unioned.

## Dedupe / Join Status

There is no meaningful dedupe/join across the two snapshots at present:

- both snapshots share `source_thread_id = 6a39089d-f298-83ec-830e-bac91f29a424`
- both snapshots resolve to canonical thread `cbf80c8bc7911e2aef1e8a236e49e2efdadf0153`
- raw `source_message_id` sets are disjoint
- normalized role/text overlap is tiny: 4 overlapping content keys
- row-count skew is not high: 152 raw rows vs 109 raw rows

So this is not the classic "tiny bad pull glued onto a large real thread" pattern. It is a same-URL/canonical-thread case with two mostly disjoint temporal/snapshot surfaces. A canonical-thread-only read would silently concatenate them and create the confusing mixed transcript we are trying to avoid.

Treat the snapshots as separate reads unless a later continuity pass proves they can be joined.

## Clean Read Artifacts

Snapshot-scoped DB exports were written under:

`/home/c/Documents/code/ITIR-suite/.cache_local/chat_clean_reads/`

Manifest:

`formalising-in-dashi_6a39089d-f298-83ec-830e-bac91f29a424_manifest.json`

The standard `reverse-engineered-chatgpt/chat_exports` directory did not contain a downloaded JSON matching this exact UUID during the 2026-06-23 check. If a browser-downloaded local copy exists elsewhere, compare it against these snapshot-scoped reads by payload `conversation_id` first, then by role/text overlap.

## Immediate Rule

When chasing the original thread, use `--turn-source-id` or a source-scoped SQL export. Do not read by canonical thread alone until the historical duplicate snapshots have been reviewed.

Example latest-snapshot read:

```bash
/home/c/Documents/code/ITIR-suite/.venv/bin/python \
  /home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py \
  6a39089d-f298-83ec-830e-bac91f29a424 \
  --db /home/c/chat_archive.sqlite \
  --turn-source-id pull_20260622T151914Z
```

Use `pull_20260622T133637Z` separately for the older segment.

## Checker Script Implication

`scripts/chat_archive_identity_anomaly_report.py` is a classifier and inventory tool, not a merge tool. For this thread it should flag:

- multi-snapshot: yes
- `source_message_id` overlap: none / effectively none
- normalized content overlap: tiny
- high row-count skew: no
- expected classification: `review_needed`, not `strong_anomaly_candidate`

That classification is correct: the checker identifies that snapshot scoping is required, but it does not decide that snapshots can or should be joined.

The current classification meanings are:

- `strong_anomaly_candidate`: likely wrong identity/contamination, especially disjoint content plus high skew.
- `likely_refetch_id_derivation`: message IDs differ but normalized content overlaps, so the issue may be ID derivation rather than identity.
- `review_needed`: disjoint or near-disjoint snapshots without high skew. This may be a legitimate continuation, branch/windowed pull, or contamination without row-count skew.

Any future join requires a separate continuity check over timestamps, first/last user turns, branch lineage, content sequence, and ideally verified payload identity provenance.
