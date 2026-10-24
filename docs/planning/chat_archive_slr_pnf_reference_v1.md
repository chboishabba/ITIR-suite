# Chat archive → SLR PNF reference packets v1

## Storage and identity contract / TODO (before implementation)

Canonical re-gpt SQLite alone owns raw ChatGPT message bodies. SLR PostgreSQL stores immutable coordinates, canonical locator, SHA-256, provenance and candidate-only parser/factor/comparison receipts. No duplicate transcript table or whole-thread flattening. Same source identity+digest is replay; changed digest is an explicit conflict, never overwrite. Source drill-down is separately authorized, bounded, and requires canonical archive digest verification; absent producer support is a declared abstention.

ITIR consumes SLR producer-owned references through a read-only capped MCP packet with explicit source/work/world selectors. Routing via `itir.ao.*` must always pass explicit `repo_root`. PNF factors and residuals are evidence, not authority, proof, automatic merge or task promotion.

TODO: [ ] complete SLR selected-span reopen/parser materialisation without PG raw bodies; [ ] validate exact producer schema and bounded packet against a local PG fixture; [ ] add operator-driven orchestration handoff policy; [ ] run focused local tests. No CI or daemon.

## Delivered producer-consumer cut

SLR PR implements reference-only registration in its existing `corpus.chat_archive_message` relation with nullable `document_ref`/`full_message_span_ref`, archive locator, source thread, digest and attachment refs. It records changed-digest conflicts rather than overwriting and fails closed on legacy body-loading APIs for reference-only rows. Its `verify_reopened_chat_reference_bytes` verifies the SHA-256 of caller-reopened canonical bytes; it does not yet implement a canonical SQLite exact-node reopen adapter or the bounded parser handoff.

The read-only `itir.pnf.reference_work_packet` consumes **existing SLR PostgreSQL producer tables** only: reference-only source coordinates, candidate-only statement factors and comparison receipt IDs. It requires explicit `pg_dsn`, `source_ref` (canonical conversation ID), `work_ref`, `world_ref`; optional `limit` 1–24. `drill_down=true` requires explicit `max_chars` 1–512 but currently returns a typed missing-evidence abstention and **never returns unverified raw text**. No transcript bodies enter the packet. The world/work selectors are carried as requested context, not falsely asserted as verified joins; missing world and related-work joins are explicitly declared.

Example operator-driven handoff (not a daemon):

1. Invoke `itir.pnf.reference_work_packet` with explicit selectors and a read-only PG connection. Inspect `missing_evidence` and candidate-only factor signatures.
2. Invoke `itir.ao.status` with `{"repo_root":"/explicit/ITIR-suite"}` to inspect current work lanes.
3. For an explicitly approved continuation, invoke `itir.ao.claim_lane` with `{"repo_root":"/explicit/ITIR-suite","orchestrator_id":"operator-chosen","lane":"pnf-review"}`. This is an orchestration claim, **not** semantic promotion.
4. Invoke `itir.ao.report_result` with explicit `repo_root`, runner and parent IDs and a summary of candidate receipt refs; do not claim proof or automatic thread merge.

Tests (local only):
```bash
python -m unittest discover -s itir-mcp/tests -p 'test_pnf_reference_packet.py' -v
```

Changelog: introduced bounded read-only SLR-source packet registration and strict no-raw-text drill-down abstention. Outstanding: producer-owned exact canonical SQLite reopen and bounded selected-span parser invocation; real PG fixture verification and world/work linkage.
