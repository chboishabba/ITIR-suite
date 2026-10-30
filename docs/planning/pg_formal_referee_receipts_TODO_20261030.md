# Formal receipt PG migration gates

- [x] Identify SQLite receipt store and source-bound validation interface.
- [x] Replace runtime SQLite receipt store with PostgreSQL implementation.
- [x] Add SQL migration and fake-connection deterministic replay tests.
- [x] Add candidate-only triangulation adapter to real ClaySprint inspection.
- [ ] Local referee run full test suite, review fake connection compatibility, and validate live PG schema.
- [ ] Provision dedicated referee INSERT and consumer SELECT roles; deny UPDATE/DELETE.
- [ ] Read-only migrate and reconcile historical SQLite formal receipts before deletion.
- [ ] Confirm existing `ops.receipt` and `formal.theorem_manifest` live schemas and define foreign-key integration.
- [ ] Replace remaining operational SQLite paths in frontier/transport modules under separate bounded cuts.
- [ ] Add genuine independent Agda kernel receipts and optional Lean parity (golden Agda first).
