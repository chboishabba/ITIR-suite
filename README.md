# ITIR-suite

ITIR-suite is the top-level workspace for a set of tools that help capture,
organize, review, and hand off difficult material without losing provenance.

In plain language:

- `tircorder-JOBBIE` and `WhisperX-WebUI` help capture and transcribe audio.
- `SensibLaw` turns messy source material into structured, reviewable artifacts.
- `StatiBaker` compiles day-level state from logs, tools, and activity traces.
- the suite-level docs and contracts in this repo keep those projects aligned.

This repo is the place where those pieces are pinned together, documented
together, and routed together. Most detailed setup and day-to-day running
happens inside the individual project directories.

## What This Repo Is For

Use the root repo when you want to:

- clone the whole suite in one shot
- keep submodules pinned to known commits
- find the main cross-project contracts and handoff docs
- understand what the suite can already do today
- jump to the right subproject README instead of guessing

This root repo is not a single deployable app. It is the shared workspace and
control surface for multiple related tools.

## Current Moonshot Direction

The current suite-level direction is compiler-shaped.

The current lane plans are stepping stones, not the top-level destination.

The original arc was closer to a smart journal than to a single legal engine:

- capture difficult reality
- preserve it without losing provenance
- compile usable state from it
- review and promote only what earns authority
- derive packets, graphs, and operator surfaces above that
- compare and union bounded products across domains

The legal/compiler work is one major proving ground inside that broader arc,
not the whole thing.

The new P0 read is that the suite should converge on a small normalized set
of concepts:

- source artifact
- provenance anchor
- context envelope
- canonical identity
- observed signal
- compiled state
- reviewable claim
- promoted record
- derived product
- follow obligation
- abstention / hold / unresolved pressure
- operator inspection surface
- bounded union surface

The current cross-lane direction is:

- bounded evidence bundle in
- promoted outcomes or abstentions out
- derived packet, report, and graph products after that

At the suite level that means:

- `tircorder-JOBBIE` and `WhisperX-WebUI` handle capture/transcription intake
- `SimulStreaming`, `whisper_streaming`, and `doctr` are additional
  evidence-shaping adapters where they stay bounded and provenance-preserving
- `chat-export-structurer` and related chat/archive tools handle canonical
  local memory/archive substrate
- `reverse-engineered-chatgpt`, `openrecall`, `notebooklm-py`, and
  `pyThunderbird` are bounded acquisition/retrieval/archive adapters
- `StatiBaker` handles read-only state compilation and continuity
- `SensibLaw` currently carries the substantive deterministic review,
  provenance, canonical reduction, promotion, and bounded graph/report work
- `SL-reasoner` remains a cordoned optional interpretive layer and stays low
  priority until the core engine is stable enough that a split is actually
  useful
- the current boundary seam is contract-shaped only:
  producer-owned repos may export read-only `reasoner_input_artifact`
  payloads, but substantive deterministic logic still stays in the owner repo
- `itir-mcp`, `itir-ribbon`, and `moltbook-api-client` are integration and
  operator-adjacent surfaces
- `itir-svelte` handles operator-facing read-only and review-first surfaces

Web-surface control note:

- `itir-svelte` is the sole intended product-facing web replacement lane
- legacy Pelican and Zola surfaces under `tircorder-JOBBIE` remain
  reference-only during migration
- root follow-up and sequencing live in [TODO.md](TODO.md) and
  [itir-svelte/README.md](itir-svelte/README.md)

The current suite-level integration doctrine is now MCP-first and guarded:

- MCP is the canonical contract layer for cross-project tool consumption
- bridge or HTTP shells are transport details, not alternate semantics
- consequential tool use should flow through guarded evaluation surfaces
  rather than raw direct calls
- policy, explanation, and receipts are intended to stay normalized rather
  than split across separate ad hoc client behaviors
- managed-host evidence and rollout lanes are higher-trust internal surfaces
- that managed-host class now explicitly includes both Windows and Linux
  evidence/evaluate/plan/apply lanes
- public repo/social discovery lanes are lower-trust candidate-risk surfaces
  that may propose follow obligations but do not authorize action on their own
