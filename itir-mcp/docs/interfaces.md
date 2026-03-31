# itir-mcp Interface Contract

## Role

`itir-mcp` is a suite adapter layer. It exposes producer-owned capabilities as
bounded MCP tools/resources while preserving producer ownership and canonical
schema authority.

## Ingress

- local Python calls into producer-owned domain functions
- optional MCP stdio transport via the Python MCP SDK
- persistent local JSON bridge protocol for native Rust/Dioxus clients

## Egress

- namespaced tool list
- tool version metadata on each spec (`response_version`)
- deterministic JSON-like result envelopes
- deterministic JSON-like result payloads
- explicit tool invocation errors

## Current provider posture

- `SensibLaw` is the first provider lane
- `chat-export-structurer` now exposes read-only archive lookup tools
- archive lookup tools support optional per-platform filtering via `platform`
  (for example `telegram`, `discord`, `facebook`, `messenger`)
- tool family is read-only and deterministic
- wider ITIR/timeline/capture surfaces are deferred until the transport and
  Dioxus client seam are verified

## Chat Archive Tool Notes

`chat_export_structurer.resolve_thread`
- Required: `selector`
- Optional: `db_path`, `allow_canonical_match`, `platform`

`chat_export_structurer.search_threads`
- Required: `selector`
- Optional: `db_path`, `limit`, `platform`

`chat_export_structurer.thread_messages`
- Required: `canonical_thread_id`
- Optional: `db_path`, `limit`, `platform`

The `platform` filter is pass-through archive scoping. It does not impose a
fixed enum at the MCP layer; any platform label present in the underlying
archive can be queried.

## Bridge Operations (Persistent Session)

- `health`: readiness and contract metadata
- `info`: contract/runtime metadata for clients
- `list`: stable tool specs
- `call`: tool invocation (`name`, `payload`)

If present on a valid request object, `request_id` is echoed in the response.
This gives native clients deterministic request/response correlation across a
persistent bridge session.

Every response is wrapped as:

- success: `{"ok": true, "result": {...}}` or tool-specific containers
- failure: `{"ok": false, "error": {"code": "input_error", ...}}`

## Guardrails

- no canonical producer semantics are redefined here
- no broad mutable operations in the first increment
- browser `dioxus/web` must not be treated as a direct stdio MCP host
