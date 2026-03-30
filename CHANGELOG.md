# Changelog

## Unreleased
- zkperf on SL stream-to-HF bounded lane:
  - Added `docs/planning/zkperf_stream_shard_contract_v1_20260330.md` and
    fixture `docs/planning/jmd_fixtures/zkperf_stream_v1.example.json`.
  - Added `itir_jmd_bridge/zkperf_stream.py` plus CLI commands to build a
    stream bundle, publish it to HF, and resolve one remote window by
    acknowledged revision.
  - Added regression coverage in `tests/test_zkperf_stream.py`.
  - Live HF publication succeeded for
    `hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.tar`
    at revision `17da96cee89e48088938a8163610371d9b8b3f46`.
  - Revision-bound read-back of `window-0002` matched the local bundle and
    kept `zkperf` observational rather than truth-promotive.
  - Extended the stream manifest with `windowCount`, `latestWindowId`, and
    `sequenceRange`.
  - `publish-zkperf-stream-hf` now optionally writes
    `stream-manifest.json`, `stream-latest.json`, and `hf-receipt.json`.
  - Added `resolve-zkperf-stream-range-hf` for latest-window, explicit
    `windowId`, and sequence-range selection by acknowledged HF revision.
  - Live latest-window recovery succeeded for `window-0002`.
  - Added append-style `zkperf-stream-index/v1` support and optional HF index
    publication from `publish-zkperf-stream-hf`.
  - Live HF index publication succeeded for
    `hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json`
    at revision `55ec2221f3a0dd627543eb5e1237b6df31a4d350`.
  - Exercised a second distinct stream revision `rev-20260330-b`; the tar ack
    advanced to `e5f4982bfdf213f92a6c5d9464c86bbd0243141a` and the index ack
    advanced to `4c53115b6606a9a8fd8af83b865e12ac1d9aefa1`.
  - Fetched remote index now preserves both revisions with
    `revisionCount = 2` and `latestWindowId = window-0003`.
  - Added index-driven consumer resolution so latest or chosen stream
    revisions can be resolved from the HF index object directly.
  - After republishing the index with per-revision window refs, live
    latest-from-index recovery succeeded for
    `rev-20260330-b -> window-0003 -> zkperf-obsv-0003`
    with index ack `b7e2c40fd8b5d5e5ec315c3aa9cad3ee9d1e89a0`.
  - Added explicit `zkperf-retention/v1` lifecycle policy with
    `retain-latest-n` enforcement in the index update path.
  - Live HF verification with `rev-20260330-c` and retention count `2`
    produced tar ack `8716333c2ae72b271b2c2c938cbc47118c8691f7` and index ack
    `640e2a6a2f91d61771e63d6b0f8ddee8ba4d98f1`.
  - The fetched remote index now retains only
    `rev-20260330-b` and `rev-20260330-c` with `revisionCount = 2`.
  - Added `scripts/run_zkperf_stream_hf.sh` as a one-shot operator wrapper for
    publish, index update, and index-driven verification.
- affidavit contested-narrative echo demotion:
  - `SensibLaw/scripts/build_affidavit_coverage_review.py` now demotes
    allegation/OCR echo blocks earlier in candidate generation so they do not
    win support simply by restating John's text.
  - contested rows now prefer explicit response sections such as `Your
    Explanation:` and `Defense Context:` while keeping duplicate allegation text
    only as reference context.
  - focused affidavit/query regression slice is green:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
    -> `48 passed`.
- publisher-native hosted acknowledgement receipts:
  - Updated the sibling publisher repo
    `/home/c/Documents/code/erdfa-publish-rs` so `PublishReceipt` now carries
    `container_ref` plus optional `hosted_acknowledgement`.
  - Added native validation for binding hosted acknowledgement facts back into
    publisher receipts without changing shard semantics.
  - Added bounded native hosted workflow helpers:
    `publish_hf_with_ack(...)` and `publish_ipfs_with_ack(...)`.
  - Added and ran `cargo run --example publish_hosted`, which bound live HF and
    local IPFS acknowledgements into native publisher receipts with
    `verified=true`.
  - Added native artifact emission for publish outcomes so the hosted workflow
    now writes `manifest.json`, `container-index.json`, and `receipt.json` per
    sink.
  - Added `docs/planning/publisher_native_hosted_ack_receipts_20260330.md`.
- IPFS acknowledgement readiness:
  - Added bounded IPFS bridge commands for gateway probe, fetch/read-back,
    local publish acknowledgement, and remote consumer rehearsal over
    `ipfs://...` object refs.
  - Added `docs/planning/ipfs_acknowledgement_readiness_20260330.md`.
  - Verified the code/test path first, then live local parity after IPFS
    Desktop/Kubo became reachable.
  - Published the real emitted tar bundle through the local Kubo API as
    `ipfs://QmR3Z8n2XFm8LPBcmNCc9d4W9tqMwDRBeUnUnXRGQy2eCa`.
  - Verified gateway read-back digest parity against the local tar:
    `4dcd386fb6323a76f934174db94deb9e528028d88c648607875c832941cb37b7`.
  - Verified remote selector rehearsal over that CID through the local gateway.
- HF receipt binding and remote bundle rehearsal:
  - Added `python -m itir_jmd_bridge publish-hf-ack` so a local artifact can
    be uploaded to HF, acknowledged by commit revision, fetched back by that
    revision, and emitted as one verified HF receipt payload.
  - Added `python -m itir_jmd_bridge rehearse-remote-hf-bundle` so a real
    emitted tar-backed manifest can resolve
    selector -> shard id -> objectRefs -> remote HF fetch by revision ->
    payload digest parity.
  - Added
    `docs/planning/hf_receipt_binding_and_remote_bundle_rehearsal_20260330.md`.
  - Verified the remote consumer path against
    `hf://datasets/chbwa/itir-zos-ack-probe/bundle-demo/erdfa-demo.tar`
    at acknowledged revision
    `dccdb582947b0ccdc7be03db5b1caa879c56d187`.
- HF write acknowledgement probe:
  - Confirmed authenticated HF user `chbwa`, created dataset
    `chbwa/itir-zos-ack-probe`, and uploaded a bounded probe artifact.
  - HF returned concrete commit acknowledgement
    `0c56f0d5b090f447d35a5525a1a8e01df10ee284`.
  - Added revision-aware HF fetch support in
    `itir_jmd_bridge/providers/hf.py` plus CLI
    `python -m itir_jmd_bridge fetch-hf-object`.
  - Verified revision-anchored read-back against that commit and confirmed the
    fetched sha256 matches the local artifact digest exactly:
    `52a02d3502cc39411dab1c291e7d6f9789f3a72aef77417a4b11637cdd4c3dfb`.
  - Added `docs/planning/hf_write_acknowledgement_probe_20260330.md`.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now records that HF write acknowledgement is concrete on a bounded probe
    object, while emitted-bundle binding remains the next gap.
- emitted HF tar bundle verification:
  - Generated a real emitted tar bundle from
    `/home/c/Documents/code/erdfa-publish-rs` and uploaded it to
    `hf://datasets/chbwa/itir-zos-ack-probe/bundle-demo/erdfa-demo.tar`.
  - HF returned acknowledged commit
    `dccdb582947b0ccdc7be03db5b1caa879c56d187`.
  - Revision-anchored read-back matched the local tar sha256 exactly:
    `4dcd386fb6323a76f934174db94deb9e528028d88c648607875c832941cb37b7`.
  - Tightened `itir_jmd_bridge/providers/hf.py` so binary HF objects no longer
    dump full payload text and commit metadata is preserved from redirect-chain
    headers when the final CAS response omits it.
- HF acknowledgement probe:
  - Added `itir_jmd_bridge/providers/hf.py` and a new CLI command,
    `python -m itir_jmd_bridge probe-hf-ack`, to capture public HF resolve
    acknowledgement metadata from an `hf://...` object.
  - Added `tests/test_hf_acknowledgement_probe.py`.
  - Added `docs/planning/hf_acknowledgement_probe_20260330.md` to record the
    successful public probe against
    `hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json`.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now records that HF read-side acknowledgement metadata is concrete, while
    write-side acknowledgement remains the next gap.
- hosted sink acknowledgement gate:
  - Added `docs/planning/hosted_sink_acknowledgement_contract_20260330.md`
    to pin the minimum remote acknowledgement object required before hosted
    HF/IPFS integration can be claimed as complete.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the next
    hosted-integration step is now explicit:
    acknowledgement object, read-after-write verification, and replay/cache
    semantics.
- delegated local publish / consume completion pass:
  - Added `docs/planning/local_publish_consume_release_gates_20260330.md`
    to record the implemented local-first artifact publication/consumption
    flow, PlantUML architecture views, and the remaining remote blockers.
  - Updated `docs/planning/affidavit_claim_reconciliation_contract_20260329.md`
    so the current repo status now explicitly records upstream persisted
    `relation_type` alongside the already-persisted relation metadata.
  - Updated `docs/planning/temp_zos_sl_bridge_impl_review_20260329.md` so the
    temp bridge review now reflects the current state accurately:
    resonance is tiebreak-only, while threshold/policy tuning remains open.
  - Added `docs/planning/itir_real_bundle_consumer_rehearsal_20260330.md` to
    record the real emitted-bundle consumer path in `itir_jmd_bridge`.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now records:
    - local-first publish substrate completion
    - real-bundle consumer rehearsal completion
    - resonance demotion in the temp ZOS bridge
    - remaining blockers for real-network HF/IPFS integration and remote JMD
      push/pull
