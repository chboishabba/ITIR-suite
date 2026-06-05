# Changelog

## Unreleased
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
