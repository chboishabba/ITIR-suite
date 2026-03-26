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
- tool family is read-only and deterministic
- wider ITIR/timeline/capture surfaces are deferred until the transport and
  Dioxus client seam are verified

## Bridge Operations (Persistent Session)

- `health`: readiness and contract metadata
- `info`: contract/runtime metadata for clients
- `list`: stable tool specs
- `call`: tool invocation (`name`, `payload`)

Every response is wrapped as:

- success: `{"ok": true, "result": {...}}` or tool-specific containers
- failure: `{"ok": false, "error": {"code": "input_error", ...}}`

## Guardrails

- no canonical producer semantics are redefined here
- no broad mutable operations in the first increment
- browser `dioxus/web` must not be treated as a direct stdio MCP host