- affidavit relation persistence upstreaming:
  - Updated `SensibLaw/scripts/build_affidavit_coverage_review.py` so the
    builder now persists `relation_type` alongside the existing contested
    relation metadata.
  - Updated `SensibLaw/src/fact_intake/read_model.py` and added
    `SensibLaw/database/migrations/016_contested_affidavit_relation_type.sql`
    so `contested_review_affidavit_rows` now store `relation_type`, with
    fallback derivation retained for older rows.
  - Updated `SensibLaw/tests/test_affidavit_coverage_review.py` and revalidated
    the focused affidavit suite:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_query_fact_review_script.py SensibLaw/tests/test_affidavit_coverage_review.py`
    -> `45 passed`.
- Affidavit sibling-leaf builder followthrough:
  - Updated `SensibLaw/scripts/build_affidavit_coverage_review.py` so the
    builder now runs a bounded sibling-leaf arbitration pass over contested
    candidates before final winner selection, keeping the direct leaf ahead of
    a nearby sibling clause when predicate alignment is stronger.
  - Tightened relation classification so `partial_support` no longer wins on
    mere contextual or same-time overlap; support now requires duplicate
    support or predicate alignment, while weaker same-window matches stay in
    `adjacent_event` or `substitution`.
  - Added focused regression coverage in
    `SensibLaw/tests/test_affidavit_coverage_review.py` for sibling-leaf
    disambiguation, the p2-s21-style adjacent-event guardrail, and strong
    partial-match promotion.
  - Revalidated the focused affidavit suite with
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
    -> `40 passed`.
  - Updated `docs/planning/affidavit_claim_reconciliation_contract_20260329.md`,
    `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo now records that
    upstream relation typing was already landed before this pass and that the
    current affidavit boundary is sibling-leaf/root-cluster quality, not
    upstream persistence.
- privacy-preserving NotebookLM history review:
  - updated `docs/planning/notebooklm_metadata_review_parity_20260311.md` and
    `docs/planning/notebooklm_interaction_capture_contract_20260311.md` so the
    NotebookLM lane now explicitly allows sanitized product/theme extraction
    from notebook asks/history when local docs are insufficient
  - recorded the operational rule that NotebookLM conversation history must not
    be copied into repo records with names, allegations, or case-specific
    factual detail
  - updated `TODO.md` and `COMPACTIFIED_CONTEXT.md` with the safe retained
    product themes:
    chunked review workflow, evidence-to-claim matching, provenance,
    contradiction handling, privacy redaction/selective sharing, and operator
    burden reduction
- notebooklm-pack dry-run wrapper:
  - Added `scripts/notebooklm_pack_ingest.py` as the first bounded integration
    seam between sibling `notebooklm-pack` output and the repo’s existing
    `notebooklm-py` push/pull surface.
  - The wrapper normalizes `manifest.json`, computes source file hashes, emits
    `pack_run` plus `packed_sources` linkage records, and produces a
    deterministic `notebooklm` command plan with optional live execution behind
    `--execute`.
  - Added focused regression coverage in `tests/test_notebooklm_pack_ingest.py`.
  - Live validation now succeeded against the local authenticated NotebookLM
    environment, including notebook creation, source upload, source wait, and
    source/artifact/status listing.
  - Fixed real live mismatches in the wrapper:
    nested JSON response shapes for notebook/source creation, unsupported
    `source wait --interval`, and local CLI discovery from the repo `.venv`.
  - Added hard preflight guards so oversized packed sources are rejected
    before any NotebookLM upload step if they exceed:
    - `500000` words
    - `200 MiB` bytes
  - The normalized `pack_run` record now stores those enforced source caps.
  - Kept a persistent validation notebook:
    `ITIR notebooklm-pack integration`
    (`ad2bbd9a-2c9c-47ee-a607-f2b735999d99`)
    with seeded linkage artifacts stored under
    `.cache_local/notebooklm_pack_runs/20260329_persistent_integration_seed/`.
  - Updated `docs/planning/notebooklm_pack_to_notebooklm_py_interface_20260329.md`,
    `docs/planning/jmd_notebooklm_seam_minimal_object_20260329.md`,
    `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and
    `SensibLaw/COMPACTIFIED_CONTEXT.md` so the repo now records the live
    success and the next JMD question as seam-object disambiguation rather
    than NotebookLM liveness.
- notebooklm-pack to notebooklm-py interface note:
  - Added `docs/planning/notebooklm_pack_to_notebooklm_py_interface_20260329.md`
    to define the clean integration seam between the sibling Rust packer and
    the repo’s existing NotebookLM interfaces.
  - Recorded the intended order as:
    repo corpus -> notebooklm-pack -> notebooklm-py -> StatiBaker capture ->
    SensibLaw reuse.
  - Updated `README.md`, `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and
    `SensibLaw/COMPACTIFIED_CONTEXT.md` so later implementation stays scoped
    to a small source-ingest wrapper or manifest-normalizer rather than a
    semantic bridge.
- notebooklm-pack boundary check:
  - Added `docs/planning/notebooklm_pack_zos_jmd_boundary_20260329.md` after
    checking the new sibling `../notebooklm-pack` repo against the current
    `ZOS` / `JMD` notes.
  - Recorded that the pack is a bounded NotebookLM source-packing utility, not
    evidence for `ZOS <-> SL` semantics, JMD push/pull, admissibility, or
    proof/receipt boundaries.
  - Updated `README.md`, `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and
    `SensibLaw/COMPACTIFIED_CONTEXT.md` so later work keeps that boundary
    explicit.
- Affidavit duplicate-root builder followthrough:
  - Updated `SensibLaw/scripts/build_affidavit_coverage_review.py` so the
    builder now promotes duplicate or near-duplicate support clauses ahead of
    nearby contextual clauses and emits `claim_root_id`, `claim_root_text`,
    `claim_root_basis`, and `alternate_context_excerpt` on affidavit rows.
  - Added focused regression coverage in
    `SensibLaw/tests/test_affidavit_coverage_review.py`.
  - Reran the live Johl Google Docs pair after the first bounded
    duplicate-root pass; `p2-s38` and `p2-s39` now resolve as support, while
    `p2-s5` and `p2-s6` remain the next same-incident sibling-leaf
    cross-swap gap and `p2-s21` still reads closer to adjacent event or
    substitution than true support.
  - Updated `docs/planning/affidavit_claim_reconciliation_contract_20260329.md`,
    `docs/planning/affidavit_coverage_review_lane_20260325.md`, `TODO.md`,
    `COMPACTIFIED_CONTEXT.md`, and
    `SensibLaw/COMPACTIFIED_CONTEXT.md` so the repo now records that the first
    duplicate-root followthrough is landed and that sibling-leaf handling is
    the next affidavit-lane quality boundary.
- Affidavit duplicate-root and Mary-parity planning alignment:
  - Updated `docs/planning/affidavit_claim_reconciliation_contract_20260329.md`, `docs/planning/affidavit_coverage_review_lane_20260325.md`, and `docs/planning/mary_parity_user_story_acceptance_matrix_20260315.md` to record the next honest affidavit-lane quality boundary: duplicate-root and same-incident sibling-leaf reconciliation across sides, with the live Johl affidavit / response pair treated as the primary Mary-parity fixture.
  - Updated `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and `SensibLaw/COMPACTIFIED_CONTEXT.md` so the repo now prioritizes shared-root clustering, side-local leaf relations, and typed local authority reading ahead of broader substitution widening.
