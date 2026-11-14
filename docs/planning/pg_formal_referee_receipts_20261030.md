# PostgreSQL-only formal referee receipts: discriminator

Authority: `docs/architecture/SINGLE_CANONICAL_STORE_AND_PG_SPINE_ROADMAP.md`; user stories demand context, provenance, abstention, explicit promotion. Golden Agda: `DASHI/Unifier.agda` and `DASHI/Physics/YangMills/BalabanClayCanonicalBMaxCutRound493Exact.agda`. Lean declaration landscape is not a checked proof parity certificate.

The referee is the only permitted writer of source-bound kernel handoff receipts. `formal_receipt_resolver` remains the validation gate. PostgreSQL `formal.referee_receipt` is the single runtime store, keyed by repo, SHA, path, thread; a conflicting replay must fail without replacing evidence. Triangulator shared invariants are candidate AST observations only and MUST NOT enter verified referee receipt storage without independent checker evidence. They can be projected as candidate rows for planning, with original source provenance and no theorem promotion. PostgreSQL outage fails closed. Legacy SQLite is bounded read-only migration input, never runtime fallback.

Formal theorem manifest (`formal.theorem_manifest`) and `ops.receipt` may be connected by migrations after inspecting live schemas; do not assume these tables have compatible columns. No edits to golden Agda, Lean or ESD surfaces in this slice.