- `WorldMonitor` and `OpenRecall` integrations now consume `itir.*` tools through
  the MCP seam only, with no duplicated core comparison or policy logic in
  either client. The consumer-side contract is adapter-only: normalize inputs,
  call ITIR/MCP, then expose bounded outputs plus receipts.

That same normalization rule is now explicit across the main `SensibLaw` lanes:

- AU legal/hearing material
- GWB public-source linkage material
- Wikidata migration/review material

The Wikidata/Nat lane is still review-first overall, but its handoff docs now
separately track candidate-level promotion gates and post-write verification
surfaces so the remaining automation gap is explicit instead of implied.

The broader legal moonshot is larger than the current bounded slices. The long
direction is toward cross-system legal understanding and comparison, but the
repo only advances that through bounded evidence, explicit promotion, and
derived challengeable products.

The next control read above the normalized-adapter phase is bounded search and
uncertainty collapse:

- inspect where the current graph, state, or product surface is weakest
- prefer local context first
- derive bounded search or follow only when current unresolved pressure
  justifies it
- target the next search toward the highest-authority and highest-yield source
  class likely to collapse uncertainty fastest
- reintegrate the result through the same promotion and derived-product rules

That means AU, GWB, Brexit, Wikidata/Nat, and large-corpus archive/retrieval
surfaces become priority drivers again, not because the normalized stack was
wrong, but because it is now real enough to pressure-test moonshot capability
at scale.

## Global Authority Expansion Control

The next widening step is global legal/source coverage, but it must remain
contract-first and bounded.

Current control read:

- English-first is the operational default for now.
- English is an adapter, not the ontology.
- Translation is allowed only as bounded alignment evidence below promotion.
- Machine translation may propose alignment or flag disagreement, but it does
  not create truth and it does not normalize canonical structure.

That means the immediate global-source program should prefer:

- sources with authoritative English text already available
- sources with stable parallel English editions or reliable official
  translations
- deterministic identifiers, structured retrieval, and clear provenance

For document-like evidence, "structured retrieval" is now read more strictly
than `vector + file path`.

The intended substrate is:

- raw document retained
- canonical text retained
- text revision identity retained
- derived chunk refs anchored by exact span/offset into canonical text

That stronger shape is what allows the suite to reconstruct exact evidence,
re-run evaluation deterministically, and emit compliance/legal receipts that
are replayable and challengeable.

High-value multilingual exceptions are allowed when they are known to be well
translated or stably parallelized, for example:

- UN documents and related UN library/document systems
- EUR-Lex and other EU official multilingual legal surfaces
- comparable treaty or transnational bodies with stable language variants

Lower-confidence multilingual surfaces should stay out of the main proof path
until they can enter through the same normalized contract with explicit
translation/alignment uncertainty.

Two named near-term proving grounds now sit inside that broader legal lane:

- AU legal follow, including one bounded AU -> UK/British follow hop when
  existing evidence already points there
- GWB legal linkage, including Brexit-era UK/EU legal-interaction cohorts and
  other bounded public-law cohorts where legal consequences are legible

Those proving grounds are normal program work now, not speculative extras.

Current rough progress read:

- capture / archive / canonical-memory substrate: roughly `55-65%`
- deterministic review / state / bounded operator surfaces: roughly `45-60%`
- recent legal/compiler program: roughly `70-80%`
- broader legal-moonshot preparation: roughly `35-45%`
- full smart-journal-to-legal-union moonshot: roughly `20-30%`

That means the suite is well past pure scaffolding, but still far from the
full end-state compiler of difficult reality.

Full-flow read at moonshot:

1. capture or ingest bounded source material
2. canonicalize identities, anchors, timestamps, envelopes, and lineage
3. compile read-only state and reviewable observations
4. follow justified dependencies and references in bounded ways
5. promote, abstain, or hold under explicit authority rules
6. derive packets, graphs, comparisons, dashboards, and operator views
7. union those bounded products across domains, jurisdictions, languages, and
   time where justified
8. analyze commonality, disjointness, conflict, and dependency structure
9. preserve challengeability, replay, and anti-panopticon constraints

The bounded planning note for that document-evidence rule is:

- [docs/planning/canonical_text_span_evidence_contract_20260407.md](docs/planning/canonical_text_span_evidence_contract_20260407.md)

