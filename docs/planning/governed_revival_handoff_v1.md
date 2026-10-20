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