- Affidavit relation-classifier followthrough:
  - Updated `SensibLaw/src/fact_intake/read_model.py` so the affidavit proving-slice lane now emits explicit `relation_type` alongside `relation_root`, `relation_leaf`, `explanation`, and `missing_dimensions`, with final section bucketing driven by typed relation output rather than only by coverage/support heuristics.
  - Updated `SensibLaw/tests/test_query_fact_review_script.py` to assert relation-type and classification behavior on the contested proving-slice surface.
  - Updated `docs/planning/affidavit_claim_reconciliation_contract_20260329.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo now records this read-model followthrough accurately while keeping the remaining upstream-builder move explicit.
- TEMP ZOS/SL bridge admissibility stage:
  - Added an explicit post-ranking admissibility boundary in `TEMP_zos_sl_bridge_impl/python/zos_pipeline/` so the temp bridge now separates candidate ranking from accepted/rejected outputs.
  - Added decision-shape wiring, CLI flags (`--admit`, `--min-score`, `--min-spectral`), and regression coverage in `TEMP_zos_sl_bridge_impl/python/tests/test_pipeline.py`.
  - Updated `docs/planning/temp_zos_sl_bridge_impl_review_20260329.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` to record that the bridge now has the required acceptance boundary, while resonance governance and threshold tuning remain open.
- Agda docs alignment:
  - Updated `SensibLaw/docs/interfaces.md` and `SensibLaw/docs/plan_qg_unification_sl_da51_agda_contract_20260324.md` so the Agda-facing boundary now explicitly matches the current `CLOCK` / `DASHI` reading: cyclic `Z/6 -> Z/3` lift, not dihedral, with cone / contraction / MDL retained as the admissibility gate.
  - Updated `SensibLaw/todo.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` to keep that interpretation explicit before returning to the retrieval-side admissibility work.
- CLOCK/DASHI and bridge-governance tightening:
  - Updated `docs/planning/resonance_and_overlap_findings_20260329.md` to make the final cyclic-lift reading explicit: `CLOCK` as `Z/6`, `DASHI` as `Z/3`, the extra bit as microphase rather than involution, and the structural analogy to proposal vs promoted-truth layers.
  - Updated `docs/planning/temp_zos_sl_bridge_impl_review_20260329.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` to pin the preferred bridge operator shape as `manifold_aware_rank -> candidate set -> admissibility filter -> promoted outputs`.
- TEMP ZOS/SL bridge remediation:
  - Fixed packaging/tests in `TEMP_zos_sl_bridge_impl/python` so `pytest -q` now runs from the bundle itself.
  - Added shared lexical `lex::*` features so query and shard vectors intersect on structured fact-derived content instead of living in separate namespaces.
  - Replaced the dead constant domain bonus with query-sensitive domain assignment: prefer explicit `domain_hint` values and otherwise infer domains from trace-window clusters with centroid matching.
  - Updated the temp bundle docs and review note to reflect that packaging, feature overlap, and domain scoring are fixed, while resonance demotion and admissibility are still open.
- TEMP ZOS/SL bridge review and thread sync:
  - Added `docs/planning/temp_zos_sl_bridge_impl_review_20260329.md` to record the review finding that the temporary bridge bundle is not ready to integrate as-is: packaging/tests fail, query/shard features do not intersect enough, domain scoring is effectively inactive, and surrogate resonance is mixed into the core score.
  - Added `docs/planning/resonance_and_overlap_findings_20260329.md` to pin the `CLOCK` as `Z/6` cyclic-lift reading, with cone, contraction, and MDL required before phase becomes admissible dynamics.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the current bridge work now has explicit guardrails and the missing thread is actually recorded.
- RG toy completion thread captured:
  - Added `docs/planning/rg_toy_completion_findings_20260329.md` to record that remaining RG-toy work is proof/content: sharper coarse agreement, real coarse-graining operator, scaling/relevance theorem, observable algebra, universality, and the theorem packs (quadratic emergence, signature/arrow/cone coupling, MDL Lyapunov descent, constraint closure, universality instances).
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` with the new note.
- AAO-all route panel split:
  - extracted the route's controls block into `ControlsPanel.svelte` and the
    selected-node context block into `ContextPanel.svelte`.
  - kept the route focused on graph assembly, evidence-lane derivation, and
    corpus-doc linking, with the new panel boundaries covered by
    `tests/graph_ui_regressions.test.js`.
- ITIR rehearsal can now use real promoted manifests and tars:
  - `rehearse-selector-fetch` and `rehearse-selector-local-tar-fetch` accept an optional container fixture and default to inferring member paths (shardId.cbor/payload/shardId.cbor) when absent.
  - `resolve_selector_to_local_member_payload` now works without a container index, so the harness can point at `/tmp/erdfa-promoted-manifest.json` and `/tmp/erdfa-demo.tar` emitted by the upstream `erdfa-publish-rs` demo.
  - Added coverage for the no-container path in `tests/test_hf_container_rehearsal.py`.
- `erdfa-publish-rs` promoted-manifest patch:
  - Patched `/home/c/Documents/code/erdfa-publish-rs/src/lib.rs` to add additive manifest-layer types: `BuildProvenance`, `ObjectRef`, `PromotedShardRef`, and `PromotedShardSet`, while keeping existing `Shard` and `ShardSet` intact.
  - Added helper conversions from `Shard` into thin and promoted refs plus regression coverage for richer manifest metadata and DA51-tagged promoted-manifest CBOR.
  - Updated `/home/c/Documents/code/erdfa-publish-rs/README.md` with the promoted-manifest usage slice and revalidated the crate with `cargo test -q`.
- AAO timeline refactor documentation sync:
  - reflected the completed `itir-svelte/src/lib/server/wiki_timeline/` runtime split and the slimmed-down `wikiTimelineAoo.ts` adapter in `docs/planning/largest_file_refactor_roadmap_20260328.md`
  - captured the current AAO-all route state (helper-backed graph/selection logic with inline controls/context/evidence panels remaining) in `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and `devlog.md`
  - marked the remaining component-extraction follow-up so future implementation rounds know the exact next gap before rerunning `node --test tests/graph_ui_regressions.test.js`
- Local tar extraction in rehearsal harness:
  - Extended `itir_jmd_bridge/hf_rehearsal.py` with local tar-member
    extraction and selector-to-local-member composition.
  - Added `rehearse-local-tar-extract` and
    `rehearse-selector-local-tar-fetch` to `itir_jmd_bridge/cli.py`.
  - Extended `tests/test_hf_container_rehearsal.py` to cover tar-member
    extraction and selector-driven local tar fetch.
  - Revalidated with
    `pytest -q tests/test_hf_container_rehearsal.py tests/test_erdfa_manifest_promotion_fixture.py`.
- Selector-to-container rehearsal composition:
  - Extended `itir_jmd_bridge/hf_rehearsal.py` so the local rehearsal path can
    now resolve selectors through the promoted-manifest fixture into HF
    container/member metadata.
  - Added `rehearse-selector-fetch` to `itir_jmd_bridge/cli.py`.
  - Extended `tests/test_hf_container_rehearsal.py` with selector-resolution
    coverage and revalidated alongside the promoted-manifest fixture tests via
    `pytest -q tests/test_hf_container_rehearsal.py tests/test_erdfa_manifest_promotion_fixture.py`.
- `erdfa-publish-rs` promoted-manifest fixture:
  - Added `docs/planning/jmd_fixtures/erdfa_manifest_promotion_v1.example.json`
    as the first tiny concrete fixture for the promoted manifest shape.
  - Added regression coverage in `tests/test_erdfa_manifest_promotion_fixture.py`.
  - Validated together with the HF rehearsal slice via
    `pytest -q tests/test_erdfa_manifest_promotion_fixture.py tests/test_hf_container_rehearsal.py`.
- HF container rehearsal harness:
  - Added `itir_jmd_bridge/hf_rehearsal.py` with a tiny local resolution path
    that loads the pinned HF container fixture and resolves `shardId` to
    container/member metadata.
  - Added `rehearse-hf-container` to `itir_jmd_bridge/cli.py` so the fixture
    can be exercised via `python -m itir_jmd_bridge`.
  - Added regression coverage in `tests/test_hf_container_rehearsal.py`.
  - Validated with `pytest -q tests/test_hf_container_rehearsal.py`.
- `erdfa-publish-rs` manifest promotion v1:
  - Added `docs/planning/erdfa_publish_rs_manifest_promotion_v1_20260329.md`
    to pin the second ranked design step as a manifest-layer promotion rather
    than a shard-payload rewrite.
  - Recorded the intended minimum additions as:
    artifact identity/provenance plus per-shard `logicalKind`, `encoding`,
    `sizeBytes`, and optional sink/routing metadata.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so later
    implementation work keeps existing `Shard`/`cid`/DA51 primitives intact
    while enriching only the manifest/catalog layer first.
- HF container/index fixture v1:
  - Added `docs/planning/hf_container_index_fixture_v1_20260329.md` and
    `docs/planning/jmd_fixtures/hf_container_index_v1.example.json` as the
    first tiny HF batching spec fixture.
  - Recorded the three-level separation explicitly:
    artifact identity, container metadata, and member metadata.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so later
    implementation work now has a pinned minimal example for container/member
    resolution.
- zkperf on SL contract v1:
  - Added `docs/planning/zkperf_on_sl_contract_v1_20260329.md` and
    `docs/planning/jmd_fixtures/zkperf_on_sl_observation_v1.example.json` as
    the first bounded `zkperf`-on-`SL` contract and fixture.
  - Recorded `ZKPerfObservation` as an observational, receipt-bearing shape
    with structured metrics, trace/proof refs, optional artifact linkage, and
    explicit non-authority for truth promotion.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so later
    ranking/artifact-linkage work now has a pinned SL-side input shape.
- zkperf on SL roadmap:
  - Added `docs/planning/zkperf_on_sl_roadmap_20260329.md` to pin `zkperf` on
    `SL` as the next gating lane before the previously-ranked implementation
    work on HF container fixtures, richer `erdfa-publish-rs` manifests, and
    rehearsal harnesses.
  - Recorded the intended role of `zkperf` as structured, receipt-bearing
    execution/proof material represented on the `SL` side before it is used by
    ranking or artifact-linkage layers.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now treats a small `zkperf_on_sl_contract_v1` note plus fixture as the next
    smallest useful deliverable.
- Shard stack layer order:
  - Added `docs/planning/shard_stack_layer_order_20260329.md` as the shortest
    end-to-end stack summary for the current shard/retrieval design.
  - Recorded the intended order as:
    `SL -> logical shard/artifact contract -> optional spectral ranking -> optional HF container/index -> sink fetch -> Zelph`.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so future
    discussion has one anti-confusion reference when truth, shard identity,
    ranking, batching, and retrieval start blending together.
- Spectral post-selector retrieval contract:
  - Added `docs/planning/spectral_post_selector_retrieval_contract_20260329.md`
    to pin spectral/eigenvector retrieval as an optional ranking layer that
    runs after selector resolution and before fetch.
  - Recorded the required ordering as:
    `selector -> logical shard ids -> spectral ranking -> fetch subset`,
    with a structured-feature-only rule and mandatory abstention when
    domain/manifold validity fails.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so ranking
    heuristics remain separated from selector semantics, shard identity, HF
    batching, and SL truth construction.
- HF container/index contract:
  - Added `docs/planning/hf_container_index_contract_20260329.md` to pin the
    HF batching layer as a distinct projection over logical shards rather than
    a replacement for the shared shard contract.
  - Recorded the intended ordering as:
    `logical shards -> container membership -> uploaded HF objects -> published index`,
    with selector-first retrieval preserved under batching.
  - Recorded the current best-fit physical direction as:
    `tar` outer format, `CBOR` payload members, `JSON` control/meta, and
    optional `zstd`.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so future HF
    batching work stays separate from shard identity, selector semantics, and
    spectral ranking logic.
- JMD HF container and spectral retrieval findings:
  - Re-pulled ChatGPT online UUID `69c4a9b1-d014-83a0-8bb0-873e4eaa4098` after
    further updates and resolved it again to canonical thread ID
    `c6e383233d0d7c4efde671be1432c825054cb222`.
  - Added `docs/planning/jmd_hf_container_and_spectral_retrieval_findings_20260329.md`
    to record three materially stronger readings from the updated thread:
    the logical artifact contract is more mature than "missing API", HF
    file-count pressure motivates a container/index design, and spectral
    retrieval belongs as a post-selector ranking layer over candidate shards.
  - Recorded the concrete batching direction from the thread as:
    `microshards -> sealed container -> uploaded object -> published manifest index`,
    with `tar` outer format, `CBOR` payload members, `JSON` control/meta, and
    optional `zstd`.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now keeps HF containerization and structured-feature spectral retrieval as
    explicit follow-up layers rather than vague extensions of the transport or
    truth contracts.
- Canonical ZKP / SL / DA51 message schema findings:
  - Pulled ChatGPT online UUID `69c3f3e7-3440-839c-8a3e-05309f1269dd` into the
    canonical archive and resolved it to canonical thread ID
    `d70ac076cbdc08df81a593b66a8915541f71f08b` from the DB.
  - Added `docs/planning/canonical_zkp_sl_da51_message_schema_findings_20260329.md`
    to record the useful future-facing message-envelope direction:
    content-addressed message IDs, JSON/CBOR dual projection, provenance DAG
    links, and optional proofs/signatures.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now keeps envelope/message schema direction separate from shard/artifact
    contracts and does not overstate that thread as a pinned wire standard.
- `erdfa-publish-rs` vs shared shard contract:
  - Added `docs/planning/erdfa_publish_rs_vs_shared_shard_contract_20260329.md`
    to compare the actual local `/home/c/Documents/code/erdfa-publish-rs`
    `ShardSet` model against the ITIR shared-shard contract.
  - Recorded that `erdfa-publish-rs` is already strong on publish-side
    primitives:
    DA51 CBOR shards/manifests, content-addressed `cid`, tar emission, and
    IPFS/paste helpers.
  - Recorded the remaining gap explicitly:
    the current crate does not yet carry artifact revision/provenance, routing
    keys, or first-class multi-sink `objectRefs[]`, so it should be treated as
    the publish substrate rather than the full Zelph-facing shared contract.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` to keep that
    distinction durable.
