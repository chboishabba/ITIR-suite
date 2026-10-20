# Frontier typed receipts / AO selector — tranche 3b

## Contract / TODO
- [ ] Completed operation selector reads bounded transport mutation receipt metadata, maps by exact canonical source_thread_id, no corpus bodies.
- [ ] Typed reference validator accepts operation/repo/formal references with source-bound status and explicit holds.
- [ ] Frontier consumes only verified typed receipts for ledger eligibility; legacy opaque labels are never evidence of verification.
- [ ] Add focused tests and caller-owned acceptance commands.

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
