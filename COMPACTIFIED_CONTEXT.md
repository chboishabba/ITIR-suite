# Compactified Context

- 2026-03-28 real promoted-record `Phi` prototype:
  - source: current working turn
  - implementation:
    - added runtime:
      `SensibLaw/src/cross_system_phi.py`
    - extended the executable contract:
      `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`
    - kept the minimal schema example aligned:
      `SensibLaw/examples/cross_system_phi_minimal.json`
    - added real promoted-report regression coverage:
      `SensibLaw/tests/test_cross_system_phi_prototype.py`
  - main decision:
    - the repo now has one bounded two-system `Phi` prototype over real
      promoted semantic relations, not only planning prose or a transport stub
    - the provenance guarantee is now explicit in the contract:
      every mapping/diagnostic must resolve through `provenance_index` to
      anchored promoted records in each referenced system
    - mismatch handling is now explicit workflow state, not an implicit note:
      `open|reviewed|waived` via `mismatch_report.workflow`
    - this remains a bounded `v1` slice, not the full richer `Phi vNext`
      witness/type system
  - validation:
    - `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_cross_system_phi_schema.py SensibLaw/tests/test_cross_system_phi_prototype.py`

- 2026-03-28 `Phi` relation + latent graph schema clarification:
  - source: current working turn
  - informed by the same archived thread:
    - title: `Zero Trust Ontology`
    - online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
    - canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
    - source used: `db`
  - main decision:
    - the currently implemented `sl.cross_system_phi.contract.v1` schema
      remains the bounded executable transport contract with statuses
      `exact|partial|incompatible|undefined`
    - the richer formal `Phi` relation is now documented as the next layer:
      mapping kinds, score, witness, constraints, transfer rules, weak
      composition, and graph typing over `L(P)`
    - the repo must not pretend the richer relation kinds are already shipped;
      any future `v2` migration must explain how it relates to the current
      bounded `v1` grammar
    - the latent graph is now explicitly documented as typed nodes, typed
      edges, first-class constraints, and provenance-preserving reconstruction
      over promoted truth
  - documentation artifact added:
    - `docs/planning/phi_mapping_and_latent_graph_schema_20260328.md`

- 2026-03-28 cross-system `Phi` mapping contract slice:
  - source: `Milestone X` execution loop
  - implementation:
    - added the machine-readable schema artifact:
      `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`
    - added the minimal bounded example payload:
      `SensibLaw/examples/cross_system_phi_minimal.json`
    - added focused schema validation coverage:
      `SensibLaw/tests/test_cross_system_phi_schema.py`
  - main decision:
    - `Phi` is now frozen in executable form as a two-system prototype bundle
      rather than only planning prose
    - mapping status is explicitly governed by the enum:
      `exact`, `partial`, `incompatible`, `undefined`
    - `undefined` remains a first-class checked outcome and must not pretend
      to have a target-system analogue
    - mismatch/contradiction reporting stays attached to the mapping contract
      instead of being hidden inside latent-state rhetoric
  - validation:
    - `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_cross_system_phi_schema.py`

- 2026-03-27 global latent legal state cross-system clarification:
  - source: current working turn
  - informed by archived thread:
    - title: `Zero Trust Ontology`
    - online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
    - canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
    - source used: `db`
  - main decision:
    - the safe global reading is not one universal promoted set; it is a
      global latent graph over multiple local promoted sets `P_i` plus a
      mapping layer `Phi` and explicit constraints
    - cross-system motif alignment must allow `exact`, `partial`,
      `incompatible`, and `undefined` outcomes rather than assuming universal
      equivalence
    - any future transfer or alignment lane must preserve local system
      authority and keep all global structure traceable back to some local
      promoted basis
    - the right first prototype, if pursued later, is two bounded systems, one
      small mapping table, and one mismatch report rather than automatic truth
      merging
  - documentation artifact added:
    - `docs/planning/global_latent_legal_state_cross_system_20260327.md`

- 2026-03-27 latent state over promoted truth clarification:
  - source: current working turn
  - informed by archived thread:
    - title: `Zero Trust Ontology`
    - online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
    - canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
    - source used: `db`
  - main decision:
    - if the repo uses `latent state` language, it should mean a compressed,
      provenance-preserving, loss-bounded derived structure over promoted
      truth `P`, not hidden truth over raw text
    - latent structure is downstream of promotion and may support DASHI/MDL
      compression, motif reuse, and conflict analysis, but it does not replace
      the truth gate or silently feed truth back upstream
    - any future `L(P)` lane should require reconstruction, anchor
      preservation, compression discipline, consistency preservation, and a
      strict downstream-only authority rule
    - the right minimal prototype, if pursued later, is:
      promoted facts -> bounded graph -> motif reuse/conflict diagnostics
      without truth mutation from latent structure alone
  - documentation artifact added:
    - `docs/planning/latent_state_over_promoted_truth_20260327.md`

- 2026-03-27 motif candidate / promotion / legal-tree clarification:
  - source: current working turn
  - informed by archived thread:
    - title: `Zero Trust Ontology`
    - online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
    - canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
    - source used: `db`
  - main decision:
    - motif / meme / cohomology language remains explanatory or exploratory
      unless it cashes out into anchors, reversible transforms, candidate
      state, promotion basis, and proofs/receipts where required
    - motifs are not yet repo-wide first-class canonical objects; the safe
      reading is candidate or overlay structure below promotion
    - cohomology currently belongs, at most, in candidate/overlay diagnostics,
      clustering, or invariance analysis, not in the truth layer
    - legal-tree language remains valid as deterministic structured logic over
      source-linked material, but a legal tree is not automatically identical
      to promoted truth in every lane
    - future formalization should require a bounded `MotifCandidate` contract
      and explicit node-family status for any tightened legal-tree schema
  - documentation artifact added:
    - `docs/planning/motif_candidate_promotion_legal_tree_20260327.md`

- 2026-03-27 JMD x SensibLaw truth-construction boundary refresh:
  - resolved via `robust-context-fetch`
  - title: `Zero Trust Ontology`
  - online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
  - canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
  - source used: `db` after direct UUID pull into `~/chat_archive.sqlite`
  - main topics / decisions pulled from the thread:
    - keep `SensibLaw` as the truth-construction layer between messy source
      substrates and downstream reasoning/agent systems
    - the useful abstraction in the thread is not "JMD integration now", but
      that repeated motifs / meme-like reusable structure should cash out into
      source anchors, reversible transforms, candidate state, promotion basis,
      and explicit abstention
    - the near-term JMD lane remains the read-only object graph -> SL corpus
      bridge, not a generic JMD runtime/scheduler or token-layer integration
    - abstention is part of the control surface, not just missing data
    - graph/overlay usefulness should be judged by whether it exposes repeated
      structure, provenance conflict, chronology tension, or promotion
      pressure beyond the base reversible serialization
  - documentation artifact added:
    - `docs/planning/jmd_sensiblaw_truth_construction_boundary_20260327.md`

- 2026-03-27 SL Observation/Claim contract ratification:
  - source: `Milestone R` execution loop
  - planning artifact:
    `docs/planning/sl_observation_claim_contract_20260327.md`
  - followthrough:
    - `Milestone R` is no longer blocked on contract ambiguity for
      `Observation`/`Claim`/evidence links.
    - R.2 contract definition moved from ratified language to concrete
      machine-readable schema at
      `SensibLaw/schemas/sl.observation_claim.contract.v1.schema.yaml`.
    - this note remains implementation-contract-first until runtime surfaces
      are added.

- 2026-03-27 workspace coordination boundary:
  - source: current working turn
  - planning note:
    `docs/planning/workspace_coordination_boundary_20260327.md`
  - main decision:
    - do not create a new top-level coordination project directory now
    - continue working across the existing repos
    - use `ITIR-suite` as the canonical control-plane repo for cross-repo
      planning, TODOs, context, and promotion decisions
    - keep repo-local semantics and implementation notes in the owning repo
      (`dashi_agda`, `FRACDASH`, etc.)
    - only create a new project directory when it has a real runtime/build or
      transport boundary, as with `itir-mcp`, rather than merely duplicating
      planning state
  - next gap:
    - keep this boundary explicit as new cross-repo runtime adapters appear so
      control-plane notes do not drift into repo-local implementation docs

- 2026-03-27 feedback receipt contract + receiver:
  - source: current working turn
  - planning note:
    `docs/planning/feedback_receipt_contract_20260327.md`
  - main decision:
    - proxy/story-derived frustrations are no longer enough as the only
      planning evidence
    - feedback needs a bounded canonical receipt with explicit provenance,
      role, task, class, severity, quote, and desired outcome
  - implementation:
    - first persisted receiver now exists in `SensibLaw`'s `itir.sqlite`
      path via the fact-intake/read-model layer
    - query surface now supports listing and inspecting feedback receipts
    - capture ergonomics now exist through
      `SensibLaw/scripts/query_fact_review.py`:
      `feedback-add` for one receipt and `feedback-import` for local JSONL/JSON
      batches
    - first collector-facing UI now exists at
      `itir-svelte /corpora/processed/personal`:
      one-receipt add form, JSONL paste/import form, and recent receipt cards
    - recent feedback receipts now expose bounded drill-ins back to relevant
      internal surfaces/workbenches when the receipt already names an internal
      route or safely maps to one
    - that drill-in logic is now provenance-first when stronger refs exist:
      canonical thread ids, fact-review selectors, or direct internal route
      refs override weaker route-level guesses
    - the collector UI now exposes explicit fields for:
      - canonical thread id
      - fact-review selector refs (`workflow_kind`, `workflow_run_id`,
        `source_label`)
      so those stronger drill-ins do not depend on ad hoc provenance entry
    - direct user evidence and `story_proxy` receipts can share the same lane,
      but they must remain explicitly distinguished
  - next gap:
    - the remaining gap is a better collector/operator UX than raw field entry
      / JSONL paste, plus broader explicit capture of other canonical object
      families when justified

- 2026-03-27 AU authority-follow UI bridge:
  - source: current working turn
  - main decision:
    - keep the generic persisted fact-review workbench contract unchanged
    - expose AU-specific authority-follow routing through the existing AU
      `demo-bundle` operator surface instead of widening the base workbench
      response for all workflows
  - implementation:
    - `itir-svelte /graphs/fact-review` now loads the AU demo-bundle surface
      in parallel for AU selectors
    - the route now exposes an `Authority follow` operator-view tab showing:
      - route-target counts
      - bounded follow-needed authority queue
      - candidate citations / authority terms / resolution hints
  - next gap:
    - if this view proves useful, decide whether the authority-follow operator
      block should later become part of the canonical persisted workbench
      contract instead of remaining an AU demo-bundle bridge

- 2026-03-27 cross-source follow/review control-plane:
  - source: current working turn
  - planning note:
    `SensibLaw/docs/planning/cross_source_follow_control_plane_20260327.md`
  - main decision:
    - even parity should live at the control-plane layer, not by forcing every
      source family into AU authority semantics
    - the portable ladder is:
      `hint -> receipt -> substrate -> follow-needed conjecture -> operator queue`
    - the first portable queue contract is `follow.control.v1`
  - implementation:
    - `SensibLaw/src/fact_intake/control_plane.py` now defines the shared
      control-plane metadata and queue-item shape
    - first concrete adopters are:
      - AU `operator_views.authority_follow`
      - generic fact-review `operator_views.intake_triage`
      - generic fact-review `operator_views.contested_items`
    - `itir-svelte /graphs/fact-review` now renders control-plane-backed
      queues generically from the shared fields rather than using an
      AU-specific renderer only
  - next gap:
    - move the next real unresolved source families onto the same queue
      grammar, especially transcript/message follow-needed work and affidavit
      source-review queues

