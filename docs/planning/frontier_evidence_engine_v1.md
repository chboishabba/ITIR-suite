# Frontier evidence engine v1 — tranche 3a

## Contract
Owner: ITIR MCP. Canonical corpus authority: `~/chat_archive.sqlite`, not the re-gpt transport cache. `canonical_thread_id` is the structurer-hashed coordinate; `source_thread_id` is the re-gpt conversation coordinate. Read-only canonical messages. Roster/transition receipts live in a separate SQLite file.

## TODO
- [ ] Metadata-only thread aggregation; bounded candidate gate and explicit external evidence.
- [ ] Compose existing comparison/coherence/envelope and canonical candidate ledger; bounded injected gap evaluator.
- [ ] Explicit abstention for unavailable gap, PNF and similarity producers.
- [ ] Durable state transitions, no transcript bodies, idempotent receipts.
- [ ] MCP registry, isolated import, focused fixture tests and transport regression.
- [ ] Record actual local checks (caller-owned when no checkout).

## Non-negotiable invariants
One GROUP BY scan may inspect canonical thread IDs, message counts, role mix, and timestamp bounds, but no bulk `text` selection. Text-based ExactGapComparator is invoked only for a selected thread with a receipt and hard budget; never a global scan. Similarity is a candidate signal, not merge authority. The existing ledger alone owns admit/park/retire/merge; only exact task and evidence equivalence can merge. External formal/PNF/repository receipts must be supplied as explicit source-linked references. A title or thread age is never evidence of junk. Metadata-only threads remain parked until supporting evidence arrives. Maximum evaluated candidates 64, default 24; maximum admitted proposals 4. A user-requested 3–5 frontier means at most four admitted per ledger contract, with a fifth held for review.

## Output
`itir.ao.frontier_evidence.v1`: `proposals`, `decisions`, `evidence_rows`, `comparison_receipts`, `gap_receipts`, `abstentions`, `truncation`, `roster`, `source_mapping`, `dispatch_performed=false`. No raw bodies.

## Acceptance
Run locally from ITIR-suite root:
```bash
python -m unittest discover -s tests -p 'test_frontier_evidence_engine.py' -v
python -m unittest discover -s tests -p 'test_pnf_work_packet_provider.py' -v
ruff check itir-mcp/src/itir_mcp/frontier_evidence.py itir-mcp/src/itir_mcp/frontier_tools.py tests/test_frontier_evidence_engine.py
(cd itir-mcp && PYTHONPATH=src python -c 'from itir_mcp.registry import build_default_registry; print([x.name for x in build_default_registry().list_tools() if "frontier" in x.name])')
```

## Delivered
Pending implementation and caller-owned local verification. No CI or production dispatch.
