# Largest Code Files Refactor Roadmap

Date: 2026-03-28

## Scope

This note audits the largest repo-owned code files in `ITIR-suite` by tracked
line count, excluding obvious vendored/build/generated paths such as
`piecash-1.2.1/`, `build/`, `dist/`, `target/`, `node_modules/`, and
`checkpoints/`.

The goal is not "make every large file small". The goal is to identify files
whose size reflects boundary drift:

- route files that also own normalization and graph-building
- loaders that also own subprocess/DB/path policy
- runtime modules that also own transport, graph projection, receipts, and
  orchestration
- naming or lane-specific logic that should instead be portable across the
  suite

## Largest Files Snapshot

Top tracked repo-owned code files by line count at audit time:

| Lines | File |
| ---: | --- |
| 2016 | `scripts/chat_context_resolver.py` |
| 1779 | `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte` |
| 1251 | `itir-svelte/src/lib/server/corpora.ts` |
| 1189 | `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte` |
| 1029 | `itir-svelte/src/routes/+page.server.ts` |
| 943 | `itir-svelte/src/lib/server/wikiTimelineAoo.ts` |
| 894 | `tools/zelph_bin_v3_bucket_builder.cpp` |
| 872 | `itir-svelte/src/routes/graphs/semantic-report/+page.svelte` |
| 848 | `itir-svelte/src/lib/sb-dashboard/components/ToolUseSummary.svelte` |
| 790 | `casey-git-clone/scripts/benchmark_casey_vs_git.py` |
| 674 | `itir_jmd_bridge/runtime.py` |
| 634 | `itir-svelte/src/routes/graphs/mission-lens/+page.svelte` |
| 611 | `casey-git-clone/src/casey_git_clone/cli.py` |
| 581 | `itir-svelte/src/lib/semantic/TokenArcInspector.svelte` |
| 573 | `itir-svelte/tests/factReview_regressions.test.js` |
| 561 | `itir-svelte/src/routes/graphs/wiki-revision-contested/+page.svelte` |
| 559 | `itir-svelte/src/lib/chat/ToolCallBlock.svelte` |
| 538 | `itir-svelte/src/lib/server/semanticReport.ts` |
| 533 | `casey-git-clone/src/casey_git_clone/runtime_sqlite.py` |
| 509 | `itir-svelte/src/routes/graphs/fact-review/+page.svelte` |

## High-Priority Refactor Targets

### 1. `scripts/chat_context_resolver.py`

Why it is oversized:

- DB lookup policy sits beside web fallback, export download, structurer ingest,
  transcript analysis, CLI parsing, and terminal rendering.
- The file currently behaves like four modules in one.

Primary seams:

