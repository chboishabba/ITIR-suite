# Chat Archive DB Exporter Roadmap

Date: 2026-05-16

## Control Read

Perplexity's own Markdown/PDF exports are not a trusted archive surface. The
canonical source is the local structured chat archive DB:

- default canonical DB: `/home/c/chat_archive.sqlite`
- thread identity: `canonical_thread_id`
- online/provider identity: `source_thread_id`, `source_message_id`
- human export surfaces: Markdown and printable HTML
- audit/export surface: structured JSON plus checksum manifest
- PDF surface: generated from archive-derived HTML only; never from
  Perplexity's own PDF export

The exporter must preserve Markdown-native content, including LaTeX source,
tables, code fences, footnotes, and section structure. PDF text extraction is a
fallback inspection aid only; it is not a source of truth because rendered
formula extraction damages structure.

## Implemented

- [x] DB-backed thread export script:
  `scripts/export_chat_archive_thread.py`
- [x] thread selection by:
  - `--canonical-thread-id`
  - `--source-thread-id`
  - `--selector`
  - `--title`
  - optional `--platform`
- [x] deterministic structured JSON export:
  `itir.chat_archive.thread_export.v1`
- [x] deterministic Markdown export
- [x] printable HTML export
- [x] rendered document HTML export with local static KaTeX pre-rendering when
  available
- [x] optional PDF render via `--pdf` and `--pdf-engine auto`
- [x] chunked long-thread HTML/PDF export via `--chunk-messages` and
  `--chunk-target-bytes`
- [x] bounded parallel PDF rendering for chunks via `--pdf-workers`
- [x] fast split-plan inspection via `--chunk-plan-only`
- [x] repeatable chunk/PDF benchmark harness:
  `scripts/benchmark_chat_archive_export_chunks.py`
- [x] display-only compaction for long visible URLs in HTML/PDF while keeping
  original link targets intact
- [x] display-only fragmented listing repair for HTML/PDF, with conservative
  structural detection and export diagnostics
- [x] lightweight export diagnostics for malformed math delimiters and likely
  truncated Markdown links
- [x] optional bundle directory with `manifest.json` and SHA256 file digests
- [x] Perplexity-style document Markdown:
  - user prompts become top-level `#` sections
  - assistant content renders as normal Markdown body
  - `---` separates turns
  - internal `##`, `###`, `***`, tables, math, code fences, and footnotes are
    preserved from DB text
- [x] explicit transcript Markdown mode:
  `--markdown-style transcript`
- [x] Perplexity duplicate DOM/export block cleanup by default
- [x] raw audit escape hatch:
  `--no-clean-perplexity-duplicates`
- [x] focused tests:
  `tests/test_export_chat_archive_thread.py`
- [x] live smoke against real Perplexity archive thread:
  `/tmp/perplexity-thread-export-docstyle`

## Usage

Export a Perplexity thread by online/source thread UUID:

```bash
/home/c/Documents/code/ITIR-suite/.venv/bin/python scripts/export_chat_archive_thread.py \
  --db /home/c/chat_archive.sqlite \
  --source-thread-id 8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3 \
  --out /tmp/perplexity-thread-export-docstyle \
  --bundle \
  --format all \
  --pdf \
  --json
```

Use transcript mode for explicit role-by-role audits:

```bash
/home/c/Documents/code/ITIR-suite/.venv/bin/python scripts/export_chat_archive_thread.py \
  --db /home/c/chat_archive.sqlite \
  --source-thread-id 8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3 \
  --out /tmp/perplexity-thread-transcript \
  --bundle \
  --format markdown \
  --markdown-style transcript
```

## Remaining Roadmap

### P1: Batch Export

- [ ] add `--all-platform perplexity` or `--where-platform perplexity`
- [ ] add `--since`, `--until`, and `--limit`
- [ ] write one bundle per canonical thread under an output directory
- [ ] emit a top-level batch manifest with thread counts, byte counts, and
  checksum coverage

### P1: Query-to-Export

- [ ] allow FTS query selection from `messages_fts`
- [ ] export all matched threads or the top N candidates
- [ ] include match metadata in the bundle manifest

### P1: Resolver Hook

- [ ] add a resolver-side export command or documented wrapper path
- [ ] after `chat_context_resolver.py` resolves a canonical thread, allow the
  same ID to be passed directly to the exporter
- [ ] keep export opt-in; resolver lookup must remain read-only by default

### P2: HTML/PDF Rendering

- [x] keep HTML printable and usable without network access
- [x] pre-render math into static KaTeX HTML before PDF when local KaTeX assets
  and Node are available
- [x] optionally render PDF with WeasyPrint when installed, falling back to
  bounded Chrome/Chromium rendering
- [x] split very long threads into independently renderable part files
- [ ] benchmark representative chunk sizes against render time, PDF size, and
  visual quality
- [ ] never treat generated PDF text as canonical

### P2: Display-Only Whitespace Repair

Perplexity/downloaded Markdown can fragment pasted terminal listings into
one-token paragraphs, which makes PDF output show vertical "columns" such as
date, icon, filename, permission fragments, and size on separate lines. This is
not repaired in canonical JSON or Markdown, because those surfaces are audit
surfaces. It is repaired only in rendered HTML/PDF display text.

Implemented policy:

- `--whitespace-repair off|conservative|aggressive`
- default: `conservative`
- applies only outside fenced code, math, tables, blockquotes, headings, lists,
  and indented code
- requires repeated structured evidence, not a hardcoded filename:
  - date/time row anchors
  - file/path-like tokens
  - permission fragments
  - size tokens
  - repeated rows
