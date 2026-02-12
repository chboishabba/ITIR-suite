# Evidence and Attribution Frame Contract v2 (2026-02-12)

## Purpose
Extend prior evidence-promotion notes with explicit frame typing and linkage rules for legal/biographical prose.

This document complements:
- `docs/planning/evidence_promotion_contract_20260212.md`

## Frame classes
1. `PROPOSITION`
   - extracted action/roles from sentence-local structure
2. `ASSERTION`
   - communication/speech acts introducing propositions (`report`, `say`, `contend`, `hold`)
3. `EVIDENCE`
   - testimony/report/artifact statements (`gave evidence`, affidavits, records)
4. `REASONING`
   - evaluative/judicial reasoning over propositions

## Deterministic extraction policy
1. Use dependency relations (`ccomp`, `xcomp`, subject/object roles)
2. Use profile verb sets for communication/evidence/reasoning classes
3. Keep regex limited to citation/date/token hygiene lanes

## Linking policy (typed, explicit)
1. `ATTRIBUTED_TO`
   - proposition linked to assertion/evidence source
2. `SUPPORTS`
   - evidence frame linked to proposition frame
3. `CITES_SAME_RECORD`
   - anchor overlap link (citation/reference based)
4. `EVALUATES`
   - reasoning frame linked to proposition frame

Each non-role link must include `basis` metadata:
- citation overlap
- paragraph adjacency
- embedded clause lineage
- source-document linkage

## Frame integrity rules
1. Do not inject evidence actors as proposition subjects unless syntactically correct for that step.
2. Cross-frame context belongs in typed edges, not role-lane mutation.
3. Preserve sentence/frame locality in role extraction.

## UI rendering rules
1. Role edges render as primary structural edges.
2. Evidence/attribution links render as overlays (dotted/dashed) with toggles.
3. Selecting a proposition should expose linked evidence frames and basis.

## Why this matters
Supports scenarios where context actors are crucial ("input evidence") without polluting proposition actor lanes or creating scope leaks.
