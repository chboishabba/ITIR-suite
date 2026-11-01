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

## Existing user-story and Wikidata handoff crosswalk (reviewed 2026-11-01)

This integration is a **generic evidential/governance coordinate** on existing review stories, not a new Wikidata lane, new AO dispatcher, new SLR source store, or a substitute for the approved candidate-change grammar.

| Existing owner and accepted surface | What Roszkowski-style deliberation can supply | What this PR does **not** supply |
| --- | --- | --- |
| `docs/user_stories.md` **ITIR-US-17** wiki revision review assist | Proposal event refs and revisions can become review-navigation candidates | Wiki page parser, citations or bounded followed-source materialisation |
| **SL-US-15/16**, contested Wikipedia moderation/Wikidata claim workers | Separates a community decision about vocabulary from evidence about a contested particular statement | Finding of truth/defamation, attribution of a person's actions, time-validity of a Wikidata claim |
| **WIKI-US-01 / SL-US-38**, `itir.wikidata.review_packet` and `itir.wikidata.object_review_bundle` | Additional provenance dimension for a **proposed new property**, alongside existing per-statement qualifier/reference review | Statement edit approval, GUID verification, datatype/constraint validation, batch transport |
| **WIKI-US-02 / SL-US-39**, `itir.wikiproject.tooling_profile` | Historical actor-and-role claims and policy revision can be inspected without tool-generated authority | Modification of bot authority profiles or QuickStatements/OpenRefine edit permission |
| **WIKI-US-03 / SL-US-40**, P2738 disjointness/migration | One provenance layer explaining *why* a change proposal was supported or contested | Extraction/counting/culprit analysis, or declaration that a structural repair is community authorised |
| **WIKI-US-04 / SL-US-41**, `sl.wikidata_signal_review_bundle.v0_1` | Attaches candidate decision-history provenance to revision-pinned wiki source views | Replacing primary evidence, temporal truth or source-grounded PNF roles |
| **AO-OP-1** and `itir.ao.operator_workflow` | Explicit missing-source/authority holds may inform an operator's next **manual** acquisition decision | Trusted AO typed reference, automatic dispatch, completed operation or formal receipt |
| **Nat climate** `P5991 → P14143` | Separates WikiProject coordination and proposal decisions from statement-level migration-policy gates | Family A–E disposition, split verification, after-state proof, user consent or live mutation |
| **Peter / Ege** `P2738` + `P11260` | Contestable *governance provenance* for a future disjointness repair proposal | Pair extraction, subclass/instance violations or culprit ranking |
| **Rosario** hotspot benchmark | Source/decision history for ontology test-case vocabulary | LLM consistency result, score-only benchmark or exact-method parity |
| **ChangeReviewPacket** `compare-candidates` | Future input reference for `new_property_obligation`, `split_class_obligation` and other candidate semantic repairs | Replacing the in-memory check family, monotone-coherence rule, or upgrading existential obligation labels to actual QIDs/PIDs |
| **WIKI-1 / SLR** source-native checker and S29 review | Source-pinned deliberation diagnostic via the existing review kind | Executed JMD Lean checker, source-revision PG witness, kernel proof or externally approved edit |

### Source-backed workflows that informed this crosswalk

- `chboishabba/SensibLaw/docs/wikidata/README.md`, stories 1–5: climate property migration; climate PNF/residual review; hotspot benchmark; P2738 disjointness; ChangeReviewPacket candidate repair comparison.
- `chboishabba/SensibLaw/docs/planning/wikidata_octf_entrypoint_20260421.md`: Dave/OCTF, Peter, Ege and Rosario reader routes, concrete CLI, first-hand edit authority boundary.
- `chboishabba/SensibLaw/docs/planning/wikimedia_prior_work_and_originality_note_20260326.md`: explicit attribution to Rosario/IBM, Ege Doğan/Peter Patel-Schneider and Shixiong Zhao/Hideaki Takeda; do not claim replication/parity beyond evidence.
- `docs/planning/wikidata_assist_lane_reviewer_packet_alignment_20260401.md`: `lane_id`, `packet_id`, `case_list`, `culprit_summary`, `qualifier_reference_index`, `progress_claim`, `governance_flags`, `reviewer_prompt`. This is a **consumer packet grammar**, not a license to add a second semantic owner; its assist lane is still review-first.
- `docs/planning/wikidata_combined_roadmap_nat_and_assist_20260401.md`: distinguish *source Cohorts A–E* from *action Families A–E* and recognise checked-safe staging as narrower than live edit authority.
- `docs/planning/wikidata_lane_architecture_and_roadmap_20260703.md`: one `sl.wikidata_signal_review_bundle.v0_1` carrier, five executable lanes, disjointness direct-Zelph versus climate/Nat adjacent-live versus hotspot/change-review geometry.
- `docs/planning/generic_world_model_compiler_convergence_20260716.md`: one generic compiler/reviewer with lane profiles; preserve receipt-free world model and source-to-review/receipt boundary.
- `docs/planning/pnf_zelph_wd_linkage_depth_contract_20260703.md`: maintain token/span → sentence/document → PNF → WD candidate → review linkages. A new `deliberation:sha256` identifier **is not** a replacement for this provenance spine.

