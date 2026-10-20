# Frontier typed receipts / AO selector — tranche 3b

## Contract / TODO
- [x] Completed operation selector reads bounded transport mutation receipt metadata, maps by exact canonical source_thread_id, no corpus bodies.
- [x] Typed reference validator accepts operation/repo/formal references with source-bound status and explicit holds.
- [x] Frontier consumes only verified typed receipts for ledger eligibility; legacy opaque labels are never evidence of verification.
- [x] Add focused tests and caller-owned acceptance commands.

## Authorities
O: ITIR AO promotion/verification, canonical archive corpus identity, re-gpt transport cache, SLR formal proof.
R: RFP for bounded typed evidence and completed operation candidate discovery.
C: ITIR MCP typed frontier/operation adapter.
S: canonical thread mapping, transport operation states, typed candidate receipts.
L: opaque -> parsed -> resolved -> source-bound -> candidate -> ledger -> independently promoted.
P: candidate frontier, not proof or dispatch.
G: no auto-resend/dispatch/DOM; explicit holds; no title or timestamp PR inference.
F: unresolved repository connector attestations and SLR kernel execution.

No raw bodies; metadata-only canonical GROUP BY. No PostgreSQL or Colab required.

## Delivered (source-written, unverified)
- `itir_mcp.frontier_reference_validation.completed_operation_candidates`: bounded latest completed mutation receipts; exact `source_thread_id` → `canonical_thread_id` resolution using canonical metadata only; unmapped and ambiguous source IDs held. No prompt/error/body columns.
- `validate_typed_references`: strict typed operation/repository/formal syntax, explicit source-bound operation verification, optional injected repo/formal verifier callbacks. Without trusted resolvers, repository/formal references stay held. A path or SHA alone never means a kernel proof passed.
- Existing `itir.ao.frontier_evidence` optionally discovers completed operations without manual evidence JSON, emits typed reference receipts and holds. Unresolved typed references cannot admit legacy opaque formal/repo labels. Legacy explicit evidence path retained for compatibility and remains candidate-only, not independently verified.
- Registered `itir.ao.completed_operation_candidates`; existing `itir.ao.frontier_evidence` supports `completed_operations=true`, `receipt_db`, `operation_limit`.
- New `tests/test_frontier_typed_references.py` exercises completed/unmapped/ambiguous receipts, typed holds, frontier discovery, and registry.

### Acceptance (caller-owned; not run)
```bash
python -m unittest discover -s tests -p 'test_frontier_typed_references.py' -v
python -m unittest discover -s tests -p 'test_frontier_evidence_engine.py' -v
python -m unittest discover -s tests -p 'test_governed_revival_handoff.py' -v
ruff check itir-mcp/src/itir_mcp/frontier_reference_validation.py itir-mcp/src/itir_mcp/frontier_evidence.py itir-mcp/src/itir_mcp/frontier_tools.py tests/test_frontier_typed_references.py
(cd itir-mcp && PYTHONPATH=src python -c "from itir_mcp.registry import build_default_registry; print([t.name for t in build_default_registry().list_tools() if 'frontier' in t.name or 'completed_operation' in t.name])")
```

Read-only local smoke (no roster_db, no dispatch):
```bash
cd itir-mcp
PYTHONPATH=src python - <<'PY'
from itir_mcp.frontier_evidence import build_frontier
r = build_frontier(archive_db="~/chat_archive.sqlite", completed_operations=True,
                   receipt_db="~/.chatgpt_history.sqlite3", operation_limit=24)
print({"evaluated":r["evaluated_threads"], "holds":len(r["operation_discovery"]["holds"]),
       "proposals":len(r["proposals"]), "dispatch":r["dispatch_performed"]})
PY
```

### Preconditions and postconditions
Canonical `messages` must expose thread/source IDs, platform, account, timestamp, role. Transport `mutation_attempts` must expose completed receipt IDs/state/time. Reads use SQLite read-only URIs. No body read, no roster write unless separately requested. Postcondition: each source-bound operation candidate has exactly one canonical thread; all unresolved references are held; no dispatch, resend, or claim promotion.

### Residual formalization gap
SLR production roadmap places source→revision→span→observation→residual→review/payment under explicit certification. This cut does **not** verify a repository PR via GitHub in the local MCP runtime or a formal Agda/Lean proof execution receipt; both require independent provider verification. Full PNF/world compilation and bounded indexed SLRW comparator remain separate.

### Refinement metric
`source_bound_completed / inspected_completed`, with unmapped/ambiguous counts and truncation flag. `verified_typed_refs / supplied_typed_refs` is a separate metric; held references never count as verified.
