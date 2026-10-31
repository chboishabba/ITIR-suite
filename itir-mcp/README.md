# itir-mcp

`itir-mcp` is the suite-level MCP adapter project for `ITIR-suite`.

It exists to expose bounded, namespaced tools/resources over existing producer
logic without taking canonical ownership away from the underlying components.

## Scope

Current scope:
- local tool/spec registry
- SensibLaw-first read-only tool adapters
- bounded ITIR-native observation comparison tools for cross-project sensing lanes
- docstore-wide status, open-question, Obsidian observer, proposal-receipt,
  Markdown projection, and bounded config-plan tools
- read-only PNF task/context projection tools over SensibLaw/StatiBaker
  producer schemas
- optional FastMCP transport when the Python MCP SDK is available
- persistent JSON bridge protocol for `dioxus` via `python -m itir_mcp --bridge`

### External graph transport

The shard transport module can fetch a published HF/Zelph manifest and produce
a generic bounded graph-slice view from explicit logical selectors. This is a
transport/provenance result: it records manifest revision, selected sections,
selected chunks, and declared bytes without fetching the shard payloads. The
caller must receive that declared selected-payload cost before it chooses to
fetch graph payloads; logical selection is not a promise that the currently
coarse physical shards are small.

A bounded slice defaults to `incomplete`, candidate-only, and non-authoritative.
It must not be described as exhaustive merely because its manifest was fetched
or its selectors resolved. SensibLaw consumes this normalized result as an
external graph view; it owns the later local bridge/decision/pressure carrier.

The registry exposes that non-fetching decision point as
`itir.shard.bounded_graph_slice_plan`. It accepts a normalized shard contract
and logical selectors, then returns the selected sections/shards, exact
declared bytes, a binary-unit display value, and `payload_fetch: false`.

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
- `itir.docstore.status`
- `itir.docstore.open_questions`
- `itir.obsidian.vault_scan`
- `itir.docstore.proposal_receipt`
- `itir.pnf.context_index`
- `itir.pnf.task_memory_preview`
- `itir.pnf.observer_evidence`
- `itir.pnf.work_packet`
- `itir.pnf.governed_handoff`
- `itir.pnf.multi_parent_handoff`
- `itir.pnf.residual_cases`
- `itir.archive.thread_view`
- `itir.ao.operation_review`
- `itir.chatgpt.operation_receipts`
- `itir.chatgpt.revive_multi`
- `itir.markdown.render_projection`
- `itir.markdown.write_projection`
- `itir.docstore.config_plan`

## Governed ChatGPT worker lane

`itir-mcp` owns the fleet-facing ChatGPT worker boundary. Callers use
`itir.chatgpt.dispatch_worker`, `itir.chatgpt.operation_status`, and
`itir.chatgpt.reconcile` rather than constructing a `re-gpt` CLI command.
The adapter delegates to the local re-gpt public API with direct async writes,
DOM fallback disabled, and receipt-bearing operation state. It does not expose
browser/session bootstrap controls and never resends an uncertain operation.
A normal worker dispatch is event-driven: the caller awaits its completion
result and does not poll while it is in flight or require a user wake-up. The
caller may complete independent work while waiting, otherwise waits silently.
`operation_status` and `reconcile` are recovery tools for an uncertain or
interrupted operation, not routine liveness checks.

ChatGPT is the normal low-cost worker for a major coherent implementation cut.
Keep tiny local fixes, bounded review repairs, test-harness adjustments, and
verification plumbing in the calling Codex/AO lane rather than creating a
worker round-trip. A report-only dispatch is an intentional phase gate:
require the worker to establish the applicable
roadmap, phase, deliverables/acceptance state, ZKP frame, and relevant
Agda/Lean proof surfaces from repository evidence. Do not impose an arbitrary
word cap on that report. A subsequent implementation dispatch should deliver
the largest coherent max-cut supported by the gate, not a needlessly tiny
patch. Every nontrivial brief carries the full `O/R/C/S/L/P/G/F` frame and
material constraints, invariants, preconditions, and postconditions; it names
the owner, disjoint write surface, post-worker verification phase, and a
measurable refinement criterion. The ChatGPT connector returns the branch/PR, intended verification
commands, and its execution boundary; it is not asked to run local tests,
assume a mounted checkout, or use GitHub Actions. Before dispatch, the calling
lane inspects available local clones and supplies the exact GitHub
repository/branch, current schema/API facts, roadmap paths, and intended
local/Colab acceptance commands. The connector uses its GitHub integration
against those named targets rather than guessing a repository mapping. The
calling Codex/AO lane
runs applicable tests or formal checks locally or in Colab. An operation or PR
receipt alone is not acceptance. Once accepted, the calling lane merges and
pushes the branch to the authoritative target before dispatching dependent
workers, so they build on checked current code.

High-RAM Colab is the escalation path for Lean/Agda or another demonstrated
memory-heavy verification need; ordinary Python/MCP tests stay local.

Use plain language and proportional accessibility requirements for
human-facing artifacts. Agents may propose a visualization or visual proof
when it materially clarifies a difficult relation, but require explicit human
approval before creating one; an approved artifact is inspected before any
claim based on it is promoted.

For ZKP-framed worker briefs and receipts, use the canonical model without
renaming or collapsing fields: `O` Organization, `R` RFP, `C` Code, `S` State,
`L` Lattice, `P` Proposal, `G` Governance, and `F` Gap function. In
particular, governance is a separate promotion/control surface, not part of
the gap function.