- 2026-03-27 cross-repo user-story + feedback audit:
  - source: current working turn
  - planning note:
    `docs/planning/repo_user_story_state_and_feedback_20260327.md`
  - main decision:
    - the suite is currently strongest on provenance, bounded review, and
      explicit uncertainty
    - it is weaker on polished end-user workflow/productization across repos
    - current “user frustration” knowledge is mostly proxy/story-derived rather
      than based on persisted interview/usability receipts
  - repo-level state summary:
    - `SensibLaw` is strongest on review/provenance/doctrine and weakest on
      polished operator UX and end-to-end guided flows
    - `itir-svelte` is the correct UI front, but still more browse/workbench
      than full product workflow
    - `StatiBaker` is strong as a state compiler and weaker as a finished
      operator product
    - `TiRCorder` is real and useful, but still exposes setup/config friction
    - chat/archive/openrecall lanes are strongest as corpus/evidence backends,
      not yet seamless mainstream-facing products
  - followthrough:
    - added a root TODO to create a bounded feedback-receipt lane
    - no code changes were made in this pass

- 2026-03-27 Meta-introspector HF/shard interface survey:
  - source: current working turn
  - repositories inspected:
    - `meta-introspector/huggingface_hub_uploader`
    - `meta-introspector/hugging-face-dataset-validator-rust`
    - `meta-introspector/hugging-push`
    - `meta-introspector/monster`
    - `kant-zk-pastebin`
  - main decision:
    - the strongest reusable shard-aware HF surface is `kant-zk-pastebin`,
      because it already combines `Shard`/`ShardSet`, `manifest.cbor`, IPFS
      content addressing, RDFa/CBOR envelopes, and a concrete shard emitter
    - `monster` is useful as a consumer-side HF client precedent
      (`HF_API_TOKEN`, `api-inference.huggingface.co`), but it is not a shard
      transport or publish/pull contract
    - `huggingface_hub_uploader` and `hugging-push` are generic HF upload /
      deployment wrappers, not the shard/interface contract we need for Zelph
    - if a shared publish/pull branch is revived, it should be aligned against
      the `kant-zk-pastebin` shard manifest shape first, then split by runtime
      target only after the artifact contract is fixed
  - followthrough:
    - recorded in `TODO.md` as the current reusable HF/shard reference surface
    - no implementation changes were made in this pass

- 2026-03-27 Zelph/Kant/ZOS shard matrix:
  - source: current working turn
  - planning note:
    `docs/planning/zelph_kant_zos_shard_contract_matrix_20260327.md`
  - main decision:
    - the unresolved piece is the shared artifact contract, not raw transport
      reachability
    - current evidence supports role-fit, not global optimality
    - best current fit by role:
      - Zelph sharder: query-shaped remote graph reads
      - Kant sharder: publish/pull artifact packaging and content identity
      - HF: practical hosted querying
      - IPFS: immutable content-addressed publication
    - current recommendation is hybrid:
      keep Zelph read/query-focused and ZOS publish/pull-focused under one
      shared contract
  - followthrough:
    - tracked in `TODO.md`
    - recorded in `CHANGELOG.md`
    - no code changes were made in this pass

- 2026-03-27 Zelph upstream handoff state:
  - source: current working turn
  - main decision:
    - the Zelph shard/HF/IPFS lane is now in upstream review/integration mode,
      not active primary implementation mode
    - `acrion/zelph#25` merged into `develop`
    - Stefan's post-merge review found one real follow-up bug in manifest
      load-all behavior
    - that fix is now isolated, rebased onto current `upstream/develop`,
      built locally, and open as `acrion/zelph#26`
  - artifact state:
    - HF dataset: bounded shard/query proof packs
    - HF bucket: `hf://buckets/chbwa/zelph-shared-contract/20260309-shared-contract`
    - IPFS: bounded proof packs mirrored, including the shared-contract pack
  - followthrough:
    - PR comments now contain the maintainer retrieval map and the follow-up
      bug discussion
    - remaining work on this lane depends on Stefan's review of `#26`

- 2026-03-27 shared shard artifact contract:
  - source: current working turn
  - planning note:
    `docs/planning/shared_shard_artifact_contract_v1_20260327.md`
  - main decision:
    - the contract must be logical first and transport-neutral
    - shard identity may not depend on HF paths or IPFS CIDs alone
    - selectors must resolve to logical shard ids before sink-specific fetch
    - JSON and CBOR are projection formats for the same semantic artifact, not
      competing contracts
    - Zelph is the read/query consumer under this contract
    - ZOS is the publish/pull orchestrator under this contract
  - followthrough:
    - implementation now exists at:
      - `tools/build_shared_shard_artifact_contract.py`
      - `tests/test_build_shared_shard_artifact_contract.py`
      - `tools/build_ipfs_shard_ref_map.py`
      - `tests/test_build_ipfs_shard_ref_map.py`
    - current builder behavior:
      - lifts a Zelph HF manifest into the shared logical contract
      - emits JSON and CBOR projections of the same artifact
      - can attach optional IPFS refs via mapping input
      - can now derive deterministic raw `ipfs://` refs for all shard objects
        and the routing sidecar from a local shard tree
    - first real artifact projection completed on the 2026 Zelph v3 proof:
      - `1536` logical shards plus the routing index
      - same logical contract now carries both HF and IPFS object refs
    - focused validation passed:
      - `python -m pytest -q tests/test_build_ipfs_shard_ref_map.py tests/test_build_shared_shard_artifact_contract.py tests/test_build_zelph_hf_manifest.py`
    - tracked in `TODO.md`
    - recorded in `CHANGELOG.md`

- 2026-03-27 Voxel Promotion and MDL framing:
  - source: `db`
  - title: `Voxel Promotion and MDL`
  - online UUID: `69c5de94-294c-83a1-a32b-5c1207e7e375`
  - canonical thread ID: `eb14970bfedb1df596a888683fb509c2c269ef0c`
  - main decision:
    - treat perf as a compression-governed stream: extract typed motifs,
      maintain a streaming MDL compressor, and define a binary output format
      before scaling output volume
    - keep Fractran as a mechanical proof-of-concept target for the small core
      subset, not as a required runtime backend
  - followthrough:
    - resolved from the canonical archive and threaded into suite docs/TODO
    - use this lane as the design basis for any future perf-output bloat
      mitigation work

- 2026-03-25 Mary/AU affidavit-coverage framing:
  - source: current working turn
  - main decision:
    - the next Mary/AU legal-operator lane should be modeled explicitly as
      corpus-to-affidavit coverage accounting, not as a vague promise to
      "extract every single fact" in one promoted pass
    - current AU dense-substrate reality is strong enough to act as the source
      side for that lane:
      - `1747` transcript units
      - `1747` dense substrate facts
      - persisted fact-review overlays and reviewed queue surfaces
    - the missing surface is a first-class comparison lane showing:
      - what affidavit propositions are source-backed
      - what is partial
      - what appears omitted
      - what remains contested or abstained rather than omission-worthy
  - followthrough:
    - added user story:
      `docs/user_stories.md` (`SL-US-31`)
    - added dedicated planning note:
      `docs/planning/affidavit_coverage_review_lane_20260325.md`
    - first bounded implementation now exists at:
      - `SensibLaw/scripts/build_affidavit_coverage_review.py`
      - `SensibLaw/tests/test_affidavit_coverage_review.py`
    - first repo-stable AU-specific checked artifact now exists at:
      - builder:
        `SensibLaw/scripts/build_au_affidavit_coverage_review.py`
      - test:
        `SensibLaw/tests/test_au_affidavit_coverage_review.py`
      - fixture directory:
        `SensibLaw/tests/fixtures/zelph/au_affidavit_coverage_review_v1/`
    - first repo-stable AU dense-substrate coverage artifact now also exists:
      - builder:
        `SensibLaw/scripts/build_au_dense_affidavit_coverage_review.py`
      - test:
        `SensibLaw/tests/test_au_dense_affidavit_coverage_review.py`
      - fixture directory:
        `SensibLaw/tests/fixtures/zelph/au_dense_affidavit_coverage_review_v1/`
    - aligned parity docs:
      `docs/planning/mary_parity_user_story_acceptance_matrix_20260315.md`
      `docs/planning/mary_parity_status_audit_20260315.md`
      `docs/planning/au_completeness_scorecard_20260324.md`
    - tracked implementation lane in:
      `TODO.md`
- 2026-03-25 checked wiki/Wikidata handoff parity decision:
  - source: current working turn
  - inputs reviewed:
    - `docs/planning/wikidata_zelph_single_handoff_20260325.md`
    - `docs/planning/zelph_handoff_index_20260324.md`
    - `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md`
    - `docs/planning/wikidata_p2738_disjointness_lane_20260325.md`
    - `SensibLaw/docs/wikidata_working_group_status.md`
    - current pinned hotspot, disjointness, and qualifier fixtures
  - main decision:
    - the wiki/Wikidata lane is now mature enough for checked-handoff parity
      with GWB/AU
    - this should be implemented as a bounded readability/handoff artifact, not
      as a broad new ingest or live-scan phase
    - the first checked artifact should be built from existing pinned surfaces:
      - promoted hotspot exemplars:
        `mixed_order_live_pack_v1`
        `p279_scc_live_pack_v1`
        `qualifier_drift_p166_live_pack_v1`
      - one held/promotable review pack:
        `software_entity_kind_collapse_pack_v0`
      - real disjointness packs:
        `disjointness_p2738_nucleon_real_pack_v1`
        `disjointness_p2738_fixed_construction_real_pack_v1`
        `disjointness_p2738_working_fluid_real_pack_v1`
      - import-preservation baseline:
        `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`
    - keep the output parallel to the GWB/AU checked handoff shape:
      summary + JSON slice + ZLP facts/rules + engine output + scorecard
    - do not automatically roll this into frozen outward-facing pack `v1.6`
  - followthrough:
    - planning note:
      `docs/planning/wikidata_structural_handoff_v1_20260325.md`
    - TODO tracking:
      `TODO.md`
    - shared index/single-handoff alignment:
      `docs/planning/zelph_handoff_index_20260324.md`
      `docs/planning/wikidata_zelph_single_handoff_20260325.md`
      `docs/planning/zelph_real_world_pack_v1_6_20260325.md`
    - implementation now completed at:
      - builder:
        `SensibLaw/scripts/build_wikidata_structural_handoff.py`
      - test:
        `SensibLaw/tests/test_wikidata_structural_handoff.py`
      - checked artifact:
        `SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/`
      - focused validation:
        `../.venv/bin/pytest -q tests/test_wikidata_structural_handoff.py`