- `n00b` corroborating surfaces:
  - Added `docs/planning/n00b_corroborating_surfaces_20260329.md` to record
    what `n00b/` usefully corroborates and what it still does not settle.
  - Recorded the relevant `n00b/.gitmodules` source mappings, including:
    `source/erdfa-publish` ->
    `https://github.com/meta-introspector/erdfa-publish.git`,
    `source/pick-up-nix` ->
    `https://github.com/meta-introspector/pick-up-nix.git`,
    and the HF-hosted frontend sources.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so `n00b/`
    is now treated as corroborating ecosystem evidence, not as a replacement
    for the current ITIR shard/routing/infra contract notes.
- Zelph / ERDFA / HF / IPFS example flow:
  - Added `docs/planning/zelph_erdfa_hf_ipfs_example_flow_20260329.md` to pin
    one concrete selector -> shard id -> sink ref -> fetch -> Zelph load/query
    walkthrough.
  - Recorded the publish/query split more concretely:
    `erdfa`/Kant-style packaging emits logical shard identity, digests,
    manifests, and HF/IPFS sink refs, while `Zelph` resolves selectors to
    logical shard ids before fetching an object from a chosen sink.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now has a direct example of how one logical shard can be mirrored to both
    HF and IPFS without changing shard meaning.
- JMD push/pull surfaces and blockers:
  - Added `docs/planning/jmd_push_pull_surfaces_and_blockers_20260329.md` to
    separate three inputs that had been getting conflated:
    semantic boundary clarification from the refreshed JMD thread, local
    scaffold value from `../rust-nix-template`, and the still-missing external
    JMD infra contract.
  - Refined the note after a fresh online re-pull:
    the refreshed JMD thread now also contributes a stronger proof-first API
    framing, with service proof described in terms of Nix flake, git history,
    perf profile, resource use, and `zkperf + erdfa` named as "the API".
  - Added one explicit provisional contract inference from that thread:
    `artifact + erdfa payload + zkperf receipt`, while keeping it marked as
    inference rather than declared JMD spec.
  - Recorded that even with that stronger inference, the thread still does not
    by itself declare stable remote push/pull endpoints, replay semantics, or
    receipt semantics.
  - Recorded that `../rust-nix-template` is useful as a local Rust/Nix home
    for a publisher/puller seam, but not as evidence that JMD host semantics
    are pinned.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so future
    push/pull work keeps semantic boundary info, local scaffolding, and
    external infra uncertainty as separate planning inputs.
- Robust context fetch for `ZOS -> SL -> Zelph` ordering:
  - Pulled ChatGPT online UUID `69c4a9b1-d014-83a0-8bb0-873e4eaa4098` into the
    canonical archive and resolved it to canonical thread ID
    `c6e383233d0d7c4efde671be1432c825054cb222` from the DB.
  - Added `docs/planning/zos_sl_zelph_contract_findings_20260328.md` to pin
    the thread-backed stack ordering:
    ZOS as dynamic candidate state, SL as deterministic extraction/promotion,
    and Zelph as downstream fact-graph reasoning.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now records the fetched thread's practical next-step order:
    define `ZOS <-> SL`, build a minimal Python ZOS engine, then map into a
    Zelph input layer.
  - Re-pulled the same online thread on 2026-03-28 after it changed and
    tightened the note further:
    ZOS must supplement, not replace or silently supplant, SL truth
    construction, and any first ZOS engine must operate on structured SL facts
    rather than naive raw-token frequency.
- ZOS vs fuzzymodo / Casey / StatiBaker role comparison:
  - Added `docs/planning/zos_vs_fuzzymodo_casey_statiBaker_20260328.md` to pin
    the practical comparison against existing repo roles.
  - Recorded the current finding that `ZOS` is closest to `fuzzymodo` as a
    supplemental reasoning/organization layer, not to `casey-git-clone` or
    `StatiBaker`.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so future
    ZOS work is now expected either to collapse into a semantic sub-lane of
    `fuzzymodo` or remain separate under explicit prohibitions against truth,
    mutable workspace, and observer-memory ownership.
- Publisher/puller contract for Zelph consumers:
  - Added
    `docs/planning/publisher_puller_contract_for_zelph_consumers_20260328.md`
    to make the push/pull split explicit without implying that `Zelph` owns
    publication.
  - Recorded the consumer/publisher split as:
    publisher/puller emits logical artifacts, sink refs, and receipts;
    `Zelph` resolves selectors to logical shards, fetches them, and loads/querys
    them.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so future
    ITIR-facing work now points at one shared logical artifact contract between
    upstream truth/promotion, publisher/puller infrastructure, and downstream
    Zelph consumption.
