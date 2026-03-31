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
- Added read-only `chat_export_structurer.*` archive lookup tools for thread resolution,
  FTS search, and canonical thread message retrieval
- Hardened the archive adapter against older SQLite schemas that do not yet include
  `source_thread_id` / `source_message_id`
- Hardened persistent bridge protocol behavior with:
  - deterministic tool ordering for `list`
  - explicit `protocol_error` for non-object request payloads
  - optional `request_id` echo on valid requests for response correlation
  - fixture-backed protocol coverage for request correlation and invalid request objects