- 2026-03-25 Wikidata hotspot benchmark framing:
  - source: current working turn
  - inputs reviewed:
    - IBM paper `2405.20163v1_rosario.pdf`
    - current Wikidata planning/status docs
    - recent live-item examples around `financial product` / `financial services`
      / `product` and `GNU` / `GNU Project`
  - main decision:
    - the repo's Wikidata lane should now be described explicitly as a
      domain-agnostic structural diagnostic surface, not merely as a
      finance/property semantics exercise
    - competitor hotspot work is useful pressure, but the repo should not copy
      the weakest part of that design: flattening `P31` and `P279` into a clean
      `subConceptOf` graph before preserving why a region is pathological
    - the stronger benchmark direction is a bounded hotspot lane that keeps
      provenance from pinned slice/revision pair -> hotspot family -> generated
      query cluster
    - canonical hotspot families for that lane are:
      - mixed-order
      - entity-kind collapse
      - SCC/circular subclass
      - property/constraint pressure
      - qualifier drift
      - typed parthood ambiguity
  - followthrough:
    - planning note:
      `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md`
    - contract/spec note:
      `docs/planning/wikidata_hotspot_pack_contract_20260325.md`
    - ratified manifest:
      `docs/planning/wikidata_hotspot_pilot_pack_v1.manifest.json`
    - TODO tracking:
      `TODO.md`
    - outward-facing wording update:
      `docs/planning/wikidata_zelph_single_handoff_20260325.md`
    - working-group appendix wording update:
      `SensibLaw/docs/wikidata_working_group_status.md`
  - current pilot-pack candidates:
    - `mixed_order_live_pack_v1`
    - `p279_scc_live_pack_v1`
    - `qualifier_drift_p166_live_pack_v1`
    - `finance_entity_kind_collapse_pack_v0`
    - `software_entity_kind_collapse_pack_v0`
  - implementation followthrough now completed in the same lane:
    - first emitted cluster-pack schema is now explicit in
      `docs/planning/wikidata_hotspot_pack_contract_20260325.md`
    - both earlier entity-kind candidates are now promoted to local
      slice-backed fixtures:
      - `SensibLaw/tests/fixtures/wikidata/finance_entity_kind_collapse_pack_v0/slice.json`
      - `SensibLaw/tests/fixtures/wikidata/software_entity_kind_collapse_pack_v0/slice.json`
    - first implementation surface now exists at:
      - module: `SensibLaw/src/ontology/wikidata_hotspot.py`
      - CLI: `sensiblaw wikidata hotspot-generate-clusters`
    - evaluator surface now also exists at:
      - module: `SensibLaw/src/ontology/wikidata_hotspot_eval.py`
      - CLI: `sensiblaw wikidata hotspot-eval`
    - canned response-bundle fixtures now pin evaluator behavior across
      multiple hotspot families
      - qualifier drift
      - software entity-kind collapse
      - finance entity-kind collapse
    - `v2` runner direction is now explicit:
      keep live execution outside `SensibLaw` by default; if convenience is
      later needed, allow only a thin adapter-command wrapper over the same
      response-bundle contract
    - promotion governance is now explicit in the hotspot lane:
      - `status` means provenance/backing only
      - `promotion_status` means readiness only
      - `hold_reason` is required for non-promoted entries
    - current hotspot pilot-pack classifications now include:
      - `mixed_order_live_pack_v1`: `promoted`
      - `p279_scc_live_pack_v1`: `promoted`
      - `qualifier_drift_p166_live_pack_v1`: `promoted`
      - `finance_entity_kind_collapse_pack_v0`: `promotable`
      - `software_entity_kind_collapse_pack_v0`: `promotable`
    - focused validation passed with the repo venv:
      - `SensibLaw/tests/test_wikidata_hotspot.py`
      - `SensibLaw/tests/test_wikidata_hotspot_eval.py`
      - `SensibLaw/tests/test_wikidata_hotspot_cli.py`
      - targeted existing projection regression checks in
        `SensibLaw/tests/test_wikidata_projection.py`
    - current parity assessment is now explicit:
      - Rosario parity: partial but meaningful on benchmark/scorer shape
      - Ege/Peter parity: improved from purely adjacent because a first bounded
        `P2738` disjointness lane now exists, but still below method parity on
        coverage and culprit sophistication
    - disjointness followthrough now completed in bounded `v1` form:
      - module:
        `SensibLaw/src/ontology/wikidata_disjointness.py`
      - CLI:
        `sensiblaw wikidata disjointness-report`
      - fixture pack:
        `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_pilot_pack_v1/slice.json`
      - tests:
        `SensibLaw/tests/test_wikidata_disjointness.py` and
        `SensibLaw/tests/test_wikidata_disjointness_cli.py`
      - current report surface covers:
        - `P2738`/`P11260` pair extraction
        - local subclass violations
        - local instance violations
        - bounded culprit classes/items
        - deterministic reviewer-facing JSON output
      - one real Wikidata-backed baseline pack now exists beside the synthetic
        pilot:
        `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_nucleon_real_pack_v1/slice.json`
      - one real Wikidata-backed contradiction pack now also exists:
        `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_fixed_construction_real_pack_v1/slice.json`
      - a cleaner real instance-violation contradiction pack now also exists:
        `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_working_fluid_real_pack_v1/slice.json`
      - contract and lane decision are now explicit in:
        `docs/planning/wikidata_disjointness_report_contract_v1_20260325.md`
      - machine-readable governance now exists for disjointness and page-review
        candidates:
        - `docs/planning/wikidata_disjointness_case_index_v1.json`
        - `docs/planning/wikidata_page_review_candidate_index_v1.json`
      - current lane decision:
        keep disjointness as a sibling diagnostic lane for now; do not feed it
        into hotspot-family promotion until more real packs exist
      - promotion ladder policy is now explicit for disjointness too, but only
        at the docs/governance layer; `wikidata_disjointness_report/v1` stays
        observational and does not carry promotion metadata
      - a callable WDQS scan script now exists for the live query/curl work:
        `SensibLaw/scripts/run_wikidata_disjointness_candidate_scan.py`
      - the scan script now has an explicit backend split:
        - `wdqs` for live subclass/instance discovery
        - `zelph` for local instance-only discovery from explicit pair seeds
      - the first repo-owned pair-seed surface now exists at:
        `SensibLaw/data/ontology/wikidata_disjointness_pair_seed_v1.json`
      - the local `zelph` path is now regression-covered end-to-end with both
        in-process and CLI smoke tests in
        `SensibLaw/tests/test_wikidata_disjointness_scan.py`
      - a real live scan against WDQS now succeeded for instance contradictions
        and surfaced `working fluid` as a direct `fluid -> {gas, liquid}`
        contradiction candidate
      - culprit semantics are now tighter:
        culprit classes expose downstream impact counts, and instance rows now
        surface `explained_by_culprit_class_qid` when applicable
      - follow-up local-bin finding:
        `wikidata-20171227-pruned.bin` and
        `wikidata-20260309-all-pruned.bin` both behaved as runtime-only
        negative controls for the current disjointness families
      - on the newer pruned bin, baseline profile, wide profile, bounded
        profile, exact-QID presence checks, and a seedless contradiction scan
        all returned zero useful local signal
      - current practical discovery posture:
        use live/current WDQS-backed Wikidata probing to find candidate
        contradiction families, then pin reviewed slices into repo fixtures
      - local bin retention note:
        both pruned bins are still retained locally for now despite their size
        (`~1.4 GiB` and `~5.6 GiB`) because deletion was deferred
      - paper positioning note:
        the added Shixiong Zhao / Hideaki Takeda paper
        (`2511.04926v2(1)_shixiong.pdf`) is primarily relevant to the broader
        `P31`/`P279` semantic-inconsistency / hotspot-risk lane rather than the
        narrower `P2738` disjointness lane
      - format/splicing note from Zelph source (0.9.5, cloned under `aur/zelph`):
        the `.bin` is a Cap'n Proto `ZelphImpl` with chunked sections for
        `left`/`right` adjacency and `name_of_node` / `node_of_name`; each chunk
        has `chunkIndex` and is written as its own packed message after the main
        header that stores chunk counts; current loader always streams all
        chunks and builds full in-memory maps (no partial load or range reads);
        sharding would need an offset table/selector plus loader changes; see
        `docs/planning/zelph_bin_sharding_note_20260326.md` for the proposed
        sidecar offset index and partial-load sketch
      - the first in-tree Zelph sharding surfaces now exist in the cloned repo:
        `.stat-file <file.bin>` for header-only inspection and
        `.index-file <file.bin> <output.json>` for sidecar byte-offset index
        generation
      - the first selector-based partial materialization path now also exists in
        the cloned Zelph source:
        - `network::Zelph::BinChunkSelection`
        - `load_from_file(filename, selection)`
        - `.load-partial <file.bin> [left=...] [right=...] [nameOfNode=...] [nodeOfName=...] [meta-only]`
      - partial mode now blocks inference, pruning, cleanup, and direct edit
        commands so the initial sharding surface remains read-only
      - current architecture choice:
        prefer sidecar offset index + read-only partial loader first; do not
        change `.bin` format semantics until this path proves useful
      - current safety boundary:
        partial loads are suitable only for under-approximate read-only
        inspection, not inference or destructive graph operations
      - important current limitation:
        the new partial loader still streams the file sequentially and only
        materializes selected chunks; sidecar-driven direct seek / HTTP range
        transport is the next milestone
      - HF storage/query contract is now explicit as `zelph-hf-layout/v1`:
        - primary hosted shape:
          monolithic `.bin` + hosted sidecar index + hosted manifest
        - selector unit:
          section-local chunk index
        - current builder:
          `tools/build_zelph_hf_manifest.py`
        - contract note:
          `docs/planning/zelph_hf_storage_contract_20260326.md`
        - validated locally against the retained 2017 pruned bin sidecar index

- 2026-03-25 single shared Wikidata/Zelph handoff:
  - source: current working turn
  - main decision:
    - the repo now has one short canonical first-link handoff for both the
      Wikidata Ontology Working Group and the Zelph developer at
      `docs/planning/wikidata_zelph_single_handoff_20260325.md`
    - the note explains, in minimal jargon, the exact current results,
      intended direction, explicit non-claims, and the distinct value offered
      to each audience
    - audience-specific notes remain in place, but should now be treated as
      appendices after the shared handoff:
      `SensibLaw/docs/wikidata_working_group_status.md`,
      `docs/planning/zelph_external_handoff_20260320.md`,
      `docs/planning/zelph_real_world_pack_v1_5_20260324.md`
  - followthrough:
    - point root README, the Zelph handoff index, the Wikidata status note,
      and TODO tracking at the shared handoff first
    - keep the shared note current before external meetings so results and
      claims do not drift apart

- 2026-03-24 checked GWB Zelph handoff artifact:
  - source: current working turn
  - main decision:
    - GWB is now materialized as the first checked public-entity Zelph handoff
      artifact after the canonical v1 pack
    - destination for the lane is complete GWB/topic understanding; the checked
      handoff is only one scored checkpoint toward that destination
    - the artifact is deliberately bounded and contains:
      19 promoted relations,
      11 seed/review lanes,
      9 ambiguous events,
      7 unresolved discourse surfaces
    - the checked handoff exists as both prose and machine-readable outputs in
      `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`
    - the checked artifact now also carries a machine-readable completeness
      scorecard at
      `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.scorecard.json`
    - the first bounded Zelph reasoning questions are:
      `executive_public_law_action` and
      `needs_review_due_to_ambiguity`
  - followthrough:
    - keep the current canonical Zelph pack v1 unchanged for now
    - decide next whether GWB should become pack v1.5 or wait for v2

- 2026-03-24 Zelph pack v1.5 and AU parity:
  - source: current working turn
  - main decision:
    - the outward-facing Zelph pack should now be treated as `v1.5`
    - `v1.5` adds the checked GWB handoff artifact and an AU checked handoff
      companion artifact
    - AU is now brought up to parity with GWB at the handoff-shape level:
      prose summary, JSON slice, ZLP facts/rules, engine output, scorecard
    - the next substantive work is no longer "does AU/GWB have a checked
      handoff?" but broader completeness expansion on both lanes
    - important correction:
      the checked AU artifact is a Mary-parity/operator-review checkpoint built
      from the current real workbench bundle, not a full corpus-completeness
      artifact; similarly, the checked GWB artifact is narrower than the wider
      GWB source inventory already present in-repo
  - followthrough:
    - use `docs/planning/zelph_real_world_pack_v1_5_20260324.md` and
      `docs/planning/zelph_real_world_pack_v1_5.manifest.json` as the
      outward-facing pack reference
    - expand GWB scorecard from checked slice to wider real-run metrics across
      source families, including public-bios and book/corpus material under
      `SensibLaw/demo/ingest/gwb/`
    - expand AU scorecard from checked workbench checkpoint to wider
      transcript/corpus metrics rather than reading the current 3-fact slice as
      topic-level completeness

