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

- `SensibLaw` remains the first producer-backed provider lane
- `ITIR` also exposes a small read-only comparison family for bounded external
  observation lanes
- tool families remain read-only and deterministic
- wider mutable timeline/capture surfaces are still deferred until the
  transport and client seams are verified
- execution telemetry may be exposed as read-only status projection, but must
  remain orthogonal to policy evidence and answer correctness

## Bridge Operations (Persistent Session)

- `health`: readiness and contract metadata
- `info`: contract/runtime metadata for clients
- `list`: stable tool specs
- `call`: tool invocation (`name`, `payload`)
- `safe_call`: guarded tool invocation (`name`, `payload`) with pre-call
  classification, post-call verification, and a governance receipt

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
For `safe_call`, the wrapped `result` is a stable decision envelope:

- `version`: guarded invocation contract version
- `tool`: canonical tool name
- `decision`: `verified`, `abstained`, or `rejected`
- `classification`: pre-call guard classification payload
- `verification`: post-call verification payload when a call completed
- `policy_outcomes`: normalized control/rule outcomes derived from the shared
  reason-code vocabulary
- `status_explanation`: normalized explanation surface for operator/readout
  consumers
- `receipt`: governance/audit receipt with input hash and policy id
- `result`: verified tool payload, or `null` when blocked/abstained

## Guardrails

- no canonical producer semantics are redefined here
- no broad mutable operations in the first increment
- browser `dioxus/web` must not be treated as a direct stdio MCP host
- execution status must not be treated as route or policy evidence
- execution telemetry must not be reinterpreted as policy or evidence
- all tool outputs are proposals until verified
- guarded rejection is expected for clear prompt-injection, social-engineering,
  or sensitive-data exfiltration attempts
- guarded abstention is expected when the returned payload does not satisfy the
  declared tool contract strongly enough to promote

## Comparison tool lane

The first ITIR-owned non-SensibLaw family is the bounded observation
comparison lane:

- `itir.compare_observations`
- `itir.score_coherence`
- `itir.build_envelope`

These tools exist to normalize observation comparison semantics once, then let
different clients consume them over MCP/bridge/API transports without
duplicating logic.

Expected clients:

- WorldMonitor via its native MCP/plugin seam
- OpenRecall via a thin Python bridge/API client
- other suite consumers through the same stable envelopes

For clients that need bounded policy visibility (for example, operator-facing
risk flags), use `safe_call` and consume the normalized `status_explanation`
object as `policy_hint`. This keeps ITIR output explicit, non-authoritative by
default, and suitable for presentation-only workflow guidance.

## Planned Windows compliance lane

The next planned systems-facing family is a Windows endpoint compliance lane.
This is a contract target only, not an implemented tool family yet.

Intended tools:

- `itir.windows.collect_registry`
- `itir.windows.collect_policy_state`
- `itir.windows.collect_service_state`
- `itir.windows.collect_local_security_state`
- `itir.windows.collect_eventlog_state`
- `itir.windows.evaluate_profile`
- `itir.windows.plan_remediation`
- `itir.windows.apply_remediation`

Intended posture:

- evidence tools are read-only and deterministic
- evaluation tools consume normalized evidence plus executable control profiles
- planning tools emit structured remediation proposals with rollback
- action tools are heavily gated and must remain harder than observation or
  evaluation

The canonical flow for that lane is:

- endpoint state
- evidence snapshot
- policy evaluation
- compliance result
- optional remediation plan
- optional approved action

This family should reuse the same guarded doctrine already documented for
`safe_call`: all outputs are proposals until verified, and consequential action
requires receipts plus policy success.

## Planned Linux compliance lane

The adjacent planned systems-facing family is a Linux endpoint compliance lane.
This is also a contract target only, not an implemented tool family yet.

Intended tools:

- `itir.linux.collect_state`
- `itir.linux.evaluate_profile`
- `itir.linux.plan_remediation`
- `itir.linux.apply_remediation`

Intended posture:

- evidence collection remains read-only and deterministic
- Linux host state is normalized across files, services, kernel, network, and
  runtime surfaces
- evaluation tools consume normalized evidence plus executable control profiles
- planning tools emit structured remediation proposals with rollback
- action tools are heavily gated and must remain harder than observation or
  evaluation

This family is a higher-trust managed-host lane, like the Windows lane.

## Planned public repo security discovery lane

The adjacent planned lower-trust family is a public repo/security-surface
discovery lane. This is also a contract target only, not an implemented tool
family yet.

Intended tools:

- `itir.discovery.collect_public_repo_surface`
- `itir.discovery.collect_repo_workflow_surface`
- `itir.discovery.evaluate_repo_risk`
- `itir.discovery.plan_internal_exposure_check`

Intended posture:

- public sources may produce candidate findings only
- findings must preserve provenance and evidence references
- the lane may open follow obligations or exposure checks
- the lane must not directly authorize remediation or exploitability claims as
  fact

The canonical doctrine for this lane is:

- public discovery proposes risk
- internal evidence authorizes action