- Publish-layer findings before Rust template work:
  - Added `docs/planning/publish_layer_findings_20260328.md` to freeze the
    current read on the publish-layer question before more Rust-facing
    exploration turns into an accidental contract.
  - Recorded the current role split:
    `kant-zk-pastebin` as the strongest retrieval / shard-manifest reference
    surface, `erdfa-publish-rs` as the strongest ERDFA shard-production
    surface, ZOS as publish/pull orchestrator, and Zelph as read/query
    consumer.
  - Tightened the intended first publisher slice to:
    logical artifact input -> digest and sink refs -> receipt output, with
    query routing and JMD bridge semantics explicitly kept out of scope.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the
    findings are durable repo state before implementation.
- Began the `scripts/chat_context_resolver.py` refactor by extracting the
  transcript/analysis subsystem into:
  - `chat_context_resolver_lib/transcript.py`
  - `chat_context_resolver_lib/analysis.py`
- Updated `scripts/chat_context_resolver.py` to consume those helpers without
  changing the CLI surface, and added focused regression coverage in
  `tests/test_chat_context_resolver_analysis.py`.
- Bounded climate text producer for the Wikidata `Phi` bridge:
  - Added `SensibLaw/schemas/sl.wikidata.climate_text_source.v1.schema.yaml`
    to define the revision-locked climate text-source input surface for the
    first real text-side producer in the `P5991 -> P14143` lane.
  - Added runtime helpers in `SensibLaw/src/ontology/wikidata.py` to emit
    `sl.observation_claim.contract.v1` rows from explicit year/value climate
    lines and feed that payload directly into the existing migration-pack
    bridge.
  - Extended
    `SensibLaw/scripts/materialize_wikidata_migration_pack.py` with optional
    `--climate-text-source` and `--climate-observation-claim-output` flags so
    one materialization run can now emit both the derived Observation/Claim
    payload and the bridge-enriched migration pack.
  - Updated the climate protocol note, bridge contract note, `TODO.md`, and
    compact context so the repo now describes the first real climate text
    producer as implemented and still intentionally narrow.
  - Recorded the current live target-selection result:
    `HSBC` / `Q190464` is not a valid target for this lane right now because
    it does not currently expose live `P5991`, so the first real artifact
    hunt should pivot to already-pinned entities such as `Atrium Ljungberg`
    or `Akademiska Hus`.
  - Added the first non-fixture climate text artifact for
    `Q10403939` / `Akademiska Hus` at
    `SensibLaw/data/ontology/wikidata_migration_packs/p5991_p14143_climate_pilot_20260328/climate_text_source_q10403939_akademiska_hus_scope1_2018_2020.json`
    using official annual report excerpts from 2018, 2019, and 2020.
  - Validated the artifact against
    `sl.wikidata.climate_text_source.v1`, converted it into `3` promoted
    observations / claims, and ran it through the current bridge against the
    pinned five-entity climate pack.
  - Current real-source result:
    before the temporal matcher fix, all `24` current `Q10403939`
    candidates received `contradiction` pressure from the older scope-1 text
    slice against the current 2023 multi-scope structured bundle.
  - Added period-aware mismatch gating in
    `SensibLaw/src/ontology/wikidata.py` so out-of-period text observations no
    longer collapse straight to hard contradiction when the structured bundle
    carries a different explicit year slice.
  - Added focused regression coverage in
    `SensibLaw/tests/test_wikidata_projection.py` for out-of-period value
    mismatches.
  - Re-running the real `Q10403939` artifact now yields `split_pressure` on
    all `24` candidates instead of `contradiction`, which better matches the
    intended review semantics.
  - Added a generic revision-locked `sl.source_unit.v1` schema at
    `SensibLaw/schemas/sl.source_unit.v1.schema.yaml` plus a
    `SourceUnitAdapter`-style runtime path in
    `SensibLaw/src/ontology/wikidata.py`.
  - Kept `sl.wikidata.climate_text_source.v1` working as a backward-compatible
    legacy subtype by adapting it into the generic source-unit payload before
    extraction.
  - Added focused coverage showing the same extractor/bridge path now accepts
    both legacy climate payloads and HTML snapshot source units.
- Boundary-artifact / morphism framing:
  - Added
    `SensibLaw/docs/planning/boundary_artifact_morphism_contract_20260328.md`
    to pin the next higher docs-first formalism above the current boundary
    object family.
  - Recorded the current decision that `SourceUnit`, `SplitPlan`,
    `EventCandidate`, affidavit comparison artifacts, and affect overlays are
    now real enough to treat as a shared boundary-artifact family.
  - Kept runtime unification deferred:
    the repo now documents governed morphisms and composition rules as the next
    abstraction, but does not yet introduce a shared transformation engine.
  - Tightened that note with the first concrete candidate next layer:
    `BoundaryArtifact.v1`, `Morphism.v1`, a bounded composition validator, and
    a small readable transformation DSL, still as docs-first planning only.
- Cross-system `Phi_meta` tightening:
  - Recorded that `Phi_meta` is already shipped as a bounded executable layer
    in `SensibLaw`, so the next useful step is a concrete example instance plus
    a bounded real-data prototype rather than another abstract schema rewrite.
  - Made the lane split explicit:
    the Wikidata climate lane still points at `source_capture -> SourceUnit`,
    while the cross-system legal lane now points at the bounded two-system
    prototype as its next optimal move.
- ITIR / SensibLaw receipts-first compiler spine:
  - Added
    `docs/planning/itir_sensiblaw_receipts_first_compiler_spine_20260328.md`
    to pin the strongest shared architectural reading across the current ITIR
    and SensibLaw materials.
  - Recorded the five-layer split:
    source substrate -> deterministic extraction -> promotion -> reasoning ->
    public-action packaging.
  - Recorded the main architectural rule that promotion is the center of the
    system, while graph reasoning and public packaging remain downstream of
    promoted truth.
  - Synced `TODO.md` and compact context so the next milestone is explicit:
    one bounded doctrine prototype that proves the whole receipts-first spine
    end to end.
- ITIR / SensibLaw identity-trust alignment refinement:
  - Added
    `docs/planning/itir_sensiblaw_identity_trust_alignment_layer_20260328.md`
    to record the stronger reading that the suite must bridge lived
    experience, evidence, formal rules, and trust-preserving action rather
    than acting as only a legal compiler.
  - Tightened the receipts-first compiler spine note so the first bounded
    doctrine prototype is now expected to be not only receipt-backed but also
    explicitly non-gaslighting and trust-preserving in presentation.
  - Synced `TODO.md` and compact context so the stronger requirement is
    durable repo state:
    trustworthy, non-gaslighting support without forcing the user to restate
    the whole story from scratch.
- Refreshed `ZKP for ITIR SensibLaw` online thread sync:
  - Pulled online UUID `69c7b950-daec-839d-89a9-8fd8e22c9136` into the
    canonical archive and resolved it to canonical thread ID
    `31a47318f53b61cac9f82705e2595b1a08f9af66` from the DB.
  - Added
    `docs/planning/itir_sensiblaw_operational_readiness_overlay_20260328.md`
    to record the next maturity gap above the current compiler spine:
    service-level definitions, incident vs problem handling, measurable
    success criteria, and explicit system-boundary / handoff views.
  - Synced `TODO.md` and compact context so those readiness gaps are durable
    repo state instead of chat-only guidance.
  - Fixed a local refactor regression in `scripts/chat_context_resolver.py`
    where stale `_truncate_text` references broke DB-backed UUID resolution
    after the helper extraction pass.
- ITIR / SensibLaw standard service application model:
  - Added
    `docs/planning/itir_sensiblaw_standard_service_application_model_20260328.md`
    to pin the repeatable application pattern for new case families above the
    existing compiler-spine and trust/readiness notes.
  - Recorded the standard case flow:
    intake -> evidence structuring -> identity/context modelling -> alignment
    -> obligation assignment -> output -> monitoring/escalation.
  - Synced `TODO.md` and compact context so the next doctrine prototype is now
    expected to carry a standardized intake shape, a mandatory obligation
    layer, a nonconformance grammar, and a minimal metric set rather than
    being argued case by case.
- ITIR / SensibLaw everyday mode:
  - Added `docs/planning/itir_sensiblaw_everyday_mode_20260328.md` to pin the
    lighter operating mode for ordinary, low-stakes scenarios without
    splitting the architecture into a second system.
  - Recorded the operating-mode rule:
    same architecture, different thresholds/defaults/surface area, with
    everyday mode biased toward guidance and next-best-action output rather
    than proof-heavy packaging.
  - Synced `TODO.md` and compact context so the next explicit design gap is
    bounded switching criteria between crisis/adversarial mode and
    everyday/navigation mode.
- ITIR / SensibLaw case-type libraries + KPI model:
  - Added
    `docs/planning/itir_sensiblaw_case_type_libraries_and_kpi_model_20260328.md`
    to define the next service layer above the standard flow:
    fixed-shape case libraries plus a shared KPI model.
  - Recorded the first four libraries supported by the current corpus:
    tenancy, abuse/accountability, medical/trauma-informed care,
    welfare/support.
  - Synced `TODO.md` and compact context so the next bounded prototype is now
    expected to choose one concrete library and one minimal KPI slice instead
    of staying fully generic.