- 2026-03-24 first corpus-level AU/GWB scorecards:
  - source: current working turn
  - main decision:
    - near-term priority is now corpus-level accounting, not only handoff-shape
      parity
    - AU now has a machine-readable corpus scorecard built over the persisted
      real workbench bundles:
      4 included bundles,
      13 facts,
      40 observations,
      2 events,
      11 review queue items,
      with the HCA transcript files kept visible as known raw-source backlog
    - GWB now has a machine-readable corpus scorecard built over broader
      source-family inventory:
      checked handoff,
      public bios pack,
      corpus timeline,
      and local book/demo files
    - this does not prove full destination-level completeness for either lane,
      but it does replace prose-only claims with repo-built corpus checkpoints
  - followthrough:
    - use
      `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`
      and
      `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`
      as the machine-readable completeness companions to the AU/GWB handoff
      artifacts
    - collapse rule for the next work:
      1. GWB broader public-source extraction first
      2. AU reviewed transcript/WhisperX expansion second
      3. safe real chat-history lane third
    - next AU step is fuller source-derived runs, especially reviewed
      transcript/WhisperX imports and other non-bundle raw surfaces
    - next GWB step is relation-coverage expansion over the broader public-bios
      and corpus/book source families, not only inventory counting

- 2026-03-24 first broader GWB extraction checkpoint:
  - source: current working turn
  - main decision:
    - the repo now has a first broader GWB extraction checkpoint over three
      source families:
      checked handoff,
      public bios rich timeline,
      and corpus/book timeline
    - result:
      18 distinct promoted relations after canonical dedupe,
      3 new promoted relations beyond the checked handoff,
      and 5 seed lanes matched across multiple source families
    - public-bios no longer runs as title-only input; it now builds a richer
      cue-filtered timeline from raw HTML pages, correctly flushes malformed
      paragraph boundaries, and preserves explicit statute-signing sentences
    - a follow-on seed-backed semantic pass plus corpus sentence-priority
      shaping now moves both broader-source families into independent promoted
      confirmation on one already-known review-relation family and several
      additional broader relations:
      public bios = 9 relation candidates / 9 promoted relations,
      corpus/books = 32 relation candidates / 32 promoted relations,
      while the deduped broader checkpoint now adds 3 new distinct promoted
      relations beyond the checked handoff:
      `George W. Bush -> signed -> No Child Left Behind Act`
      and
      `George W. Bush -> signed -> Northwestern Hawaiian Islands Marine National Monument`
      and
      `George W. Bush -> ruled_by -> Supreme Court of the United States`
    - a follow-on disambiguation pass now abstains father/family-history
      bare-`Bush` corpus rows instead of resolving them directly to
      `actor:george_w_bush`
    - the next GWB bottleneck is now extending broader-source promotion beyond
      the Supreme Court review, NCLB signing, marine-monument proclamation,
      and new corpus-lane review/nomination confirmations

- 2026-03-25 GWB memoir-rooted corpus confirmation + AU parity companion:
  - source: current working turn
  - main decision:
    - the GWB semantic lane now uses the corpus builder's existing `root_actor`
      memoir hint for a conservative first-person legal-action pass on matched
      broader-source events
    - this does not widen the deduped broader checkpoint beyond `18` / `3`,
      but it does independently confirm one already-checked legal-action
      family from the corpus/book lane:
      `George W. Bush -> vetoed -> Stem Cell Research Enhancement Act`
    - the broader AU lane now has a diagnostics companion under
      `SensibLaw/tests/fixtures/zelph/au_broader_corpus_diagnostics_v1/`,
      which makes the current 4 real bundles, 2 workflow kinds, transcript
      lane pressure, and 4-file raw transcript backlog explicit
    - the outward-facing pack has been advanced to `v1.6`, which now includes
      both checked handoffs and broader corpus companions instead of only the
      narrower `v1.5` checked-slice story

- 2026-03-25 AU real transcript structural checkpoint:
  - source: current working turn
  - main decision:
    - the transcript loader now treats the real HCA hearing files as transcript
      events rather than one or two giant blobs:
      - AustLII/HCA hearing text splits on speaker turns
      - Whisper-style timestamp markdown groups into sentence-ish units
    - new internal AU checkpoint artifact:
      `SensibLaw/tests/fixtures/zelph/au_real_transcript_structural_checkpoint_v1/`
    - current checkpoint reading:
      - 2 real transcript files
      - 1747 transcript units
      - 2224 structural/legal tokens
      - 1348 unique structural atoms
      - 12 selected high-signal excerpts
    - this means the raw HCA hearing lane is no longer only counted as backlog,
      but it is still not yet promoted as reviewed fact/event coverage
    - outward-facing pack remains frozen at `v1.6`; the transcript checkpoint
      is internal until sharing review is complete

- 2026-03-25 AU dense transcript substrate:
  - source: current working turn
  - main decision:
    - the AU hearing lane should be evaluated as a dense transcript-derived
      substrate first, not only as a narrow reviewed handoff
    - new internal AU dense artifact:
      `SensibLaw/tests/fixtures/zelph/au_real_transcript_dense_substrate_v1/`
    - current dense artifact reading:
      - 2 real transcript files
      - 1747 transcript units
      - 1747 facts
      - 1482 observations
      - 0 events
      - 24-item reviewed hearing-event projection
      - 183 review-queue links
      - 0.104751 reviewed-event coverage ratio
      - quality state: high-density, low-trust queue (good provenance, weak
        finalization) pending stricter actor/date/chronology gates
    - the secondary overlay reuses `fact.review.bundle.v1`, but it is treated
      as a smaller reviewed projection over the dense substrate rather than as
      the primary transcript representation
    - the AU structural checkpoint and dense-substrate builders now expose an
      opt-in `--progress` stage stream so longer local runs are visible without
      changing default machine-readable stdout behavior
    - the shared transcript scripts now expose the same opt-in `--progress`
      contract:
      `SensibLaw/scripts/transcript_semantic.py` and
      `SensibLaw/scripts/transcript_fact_review.py`
    - fact-intake persistence now reports nested section progress
      (`sources`, `excerpts`, `statements`, `observations`, `facts`,
      `event_assembly`, semantic refresh stages) with totals, elapsed seconds,
      item rates, estimated finish times, and heuristic ETA intervals, so long
      AU runs no longer stall at an opaque
      `persist_started`
    - shared CLI runtime helper now exists in
      `SensibLaw/scripts/cli_runtime.py`:
      - human-readable stderr progress is the default operator mode
      - terminal `bar` mode now exists for local long-running runs
      - optional `json` progress remains available for wrappers/adapters
      - `--log-level` now propagates through the transcript/AU/GWB long-running
        scripts that were just instrumented, plus the current Wikidata /
        Wikipedia runner entrypoints
    - deeper Wikidata / Wikipedia inner-loop progress is now wired too:
      - `src/ontology/wikidata.py::find_qualifier_drift_candidates(...)`
        emits candidate-query, revision-metadata, and revision-compare updates
      - `src/wiki_timeline/revision_pack_runner.py::run(...)` emits
        per-article, history, candidate-scoring, and pair-report progress
      - renderer behavior is now pinned in
        `SensibLaw/tests/test_cli_runtime.py`
    - the dense AU artifact now also includes a first hearing-procedural
      reviewed projection that lifts party submissions, court interventions,
      and statute-heavy turns out of the flatter dense transcript substrate
    - the same AU dense hearing lane now also carries a first classified
      `hearing_act` layer and a first bounded `procedural_move` assembly layer
      over adjacent compatible hearing acts
    - that AU dense hearing lane now also carries a first conservative
      hearing-event assembly layer above procedural moves
    - that event layer now covers short local bench↔counsel exchanges and
      authority/submission clusters, not only one-move event lifts
    - that event layer now also exposes procedural-move coverage metrics so AU
      progress can be measured as lifted local structure, not only raw event
      count
    - explicit speaker labels now propagate through hearing acts, procedural
      moves, and assembled events, improving local bench/counsel continuity
      without loosening the conservative event contract
    - the current conservative AU event assembly is now effectively governed by
      three local signals together:
      local cue strength, speaker continuity, and bounded topic continuity
    - procedural moves now also preserve transcript order explicitly, because
      event assembly over ranked move order was shown to scramble local
      bench/counsel exchange structure
    - section references and case-style authority cues now normalize into
      topic tokens such as `section_6k`, improving legal-substance continuity
      across adjacent moves/events
    - the dense AU artifact now also carries a smaller reviewed
      hearing-event projection derived from assembled local events plus linked
      fact/review support, so operator-facing review is no longer only a dense
      fact overlay
    - next AU bottleneck:
      improve reviewed event assembly coverage over that denser
      hearing-understanding stack without suppressing transcript density

- 2026-03-24 Dashifine/TextGraphs bridge lesson applied to ITIR graph/text lanes:
  - source: current working turn plus local Dashifine bridge artifacts in
    `../dashifine/`
  - main decision:
    - the useful bridge pattern is not "turn text into a graph because graphs
      are interesting"; it is:
      `canonical state -> conservative serialization -> graph observables ->
      compare against source invariants`
    - the Dashifine result matters because it separates three stages cleanly:
      - faithful export of one canonical object into graph form,
      - invariant-preserving transport of semantic/window summaries,
      - non-local graph constructions that become informative rather than just
        path-shaped
    - for ITIR/JMD/SL-facing work, the practical analogue is:
      - canonical object or article state remains the source of truth
      - lexer/token/corpus graph layers are derived observational surfaces
      - bridge quality should be judged first by reversibility and provenance,
        then by whether graph metrics actually reveal something useful about
        the underlying state
    - the Dashifine sweep result (`ternary_l1_le_2` currently wins by global
      graph-lift score) is a warning as well as a positive result:
      structural richness alone is not enough; the eventual selector should be
      semantic/window-aware, not just density/SCC-boosting
  - useful outcome for ITIR:
    - keep canonical state, lexer output, and graph projection as separate
      layers with explicit ownership
    - treat graph/overlay views as measurement instruments over canonical
      state, not as replacement authority
    - when evaluating future text/graph/lexer bridges, require:
      - one canonical shared state record
      - one reversible serializer
      - one conservative baseline graph
      - one informative non-local graph family
      - one scoring rule that prefers semantic alignment over raw graph lift
  - followthrough:
    - update JMD/SL bridge planning docs with the conservative-bridge and
      informative-graph distinction
    - update `TODO.md` so future lexer/graph work is judged by reversibility
      plus semantic usefulness, not graph richness alone
    - keep one explicit repo-facing doctrine:
      - source anchors are canonical substrate, not promoted truth
      - promotion is the sole path to truth-bearing canonical records
      - `TextGraphs`-style layers are admissible only below canonicality as
        analytical/diagnostic/candidate overlays
      - `TextGraphs` proposes, `SensibLaw` promotes, `Zelph` reasons
      - inside SL, do not collapse the spaCy auxiliary lane into the canonical
        reducer lane; that is evidence vs interpretation
      - the real risk is candidate layers starting to behave like truth
    - canonical architecture note:
      `docs/architecture/admissibility_lattice.md`
    - compact bridge note:
      `docs/planning/textgraphs_sl_bridge_contract_20260324.md`

- 2026-03-24 real-first demo policy and Zelph pack ranking:
  - source: current working turn
  - main decision:
    - synthetic fixtures should only exist when there is no access to real
      material, and even then they should stay minimal and contract-focused
    - benchmark seeds such as `fact_semantic_bench/*_seed.json` are regression
      harnesses, not demo evidence for external or Zelph-facing positioning
    - the current strongest repo-stable real-world demo candidates are the
      persisted `real` fact-review bundles in `itir-svelte/tests/fixtures/`,
      especially:
      `fact_review_wave1_real_au_demo_bundle.json`,
      `fact_review_wave5_real_professional_handoff_demo_bundle.json`,
      `fact_review_wave3_real_fragmented_support_demo_bundle.json`,
      with the real Wikidata qualifier slice as a secondary non-transcript
      import example
    - there is not yet a comparably strong repo-stable real chat-history run
      artifact suitable for the Zelph pack; that is now an explicit gap
    - the Zelph-facing pack should lead with real operator/workbench/run-derived
      artifacts rather than synthetic benchmark seeds or the older wiki/revert
      framing
  - followthrough:
    - update the Zelph handoff note to reflect real-first positioning and the
      current ranked pack candidates
    - add a canonical pack spec + manifest for v1
    - add a concrete GWB public-entity handoff spec as the next recommended
      Zelph-facing artifact after the canonical v1 pack
    - update `TODO.md` so the missing real chat-history demo lane is explicit
