# Epistemic deliberation over ontology evolution — source-pinned governance cut (2026-11-01)

## Attribution and scope

- Original research: Marcin Roszkowski (2024), *Navigating change: an exploration of socio-epistemic process of extending Wikidata ontology with new properties*, *Journal of Documentation* 80(6), 1291–1312, DOI [10.1108/JD-01-2024-0008](https://doi.org/10.1108/JD-01-2024-0008).
- 2026 conference presentation: Roszkowski, *“Done. Make Good Use of It.” Epistemic Practices Behind Wikidata's Ontology Evolution*, Open Knowledge: Wikimedia & Research in the CEE Region, [accepted abstract](https://meta.wikimedia.org/wiki/Open_Knowledge:_Wikimedia_%26_Research_in_the_CEE_Region/Submissions/%E2%80%9CDone._Make_Good_Use_of_It.%E2%80%9D_Epistemic_Practices_Behind_Wikidata%27s_Ontology_Evolution).
- Roszkowski supplies the *initiation → knowledge work → closure* socio-epistemic process and the institutional division-of-labour question. The typed event schema, policy-age checks and non-promotion boundaries here are ITIR-local engineering, **not theorems from his paper**.
- James Michael DuPont's Lean finite-KB diagnostic and repair results are separately attributed and bounded by SLR's existing `docs/wiki1_ontology_diagnostics.md`. An exported diagnostic, a checked theorem, a community decision and a live Wikidata edit are different objects.
- DASHI Agda governance owners (not recreated here): `DASHI/Core/EpistemicInquiryGovernance.agda`, `DASHI/Ontology/WikidataDiagnosticGovernanceExact.agda`, `DASHI/Core/ActiveObligationEvidenceFibreExact.agda`, and `DASHI/Ontology/WikidataRepairReopeningExact.agda`.

## Actual owners

```
source revision and discussion events ──> SLR native source/PNF evidence
                  │                           │
                  │                           └──> existing S29 OntologyDiagnostic review
                  ▼
 ITIR itir.governance.deliberation_assessment (pure, candidate only)
                  │
                  └──> bounded AO evidence/hold material (never a lane claim,
                       verification receipt, proposal approval or dispatch)
```

The new generic function `itir_mcp.epistemic_deliberation.assess_deliberation` is registered through **existing** `itir_mcp.governance_tools` as `itir.governance.deliberation_assessment`. It accepts source/policy revision refs, an explicit historical age threshold, and a bounded ordered list of source-pinned events. The tool makes no network calls and never persists source state. It rejects duplicate IDs, naive timestamps, disorder, incorrectly attributed decision fields and forward amendment references.

SLR (separate PR) owns a typed native `DeliberationPacket` and `assess_deliberation` with explicit original revision identifiers, Unix seconds from the source producer, and a `project_s29_diagnostic_review_item` adapter. SLR's canonical source-revision reopening and existing S29 review/store must validate real source provenance before any persistence or workflow claim. Creating the Rust review item is **not** proof that its source refs exist in PostgreSQL. There is no second source store, parser, public editor or review reducer.

AO currently uses `operator_workflow.py` / `frontier_evidence.py` and `frontier_reference_validation.py`: trusted reference kinds are operation, repository and formal, while `evidence_refs` are candidate metadata rather than independently verified provenance. Therefore this tranche does **not** register a new trusted AO reference kind or feed `packet_ref` into AO as an authenticated receipt. An AO operator can use the diagnostic's holds to propose further source retrieval through existing bounded planning; only an independently bound, source-verified SLR receipt can be referenced as source evidence. This is deliberate non-promotion.

## ZKP O/R/C/S/L/P/G/F

| Coordinate | Contract |
|---|---|
| **O** Organization | Wikidata community controls its own property-creation roles; SLR owns source persistence and review; ITIR projects bounded diagnostics; AO plans candidate work; DASHI is the formal reference. |
| **R** RFP | Recover proposal→argument→revision→recorded closure without conflating structural completeness, community acceptance, ontology truth or edit permission. |
| **C** Code | `itir-mcp/src/itir_mcp/epistemic_deliberation.py`, existing governance registry, focused regressions; SLR source-native peer. |
| **S** State | Proposal, pinned source snapshot, historical policy revision, ordered actor/source/event stream, optional observed created property, explicit holds. |
| **L** Lattice | Positive support and counterarguments remain different event kinds; a missing consensus record is not a negative consensus vote. |
| **P** Proposal | The output is a deterministic candidate *record-completeness* receipt for review, never a semantic/policy judgement. |
| **G** Governance | Only source-pinned human/community judgement may decide consensus; role attestation is a supplied reference, not verified by these pure functions. No public edit, claim promotion, AO dispatch, or S29 bypass. |
| **F** Gap function | Missing independent participation, decision, source refs, age compliance, creator separation or property identity yield separate holds; subsequent evidence must reopen the original source. |

### Preconditions, invariants and postconditions

Preconditions: explicit nonempty proposal/source/policy refs; historical minimum age in seconds; one proposal event followed by at most 127 other events; timezone-qualified timestamps; each event carries original source revision and actor ref.

Invariants: event order retained, objections never erased by subsequent amendments, amendments target previously seen events, terminal decision has an explicit source-based judgement and optional consensus/authority *claims*, missingness remains explicit, no implicit consensus from vote counts, no independent source authentication from an input string.

Postconditions: stable deterministic digest over the exact canonical supplied packet; inspectable event and source refs; separate assessment holds and recorded judgement; `semantic_truth_promoted=false`, `community_consensus_verified=false`, `wikidata_edit_authorised=false`, `ao_dispatch_allowed=false`.

### Historical policy/version edge

The minimum-age check is conditional on caller-supplied `minimum_age_seconds` and `policy_revision_ref`. This is not a claim that today's Wikidata policy governed every historical proposal. `age <= minimum` is held under the explicitly selected older-than threshold. We cannot independently verify the historical rule, actor role, timestamp accuracy or community consensus with this pure assessment alone. Even a `record_completeness=reviewable` packet may be wrong.

The historical P10322 `time in the pouch` proposal can be used as a **future source-pinned acceptance corpus** only once original proposal revisions, discussion event refs, timestamps and Wikidata property-creation revision have been reopened. Current tests use deliberately generic fictional event refs, **not synthetic historical evidence**.

## Acceptance

- `python -m pytest itir-mcp/tests/test_epistemic_deliberation.py -q` with `itir-mcp/src` on `PYTHONPATH`.
- `cargo test -p sensiblaw-pg-source-store epistemic_deliberation` in SLR.
- Source-backed P10322 (and dissenting/uncertain cases) and real PostgreSQL S29 close/reopen remain explicit further acceptance obligations.
- Neither connector writes nor these proposed tests establish a fresh Rust run, Agda kernel receipt or checked live-Wikidata event.

## Exact next residuals

1. Reopen a real complete immutable P10322 discussion and policy revision; reconcile Wikidata revision times with the source-producer Unix/ISO timestamp representations and record the conversion.
2. Require SLR's real PostgreSQL source lookup to bind every event source ref and S29 diagnostic to a trusted source/consumer scope before exposing the packet as an AO evidence reference.
3. Compare historical consensus/evidential reasoning to actual community roles and rule changes without inventing automatic consensus criteria.
4. Obtain exact Agda theorem dependency and kernel execution receipts independently. No source citation or Rust/Python test substitutes for these receipts.