Current P0 control read:

- keep the current plans
- reinterpret them as stepping stones under the normalized concepts above
- treat the normalized stack as infrastructure and use existing proving-ground
  lanes plus large corpora to drive bounded search, uncertainty-collapse
  quality, and authority-sensitive source selection
- only add implementation work where a submodule clearly violates that shape

That means existing AU, GWB, Wikidata/Nat, Brexit, JOHL, dad, and similar
domain lanes remain useful adopters and proving grounds, but they do not set
the suite priority order. The suite priority order is driven by product-stack
gaps in the correct repos:

- capture and archive producers in capture/archive repos
- compiled state in `StatiBaker`
- review and promotion in `SensibLaw`
- optional interpretive overlays in `SL-reasoner` only after the engine is
  sound enough that the boundary helps more than it hurts
- approved future-facing seam:
  contract-shaped read-only `reasoner_input_artifact` inputs from producer
  repos, with `SL-reasoner` limited to derived reasoning artifacts
- operator and integration surfaces in `itir-svelte`, `itir-mcp`,
  `itir-ribbon`, and related integration repos
- retrieval and bounded follow adapters in retrieval/archive repos

## Suite Constraints And Invariants

Hard constraints:

- no hidden rewrite of source reality
- no authority crossing without explicit promotion receipts
- no silent conversion of derived overlays into canonical truth
- no context-free rendering of consequential outputs
- no accidental second canonical reducer in side systems
- no follow expansion without an explicit bounded trigger
- no panopticon drift

Suite-wide invariants:

- provenance invariant
- normalization invariant
- expansion invariant
- context invariant
- authority invariant
- replay invariant
- derived-only invariant
- append-only state invariant
- anti-panopticon invariant

Preconditions:

- source artifacts are addressable
- provenance and identity fields are sufficient to anchor the flow
- context envelope is present when the output would otherwise be context-free
- authority class of the write path is known

Postconditions:

- artifacts are replayable and inspectable
- canonical writes are backed by promotion receipts
- derived products are explicitly marked as derived
- unresolved pressure remains visible as abstain / hold / follow-needed
- downstream handoff preserves IDs, lineage, and versioned assumptions

See:

- [docs/planning/moonshot_compiler_normalization_reconsideration_20260402.md](docs/planning/moonshot_compiler_normalization_reconsideration_20260402.md)
- [docs/planning/suite_bounded_search_uncertainty_collapse_20260403.md](docs/planning/suite_bounded_search_uncertainty_collapse_20260403.md)
- [docs/planning/legal_moonshot_au_follow_graph_and_panopticon_boundary_20260402.md](docs/planning/legal_moonshot_au_follow_graph_and_panopticon_boundary_20260402.md)
- [docs/planning/suite_smart_journal_moonshot_and_invariants_20260402.md](docs/planning/suite_smart_journal_moonshot_and_invariants_20260402.md)
- [docs/planning/suite_p0_moonshot_normalized_concepts_20260402.md](docs/planning/suite_p0_moonshot_normalized_concepts_20260402.md)

## Anti-Panopticon Boundary

The repo does not treat “understanding more” as permission to build
surveillance, prediction, or hidden interpretive authority.

Hard boundaries:

- no person-scoring or predictive judgment
- no hidden cross-context identity resolution
- no silent promotion of derived graphs into truth
- no replacement of primary legal authority with support summaries

See:

- [SensibLaw/docs/panopticon_refusal.md](SensibLaw/docs/panopticon_refusal.md)
- [SensibLaw/docs/red_team_anti_panopticon.md](SensibLaw/docs/red_team_anti_panopticon.md)
- [SensibLaw/docs/judicial_decision_behavior_contract.md](SensibLaw/docs/judicial_decision_behavior_contract.md)
- [SensibLaw/docs/official_decision_behavior_contract.md](SensibLaw/docs/official_decision_behavior_contract.md)

## What You Can Do Today

### 1. Capture and transcribe real-world material

The suite can capture spoken material, run transcription, and keep the outputs
available for downstream review instead of treating them as disposable text.

Typical flow:

