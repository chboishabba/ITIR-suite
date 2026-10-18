# Chat archive → SLR PNF reference packets v1

## Storage and identity contract / TODO (before implementation)

Canonical re-gpt SQLite alone owns raw ChatGPT message bodies. SLR PostgreSQL stores immutable coordinates, canonical locator, SHA-256, provenance and candidate-only parser/factor/comparison receipts. No duplicate transcript table or whole-thread flattening. Same source identity+digest is replay; changed digest is an explicit conflict, never overwrite. Source drill-down is separately authorized, bounded, and requires canonical archive digest verification; absent producer support is a declared abstention.

ITIR consumes SLR producer-owned references through a read-only capped MCP packet with explicit source/work/world selectors. Routing via `itir.ao.*` must always pass explicit `repo_root`. PNF factors and residuals are evidence, not authority, proof, automatic merge or task promotion.

TODO: [ ] complete SLR selected-span reopen/parser materialisation without PG raw bodies; [ ] validate exact producer schema and bounded packet against a local PG fixture; [ ] add operator-driven orchestration handoff policy; [ ] run focused local tests. No CI or daemon.
