# Largest-File Refactor Roadmap

## Purpose

Identify the largest repo-owned code files in `ITIR-suite` by line count and
use that inventory to choose the next repo-wide normalization/refactor slices.

This note is intentionally about *owned* code only. It excludes obvious vendor,
generated, checkpoint, and build-output surfaces such as:

- `piecash-1.2.1/`
- `node_modules/`
- `build/`
- `dist/`
- `target/`
- `checkpoints/`
- generated docs assets

The goal is not “make every file small.” The goal is to identify where a large
file is hiding multiple contracts that should live in separate modules, and
where product- or corpus-specific naming is leaking into suite-level
infrastructure that is meant to stay general.

This lane is docs-first. Before triaging any specific file into an
implementation queue, write a short file-local refactor brief in this roadmap
or in a linked child note. That brief must state:

- the intended reusable contract
- what remains lane/provider/corpus-specific
- the proposed extraction boundary
- the acceptance check for calling the split complete

Line count alone is not enough to justify triage.

## Largest Repo-Owned Files

Baseline command used on 2026-03-28:

```bash
git ls-files \
  | rg '\.(py|js|jsx|ts|tsx|svelte|rs|go|java|c|cc|cpp|cxx|h|hpp|jl|lean|agda|sh|sql|css|scss|html|vue|mjs|mts|cts|kt|scala|rb|php)$' \
  | rg -v '^(piecash-1\.2\.1/|node_modules/|dist/|build/|coverage/|\.svelte-kit/|checkpoints/|docs/assets/|target/|vendor/|third_party/)' \
  | xargs -r wc -l | sort -nr | head -n 80
```

Top files:

| Lines | File | Primary issue |
| ---: | --- | --- |
| 2016 | `scripts/chat_context_resolver.py` | resolver, live fallback, transcript analysis, formatting, and CLI all live together |
| 1779 | `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte` | giant route component mixing graph building, filters, context, evidence, and AAO-specific presentation |
| 1251 | `itir-svelte/src/lib/server/corpora.ts` | too many server-side corpus loaders and drill-in helpers in one module |
| 1189 | `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte` | same family of route-local graph + inspector + filtering concerns |
| 1029 | `itir-svelte/src/routes/+page.server.ts` | dashboard daily/range loading, fallback reads, heatmaps, and auto-build behavior collapsed into one loader |
| 943 | `itir-svelte/src/lib/server/wikiTimelineAoo.ts` | normalization, DB/python bridge, HCA overlay behavior, and AAO payload shaping in one server module |
| 894 | `tools/zelph_bin_v3_bucket_builder.cpp` | rebucketing pipeline, temp-record IO, route writing, and Zelph-specific CLI policy mixed together |
| 872 | `itir-svelte/src/routes/graphs/semantic-report/+page.svelte` | report summary, token arc inspection, correction workflow, source document viewer, and graph UI in one route |
| 848 | `itir-svelte/src/lib/sb-dashboard/components/ToolUseSummary.svelte` | command parsing/grouping logic embedded inside the presentational component |
| 790 | `casey-git-clone/scripts/benchmark_casey_vs_git.py` | benchmark scenario definitions, runners, metrics, and report rendering all mixed |
| 674 | `itir_jmd_bridge/runtime.py` | runtime object assembly, graph construction, receipts, and concurrent ingest in one module |
| 634 | `itir-svelte/src/routes/graphs/mission-lens/+page.svelte` | route-level aggregation instead of smaller mission-lens panels/adapters |
| 611 | `casey-git-clone/src/casey_git_clone/cli.py` | all CLI commands and observer wiring packed into one file |
| 581 | `itir-svelte/src/lib/semantic/TokenArcInspector.svelte` | nontrivial semantic-selection and highlighting logic trapped inside a view component |
| 573 | `itir-svelte/tests/factReview_regressions.test.js` | multiple behavioral lanes combined in one regression file |
| 561 | `itir-svelte/src/routes/graphs/wiki-revision-contested/+page.svelte` | route component still owns too much contested-view orchestration |
| 559 | `itir-svelte/src/lib/chat/ToolCallBlock.svelte` | formatting logic and tool-call presentation tightly coupled |
| 538 | `itir-svelte/src/lib/server/semanticReport.ts` | multi-purpose semantic report server logic still aggregated |
| 533 | `casey-git-clone/src/casey_git_clone/runtime_sqlite.py` | schema, metadata, tree, workspace, and build persistence all collapsed together |
| 509 | `itir-svelte/src/routes/graphs/fact-review/+page.svelte` | route owns operator navigation, issue filtering, inspector selection, and source-centric reopen state |