- capture or collect audio in `tircorder-JOBBIE`
- transcribe through `WhisperX-WebUI`
- pass transcripts and related outputs into structured review surfaces

Why that matters:

- you keep a trail back to the source material
- downstream tools can work from stable artifacts instead of ad hoc notes

### 2. Turn messy source material into reviewable structured data

`SensibLaw` is the main deterministic review layer in the suite. It is built to
take difficult source material and turn it into bounded, inspectable outputs
rather than magical summaries.

Typical outputs include:

- structured slices and projections
- review queues
- handoff bundles
- provenance-backed JSON artifacts

Why that matters:

- a later reviewer can inspect what was found
- you can keep uncertainty visible instead of flattening it away

### 3. Compile day-level state instead of relying on memory

`StatiBaker` turns logs, activity, and machine-readable traces into a daily
state view.

Typical outputs include:

- what changed
- what stalled
- what remains unresolved
- what actions or machine states are still pending

Why that matters:

- it is designed to preserve traceable state, not pretend to be a chatbot
- it helps recover continuity after interruption or context collapse

### 4. Run bounded ontology diagnostics and produce human-readable review artifacts

The suite also includes a bounded Wikidata diagnostics lane inside
`SensibLaw`. This is one of the clearest current examples of the repo doing
something concrete and externally legible.

The important point is not just "we have diagnostics." It is that the outputs
are small, pinned, reviewable, and backed by repo artifacts.

## Proven Abilities

These are not abstract goals. They are current repo-backed examples.

### Bounded Wikidata examples

- A clean baseline around `nucleon` / `proton` / `neutron`, where the
  disjointness relation is present but there are no violations.
- A real contradiction around `working fluid`, where `working fluid` is typed
  as both `gas` and `liquid`.
- A real contradiction in the `fixed construction` / `geographic entity` area,
  where the current pinned slice shows several subclass violations.
- A synthetic transport example used to make the reporting deterministic, with
  amphibious/land/water subclass and instance violations.

What those examples mean:

- the system can preserve a real "nothing wrong here" baseline, not just find
  false alarms everywhere
- it can catch direct item-level conflicts
- it can also catch longer subclass-chain structural problems
- it can turn those findings into checked summaries and review rows instead of
  leaving them as raw graph noise

Short version:

- one zero-violation baseline
- one direct instance contradiction
- one subclass contradiction chain
- one synthetic deterministic regression/demo case

### Human-readable review and handoff surfaces

The suite already has checked handoff artifacts that summarize bounded slices in
plain-language summaries plus machine-readable artifacts, instead of expecting a
reviewer to inspect only raw intermediate data.

That matters because:

- the outputs are discussable with collaborators
- they are stable enough to revisit
- they make the current boundaries explicit: what is demonstrated, what is
  still under review, and what is not being claimed yet

### Cross-project workflow, not just isolated modules

The projects in this workspace are not just adjacent folders. The repo already
contains cross-project contracts covering handoff, review boundaries, and
orchestration responsibilities.

That means the suite is already useful as:

- a bounded evidence-to-review workflow
- a diagnostics-and-handoff workspace
- a place to keep multiple tools aligned without silently merging their roles

## Root Setup

Clone the suite and initialize the pinned submodules:

```bash
git clone https://github.com/chboishabba/ITIR-suite.git
cd ITIR-suite
./setup.sh
```

If you already have the repo:

```bash
git submodule update --init --recursive
```

Optional root Python environment:

```bash
./env_init.sh
source .venv/bin/activate
```

Use the root environment when you need a shared compatibility environment across
the workspace. For most real work, prefer the setup instructions in each
subproject's own README.

## How To Use The Suite

Start at the root only long enough to get the workspace in place. Then move to
the subproject that matches the job you actually want to do.

### If you want to work with structured review, provenance, or Wikidata diagnostics

Go to [SensibLaw/README.md](SensibLaw/README.md).

### If you want audio capture and transcription intake

Go to [tircorder-JOBBIE/README.md](tircorder-JOBBIE/README.md)
and [WhisperX-WebUI/README.md](WhisperX-WebUI/README.md).

### If you want daily state compilation and context recovery

Go to [StatiBaker/README.md](StatiBaker/README.md).

### If you want the chat/context tooling