- ITIR / SensibLaw diagrams + mode-switching / UI / templates:
  - Added
    `docs/planning/itir_sensiblaw_service_architecture_plantuml_20260328.puml`
    as the repo-owned PlantUML bundle for the system context, containers,
    standard flow, four case libraries, and obligation sequence.
  - Added
    `docs/planning/itir_sensiblaw_mode_switching_ui_and_templates_20260328.md`
    to define the next product-layer refinement:
    bounded mode switching, everyday UI flow, and common ordinary-user
    templates.
  - Tightened that note with a deterministic trigger reading over risk,
    time pressure, conflict level, evidence completeness, trust state, and
    user intent, plus a simple mode decision matrix and behavioral
    differences between light and strict operation.
  - Added explicit everyday screen and tone structure guidance along with
    always-on guardrails:
    no identity assertions without evidence, no moralizing language,
    no hidden assumptions, abstain when uncertain, local-first by default.
  - Extended the same note with concrete light-to-strict scenario templates
    for work/manager conversations, email/communication, tenancy friction,
    money/bills, health/appointments, personal planning, and low-to-high
    conflict.
  - Added starter mode/UX/safety KPIs and documented the `Mode Controller`
    placement in the container/application view so mode is treated as an
    explicit control surface rather than a hidden UI toggle.
  - Consolidated the same note further with the product-spec surface for the
    mode controller itself:
    inputs, outputs, deterministic logic, behavior profiles, trust controls,
    and the core `Obligation` primitive.
  - Extended the PlantUML bundle with explicit mode-controller alignment and
    everyday UX-flow diagrams so the controller and light/strict UX paths are
    visible in the architecture artifacts.
  - Added compact PlantUML variants for context, container, mode selection,
    standard flow, and obligation lifecycle so the architecture now has both
    concise and expanded diagram views in one repo-owned bundle.
  - Added the final system summary to the mode/UI note:
    the suite is now documented not only as a thinking aid but as a
    controlled service that turns human situations into structured,
    actionable, accountable outcomes.
  - Synced `TODO.md` and compact context so the next design gap is now
    explicit:
    define the switch table and starter everyday template set before widening
    normal-user scope further.
- ITIR / SensibLaw production schema / dashboard / deployment pack:
  - Added
    `docs/planning/itir_sensiblaw_production_schema_dashboard_deployment_pack_20260328.md`
    to define the next production-facing contract layer for entities,
    dashboards, and local-first deployment.
  - Recorded the first production entity set, the three-layer dashboard split,
    and the staged local-first deployment topology:
    local single-user runtime first, optional trusted sync second, restricted
    collaboration later.
  - Synced `TODO.md` and compact context so the immediate production
    validation target is now explicit:
    validate a local-first single-user case engine with truth-status states,
    obligation object, and dashboard surfaces before attempting full
    collaboration-platform scope.
- Refreshed online thread sync for fact-bundle and affect boundaries:
  - Refreshed three ChatGPT threads live via `robust-context-fetch`,
    including the missed `Zero Trust Ontology` UUID, and recorded the
    canonical IDs plus live-refresh status in `COMPACTIFIED_CONTEXT.md`.
  - Added
    `docs/planning/all_sources_factbundle_reconciliation_boundary_20260328.md`
    to pin the broader direction:
    current `Observation` / `Claim` work should generalize toward an
    all-sources reconciliation bundle over promoted observations/claims, not
    a Wikidata-shaped canonical ontology.
  - Added `docs/planning/sentiment_affect_noncanonical_boundary_20260328.md`
    to pin the current doctrine that sentiment/affect remains
    speaker/utterance-anchored candidate or overlay material rather than
    legal truth.
  - Updated `README.md`, `TODO.md`,
    `docs/planning/sl_observation_claim_contract_20260327.md`, and
    `docs/planning/transcript_semantic_phase_v1_20260308.md` so those
    refreshed boundaries are durable repo state rather than chat-only memory.
- Added `docs/planning/orchestrator_control_plane_20260328.md` to record the
  current shared-orchestration control-plane state for `ITIR-suite`.
- Recorded the current orchestration boundary:
  - multi-runner coordination in one repo is now supported via namespaced
    runner-local status/log files in the shared control-plane skills
  - child handoffs now start from a compact ZKP frame plus runtime
    model-allocation block
  - master-orchestrator -> sub-orchestrator hierarchy is still only supported
    by convention, not as first-class governed runtime support
- Updated `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and `devlog.md` so the next
  control-plane step is explicit:
  add first-class hierarchical orchestrator support with parent/child
  registry, lane ownership, and completion/escalation reporting.
- Added `docs/planning/largest_file_refactor_roadmap_20260328.md` to inventory
  the largest repo-owned code files and pin the next high-value normalization
  slices.
- Recorded the current large-file governance rule:
  prioritize extraction where reusable suite contracts are still encoded behind
  lane-specific names such as `AAO`, Zelph/HF transport labels, or other
  historical one-surface seams.
- Tightened the roadmap workflow so file triage now requires a bounded
  file-local refactor brief before any implementation queueing starts.
- Added `docs/planning/largest_file_refactor_priority1_briefs_20260328.md` to
  supply the first five file-local briefs required by that workflow.
- Updated `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and `devlog.md` so the audit is
  durable repo state rather than an ephemeral chat decision.
- Typed latent-graph runtime slice over promoted relations:
  - Added `SensibLaw/src/latent_promoted_graph.py` and
    `SensibLaw/schemas/sl.latent_promoted_graph.v1.schema.yaml` so the repo
    now has a bounded executable `L(P)`-style graph contract over promoted
    relations rather than only planning prose.
  - Added `SensibLaw/tests/test_latent_promoted_graph.py` to validate the
    graph contract over real AU and GWB promoted semantic reports.
  - Extended `SensibLaw/src/cross_system_phi.py`,
    `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`, and
    `SensibLaw/examples/cross_system_phi_minimal.json` so the current `Phi`
    payload now exposes latent-graph summaries and mapping-level latent graph
    refs tied to the same promoted-record provenance basis.
- `Phi` witness/explanation enrichment:
  - Extended `SensibLaw/src/cross_system_phi_meta.py` so `Phi_meta`
    validation now emits explicit witness objects for type, role, authority,
    constraint, and scope checks.
  - Extended `SensibLaw/src/cross_system_phi.py` and
    `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml` so
    admitted mappings now carry `mapping_explanation` plus structured witness
    detail rather than only a free-text rationale.
  - Updated `SensibLaw/examples/cross_system_phi_minimal.json` and tightened
    regression coverage in
    `SensibLaw/tests/test_cross_system_phi_meta.py` and
    `SensibLaw/tests/test_cross_system_phi_prototype.py`.
- `Phi_meta` admissibility gate:
  - Added `SensibLaw/schemas/sl.cross_system_phi_meta.v1.schema.yaml` and
    `SensibLaw/src/cross_system_phi_meta.py` so cross-system mapping now has a
    bounded type/authority/constraint admissibility layer above `Phi_ij`.
  - Extended `SensibLaw/src/cross_system_phi.py` and
    `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml` so the
    current real prototype emits `meta_validation` receipts for admitted
    mappings and an explicit `meta_validation_report` for blocked pairs.
  - Added regression coverage in
    `SensibLaw/tests/test_cross_system_phi_meta.py` and updated
    `SensibLaw/tests/test_cross_system_phi_prototype.py` so one
    structurally-similar-but-inadmissible pair is blocked before `Phi_ij`
    runs.
- Real promoted-record `Phi` prototype:
  - Added `SensibLaw/src/cross_system_phi.py` so the bounded
    `sl.cross_system_phi.contract.v1` package now has a real two-system
    builder over existing promoted semantic-report rows rather than only a
    schema stub.
  - Extended `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`
    and `SensibLaw/examples/cross_system_phi_minimal.json` with:
    explicit provenance-preservation rule, provenance index, and mismatch
    workflow metadata.
  - Added `SensibLaw/tests/test_cross_system_phi_prototype.py` to validate
    the prototype against real AU and GWB promoted relations, including one
    partial mapping path, one incompatible path, and dual-anchor provenance
    guarantees.
- `Phi` relation and latent graph schema formalization:
  - Added `docs/planning/phi_mapping_and_latent_graph_schema_20260328.md` to
    document the richer formal `Phi` relation, typed `L(P)` graph schema, and
    guarded transfer semantics.
  - Recorded the crucial compatibility rule:
    the current executable `sl.cross_system_phi.contract.v1` schema remains
    the bounded transport grammar, while the richer relation kinds are a next
    formal layer rather than an already-shipped runtime change.
  - Updated the root README, TODO, compact context, `plan.md`, `status.json`,
    and `devlog.md` so the next `Milestone X` step is the richer semantic
    formalization over the bounded `v1` schema.
