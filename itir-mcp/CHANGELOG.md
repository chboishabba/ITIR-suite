# Changelog

## Unreleased
- Added the initial `itir-mcp` scaffold with:
  - a namespaced tool/spec registry
  - SensibLaw-backed read-only tool adapters
  - an optional `FastMCP` bridge for stdio transport
  - local tests for registry behavior and a deterministic obligations query path
- Added a persistent JSON bridge protocol for native consumers (`python -m itir_mcp --bridge`)
- Added structured tool envelopes and explicit input/execution error codes
- Added versioned `health` / `version` metadata to support Dioxus bridge hardening