Go to [reverse-engineered-chatgpt/README.md](reverse-engineered-chatgpt/README.md)
and [chat-export-structurer/README.md](chat-export-structurer/README.md).

## Where To Find Things

### Suite-level orientation

- project interface index:
  [docs/planning/project_interfaces.md](docs/planning/project_interfaces.md)
- orchestration role:
  [docs/planning/itir_orchestrator.md](docs/planning/itir_orchestrator.md)
- architecture boundary doctrine:
  [docs/architecture/admissibility_lattice.md](docs/architecture/admissibility_lattice.md)
- JMD x SensibLaw truth-construction boundary:
  [docs/planning/jmd_sensiblaw_truth_construction_boundary_20260327.md](docs/planning/jmd_sensiblaw_truth_construction_boundary_20260327.md)
- motif candidate / promotion / legal-tree boundary:
  [docs/planning/motif_candidate_promotion_legal_tree_20260327.md](docs/planning/motif_candidate_promotion_legal_tree_20260327.md)
- latent state over promoted truth:
  [docs/planning/latent_state_over_promoted_truth_20260327.md](docs/planning/latent_state_over_promoted_truth_20260327.md)
- global latent legal state across systems:
  [docs/planning/global_latent_legal_state_cross_system_20260327.md](docs/planning/global_latent_legal_state_cross_system_20260327.md)
- Mirror Telegram support-layer boundary:
  [docs/planning/mirror_telegram_support_layer_boundary_20260401.md](docs/planning/mirror_telegram_support_layer_boundary_20260401.md)
- `Phi` mapping and latent graph schema:
  [docs/planning/phi_mapping_and_latent_graph_schema_20260328.md](docs/planning/phi_mapping_and_latent_graph_schema_20260328.md)
- all-sources `FactBundle` / reconciliation boundary:
  [docs/planning/all_sources_factbundle_reconciliation_boundary_20260328.md](docs/planning/all_sources_factbundle_reconciliation_boundary_20260328.md)
- sentiment / affect non-canonical boundary:
  [docs/planning/sentiment_affect_noncanonical_boundary_20260328.md](docs/planning/sentiment_affect_noncanonical_boundary_20260328.md)
- publish-layer findings and role split:
  [docs/planning/publish_layer_findings_20260328.md](docs/planning/publish_layer_findings_20260328.md)
- ZOS / SL / Zelph contract findings:
  [docs/planning/zos_sl_zelph_contract_findings_20260328.md](docs/planning/zos_sl_zelph_contract_findings_20260328.md)
- ZOS vs fuzzymodo / Casey / StatiBaker:
  [docs/planning/zos_vs_fuzzymodo_casey_statiBaker_20260328.md](docs/planning/zos_vs_fuzzymodo_casey_statiBaker_20260328.md)
- publisher/puller contract for Zelph consumers:
  [docs/planning/publisher_puller_contract_for_zelph_consumers_20260328.md](docs/planning/publisher_puller_contract_for_zelph_consumers_20260328.md)
- JMD push/pull surfaces and blockers:
  [docs/planning/jmd_push_pull_surfaces_and_blockers_20260329.md](docs/planning/jmd_push_pull_surfaces_and_blockers_20260329.md)
- Zelph / ERDFA / HF / IPFS example flow:
  [docs/planning/zelph_erdfa_hf_ipfs_example_flow_20260329.md](docs/planning/zelph_erdfa_hf_ipfs_example_flow_20260329.md)
- `n00b` corroborating surfaces:
  [docs/planning/n00b_corroborating_surfaces_20260329.md](docs/planning/n00b_corroborating_surfaces_20260329.md)
- `erdfa-publish-rs` vs shared shard contract:
  [docs/planning/erdfa_publish_rs_vs_shared_shard_contract_20260329.md](docs/planning/erdfa_publish_rs_vs_shared_shard_contract_20260329.md)
- canonical ZKP / SL / DA51 message schema findings:
  [docs/planning/canonical_zkp_sl_da51_message_schema_findings_20260329.md](docs/planning/canonical_zkp_sl_da51_message_schema_findings_20260329.md)