- Canonical planning-state realignment:
  - Replaced the stale root `spec.md` and `architecture.md` workbench scope
    with the current latent-state / cross-system mapping program.
  - Added `Milestone X` to `plan.md` and repointed `status.json` so the
    autonomous control plane now tracks the bounded `L(P)` / `Phi` contract
    package rather than the prior workbench milestone.
  - Recorded the shift in `devlog.md`; no code behavior changed in this pass.
- Global latent legal state across systems clarification:
  - Added `docs/planning/global_latent_legal_state_cross_system_20260327.md`
    to extend the latent-state discipline into the multi-system case without
    collapsing legal traditions into one hidden universal ontology.
  - Recorded that any future global lane must operate over local promoted
    truth sets `P_i` plus a checked mapping layer `Phi`, with explicit
    `exact|partial|incompatible|undefined` outcomes.
  - Updated the root README, TODO, and compact context so any future
    cross-system transfer or alignment work starts with bounded mapping
    contracts and mismatch reports rather than automatic truth merge.
- Latent state over promoted truth clarification:
  - Added `docs/planning/latent_state_over_promoted_truth_20260327.md` to pin
    `latent state` language to a derived compression over promoted truth
    rather than a hidden truth layer over raw text.
  - Recorded the required constraints for any future `L(P)` lane:
    reconstruction, anchor preservation, compression discipline, consistency
    preservation, and downstream-only authority.
  - Updated the root README, TODO, and compact context so any future latent
    graph or DASHI-style compression work stays downstream of promotion and
    cannot silently mutate truth.
- Motif candidate / promotion / legal-tree clarification:
  - Added `docs/planning/motif_candidate_promotion_legal_tree_20260327.md`
    to state the disciplined repo reading of motif, cohomology, and
    legal-tree language.
  - Recorded that motifs remain candidate/overlay structure until a lane
    defines explicit promotion semantics, and that cohomology is currently an
    analysis aid rather than a truth-bearing architectural role.
  - Updated the root README, TODO, and compact context so future legal-tree or
    motif work must stay anchored to source-linked records, promotion gates,
    and explicit node-family status.
- JMD x SensibLaw truth-construction boundary:
  - Added `docs/planning/jmd_sensiblaw_truth_construction_boundary_20260327.md`
    from the archived `Zero Trust Ontology` thread resolved via
    `robust-context-fetch`.
  - Recorded the sharpened boundary:
    `SensibLaw` is the truth-construction layer between messy source
    substrates and downstream reasoning/agent systems, not a generic JMD
    runtime or scheduler surface.
  - Updated the root README, TODO, and compact context so future JMD/SL graph
    work stays tied to source anchors, reversible transforms, promotion basis,
    and explicit abstention.
- Cross-source follow/review control-plane parity:
  - Added `SensibLaw/docs/planning/cross_source_follow_control_plane_20260327.md`
    and the first portable `follow.control.v1` queue/control-plane contract in
    `SensibLaw/src/fact_intake/control_plane.py`.
  - First concrete adopters now span AU plus generic fact-review:
    `authority_follow`, `intake_triage`, and `contested_items`.
  - `itir-svelte /graphs/fact-review` now renders these control-plane-backed
    queues generically from shared metadata/queue fields, reducing AU-specific
    UI special casing and making the next source-family rollouts cheaper.
- AU authority-follow UI bridge:
  - `itir-svelte /graphs/fact-review` now exposes the AU
    `authority_follow` operator view for AU selectors by bridging the AU
    `demo-bundle` operator surface alongside the persisted workbench route.
  - The new tab shows route-target counts plus the bounded follow-needed
    authority queue without changing the generic persisted fact-review
    workbench contract for other lanes.
- Workspace coordination boundary:
  - Added `docs/planning/workspace_coordination_boundary_20260327.md` to make
    the repo-boundary decision explicit.
  - Recorded that the workspace should continue operating across the existing
    repos, with `ITIR-suite` as the control plane for cross-repo planning and
    promotion decisions.
  - Recorded that a new top-level project dir is not justified yet; new dirs
    should be created only for genuine runtime/build or transport surfaces,
    not duplicate coordination state.
- Feedback receipt collector UI:
  - Extended `itir-svelte /corpora/processed/personal` with the first
    collector-facing feedback capture surface over the canonical ITIR DB:
    one-receipt add form, JSONL paste/import form, and recent receipt cards.
  - This now sits above the existing `feedback.receipt.v1` receiver and
    `query_fact_review.py feedback-add|feedback-import|feedback-receipts`
    commands.
  - Recent feedback receipts now use provenance-first drill-ins back to
    internal objects/routes when a stable ref already exists.
  - The collector UI now captures canonical thread ids and fact-review
    selector refs explicitly so those drill-ins are available more often.
- Feedback receipt capture ergonomics:
  - Extended `SensibLaw/scripts/query_fact_review.py` with `feedback-add` and
    `feedback-import` so `feedback.receipt.v1` rows can be captured without
    manual sqlite seeding.
  - Updated the contract/TODO/context surfaces so CLI add plus local
    JSONL/JSON import is the first bounded intake path for real user feedback.
- Feedback receipt contract + first persisted receiver:
  - Added `docs/planning/feedback_receipt_contract_20260327.md` to define the
    bounded cross-repo receipt contract for competitor frustrations,
    frustrations with our suite, and delight/retention signals.
  - Added the first persisted `feedback.receipt.v1` receiver in
    `SensibLaw`'s `itir.sqlite` path, with query surfaces for listing and
    inspecting receipts.
  - Updated the root TODO so the next step is capture/import ergonomics rather
    than leaving feedback evidence as chat lore.
- Cross-repo user-story + feedback audit:
  - Added `docs/planning/repo_user_story_state_and_feedback_20260327.md` to
    assess the major suite repos against the current user stories and record
    the strongest likely competitor frustrations, likely frustrations with our
    current surfaces, and likely user-valued strengths.
  - Made the missing evidence explicit: current frustration knowledge is still
    mostly story-derived/proxy rather than based on persisted interview or
    usability receipts.
  - Added a root TODO to establish a bounded feedback-receipt lane so future
    prioritization can use real user evidence instead of chat lore alone.
- Shared shard artifact contract:
  - Added `docs/planning/shared_shard_artifact_contract_v1_20260327.md` to
    freeze the first transport-neutral contract across Zelph, Kant, ZOS, HF,
    and IPFS.
  - Recorded that shard identity must be logical first, selectors must resolve
    to logical shard ids before sink fetch, and JSON/CBOR are projection
    formats rather than competing semantic contracts.
  - Added `tools/build_shared_shard_artifact_contract.py` plus
    `tests/test_build_shared_shard_artifact_contract.py` for the first bounded
    implementation slice:
    lift a Zelph HF manifest into one logical artifact and emit both JSON and
    CBOR projections, with optional IPFS object-ref attachment.
  - Added `tools/build_ipfs_shard_ref_map.py` plus
    `tests/test_build_ipfs_shard_ref_map.py` to derive deterministic raw
    `ipfs://` refs from a local shard tree, including the routing sidecar.
  - Completed the first real dual-sink projection on the 2026 Zelph v3 proof
    artifact:
    `1536` logical shards plus the routing index now project from the same
    logical contract into both HF-backed and IPFS-backed object refs.
  - Mirrored the bounded proof artifacts across both sink families:
    HF dataset shard/query proofs, HF bucket storage for the shared-contract
    companion pack, and IPFS proof roots.
- Zelph upstream handoff:
  - `acrion/zelph#25` merged into `develop`.
  - Stefan's post-merge review identified one real follow-up bug in manifest
    load-all behavior.
  - Rebasing onto current `develop`, isolating the selector-guard fix, and a
    successful local rebuild produced the follow-up branch/PR:
    `acrion/zelph#26`.
- Zelph / Kant / ZOS shard architecture framing:
  - Added `docs/planning/zelph_kant_zos_shard_contract_matrix_20260327.md`
    to make the current shard decision explicit as a four-axis problem:
    sharder, sink, consumer runtime, and shared artifact contract.
  - Recorded that current evidence supports role-fit, not a proof of global
    optimality.
  - Recorded the current best-fit split:
    - Zelph sharder for query-shaped remote reads
    - Kant sharder for publish/pull packaging and content identity
    - HF for practical hosted querying
    - IPFS for immutable publication
- Meta-introspector HF/shard survey:
  - Recorded `kant-zk-pastebin` as the strongest reusable shard-aware HF
    surface, because it already combines shard objects, `manifest.cbor`, IPFS
    addressing, and shard emission.
  - Recorded `monster` as a consumer-side Hugging Face inference precedent
    only, and `huggingface_hub_uploader` / `hugging-push` as generic upload /
    deployment wrappers rather than the shard transport contract.
- Perf-output compression framing:
  - Recorded the `Voxel Promotion and MDL` thread as the current design basis
    for perf output compression.
  - The thread decision is to treat perf as a compression-governed stream with
    typed motif extraction, a streaming MDL compressor, and a binary output
    format, with Fractran kept as a mechanical proof-of-concept target.