- 2026-03-23 JMD status/uncertainty refresh plus Zelph contact-surface clarification:
  - source: current working turn
  - main decision:
    - the near-term JMD lane remains the read-only object graph -> SL corpus
      bridge, now with a local Casey/SL-side proof prototype and a latest-post
      prototype inspection path
    - current bridge progress is real but still bounded:
      runtime object/graph/receipt contracts exist, latest-post ingest exists,
      local MDL-style normalization/proof prototype exists, and latest-post
      prototype summaries can run when browse/raw surfaces cooperate
    - the main operational uncertainty is host instability rather than bridge
      shape:
      `/browse` and `/raw/{id}` are still not stable enough to treat as strong
      declared host guarantees
    - the next resilience step should be local replay surfaces:
      cached latest-index entries and cached resolved bundles, so inspection can
      continue when live browse is unavailable
    - the Zelph-facing repo note should distinguish:
      safe dev contact surfaces inside the repo,
      current demonstrated behavior,
      and unresolved questions about uncertainty/probability handling and pack
      hygiene
  - followthrough:
    - update JMD planning docs with explicit progress, uncertainties, and
      implementation status
    - update the Zelph external handoff note with concrete repo contact
      surfaces and open collaboration questions
    - update `TODO.md` so cache/replay and Zelph handoff hygiene remain visible
- 2026-03-22 Casey x JMD MDL bridge clarification:
  - source: current working turn
  - main decision:
    - no JMD-side PR is required for phase-1 interoperability if SL/ITIR can
      already ingest raw JMD-facing surfaces and emit normalized semantic
      outputs on its own side
    - a JMD-side PR only becomes justified for phase-2 proof-carrying interop:
      embedding SL-normal-form and MDL-proof references into JMD-native shard
      or step objects
    - the intended minimal JMD-side optional extension fields are:
      `sl:normal_form_cid`, `sl:mdl_proof_cid`,
      `sl:canonicalization_version`
    - the clean local bridge point is:
      parse raw surface -> emit semantic atoms -> map into structured graph ->
      run DASHI/MDL-style collapse -> emit canonical graph plus proof object
    - the first prototype should stay entirely on the ITIR/SL side and prove
      the shape of:
      input graph, candidate transforms, transform plan, normalized graph, and
      MDL proof object
  - followthrough:
    - add a planning note for the Casey/JMD MDL contract and proof object
    - add a small local prototype rather than opening a speculative upstream PR
    - keep any future upstream PR intentionally tiny and optional
- 2026-03-22 DASHI x JMD/SL bridge role clarification:
  - source: current working turn
  - main decision:
    - for the JMD canonical object graph -> SL corpus graph bridge, `ERDFA` /
      `DASL` remains the representation, addressing, and execution substrate
    - `DASHI` is the missing selection/compression/invariance layer over that
      substrate, not a competing shard format or transport
    - the practical SL bridge composition is:
      ERDFA/DASL object or trace graph -> DASHI-style quotient / MDL collapse
      -> SL reversible anchors and advisory overlays
    - provenance bundles should therefore be read as structured hypothesis
      spaces: binaries/source/debug symbols/traces/models/events are inputs to
      canonicalisation, not just opaque attachments
    - the bridge proof target is not merely "can SL read the shard", but "can
      SL attest that the chosen representation is a minimal canonical
      explanation over declared evidence"
  - immediate followthrough:
    - update the JMD bridge contract and triage roadmap so the DASHI layer is
      explicit
    - update `TODO.md` so future bridge work keeps MDL collapse, symmetry
      quotienting, and proof fields aligned with the read-only bridge lane
    - keep runtime code conservative until the doc/TODO framing is stable
- 2026-03-22 Wikipedia random-page ingest realignment:
  - source: current working turn
  - main decision:
    - treat random Wikipedia pages as an article-ingest coverage lane first,
      not as a revision/reversion lane and not only as date-anchored timeline
      readiness
    - primary goal is to identify the people/entities named in arbitrary
      article text and what they did, with bounded when/where/why/context when
      deterministic local extraction supports it
    - timeline quality remains important, but as a derived surface over the
      broader article-ingest pass
    - start bounded link expansion at one hop only
    - keep live acquisition separate from offline scoring
    - shared reducer output remains useful companion diagnostics, but the main
      success condition is broader article ingest over arbitrary non-legal
      pages rather than abstention
  - followthrough:
    - add a parent random-page article-ingest contract in `SensibLaw/docs/`
    - retarget `Antigravity-Aether` away from reversion/sentinel wording and
      toward article-ingest coverage plus timeline-enabling unit tests
    - add a new article-ingest report path and one-hop sample-manifest support
- 2026-03-22 Wikipedia canonical-state split:
  - source: current working turn
  - main decision:
    - use one deterministic canonical wiki-state compiler as the shared middle
      for Wikipedia ingest
    - reuse the existing fact-intake observation/event vocabulary instead of
      inventing a Wikipedia-only ontology
    - keep `timeline` as the user-facing name even when ordered events are
      undated, but require explicit anchor status (`explicit`, `weak`, `none`)
    - make revision review a state-first diff over canonical wiki state, with
      graph/timeline/editorial summaries derived secondarily
  - followthrough:
    - add a canonical wiki-state helper under `SensibLaw/src/wiki_timeline/`
    - refactor article-ingest scoring onto that helper
    - refactor revision diffs to compare canonical state before projection
      summaries
- 2026-03-23 Wikipedia ingest honesty pass:
  - source: current working turn
  - main decision:
    - keep the existing article-ingest coverage score for comparability, but do
      not let it stand alone as the quality signal
    - add a second honesty-oriented score family that penalizes observation
      explosion, malformed/noisy extracted text, and weak actor/object binding
    - keep timeline honesty separate from article-ingest honesty; mostly
      undated pages are not automatically ingest failures
    - treat density metrics as first-class review evidence rather than just
      hidden implementation detail
  - followthrough:
    - bump the report schema and emit `honesty_scores`,
      `timeline_honesty`, and `density_metrics`
    - use the stored random-page manifest as the first calibration pass for the
      new honesty surface
    - defer page-family stratification and link-relevance scoring until after
      the scorer-only honesty pass is stable
- 2026-03-23 Wikipedia ingest calibration pass:
  - source: current working turn
  - main decision:
    - keep the earlier coverage and honesty tracks intact, but add a separate
      scorer-only calibration layer for abstention quality, sentence-link
      relevance, and claim/attribution grounding
    - stratify report summaries by heuristic page family so biography/place/
      project/species pages stop hiding each other's failure modes
    - keep this pass report-only; do not mutate the canonical extractor again
      yet
  - followthrough:
    - bump the report schema again and emit calibration scores plus page-family
      profile data
    - rerun the stored random-page manifest and use the family split to decide
      whether weak object binding is a real extractor defect or a page-shape
      calibration problem
- 2026-03-23 Wikipedia ingest regime basis:
  - source: current working turn
  - main decision:
    - add a low-dimensional regime vector to the canonical wiki article state
      so the ingest report can distinguish narrative, descriptive, and formal
      pages without adding more page-family categories
    - keep page-family labels as derived/debug output, but make regime-aware
      scoring the primary comparison surface for the article-ingest report
  - followthrough:
    - store the regime vector on canonical article state
    - emit regime-aware honesty/calibration score paths alongside the legacy
      compatibility outputs
    - rerun the stored random-page manifest and compare the regime averages
      against the existing family stratification
    - add dominant-regime counts and follow-yield summaries so the next stage
      can test regime generalization and graph usefulness on a larger random
      slice
    - extend follow-yield with the explicit richness / non-list / regime /
      information-gain blend, plus hop decay and best-path probing
    - keep page-family labels as derived debug output only
- 2026-03-24 Wikipedia follow-quality first live campaign:
  - source: current working turn
  - artifacts:
    - manifest: `/tmp/wiki_random_manifest_large.json`
    - report: `/tmp/wiki_random_article_ingest_report_large.json`
  - main findings:
    - root-link relevance remained near-saturated (`0.982143`)
    - followed-link relevance dropped to `0.5625`
    - follow-target quality averaged `0.446047`
    - hop-2 quality did not collapse relative to hop-1 on the first 8-page
      slice (`0.471626` vs `0.446047`)
    - best-path stayed above average candidate path quality by `0.055025`
  - failure clustering:
    - worst follow targets were dominated by pages with `non_list_score = 0.0`
    - the immediate empirical bottleneck is list/year/generic aggregation
      follows, not shallow path-decay collapse
  - followthrough:
    - add repeat-run campaign tooling with archived outputs
    - add explicit weak-follow failure buckets
    - tighten non-list discrimination using title/warning-level cues before
      adjusting richer path metrics
  - implementation follow-up:
    - `scripts/run_follow_quality_campaign.sh` now supports archived multi-run
      output directories and aggregate post-run analysis
    - `SensibLaw/scripts/analyze_follow_quality_reports.py` aggregates report
      directories and clusters weak follows by bucket
    - `non_list_score` now looks at title-level and warning-level aggregation
      cues, not just raw-text markers
  - follow-up bug fix:
    - raw wikitext `[[Category:...]]` residue was causing false
      `list_like_follow` hits on ordinary pages like `Alaska`
    - `non_list_score` now strips category/defaultsort markup before
      evaluating text markers
  - corrected aggregate after the category-markup fix:
    - 3 runs / 24 root pages still showed the same high-level shape
    - root-link relevance remained high while followed-link relevance and
      follow-target quality stayed materially lower
    - hop decay remained near zero, so the graph still is not collapsing at
      two hops
    - `list_like_follow` remained the largest weak-follow bucket, with
      `low_information_gain_follow` second
  - slice-1 continuation-specificity implementation:
    - kept the existing 4-part follow-target-quality blend and weak-follow
      thresholds unchanged
    - expanded `non_list_score` / `list_like_follow` with bounded title
      heuristics, lexical parent-child specificity checks, and same-
      neighborhood/no-lift detection
    - added explicit specificity reasons to follow details and summary output
    - next step is the comparable 3x8 rerun before touching
      `low_information_gain_follow`
  - post-slice-1 live rerun reading:
    - the new specificity reasons are firing on the intended page shapes
    - the rerun is still not a clean before/after because the random sample
      changed
    - next work should add fixed-manifest rescoring / report comparison, then
      tighten the existing information-gain component for related-but-generic
      continuations
  - fixed-manifest + slice-2 implementation:
    - added a fixed-manifest report comparison path so before/after scorer
      changes can be compared on the same manifests
    - kept the current follow-target-quality score shape unchanged
    - tightened the existing information-gain component for related-but-generic
      continuations using bounded penalties over umbrella/year/generalization
      and low-novelty signals
    - fixed-manifest comparison then showed:
      - `list_like_follow` unchanged on the same manifests
      - `low_information_gain_follow` only slightly higher
      - average `follow_target_quality_score` lower (`0.525836 -> 0.507564`)
      - `best_path_vs_avg_gap` slightly higher (`0.047057 -> 0.050072`)
      - `hop_quality_decay` effectively flat (`-0.021348 -> -0.019689`)
    - conclusion:
      - keep the fixed-manifest comparison path
      - keep the information-gain reason instrumentation
      - narrow the score penalties so title-shape cues alone do not act as a
        scoring downgrade
      - require co-occurring low-novelty / no-lift evidence before the main
        year/umbrella/generalization information-gain penalties apply
    - narrower `v0_9` rescoring then showed:
      - weak-follow bucket counts unchanged on the same manifests
      - average follow-target quality nearly flat rather than materially lower
      - hop decay and best-path gap effectively stable
      - information-gain reasons still surfaced even when they no longer
        triggered score penalties
    - next scorer step:
      - stop tightening title cues
      - add a content-based continuation-lift signal inside the existing
        information-gain component so relation-bearing structural lift can help
        distinguish useful continuations from generic title matches