- JMD HF container and spectral retrieval findings:
  [docs/planning/jmd_hf_container_and_spectral_retrieval_findings_20260329.md](docs/planning/jmd_hf_container_and_spectral_retrieval_findings_20260329.md)
- notebooklm-pack vs ZOS/JMD boundary:
  [docs/planning/notebooklm_pack_zos_jmd_boundary_20260329.md](docs/planning/notebooklm_pack_zos_jmd_boundary_20260329.md)
- notebooklm-pack to notebooklm-py interface:
  [docs/planning/notebooklm_pack_to_notebooklm_py_interface_20260329.md](docs/planning/notebooklm_pack_to_notebooklm_py_interface_20260329.md)
- JMD NotebookLM seam minimal object:
  [docs/planning/jmd_notebooklm_seam_minimal_object_20260329.md](docs/planning/jmd_notebooklm_seam_minimal_object_20260329.md)
- repo-local NotebookLM clarify bridge:
  `scripts/notebooklm_clarify.py`
- HF container/index contract:
  [docs/planning/hf_container_index_contract_20260329.md](docs/planning/hf_container_index_contract_20260329.md)
- HF container/index fixture v1:
  [docs/planning/hf_container_index_fixture_v1_20260329.md](docs/planning/hf_container_index_fixture_v1_20260329.md)
- `erdfa-publish-rs` manifest promotion v1:
  [docs/planning/erdfa_publish_rs_manifest_promotion_v1_20260329.md](docs/planning/erdfa_publish_rs_manifest_promotion_v1_20260329.md)
- spectral post-selector retrieval contract:
  [docs/planning/spectral_post_selector_retrieval_contract_20260329.md](docs/planning/spectral_post_selector_retrieval_contract_20260329.md)
- shard stack layer order:
  [docs/planning/shard_stack_layer_order_20260329.md](docs/planning/shard_stack_layer_order_20260329.md)
- RG toy completion findings:
  [docs/planning/rg_toy_completion_findings_20260329.md](docs/planning/rg_toy_completion_findings_20260329.md)
- Resonance and Overlap findings:
  [docs/planning/resonance_and_overlap_findings_20260329.md](docs/planning/resonance_and_overlap_findings_20260329.md)
- TEMP ZOS/SL bridge review:
  [docs/planning/temp_zos_sl_bridge_impl_review_20260329.md](docs/planning/temp_zos_sl_bridge_impl_review_20260329.md)
- affidavit claim reconciliation contract:
  [docs/planning/affidavit_claim_reconciliation_contract_20260329.md](docs/planning/affidavit_claim_reconciliation_contract_20260329.md)
- affidavit coverage review lane and Johl Mary-parity fixture:
  [docs/planning/affidavit_coverage_review_lane_20260325.md](docs/planning/affidavit_coverage_review_lane_20260325.md)
- local publish / consume release gates:
  [docs/planning/local_publish_consume_release_gates_20260330.md](docs/planning/local_publish_consume_release_gates_20260330.md)
- hosted sink acknowledgement contract:
  [docs/planning/hosted_sink_acknowledgement_contract_20260330.md](docs/planning/hosted_sink_acknowledgement_contract_20260330.md)
- HF acknowledgement probe:
  [docs/planning/hf_acknowledgement_probe_20260330.md](docs/planning/hf_acknowledgement_probe_20260330.md)
- HF write acknowledgement probe:
  [docs/planning/hf_write_acknowledgement_probe_20260330.md](docs/planning/hf_write_acknowledgement_probe_20260330.md)
- HF receipt binding and remote bundle rehearsal:
  [docs/planning/hf_receipt_binding_and_remote_bundle_rehearsal_20260330.md](docs/planning/hf_receipt_binding_and_remote_bundle_rehearsal_20260330.md)
- IPFS acknowledgement readiness:
  [docs/planning/ipfs_acknowledgement_readiness_20260330.md](docs/planning/ipfs_acknowledgement_readiness_20260330.md)
- publisher-native hosted acknowledgement receipts:
  [docs/planning/publisher_native_hosted_ack_receipts_20260330.md](docs/planning/publisher_native_hosted_ack_receipts_20260330.md)
