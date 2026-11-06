# Biological GO-CAM / SBML / Assay Candidate Bridge

6 November 2026.  Source-connected ITIR contribution to Golden DASHI
biology history/future quotient max-cut (DASHI PR #1471).

## Additional source-anchoring acceptance (6 November 2026)

The source producer in DASHI PR #1471 and this ITIR candidate consumer now
**independently** require that the original evidence reference of every
GO-CAM-activity / SBML-reaction join is actually present on the selected
original GO-CAM activity's molecular-function or causal-edge evidence.
An arbitrary citation string, a citation belonging to another activity,
or a missing reference cannot authorize even a candidate join.

This is a source-local evidence-integrity check, **not** a reviewed PNF
source span, biochemical equivalence, a PostgreSQL write or authority
promotion. The consumer's negative tests exercise absent and
wrong-activity references. The generic span-bearing canonical
parser/reviewer remains the only acceptance route for authoritative
PNF reconciliation.

## Authority and role

PostgreSQL PNF is the *single* canonical world-model persistence layer.  This
adapter does not create a new store, write an old SQLite/SLRW file, synthesize
source spans, treat string similarity as mechanistic equivalence, or create
an unchecked source statement / ontology/promotion receipt.

Module: `itir-mcp/src/itir_mcp/biological_source_candidate_adapter.py`.
Regression: `tests/test_biological_source_candidate_adapter.py`.

The input is the read-only unpromoted receipt produced by
`dashi_agda/scripts/biological_gocam_sbml_receipt_intake.py`.
The pure projection returns a source-scoped candidate bundle:
- original GO-CAM and SBML IDs, content digests, schema-validation standing;
- each asserted causal edge and the *explicit* original evidence references;
- source-anchored, untrusted GO-CAM-activity / SBML-reaction join hypotheses;
- separately identified kinetic or genotype-assay reports (without assuming
  a shared model identity merely because both are biological);
- fail-closed evidence/review/authority flags and the required next gates.

No candidate is promoted, no PostgreSQL mutation is performed.  The bundle is
**not** an accepted canonical PNF candidate until the native source-span
parser and reviewer/receipt bridge has separately accepted it.  This is
important: a structured GO-CAM graph does not replace text-anchored PNF
semantics or review policy.

## Tests and exact review

```bash
PYTHONPATH=itir-mcp/src python -m unittest discover \
  -s tests -p 'test_biological_source_candidate_adapter.py' -v
```

Fail-closed cases: invalid source digest, missing causal-evidence reference,
nonexistent activity/reaction endpoint, candidate join marked trusted, input
claiming prior PNF mutation, duplicate identity, or assay claimed to be joined
to a model without source evidence.

## Remaining genuine production walls

1. A **source-span-bearing adapter** from reviewed GO-CAM model objects into
   canonical `corpus.source_statement` / `pnf.statement_candidate_factor`
   via the existing generic source parser rather than a competing compiler.
2. Schema-validated original GO-CAM (gocam-py) and SBML (libSBML) models,
   with version pins, provenance of ontology IDs, units, amendments and source
   discrepancies.
3. Original biological measured trajectories and independent source/calibration
   receipts; no auto-promotion from a successful synthetic regression.
4. A **reviewed only** PostgreSQL PNF reconciliation receipt and a separate
   authorizing operation before any candidate may become trusted.

The adapter is deliberately safe to run without a PostgreSQL connection; no
synthetic evidence can become canonical data merely because it was parsed.