- 2026-03-23 unresolved ChatGPT context fetch:
  - source: current working turn
  - referenced online UUID:
    `69c0b4d1-d714-839b-b21c-ce162292db4f`
  - source used: prior local context plus failed later refresh attempt
  - fetch status:
    - `chat_context_resolver.py` returned only DB FTS candidates and explicitly
      did not use the web
    - direct `pull_to_structurer.py` fetch failed because `re_gpt` could not
      obtain an auth token from the stored ChatGPT session
    - `python -m re_gpt.cli --view ...` fell back to requesting a fresh
      `__Secure-next-auth.session-token`, but that fallback should not be read
      as proof the token was stale
  - current best reading:
    - the later refresh path failed, but that does not prove the original pull
      never succeeded
    - the likely fault is in the live fetch request/auth flow, not a safe
      assumption of token staleness
- 2026-03-23 ChatGPT auth-bootstrap debug:
  - source: current working turn
  - referenced online UUID:
    `69c0bd1d-389c-8399-a23e-10efab70a1a9`
  - DB lookup status:
    - `chat_context_resolver.py` returned only `db_fts_candidates`; no exact
      local resolution and web was not used
  - live pull status:
    - direct `pull_to_structurer.py --engine async` reproduced a concrete auth
      bootstrap failure before any conversation fetch began
    - `/api/auth/session` returned JSON with only `WARNING_BANNER` and no
      `accessToken`
  - main decision:
    - treat this as a `re_gpt` auth-bootstrap defect until disproven
    - likely cause: calling `/api/auth/session` with only the
      `__Secure-next-auth.session-token` cookie instead of a hydrated frontend
      cookie jar
  - intended followthrough:
    - patch `re_gpt` so sync/async auth bootstrap can hydrate frontend cookies
      from `https://chatgpt.com/` and retry `api/auth/session` on the
      warning-banner-only response
    - recover the thread after the fix and fold any graph-quality /
      `PositiveBorelMeasure` guidance into the durable docs
  - implementation/result:
    - patched `re_gpt` sync/async auth bootstrap to preserve non-empty session
      cookies, hydrate frontend cookies, and fall back to parsing
      `client-bootstrap` access tokens where available
    - added focused regression coverage in
      `reverse-engineered-chatgpt/tests/test_list_all_conversations.py`
    - live recovery is still blocked in this environment because both `/` and
      `/c/<uuid>` frontend pages currently render `client-bootstrap` with
      `authStatus: logged_out`, so there is still no recoverable access token
- 2026-03-24 resolver UUID/path fix:
  - source: current working turn
  - referenced online UUID:
    `69c1ed37-0ea8-839b-9854-6d0401376233`
  - source used:
    - resolver local DB miss plus failed live fetch
  - main decision:
    - `chat_context_resolver.py` must extract only the `/c/<uuid>` segment from
      ChatGPT URLs
    - canonical-thread-id matching should only run when the selector is
      explicitly a canonical SHA1-style id, not as a general fallback
    - web fallback should prefer the ITIR-suite venv `re_gpt.cli` path over the
      unrelated `pipx` `re-gpt` binary so resolver behavior matches the local
      reverse-engineered-chatgpt environment
  - current status:
    - resolver code now normalizes ChatGPT URLs to the online UUID and no
      longer produces DB FTS false positives for UUID lookups
    - the remaining live fetch failure is no longer explained by the `pipx`
      environment mismatch; if it persists, it is a real `re_gpt` auth/frontdoor
      issue rather than the resolver using the wrong Python environment
- 2026-03-24 Cloudflare/browser-path posture:
  - source: current working turn
  - main decision:
    - do not position the Playwright/Firefox challenge solver as the current
      fix path for live chat recovery
    - current priority remains getting direct web pulls and auth bootstrap
      working again without relying on the browser-challenge branch
  - implication:
    - Cloudflare-triggered browser fallback should be documented as an
      experimental escape hatch only, not as the primary operating procedure
      or thread payload from the current session-token-only path
- 2026-03-23 chunked session-token file:
  - source: current working turn
  - local artifact:
    `~/.chatgpt_session_new`
  - observed shape:
    - two non-empty raw lines, corresponding to token chunks rather than a
      single `token=` record
  - decision:
    - `re_gpt` should treat a chunked session-token file as a supported input
      path and concatenate the chunks before auth bootstrap
  - followthrough:
    - extend `get_session_token()` to read chunked token files before the
      fallback prompt path
      as proof that the token was actually stale
  - consequence:
    - do not treat the later refresh failure as evidence that the original pull
      never worked
    - the safer reading is: prior thread context may already have been ingested
      or reflected locally, but this pass could not re-verify it live because
      the refresh path failed
    - current leading suspicion is a bug in the live fetch/request flow
      itself, potentially a malformed POST or related auth-request regression,
      and that should be debugged explicitly rather than blamed on token age
    - repo-facing changes in this pass should still be justified by local repo
      state, tests, and stored-manifest evidence unless the thread is
      re-verified explicitly
- 2026-03-21 agent test-loop audit:
  - source: current working turn
  - scope:
    - reconcile `docs/planning/agent_test_loop.md` check-ins against actual
      working-tree artifacts and rerun the smallest matching slices
  - verified completed loops on rerun:
    - `Codex-Aster`: `itir-svelte` graph UI gate rerun passed
      (`npm test -- --test-name-pattern graph_ui_regressions`,
      `npm run check`, `npm run build`)
    - `Antigravity-Zelph`: `SensibLaw/tests/test_sl_zelph_demo_tools.py`
      passed (13)
    - `Antigravity-Warp`: `SensibLaw/tests/test_query_fact_review_script.py`
      passed (8) and `StatiBaker/tests/test_observed_signals_contract.py`
      passed (17)
    - `Antigravity-Apex`: `SensibLaw/tests/test_migration_integrity.py`
      passed (2) and `StatiBaker/tests/test_apex_schema_validation.py`
      passed (2)
    - `Antigravity-Sentinel`: ASR/WhisperX importer slice passed (6) and
      `SensibLaw/tests/test_fact_intake_read_model.py` passed (15)
    - `Antigravity-Orion`: `SensibLaw` Zelph tool slice passed (13) and
      `itir-svelte/tests/zelph_integration.test.js` passed (1)
    - `Antigravity-Titan`: benchmark matrix reran successfully at `--max-tier 100`
      across four corpora, but the earlier exact pass-count wording was not
      supported by retained artifacts
  - followthrough:
    - keep only completed loops in `agent_test_loop.md`
    - move initialization-only lanes to TODO follow-up until they have exact
      commands and terminal outcomes
    - fix trivial rerun blockers when local and mechanical; during this pass that
      included restoring the missing `path` import in
      `itir-svelte/src/lib/server/factReview.ts` and correcting a faulty source-type
      setup in `SensibLaw/tests/test_zelph_wiki_extended_coverage.py`
- 2026-03-19 web-surface transition clarification:
  - source: current working turn
  - main decision:
    - `itir-svelte/` is the sole intended web interface for ITIR-suite going
      forward
    - `tircorder-JOBBIE/Pelican/` and `tircorder-JOBBIE/Zola/` remain in-tree
      only as legacy/reference material during transition
    - do not treat Pelican or Zola as active runtime web targets for new work
    - new UI behavior, parity, and route ownership should land in
      `itir-svelte/`
  - followthrough:
    - update TiRC docs so Pelican/Zola are described as reference-only
    - keep only bounded regression/reference coverage on legacy helpers needed
      to understand or port behavior into Svelte
    - eventually delete legacy web generators once needed behavior is absorbed
      into `itir-svelte/`
- 2026-03-19 transcript-browser parity pass:
  - source: current working turn
  - scope:
    - compare retained `tircorder-JOBBIE/Pelican/` transcript-browser behavior
      against current `itir-svelte/` viewer surfaces
  - parity finding:
    - `itir-svelte` already covers the core reusable viewer substrate:
      transcript cue parsing, seekable audio, cue highlighting, cue scrolling,
      search/filtering, and document-side inspection via
      `/viewers/hca-case`
    - the clearest remaining parity gap in the current viewer primitive was the
      lack of a live accessibility status echo for the active cue
  - implementation decision:
    - close the `aria-live` cue-status gap in `TranscriptViewer.svelte`
    - document other legacy-only behaviors as deferred migration items instead
      of extending Pelican/Zola
- 2026-03-19 archived thread resolution pass:
  - resolved nine online UUIDs using `robust-context-fetch`
  - canonical source path: `~/chat_archive.sqlite`
  - write persistence for the newly supplied IDs was blocked during this pass by
    `sqlite3.OperationalError: database is locked`, so exact archive matches are
    marked `db` and the remaining titles/topics were captured via live read-only
    web fetches
  - summary:
    - `69b90f8b-3cf8-839c-bffe-b7da95565338`
      - title: `Zelph 0.9.5 Update`
      - canonical thread ID:
        `e45a889fa7d88547021c2a95ded89270b40fd6db`
      - source used: `db`
      - main topic: the full conversation moved from assessing Zelph as early
        stage-but-promising, to checking whether it overlaps with SL/ITIR, to
        defining a minimal negligence rule set and "irreducible disagreement,"
        and finally to a tiny deterministic SL -> Zelph bridge demo
      - demo takeaway: keep it tiny, deterministic, and legally meaningful
        enough to show a clean fact-graph handoff rather than a full
        integration
    - `69b9f131-bb3c-839c-b2cd-233b4af8c72a`
      - title: `Branch · Zelph 0.9.5 Update`
      - canonical thread ID:
        `e3d8bffb77f7df0337efe3684653c6bf441ca061`
      - source used: `db`
      - main topic: refine the Stefan-facing update so it sounds more precise,
        technically grounded, and clearly upstream rather than dependent on
        Zelph; Mary was explicitly treated as a competitor / external
        benchmark, not as evidence of the user’s own architecture
    - `69b75a97-6784-839b-bc2b-3824717279e0`
      - title: `ITIR SensibLaw Model`
      - canonical thread ID:
        `044540f8d6f0a880d507c1ce81341613b56d13b9`
      - source used: `db`
      - main topic: formalize ITIR/SL in a clean model, while treating uploaded
        content as partial snippets and forcing file-search / full-document
        lookup before answering from truncated excerpts
    - `69b7e167-53d8-839d-a9e6-56b239746525`
      - title: `Governance Model Mapping`
      - canonical thread ID:
        `49554563c68c31b87b5f28ff673355c0ff8b2a1b`
      - source used: `db`
      - main topic: map the printed O/R/C/S/L/P/G/F model onto the ITIR /
        SensibLaw governance machine and make the operator explicit for
        convergence, proofs, and ZK attestation reasoning
    - `69b7e164-d0a8-839d-8418-41769163ba6d`
      - title: `Formal Model Application`
      - canonical thread ID:
        `c1279d811ec67be9ebae1cab6c1ee865ca24299b`
      - source used: `db`
      - main topic: apply a state-compiler / prototype model to the problem
        using uploaded files, with the archive noting that the files were fully
        loaded and should be searched directly when needed
    - `69ba8956-35b8-839b-9707-f8c91c2b02dd`
      - title: `Ambiguity of "Community"`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: `"community"` in legal text is often a normative
        placeholder rather than a concrete entity, so SL should not expect
        Wikidata/entity linking to resolve it automatically
      - design takeaway: keep this lane text-grounded and support unresolved
        normative-reference handling instead of forcing entity resolution
    - `69bab27a-cb28-8398-b3ea-940d4fb47772`
      - title: `Branch · Ambiguity of "Community"`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: branch follow-up reinforcing the same ambiguity boundary
        and the need to preserve underdetermined legal placeholders
    - `69ba8c55-163c-839d-86b9-6c366a8dc29a`
      - title: `Formal Model to Engine`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: map the O/R/C/S/L/P/G/F-style formal model directly onto
        the ingest / lexer / compression engine so organization, demand, code,
        state, lattice, proposal, and gap remain explicit in that pipeline
    - `69b7eb5b-0c78-839d-9012-a484905fdf0c`
      - title: `Model Mapping to Casey`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: map the same formal model onto Casey with
        `TreeState + WorkspaceView` as state, the per-path candidate set as the
        lattice, collapse as explicit governance, and divergence as a first
        class measurable gap
    - `69b89b50-5554-839d-b9cf-f50f6eab3b8b`
      - title: `Debugging UX in Games`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: stream/debugging isolation discussion; recorded for
        completeness but not treated as a current repo-facing planning input
    - `69ba3af2-5df8-839b-bd8a-7c865be0b052`
      - title: `Casey Git Clone Differences`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: concise Casey differentiators: superposition instead of
        snapshots, conflicts as valid state, explicit collapse, workspace as
        selection over candidates, and immutable build projections
