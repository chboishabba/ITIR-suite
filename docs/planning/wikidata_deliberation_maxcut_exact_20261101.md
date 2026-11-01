# Wikidata deliberation exact max-cut — four-repository roadmap
Status date: 2026-11-01. Scope: Roszkowski 2024/2026, real P10322 history, ITIR/SensibLaw/SLR/DASHI authority. **This is a source-code roadmap, not a verified external permission certificate.**

## Normative owner chain

| Authority | Canonical owner | New branch / PR | Source boundary |
|---|---|---|---|
| Social-epistemic research | Marcin Roszkowski, *Navigating change* (2024), DOI 10.1108/JD-01-2024-0008; Wikimedia CEE 2026 | prior work | Empirical explanation of Wikidata property proposal phases, *not* proof of our formal or runtime rules |
| Historical policy, participants and property creation | Wikidata community and individual discussants | Public Wikidata archive; original 2022 revisions | Independent historical evidence, not automatic truth or permission |
| Native golden theorem laws | DASHI `EpistemicInquiryGovernance`, `WikidataDiagnosticGovernanceExact` | [DASHI #1447](https://github.com/chboishabba/dashi_agda/pull/1447) | Conditional `ClosureAdmission` and explicitly missing provenance/creator/consensus/policy/time witnesses; kernel check not executed |
| Source representation and generic Wiki consumer | Existing SensibLaw Wiki pull and `sl.wikidata_signal_review_bundle.v0_1` | [SensibLaw #511](https://github.com/chboishabba/SensibLaw/pull/511) | Exact original text→source-byte anchors, real five-lane candidate property cone; original diagnostic ownership retained |
| Read-only governance contract | ITIR `itir.governance` | [ITIR #70](https://github.com/chboishabba/ITIR-suite/pull/70) | Generic assessment, strict source/byte/canonical-ID validation, no external trust |
| Canonical source and S29 review persistence | SLR INGEST-1 `generic_source_content_store` and S29 `review_workstation_store` | [SLR #76](https://github.com/chboishabba/slr/pull/76) | Exact source ID+byte reopening, fully typed incoming JSON, atomic S29+sidecar review, no independent source-store or second reviewer |
| Downstream matters, tool dispatch and external edits | Existing S30/AO/Wikidata community governance | none promoted | No entrypoint from this tranche bypasses recipient/role/purpose/knowledge-cut checks or grants Wikidata edit authority |

## Concrete code obligations

Status vocabulary: **source-written** = implemented and committed but not executed/verified through this GitHub-only turn; **held-external** = needs evidence or executor beyond current PR source text; **bounded original** = existing owner remains authoritative.

| ID | Exact obligation | Owner / contract | Status |
|---|---|---|---|
| K00 | Identify actual P10322 proposal, actor statements, dates and output property without inventing a newer property snapshot | SensibLaw `p10322_history_primary_20220204.json` and original wiki archive | Source-written historical *locator*; full original wikitext not fetched |
| K01 | Reuse original MediaWiki revision fetch for Wikidata with exact oldid, missing-text and wrong-page refusal | `scripts/wiki_pull_api.py --wiki wikidata --revid` | Source-written |
| K02 | Select historical rule document at/before proposal time, not current policy or a post-proposal revision | original `--at-or-before`, `build_historical_source_handoff` source age guard | Source-written; historical rule version not fetched |
| K03 | Derive unique event signature byte intervals and SHA-256 from original UTF-8 revision content | `project_historical_source_anchors` | Source-written; source interpretation still claimed |
| K04 | Prove **field-exact canonical source-revision identity** at runtime via SLR's `generic-source-revision:v1` length-framed SHA-256, with same provider, acquisition, media and original text bytes | SensibLaw `build_historical_source_handoff`, ITIR `project_source_replay_handoff`, SLR `canonical_generic_source_revision_ref` | Source-written triple-check; cross-language Agda theorem not claimed |
| K05 | Build complete `SourceIngestEnvelope`/canonical text inputs plus matching seals/anchors, with source revisions as canonical **SHA IDs**, not raw `wikidata:page:<oldid>` | SensibLaw `history-snapshot-handoff` | Source-written |
| K06 | Keep independently validated user-supplied timestamps, events, policy-age threshold, objections/amendments/decision claims | ITIR `deliberation_assessment`, `deliberation_slr_handoff` | Source-written; original actor timestamps unverified at provider |
| K07 | Independently verify complete canonical source content, source-seal correspondence, source-hash and event byte-span hashes; reject forged nonpromotion flags | ITIR `wikidata_source_replay_handoff` | Source-written; self-reported acquisition metadata not externally authenticated |
| K08 | Deserialize strict ITIR *full JSON* source envelope into SLR native `DeliberationPacket`, original `SourceIngestEnvelope` and exact byte anchors | SLR `persist_deliberation_source_replay_json` | Source-written; opt-in physical run not executed |
| K09 | Verify source identities again before writes, ingest via original INGEST-1, reopen original corpus bytes, then commit original S29 + candidate-only sidecar atomically | SLR `persist_deliberation_from_source_inputs` + `persist_deliberation_diagnostic` | Source-written |
| K10 | Scope-specific S29 review item identity and receipt/reopen (evidence request, qualification, abstention; never community approval) | SLR original S29 + `load_deliberation_diagnostic_scoped` | Source-written; S30 access decision still caller-owned |
| K11 | Compose with real review geometry, not just reference-string hits; preserve all existing original consumer diagnostics and nonpromotion | SensibLaw `attach_deliberation_context` | Source-written for climate/Nat, ChangeReviewPacket, Peter/Ege disjointness, Rosario hotspot and live-follow |
| K12 | Formal independent creator, proposer-separation, historical-policy-source, consensus, age and exact-source obligations; reuse checker non-authority theorem | DASHI `WikidataDeliberationGovernanceExact.agda` | Source-written, **kernel unverified** |
| K13 | Regress native two-source JSON handoff, canonical IDs, event spans, source tampering, role flags, real bounded lane reports and scoped PG replay | Four PRs’ test files | Source-written, **not executed**, per user request not to prioritise CI |

## Exact remaining real-world acceptance obligations

These are NOT equivalently satisfied by K00–K13. All must remain visible and cannot be labelled complete just because the type/representation exists.

- **A00: Actual P10322 exact-archive bytes.** Fetch `Wikidata:Property proposal/time in the pouch` at oldid `1572799769`. Confirm page title, revision timestamp, each signature needle, original text SHA and recorded actor/event interpretation. If a locator doesn't match, revise the manifest *from the actual primary source*, not by weakening checks. The February 2022 archive verifies P10322 and the date window, not necessarily each wikitext event byte.
- **A01: Historical policy applicability.** Fetch `Wikidata:Property creation` as of **2022-01-28 before 12:41 UTC** and compare as of **2022-02-04**. Pin original oldids, diffs and the applicable version, including whether one-week age and creator rule existed then. The candidate `604800` is not a verified historical rule.
- **A02: Independent creator identity/rights.** Source the historical creation log and Jura's relevant role/right at the actual creation instant; prove the closer/creator/proposer relationship, not only their strings in wikitext. This requires an independently source-bearing role/permission witness.
- **A03: Community consensus.** Review historical objections, supporters, amendments and policy-defined closure criteria. Do not treat a discussion's `Done` label, support count, a local signature SHA or a formally inhabited abstract `CommunityRule` as external adjudication.
- **A04: Physical source replay and bounded re-open.** Run the opt-in PostgreSQL acceptance on a **disposable migrated DB**; verify source IDs, bytes, scope, S29 receipt, idempotence, tamper refusal, read-only posture, no unlinked rows. Do not use the user's production DB.
- **A05: S30 recipient/role/purpose/knowledge-cut.** The current scoped SLR API enforces scope equality, **not S30 permissions**. Any outward consumer integration must call an independently trusted S30 gate before exposing a matter's source or review state; do not equate a caller-provided scope string with authorisation.
- **A06: Kernel and runtime correspondence.** Execute focused and golden pinned Agda check, Python regression, Rust unit and physical PG tests; establish any stronger Agda↔Rust/Python same-object theorem separately from a successful test and retain original code provenance. Unexecuted proof files are not kernel receipts.
- **A07: External edits.** None are authorised by this tranche. A future edit requires a separate community and operator approval and an independent execution/audit trail; no automatic Wikidata mutation is a pending step here.

## Execution order (max-cut / Pareto)

1. **In-source handoff and invariant repair (implemented as code):** K04→K05→K07→K08→K09→K10, preserving original owners and no fabricated source receipts.
2. **Repository document sync:** source/route docs in all four PRs, user stories, cross-repo links, S29/S30 and attribution now recorded.
3. **Primary evidence ingestion (held-external):** A00→A01→A02→A03. Failure of any source/policy check becomes a typed hold, **not** permission to invent a receipt.
4. **Local acceptance (not CI-driven):** A04→A05→A06. CI need not block local implementation work, but no unrun checks can be described as passed.

## Attribution
Wikidata community for original edits/rules; Roszkowski for empirical theory; JMD/Aristotle for original Lean finite-KB checker; Ege Doğan and Peter Patel-Schneider for disjointness prior work; Rosario/IBM for hotspot benchmark; original SensibLaw/ITIR/SLR/DASHI contributors for predecessor implementations; new PR authorship strictly limited to code and conditional theorems actually written in these branches. No inferred same-object Monster/other math theorem, no live change, no semantically verified receipt without original sources.


### 2026-11-01 source-written historical policy-drift closure

The source handoff now supports a separately fetched **as-of-closure** policy snapshot in addition to the as-of-proposal policy. SensibLaw produces `historical_policy_drift_status=closure_policy_not_examined | unchanged_across_proposal_window | changed_during_proposal_requires_independent_rule_adjudication`, and detects same-oldid/different-byte contradictions. ITIR retains this exact state and exports `normative_policy_hold`; SLR requires `unchanged_across_proposal_window` with no normative hold before accepting native historical-source JSON into its canonical ingest/S29 path. A changed or unexamined rule remains a reviewable source-history candidate, never a silently accepted historical authority.

The additional closure snapshot has not actually been fetched in this GitHub-only session. Even `unchanged_across_proposal_window` is a comparison of caller-supplied original revision snapshots, **not** independently verified Wikidata community policy/actor rights/consensus. Source-authentic historical closure, the S30 audience check, Agda kernel run and physical PG run remain separately unpaid as detailed in A00–A06.


## 2026-11-01 continuation: last source-code max-cut and exact remaining evidence

- **K14 source-written:** The independent opening/closure policy-window **source witness** now retains two MediaWiki oldids, original revision timestamps, opening/closing canonical UTF-8 digests and the closure acquisition URL. It is independent *source-data claimed evidence*, not policy adjudication. SensibLaw checks same-oldid + same-bytes and refuses forged/misordered timestamps; ITIR checks source-witness identity against the exact native INGEST-1 opening-policy envelope; SLR requires this witness in its strict JSON and rechecks content equality before source ingest and S29 review. Changed/unexamined windows remain held. Positive and negative tests are authored, not executed.
- **K15 source-written:** SLR's `load_deliberation_diagnostic_scoped` compares matter-scope identity *before* reopening source text and S29 records. Scope equality still **does not authorise an S30 recipient/role/purpose/knowledge-cut**; the trusted S30 policy owner must be called by an outward consumer.
- **K16 source-written:** The original Wiki puller's `auto` driver now selects its API path for Wikidata rather than falling into the existing enwiki/simplewiki-only pywikibot path, and source revision timestamps are parsed as timezone-qualified ISO instants rather than a matching text prefix.
- **K17 source-written:** An additional Agda `PolicyWindowValid` witness and `missingPolicyWindowBlocksClosure` theorem model the independent historical rule-drift obligation, referenced in the existing Wikidata working-group regression root. No separate compiler or consensus oracle added.
- **A00–A06 unchanged as external/executed obligations:** the oldid=1572799769 original wikitext and two historical policy snapshots cannot be obtained from a GitHub-only source-write transaction; actor attribution/rights and a community consensus adjudication require independent original evidence. A physical disposable PG run, focused Python checks, Agda kernel acceptance and S30 outward authorisation have not been performed. No Wikidata edits.
- **Research attribution verified:** Marcin Roszkowski, Journal of Documentation 80(6), 1291–1312, DOI 10.1108/JD-01-2024-0008 (2024), independently listed by publisher and bibliographic sources. The P10322 February 2022 archive establishes the proposal date, close date, proposer and property, but not source-byte hashes/actual creator roles by itself.
