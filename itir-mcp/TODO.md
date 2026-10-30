# itir-mcp TODO

## Current Numeric ABI Boundary

- `itir_mcp.pnf_numeric_abi` is present as a narrow
  `itir.pnf.numeric_abi.v0_1` GEMV validation/parity helper for
  receipt-bearing row maps.
- Do not treat the current ABI as spectral materialization. Signed adjacency,
  Laplacians, eigenvectors, graph versions, and rebuildability payloads remain
  future producer work.

## Docstore and Obsidian Follow-ups

- Verify `obsidian-itir-plugin` inside a real Obsidian vault after dependency
  installation.
- Exercise the plugin against a live HTTP adapter for the registered MCP tools.
- Decide whether `itir.docstore.config_plan` should become a required preflight
  for all docstore scan calls or remain an explicit planning tool.
- Add persistent cache storage only if repeated large-vault scans show measured
  latency pressure.


## RPD PNF Hierarchical Fibres / Ontology Routing

### This tranche

- [x] Remove all active `GENERIC_CONVERSATIONAL_PREDICATES`, `_HEAD_PARTICLES`, `_HEAD_FUNCTION_WORDS`, and `_DOMAIN_HEADS` style lexical sets from `pnf_spectral_packet.py`.
- [x] Gate lexical head candidates through `sensiblaw.interfaces.parser_adapter.parse_canonical_text`; retain parser `PROPN`/`NOUN`, explicit AST symbols, and supplied ontology QIDs; reject particle-only/parser-noise candidates.
- [x] Expose document-frequency ratio and Marchenko–Pastur retained/noise status as data-driven candidate evidence.
- [x] Add hierarchy metadata validation for K=50 and K=100 with eigenspace / primary-topic / subtopic / fibre / goal separation.
- [x] Add canonical root + typed child-branch + shared invariant-fibre structures. Seed Yang–Mills as `Q271810` / `F_YM`.
- [x] Preserve live `execute_pareto_conductor`, `spawn_parallel_lanes`, and current conductor cost-law semantics.
- [x] Add round-barrier planning for at most 20 workers per round and at most 20 rounds; require pairwise typed-support `noTypedMeet` before concurrent selection.
- [x] Reuse SensibLaw Wikimedia provider interfaces for Wiktionary/Wikidata candidate lookup. Do not copy provider logic into ITIR.
- [x] Add permanent-QID normalization, candidate-only `cand:Q_*` minting with explicit `P279`/`P361` anchors, and observational P2738 audit attachment.
- [x] Add deterministic P279/P361 DAG walking and lemma routing over explicit verified lemma attachments.
- [x] Add focused tests in `itir-mcp/tests/test_ao_pnf_spectral_fleet.py`.
- [ ] Verify branch diff has zero protected ESD/digital_esd files and no trust-escape markers. Source audit pending final head.
- [ ] Run focused pytest and available lint before marking complete. Local checkout is blocked by DNS; exact-head CI receipt is being requested by branch workflow.

### Follow-up, not claimed by this tranche

- [ ] Port bounded Wiktionary/Wikidata resolution and ontology DAG closure to native `slr` Rust crates per the approved RPD.
- [ ] Add PostgreSQL persistence for fibre bundles and candidate frontier entities against the canonical TrueNAS spine.
- [ ] Connect the Python/runtime receipts to the existing golden Agda formal owners and Lean mirrors with an exact cross-language ABI receipt.
- [ ] Prove any desired theorem transport between Yang–Mills representation branches explicitly; shared fibre membership alone is non-promoting.