### Historical-note correction

The March 25 Rosario/Ege/Peter parity note predates the implemented P2738 report lane. By July the architecture documents a bounded disjointness report and first local direct-Zelph proof route; this does **not** establish full hosted WD shard acceptance or exact Ege/Peter method parity. The actual current status must come from the pinned fixtures, the dated July executable-lane notes, and new execution receipts, not from the March gap statement in isolation.

### Implemented cross-repository max-cut (2026-11-01)

**SLR #76** now source-writes the production-layer adapter, not merely a projected review item:

- `persist_deliberation_diagnostic` creates a candidate-only PG sidecar only after reopening all **canonical source bytes** through existing `load_generic_text_source`; proposal, every event and the historical policy must have independently supplied, exact, matching source/acquisition SHA-256 seals.
- `DeliberationEventAnchor` requires one nonempty exact byte interval and excerpt SHA-256 for every event; replay reopens bytes and checks intervals/digests again. A correct span does **not** prove its textual interpretation or historical authority.
- The existing S29 `OntologyDiagnostic` review item is bound to a deterministic **consumer-scoped** ID and inherits its ordinary review transaction and receipt storage. No separate approval reducer or fabricated JMD Lean diagnostic receipt is used. Only evidence-request/qualification/abstention/source-opening actions are offered, never external property approval.
- `load_deliberation_diagnostic_scoped` and `apply_deliberation_diagnostic_review` require the explicit consumer scope and fail on scope mismatch; a caller must still enforce S30 recipient, role, purpose and knowledge-cut permissions before displaying any source.
- A **disposable, pre-migrated PostgreSQL** opt-in physical acceptance test is now source-written in `crates/sl-pg-source-store/tests/epistemic_deliberation_replay.rs`. It exercises source ingest, byte-span checking, idempotent PG replay, negative seals, unrelated scope rejection and S29 evidence-request re-open. This test has **not run** through the GitHub-only connector.

**ITIR-suite #70** now exposes three actual read-only tools through the shared governance registry:

1. `itir.governance.deliberation_assessment` — separately recorded arguments, objections, amendments, policy age, and conditional discussion closure.
2. `itir.governance.deliberation_slr_handoff` — exact timezone-qualified ISO instant to **whole Unix seconds**, with explicit caller-supplied source seal and per-event byte-span grammar matching SLR's native `DeliberationPacket`, `DeliberationSourceSeal` and `DeliberationEventAnchor`. It **does not authenticate** the caller-supplied hashes; SLR must do so physically.
3. `itir.governance.deliberation_consumer_link` — explicit consumer source and alignment references plus optional exact property-ID navigation for climate, `ChangeReviewPacket`, P2738 and Rosario/hotspot carriers. Matching IDs are **not** licensed identity, source credibility, semantic truth or a safe edit.

The generic linkage remains a **candidate overlay**, not an automatic edit/merge or a trusted AO typed-reference kind. **DASHI Agda #1447** adds formal conditional obligations and the no-checker-authority regression to the focused Wikidata root, without independently authorising Wikidata decisions.

### Exact remaining acceptance obligations

