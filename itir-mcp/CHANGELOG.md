# Changelog

## Unreleased
- Implemented the approved RPD PNF hierarchy slice on a branch based at main `cf4ae65`: removed the active hardcoded conversational predicate set and replaced lexical head admission with SensibLaw parser POS evidence plus DF/N and Marchenko–Pastur candidate evidence.
- Added K=50/K=100 hierarchy metadata validation, canonical invariant-fibre bundles with Yang–Mills root `Q271810` / fibre `F_YM`, non-promoting adjacent-branch invariant routing, and explicit ontology/AST authority boundaries.
- Added SensibLaw Wikimedia provider reuse for Wiktionary/Wikidata candidate grounding, permanent-QID projection, candidate-only `cand:Q_*` minting with P279/P361 anchors and observational P2738 audit attachment, plus bounded P279/P361 DAG walking and verified-lemma route candidates.
- Preserved the live `execute_pareto_conductor`, `spawn_parallel_lanes`, and `conductor_topic_cost` contracts; added a deterministic 20-worker × 20-round barrier planner with explicit pairwise `noTypedMeet` receipts and a hard 20-lane dispatch cap.
- Added focused AO/PNF discriminator regressions and a branch-specific exact-head workflow. Local checkout remains unavailable because the runtime cannot resolve github.com; no green test claim is made until the workflow produces a receipt.
- Added `itir.shard.bounded_graph_slice_plan`, a generic non-fetching plan
  surface that reports selected logical coverage and declared payload cost
  before a consumer decides to retrieve graph shard bytes.
- add a generic bounded graph-slice transport view over revision-bound HF/Zelph
  manifest contracts. It records the selected logical shard plan and declared
  byte cost without fetching graph payloads, and remains explicitly incomplete,
  candidate-only, and non-authoritative.
- Added `itir_mcp.pnf_numeric_abi`, a narrow receipt-bearing
  `itir.pnf.numeric_abi.v0_1` GEMV validation/parity helper. This is diagnostic
  adapter plumbing only and does not materialize spectral PNF state,
  eigenvectors, support authority, routing, or promotion.
- Added the read-only PNF MCP family:
  - `itir.pnf.context_index`
  - `itir.pnf.task_memory_preview`
  - `itir.pnf.observer_evidence`
- Added OpenRecall/browser-assist observer evidence handling for PNF residuals
  without task, runsheet, or Kanboard mutation.
- Added the docstore/Obsidian MCP family:
  - `itir.docstore.status`
  - `itir.docstore.open_questions`
  - `itir.obsidian.vault_scan`
  - `itir.docstore.proposal_receipt`
  - `itir.markdown.render_projection`
  - `itir.markdown.write_projection`
  - `itir.docstore.config_plan`
- Added producer-pressure adapters for SensibLaw review/operator surfaces,
  StatiBaker dashboard/codex traces, and explicit generated-artifact
  normalized-artifact gaps.
- Added generated Markdown projection rendering/writing for
  `_ITIR/generated/...` pages with replaceable generated blocks.
- Added an Obsidian plugin scaffold under `obsidian-itir-plugin/` with bundle
  export, settings, status pane commands, and refresh actions.
- Added the initial `itir-mcp` scaffold with:
  - a namespaced tool/spec registry
  - SensibLaw-backed read-only tool adapters
  - an optional `FastMCP` bridge for stdio transport
  - local tests for registry behavior and a deterministic obligations query path
- Added a persistent JSON bridge protocol for native consumers (`python -m itir_mcp --bridge`)
- Added structured tool envelopes and explicit input/execution error codes
- Added versioned `health` / `version` metadata to support Dioxus bridge hardening