- 2026-03-19 ITIR surface-boundary followthrough:
  - source: current working turn
  - main decision:
    - `SL` owns representation/compression
    - `casey-git-clone` owns mutable possibility state and operational
      collapse/build authority
    - `fuzzymodo` owns read-only reasoning over exported Casey state
    - `StatiBaker` owns observer-only governance memory and alignment judgment
  - documentation artifacts added:
    - `docs/planning/casey_fuzzymodo_interface_contract_20260319.md`
    - `docs/planning/casey_statiBaker_receipt_schema_20260319.md`
  - immediate implementation priority at the time:
    - implement Casey -> fuzzymodo as the next boundary
    - then implement the sharpened Casey -> StatiBaker receipt seam
- 2026-03-19 Casey -> fuzzymodo advisory refinement:
  - source: current working turn
  - main decision:
    - keep the Casey/fuzzymodo seam path-local and advisory-only
    - extend `casey.facts.v1` with optional namespaced candidate feature bags
      carrying Casey-known metadata today and future SL/LCE signals later
    - upgrade `fuzzymodo.casey.advisory.v1` from candidate-count-only gaps to
      explanation-first divergence summaries with:
      - `primary_axis`
      - structured `gap_items`
      - `suggested_actions`
  - implementation status:
    - Casey export adapter now emits optional feature bags
    - fuzzymodo Casey adapter now consumes those features when present
    - targeted Casey/fuzzymodo CLI/export tests pass for the refined seam
  - remaining followthrough:
    - feed real SL/LCE-derived signals into the optional feature bag
    - add stronger cross-component conformance checks over the advisory payload
- 2026-03-20 Casey benchmark interpretation refinement:
  - source: current working turn
  - main decision:
    - Casey library is the closest current proxy to
      "Casey competing with git if git were in Python"
    - Casey CLI is not there yet; it is still materially limited by Python
      process startup and remaining command-path overhead even after
      `--no-observer`, lazy imports, and command-scoped runtime batching
  - followthrough:
    - keep benchmark claims split between Casey library vs subprocess git and
      Casey CLI vs git CLI
    - add a clearer interpretation lane / reporting cut in the benchmark docs
- 2026-03-19 JMD/ERDFA intended-surface awareness:
  - resolved via `robust-context-fetch`
  - title: `Dependency-aware task scheduling`
  - online UUID: `69bb8ef6-e9d0-839c-a917-ae92116a02cd`
  - canonical thread ID: `2a13394ff8c932629d42aed76bb07f049eede036`
  - source used: `db` after pulling the online UUID into `~/chat_archive.sqlite`
  - main topic / decision:
    - treat JMD/ERDFA shard-graph scheduling as a future external surface only
    - draft mapping is JMD shard graph -> Casey runtime state -> fuzzymodo
      scoring -> StatiBaker receipts
    - do not promote it to an active Casey/fuzzymodo/SB contract yet
  - documentation artifact added:
    - `docs/planning/jmd_itir_intended_surface_20260319.md`
- 2026-03-19 JMD object graph -> SL corpus graph bridge framing:
  - source: current working turn
  - main decision:
    - the first serious bridge is not Casey <-> JMD execution
    - the bridge boundary is JMD canonical objects -> SL read-only corpus
      organisation -> advisory overlays / optimisation hints back to JMD
    - JMD remains authoritative for canonical stored objects, publication, and
      execution/orchestration
    - SL remains authoritative for tokenisation under a named profile, span
      anchors, lexical groups, and organisation overlays
    - Casey is the governed proposal surface for competing reorganisations or
      optimisation proposals
    - StatiBaker stores refs/digests/receipts only
  - documentation artifact added:
    - `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md`
  - immediate followthrough:
    - start with read-only JMD -> SL ingest payloads and reversible anchor
      generation
    - defer direct executor/adapter work until object/anchor/overlay invariants
      are clearer
- 2026-03-19 archived thread resolution:
  - resolved via `robust-context-fetch`
  - title: `Full Stack Architecture`
  - online UUID: `69bb70ca-19ac-83a0-a087-8d2416e8be07`
  - canonical thread ID: `fe1aead0a943806609b767cf3c27e2eeef2e54f1`
  - source used: `db` after direct UUID pull into `~/chat_archive.sqlite`
  - archived refresh after later pull:
    - latest archived assistant timestamp: `2026-03-19T13:27:48+00:00`
    - archived message count after refresh: `137`
  - main topics / decisions pulled from the thread:
    - Rabbit is the process/queue I/O fabric rather than just a loose
      orchestration helper
    - pastebin/IPFS acts like the persistent shared memory/state layer
    - ERDFA is better treated as canonical structural/shard substrate than as
      an embedding layer
    - Rust appears as a programmable transformation/execution layer via custom
      driver/plugin tooling
    - this sharpens the bridge posture: shared identity substrate first,
      separate planning/governance/execution control planes second
    - later turns sharpen the scoring/provenance side:
      - post-entropy should measure corpus-relative compression efficiency plus
        divergence/novelty relative to corpus, not just local compression gain
      - typed shards need declared corpus/pipeline/metric commitments rather
        than vague "necessary cycles" rhetoric
      - a replayable provenance bundle should keep binaries, source, debug
        symbols, traces, models, and prior events linked together
- 2026-03-20 JMD docs triage / roadmap pass:
  - source: current working turn
  - main decision:
    - split "JMD integration" into three lanes:
      future shard/task surface, near-term object-to-corpus bridge, and
      reserved proof/provenance design constraints
    - keep the JMD/ERDFA scheduler surface explicitly deferred
    - treat the JMD object graph -> SL corpus graph bridge as the only
      near-term JMD implementation candidate
    - require fixture-backed ingest + anchor/overlay examples before any bridge
      code starts
  - documentation artifact added:
    - `docs/planning/jmd_triage_roadmap_20260320.md`
- 2026-03-20 JMD fixture v1 closeout:
  - source: current working turn
  - main decision:
    - first canonical bridge example is one ERDFA-backed text shard
    - dual refs are mandatory in the canonical example:
      pastebin raw retrieval + IPFS CID integrity
    - `byte_start` / `byte_end` are the normative reversible anchor trace;
      token offsets are secondary metadata only
    - `zos-server` stays outside the normative v1 payload and remains a future
      infrastructure concern
    - provenance bundle and proof/metric commitment fields remain reserved but
      optional in v1
  - documentation artifacts added:
    - `docs/planning/jmd_fixture_v1_20260320.md`
    - `docs/planning/jmd_fixtures/jmd_sl_ingest_v1.example.json`
    - `docs/planning/jmd_fixtures/sl_jmd_overlay_v1.example.json`
- 2026-03-20 Zelph external handoff note:
  - source: current working turn plus the 2026-03-18 to 2026-03-20 Stefan
    exchange supplied in chat
  - main decision:
    - write one upstream-facing repo note explaining the SL -> Zelph bridge in
      external-collaboration language
    - keep the positioning explicit:
      SensibLaw upstream ingest/review/provenance, Zelph downstream reasoning
    - point external readers to repo-backed demo evidence rather than broad
      architecture claims
    - treat benchmark/result JSONs as review-required before external sharing
      because they may contain personal or case-linked material
  - documentation artifact added:
    - `docs/planning/zelph_external_handoff_20260320.md`
- 2026-03-20 ZK legal context refresh:
  - resolved archived thread via `robust-context-fetch`
  - title: `ZK in Legal Context`
  - online UUID: `69bca95c-4f7c-839e-8b3a-3c5e273f185a`
  - canonical thread ID: `f9eec63632218ec0924bc7e5ba1cf041cafc5542`
  - source used: `db` (after direct UUID pull into `~/chat_archive.sqlite`)
  - main topics / decisions pulled from the thread:
    - the family-court `Magellan` / `Lighthouse` / `Evatt` pathways are a real
      institutional entry point for privacy-preserving legal tech, not just a
      generic use case
    - the compelling fit is bounded verification under information asymmetry:
      sensitive evidence, child-safety / DV risk signals, and claims that may
      need to be verified without broad disclosure
    - treat this as problem-framing / future product-positioning context, not a
      current implementation milestone
    - keep present repo work focused on fact-layer / provenance / operator
      review seams before any stronger ZK or court-workflow claims

- 2026-03-14 whitepaper context refresh:
  - resolved archived thread via `robust-context-fetch`
  - title: `Insights from Whitepaper`
  - online UUID: `69b41f22-a514-839f-946c-fa0e9f75cc46`
  - canonical thread ID: `eab13fe32136bc69aebdb9a21888b76215faab11`
  - source used: `db` (after pulling the online UUID into `~/chat_archive.sqlite`)
  - main topics / decisions pulled from the thread:
    - keep SL event-centric and observation-aware; do not flatten the core model
      into plain RDF triples
    - treat RDF/Wikidata compatibility as an adapter/export surface over SL's
      richer event / observation / provenance model
    - prioritize an explicit Observation layer that separates source statements
      from real-world events
    - prioritize case-construction primitives
      (`evidence -> fact -> norm -> claim`) ahead of broader ontology expansion
    - queue temporal law/versioning and jurisdiction as critical follow-on
      infrastructure after the observation/claim seam is explicit
    - avoid ontology explosion by preferring lean primitives plus typed
      relations/attributes over proliferating node classes
    - use p-adic / ultrametric structure as a candidate formalism for
      hierarchical case similarity and doctrinal clustering without defaulting
      to embedding-first search
    - treat legal reasoning as typed state transitions with guarded,
      provenance-auditable seams; "reversible" is a design direction for some
      transitions, not a blanket claim about all legal reasoning
    - prioritize Wikidata shapes that help with jurisdiction, court hierarchy,
      legislation/case relations, party/actor identity, temporal validity, and
      external-reference prepopulation rather than importing generic triples
- 2026-03-15 whitepaper thread re-resolved after further posts:
  - title: `Insights from Whitepaper`
  - online UUID: `69b41f22-a514-839f-946c-fa0e9f75cc46`
  - canonical thread ID: `eab13fe32136bc69aebdb9a21888b76215faab11`
  - source used: `db`
  - archived message count at refresh: `122`
  - latest archived assistant timestamp: `2026-03-13T15:19:54+00:00`
  - Mary Technology / parity takeaway:
    - near-term product priority should be parity with Mary's practical
      fact-management / chronology / provenance / contestation workflow layer
    - current SL whitepaper priorities remain valid, but should be treated as
      layer-two legal-semantic followthrough over a Mary-equivalent fact
      substrate rather than the first user-facing milestone
    - ontology bridge / branch-set / external-ref work should be framed as
      support infrastructure for that parity target
    - typed transitions, burden policy, and p-adic retrieval remain strategic
      differentiators after the fact layer is credible
