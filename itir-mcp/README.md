# itir-mcp

`itir-mcp` is the suite-level MCP adapter project for `ITIR-suite`.

It exists to expose bounded, namespaced tools/resources over existing producer
logic without taking canonical ownership away from the underlying components.

## Scope

Current scope:
- local tool/spec registry
- SensibLaw-first read-only tool adapters
- bounded ITIR-native observation comparison tools for cross-project sensing lanes
- optional FastMCP transport when the Python MCP SDK is available
- persistent JSON bridge protocol for `dioxus` via `python -m itir_mcp --bridge`

Not in scope for the first increment:
- broad mutable actions
- direct browser-WASM transport for Dioxus web
- redefining component schemas or producer semantics

## Initial tool family

- `sensiblaw.obligations_query`
- `sensiblaw.obligations_explain`
- `sensiblaw.obligations_alignment`
- `sensiblaw.obligations_projection`
- `sensiblaw.obligations_activate`
- `itir.compare_observations`
- `itir.score_coherence`
- `itir.build_envelope`

Planned next family, not yet implemented:

- `itir.windows.collect_registry`
- `itir.windows.collect_policy_state`
- `itir.windows.collect_service_state`
- `itir.windows.collect_local_security_state`
- `itir.windows.collect_eventlog_state`
- `itir.windows.evaluate_profile`
- `itir.windows.plan_remediation`
- `itir.windows.apply_remediation`
- `itir.linux.collect_state`
- `itir.linux.evaluate_profile`
- `itir.linux.plan_remediation`
- `itir.linux.apply_remediation`

Adjacent planned discovery family, also not yet implemented:

- `itir.discovery.collect_public_repo_surface`
- `itir.discovery.collect_repo_workflow_surface`
- `itir.discovery.evaluate_repo_risk`
- `itir.discovery.plan_internal_exposure_check`

## External producer posture

`itir-mcp` is also the bounded comparison seam for external producer lanes such
as WorldMonitor and OpenRecall.

- WorldMonitor should consume these tools through its existing MCP/plugin seam
  rather than copying ITIR comparison logic into TypeScript.
- OpenRecall may consume the same tool family through an MCP client wrapper;
  today that wrapper uses the local `itir-mcp --bridge` JSON transport while
  keeping the same canonical tool names.

MCP is the primary contract layer. Bridge/HTTP shells are transport details,
not alternate semantics.

For the planned Windows endpoint lane, the contract doctrine is:

- observe
- evaluate
- plan
- act

Only the first two should be easy by default. Action remains deliberately
harder and must stay subordinate to policy, receipts, and bounded scope.

The planned Linux endpoint lane follows the same doctrine, but over a
distributed configuration substrate:

- files
- services
- kernel state
- firewall/network state
- package/runtime state

It is the same managed-host trust model as Windows, not a lower-trust
discovery lane.

For the planned public discovery lane, the trust model is intentionally lower:

- public discovery proposes risk
- internal evidence authorizes action

That lane is for candidate findings and follow obligations, not autonomous
enforcement.

## Development

Run local tests:

```bash
pytest itir-mcp/tests -q
```

If you want to run the optional FastMCP transport bridge, install the transport
extra first:

```bash
pip install -e itir-mcp[transport]
python -m itir_mcp
```

For the long-lived JSON bridge used by native Dioxus:

```bash
python -m itir_mcp --bridge
```

Bridge operations now include:

- `call`: raw deterministic tool invocation
- `safe_call`: guarded invocation with pre-call classification, post-call
  verification, and a governance receipt

Tool responses and failures are wrapped in the same envelope schema for both HTTP
bridges and local adapters:

```json
{"ok": true, "result": {...}}
{"ok": false, "error": {"code": "input_error", "message": "...", "details": {...}}}
```

For guarded invocations, `result` carries:

- `classification`
- `verification`
- `policy_outcomes`
- `status_explanation`
- `receipt`
- `decision`

Doctrine: all tool outputs are proposals until verified.

## Relationship to Dioxus

`itir-mcp` is the suite adapter/server side of the boundary. For Dioxus:

- `dioxus/web` should call a backend/native seam that talks to this adapter
- existing internal Dioxus MCP-like registries remain useful UI/debug surfaces
  but are not the canonical suite transport layer
