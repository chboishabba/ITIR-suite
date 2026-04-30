# ITIR MCP + Dioxus Contract (2026-03-26)

This note defines the first concrete MCP surface for `ITIR-suite` and the
corresponding Dioxus integration posture.

It is a contract/planning artifact, not a claim that the full transport or all
tools already exist.

## ZKP Frame

O:
- User + repository owner decide the suite-level boundary and promotion rules.
- `ITIR-suite` is the control plane for cross-project contracts.
- `SensibLaw` owns deterministic legal/domain logic and existing HTTP surfaces.
- `ITIR` owns cross-project coordination and read-safe orchestration.
- `solfunmeme-dioxus` is an existing Rust UI/runtime with an internal
  MCP-shaped registry but not yet a full MCP transport implementation.

R:
- Add a governed MCP lane without rewriting component internals.
- Keep component ownership intact: MCP must be an adapter over existing domain
  logic, not a replacement authority surface.
- Start with deterministic, read-only, narrow tools.
- Keep browser-WASM transport constraints explicit: Dioxus web must not assume
  direct stdio MCP execution.

C:
- `ITIR-suite/docs/planning/*`
- `ITIR-suite/README.md`
- `ITIR-suite/TODO.md`
- `ITIR-suite/__CONTEXT/COMPACTIFIED_CONTEXT.md`
- new root package directory `ITIR-suite/itir-mcp/`
- existing producer logic in `SensibLaw/`
- future consumer/gateway work in `solfunmeme-dioxus/`

S:
- `SensibLaw` already exposes useful programmatic surfaces through FastAPI
  routes and underlying Python functions.
- `ITIR-suite` already enforces explicit interface contracts and control-plane
  planning before implementation.
- `solfunmeme-dioxus` already has an internal registry/playground shape for
  MCP-like tools, but it is not itself a suite MCP transport/server/client.
- No suite-level MCP server directory currently exists in `ITIR-suite`.
- Root `ITIR-suite` currently has no `CHANGELOG.md`.

L:
- vague intent -> contract note
- contract note -> repo scaffold
- scaffold -> deterministic tool adapters
- deterministic tool adapters -> verified stdio/server transport
- verified transport -> Dioxus backend/native client integration
- backend/native integration -> optional wider ITIR read-model expansion

P:
- P1: Create a new root project `itir-mcp/` as the suite-level MCP adapter.
  - Why: keeps MCP transport/orchestration separate from component internals.
  - Evidence needed: scaffold compiles/imports cleanly and documents exact
    ownership boundaries.
  - Promotion blockers: unclear contract or accidental authority drift.
- P2: Make `SensibLaw` the first real tool provider.
  - Why: it already has deterministic read-oriented API/domain surfaces.
  - Evidence needed: wrapper functions call existing logic without duplicating
    semantics.
  - Promotion blockers: route-only logic that must be factored down first.
- P3: Integrate Dioxus through a backend/native gateway, not direct browser
  transport.
  - Why: `dioxus/web` cannot directly host stdio MCP servers.
  - Evidence needed: one backend-facing endpoint or native runner can list and
    invoke suite tools.
  - Promotion blockers: trying to bind web WASM directly to stdio MCP.

G:
- Docs -> TODO -> code -> changelog sequencing is mandatory.
- New cross-project behavior must be declared via suite contracts before code.
- The first MCP lane must remain read-only and deterministic unless a later
  contract explicitly broadens authority.
- Validation gate for this phase:
  - suite docs mention the new lane
  - TODO reflects next executable milestones
  - `itir-mcp` scaffold exists
  - tests pass for local pure-Python scaffold surfaces

F:
- Missing suite-level MCP package/scaffold.
- Missing explicit contract tying MCP transport to the existing interface
  doctrine.
- Missing Dioxus integration boundary note at the suite level.
- Missing root changelog to record the new interface/workflow surface.

Synthesis:
- The correct first move is a suite-level MCP adapter project rooted in
  `itir-mcp/`, with SensibLaw-first read-only tools and a Dioxus backend/native
  integration posture.

Adequacy:
- adequate for implementation of the first scaffold

Next action:
- update root docs/TODO/context to freeze this contract, then create the
  `itir-mcp/` scaffold and first SensibLaw-backed tool registry.

## Contract

### 1. Ownership and boundary

- `SensibLaw`, `tircorder-JOBBIE`, `StatiBaker`, and other components keep
  ownership of their internal logic and schemas.
- `itir-mcp` is a suite adapter layer:
  - transport
  - tool/resource declarations
  - cross-component namespacing
  - lightweight orchestration
- `itir-mcp` must not redefine canonical meaning for producer components.

### 2. First tool lane

Initial suite tool namespace should prefer explicit producer prefixes:

- `sensiblaw.obligations_query`
- `sensiblaw.obligations_explain`
- `sensiblaw.obligations_alignment`
- `sensiblaw.obligations_projection`
- `sensiblaw.obligations_activate`

For ITIR-owned cross-project comparison semantics, the next bounded family is:

- `itir.compare_observations`
- `itir.score_coherence`
- `itir.build_envelope`

The first phase should avoid broad mutable operations and should not expose raw
UI control surfaces.

### 3. Dioxus integration posture

- `dioxus/web` must use an HTTP/WebSocket/backend mediation layer.
- desktop/native/fullstack Rust may host an MCP client directly.
- existing `solfunmeme-dioxus` MCP-like registry remains useful as an internal
  UI/debug layer, but is not the transport contract for the suite.

### 4. Suggested directory shape

```text
itir-mcp/
  README.md
  CHANGELOG.md
  pyproject.toml
  docs/
    interfaces.md
  src/itir_mcp/
    __init__.py
    contracts.py
    registry.py
    sensiblaw_tools.py
    server.py
  tests/
```

### 5. Promotion criteria for the next increment

- At least one tool family is callable through the package boundary.
- Tool naming is namespaced and stable.
- The scaffold has tests for registry/spec behavior.
- The read-only posture is explicit in docs and code comments.
- Future Dioxus work can target one declared backend/native seam rather than an
  ambiguous direct-web transport idea.