- 2026-03-15 Mary-parity fact-substrate interpretation update:
  - source: current working turn, aligned against
    `docs/planning/mary_parity_roadmap_20260315.md`
  - main decision:
    - the first Mary-parity fact substrate should not jump directly from
      `statement -> fact`
    - it should introduce a text-grounded `ObservationRecord` seam using a
      small stable predicate catalog for roughly 80-90% of factual statements
  - comparison with existing repo concepts:
    - existing `CaseObservation`, `ActionObservation`, `AlignmentObservation`,
      and `DecisionObservation` types are projection/aggregation shapes, not
      the canonical fact-intake observation lane
    - the new fact-intake observation layer should remain text-grounded and
      provenance-linked to statements/excerpts/sources
  - initial predicate families to scaffold:
    - actor identification
    - actions / events
    - object / target
    - temporal
    - harm / consequence
    - legal / procedural
  - design rule:
    - keep predicates few and stable, keep objects rich, and treat Wikidata as
      enrichment for objects rather than authority for predicate vocabulary
- 2026-03-15 event-candidate followthrough:
  - source: current working turn, aligned against the new fact-observation
    scaffold
  - main decision:
    - the next deterministic seam after observations is a derived
      `EventCandidate` layer
    - events should be reconstructable from observations and never become the
      primary source of truth
  - storage shape:
    - `event_candidates`
    - `event_attributes`
    - `event_evidence`
  - assembly stance:
    - rule-based and conservative
    - create events from event-trigger predicates plus actor/context anchors
    - merge only on stable explicit signatures
    - keep contestation observation-first, even when observations attach to the
      same event
- 2026-03-15 fact-substrate tightening pass:
  - reserve explicit distinction between:
    - structural/content-derived identity
    - run/execution metadata
  - make abstention explicit rather than inferring it from missing rows
  - keep event assembly language- and jurisdiction-neutral by consuming only
    normalized observation predicates; variation belongs in dictionaries,
    mappings, and parser-backed normalization packs instead
- 2026-03-15 Mary-parity role-pressure expansion:
  - expanded the new Mary-parity user stories in `docs/user_stories.md` for:
    - community legal centre intake
    - NGO litigation/campaign assembly
    - paralegal, solicitor, barrister, and judge/associate workflows
    - personal ITIR, investigative ITIR, trauma-survivor, and support-worker
      workflows
    - contested Wikipedia / Wikidata moderation and legality-assessment roles
    - adversarial public-figure and source-shopping / overstatement /
      sanitization pressures
    - family-law, child-sensitive, and cross-side handoff workflows
    - medical-negligence and professional-discipline overlap workflows
    - personal-to-professional handoff workflows
    - anti-AI-psychosis / false-coherence-resistance workflows
  - added the planning follow-ons:
    - `docs/planning/mary_parity_user_story_acceptance_matrix_20260315.md`
    - `docs/planning/mary_parity_gap_analysis_20260315.md`
  - story-informed near-term Mary-parity priority order:
    1. richer review queue reasons and contested/chronology triage
    2. source workflow run -> fact-review run reopen mapping
    3. widened legal/procedural observation visibility
- 2026-03-15 Mary-parity acceptance expansion status:
  - explicit passing gates now exist for:
    - `wave1_legal`
    - `wave2_balanced`
    - `wave3_trauma_advocacy`
    - `wave3_public_knowledge`
    - `wave4_family_law`
    - `wave4_medical_regulatory`
    - `wave5_handoff_false_coherence`
  - Wave 5 is no longer synthetic-only; it now includes repo-curated real
    transcript fixtures for professional handoff and contradiction-preserving
    false-coherence review
  - current Mary-parity limiting factor is no longer missing substrate
  - current limiting factors are:
    - real-fixture breadth in some newer waves
    - operator/workbench/export polish
  - planning baseline for the next loop:
    - `docs/planning/mary_parity_status_audit_20260315.md`
- 2026-03-26 user-story implementation coverage audit:
  - user-story breadth is now materially ahead of implementation breadth
  - repo-backed support is currently strongest in:
    - AU affidavit review geometry
    - Wikidata checked/dense structural review
    - GWB checked/broader review
    - normalized cross-lane metrics and profile mapping
    - deterministic provenance-bearing export artifacts
  - repo support is only partial/implicit for:
    - provenance-only partner/integrator use
    - offline capture beyond the narrow QG -> TiRC sink bridge
  - current honest boundary:
    - stories exist for private-user escalation, whistleblower workflows,
      community/disability intake, annotation/QA, research/publication,
      field inspection, and SDK/API integrators
    - those are not yet product-grade implementation claims
  - audit/spec note added at:
    - `SensibLaw/docs/planning/user_story_implementation_coverage_20260326.md`
  - follow-on TODOs now explicitly track the missing implementation lanes so
    story coverage does not silently masquerade as code coverage
- 2026-03-15 Mary-parity Wave 1 legal gate:
  - added a canonical fixture manifest at
    `SensibLaw/data/fact_review/wave1_legal_fixture_manifest_v1.json`
  - added `SensibLaw/scripts/run_fact_review_acceptance_wave.py` to build the
    canonical transcript/AU + synthetic fixtures and emit a batch acceptance
    report for `wave1_legal`
  - tightened acceptance results with failed-check IDs and gap tags so the
    next implementation loop can be backlog-driven from real story failures
  - tightened the fact-review workbench with grouped issue filters,
    source-centric reopen links, approximate chronology visibility, and a
    clearer assertion/outcome/annotation distinction
- 2026-03-19 Mary-parity next-step lock:
  - next SL-facing priority is operator-surface validation over the existing
    persisted fact-review contract, not more substrate expansion
  - the current Mary-parity pressure is:
    - `itir-svelte` `/graphs/fact-review` behavior against persisted
      `wave1_legal` runs
    - source-centric reopen behavior
    - canonical issue-filter switching
    - inspector classification rendering for `party_assertion`,
      `procedural_outcome`, and `later_annotation`
  - the fact-review route/server adapter has already been tightened to consume
    explicit workbench fields instead of ad hoc client derivation, so the next
    follow-through should prefer behavior-level UI validation and operator
    polish before another semantic-family expansion
- Completed slices:
  - workbench graph/review contract implementation in `itir-svelte`
  - P0 tokenizer/lexeme migration verification refresh with passing regression lane
  - P1 SL engine/profile followthrough v1 with concrete profile admissibility implementation and tests
  - NotebookLM metadata/review parity v1 started as a neutral read-model/source
    reuse slice rather than a fake activity-accounting upgrade
- New SL profile module:
  - `SensibLaw/src/text/profile_admissibility.py`
  - enforces profile allowlists and global span linting while preserving canonical tokens
- New tests:
  - `SensibLaw/tests/test_profile_admissibility.py` (passing)
- Documentation now aligned with implementation for:
  - `compression_engine.md`
  - `profile_contracts.md`
  - `profile_lint_rules.md`
  - `cross_profile_safety_tests.md`
- Progress on next priority sprint:
  - DONE: Tool Use Summary hydration fix for `Shell/hour` and `Input/hour` in
    SB reducer (`exec_command` + `request_user_input` hour bins).
  - DONE: regression coverage for these counters in
    `StatiBaker/tests/test_dashboard.py`.
  - DONE: NotebookLM notes-meta events now flow into tool-use stream as
    `notebooklm_meta_event` (family + hour bins).
- Additional hardening slice completed:
  - DONE: `A8` fail-closed CI stubs + waiver path for assumption controls
    (`docs/planning/assumption_controls_registry.json`).
  - DONE: `A1/Q1` axis hierarchy fixture coverage (collision detection +
    deterministic 2D fallback) in SensibLaw ribbon utilities/tests.
  - DONE: `A7/Q11` lexical-noise actor guards for stopwords/number-heavy spans/citation
    boilerplate flooding in `SensibLaw/tests/test_obligations_detection.py` and
    noise-actor fixtures.
- Ribbon ownership/context alignment:
  - archive thread resolved from local DB:
    - title: `Timeline Ribbon Overview`
    - online UUID: `69857c15-29ec-8398-ab2d-11f89180f79e`
    - canonical thread ID: `44e84563357cc580eb3f33faa72bf5658202364e`
    - source used: `db`
  - supporting historical concept thread also resolved from local DB:
    - title: `Feature timeline visualization`
    - online UUID: unknown / not stored
    - canonical thread ID: `f8170d36e0b2c28b2bb0366a7dc35a433e26ca00`
    - source used: `db`
  - current repo-facing decision:
    - `itir-ribbon/` remains the contract/spec source for ribbon invariants,
      lens DSL, and phase packs
    - `itir-svelte/` is the active UI/dev front where richer ribbon surfaces
      should live
    - when stream-oriented language appears in planning or pitches, treat it as
      the substrate feeding Ribbon rather than as a separate product surface
    - Ribbon remains general-purpose across conserved-allocation / timeline
      views; finance/social/legal streams are examples, not the boundary of the
      surface
    - existing `step-ribbon` wiki layout is a deterministic graph placement
      mode, not the full conserved-allocation ribbon surface
- NotebookLM current testing posture:
  - prefer a bounded live E2E smoke before broader network/generation runs
  - smoke should cover:
    - `auth check --test`
    - readonly notebook listing/get
    - one bounded chat ask
    - source listing on the same readonly notebook
  - first live attempt exposed an environment-only blocker:
    - repo `.venv` had valid NotebookLM auth storage
    - repo `.venv` was missing `pytest-asyncio` and `pytest-timeout`
    - async E2E fixtures therefore failed before the readonly smoke reached
      the API layer
  - resolved live-smoke path:
    - install the missing NotebookLM test deps into the repo-root `.venv`
    - keep using the repo-root `.venv` for live NotebookLM smoke runs
    - nested `notebooklm-py/.venv` was removed
    - live `auth check --test` succeeded
    - live bounded readonly smoke succeeded against notebook
      `2c63ab1a-08b9-4b6a-99e6-93469cc83c7f` (`SENSIBLAW`):
      - list notebooks
      - get notebook
      - one bounded chat ask
      - list sources
  - smoke runner should trust its explicit safe node list rather than the
    broader `readonly` pytest marker, because current marker coverage is
    incomplete for some live-read tests
  - treat token refresh and network permission as explicit prerequisites rather
    than assuming live NotebookLM access is always available
  - current NotebookLM suite posture:
    - enough for lifecycle/review/source reuse
    - not yet honest enough for waterfall/timeline activity parity
  - first standardization slice should add:
    - producer-owned NotebookLM observer report/query helpers
    - source-unit projection from source summaries/snippets
    - no reinterpretation of `notes_meta` as sessionized activity
  - DONE: separate additive NotebookLM interaction capture over conversation
    history + notes
    - raw families: `conversation_observed`, `note_observed`
    - normalized signal stays separate (`notebooklm_activity`)
    - query/read-model helpers and `TextUnit` preview projection now exist
    - still no dashboard session/waterfall claims from this lane alone
  - DONE: `A2/Q2` SB fold neutrality hardening via explicit fold-policy receipt,
    machine `mechanical_should_flags`, explicit fold `loss_profile`, and
    anti-nudge red-team tests.
  - DONE: `A3` causal claim-link provenance gates in
      `SensibLaw/src/reporting/narrative_compare.py`:
    - `supports`/`undermines` now emit required
      `link_type`, `confidence`, `counter_hypothesis_ref`
    - public artifact validator fails closed on missing causal provenance
    - regression coverage added in
      `SensibLaw/tests/test_narrative_compare.py`
    - host-wide pytest run and direct smoke run passed
  - DONE: additive fact-intake semantic normalization in `SensibLaw`
    - raw source/excerpt/statement/observation/fact/event tables remain the
      canonical observed layer
    - new sidecar semantic tables persist:
      - controlled classifications
      - inference results
      - cross-entity relations
      - policy outcomes
      - semantic refresh receipts
    - `persist_fact_intake_payload(...)` now dual-writes semantic
      materialization for new runs
    - `scripts/backfill_fact_semantics.py` rebuilds normalized semantics for
      existing runs without migration-time auto-backfill
    - review summary/workbench now prefer normalized semantic rows and only
      fall back to legacy derivation for non-materialized runs
    - lexical Zelph graphs remain derived/materialized, not OLTP-normalized
