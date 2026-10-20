# Governed revival and canonical handoff — max-cut working notes

FORMAL MODEL: O, R, C, S, L, P, G, F

- O (Organization): ITIR MCP exposes evidence and governance; canonical archive is corpus authority; SensibLaw owns token/PNF parsing; AO owns lifecycle decisions; re-gpt owns async mutation.
- R (RFP): revive a predecessor through canonical graph evidence, task/proof-gap/repo receipts, bounded handoff and explicit operation disposition.
- C (Code): ITIR `pnf_work_packet_provider`, `pnf_tools`, `registry`, `server`, `autonomous_orchestrator_tools`, `scripts/autonomous_fleet_daemon.py`; SensibLaw `shared_reducer`, `deterministic_legal_tokenizer`, `residual_lattice`; Dashi `audit_pnf_numeric_abi_surface.py`.
- S (State): parent canonical thread, candidate successor, source message/node parent pointers, explicit operation status and receipt.
- L (Lattice): parsed token evidence is weaker than reviewed typed PNF, which is weaker than kernel/formal proof; contradiction and missing receipts block promotion.
- P (Proposal): task atom, formal-gap/repo/PNF receipts, compact source span refs and derived candidates.
- G (Governance): reference-only inspection; no dispatch, no browser/DOM, no retry of commit-unknown operations.
- F (Gap): unresolved formal obligation and parser/proof receipt difference; lexical signals never close the gap.

## Inspected repository evidence

- ITIR-suite `ROADMAP.md` and `docs/planning/canonical_candidate_ledger_v1.md` prescribe structured canonical corpus and evidence-first admit/merge/park/retire.
- `scripts/autonomous_fleet_daemon.py` still queries `~/.chatgpt_history.sqlite3`, uses title-derived prompts, and includes an unsafe DOM fallback after retries. This cut does not call that daemon.
- `itir_mcp.pnf_work_packet_provider` already provides bounded canonical references, but tail-only selection can omit earlier proof decisions; it currently emits lexical hints only.
- `itir_mcp.autonomous_orchestrator_tools` supplies status/claim/heartbeat/report governance, not a canonical handoff view.
- SensibLaw `docs/pnf_itir_primer.md` explicitly prohibits promoting regex matches to semantic PNF authority; `src.text.deterministic_legal_tokenizer.tokenize_with_spans` exposes span offsets.
- Dashi `scripts/audit_pnf_numeric_abi_surface.py` maps Python ABI to Agda but does not certify revival safety; formal gap recorded below.

## Contract

New read-only MCP tools must expose (1) bounded canonical thread view and (2) task-aware predecessor→child handoff with provenance and explicit operation gating. Scan **all messages** in the selected thread via streaming cursor to find evidence across the full timeline, not the first 30,000 characters; retain a recent-tail anchor and high-value task matches, subject to hard budgets. Never serialize raw message bodies. Preserve `parent_node_id`, `node_id`, `branch_membership` and source locator/digest. PNF tokens, if SensibLaw is importable, are source-linked lexical evidence, not typed proof; if unavailable, abstain explicitly. Do not write canonical messages or invoke re-gpt mutation. No automatic resend of `async_starting`/`commit_unknown`.

## TODO

- [ ] Implement full-span, bounded selection with deterministic receipts and explicit truncation.
- [ ] Expose read/view/operation-review MCP surfaces without raw SQLite.
- [ ] Test real-schema fixtures, lineage, tail decision preservation, ambiguity gate, budgets and registry.
- [ ] Record local execution results, formalisation gap and next phase.

## Delivered — reference-only canonical handoff slice

- `itir_mcp.governed_revival.governed_handoff` streams the **entire** canonical predecessor in chronological order (hard scan ceiling one million rows), ranks bounded task/proof signals and retains the last two messages regardless of score. This replaces a first-30,000-character cut with a full-timeline scan and bounded selected output, not unbounded transcript copying.
- Canonical source refs include `message_id`, `source_message_id`, `source_thread_id`, `node_id`, `parent_node_id`, `branch_membership`, timestamp, role, digest and SQLite locator. No source text leaves the archive.
- SensibLaw's `tokenize_with_spans` is used when available at the suite-relative `SensibLaw` location. A bounded regex fallback is explicitly labeled `regex_hint_only`; both routes abstain from claiming typed semantic PNF. The existing SLR world-store/typed predicate reducer is **not yet wired**, and is not silently emulated.
- A deterministic packet ID, task and proof-gap receipt refs, explicit full-scan/selection/truncation receipt, parent→proposed-child lineage receipt, and ambiguity-aware governance decision are returned.
- Registered read-only MCP tools: `itir.pnf.governed_handoff`, `itir.archive.thread_view`, `itir.ao.operation_review`. They follow the existing ToolSpec/registry and FastMCP wrapper; the archive is read via `mode=ro`.
- `itir.ao.operation_review` treats `async_starting` and `commit_unknown` as `hold_reconcile_no_resend`, and **never** authorizes dispatch. It reviews supplied operation state; it does not read or modify a live operation ledger.
- Authority separation: canonical archive (source), legacy history cache (excluded), lexical/PNF projection (candidate), reviewed controversy (receipt only), formal evidence (receipt only), UI (projection only).

### Exact local verification commands

```bash
python -m unittest discover -s tests -p 'test_governed_revival_handoff.py' -v
python -m unittest discover -s tests -p 'test_pnf_work_packet_provider.py' -v
ruff check itir-mcp/src/itir_mcp/governed_revival.py itir-mcp/src/itir_mcp/pnf_tools.py tests/test_governed_revival_handoff.py
PYTHONPATH=itir-mcp/src python -c 'from itir_mcp.registry import build_default_registry; print([t.name for t in build_default_registry().list_tools() if t.name in ("itir.pnf.governed_handoff", "itir.archive.thread_view", "itir.ao.operation_review")])'
```

**Execution status:** these commands have **not** been run on a local checkout; GitHub access is connector-only and direct git clone fails DNS resolution. No CI/Colab or Agda kernel verification was run. The test file contains four offline fixture cases, but green status is not claimed.

### Formalisation gap (explicit)

Existing Dashi Agda PNF/numeric ABI surfaces and SensibLaw residual lattice do **not** establish a proof that a selected canonical message set is sufficient for revival or that a candidate is authorized. Required future theorem: for a canonical graph `H`, selector `S(H,task)`, handoff `P`, and authorization predicate `Auth`, prove (i) every selected reference resolves to a node in `H` with equal digest and parent pointer, (ii) `Auth(P)=false` absent explicit review, (iii) an ambiguous operation receipt entails `¬Resend`, and (iv) omitted evidence is reported as a residual rather than interpreted as absence. This is a **formal obligation**, not an Agda/Lean checked theorem.

### Remaining blockers / next phase

1. Wire the producer-owned SLR parser, typed `PredicatePNF` reducer and durable world-store to the selected spans, with exact parser/ontology version receipts. Lexical span candidates are not semantic evidence.
2. Build an authenticated, durable operation-status reader and explicit approval/reconciliation workflow; supplied operation status is not independently verified.
3. Integrate this handoff with a replacement for the legacy fleet daemon. **Do not run the old daemon as a governed revival controller**: it still uses the transport cache, title-derived prompts, and contains a DOM fallback. The new read-only MCP path does not call it.
4. Provide source-span completeness and privacy review policies, branch-aware chronology semantics, durable handoff/parent-child operation receipts, and Agda/Lean invariant proof.
5. Verify on the production MCP stdio transport and canonical archive under AO/referee control. No mutation, dispatch, browser, CI or PG work was performed in this cut.