- plain single-word names such as `artifacts` or `build` are accepted only
  after a timestamped listing row is already in progress and still lacks a
  filename; they never start a repair span on their own
- conservative mode requires at least three reconstructed rows and high
  confidence
- repaired spans are emitted as `text` fences in rendered Markdown/HTML so the
  listing remains monospaced and readable
- high-confidence Codex-style tool transcript blocks (`Ran`, `Explored`,
  `Edited`, `Waited`) are also display-repaired into monospaced blocks, with
  split command arguments compacted back onto one command line; this is scoped
  to rendered HTML/PDF and does not alter canonical text
- every repair emits an export diagnostic with source line range, repaired row
  count, and confidence
- bundle manifests record the active `html_pdf_display_policy`

Non-goals:

- no mutation of DB text
- no mutation of structured JSON
- no default mutation of Markdown exports
- no global whitespace normalization of poetry, prose, tables, math, or code

### P2: Split Tuning Tests

- [x] unit-test split planning against message-count and byte-budget limits
- [x] unit-test chunked bundle output and manifest chunk-plan recording
- [x] add a timing harness for candidate settings such as:
  - 40 messages / 600 KB
  - 80 messages / 1.2 MB
  - 120 messages / 1.8 MB
- [x] record render success/failure, elapsed time, PDF bytes, and first error
  per run

Benchmark run against source thread
`8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3` on 2026-05-17:

| Profile | Chunks | Workers | Elapsed | Result |
| --- | ---: | ---: | ---: | --- |
| 40 messages / 600 KB | 44 | 2 | 107.012s | 44/44 PDFs |
| 80 messages / 1.2 MB | 22 | 2 | 99.991s | 22/22 PDFs |
| 120 messages / 1.8 MB | 15 | 2 | 99.871s | 15/15 PDFs |
| 80 messages / 1.2 MB | 22 | 3 | 87.715s | 22/22 PDFs |

Current default recommendation for this host and thread shape:
`--chunk-messages 80 --chunk-target-bytes 1200000 --pdf-workers 3`.
Use `--pdf-workers 2` as the conservative profile when memory pressure is
visible.

### P2: Provenance Sidecar

- [ ] include `message_blocks` by default in JSON once block coverage is stable
- [ ] add source DB schema/version details to the manifest
- [ ] add export policy fields:
  `cleaned_text`, `raw_text_available`, `dedupe_strategy`
- [ ] add display-repair backrefs:
  - canonical `message_id` / `canonical_thread_id`
  - source line/span range in the rendered Markdown input
  - repair kind and confidence
  - optional external trace refs when a repair corresponds to Codex or terminal
    logs

### P2: StatiBaker Parity and Backrefs

StatiBaker already has the correct observer/provenance shape for the new
Perplexity/Codex rendering work:

- `StatiBaker/sb/codex_trace.py` can derive `codex_trace_facts_v1` from the
  chat archive DB (`source_route=chat_archive`) and from raw Codex history/TUI
  logs (`source_route=raw_codex_logs`).
- `StatiBaker/sb/dashboard.py` already treats sqlite chat as the preferred chat
  source, tags `source_id` values beginning with `codex_` as `codex-ingest`,
  and counts structured `role=tool` `exec_command` messages separately from
  printed command text.
- `StatiBaker/docs/observed_signals.md` requires CLI activity to stay
  metadata-only (`cmd_hash`, `cwd_hash`, `exit`, provenance), while
  `docs/activity_dashboard.md` and `docs/interfaces.md` keep dashboard/observer
  views read-only and reference-heavy.

Parity rule:

- the chat archive DB stores canonical conversation text once
- raw Codex/TUI/terminal logs remain their own source artifacts or metadata
  lanes
- exports store derived manifests, diagnostics, and refs only
- a terminal paste repair should be able to point back to a Codex/log/CLI
  source when there is evidence, but must not copy that source into a second
  canonical store

Near-term bridge:

- [ ] add an exporter manifest `backrefs` array for display repairs and
  suspicious terminal-paste spans
- [ ] add a StatiBaker-side query/helper that can match a canonical chat
  message span to raw Codex history/TUI-log facts by thread, timestamp window,
  role/tool kind, and digest/preview evidence
- [ ] emit only refs/hashes/line spans by default; keep full text in the
  canonical chat archive or source log, not SB dashboard rows
- [ ] use the exporter as the parity PDF renderer for Perplexity, ChatGPT, and
  Codex-ingested archive threads
- [ ] add fixtures that render one Perplexity thread and one Codex/GPT archive
  thread to HTML/PDF and verify the manifest preserves canonical IDs plus SB
  backref hooks

### P3: MyChatArchive Bridge

- [ ] export MCA search result sets by canonical thread/message IDs
- [ ] allow semantic/hybrid candidate lists to be materialized as DB-backed
  document bundles
- [ ] maintain the rule: vectors point to canonical rows; exported Markdown is a
  sidecar, not the source of truth

## Acceptance Gate

This roadmap is complete for the current slice when:

- [x] a real Perplexity thread can be exported from `/home/c/chat_archive.sqlite`
  without using Perplexity's own Markdown/PDF output
- [x] exported Markdown follows the practical Perplexity document convention
  without relying on the logo
- [x] JSON preserves canonical/source IDs for later MCA/vector provenance
- [x] tests cover selection, bundle output, Markdown modes, HTML output, and
  duplicate-block cleanup
- [ ] batch export and resolver hook are implemented in a later slice