1. **Execute verification** on real user facilities: focused Python tests, SLR Rust unit regressions, disposable migrated PG acceptance, and independently kernel-checked Agda focused root / golden pinned Track A. No green test or proof status follows merely from source-written code.
2. Reopen the **historical P10322** proposal discussion, its event spans, creator-role evidence, property creation revision, and the *then-effective* rule. No synthetic fixture or current rule may be substituted.
3. Authenticate the historical policy/creator and community consensus through **independent reviewers**. Accurate source bytes and decision labels are not a policy-authority witness.
4. Bind **actual consumer artifacts**, not only reference fields, through the existing SLR generic source/PNF/projection and S30 access-control checks. Exercise real Nat climate P5991→P14143, disjointness P2738/P11260, Rosario/hotspot and `ChangeReviewPacket` specimens. Current ITIR linkage is deliberately candidate-only.
5. Obtain the stronger **same-object ABI theorem**: source-backed ISO↔Unix conversion plus exact Rust/Python packet semantics and Agda witness, not merely equal names or matching fingerprints. As implemented, the ITIR digest and SLR JSON digest intentionally differ because they describe different receipt encodings.
6. Preserve **one shared generic review/model owner**. ChangeReviewPacket's structural severity monotonicity, source relevance, community policy legitimacy, and Wikidata edit authority remain separate gates. AO does not gain autonomous dispatch from any of them.

No external Wikidata edits, checked historical consensus, or completed repository kernel receipts are claimed.


### 2026-11-01 original historical-source and consumer runtime linkage

[SensibLaw PR #511](https://github.com/chboishabba/SensibLaw/pull/511) now supplies the original real P10322 oldid `1572799769`, an attributed and explicitly unverified actual community-event locator manifest, exact oldid/UTC-minute/unique text-signature to byte-hash projection, and the existing Wiki puller's Wikidata and as-of historical policy retrieval path. No historical policy revision or creator-rights decision is synthesized.

That PR also extends `sl.wikidata_signal_review_bundle.v0_1` with an actual **candidate property + focus PID cone intersection** overlay, exercised against five real existing lane-built climate/Nat, ChangeReviewPacket, P2738/Ege-Peter, Rosario hotspot and live-follow reports. It preserves all original diagnostics, source structure, refusals and distributions. The original `python -m src.cli wikidata lane-bundle` has an optional source-deliberation overlay; `python -m src.cli wikidata history-snapshot-handoff` projects fetched proposal/policy snapshots into native `deliberation`/`source_seals`/`event_anchors` records. The historical rule-age input is a caller-supplied candidate; original policy applicability remains held.

ITIR now also registers **`itir.governance.wikidata_source_replay_handoff`**, which checks the SensibLaw source-projection wrapper's non-promoting evidence flags and delegates to the existing `project_slr_handoff` invariant checks instead of copying an independent validator. Both the captured source's SHA and any claimed acquisition receipt remain self-reported until SLR independently reopens its persisted canonical content. `source_revision_refs` must match exactly the source-seal set, and the historical producer cannot assert community role, consensus, edit or AO dispatch authority.

SLR PR #76 additionally implements `persist_deliberation_from_source_inputs`: existing INGEST-1 canonical wiki text source writes precede independently verified S29 sidecar persistence, with one atomic S29+sidecar transaction. Its disposable-DB acceptance test is now authored over that direct canonical-ingest entrypoint, **not** a fake source row.

These are functional source-written cross-repo joins with tests. They **do not** constitute an executed P10322 policy/role adjudication, an Agda kernel receipt, or an external edit.


### Canonical synchronized K00–K13 / A00–A07 status (2026-11-01)

See the [single four-repo max-cut roadmap](https://github.com/chboishabba/ITIR-suite/blob/agent/epistemic-deliberation-candidate-governance-20261101/docs/planning/wikidata_deliberation_maxcut_exact_20261101.md) for each exact owner, source-written code, and remaining primary-source acceptance. The latest canonical source ABI uses SensibLaw's length-framed SHA-256 INGEST-1 source identity, independently reverified by ITIR against original UTF-8 text and byte anchors, and SLR's full typed JSON replay into existing INGEST-1 + atomic S29 review. This is committed source code, not an executed kernel/PG check. Historical P10322 original bytes, applicable policy, creator rights, consensus, actual S30 permission and cross-language formal proof remain independent obligations; no external Wikidata edits are authorised.