## Multi-parent revival

The read-only `itir.pnf.multi_parent_handoff` accepts 2–10 distinct canonical thread IDs and returns separate bounded parent projections plus a candidate-only reference world. Save that result to an explicit caller-owned artifact path, then use `itir.chatgpt.revive_multi` to create one fresh ChatGPT conversation and attach that artifact over direct async CFFI. Ordered canonical parent IDs and the attachment operation receipt are retained in the re-gpt operational lineage receipt store; that store is not corpus authority. Unavailable SensibLaw public parsing abstains. No cross-parent equivalence, parent retirement, automatic retry, or selected-context sufficiency proof is inferred.

See `docs/planning/governed_revival_handoff_v1.md` for the complete contract and referee commands.

## Numeric ABI

`itir_mcp.pnf_numeric_abi` is a narrow receipt-bearing numeric ABI for
diagnostic GEMV parity. It validates `itir.pnf.numeric_abi.v0_1` payloads with
`float32` vectors, a square row-major `A`, optional `b`, and a receipt-bearing
`row_map`, then exposes a deterministic CPU GEMV and parity hash.

This is plumbing, not spectral materialization. Callers such as Mirror's
daily-summary `numeric-abi-smoke` lane may map selected support rows into this
ABI to prove adapter parity, but the result does not create PNF eigenvectors,
support authority, answer authority, routing authority, or promotion.

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


## Dioxus fleet/research cockpit integration (2026-10-23 planning addendum)

Canonical operator UI: `chboishabba/itir-dioxus` M10/M11, **not** legacy `itir-svelte`. Reuse Dioxus `VisualisationIr` and the shared `DomainCommand` reducer. UI must not become a second fleet controller, archive, world store, or semantic authority.

**Read-only producer projection** should link AO operation/lane/worker state, canonical archive handoff and source digests, StatiBaker observer chronology, SLR candidate-only proof-search/residual receipts and exact verifier evidence by stable scoped references. First cut is one mission end-to-end with bounded graph/timeline/inspector selection. Do not infer success from a heartbeat, output text, GPU node color or PR creation.

**Governed action boundary:** `itir.chatgpt.dispatch_worker`, `operation_status`, `reconcile` and `itir.ao.*` remain the only documented controller interfaces for their respective operations. Dioxus may propose a typed requested action, but execution requires scope and policy review, explicit approval where applicable, and a receipt of the actual outcome. `async_starting` and `commit_unknown` are hold/reconcile/no-resend, never auto-retry. Ordinary dispatch is event-driven and should not be converted into polling for dashboard animation. The historical title/DOM-based fleet daemon is excluded from this governed path.

**Cross-project acceptance:** deterministic replay and stable selection IDs, unknown versus unavailable versus redacted visually distinct, bounded raw-source drill-down, identical GPU/shell selection reducer outcome, no implicit promotion and no new semantic write by UI. Verified-progress metrics require producer-owned proof/test receipts; match evaluation budgets before claiming improvements from Cogentic-style prover populations or self-improving harnesses.

See `docs/planning/user_story_alignment_and_reprioritization_20260402.md` (superseding UI note), `docs/planning/governed_revival_handoff_v1.md`, `itir-dioxus/docs/M10_UNIFIED_WORKBENCH.md` and `slr/docs/ROADMAP.md`. External research inputs: https://arxiv.org/abs/2609.40324 (Cogentic), https://arxiv.org/abs/2609.00006 (harness taxonomy), https://arxiv.org/abs/2606.09498 (Self-Harness), https://arxiv.org/abs/2610.05300 (MESH). **Planning only; no new runtime/kernel/test acceptance claimed.**


## RPD PNF fibres, ontology grounding, and fleet barriers

The implementation contract is `docs/planning/rpd_pnf_hierarchical_fibres_slr_wikidata_bridge_20261030.md`.

The active PNF spectral path must use `sensiblaw.interfaces.parser_adapter.parse_canonical_text` for linguistic POS evidence. It does not own English stopword or predicate sets. Lexical heads are eligible only from substantive parser categories (`PROPN`, `NOUN`), explicit formal AST symbols, or supplied ontology identifiers. Corpus document frequency and the existing Marchenko–Pastur threshold are data-driven noise/retention signals; they do not create semantic authority.

The hierarchy supports canonical ontology roots with typed representation children and shared invariant-fibre references. For Yang–Mills, the canonical root is `Q271810` and the fibre key is `F_YM`. Lattice, continuum, and constructive/formal branches remain separate objects. Shared fibre membership enables discovery of adjacent verified invariants but never promotes one branch proof into another branch without an explicit formal bridge.

The fleet runner retains the live `execute_pareto_conductor` and `spawn_parallel_lanes` APIs. A round is a barrier over at most 20 concurrent lanes. Twenty rounds can therefore plan at most 400 worker calls. Every concurrent pair must pass typed-support `noTypedMeet` separation before dispatch.

Wikimedia grounding reuses SensibLaw's public `WiktionaryProvider` and `WikidataProvider` rather than duplicating provider logic. Permanent QIDs remain external candidate evidence. New frontier concepts stay candidate-only under `cand:Q_*`, with explicit `P279`/`P361` anchors and an observational P2738 disjointness gate. Ontology walking and lemma routing use explicit graph edges and explicit verified lemma attachments only.

Golden safe Agda remains the theorem authority. Lean follows Agda. ITIR receipts are operational/candidate evidence and do not establish proof authority.