## Main Refactor Themes

### 1. Route files are acting as application runtimes

The biggest `itir-svelte` route files are not just “big UI components.” They
are carrying domain state derivation, graph assembly, evidence filtering,
selection logic, and product/lane-specific policy.

High-signal examples:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`
- `itir-svelte/src/routes/graphs/semantic-report/+page.svelte`
- `itir-svelte/src/routes/graphs/fact-review/+page.svelte`
- `itir-svelte/src/routes/+page.server.ts`

Recommended normal form:

- keep route files as thin composition shells
- move graph-building and filtering logic into `$lib/.../adapters` or
  `$lib/.../view-models`
- move inspector panes and evidence tables into standalone components
- keep selection/highlight logic in dedicated helpers instead of inline route
  reactivity

### 2. “AAO” / corpus-specific naming is leaking into intended shared surfaces

The current `wikiTimelineAoo` family is useful, but the naming still implies
that the core logic belongs to a single corpus/lane when parts of it are
actually generic timeline/event/evidence mechanics.

High-signal examples:

- `itir-svelte/src/lib/server/wikiTimelineAoo.ts`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`

Recommended normalization:

- preserve explicit AAO adapters where the payload really is AAO-specific
- lift generic timeline graph construction, event normalization, evidence lane
  rendering, and HCA overlay policy into neutral modules
- rename “AAO” modules only when the extracted contract is genuinely reusable;
  do not merely cosmetically rename a still-specialized implementation

The guiding rule is:

> if docs describe a general suite capability, the reusable core should not be
> named after one corpus, parser, or historical lane.

### 3. Server-side loader modules are becoming catch-all service bags

Two large examples stand out:

- `itir-svelte/src/lib/server/corpora.ts`
- `itir-svelte/src/routes/+page.server.ts`

`corpora.ts` now bundles:

- processed corpus summaries
- broader diagnostics
- messenger/openrecall readers
- feedback receipt drill-ins
- chat archive overview
- fact-review adjacency

That is several module families, not one.

Recommended split:

- `server/corpora/processed.ts`
- `server/corpora/broader_diagnostics.ts`
- `server/corpora/feedback.ts`
- `server/corpora/chat_archive.ts`
- `server/corpora/messenger.ts`
- `server/corpora/openrecall.ts`

Similarly, `src/routes/+page.server.ts` should split into:

- dashboard payload loading
- daily/range aggregation
- notebook meta loading
- auto-build/backfill policy
- heatmap/stat reducers

### 4. Transport-specific tools are hiding reusable suite contracts

Several of the largest Python/C++ files are large because they mix:

- a general artifact/manifest/ingest contract
- a transport- or product-specific adapter
- a top-level CLI/harness

High-signal examples:

- `tools/zelph_bin_v3_bucket_builder.cpp`
- `tools/build_zelph_hf_manifest.py`
- `tools/build_shared_shard_artifact_contract.py`
- `tools/run_zelph_partial_load_harness.py`
- `itir_jmd_bridge/runtime.py`
- `itir_jmd_bridge/providers/pastebin.py`
- `itir_jmd_bridge/providers/erdfa.py`

Recommended normalization:

- keep shared contract logic in neutral modules
- treat Zelph/HF/IPFS/Pastebin/ERDFA as adapters at the edge
- keep CLI/harness scripts thin and data-driven

This is the same pattern as the AAO issue:
the reusable contract should not inherit a tool- or provider-branded name
unless the contract is truly specific to that tool/provider.

### 5. CLI and storage layers need command/storage decomposition

High-signal examples:

- `casey-git-clone/src/casey_git_clone/cli.py`
- `casey-git-clone/src/casey_git_clone/runtime_sqlite.py`
- `casey-git-clone/scripts/benchmark_casey_vs_git.py`

Recommended split:

- command handlers per command family under `commands/`
- observer/renderer helpers outside the top-level CLI file
- sqlite persistence split by domain:
  schema, metadata, trees, workspaces, builds
- benchmark scenario/runners/metrics/reporting separated into distinct modules

### 6. Presentational components are carrying parser/reducer logic

High-signal examples:

- `itir-svelte/src/lib/sb-dashboard/components/ToolUseSummary.svelte`
- `itir-svelte/src/lib/semantic/TokenArcInspector.svelte`

Recommended split:

- move parsing/grouping/highlighting logic into pure TS helpers
- keep `.svelte` files focused on display and interactions
- make parser/reducer logic independently testable without component mounting

## File-Specific Extraction Candidates

### `scripts/chat_context_resolver.py`

Current mixed concerns:

- selector parsing and DB resolution
- live fallback via external tool/web path
- transcript stitching and cross-thread analysis
- result formatting
- CLI option registration and main orchestration

Recommended modules:

- `resolver/db_lookup.py`
- `resolver/live_provider.py`
- `resolver/analysis.py`
- `resolver/formatters.py`
- `resolver/cli.py`

Important naming correction:

- hide `re_gpt` behind a neutral “live chat provider” interface

### `itir-svelte/src/lib/server/wikiTimelineAoo.ts`

Current mixed concerns:

- payload normalization
- python bridge execution
- DB path/env resolution
- HCA overlay handling
- AAO payload-specific shaping

Recommended split:

- `server/wiki_timeline/runtime.ts`
- `server/wiki_timeline/normalize.ts`
- `server/wiki_timeline/hca_overlay.ts`
- `server/wiki_timeline/aoo_adapter.ts`

### `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`

Current mixed concerns:

- graph lane/filter state
- node/edge assembly helpers
- evidence/source/lens toggles
- context tables
- corpus-doc linking

Recommended split:

- `WikiTimelineGraphControls.svelte`
- `WikiTimelineContextPanel.svelte`
- `WikiTimelineEvidencePanel.svelte`
- `wikiTimelineGraph.ts`
- `wikiTimelineSelection.ts`

### `itir-svelte/src/lib/server/corpora.ts`

Current mixed concerns:

- corpus home overview
- processed personal corpus summaries
- broader diagnostics details
- feedback receipt loading and drill-ins
- messenger/openrecall/chat archive readers

Recommended split:

- `server/corpora/home.ts`
- `server/corpora/personal_processed.ts`
- `server/corpora/broader_diagnostics.ts`
- `server/corpora/feedback_receipts.ts`
- `server/corpora/messenger.ts`
- `server/corpora/openrecall.ts`
- `server/corpora/chat_archive.ts`

### `itir-svelte/src/routes/+page.server.ts`

Current mixed concerns:

- date/range validation
- DB/file fallback loading
- NotebookLM metadata recovery
- dashboard auto-build policy
- heatmap and aggregate reducers

Recommended split:

- `server/dashboard/loaders.ts`
- `server/dashboard/notebook_meta.ts`
- `server/dashboard/range_aggregation.ts`
- `server/dashboard/heatmaps.ts`
- `server/dashboard/autobuild.ts`

### `tools/zelph_bin_v3_bucket_builder.cpp`

Current mixed concerns:

- temp record IO
- rebucketing
- chunk emission
- route index writing
- Zelph-specific CLI layout assumptions

Recommended split:

- `bucket_io.*`
- `rebucketing.*`
- `chunk_emitters.*`
- `route_index.*`
- thin `zelph_bin_v3_bucket_builder.cpp` CLI wrapper

### `tools/build_zelph_hf_manifest.py` and `tools/build_shared_shard_artifact_contract.py`

Refactor together, not separately.

Reason:

- both are converging on a shared artifact/manifest layer
- one is still branded around Zelph/HF
- the other is already closer to the transport-neutral contract

Recommended direction:

- neutral shared shard/manifest core
- HF projection adapter
- Zelph manifest adapter
- CLI entrypoints that only compose those pieces

### `itir_jmd_bridge/runtime.py`

Current mixed concerns:

- runtime object construction
- graph derivation
- receipt derivation
- browse-list ingestion/concurrency

Recommended split:

- `runtime_object.py`
- `runtime_graph.py`
- `runtime_receipt.py`
- `runtime_ingest.py`

### `itir_jmd_bridge/providers/erdfa.py`

Current mixed concerns:

- CBOR decoding
- ERDFA decode/summary
- archive-to-graph derivation

Recommended split:

- `providers/cbor_minimal.py`
- `providers/erdfa_decode.py`
- `providers/erdfa_archive.py`

### `casey-git-clone/src/casey_git_clone/cli.py`

Recommended split:

- `commands/init.py`
- `commands/publish.py`
- `commands/sync.py`
- `commands/collapse.py`
- `commands/build.py`
- `commands/export.py`
- `commands/advise.py`
- `observer_cli.py`

### `casey-git-clone/src/casey_git_clone/runtime_sqlite.py`

Recommended split:

- `db/schema.py`
- `db/meta.py`
- `db/trees.py`
- `db/workspaces.py`
- `db/builds.py`

## Priority Order

### Priority 1: generalization + naming hygiene

These give the best payoff because they reduce future drift between docs and
code boundaries:

1. `scripts/chat_context_resolver.py`
2. `itir-svelte/src/lib/server/wikiTimelineAoo.ts`
3. `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`
4. `tools/build_zelph_hf_manifest.py` + `tools/build_shared_shard_artifact_contract.py`
5. `itir_jmd_bridge/runtime.py`

## Pre-Triage Rule

For each candidate in the priority list, triage starts only after a bounded
refactor brief exists.

Minimum pre-triage brief fields:

1. `Current surface`
2. `Reusable core to preserve or extract`
3. `Specialized adapter/overlay that should remain explicit`
4. `Files/modules expected after split`
5. `Tests or checks that prove the split did not widen behavior`

Preferred shape:

```md
## <target file>
- Why this file is overloaded
- What is genuinely generic here
- What must stay lane-specific
- Proposed module split
- Acceptance checks
```

This keeps the workflow explicit:

- docs first
- then triage
- then implementation

Without that brief, triage is premature.

### Priority 2: frontend/server decomposition

1. `itir-svelte/src/lib/server/corpora.ts`
2. `itir-svelte/src/routes/+page.server.ts`
3. `itir-svelte/src/routes/graphs/semantic-report/+page.svelte`
4. `itir-svelte/src/routes/graphs/fact-review/+page.svelte`
5. `itir-svelte/src/lib/sb-dashboard/components/ToolUseSummary.svelte`

### Priority 3: package-local cleanup

1. `casey-git-clone/src/casey_git_clone/cli.py`
2. `casey-git-clone/src/casey_git_clone/runtime_sqlite.py`
3. `casey-git-clone/scripts/benchmark_casey_vs_git.py`
4. test-file splits in `itir-svelte` and `casey-git-clone`

## Governance Rule For Future Refactors

Before extracting or renaming anything in this roadmap, check:

1. Is the target contract actually reused or clearly meant to be reusable?
2. If yes, does the name still carry one corpus/tool/provider’s accidental
   history?
3. If yes, extract the reusable core first, then leave a thin named adapter
   for the specialized lane.

This avoids the two common failure modes:

- premature “generic” renaming of still-specialized code
- leaving a genuinely shared contract trapped behind one lane’s historical name

## Recommended Next Execution Slice

The next bounded repo-wide refactor slice should be:

1. extract a neutral wiki timeline server/runtime core from the current
   `wikiTimelineAoo` family
2. extract a neutral manifest/shard core from the current Zelph/HF builders
3. split `scripts/chat_context_resolver.py` into resolver, live-provider,
   analysis, and CLI modules

That sequence hits the biggest current boundary mismatch:

- the docs describe a general suite
- several large files still encode one-lane or one-provider history in the
  reusable core