- `DbMatch` lookup and FTS candidate resolution around
  [`scripts/chat_context_resolver.py:320`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py#L320)
  should move into a `chat_context_resolver/db_lookup.py` module.
- Live web fallback and `re_gpt` command construction around
  [`scripts/chat_context_resolver.py:531`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py#L531)
  and
  [`scripts/chat_context_resolver.py:721`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py#L721)
  should move into a `live_fetch.py` module.
- Thread-local and cross-thread analysis around
  [`scripts/chat_context_resolver.py:1216`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py#L1216)
  and
  [`scripts/chat_context_resolver.py:1275`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py#L1275)
  should move into `analysis.py`.
- Web-miss persistence and structurer ingest around
  [`scripts/chat_context_resolver.py:1491`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py#L1491)
  should move into `persist.py`.
- CLI parsing/output rendering should stay thin, with `main()` in
  [`scripts/chat_context_resolver.py:1674`](/home/c/Documents/code/ITIR-suite/scripts/chat_context_resolver.py#L1674)
  reduced to orchestration only.

Normalization note:

- This is already general-use logic. Keep the name neutral. Do not let the
  fallback/persistence path implicitly depend on `reverse-engineered-chatgpt`
  naming in its public contract.

### 2. `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`

Why it is oversized:

- The route owns UI state, graph construction, numeric normalization, source and
  lens derivation, context-row generation, highlighting, and large render blocks.
- This is the clearest example of a route file acting as a domain module.

Primary seams:

- Numeric parsing and lane-key logic around
  [`+page.svelte:291`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte#L291)
  should move into a reusable `$lib/wikiTimeline/numeric.ts`.
- Source label derivation around
  [`+page.svelte:627`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte#L627)
  should move into `$lib/wikiTimeline/sourceLabels.ts`.
- Lens derivation around
  [`+page.svelte:700`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte#L700)
  should move into `$lib/wikiTimeline/lensLabels.ts`.
- Highlighting and text-context helpers around
  [`+page.svelte:919`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte#L919)
  should move into `$lib/wikiTimeline/context.ts`.
- `CtxRow` and related context-row shaping around
  [`+page.svelte:242`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte#L242)
  should move into a typed `$lib/wikiTimeline/contextRows.ts`.
- The rendered "Corpus docs" and "Context" panels should become separate
  components; the route should pass prepared props, not compute everything
  inline.

Normalization note:

- `AAO` is a lane/view name, not a suite-level abstraction. The reusable pieces
  should live under a neutral `wikiTimeline/` or `timelineGraph/` namespace,
  with `aoo-all` remaining a composition surface only.

### 3. `itir-svelte/src/lib/server/corpora.ts`

Why it is oversized:

- This file is currently a server-side omnibus for messenger, OpenRecall,
  processed corpora, feedback receipts, broader diagnostics, and fact-review
  drill-in policy.

Primary seams:

- Feedback drill-in and raw-source routing logic around
  [`corpora.ts:290`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/corpora.ts#L290)
  and
  [`corpora.ts:365`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/corpora.ts#L365)
  should move into a neutral `corpora/navigation.ts`.
- The large personal-results loader around
  [`corpora.ts:485`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/corpora.ts#L485)
  should be split into:
  `personalProcessedRuns.ts`, `affidavitResults.ts`, and `feedbackReceipts.ts`.
- Corpus-home summary loading around
  [`corpora.ts:771`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/corpora.ts#L771)
  should stay as a thin aggregator over smaller loaders.
- Broader diagnostics summary/detail loading around
  [`corpora.ts:877`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/corpora.ts#L877)
  and
  [`corpora.ts:979`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/corpora.ts#L979)
  should become a distinct `broaderDiagnostics.ts` module.

Normalization note:

- `buildRawSourceHref()` currently mixes product routing policy with source-kind
  heuristics. That policy should be declared once and reused across corpora and
  feedback lanes.

### 4. `itir-svelte/src/routes/+page.server.ts`

Why it is oversized:

- One load function currently owns date selection, DB-vs-file fallback policy,
  dashboard autogeneration, range aggregation, heatmap construction, notes-meta
  stitching, artifact mtime enrichment, and action handling.

Primary seams:

- Date and dashboard source discovery around
  [`+page.server.ts:159`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/+page.server.ts#L159)
  and
  [`+page.server.ts:191`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/+page.server.ts#L191)
  should move into `$lib/server/dashboard/loaders.ts`.
- Heatmap construction around
  [`+page.server.ts:299`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/+page.server.ts#L299)
  should move into `$lib/sb-dashboard/heatmaps.ts`.
- Range aggregation around
  [`+page.server.ts:410`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/+page.server.ts#L410)
  should move into `$lib/sb-dashboard/rangeAggregate.ts`.
- The route `load()` at
  [`+page.server.ts:711`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/+page.server.ts#L711)
  should become composition only.
- `actions.buildMissing` at
  [`+page.server.ts:983`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/+page.server.ts#L983)
  should be a small wrapper over a reusable dashboard build service.

Normalization note:

- This is dashboard infrastructure, not root-route-specific logic. The reusable
  pieces should be named for dashboard aggregation, not for `/`.

### 5. `itir-svelte/src/lib/server/wikiTimelineAoo.ts`

Why it is oversized:

- The module contains types, payload normalization, DB subprocess execution,
  HCA-specific overlay behavior, action/negation normalization, and an
  unreachable legacy JSON fallback block.

Primary seams:

- `normalizePayloadObject()` at
  [`wikiTimelineAoo.ts:285`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/wikiTimelineAoo.ts#L285)
  should move into `wikiTimeline/normalize.ts`.
- The HCA-only patch path at
  [`wikiTimelineAoo.ts:571`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/wikiTimelineAoo.ts#L571)
  should move into `wikiTimeline/overlays/hca.ts`.
- Shared negation/action canonicalization at
  [`wikiTimelineAoo.ts:598`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/wikiTimelineAoo.ts#L598)
  and
  [`wikiTimelineAoo.ts:609`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/wikiTimelineAoo.ts#L609)
  should move into `wikiTimeline/normalizeShared.ts`.
- The loader at
  [`wikiTimelineAoo.ts:624`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/wikiTimelineAoo.ts#L624)
  should be reduced to DB resolution plus optional overlay composition.
- The unreachable legacy fallback starting near
  [`wikiTimelineAoo.ts:658`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/wikiTimelineAoo.ts#L658)
  should either be deleted or moved to a separate regression-fixture helper.

Normalization note:

- The file name still encodes `AOO`. If the normalization logic is intended to
  support multiple wiki timeline surfaces, move the portable pieces under a
  generic `wikiTimeline` namespace and keep `Aoo` only on the final typed
  loader/export surface.

### 6. `itir_jmd_bridge/runtime.py`

Why it is oversized:

- It mixes provider fetch behavior, adaptive ingest policy, runtime object
  projection, runtime graph projection, receipt generation, batch ingest, and
  prototype/MDL inspection.

Primary seams:

- Adaptive ingest settings at
  [`runtime.py:133`](/home/c/Documents/code/ITIR-suite/itir_jmd_bridge/runtime.py#L133)
  should move into `rate_policy.py`.
- Runtime object, graph, and receipt builders at
  [`runtime.py:168`](/home/c/Documents/code/ITIR-suite/itir_jmd_bridge/runtime.py#L168),
  [`runtime.py:247`](/home/c/Documents/code/ITIR-suite/itir_jmd_bridge/runtime.py#L247),
  and
  [`runtime.py:329`](/home/c/Documents/code/ITIR-suite/itir_jmd_bridge/runtime.py#L329)
  should become separate modules under `contracts/` or `projection/`.
- Batch ingest at
  [`runtime.py:451`](/home/c/Documents/code/ITIR-suite/itir_jmd_bridge/runtime.py#L451)
  and prototype inspection at
  [`runtime.py:560`](/home/c/Documents/code/ITIR-suite/itir_jmd_bridge/runtime.py#L560)
  should share a common browsing executor instead of duplicating the browse /
  adaptive-rate / thread-pool loop.

Normalization note:

- Keep "JMD bridge" as the package boundary, but move provider-neutral runtime
  contracts out of "bridge runtime" naming where possible. The suite-level
  idea is "external object graph projection", not "pastebin-only runtime".

### 7. `casey-git-clone/src/casey_git_clone/cli.py`

Why it is oversized:

- The file mixes command registration, rendering, operation execution, observer
  attachment, and optional advisory integration.

Primary seams:

- Observer attachment around
  [`cli.py:56`](/home/c/Documents/code/ITIR-suite/casey-git-clone/src/casey_git_clone/cli.py#L56)
  should move into `observer_cli.py`.
- Console rendering around
  [`cli.py:91`](/home/c/Documents/code/ITIR-suite/casey-git-clone/src/casey_git_clone/cli.py#L91)
  should move into `render.py`.
- Individual command handlers such as
  [`cli.py:247`](/home/c/Documents/code/ITIR-suite/casey-git-clone/src/casey_git_clone/cli.py#L247),
  [`cli.py:311`](/home/c/Documents/code/ITIR-suite/casey-git-clone/src/casey_git_clone/cli.py#L311),
  [`cli.py:369`](/home/c/Documents/code/ITIR-suite/casey-git-clone/src/casey_git_clone/cli.py#L369),
  and
  [`cli.py:434`](/home/c/Documents/code/ITIR-suite/casey-git-clone/src/casey_git_clone/cli.py#L434)
  should move into `commands/*.py`.
- Parser wiring at
  [`cli.py:510`](/home/c/Documents/code/ITIR-suite/casey-git-clone/src/casey_git_clone/cli.py#L510)
  should become declarative once commands are split.

Normalization note:

- The observer path is useful outside Casey. If the receipt/bundle emission
  contract is meant to be suite-portable, Casey should depend on that shared
  observer emitter rather than owning a Casey-shaped copy of the orchestration.

## Secondary Candidates

These are large enough to warrant a follow-up split pass once the top seven are
under control.

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte` (1189):
  likely split into lane-specific controls, graph data shaping, and context
  panels alongside the `aoo-all` extraction work.
- `tools/zelph_bin_v3_bucket_builder.cpp` (894):
  split argument parsing / binary section writers / JSON manifest emitters /
  route generation into separate translation units if this tool is expected to
  keep growing.
- `itir-svelte/src/routes/graphs/semantic-report/+page.svelte` (872):
  likely split view filters, summary panels, and relation-table renderers.
- `itir-svelte/src/lib/sb-dashboard/components/ToolUseSummary.svelte` (848):
  likely split family table, variant drawer, and command-detail formatting into
  focused components.
- `casey-git-clone/scripts/benchmark_casey_vs_git.py` (790):
  split fixture generation, measurement, snapshotting, and report formatting.
- `itir-svelte/src/routes/graphs/mission-lens/+page.svelte` (634),
  `itir-svelte/src/lib/semantic/TokenArcInspector.svelte` (581), and
  `itir-svelte/src/routes/graphs/fact-review/+page.svelte` (509):
  each likely owns too much data shaping relative to its route/component role.
- `casey-git-clone/src/casey_git_clone/runtime_sqlite.py` (533):
  split schema/init, tree persistence, workspace persistence, and build
  persistence into separate persistence modules if Casey continues to grow.

## Cross-Cutting Normalization Rules

These rules should govern the extraction work:

1. Move lane-specific code behind generic contracts.
   Example: `wikiTimeline` helpers should not need `AOO` in their names unless
   the data shape is truly AAO-specific.

2. Keep routes and CLIs thin.
   Large routes should compose loaders/helpers/components. Large CLIs should
   compose commands/renderers/services.

3. Separate policy from transport.
   Path routing, feature fallback, rate policy, and dataset-specific overlays
   should not live inline with parsing or rendering.

4. Treat legacy one-off names as adapters, not canonical abstractions.
   If a helper only exists because of one lane's historical shape, park it in an
   adapter/overlay file instead of letting it name the general interface.

5. Remove dead fallback code once the governing path is frozen.
   Unreachable or legacy retention blocks make large files much harder to audit.

## Suggested Execution Order

### Phase 1: High-leverage decomposition

- `scripts/chat_context_resolver.py`
- `itir-svelte/src/lib/server/corpora.ts`
- `itir-svelte/src/routes/+page.server.ts`

Rationale:

- These files mix the most orthogonal responsibilities.
- They offer the biggest readability/testability gains without touching the
  densest graph UIs first.

### Phase 2: Wiki timeline normalization

- `itir-svelte/src/lib/server/wikiTimelineAoo.ts`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`

Rationale:

- The server normalizer and the route surfaces should be split together so the
  new helper boundaries are shared rather than duplicated.

### Phase 3: Package-local cleanup

- `itir_jmd_bridge/runtime.py`
- `casey-git-clone/src/casey_git_clone/cli.py`
- `casey-git-clone/src/casey_git_clone/runtime_sqlite.py`
- `casey-git-clone/scripts/benchmark_casey_vs_git.py`

Rationale:

- These are self-contained subpackages and can be improved with less risk to the
  main web surface.

## Exit Criteria

The roadmap is satisfied when:

- each target file has an agreed extraction plan
- generic helpers live under generic names
- route/CLI files primarily compose imported logic
- lane-specific overlays are explicit adapter modules
- dead legacy fallback blocks are either removed or isolated as fixtures
