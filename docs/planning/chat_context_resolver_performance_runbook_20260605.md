# Chat Context Resolver Performance Runbook (2026-06-05)

## Purpose

This runbook documents operator-facing best practice for
`scripts/chat_context_resolver.py` after the 2026-06-04 cross-thread FTS
optimization and benchmark pass against `/home/c/chat_archive.sqlite`.

The resolver is now fastest when archive-wide term work stays on the exact FTS
path. Regex, broad semantic/vector lanes, and ambiguous non-cross-thread text
lookup should be treated as special cases, not defaults.

## Recommended Commands

Fast exact archive-wide term ranking:

```bash
.venv/bin/python scripts/chat_context_resolver.py "dart" \
  --db ~/chat_archive.sqlite \
  --analyze-term "dart" \
  --cross-thread \
  --limit 10 \
  --json
```

Use progress for broad terms or interactive/operator UX:

```bash
.venv/bin/python scripts/chat_context_resolver.py "schema" \
  --db ~/chat_archive.sqlite \
  --analyze-term "schema" \
  --cross-thread \
  --limit 10 \
  --progress \
  --json
```

Use multiple exact terms when lexical recall is more important than speed, but
expect runtime to scale with combined FTS hit rows:

```bash
.venv/bin/python scripts/chat_context_resolver.py "dart schema" \
  --db ~/chat_archive.sqlite \
  --analyze-term "dart" \
  --analyze-term "schema" \
  --cross-thread \
  --limit 10 \
  --json
```

## Performance Expectations

Measured on `/home/c/chat_archive.sqlite` (`1002M`, 634,329 messages,
6,475 threads) after the FTS-hit aggregation change.

| Query shape | Median / elapsed | Result mode | Notes |
| --- | ---: | --- | --- |
| `dart`, limit 10 | `0.137s` median | `fts_hit_aggregation` | 72 FTS hit rows, 34 ranked threads |
| `dart`, limit 100 | `0.118s` median | `fts_hit_aggregation` | limit cost negligible when hit set is small |
| `dart --progress` | `0.112s` median | `fts_hit_aggregation` | progress overhead negligible |
| `dart --case-sensitive` | `0.094s` median | `fts_hit_aggregation` | same FTS hit set, fewer ranked threads |
| `database`, limit 10 | `1.024s` median | `fts_hit_aggregation` | 1,753 FTS hit rows |
| `schema`, limit 10 | `3.218s` median | `fts_hit_aggregation` | 7,479 FTS hit rows |
| missing term | `0.075s` median | `fts_hit_aggregation` | clean empty result |
| `dart OR schema` via two `--analyze-term` flags | `4.583s` median | `fts_hit_aggregation` | 7,546 FTS hit rows |

## Avoid As Defaults

- Avoid `--regex --cross-thread` for normal archive search. It currently falls
  back to thread scanning and exceeded the 20 second benchmark cap for `dart`.
- Avoid `--semantic` and `--hybrid` as default resolver paths. Direct MCA search
  worked only under an environment that allowed SQLite WAL sidecar writes near
  `/home/c/chat_archive_mca.sqlite`, and was materially slower:
  - direct MCA semantic `dart`: `18.406s`
  - direct MCA hybrid `dart`: `9.982s`
  - resolver cross-thread plus MCA semantic `dart`: `76.886s`
  - resolver cross-thread plus MCA hybrid `dart`: `84.529s`
- Avoid ambiguous non-cross-thread keyword lookups when the intent is
  archive-wide search. `dart --no-web` without `--cross-thread` measured
  `7.353s` median because it uses selector/title/FTS-candidate resolution rather
  than direct archive-wide term aggregation.

## Decision Rules

- Use `--analyze-term TERM --cross-thread --json` for exact archive-wide term
  ranking.
- Add `--progress` when the term is broad or operator visibility matters; it
  emits JSONL progress to stderr and keeps final JSON on stdout.
- Increase `--limit` freely for narrow terms; it is cheap when the FTS hit set is
  small.
- Prefer separate exact terms over regex when possible.
- Use `--semantic` or `--hybrid` only when semantic similarity is the actual
  question and slower startup/search is acceptable.
- Use thread-local analysis only after resolving a specific thread; do not use
  it as a broad discovery path.

## Output Signals To Check

In JSON output, fast cross-thread runs should show:

```json
{
  "analysis": {
    "mode": "fts_hit_aggregation",
    "performance": {
      "fts_query": "dart*",
      "fts_hit_rows": 72,
      "ranked_thread_count": 34
    }
  }
}
```

If `analysis.mode` is `thread_scan_fallback`, expect slower behavior and use
`--progress` or narrow the query.

## Known Follow-Ups

- Add a fast regex/predicate prefilter or explicit warning before the slow
  fallback path.
- Add resolver-side indexes/migrations for ambiguous non-cross-thread selector
  lookup.
- Fix resolver + MCA candidate resolution so vector candidates do not re-enter
  slow canonical lookup paths.
- Make MCA wrappers open read-only when used for search, or document that the
  current backend requires WAL sidecar write permission beside the MCA DB.
