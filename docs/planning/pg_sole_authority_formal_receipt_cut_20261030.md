# Sole PostgreSQL authority: formal receipt and semantic cut

Authority: docs/architecture/SINGLE_CANONICAL_STORE_AND_PG_SPINE_ROADMAP.md and docs/user_stories.md. Golden proof source: dashi_agda DASHI/Unifier.agda and DASHI/Physics/YangMills/BalabanClayCanonicalBMaxCutRound493Exact.agda. Lean docs/DECLARATION_LANDSCAPE.md distinguishes checked-in declarations from bundle-only candidates.

Operational semantic reads must fail closed when PostgreSQL is unavailable. SLRW is migration input only, never an alternative authority. Historical SQLite is one-way backfill only. AST symbols require source repo, SHA, module, digest and referee verification; attachment is not proof transport. Consumer-exposure max-cut is scheduling metadata, not theorem closure. No ESD edits.

Next gates: (1) remove operational SQLite receipt authority via PG formal/ops migration; (2) reject runtime SLRW fallback; (3) reconcile schema and receipt provenance; (4) verify Agda/Lean parity and import graph. Never delete legacy data before migration reconciliation and rollback receipts.
