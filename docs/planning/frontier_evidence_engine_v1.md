# Frontier evidence engine v1 — tranche 3a

## Contract
Owner: ITIR MCP. Canonical corpus authority: `~/chat_archive.sqlite`, not the re-gpt transport cache. `canonical_thread_id` is the structurer-hashed coordinate; `source_thread_id` is the re-gpt conversation coordinate. Read-only canonical messages. Roster/transition receipts live in a separate SQLite file.

## TODO
- [x] Metadata-only thread aggregation; bounded candidate gate and explicit external evidence.
- [x] Compose existing comparison/coherence/envelope and canonical candidate ledger; bounded injected gap evaluator.
- [x] Explicit abstention for unavailable gap, PNF and similarity producers.
- [x] Durable state transitions, no transcript bodies, idempotent receipts.
- [x] MCP registry, isolated import, focused fixture tests and transport regression.
- [x] Record actual local checks (caller-owned when no checkout).

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

## Delivered — source-written, local verification pending

Implemented:
- `itir_mcp.frontier_evidence.build_frontier`: metadata-only `GROUP BY` over canonical thread ID, source ID, role counts and timestamps; bounded evidence-first gate; no corpus body reads.
- Existing `select_candidate_ledger` dynamically imported from `scripts/canonical_candidate_ledger.py` rather than reimplemented. Exact task/evidence equivalence is the only merge authority.
- Existing `compare_observations`, `score_coherence`, `build_envelope` composed over supplied task-atom candidate features; similarity is advisory only.
- Explicit injected gap-evaluator seam for on-demand selected-thread work. Without a bounded configured evaluator, formal artifact requests abstain. **Not yet a production ExactGapComparator integration**: current `ExactGapComparator.load_thread_multiset` scans the entire SLRW file, so blindly invoking it would violate this tranche's no-bulk-read contract. A per-thread indexed SLRW reader/adapter is the next gap.
- Separate SQLite `frontier_roster` and `frontier_transitions` tables with source mapping and state transition receipts. No canonical message writes.
- `itir.ao.frontier_evidence` MCP tool via default registry. No dispatch.
- `tests/test_frontier_evidence_engine.py`: live canonical-column fixture, metadata gate, ledger merge/retire/park, injected comparator, roster, registry and production-cwd import.

Unverified: tests, Ruff, actual live archive smoke, FastMCP registered transport regression. No local checkout is mounted; GitHub connector cannot run them. No CI run.

### AO convergence dry-run #1
1. Produce an explicit `evidence.json` containing 3–5 **canonical-hashed** thread IDs, `task_atom`, formal artifact path, PR/branch receipt refs, PNF receipt refs and provenance digests. Discover candidates using cheap canonical metadata and existing repo/ledger receipts; do not select via titles or raw transcript sweeps.
2. Invoke the registered tool from a local Python process (the MCP tool takes the same payload):
```bash
cd ITIR-suite/itir-mcp
PYTHONPATH=src python - <<'PY'
import json
from itir_mcp.registry import build_default_registry
evidence = json.load(open("../evidence.json", encoding="utf-8"))
payload = {"archive_db": "~/chat_archive.sqlite",
           "roster_db": "../artifacts/frontier_roster.sqlite",
           "evidence": evidence, "max_evaluated": 24, "max_proposals": 4}
result = build_default_registry().invoke("itir.ao.frontier_evidence", payload)
print(json.dumps(result, indent=2))
PY
```
3. AO reviews the full decision ledger and up to four admitted work-packet-ready coordinates. A fifth candidate is not auto-dispatched and must remain for a subsequent review. This tranche does not call `itir.pnf.work_packet` automatically; invoke it separately for approved proposals.

Remaining blockers: automated formal-artifact-to-thread lane matching, indexed bounded SLRW gap comparator, real PNF receipt lookup, external semantic-search provider, and FastMCP registered transport test. Explicit evidence receipts can be supplied now; absent providers must abstain, not fabricate evidence.

