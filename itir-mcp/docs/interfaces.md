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
- bounded execution telemetry when a tool exposes job-status state

## Job-Status Surface

When a producer-owned tool exposes job status, that surface is treated as
execution telemetry for control flow only.

- job status may report bounded runtime state such as queued, running,
  completed, failed, cancelled, progress markers, timestamps, and opaque job
  identifiers
- job status is not canonical policy evidence
- job status is not legal/compliance reasoning output
- job status must not be consumed as document authority, factual proof, or
  admissibility evidence
- any producer-owned evidence surface must remain separately versioned and
  explicitly namespaced in the tool result contract

This keeps execution control telemetry distinct from evidence-bearing producer
artifacts.

## Current provider posture

- `SensibLaw` is the first provider lane
- tool family is read-only and deterministic
- wider ITIR/timeline/capture surfaces are deferred until the transport and
  Dioxus client seam are verified
- execution telemetry may be exposed as read-only status projection, but must
  remain orthogonal to policy evidence and answer correctness

## Bridge Operations (Persistent Session)

- `health`: readiness and contract metadata
- `info`: contract/runtime metadata for clients
- `list`: stable tool specs
- `call`: tool invocation (`name`, `payload`)

Every response is wrapped as:

- success: `{"ok": true, "result": {...}}` or tool-specific containers
- failure: `{"ok": false, "error": {"code": "input_error", ...}}`

## Current tool families

- obligations:
  - deterministic read-only query/explain/alignment/projection/activation
- ITIR job status:
  - deterministic read-only projection over existing progress/checkpoint state
  - intended for execution control decisions such as wait/cancel/resume timing
  - not intended as policy, routing, admissibility, or correctness evidence

## Guardrails

- no canonical producer semantics are redefined here
- no broad mutable operations in the first increment
- browser `dioxus/web` must not be treated as a direct stdio MCP host
- execution status must not be treated as route or policy evidence
- execution telemetry must not be reinterpreted as policy or evidence
