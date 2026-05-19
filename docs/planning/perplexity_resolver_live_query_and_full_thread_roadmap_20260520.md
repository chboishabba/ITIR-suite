# Perplexity Resolver Live Query and Full-Thread Roadmap

Date: 2026-05-20

## Correction

Do not describe Perplexity's downloaded Markdown/export-button output as
canonical. Those files are user-visible recovery artifacts and may be seriously
incomplete. They can be bundled and ingested with provenance, but they should not
be treated as proof that the online thread was fully captured.

For thread `8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3`, the current archive has:

- `perplexity_auto`: 20 messages from the app API first-page style export.
- `perplexity_download_pumls_blockers`: 1706 messages from bundled Markdown
  files under `/home/c/Downloads`.
- total DB view: 1726 messages.

That split is a provenance fact, not a claim that the Downloads files are
complete or authoritative. The online Perplexity thread may still contain more
than either source currently captures.

## Current Finding

The app does have a fuller loading path than the current single-thread resolver
exporter uses.

Observed with Playwright on the live thread page:

- The main thread uses a `.scrollable-container` with large `scrollHeight`.
- Initial rendered text is only a slice of the thread.
- Scrolling the container causes Perplexity to issue additional requests:
  `/rest/thread/<thread-id>?...&limit=100&from_first=true&cursor=<cursor>`.
- Cursors change as the page loads more history.
- The current extractor resolves the first `/rest/thread/<id>` response too
  early, then tries its own cursor/offset fetch path. That path can replay the
  first page and falsely appear complete unless we reject partial exports.

Therefore, the full-thread resolver path should be browser-page driven:

1. Open the Perplexity thread in Playwright.
2. Register all matching `/rest/thread/<id>` responses.
3. Drive the actual app scroll container, not `window.scrollY`.
4. Merge entries from every captured response by stable entry identity.
5. Continue until the app reaches a stability condition.

## Full-Thread Loader Contract

Add a dedicated Perplexity full-thread loader surface in `perplexity-ai-export`.

Required behavior:

- Use the authenticated Playwright page context.
- Locate the active thread scroll container, currently visible as
  `.scrollable-container`.
- Scroll in bounded passes toward the load direction that reveals more turns.
- Capture every `/rest/thread/<thread-id>` response while scrolling.
- Merge all `entries` by `entry_uuid`, `frontend_uuid`, `uuid`, or fallback
  timestamp/query hash.
- Treat an export as partial if:
  - the last captured API payload reports `has_next_page=true`;
  - the UI can still trigger new `/rest/thread/<id>` responses;
  - scroll height/body text keeps changing after the stability window;
  - the merged entry count is less than the existing DB count for that thread
    when the resolver is explicitly refreshing an already-known thread.
- Emit diagnostics: captured response count, unique cursor count, merged entry
  count, message count, max scroll height, stable passes, and whether the run
  stopped due completion, timeout, or max-scroll cap.

Suggested completion heuristic:

- No new matching thread API response for N consecutive scroll passes.
- No increase in merged entry count for N consecutive passes.
- Scroll container cannot advance further in the requested direction.
- Add a final wait-and-scroll probe because Perplexity can pause and then load
  more after it first looks done.

Do not silently ingest partial exports. The current partial-export rejection is
correct and should remain.

## Resolver Integration

Resolver behavior for Perplexity URLs should be:

1. DB-first exact lookup by source thread ID.
2. If refresh/live fallback is requested:
   - run the full-thread Playwright loader;
   - keep captured message count versus existing DB count as a diagnostic only;
   - ingest only if complete or explicitly marked as recovery/partial by an
     opt-in flag.
3. If the full loader cannot prove completion:
   - return a structured partial result;
   - keep the DB match as the best current context;
   - do not add another first-page source to the archive.

Possible flags:

- `--provider perplexity`
- `--perplexity-full-load`
- `--perplexity-scroll-mode step|end|hybrid`
- `--perplexity-max-scroll-passes <n>`
- `--allow-partial-perplexity-ingest` disabled by default
- `--perplexity-diagnostics-json <path>`

Scroll mode semantics:

- `step`: correctness-oriented full-load mode. It advances the real
  `.scrollable-container` in bounded increments so the app has a chance to emit
  intermediate `/rest/thread/<id>` pages.
- `end`: fast tail probe. It may skip middle virtual-scroll loader boundaries,
  so its diagnostics must be treated as possible-gap evidence unless overlap is
  independently proven.
- `hybrid`: mostly stepped loading with occasional end probes. Useful for
  experiments, not sufficient by itself as proof of full history.

Existing DB count is not a completeness oracle. A fresh live pull with fewer
messages may still be a valid newest/tail overlay, and an older DB source may be
larger because it came from a different recovery path. For full refresh, require
cursor/page continuity or an observed overlap boundary; for latest refresh,
store the live capture with provenance and diagnostics.

## Newest-Only Refresh

Newest-only refresh may be possible, but should not be assumed.

Perplexity's UI loads history through cursor pages, and long threads can report
more after seeming stable. A safe newest-only mode needs a stable boundary:

- known DB source message IDs or entry hashes;
- cursor payloads that can be mapped to entry IDs;
- a rule to stop only after overlapping existing DB entries are observed.

Until that is proven, the resolver may need to let the page load the whole
available history, then dedupe on ingest.

## Live Ask Query Surface

This is a separate provider capability from history export.

Target surface:

- `perplexity-ai-export` adds an `ask` command:
  `npm run ask -- --prompt "<text>" [--thread-url <url>] [--out <json>]`.
- The implementation uses the real Playwright page, not direct HTTP.
- For a new query, open Perplexity's composer, fill the prompt, submit, and
  capture the resulting thread URL plus `/rest/thread/<id>` responses.
- For follow-up mode, open an existing thread, scroll/load as needed, use the
  follow-up composer, submit, wait for answer completion, then export/ingest the
  updated thread.

Acceptance criteria:

- Captures the new thread ID or existing thread ID deterministically.
- Waits for answer completion without relying on a fixed sleep only.
- Exports the new/updated thread as `itir.perplexity.thread.v1`.
- Ingests through the resolver provider registry with
  `--format perplexity --account perplexity`.
- Never claims completion if answer streaming or history pagination is still
  active.

## Documentation Rule

Docs must distinguish:

- **App API capture**: preferred when the full-thread loader proves completion.
- **Perplexity export-button/download Markdown**: incomplete-prone recovery
  input, useful with provenance, not canonical truth.
- **Canonical DB view**: best current local context after provenance-aware
  ingest and dedupe.