- Suite MCP contract + scaffold lane:
  - Added `docs/planning/itir_mcp_dioxus_contract_20260326.md` to define the
    first suite-level MCP boundary, the `itir-mcp/` project direction, the
    SensibLaw-first read-only tool rollout, and the Dioxus backend/native
    integration posture.
  - Updated root planning/context surfaces so the MCP lane is tracked as a
    suite contract rather than an ad hoc sidecar.
  - Added the first `itir-mcp/` scaffold as a suite adapter project instead of
    folding MCP transport directly into existing component internals.
  - Hardened `itir-mcp` with a persistent `--bridge` protocol, structured
    envelopes, and version metadata for client health/version checks.
  - Added Dioxus native-gateway persistence and optional local fallback controls
    before reducing fallback dependency for production flow.
- ITIR / SensibLaw PostgreSQL schema and deployment bundle:
  - Added
    `docs/planning/itir_sensiblaw_postgres_schema_and_deployment_bundle_20260328.md`
    as the execution-oriented refinement of the current production pack.
  - Recorded PostgreSQL as the reference production schema while keeping the
    first runtime target local-first and single-user.
  - Made the reference bundle explicit about:
    extensions/enums, dependency-ordered core tables, trigger helpers,
    operational views, dashboard roles, and staged deployment tiers.
  - Tightened the same note with explicit migration ordering plus the bounded
    interface split:
    `/api/v1` REST surface for case/runtime endpoints and local worker-service
    interfaces for processing, identity, graph, alignment, mode, obligation,
    output, and governance.
  - Synced TODO/context so the next bounded implementation artifact is framed
    as migration-ready SQL in execution order or a local service/API spec over
    the same entity set, not a full collaboration-platform rollout.
- Affidavit local-first proving slice:
  - Added `docs/planning/affidavit_local_first_proving_slice_20260329.md` to
    pin affidavit, not tenancy, as the first SQLite/local-first proving slice
    for narrative integrity and evidence structure.
  - Tightened
    `docs/planning/affidavit_coverage_review_lane_20260325.md` so the current
    lane now explicitly includes a bounded grouped proving-slice read model.
  - Added `build_contested_affidavit_proving_slice(...)` in
    `SensibLaw/src/fact_intake/read_model.py` plus a
    `contested-proving-slice` query surface in
    `SensibLaw/scripts/query_fact_review.py`.
  - Added focused regression coverage in
    `SensibLaw/tests/test_affidavit_coverage_review.py` and
    `SensibLaw/tests/test_query_fact_review_script.py`.
  - Verified the new slice with:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
  - Tightened the proving-slice grouping so explicit response-role and
    support/conflict signals can promote rows into `disputed` or
    `weakly_addressed` without inflating `covered`.
  - On the real Google Docs affidavit/response run, the grouped top-line read
    improved from:
    `supported 1 / missing 28 / needs_clarification 17 / disputed 0`
    to:
    `supported 1 / disputed 7 / weakly_addressed 36 / missing 2`.
  - Added opt-in progress reporting to
    `SensibLaw/scripts/build_affidavit_coverage_review.py` and
    `SensibLaw/scripts/build_google_docs_contested_narrative_review.py`, so
    live contested Google Docs runs now emit fetch/extract/group/match/write
    stages and per-proposition matching progress instead of appearing stalled.
  - Added opt-in trace reporting to the same affidavit builders so operators
    can stream proposition decomposition and classification events such as:
    proposition start, tokenization, top candidate selection, response packet
    inference, final classification, semantic basis, and promotion result.
  - Added regression coverage for the new progress surfaces in
    `SensibLaw/tests/test_affidavit_coverage_review.py` and
    `SensibLaw/tests/test_google_docs_contested_narrative_review.py`.
  - Added
    `docs/planning/affidavit_claim_reconciliation_contract_20260329.md` to
    pin the next quality step as relation-driven claim reconciliation rather
    than more similarity-led bucketing.
  - Tightened
    `docs/planning/affidavit_coverage_review_lane_20260325.md` so the current
    matcher is now explicitly described as a bounded `v0` bridge toward a
    typed relation classifier with dominant-relation bucket resolution.
  - Synced `TODO.md` and context so the next affidavit-lane quality work is
    now framed as:
    normalized proposition/response typing -> bounded relation classifier ->
    dominant relation resolution -> final bucket mapping.
  - Tightened the same affidavit planning notes so `weakly_addressed` is now
    explicitly treated as a transitional defect bucket rather than a stable
    target output class.
  - Recorded the next classifier expectation as:
    split mixed `weakly_addressed` rows into `partial_support`,
    `adjacent_event`, `substitution`, and `non_substantive_response`, while
    requiring per-row explanation fields:
    classification, matched response, reason, and missing dimension.
  - Added an explicit cross-lane priority decision:
    affidavit claim reconciliation is now the higher immediate implementation
    priority, while `TEMP_zos_sl_bridge_impl` stays second priority until its
    retrieval path gains an explicit admissibility / acceptance boundary.
  - Implemented the first affidavit claim-reconciliation followthrough in
    `SensibLaw/src/fact_intake/read_model.py`:
    the proving slice now emits `relation_root`, `relation_leaf`,
    `explanation`, and `missing_dimensions`, and exposes explicit
    `partial_support` / `adjacent_event` / `substitution` /
    `non_substantive_response` sections instead of a stable
    `weakly_addressed` section.
  - Updated focused regression coverage in
    `SensibLaw/tests/test_affidavit_coverage_review.py` and
    `SensibLaw/tests/test_query_fact_review_script.py`.
  - Verified with:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
  - Refined builder-side sibling-leaf arbitration in
    `SensibLaw/scripts/build_affidavit_coverage_review.py` so same-incident
    sibling clauses can survive as alternate context without replacing a direct
    duplicate-root winner.
  - Added a tighter predicate-alignment boundary and explanatory-clause guard:
    explanatory framing like “true fact regarding ... insofar as ...” now stays
    non-substantive instead of being promoted as sibling support.
  - Extended focused affidavit regressions and reverified with:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
  - Added bounded clause-level candidate decomposition inside
    `SensibLaw/scripts/build_affidavit_coverage_review.py` so compound source
    rows can yield clause candidates for action and cause/effect leaves without
    changing persisted affidavit proposition ids.
  - Tightened alternate-context selection so embedded clause fragments do not
    displace better sibling-segment context in the top match summary.
  - Reverified with:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
  - Added a response-side `claim_echo` boundary so duplicate John claim text
    that appears as a heading/reference inside a longer Johl response block is
    treated as quoted claim framing rather than automatic support.
  - Live five-row Johl spot-check after the clause pass:
    - `p2-s5` and `p2-s6` now resolve to direct clause-level support
    - `p2-s38` and `p2-s39` remain support inside the same incident cluster
    - `p2-s21` still promotes, so the remaining gap is quote/reference versus
      Johl-authored assertion disambiguation, not the old cross-swap matcher bug
  - Reverified local gates with:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
  - Tightened revocation-row handling in
    `SensibLaw/scripts/build_affidavit_coverage_review.py`:
    - EPOA rebuttal clauses such as
      `failed to complete the necessary steps to revoke his EPOA`
      now classify as dispute instead of weak support
    - stronger independent confirmation anchors such as
      dated revocation signatures and receipt-of-revocation language now score
      above generic status references
    - duplicate echoed John claim text no longer rescues a disputed response
      row back into support
  - Live targeted Dad/Johl rerun for `p2-s21` now lands as:
    - `disputed / explicit_dispute`
    - matched response:
      `John had failed to complete the necessary steps to revoke his EPOA`
    - duplicate John claim preserved only as lineage:
      `In August 2024 I took steps to revoke my EPOA`
  - Dad Court notebook persisted-thread feedback on the exact updated strings:
    - agreed the quote echo should not rescue support
    - ranked independent Johl-authored confirmation candidates like
      `I had only received the revocation three weeks ago` and
      `This is corroborated by the dated signature on the revocation documents`
      as support-bearing
    - suggested the next refinement is a technical-qualification /
      conceded-fact class for rows like `p2-s21`, rather than a flat dispute
  - Reverified with:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
  - Checked the local formalism repos `../dashi_agda` and `../zkperf` before
    widening the new EPOA-specific heuristics further.
    Result:
    - the current lexical anchor/rebuttal lists should be treated as stopgap
      witness heuristics only
    - the target shape is:
      preserve event root, refine leaf relation, and keep witness/admissibility
      separate from the semantic class
    - recorded that direction in
      `docs/planning/affidavit_claim_reconciliation_contract_20260329.md` and
      `TODO.md`
  - Landed a bounded affidavit matcher optimization pass in
    `SensibLaw/scripts/build_affidavit_coverage_review.py`:
    - source-row segment/clause candidates are now precomputed once per row
    - repeated tokenization, clause splitting, structural parsing, and
      leaf-signature derivation now use local memoization
    - non-contested segment-level matching remains intact
  - Reverified with:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
    -> `53 passed in 2.36s`
  - Timed live targeted Dad/Johl `p2-s21` probe:
    fetch + group + payload build + row scoring completed in about `5.606s`