- ITIR real bundle consumer rehearsal:
  [docs/planning/itir_real_bundle_consumer_rehearsal_20260330.md](docs/planning/itir_real_bundle_consumer_rehearsal_20260330.md)
- zkperf on SL roadmap:
  [docs/planning/zkperf_on_sl_roadmap_20260329.md](docs/planning/zkperf_on_sl_roadmap_20260329.md)
- zkperf on SL contract v1:
  [docs/planning/zkperf_on_sl_contract_v1_20260329.md](docs/planning/zkperf_on_sl_contract_v1_20260329.md)
- zkperf stream shard contract v1:
  [docs/planning/zkperf_stream_shard_contract_v1_20260330.md](docs/planning/zkperf_stream_shard_contract_v1_20260330.md)

### ZKPerf stream operator command

- one-shot publish plus verify:
  `scripts/run_zkperf_stream_hf.sh --fixture <path-to-zkperf-stream-json>`

### Proven example and handoff docs

- shortest Wikidata/Zelph external handoff overview:
  [docs/planning/wikidata_zelph_single_handoff_20260325.md](docs/planning/wikidata_zelph_single_handoff_20260325.md)
- current Wikidata working status:
  [SensibLaw/docs/wikidata_working_group_status.md](SensibLaw/docs/wikidata_working_group_status.md)
- disjointness report contract:
  [docs/planning/wikidata_disjointness_report_contract_v1_20260325.md](docs/planning/wikidata_disjointness_report_contract_v1_20260325.md)
- disjointness case index:
  [docs/planning/wikidata_disjointness_case_index_v1.json](docs/planning/wikidata_disjointness_case_index_v1.json)
- checked structural handoff summary:
  [SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/wikidata_structural_handoff_v1.summary.md](SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/wikidata_structural_handoff_v1.summary.md)

### Additional operator and onboarding docs

- SensibLaw onboarding playbooks:
  [SensibLaw/docs/onboarding_playbooks.md](SensibLaw/docs/onboarding_playbooks.md)
- suite user stories:
  [docs/user_stories.md](docs/user_stories.md)

## Handoff And Collaboration

If you need a bounded, sendable explanation of what is already demonstrated and
what is not yet being claimed, start with:

- [docs/planning/wikidata_zelph_single_handoff_20260325.md](docs/planning/wikidata_zelph_single_handoff_20260325.md)

If you need the concrete checked artifact surfaces behind that summary, use:

- [SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/wikidata_structural_handoff_v1.summary.md](SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/wikidata_structural_handoff_v1.summary.md)
- [docs/planning/wikidata_disjointness_case_index_v1.json](docs/planning/wikidata_disjointness_case_index_v1.json)

This repo currently treats handoff as document- and artifact-backed. In other
words, the collaboration surface is the checked documentation and fixture
artifacts, not a vague promise that the system can do more than it has already
shown.

## Working With Submodules

- sync pinned submodules:
  ```bash
  git submodule update --init --recursive
  ```
- fast-forward submodules to tracked upstream state:
  ```bash
  git submodule update --remote --recursive
  ```
- sync clean submodules safely:
  ```bash
  ./sync-all-submodules.sh
  ```

If you change a submodule, commit inside that submodule first, then record the
updated pointer in this root repo.

## Helpful Root Scripts

- `./setup.sh`: initialize and update submodules
- `./env_init.sh`: build an optional root compatibility venv
- `./scripts/gitin-recursive.sh`: fast-forward pull the root repo, then sync
  and update submodules to the pinned commits recorded by the root repo while
  reporting any branch-attached submodule drift
- `./scripts/gitout-recursive.sh`: pull, commit, and push dirty repos
  recursively, with submodules first and explicit diverged-branch reporting
- `./scripts/sync_chat_context.sh`: sync conversation context into
  `__CONTEXT/last_sync/`
- `python scripts/build_docs_site.py`: build a lightweight local index of the
  repo's markdown docs under `docs/_site/`

## Advanced Environment Note

This workspace includes a compatibility-container path used during development
for AMD RX580 / older ROCm-related constraints. That is an environment-specific
development workaround, not the main entrypoint for most readers.

If you need that path, see the existing container/dev notes in the repo and the
relevant subproject setup docs before using it.
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/chboishabba/ITIR-suite)
