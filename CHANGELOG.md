# Changelog

## Unreleased
- Extended the AU legal-follow operator slice again without widening
  ownership: `SensibLaw/src/policy/legal_follow_graph.py` now ranks derived
  legal-claim review packets from structural `edge_admissibility` pressure
  and exposes bounded priority rollups in the operator summary, while
  `SensibLaw/src/fact_intake/review_bundle.py` can now recommend
  `legal_follow_graph` when legal-follow admissibility review pressure
  dominates promotion pressure. Validation:
  from `SensibLaw/`:
  `PYTHONPATH=. ../.venv/bin/python -m pytest tests/test_legal_follow_graph.py tests/test_au_fact_review_bundle.py tests/test_latent_promoted_graph.py tests/test_cross_system_phi_prototype.py -q`
  -> `29 passed`
- Extended the worker-landed AU legal-follow slice:
  `SensibLaw/src/policy/legal_follow_graph.py` now summarizes admissibility
  across derived `asserts_*` edges and exposes a bounded
  `edge_admissibility_queue` plus legal-claim packet detail rows. Downstream,
  `SensibLaw/src/fact_intake/au_review_bundle.py` now surfaces summary-level
  legal-follow edge-admissibility counts in both
  `semantic_context.legal_follow_graph.summary` and
  `operator_views.legal_follow_graph.summary`. Validation:
  from `SensibLaw/`:
  `PYTHONPATH=. ../.venv/bin/python -m pytest tests/test_legal_follow_graph.py tests/test_au_fact_review_bundle.py tests/test_latent_promoted_graph.py tests/test_cross_system_phi_prototype.py -q`
  -> `26 passed`
- Tightened the next AU legal-graph slice without widening ownership:
  `SensibLaw/src/policy/legal_follow_graph.py` now attaches typed
  `sl.legal_edge_admissibility.v1` output to derived `asserts_*` edges built
  from legal-claim relations. Promoted-anchor reuse keeps its existing owner
  surface in `SensibLaw/src/latent_promoted_graph.py`, while lower-layer
  relation candidates remain auditable instead of silently becoming promoted
  truth. Updated `SensibLaw/tests/test_legal_follow_graph.py`,
  `SensibLaw/README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md`.
  Validation:
  from `SensibLaw/`:
  `PYTHONPATH=. ../.venv/bin/python -m pytest tests/test_legal_follow_graph.py tests/test_latent_promoted_graph.py tests/test_cross_system_phi_prototype.py -q`
  -> `16 passed`
- Added
  [docs/planning/legal_ir_phi_composition_admissibility_boundary_20260417.md](/mnt/truenas/gem-net/mirror-nix/mirror_community_mgr/ITIR-suite/docs/planning/legal_ir_phi_composition_admissibility_boundary_20260417.md),
  updated
  [docs/architecture/admissibility_lattice.md](/mnt/truenas/gem-net/mirror-nix/mirror_community_mgr/ITIR-suite/docs/architecture/admissibility_lattice.md),
  [README.md](/mnt/truenas/gem-net/mirror-nix/mirror_community_mgr/ITIR-suite/README.md),
  [TODO.md](/mnt/truenas/gem-net/mirror-nix/mirror_community_mgr/ITIR-suite/TODO.md),
  and [COMPACTIFIED_CONTEXT.md](/mnt/truenas/gem-net/mirror-nix/mirror_community_mgr/ITIR-suite/COMPACTIFIED_CONTEXT.md)
  to pin the legal-IR boundary above minimal `Phi` emissions. The root docs
  now make the normalization rule explicit:
  `Phi -> composed candidate nodes -> admissibility -> promoted records -> derived graph`,
  with MDL / latent compression kept derived and non-promotive, and with the
  next worker lanes split across substrate, composition, admissibility,
  latent/MDL, and verification/docs ownership.
- Added the first bounded `SensibLaw` implementation slice for that boundary:
  `sl.composed_candidate_node.v1` plus a fail-closed composed-candidate
  admissibility gate. The new files are:
  `SensibLaw/src/models/composed_candidate_node.py`,
  `SensibLaw/src/composed_candidate_admissibility.py`,
  `SensibLaw/schemas/sl.composed_candidate_node.v1.schema.yaml`,
  `SensibLaw/examples/composed_candidate_node_minimal.json`,
  `SensibLaw/tests/test_composed_candidate_node.py`, and
  `SensibLaw/tests/test_composed_candidate_admissibility.py`.
  Validation:
  `PYTHONPATH=SensibLaw ./.venv/bin/python -m pytest SensibLaw/tests/test_composed_candidate_node.py SensibLaw/tests/test_composed_candidate_admissibility.py -q`
  -> `10 passed`
- Extended that slice with the first bounded downstream consumer:
  `SensibLaw/src/policy/review_claim_records.py` now adapts
  `sl.composed_candidate_node.v1` payloads into the existing
  `review_candidate` envelope without widening fact-intake or review-bundle
  contracts and without making candidate state truth-bearing.
  Validation:
  `PYTHONPATH=SensibLaw ./.venv/bin/python -m pytest SensibLaw/tests/test_composed_candidate_node.py SensibLaw/tests/test_composed_candidate_admissibility.py SensibLaw/tests/test_review_claim_records.py -q`
  -> `30 passed`
- Added the first bounded legal edge gate on top of that node-level surface:
  `SensibLaw/src/legal_edge_admissibility.py` now evaluates typed
  `relation_kind`, endpoint admissibility inputs, wrapper/status
  compatibility, section/genre compatibility, shared linkage, shared content
  identity where required, and structural status conflict for
  `contradicts` / `overrules`. The gate stays fail-closed and returns
  `promote | audit | abstain` without inferring relation meaning from raw
  text. Added focused coverage in
  `SensibLaw/tests/test_legal_edge_admissibility.py`.
  Validation:
  `PYTHONPATH=SensibLaw ./.venv/bin/python -m pytest SensibLaw/tests/test_composed_candidate_node.py SensibLaw/tests/test_composed_candidate_admissibility.py SensibLaw/tests/test_review_claim_records.py SensibLaw/tests/test_legal_edge_admissibility.py -q`
  -> `38 passed`
- Landed the next promoted-graph ownership slice:
  `SensibLaw/src/latent_promoted_graph.py` now emits promoted `legal_claim`
  nodes plus typed `grounds_claim`, `claim_subject`, and `claim_object`
  edges for promoted `review_relation` rows, with schema coverage in
  `SensibLaw/schemas/sl.latent_promoted_graph.v1.schema.yaml`. The first
  derived consumer now exists in
  `SensibLaw/src/policy/legal_follow_graph.py`, which can reuse that
  promoted-anchor surface instead of rebuilding legal claims from lower-layer
  state. Validation:
  from `SensibLaw/`:
  `PYTHONPATH=. ../.venv/bin/python -m pytest tests/test_latent_promoted_graph.py tests/test_legal_follow_graph.py tests/test_cross_system_phi_prototype.py -q`
  -> `15 passed`
- Added [SensibLaw/src/sources/worldbank_adapter.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/sources/worldbank_adapter.py),
  [SensibLaw/src/sources/worldbank/worldbank_follow_contract.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/sources/worldbank/worldbank_follow_contract.py),
  and extended
  [SensibLaw/src/search_selection/search_union.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/search_selection/search_union.py)
  plus
  [SensibLaw/src/metrics/source_normalization.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/metrics/source_normalization.py)
  so World Bank is now the second bounded global adopter on the normalized
  source contract. The new slice adds:
  - a normalized World Bank source adapter with deterministic doc ids,
    provenance, language/translation flags, and live/fallback status
  - a bounded live probe over one known World Bank document URL
  - a declarative follow contract for World Bank documents
  - World Bank readiness metrics layered onto the existing normalization gate
  Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_worldbank_source.py SensibLaw/tests/test_worldbank_follow_contract.py SensibLaw/tests/test_search_union.py SensibLaw/tests/metrics/test_source_normalization.py`
    -> `19 passed`
  - compile sanity:
    `.venv/bin/python -m py_compile SensibLaw/src/sources/worldbank_adapter.py SensibLaw/src/sources/worldbank/worldbank_follow_contract.py SensibLaw/src/sources/worldbank/__init__.py SensibLaw/src/search_selection/search_union.py SensibLaw/src/metrics/source_normalization.py`
  - direct live probe:
    `fetch_live_worldbank_report(doc_id=\"WDR2021\", url=\"https://documents.worldbank.org/en/publication/documents-reports/documentdetail/401781609909355252/world-development-report-2021\")`
    now returns a normalized live World Bank source unit.
- Extended [SensibLaw/src/sources/undocs.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/sources/undocs.py)
  and [SensibLaw/tests/test_undocs_source.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_undocs_source.py)
  so the bounded live UNDOCS slice now resolves past the language selector and
  normalizes the actual English document asset endpoint from the embedded UN
  viewer. Live probes for `A/RES/77/1` now return:
  - title: `UN document A/RES/77/1`
  - url:
    `https://documents.un.org/api/symbol/access?s=A/RES/77/1&l=en&t=pdf`
  Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_undocs_source.py`
    -> `3 passed`
  - compile sanity:
    `.venv/bin/python -m py_compile SensibLaw/src/sources/undocs.py`
- Added [SensibLaw/src/sources/undocs.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/sources/undocs.py),
  [SensibLaw/src/sources/un/un_follow_contract.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/sources/un/un_follow_contract.py),
  and extended
  [SensibLaw/src/search_selection/search_union.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/search_selection/search_union.py),
  [SensibLaw/src/search_selection/search_selection.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/search_selection/search_selection.py),
  and [SensibLaw/src/metrics/source_normalization.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/metrics/source_normalization.py)
  so the first real non-UK/EU adopter now exists on the normalized global
  source contract. The new UNDOCS slice adds:
  - deterministic UN document normalization around symbol/id, title, URL,
    authority/source type, provenance, primary language, translation status,
    and live/fallback fields
  - English-first search/rank plumbing that admits a bounded UN authority slot
    without pretending broader global coverage already exists
  - a declarative UN follow contract that keeps translation-derived links
    evidentiary and non-promotive
  - UN-specific readiness checks layered on top of source-normalization metrics
  Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_undocs_source.py SensibLaw/tests/test_un_follow_contract.py SensibLaw/tests/test_search_union.py SensibLaw/tests/metrics/test_source_normalization.py`
    -> `12 passed`
  - compile sanity:
    `.venv/bin/python -m py_compile SensibLaw/src/sources/undocs.py SensibLaw/src/sources/un/un_follow_contract.py SensibLaw/src/search_selection/search_union.py SensibLaw/src/search_selection/search_selection.py SensibLaw/src/metrics/source_normalization.py`
  - no-regression builder:
    `PYTHONPATH=. SENSIBLAW_EUR_LEX_LIVE=1 .venv/bin/python SensibLaw/scripts/build_gwb_broader_review.py --output-dir /tmp/gwb_undocs_round1`
    with queue stability preserved at `12` items, `12/12` non-null priority
    coverage, and `0` raw URL titles.
- Added [docs/planning/global_authority_source_normalization_20260403.md](/home/c/Documents/code/ITIR-suite/docs/planning/global_authority_source_normalization_20260403.md),
  updated [README.md](/home/c/Documents/code/ITIR-suite/README.md),
  [TODO.md](/home/c/Documents/code/ITIR-suite/TODO.md), and
  [__CONTEXT/COMPACTIFIED_CONTEXT.md](/home/c/Documents/code/ITIR-suite/__CONTEXT/COMPACTIFIED_CONTEXT.md)
  to lock the next global-source widening rule:
  English-first operationally, English as an adapter rather than ontology, and
  translation/alignment below promotion as bounded evidence only. The docs now
  also flag UN-style and other stable parallel-English corpora as early
  high-value exceptions rather than pretending to support broad multilingual
  normalization already.
- Added
  [SensibLaw/src/sources/normalized_source.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/sources/normalized_source.py),
  [SensibLaw/src/search_selection/search_union.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/search_selection/search_union.py),
  [SensibLaw/src/search_selection/search_selection.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/search_selection/search_selection.py),
  [SensibLaw/src/metrics/source_normalization.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/metrics/source_normalization.py),
  and extended
  [SensibLaw/src/sources/uk_legislation.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/sources/uk_legislation.py)
  plus
  [SensibLaw/src/sources/national_archives/brexit_national_archives_lane.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/sources/national_archives/brexit_national_archives_lane.py)
  so the suite now has its first bounded global-source normalization slice:
  - canonical normalized source units with language and translation-status
    fields
  - English-first search/ref union and authority-aware ranking helpers
  - explicit translation-bounded follow constraints for archive/legal follows
  - source-normalization readiness metrics covering contract completeness,
    authority lattice clarity, provenance, live/fallback visibility, and
    translation/alignment boundedness
  Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_normalized_source.py SensibLaw/tests/test_uk_legislation_follow.py SensibLaw/tests/test_search_union.py SensibLaw/tests/test_national_archives_follow_contract.py SensibLaw/tests/metrics/test_source_normalization.py`
    -> `15 passed`
  - compile sanity:
    `.venv/bin/python -m py_compile SensibLaw/src/sources/normalized_source.py SensibLaw/src/sources/uk_legislation.py SensibLaw/src/search_selection/search_union.py SensibLaw/src/search_selection/search_selection.py SensibLaw/src/sources/national_archives/brexit_national_archives_lane.py SensibLaw/src/metrics/source_normalization.py`
  - no-regression builder:
    `PYTHONPATH=. SENSIBLAW_EUR_LEX_LIVE=1 .venv/bin/python SensibLaw/scripts/build_gwb_broader_review.py --output-dir /tmp/gwb_global_norm_round1`
    with queue stability preserved at `12` items, `12/12` non-null priority
    coverage, and `0` raw URL titles.
- Extended [SensibLaw/src/ontology/wikidata_grounding_depth.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/ontology/wikidata_grounding_depth.py)
  and [SensibLaw/tests/test_wikidata_nat_grounding_depth.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_grounding_depth.py)
  so Nat grounding summary/report/priority surfaces can consume bounded live-follow
  result rows. When a packet already has fetched live receipts, the priority
  surface now marks it as `live_receipts_ready_for_review` and points the next
  bounded action at reviewing that evidence instead of requesting another
  follow. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_nat_grounding_depth.py`
    -> `16 passed`
  - root governance:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `5 passed`
- Extended [SensibLaw/src/ontology/wikidata_nat_live_follow_executor.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/ontology/wikidata_nat_live_follow_executor.py),
  [SensibLaw/tests/test_wikidata_nat_live_follow_executor.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_live_follow_executor.py),
  and [SensibLaw/tests/fixtures/wikidata/wikidata_nat_cohort_b_operator_packet_input_20260402.json](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/fixtures/wikidata/wikidata_nat_cohort_b_operator_packet_input_20260402.json)
  so Nat live-follow now reads concrete local Cohort B row reference URLs for
  reconciled non-business variance instead of falling back immediately to
  revision-locked fetches. Live reruns now show:
  - `split_heavy_business_family` resolves both rows through
    `named_query_link`
  - `policy_risk_population_preview` resolves both rows through
    `named_reference_url`
  - `reconciled_non_business_variance` now also resolves both rows through
    `named_reference_url`
  Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_wikidata_nat_live_follow_executor.py tests/test_wikidata_cli.py -k 'live_follow_execute or live_follow_campaign'`
    -> `9 passed`
- Extended [SensibLaw/src/ontology/wikidata_nat_live_follow_executor.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/ontology/wikidata_nat_live_follow_executor.py)
  and [SensibLaw/tests/test_wikidata_nat_live_follow_executor.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_live_follow_executor.py)
  so Nat live-follow now implements `named_reference_url` from locally pinned
  reference surfaces. Live reruns show:
  - `policy_risk_population_preview` now resolves both rows through
    `named_reference_url`
  - `reconciled_non_business_variance` initially still fell back to
    `named_revision_locked_source` before the later Cohort B packet-input
    reference-url pinning completed
- Added [SensibLaw/src/ontology/wikidata_nat_live_follow_executor.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/ontology/wikidata_nat_live_follow_executor.py)
  and extended [SensibLaw/cli/__main__.py](/home/c/Documents/code/ITIR-suite/SensibLaw/cli/__main__.py),
  [SensibLaw/tests/test_wikidata_nat_live_follow_executor.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_live_follow_executor.py),
  and [SensibLaw/tests/test_wikidata_cli.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_cli.py)
  so the pinned Nat live-follow campaign can now be executed as a bounded
  live fetch run through `sensiblaw wikidata nat-live-follow-execute`. The
  executor currently supports revision-locked Wikidata fetches, preserves
  real fetch errors over unsupported fallback source classes, and has already
  been exercised live on:
  - `hard_grounding_packet:1` -> `Q10403939`
  - `split_heavy_business_family:1` -> `Q738421`
  Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_wikidata_nat_live_follow_campaign.py tests/test_wikidata_nat_live_follow_campaign_plan.py tests/test_wikidata_nat_live_follow_executor.py tests/test_wikidata_cli.py -k 'live_follow_campaign or live_follow_execute'`
    -> `9 passed`
- Added [SensibLaw/src/ontology/wikidata_nat_live_follow_campaign.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/ontology/wikidata_nat_live_follow_campaign.py)
  and extended [SensibLaw/cli/__main__.py](/home/c/Documents/code/ITIR-suite/SensibLaw/cli/__main__.py),
  [SensibLaw/tests/test_wikidata_nat_live_follow_campaign_plan.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_live_follow_campaign_plan.py),
  and [SensibLaw/tests/test_wikidata_cli.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_cli.py)
  so the pinned Nat live-follow campaign can now be emitted as one bounded
  per-target execution plan through `sensiblaw wikidata nat-live-follow-campaign`.
  Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_wikidata_nat_live_follow_campaign.py tests/test_wikidata_nat_live_follow_campaign_plan.py tests/test_wikidata_cli.py -k 'live_follow_campaign'`
    -> `5 passed`
- Added [SensibLaw/docs/planning/wikidata_nat_live_follow_campaign_20260403.md](/home/c/Documents/code/ITIR-suite/SensibLaw/docs/planning/wikidata_nat_live_follow_campaign_20260403.md),
  [SensibLaw/tests/fixtures/wikidata/wikidata_nat_live_follow_campaign_20260403.json](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/fixtures/wikidata/wikidata_nat_live_follow_campaign_20260403.json),
  and [SensibLaw/tests/test_wikidata_nat_live_follow_campaign.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_live_follow_campaign.py)
  to pin the first bounded multi-category Nat live-follow campaign. The
  campaign explicitly spans hard grounding, split-heavy business-family rows,
  reconciled non-business variance, policy-risk live preview, missing
  instance-of typing deficits, and unreconciled instance-of split-axis cases,
  while keeping source order local-first and hop limits capped at two.
  Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_wikidata_nat_live_follow_campaign.py`
    -> `2 passed`
- Extended [SensibLaw/src/ontology/wikidata_nat_cohort_d_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/ontology/wikidata_nat_cohort_d_review.py),
  [SensibLaw/tests/test_wikidata_nat_cohort_d_operator_report.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_cohort_d_operator_report.py),
  and [SensibLaw/tests/test_wikidata_nat_cohort_d_review_control_index.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_cohort_d_review_control_index.py)
  so the Wikidata/Nat cohort-D operator report and review control index now
  expose a read-only `workflow_summary` with the next bounded review mode.
  Nat packet consumers can now see whether the next move is unresolved packet
  reference cleanup, queued typing review, or simple record-state capture
  without reconstructing that from queue counts alone. Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_wikidata_nat_cohort_d_operator_report.py tests/test_wikidata_nat_cohort_d_review_control_index.py tests/test_wikidata_nat_cohort_d_operator_review_surface.py tests/test_wikidata_nat_cohort_d_review_lane.py`
    -> `8 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `5 passed`
- Extended [SensibLaw/scripts/build_gwb_public_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/scripts/build_gwb_public_review.py),
  [SensibLaw/scripts/build_gwb_broader_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/scripts/build_gwb_broader_review.py),
  [SensibLaw/tests/test_gwb_public_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_gwb_public_review.py),
  and [SensibLaw/tests/test_gwb_broader_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_gwb_broader_review.py)
  so GWB review payloads now expose a read-only `workflow_summary` with the
  next recommended operator view. Public and broader GWB review slices can now
  tell downstream consumers whether the next move is legal-follow, source-row
  review, or simple record-state capture. Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_gwb_public_review.py tests/test_gwb_broader_review.py`
    -> `8 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `5 passed`
- Extended [SensibLaw/src/fact_intake/review_bundle.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/fact_intake/review_bundle.py),
  [SensibLaw/src/fact_intake/au_review_bundle.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/fact_intake/au_review_bundle.py),
  [SensibLaw/schemas/fact.review.bundle.v1.schema.yaml](/home/c/Documents/code/ITIR-suite/SensibLaw/schemas/fact.review.bundle.v1.schema.yaml),
  [SensibLaw/tests/test_fact_review_bundle_component.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_fact_review_bundle_component.py),
  and [SensibLaw/tests/test_au_fact_review_bundle.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_au_fact_review_bundle.py)
  so shared fact-review bundles can now carry a read-only `workflow_summary`
  directly on the bundle envelope. AU bundles now expose the same
  recommended-view / stage guidance that previously only existed in the full
  workbench. Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_fact_review_bundle_component.py tests/test_au_fact_review_bundle.py tests/test_legal_follow_graph.py`
    -> `17 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `5 passed`
- Extended [tests/test_cross_adopter_governance.py](/home/c/Documents/code/ITIR-suite/tests/test_cross_adopter_governance.py)
  so the root suite gate now also asserts cross-lane uncertainty and
  prioritization surfaces for:
  - AU authority-follow
  - GWB legal-follow
  - Wikidata/Nat grounding depth
  - `chat-export-structurer` archive search
  This keeps ranked follow queues, grounding-gap triage, and archive
  bounded-search signals suite-governed instead of repo-local only. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `5 passed`
- Extended [chat-export-structurer/src/archive_search_follow.py](/home/c/Documents/code/ITIR-suite/chat-export-structurer/src/archive_search_follow.py)
  and [chat-export-structurer/tests/test_archive_search_follow.py](/home/c/Documents/code/ITIR-suite/chat-export-structurer/tests/test_archive_search_follow.py)
  so archive-search derived products now expose bounded-search pressure
  signals instead of only result counts. The raw and normalized artifacts now
  report `search_bounds_status`, and the normalized product also reports an
  `uncertainty_surface` with `local_archive_sufficient` and a bounded
  `recommended_next_bound`. Validation:
  - from repo root:
    `PYTHONPATH=chat-export-structurer/src .venv/bin/python -m pytest -q chat-export-structurer/tests/test_archive_search_follow.py`
    -> `3 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `4 passed`
- Extended [SensibLaw/src/ontology/wikidata_grounding_depth.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/ontology/wikidata_grounding_depth.py)
  and [SensibLaw/tests/test_wikidata_nat_grounding_depth.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_wikidata_nat_grounding_depth.py)
  so the Wikidata/Nat grounding priority surface now distinguishes
  `grounding_gap_class` and `recommended_follow_scope` instead of only
  exposing row order. The top-level priority surface now also reports
  `gap_class_counts`, `missing_field_counts`, `recommended_follow_scope_counts`,
  and `highest_priority_score` for bounded grounding-breadth triage. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_nat_grounding_depth.py`
    -> `15 passed`
- Extended [SensibLaw/src/fact_intake/au_review_bundle.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/fact_intake/au_review_bundle.py)
  and [SensibLaw/tests/test_au_fact_review_bundle.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_au_fact_review_bundle.py)
  so AU authority-follow no longer exposes a descriptive queue only. Queue
  items now carry `priority_score`, `priority_rank`, and `authority_yield`,
  and the authority-follow summary now reports `priority_band_counts`,
  `highest_priority_score`, and `highest_authority_yield` for bounded
  uncertainty-collapse triage. Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_au_fact_review_bundle.py tests/test_legal_follow_graph.py`
    -> `13 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `4 passed`
- Extended [SensibLaw/src/policy/gwb_legal_follow_graph.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/policy/gwb_legal_follow_graph.py),
  [SensibLaw/tests/test_gwb_public_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_gwb_public_review.py),
  and [SensibLaw/tests/test_gwb_broader_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_gwb_broader_review.py)
  so the GWB/Brexit legal-follow control plane no longer exposes a flat queue
  only. Queue items now carry `priority_score`, `priority_rank`, and
  `authority_yield`, and the operator summary now reports
  `priority_band_counts`, `highest_priority_score`, and
  `highest_authority_yield` for bounded uncertainty-collapse triage. Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_gwb_public_review.py tests/test_gwb_broader_review.py`
    -> `8 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `4 passed`
- Extended [tests/test_cross_adopter_governance.py](/home/c/Documents/code/ITIR-suite/tests/test_cross_adopter_governance.py) so the root suite gate now also asserts bounded legal-follow control-plane behavior for:
  - AU legal-follow operator view
  - GWB legal-follow operator view
  This keeps the new `follow.control.v1` surfaces from silently regressing back
  to graph-only summaries. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `4 passed`
- Extended `SensibLaw/src/policy/legal_follow_graph.py`,
  `SensibLaw/src/fact_intake/au_review_bundle.py`,
  `SensibLaw/tests/test_legal_follow_graph.py`, and
  `SensibLaw/tests/test_au_fact_review_bundle.py` so AU legal-follow no
  longer stops at graph summary only. The AU bundle now emits a bounded
  `follow.control.v1` operator view plus queue items over derived legal follow
  targets such as the UK/British follow target. Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_legal_follow_graph.py tests/test_au_fact_review_bundle.py`
    -> `13 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `4 passed`
- Extended `SensibLaw/src/ontology/wikidata_grounding_depth.py` and
  `SensibLaw/tests/test_wikidata_nat_grounding_depth.py` so the Wikidata/Nat
  grounding-depth lane now emits a ranked
  `sl.wikidata_review_packet.grounding_depth_priority_surface.v0_1`. The new
  surface highlights which packets still need revision-locked evidence,
  exposes missing fields and priority score, and recommends bounded follow
  against `revision_locked_evidence` instead of leaving incomplete grounding as
  a flat summary only. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_nat_grounding_depth.py`
    -> `15 passed`
- Extended `SensibLaw/src/policy/gwb_legal_follow_graph.py`,
  `SensibLaw/tests/test_gwb_public_review.py`, and
  `SensibLaw/tests/test_gwb_broader_review.py` so the GWB/Brexit legal-follow
  operator view now emits a bounded `follow.control.v1` plane plus queue items
  over followed legal sources instead of remaining graph-only. Brexit-related
  legal URLs now route through explicit bounded targets such as
  `uk_legislation_follow` and `eur_lex_follow`. Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_gwb_public_review.py tests/test_gwb_broader_review.py`
    -> `8 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py`
    -> `4 passed`
- Refined `normalized_artifact_join.py`,
  `schemas/itir.normalized.artifact.join.v1.schema.json`, and
  `tests/test_normalized_artifact_join.py` so the root join now emits a small
  `compatibility.uncertainty_surface` summary with dominant unresolved
  pressure, priority rank, and a bounded-search recommendation. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Extended `tests/test_cross_adopter_governance.py` with a bounded
  local-first follow helper/assertion so retrieval/follow artifacts are
  explicitly checked for:
  - `derived_inspection` authority
  - visible trigger/scope/stop fields
  - bounded local-first follow posture
  Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Extended `StatiBaker/sb/drift.py`, `StatiBaker/tests/test_drift.py`, and
  `StatiBaker/DRIFT_SIGNALS.md` so `StatiBaker` now emits a read-only
  `context_dominance` drift signal with `dominant_thread_fraction` and
  `dominant_thread_id` counters when one thread dominates large-corpus state.
  Validation:
  - from `StatiBaker`:
    `../.venv/bin/python -m pytest -q tests/test_drift.py tests/test_time_hygiene.py`
    -> `4 passed`
- Added `docs/planning/suite_bounded_search_uncertainty_collapse_20260403.md`
  and updated the root control docs so the next suite-level driver is now
  explicitly bounded search and uncertainty collapse over existing
  proving-ground lanes and large corpora, rather than further adapter
  proliferation for its own sake.
- Refined `normalized_artifact_join.py`,
  `schemas/itir.normalized.artifact.join.v1.schema.json`, and
  `tests/test_normalized_artifact_join.py` so the root join now also emits a
  `severity_summary` map and `highest_severity` rollup above the existing
  incompatibility policy surfaces. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Refined `normalized_artifact_join.py`,
  `schemas/itir.normalized.artifact.join.v1.schema.json`, and
  `tests/test_normalized_artifact_join.py` so the root join now also emits a
  small `dominant_disposition` summary above the existing named
  incompatibility policy surfaces. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Refined `normalized_artifact_join.py`,
  `schemas/itir.normalized.artifact.join.v1.schema.json`, and
  `tests/test_normalized_artifact_join.py` so the root join now emits
  per-code `policy_guidance` strings above named incompatibility records and
  disposition counts. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Added `tircorder-JOBBIE/integrations/chat_history_follow.py` and
  `tircorder-JOBBIE/tests/test_chat_history_follow.py` so `tircorder-JOBBIE`
  now has a producer-owned chat-history follow helper plus a
  suite-normalized `derived_product` wrapper over bounded conversation
  discovery results. Validation:
  - from repo root:
    `PYTHONPATH=tircorder-JOBBIE .venv/bin/python -m pytest -q tircorder-JOBBIE/tests/test_chat_history_follow.py`
    -> `4 passed`
- Refined `normalized_artifact_join.py`,
  `schemas/itir.normalized.artifact.join.v1.schema.json`, and
  `tests/test_normalized_artifact_join.py` again so the root join now emits a
  `policy_summary` over named incompatibility dispositions in addition to the
  named incompatibility records themselves. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Added `chat-export-structurer/src/archive_search_follow.py` and
  `chat-export-structurer/tests/test_archive_search_follow.py` so
  `chat-export-structurer` now has a producer-owned bounded archive-search
  follow helper plus a suite-normalized `derived_product` wrapper over FTS
  search results. Validation:
  - from repo root:
    `PYTHONPATH=chat-export-structurer/src .venv/bin/python -m pytest -q chat-export-structurer/tests/test_archive_search_follow.py`
    -> `3 passed`
- Refined `normalized_artifact_join.py`,
  `schemas/itir.normalized.artifact.join.v1.schema.json`, and
  `tests/test_normalized_artifact_join.py` so the root join now emits
  structured `named_incompatibilities` records with explicit `code`,
  `severity`, `artifacts`, `reason`, and `disposition` fields in addition to
  the existing compatibility summary. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Added `reverse-engineered-chatgpt/re_gpt/retrieval_follow.py`,
  extended `reverse-engineered-chatgpt/re_gpt/cli.py`, and added
  `reverse-engineered-chatgpt/tests/test_retrieval_follow.py` so
  `reverse-engineered-chatgpt` now has a producer-owned bounded
  conversation-list follow helper plus a suite-normalized `derived_product`
  wrapper for opt-in `--list` retrieval flows. Validation:
  - from repo root:
    `PYTHONPATH=reverse-engineered-chatgpt .venv/bin/python -m pytest -q reverse-engineered-chatgpt/tests/test_retrieval_follow.py`
    -> `4 passed`
- Refined `normalized_artifact_join.py`,
  `schemas/itir.normalized.artifact.join.v1.schema.json`, and
  `tests/test_normalized_artifact_join.py` so the root bounded join now emits
  clearer compatibility and incompatibility signals instead of only raw role
  mixing. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Refined `StatiBaker/sb/suite_normalized_artifact.py` and
  `StatiBaker/tests/test_suite_normalized_artifact.py` so compiled-state
  exports enforce the exported `context_envelope_ref` path more strictly while
  keeping the canonical compiled-state artifact first in lineage. Validation:
  - from `StatiBaker`:
    `../.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact.py`
    -> `3 passed`
- Added `openrecall/openrecall/retrieval_follow.py` and
  `openrecall/tests/test_retrieval_follow.py` so OpenRecall now has a
  dedicated producer-owned retrieval/follow helper that reuses the existing
  normalized search-follow contract rather than inventing a parallel derived
  shape. Validation:
  - from `openrecall`:
    `../.venv/bin/python -m pytest -q tests/test_normalized_artifact.py tests/test_retrieval_follow.py`
    -> `6 passed`
- Added `normalized_artifact_join.py`,
  `schemas/itir.normalized.artifact.join.v1.schema.json`, and
  `tests/test_normalized_artifact_join.py` so the root repo now has a
  bounded read-only join/composition seam for normalized artifacts that
  preserves lineage, unresolved-pressure counts, and compatibility flags
  rather than collapsing producer roles. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py tests/test_normalized_artifact_join.py`
    -> `7 passed`
- Added `chat-export-structurer/src/context_envelope.py`,
  `chat-export-structurer/src/__init__.py`, and
  `chat-export-structurer/tests/test_context_envelope.py` so archive exports
  now share one producer-owned context-envelope helper instead of hardcoded
  envelope IDs/kinds. Validation:
  - from `chat-export-structurer`:
    `../.venv/bin/python -m pytest -q tests/test_context_envelope.py`
    -> `3 passed`
- Extended `StatiBaker/sb/suite_normalized_artifact.py` and
  `StatiBaker/tests/test_suite_normalized_artifact.py` so compiled-state
  exports retain the canonical compiled-state artifact ID in lineage and
  accept explicit context-envelope refs more cleanly. Validation:
  - from `StatiBaker`:
    `../.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact.py`
    -> `3 passed`
- Added `pyThunderbird/thunderbird/follow.py`,
  extended `pyThunderbird/thunderbird/mail_cmd.py`, and added
  `pyThunderbird/tests/test_follow.py` so `pyThunderbird` now emits bounded
  retrieval-follow artifacts for `--mailid-like` searches plus a normalized
  `derived_product` wrapper via `--normalized-artifact-out`. Validation:
  - from repo root:
    `PYTHONPATH=pyThunderbird .venv/bin/python -m pytest -q pyThunderbird/tests/test_follow.py`
    -> `2 passed`
- Extended `tests/test_cross_adopter_governance.py` so the root governance
  gate now covers join semantics and `pyThunderbird` retrieval-follow
  normalization in addition to the existing legal/archive families.
- Added `tircorder-JOBBIE/tircorder/normalized_source_sidecar.py` so
  TiRCorder can emit one producer-owned normalized `source_artifact` sidecar
  aligned to the root `itir.normalized.artifact.v1` schema without replacing
  canonical capture storage. Validation:
  - manual smoke:
    `python tircorder/normalized_source_sidecar.py --artifact-id smoke.capture.1 --source-path README.md --output /tmp/tircorder-normalized-sidecar.json`
    -> emitted normalized sidecar JSON
- Added `notebooklm-py` bounded retrieval posture via
  `notebooklm research follow`, which emits one non-authoritative derived
  follow artifact over completed NotebookLM research output. Validation:
  - from `notebooklm-py`:
    `PYTHONPATH=src ../.venv/bin/python -m pytest -q tests/unit/cli/test_helpers.py`
    -> `66 passed`
  - `../.venv/bin/python -m py_compile src/notebooklm/cli/helpers.py src/notebooklm/cli/research.py`
    -> passed
- Added `tests/test_cross_adopter_governance.py` so the root suite now pins
  derived-graph, promotion-gate, and unique-derived-role invariants across AU
  and GWB normalized artifacts. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py tests/test_cross_adopter_governance.py`
    -> `4 passed`
- Tightened `StatiBaker/sb/suite_normalized_artifact.py` so the compiled-state
  writer can carry an explicit `context_envelope_ref` through the
  normalized-artifact export path without changing the underlying reducer.
- Widened `itir-svelte` normalized-artifacts inspection so it now consumes
  explicit-path `chat-export-structurer` archive artifacts and explicit-path
  `tircorder-JOBBIE` capture/source artifacts through the same read-only
  normalized contract surface. Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py tests/test_suite_normalized_artifact_schema.py`
    -> `4 passed`
  - from `itir-svelte`:
    `npm run check`
    -> still fails only on unrelated pre-existing
       `graphs/wiki-timeline-aoo-all/+page.svelte` errors
- Added a producer-owned root normalized wrapper for `notebooklm-py`
  research-follow output and widened `itir-svelte` normalized-artifacts
  inspection to consume explicit-path retrieval/research artifacts through the
  same read-only normalized contract surface. Validation:
  - from `notebooklm-py`:
    `PYTHONPATH=src ../.venv/bin/python -m pytest -q tests/unit/cli/test_helpers.py`
    -> `67 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py tests/test_suite_normalized_artifact_schema.py`
    -> `4 passed`
  - from `itir-svelte`:
    `npm run check`
    -> still fails only on unrelated pre-existing
       `graphs/wiki-timeline-aoo-all/+page.svelte` errors
- Added a producer-owned root normalized conversation/source wrapper for
  `reverse-engineered-chatgpt` single-target downloads and widened
  `itir-svelte` normalized-artifacts inspection to consume explicit-path
  live-conversation/source artifacts through the same read-only contract
  surface. Validation:
  - from `reverse-engineered-chatgpt`:
    `python -m pytest -q tests/test_storage.py tests/test_cli.py`
    -> `23 passed`
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_cross_adopter_governance.py tests/test_suite_normalized_artifact_schema.py`
    -> `4 passed`
  - from `itir-svelte`:
    `npm run check`
    -> still fails only on unrelated pre-existing
       `graphs/wiki-timeline-aoo-all/+page.svelte` errors
- Added a bounded `SL-reasoner` contract+adapter seam without extracting any
  substantive deterministic logic out of `SensibLaw`. `SensibLaw` AU
  fact-review now emits `semantic_context.reasoner_input_artifact`,
  `SL-reasoner` now validates read-only reasoner input artifacts and can emit
  derived reasoning artifacts, and the boundary docs now explicitly say this
  is a deferred seam rather than a refactor mandate.
- Clarified the suite-level `SL-reasoner` posture in
  `SL-reasoner/README.md`, `SL-reasoner/docs/interfaces.md`, and the root
  roadmap/readme/TODO/context docs: it remains an optional
  interpretive/non-authoritative scaffold, while substantive deterministic
  engine work continues in `SensibLaw` for now. The repo should stay low
  priority until core complexity grows enough that extraction into
  `SL-reasoner` becomes materially useful.
- Updated the suite-level roadmap/readme/context docs so older
  domain-specific proving grounds no longer control the top-level priority
  order. The suite is now explicitly product-stack-first: capture/archive,
  state, review/promotion, operator/integration, retrieval/bounded-follow,
  then additional domain adopters in the correct owning repos.
- Added
  `docs/planning/suite_p0_completion_roadmap_20260402.md`,
  `schemas/itir.normalized.artifact.v1.schema.json`,
  `examples/itir.normalized_artifact.minimal.json`, and
  `tests/test_suite_normalized_artifact_schema.py` so the new suite-level P0
  moonshot now has one machine-readable normalized artifact contract, one
  focused validation gate, and one explicit worker-lane completion roadmap.
  Validation:
  - `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py`
    -> `3 passed`
- Updated `SensibLaw/src/fact_intake/au_review_bundle.py`,
  `SensibLaw/src/policy/suite_normalized_artifact.py`,
  `SensibLaw/schemas/fact.review.bundle.v1.schema.yaml`, and
  `SensibLaw/tests/test_au_fact_review_bundle.py` so the AU fact-review
  bundle now emits one `semantic_context.suite_normalized_artifact` payload
  aligned to the root `itir.normalized.artifact.v1` schema.
  Validation:
  - from `SensibLaw`:
    `../.venv/bin/python -m pytest -q tests/test_au_fact_review_bundle.py`
    -> `6 passed`
- Added `StatiBaker/sb/suite_normalized_artifact.py`,
  `StatiBaker/tests/test_suite_normalized_artifact.py`, and updated
  `StatiBaker/scripts/bundle_export.py` plus `StatiBaker/BUNDLE_SPEC.md` so
  StatiBaker bundle exports now emit `suite_normalized_artifact.json` as a
  first real `compiled_state` adopter aligned to the root
  `itir.normalized.artifact.v1` schema.
  Validation:
  - from repo root:
    `.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact_schema.py`
    -> `3 passed`
  - from `StatiBaker`:
    `../.venv/bin/python -m pytest -q tests/test_suite_normalized_artifact.py tests/test_bundle.py`
    -> `4 passed`
- Added `itir-svelte/src/lib/server/normalizedArtifacts.ts` and
  `/graphs/normalized-artifacts` so the operator layer now reads normalized
  artifacts from `SensibLaw` and `StatiBaker` directly without local
  reinterpretation.
  Validation:
  - from `itir-svelte`:
    `npm run check`
    -> still fails only on unrelated pre-existing
       `graphs/wiki-timeline-aoo-all/+page.svelte` errors
- Added `chat-export-structurer/src/suite_normalized_artifact.py` and updated
  `chat-export-structurer/src/ingest.py` so archive ingestion can emit one
  producer-owned suite normalized archive sidecar via
  `--normalized-artifact-out`.
  Validation:
  - from `chat-export-structurer`:
    `../.venv/bin/python -m pytest -q tests/test_ingest.py tests/test_cli.py tests/test_suite_normalized_artifact.py`
    -> `5 passed`
- Added
  `docs/planning/suite_p0_moonshot_normalized_concepts_20260402.md`
  and updated the root README/TODO/context so the current capture, archive,
  state, legal, retrieval, and operator plans are now explicitly treated as
  stepping stones under a new suite-level P0 moonshot with shared normalized
  concepts, stronger suite-wide control language, and explicit
  no-unbounded-follow governance.
- Added
  `docs/planning/suite_smart_journal_moonshot_and_invariants_20260402.md`
  and updated root README/TODO/context so the moonshot is now framed at the
  whole-suite level again: capture, archive, canonicalization, state
  compilation, review/promotion, derived products, and bounded union, with
  explicit constraints, invariants, preconditions, and postconditions.
- AU legal-follow graph slice:
  - Added
    `docs/planning/legal_moonshot_au_follow_graph_and_panopticon_boundary_20260402.md`
    to freeze the legal-moonshot read around AU case follow, supporting
    legislation / cited instrument understanding, derived legal-follow graph
    surfaces, and explicit anti-panopticon boundaries.
  - Added `SensibLaw/docs/red_team_anti_panopticon.md` and linked it from
    `SensibLaw/docs/panopticon_refusal.md` so anti-panopticon red-team checks
    are now explicit for the legal-expansion lane.
  - Updated `README.md` and
    `docs/planning/itir_sensiblaw_service_architecture_plantuml_20260328.puml`
    so the root repo now points directly at the compiler-shaped moonshot,
    the anti-panopticon boundary, and the promotion-core / derived-graph
    separation.
  - Added `SensibLaw/src/policy/legal_follow_graph.py` as the first bounded AU
    derived legal-follow graph builder.
  - Updated `SensibLaw/src/au_semantic/semantic.py` so AU authority-receipt
    context now emits structured `legal_ref_details`,
    `candidate_citation_details`, and legal-ref class counts for downstream
    legal-follow consumers.
  - Updated `SensibLaw/src/fact_intake/au_review_bundle.py` so AU
    fact-review bundles now emit `semantic_context.legal_follow_graph`,
    `operator_views.legal_follow_graph.summary`, and richer
    `authority_follow` packet detail rows for reference-class inspection.
  - Refined `SensibLaw/src/policy/legal_follow_graph.py` so the derived graph
    now distinguishes `case_ref`, `supporting_legislation`, and
    `cited_instrument` surfaces while staying derived-only and challengeable.
  - Updated `SensibLaw/src/policy/compiler_contract.py` so AU
    fact-review bundles now declare `legal_follow_graph` as an explicit
    derived product.
  - Extended
    `SensibLaw/tests/test_legal_follow_graph.py`,
    `SensibLaw/tests/test_compiler_contract.py` and
    `SensibLaw/tests/test_au_fact_review_bundle.py`.
  - Refined `SensibLaw/src/policy/legal_follow_graph.py` again so shared
    nodes merge richer receipt/conjecture metadata instead of keeping the
    first sparse version, and supporting-legislation / cited-instrument /
    citation / authority-receipt surfaces now retain more inspectable
    provenance.
  - Refined `SensibLaw/src/policy/legal_follow_graph.py` again so
    attachment-bearing graph nodes accumulate bounded supporting event and
    supporting receipt provenance where available.
  - Extended `SensibLaw/tests/test_legal_follow_graph.py` to pin merged
    receipt/citation metadata on the derived graph surface.
  - Extended `SensibLaw/tests/test_legal_follow_graph.py` again to pin
    supporting event / supporting receipt provenance on shared graph nodes.
  - Froze the next bounded AU legal round as a dual slice:
    deeper attachment provenance plus read-only legal-follow graph exposure in
    the fact-review workbench, with no change to the derived-only /
    anti-panopticon posture.
  - Extended `SensibLaw/src/policy/legal_follow_graph.py` so the derived
    graph summary now reports supporting receipt counts and supporting
    authority-kind counts for downstream inspection.
  - Updated `SensibLaw/src/policy/legal_follow_graph.py` so supporting
    legislation nodes now expose `supporting_legislation_roles` plus
    `supporting_legislation_role_counts` for enabling/constraining/procedural/amending context.
  - Updated `itir-svelte/src/lib/server/factReview.ts` and
    `itir-svelte/src/routes/graphs/fact-review/+page.svelte` so the
    fact-review workbench now surfaces one read-only derived legal-follow
    graph inspection pane from `semantic_context.legal_follow_graph`, with
    summary, authority/receipt, ref/citation, and typed-link sections.
  - Added `SensibLaw/src/policy/gwb_legal_follow_graph.py` as the first
    bounded derived GWB legal-linkage graph helper.
  - Updated `SensibLaw/scripts/build_gwb_public_review.py` and
    `SensibLaw/scripts/build_gwb_broader_review.py` so those review products
    now emit `legal_follow_graph`.
  - Updated the existing GWB review summaries so they now expose a bounded
    "Derived Legal-Linkage Graph" section without inventing a separate UI
    lane.
  - Updated `SensibLaw/src/policy/compiler_contract.py` so GWB public-review
    and broader-review contracts now list `legal_linkage_graph` as an
    explicit derived product.
  - Extended `SensibLaw/tests/test_gwb_public_review.py` and
    `SensibLaw/tests/test_gwb_broader_review.py` to pin the new graph surface
    and derived-product roles.
  - Extended `SensibLaw/tests/test_au_fact_review_bundle.py` to pin the new
    graph summary counts at the AU bundle boundary.
  - Updated `SensibLaw/src/au_semantic/semantic.py` again so AU legal-ref
    details now also carry bounded `jurisdiction_hint` and
    `instrument_kind` semantics.
  - Updated `SensibLaw/src/fact_intake/au_review_bundle.py` so
    `authority_follow` now exposes jurisdiction and instrument-kind counts in
    both queue items and summary payloads.
  - Updated `SensibLaw/src/fact_intake/au_review_bundle.py` again so
    `authority_follow` now also exposes bounded `ref_kind_counts` in queue
    items and summary payloads.
  - Updated `SensibLaw/src/fact_intake/au_review_bundle.py` again so
    `authority_follow` now also exposes bounded `citation_court_hint_counts`
    and `citation_year_counts` in queue items and summary payloads.
  - Updated `SensibLaw/src/policy/legal_follow_graph.py` so supporting
    legislation and cited instrument nodes/edges now preserve those
    jurisdiction/instrument hints and report bounded summary counts for them.
  - Updated `SensibLaw/src/policy/legal_follow_graph.py` again so the AU
    legal-follow summary now also reports bounded `reference_kind_counts`,
    `reference_class_counts`, `ref_kind_counts`, `edge_kind_counts`,
    `edge_reference_class_counts`, and `edge_ref_kind_counts`.
  - Updated `SensibLaw/src/policy/legal_follow_graph.py` again so the AU
    legal-follow summary now also reports bounded
    `citation_court_hint_counts` and `citation_year_counts`.
  - Extended `SensibLaw/tests/test_legal_follow_graph.py`,
    `SensibLaw/tests/test_au_fact_review_bundle.py`, and
    `SensibLaw/tests/test_au_fact_review_script.py` to pin the richer AU
    legal-ref semantics.
  - The fact-review legal-follow pane is now typed to render bounded
    distribution grids when a derived legal-follow graph exposes them, which
    keeps the AU and GWB read-only operator posture aligned.
  - Updated `SensibLaw/scripts/build_gwb_public_review.py` and
    `SensibLaw/scripts/build_gwb_broader_review.py` again so their markdown
    summaries now expose bounded `Graph inspection` and `Sample typed links`
    sections for read-only legal-linkage inspection.
  - Updated `SensibLaw/src/policy/gwb_legal_follow_graph.py`,
    `SensibLaw/scripts/build_gwb_public_review.py`, and
    `SensibLaw/scripts/build_gwb_broader_review.py` so GWB review payloads
    now also expose one bounded JSON `operator_views.legal_follow_graph`
    surface with summary, highlight-node, and sample-edge inspection data.
  - Extended `SensibLaw/tests/test_gwb_public_review.py` and
    `SensibLaw/tests/test_gwb_broader_review.py` to pin those richer GWB
    summary surfaces.
  - Validation:
    - focused AU+GWB/compiler gate: `25 passed`
    - touched modules `py_compile` clean
    - `itir-svelte` `npm run check` still fails only on the pre-existing
      `wiki-timeline-aoo-all/+page.svelte` errors
- fact-review operator workflow slice:
  - Added `docs/planning/fact_review_operator_workflow_slice_20260402.md`.
  - Updated `SensibLaw/src/fact_intake/read_model.py` so the persisted
    fact-review workbench now emits `semantic_context` and one derived
    `workflow_summary` block.
  - Updated `itir-svelte/src/routes/graphs/fact-review/+page.svelte` and
    `itir-svelte/src/lib/server/factReview.ts` so the fact-review route now
    shows the current workflow stage, recommended next view, suggested fact
    focus, and compact pressure counts.
  - Updated focused backend tests in
    `SensibLaw/tests/test_fact_intake_read_model.py` and
    `SensibLaw/tests/test_query_fact_review_script.py`.
  - Validation:
    - backend focused gate: `30 passed`
    - `read_model.py` `py_compile` clean
    - repo-wide `npm run check` still fails on unrelated pre-existing
      `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`
      errors
- moonshot compiler gate slice:
  - Added `SensibLaw/src/policy/product_gate.py` as the first reusable
    `promote | abstain | audit` decision layer above normalized
    `compiler_contract` payloads.
  - Adopted the gate in AU public handoff, AU fact-review bundle, GWB public
    handoff, GWB public review, GWB broader review, and the Wikidata migration
    pack so each now emits a common decision record without rewriting lane
    semantics.
  - Updated `SensibLaw/schemas/fact.review.bundle.v1.schema.yaml` and the
    focused adopter tests to pin the gate at the payload boundary.
  - Added outcome/validation status to
    `docs/planning/promote_abstain_audit_gate_slice_20260402.md`, `TODO.md`,
    `SensibLaw/todo.md`, and `COMPACTIFIED_CONTEXT.md`.
  - Validation:
    - `28 passed`
    - touched modules `py_compile` clean
- moonshot compiler normalization reconsideration:
  - Added
    `docs/planning/moonshot_compiler_normalization_reconsideration_20260402.md`
    to restate the moonshot read in compiler/product terms across AU, GWB,
    and Wikidata/Nat.
  - Updated `docs/planning/judgment_architecture_lane_split_20260402.md`,
    `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the next orchestration phase
    centers on bounded evidence-group -> promoted-outcome contracts and
    lane-normalized product surfaces, with graph remaining derived rather than
    the organizing truth layer.
  - Reaffirmed the one-worker-per-lane split and current promotion order:
    `Ramanujan`, `Erdos`, `Lorentz`, `Euler`, `Ohm`, `Huygens`.
  - Re-read the checkpoint and kept the same split and order with no reshuffle.
  - Added an explicit note that no further allocation change is justified at
    this checkpoint and the next valid move is implementation promotion.
  - Rechecked the same moonshot orchestration checkpoint again with no change
    in lane ownership or promotion order.
  - Added one more explicit repeated-checkpoint note: still no lane or order
    change, still no new evidence requiring a reshuffle.
  - Added an explicit endpoint note: further docs-only reaffirmation would now
    be repetition rather than new governance signal.
  - Recorded the convergence point explicitly: the lane-order conflict is
    resolved, the controlling note is stable, and the only honest next move is
    implementation promotion under the same worker ownership.
  - Resolved the remaining doc-order ambiguity by making the compiler/product
    normalization note the controlling lane-order source and aligning the
    judgment-support note behind `Ramanujan`, `Erdos`, `Lorentz`, `Euler`,
    `Ohm`, `Huygens`.
  - Added an explicit docs-freeze note for this checkpoint: no more docs-only
    orchestration updates unless new lane evidence materially changes the
    worker ownership, promotion order, or contract scope.
  - Added an explicit user-override note: a user-requested reaffirmation may
    append a no-change checkpoint without reopening the frozen worker split or
    promotion order.
- Wikidata moonshot gap lane split:
  - Added `SensibLaw/docs/planning/wikidata_nat_grounding_depth_evidence_20260402.md`,
    `SensibLaw/docs/planning/wikidata_nat_cohort_b_review_bucket_20260402.md`,
    `SensibLaw/docs/planning/wikidata_nat_cohort_c_live_preview_extension_20260402.md`,
    `SensibLaw/docs/planning/wikidata_nat_cohort_d_review_lane_20260402.md`,
    `SensibLaw/docs/planning/wikidata_nat_cohort_e_reconciliation_scan_plan_20260403.md`,
    and `SensibLaw/docs/planning/wikidata_nat_automation_graduation_criteria_20260402.md`
    so the current gap-to-moonshot program now resolves into explicit lane-local
    artifacts rather than only roadmap language.
  - Added the first bounded runtime/test surfaces for the new non-company axis:
    `SensibLaw/src/ontology/wikidata_nat_cohort_b_review_bucket.py`,
    `SensibLaw/tests/test_wikidata_nat_cohort_b_review_bucket.py`,
    `SensibLaw/tests/test_wikidata_cohort_c_live_preview_extension.py`,
    `SensibLaw/tests/test_wikidata_nat_cohort_d_review_lane.py`, and
    `SensibLaw/tests/test_wikidata_nat_grounding_depth.py`.
- Wikidata moonshot helper tranche:
  - Added executable bounded helpers for the current moonshot-gap lanes:
    `SensibLaw/src/ontology/wikidata_grounding_depth.py`,
    `SensibLaw/src/ontology/wikidata_nat_cohort_b_operator_packet.py`,
    `SensibLaw/src/ontology/wikidata_nat_cohort_d_review.py`,
    `SensibLaw/src/ontology/wikidata_cohort_e_diagnostics.py`, and
    `SensibLaw/src/ontology/wikidata_nat_automation_graduation.py`.
  - Added matching docs/fixtures/tests for the richer Cohort C operator
    evidence packet, Cohort D type-probing surface, Cohort E diagnostics
    helper, and fail-closed graduation evaluator.
- Wikidata moonshot operator-surface tranche:
  - Added a grounding-depth attachment surface, a pinned Cohort B operator
    packet surface, a Cohort D operator review queue surface, and the report
    builder above the automation graduation evaluator.
  - Validated the operator-facing Nat moonshot helper suite at `21 passed`.
- Wikidata moonshot reproducible artifact tranche:
  - Added the grounding-depth batch artifact, a deterministic Cohort C
    operator report, a Cohort E diagnostics CLI/report lane, and the
    automation-graduation operator CLI.
  - Validated the focused report/artifact tranche at `15 passed, 24 deselected`.
- Wikidata moonshot reproducible batch/report tranche:
  - Added a grounding-depth CLI plus batch review-packet report,
    a Cohort B operator report, a Cohort C operator-report batch surface,
    a Cohort D operator report plus CLI, a Cohort E diagnostics batch report,
    and automation-graduation batch proposal evaluation.
  - Updated the moonshot roadmap/status/TODO/context surfaces so the current
    gap now points at measured operator evidence rather than more packet-shape
    expansion.
- Wikidata moonshot broader measured-evidence tranche:
  - Added a grounding-depth evidence report, a Cohort B deterministic
    operator batch report, a broader Cohort C measured-evidence sample, a
    Cohort D operator report batch plus CLI, a Cohort E grouped diagnostics
    summary, and an automation-graduation repeated-run evidence report.
  - Updated the moonshot roadmap/status/TODO/context surfaces so the next
    gap-closing step is explicitly broader measured evidence over multiple
    cases rather than more one-off examples.
- Wikidata moonshot broader operator/governance tranche:
  - Added a grounding-depth comparison/index report, a Cohort B operator
    evidence index, a Cohort C operator index, a Cohort D review-control
    index, a Cohort E summary index, and an automation-graduation governance
    index over repeated evidence snapshots.
  - Updated the moonshot roadmap/status/TODO/context surfaces so the next
    gap-closing step is explicitly broader operator/governance evidence over
    repeated runs rather than only more batch outputs.
- Wikidata Shixiong handoff:
  - Added
    `SensibLaw/docs/planning/wikidata_shixiong_handoff_20260402.md`
    as a short plain-language onboarding note for the current climate
    migration + Nat reviewer-packet lane.
  - Updated `SensibLaw/docs/wikidata_working_group_status.md`, `TODO.md`, and
    `COMPACTIFIED_CONTEXT.md` so the handoff is discoverable from the main
    Wikidata status surfaces.
- Wikidata blind-migration moonshot framing:
  - Updated `SensibLaw/docs/planning/wikidata_nat_end_product_and_tiered_automation_20260401.md`
    and the matching status/TODO/context surfaces so the repo now says
    explicitly that a blind migration bot is the P0 moonshot for the Nat lane.
  - Kept the current operating posture honest: review-first, split-first, and
    fail-closed until the smaller automation tiers prove stable enough to earn
    that moonshot.
- Wikidata reviewer-packet variant comparison:
  - Added a bounded variant-comparison lane to the Nat reviewer-packet plan
    and contract so targeted cross-variant inspection can reduce uncertainty
    without becoming a hidden truth engine.
  - Added a grounded sibling-variant comparison path so the Nat packet can
    compare real cohort peers from the same split-plan family, not just
    abstract examples, and derive that bounded comparison automatically when
    sibling plans are present in the split payload.
- Wikidata reviewer-packet helper lanes:
  - Added standalone helper modules and tests for follow depth,
    claim-boundary mapping, cross-source alignment, reviewer actions, and
    bounded variant comparison so the reviewer-packet lane now has explicit
    bounded sub-lanes, and wired those helpers into the optional semantic
    sidecar.
- major user-story alignment and reprioritization pass:
  - Added
    `docs/planning/user_story_alignment_and_reprioritization_20260402.md`
    to freeze the first post-substrate story-fit read across the suite.
  - Updated `TODO.md`, `SensibLaw/todo.md`, and `COMPACTIFIED_CONTEXT.md` so
    the active priority order now favors guided workflow UX, annotation/QA
    workbench depth, and direct feedback evidence over further broad substrate
    refactoring.
- manifest runtime substrate:
  - Added `SensibLaw/src/storage/manifest_runtime.py` as the shared owner for
    repo-owned manifest-path resolution and top-level JSON-object loading.
  - Adopted it first in
    `SensibLaw/src/fact_intake/acceptance_fixtures.py` and
    `SensibLaw/scripts/source_pack_manifest_pull.py`.
  - Added `SensibLaw/tests/test_manifest_runtime.py` and extended the
    acceptance-wave and source-pack tests to pin the new shared owner.
- revision-monitor path residue cut:
  - Added `docs/planning/wiki_revision_monitor_path_residue_cut_20260402.md`
    to freeze the last small schema contraction before the user-story pass.
  - Updated `SensibLaw/src/wiki_timeline/revision_pack_runner.py` so
    `timeline_path` and `aoo_path` are removed from article-state and
    article-result storage, including old-DB rebuilds.
  - Extended `SensibLaw/tests/test_wiki_revision_pack_runner.py` to pin the
    narrower schema and migration boundary.
- revision-monitor final tiny path-residue cut:
  - Added `docs/planning/wiki_revision_monitor_path_residue_cut_20260402.md`
    to freeze the last small schema/contract cleanup still worth landing
    before the user-story sweep.
- manifest-root normalization slice:
  - Added `docs/planning/manifest_root_normalization_slice_20260402.md` to
    freeze the first bounded manifest-path/manifest-load owner slice after the
    repo-root substrate work.
- shared repo-root structural script adoption:
  - Added `docs/planning/repo_roots_structural_script_adoption_20260402.md`
    to freeze the next tested adoption slice after the runtime collapse.
  - Switched
    `SensibLaw/scripts/build_wikidata_structural_handoff.py`,
    `SensibLaw/scripts/build_wikidata_structural_review.py`,
    `SensibLaw/scripts/build_wikidata_dense_structural_review.py`, and
    `SensibLaw/scripts/build_gwb_broader_corpus_checkpoint.py` to consume the
    canonical root helpers in `SensibLaw/src/storage/repo_roots.py`.
  - Extended the focused Wikidata structural and broader checkpoint tests to
    pin `repo_root()` / `sensiblaw_root()` adoption.
- shared repo-root bootstrap collapse:
  - Added `docs/planning/repo_roots_runtime_collapse_20260402.md` to freeze
    the final collapse of the duplicate script bootstrap helper.
  - Extended `SensibLaw/src/storage/repo_roots.py` so it now owns both the
    canonical repo-root helpers and the remaining script-file-based root
    resolution helpers.
  - Switched the remaining adopters in
    `SensibLaw/scripts/report_wiki_random_timeline_readiness.py`,
    `SensibLaw/scripts/report_wiki_random_article_ingest_coverage.py`, and
    `SensibLaw/scripts/run_fact_semantic_benchmark_matrix.py`, then removed
    `SensibLaw/src/storage/repo_runtime.py` and its duplicate test file.
- Wikidata orchestration posture clarification:
  - Updated `SensibLaw/docs/wikidata_working_group_status.md`,
    `SensibLaw/docs/planning/wikidata_review_packet_plan_20260401.md`,
    `SensibLaw/docs/planning/wikidata_nat_end_product_and_tiered_automation_20260401.md`,
    `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the repo now says explicitly
    that when a work surface is wide enough, the preferred shape is one
    nonblocking lane per worker with disjoint ownership rather than a single
    serialized runner.
  - This keeps the Nat review/split lane aligned with the existing
    review-first posture while making parallel orchestration an explicit
    documented option instead of an implicit practice.
- Wikidata assist-lane reviewer-packet alignment:
  - Added `docs/planning/wikidata_assist_lane_packet_fixture_note_20260402.md`
    and updated `docs/planning/wikidata_assist_lane_reviewer_packet_alignment_20260401.md`
    so the Peter/Ege/Rosario lane now has an explicit smallest-fixture note in
    addition to the alignment note.
  - Updated `SensibLaw/docs/wikidata_working_group_status.md` and `TODO.md`
    so the shared docs point to the new assist-lane fixture note instead of
    leaving it implicit.
- Wikidata reviewer-packet semantic sidecar:
  - Added `docs/planning/wikidata_review_packet_semantic_layer_20260402.md`
    and extended `SensibLaw/src/ontology/wikidata.py` so the deeper semantic
    layer now lives behind `include_semantic_decomposition=True` without
    changing the default shallow packet contract.
  - Added `SensibLaw/tests/test_wikidata_review_packet_semantics.py` and
    updated the packet docs so the repo now says explicitly that the new layer
    is a separate sidecar above/beside `parsed_page`, not a replacement for
    it.
  - The sidecar now publishes anchor-derived reviewer units plus explicit
    bounded follow-receipt units, explicit missing-evidence gap units, plus
    explicit split-review context units (merged split axes + recommended
    actions), so reviewers can rely on the layer without assuming
    `parsed_page` is already full semantic decomposition.
- Nat reviewer-packet coverage expansion:
  - Expanded `SensibLaw/tests/fixtures/wikidata/wikidata_nat_review_packet_attachment_coverage_20260401.json`
    and the matching planning note to `15 / 53` packetized rows after adding
    `Q1785637` and `Q738421` as additional wider-online reviewed rows on top of
    `Q10416948` and `Q56404383` as sidecar-backed pilot-pack packets and
    `Q731938` as a third packetized held row.
  - Clarified that the packet coverage lane is now near diminishing returns and
    only genuinely new split shapes should justify another attachment record.
- Cohort C scan normalizer:
  - Added a bounded runtime normalizer for the pinned non-GHG / missing `P459`
    Cohort C sample fixture so the branch now has a review-first runtime
    surface without implying that a live population scan has already run.
  - Added a bounded live scan preview helper using the same selection rule, so
    Cohort C now has a live-query-backed review-first runtime surface without a
    blanket execution lane.
  - Added an operator packet wrapper over the Cohort C preview so the decision
    state, triage prompts, and fail-closed behavior are explicit.
  - Added a CLI entrypoint for the Cohort C operator packet so reviewers can
    export a saved-scan packet or request a bounded live preview in one call.
- revision-monitor provenance boundary clarification:
  - Added
    `docs/planning/wiki_revision_monitor_provenance_path_boundary_20260401.md`
    to freeze the post-JSON/post-path read on provenance and sharing.
  - Updated
    `SensibLaw/docs/wiki_revision_pack_runner_contract_v0_3.md`,
    `docs/planning/wiki_revision_monitor_no_routine_json_reports_20260401.md`,
    `docs/planning/wiki_revision_monitor_path_contract_demotion_20260401.md`,
    `TODO.md`, `SensibLaw/todo.md`, and `COMPACTIFIED_CONTEXT.md` so the repo
    now says explicitly that local path fields are not truth, and that trusted
    sharing should resolve through logical artifact identity, revision,
    digest, sink refs, and acknowledgement/receipt semantics rather than local
    JSON/path assumptions.
- shared repo/runtime helper narrowing:
  - Added `SensibLaw/src/storage/repo_runtime.py` as the bounded helper home
    for script-file-based `repo_root` / `SensibLaw_root` resolution and
    repo-relative path normalization.
  - Adopted it in
    `SensibLaw/scripts/report_wiki_random_timeline_readiness.py`,
    `SensibLaw/scripts/report_wiki_random_article_ingest_coverage.py`, and
    `SensibLaw/scripts/run_fact_semantic_benchmark_matrix.py`.
  - Added `SensibLaw/tests/test_repo_runtime.py` and validated the focused
    adopter gate.
- shared repo-root substrate:
  - Added `SensibLaw/src/storage/repo_roots.py` as the shared owner for repo
    root and SensibLaw root resolution plus repo-relative path helpers.
  - Adopted it first in `SensibLaw/scripts/build_gwb_corpus_scorecard.py`,
    `SensibLaw/scripts/source_pack_manifest_pull.py`,
    `SensibLaw/scripts/source_pack_authority_follow.py`,
    `SensibLaw/scripts/report_wiki_random_timeline_readiness.py`, and
    `SensibLaw/scripts/report_wiki_random_article_ingest_coverage.py`.
  - Added `SensibLaw/tests/test_repo_roots.py` and verified the first adopter
    set with the report and scorecard regression gates.
- shared reviewer-packet geometry substrate:
  - Added `SensibLaw/src/review_geometry/reviewer_packets.py` as the shared
    owner for queue-item normalization and packet-summary counts.
  - Adopted it first in `SensibLaw/src/fact_intake/control_plane.py`.
  - Added a focused planning note and tests for deterministic queue-item
    geometry.
- shared provenance / receipt geometry substrate:
  - Added `SensibLaw/src/policy/provenance_packet_geometry.py` as the shared
    owner for receipt rows and packet-header normalization.
  - Adopted it first in `SensibLaw/src/reporting/narrative_compare.py` and
    `SensibLaw/src/fact_intake/handoff_artifacts.py`.
  - Added a focused planning note for the new packet geometry contract.
- shared SQLite runtime substrate:
  - Added `SensibLaw/src/storage/sqlite_runtime.py` as the shared owner for
    repo-relative SQLite path resolution and connection plumbing.
  - Adopted it first in `SensibLaw/src/wiki_timeline/query_runtime.py`,
    `SensibLaw/scripts/query_wiki_timeline_aoo_db.py`, and
    `SensibLaw/scripts/query_fact_review.py`.
  - Added `SensibLaw/tests/test_sqlite_runtime.py` to pin explicit-path and
    read-only connection behavior.
- revision-monitor dead-path schema drop:
  - Added
    `docs/planning/wiki_revision_monitor_dead_path_schema_drop_20260401.md`
    to freeze the next schema-contraction slice after the no-routine-JSON cut.
  - Updated `SensibLaw/src/wiki_timeline/revision_pack_runner.py` so fresh
    revision-monitor schema and old-DB rebuilds drop `report_path`,
    `pair_report_path`, and `graph_path` from the dead compatibility surfaces.
  - Updated `SensibLaw/src/wiki_timeline/revision_monitor_read_models.py` so
    the read-model schema also rebuilds out dead report/graph path columns.
  - Extended `SensibLaw/tests/test_wiki_revision_pack_runner.py` and
    `SensibLaw/tests/test_revision_monitor_read_models.py` to pin the in-place
    rebuild boundary, with the focused revision-monitor gate still green.
- revision-monitor no-routine-json-report slice:
  - Added
    `docs/planning/wiki_revision_monitor_no_routine_json_reports_20260401.md`
    to freeze the export posture after the SQLite-first contraction work.
  - Updated `SensibLaw/src/wiki_timeline/revision_pack_runner.py` so the
    default runner path no longer writes pair-report JSON or contested-graph
    JSON, and no longer advertises those paths in the returned article/pair
    summary surface.
  - Updated `SensibLaw/src/wiki_timeline/revision_pack_summary.py` so
    pack-triage and human-summary output stop carrying report/graph path
    fields as if they were routine operator contract.
  - Updated `SensibLaw/tests/test_wiki_revision_pack_runner.py` and
    `SensibLaw/tests/test_revision_pack_summary.py` to pin the no-routine-JSON
    default path.
- revision-monitor path contract demotion:
  - Added
    `docs/planning/wiki_revision_monitor_path_contract_demotion_20260401.md`
    to freeze the first narrow post-contraction cleanup slice.
  - Updated
    `SensibLaw/src/wiki_timeline/revision_monitor_read_models.py` so default
    changed-article, selected-pair, selected-graph, and summary top-article
    payloads no longer expose export-path fields as ordinary runtime state.
  - Extended
    `SensibLaw/tests/test_revision_monitor_read_models.py` and
    `SensibLaw/tests/test_revision_monitor_query.py` to pin the demoted
    default payload contract.
  - Verified from `SensibLaw/` with:
    `../.venv/bin/python -m pytest -q tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_wiki_revision_pack_runner.py tests/test_revision_pack_summary.py`
    -> `18 passed`.
- roadmap/state reconciliation followthrough:
  - Updated `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and
    `docs/planning/roadmap_state_reconciliation_20260401.md` so the root
    status no longer overstates the revision-monitor writer side as fully
    artifact-free.
  - Updated
    `docs/planning/chat_context_resolver_refactor_brief_20260328.md`,
    `docs/planning/largest_file_refactor_roadmap_20260328.md`,
    `docs/planning/largest_code_files_refactor_roadmap_20260328.md`, and
    `docs/planning/wiki_timeline_aoo_all_route_refactor_brief_20260328.md`
    so already-landed resolver and wiki-timeline runtime reductions are
    recorded as completed or narrowed rather than still framed as open in their
    old form.
  - Updated
    `SensibLaw/docs/wiki_revision_pack_runner_contract_v0_3.md`,
    `SensibLaw/docs/external_ingestion.md`, and `SensibLaw/todo.md` so the
    revision-monitor lane is described as SQLite-canonical in current posture
    and the stale affidavit normalization umbrella is closed.
- Wikidata reviewer-packet semantic-layer boundary clarification:
  - Updated `SensibLaw/docs/planning/wikidata_review_packet_contract_20260401.md`,
    `SensibLaw/docs/planning/wikidata_review_packet_plan_20260401.md`, and
    `SensibLaw/docs/wikidata_working_group_status.md` so the repo now says
    explicitly that `parsed_page` is only the current shallow surface-parse
    helper, not the full SensibLaw decomposition / contingent-clause layer.
  - Updated `TODO.md` and `COMPACTIFIED_CONTEXT.md` so the next missing layers
    are recorded honestly: broader held-row packet coverage and later
    semantic decomposition, while the initial bounded follow-receipt seam is
    now explicit.
- Wikidata reviewer-packet parser upgrade:
  - Extended `build_wikidata_review_packet(...)` so the first Nat packet now
    carries bounded parsed-page structure:
    section headings, done/to-do task buckets, query rows, and cohort-oriented
    task lines.
  - Refreshed
    `SensibLaw/tests/fixtures/wikidata/wikidata_nat_review_packet_20260401.json`
    to pin the richer parsed-page surface.
  - Extended focused regression coverage in
    `SensibLaw/tests/test_wikidata_projection.py`.
  - Verified with:
    `../.venv/bin/python -m pytest -q tests/test_wikidata_projection.py`
    from `SensibLaw/` (`48 passed`).
- Wikidata reviewer-packet contract / first runtime slice:
  - Added
    `SensibLaw/docs/planning/wikidata_review_packet_contract_20260401.md`
    to pin the machine-readable review-packet contract above
    `sl.source_unit.v1` and `sl.wikidata_split_plan.v0_1`.
  - Added schema
    `SensibLaw/schemas/sl.wikidata_review_packet.v0_1.schema.yaml`.
  - Added `build_wikidata_review_packet(...)` in
    `SensibLaw/src/ontology/wikidata.py` so one revision-locked Nat wiki
    source unit can be attached to one held split plan without widening
    authority.
  - Added pinned fixture
    `SensibLaw/tests/fixtures/wikidata/wikidata_nat_review_packet_20260401.json`
    plus focused regression coverage in
    `SensibLaw/tests/test_wikidata_projection.py`.
  - Verified with:
    `../.venv/bin/python -m pytest -q tests/test_wikidata_projection.py`
    from `SensibLaw/` (`48 passed`).
- Wikidata reviewer-packet bounded follow receipts:
  - `build_wikidata_review_packet(...)` now auto-attaches a bounded follow
    receipt from the Nat query-link surface when one is present, while
    explicit empty receipts remain an opt-out.
  - The Nat packet fixture now pins that query-link receipt and no longer
    advertises `no_follow_receipts` for the default packetized source surface.
  - Focused regression coverage now includes both the auto-derived receipt and
    explicit empty-receipt opt-out behavior.
- Wikidata Nat packet attachment coverage:
  - Added
    `SensibLaw/docs/planning/wikidata_nat_review_packet_attachment_coverage_20260401.md`
    and the machine-readable coverage index
    `SensibLaw/tests/fixtures/wikidata/wikidata_nat_review_packet_attachment_coverage_20260401.json`.
  - The Nat review-packet lane now has a first bounded multi-row attachment
    surface with `10 / 53` packetized held split rows, covering the original
    `Q10403939` packet, a second packetized held row for `Q10422059`, and
    eight wider-online reviewed rows from the live tranche.
- Wikidata assist-lane reviewer-packet alignment:
  - Added `docs/planning/wikidata_assist_lane_reviewer_packet_alignment_20260401.md`
    so the Peter/Ege/Rosario lane can adopt the reviewer-packet grammar
    without overstating parity or completion.
- Wikidata Nat end-product / tiered automation alignment:
  - Added
    `SensibLaw/docs/planning/wikidata_nat_end_product_and_tiered_automation_20260401.md`
    to pin the full intended Nat flow and the honest tiered automation posture:
    full pipeline coverage, but only bounded checked-safe automation where the
    evidence repeatedly justifies it.
  - Added shared handoff/roadmap notes at
    `docs/planning/wikidata_combined_assist_handoff_20260401.md` and
    `docs/planning/wikidata_combined_roadmap_nat_and_assist_20260401.md` so the
    top-level status links now resolve again.
  - Updated Nat-facing status and handoff notes to reflect current reality:
    bounded mainline complete, wider proof lane complete, wider online lane
    held, and reviewer-packet support as the next missing layer.
- Mirror Telegram support-layer boundary:
  - Added `docs/planning/mirror_telegram_support_layer_boundary_20260401.md`
    to freeze the current ITIR posture for the sibling Mirror Telegram work:
    ITIR should not own top-level Telegram routing, but it should own the
    support-layer normalization, disambiguation, parser/model lanes,
    provenance, and labeled fallback discipline that de-brittle routing.
  - Updated `README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md` so the suite
    now records:
    - Mirror route ownership stays local
    - Core AI remains downstream execution rather than route authority
    - Telegram chats are now present in `~/chat_archive.sqlite` for local-first
      follow-up analysis
    - the next bounded followthrough is a classifier-hardening spec in the
      sibling Mirror repo
- roadmap/state reconciliation checkpoint:
  - Updated `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and `SensibLaw/todo.md` to
    reflect the actual substrate state as of `2026-04-01` rather than the
    older pre-contraction snapshot.
  - Froze the current meta-priority explicitly:
    reusable Python/store/runtime substrate first, cross-lane reuse second,
    local cleanup last.
  - Recorded the current pre-user-story sequence explicitly:
    one real roadmap/state reconciliation round, one remaining wiki revision
    monitor contract-cleanup round, and at most one or two more clearly
    high-leverage cross-lane substrate promotions before the broader
    user-story pass.
- Zelph handoff / grant framing alignment:
  - Added `docs/planning/zelph_nlnet_grant_draft_20260401.md` to freeze a
    Stefan-facing lower-bound-deliverable grant draft backed by the resolved
    thread `Strategic Contribution Advice`
    (`69cbf880-05ec-839a-8603-8532ca426638` /
    `b0499d873b1a162931c96a0a8e016b9906da540a`).
  - Updated `docs/planning/zelph_external_handoff_20260320.md` so the bounded
    grant-safe claim is explicit:
    `text -> reviewed facts -> Zelph reasoning -> output`, without implying
    that Zelph becomes a raw-text ingest engine.
  - Updated `docs/planning/zelph_handoff_index_20260324.md` so the grant-ready
    note sits beside the main external handoff reading order.
  - Kept the framing pinned through ZKP, ITIL, ISO 9000, ISO 42001,
    ISO 27001, Six Sigma, and C4/PlantUML rather than leaving the grant note as
    free-floating prose.
- Wikidata review packet plan:
  - Added
    `SensibLaw/docs/planning/wikidata_review_packet_plan_20260401.md` to pin
    the exact next reviewer-assist workflow for Nat/Wikidata split-heavy rows:
    revision capture, bounded parsing, selected follow receipts, and reviewer
    packet attachment.
  - Updated `SensibLaw/docs/wikidata_working_group_status.md` and `TODO.md` so
    the repo now explicitly records that this pass was docs-only and that the
    next work is contract/parser/follow-receipt implementation rather than
    vague “assist” work.
- Wikidata review/split user-story alignment:
  - Added `docs/user_stories.md` story `ITIR-US-17: Wiki Revision Review Assist`
    so the suite now explicitly says ITIR should capture revision-locked wiki
    surfaces, expose refs/links, and reduce reviewer uncertainty without
    turning wiki prose into authority.
  - Strengthened `SensibLaw/docs/user_stories.md` for the `Wikidata editor /
    ontology reviewer` role so ITIR-backed wiki parsing/follow assist is
    explicit.
  - Updated
    `SensibLaw/docs/planning/user_story_implementation_coverage_20260326.md`
    to say this support is partial today: revision-locked proposal capture and
    split verification exist, but generic wiki-page ref/link-follow reviewer
    packets do not yet.
  - Added
    `SensibLaw/docs/planning/wikidata_review_split_assist_user_story_alignment_20260401.md`
    to pin the ZKP/ITIL/ISO 9000/ISO 42001/ISO 27001/Six Sigma/C4 framing for
    that alignment.
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
  - Landed first-class `technical_qualification` / `conceded_fact` response
    handling in:
    - `SensibLaw/scripts/build_affidavit_coverage_review.py`
    - `SensibLaw/src/fact_intake/read_model.py`
  - Added focused regressions in:
    `SensibLaw/tests/test_affidavit_coverage_review.py`
  - Reverified with:
    `.venv/bin/python -m pytest -q SensibLaw/tests/test_affidavit_coverage_review.py SensibLaw/tests/test_query_fact_review_script.py`
    -> `57 passed in 2.44s`
  - Live full Dad/Johl rerun now lands `p2-s21` as:
    - `supports / conceded_fact`
    - matched rebuttal clause:
      `John had failed to complete the necessary steps to revoke his EPOA`
    - retained lineage echo:
      `In August 2024 I took steps to revoke my EPOA`
    - nearby independent confirmation in the same response block:
      `This is corroborated by the dated signature on the revocation documents.`
  - Persisted Dad Court notebook follow-up on the same visible thread agreed:
    - `p2-s21` supports `conceded_fact`
    - best operator-facing label:
      `Conceded Fact (+ Technical Qualification)`
    - next highest-signal refinement:
      strict echo masking for quoted allegation headers / pasted affidavit text
- 2026-04-02: Added
  `docs/planning/judgment_architecture_lane_split_20260402.md` and synced
  `TODO.md`, `SensibLaw/todo.md`, and `COMPACTIFIED_CONTEXT.md` so the next
  execution split is explicitly grounded in reusable judgment architecture
  rather than more default substrate cleanup. The current order is now:
  text bridge first, legal doctrinal primitives second, common
  primitive/comparison architecture third, then Nat grounding depth,
  disciplined graph challengeability, and stronger promotion/audit gates.
- 2026-04-02: Synced the returned judgment-architecture worker briefs into the
  planning/status docs. The confirmed promotion order remains:
  `Ramanujan`, `Erdos`, `Euler`, `Lorentz`, `Ohm`, `Huygens`. The briefs also
  froze the safe boundaries:
  Ramanujan as a pinned additive climate text bridge,
  Erdos as a doctrinal projection layer rather than a semantic-core rewrite,
  and Euler as a very small shared primitive/comparison surface that should be
  derived from those two concrete lanes.
- 2026-04-02: Added the immediate execution checkpoint to the
  judgment-architecture note and synced root/SensibLaw status files:
  promote `Ramanujan` next, keep the remaining lanes assigned in ranked order,
  and only reshuffle if the first implementation slice reveals hidden coupling
  or a stronger bounded promotion.
- 2026-04-02: Reaffirmed the unchanged judgment-architecture orchestration
  state in the planning/status docs:
  same one-lane-per-worker split, same ranked order, and no new selection
  round before the first implementation promotion.
- 2026-04-02: Tightened the Shixiong Wikidata handoff note so it reflects his
  actual fit better: bounded validation, correction-worthiness criteria,
  reviewer-inspectable packet surfaces, and provenance strictness, rather than
  generic migration onboarding.
- Wikidata Nat gap-to-moonshot program is now pinned at
  `SensibLaw/docs/planning/wikidata_nat_gap_to_moonshot_program_20260402.md`,
  making the staged gap from the current review-first lane to the blind
  migration-bot moonshot explicit in ZKP, ITIL, ISO 9000, ISO 42001, ISO
  27001, ISO 27701, ISO 23894, NIST AI RMF, Six Sigma, C4, and PlantUML terms.
- The Nat end-product, working-group status, combined roadmap, and TODO now
  say the same thing about current priorities:
  grounding depth first, non-company structural breadth second, promotion
  gates third, and only then stronger moonshot-readiness claims.
# 2026-04-02

- docs: aligned the moonshot/compiler normalization docs with the current
  completion roadmap and progress read
- docs: recorded the remaining top-priority sequence explicitly:
  shared contract -> AU normalization -> GWB normalization -> reusable
  promote/abstain/audit gate -> operator-grade workflow layer
- docs: removed stale compacted-context ordering residue that conflicted with
  the controlling compiler-shaped frame
- 2026-04-02: Added `docs/planning/shared_evidence_bundle_promoted_outcome_contract_20260402.md`
  and synced root/SensibLaw TODO plus compacted context so the first real
  compiler-contract implementation slice is explicit: one tiny shared
  `compiler_contract` payload, adopted first by AU public handoff, GWB public
  handoff, and Wikidata migration pack, with product-shape normalization only.
- 2026-04-02: Landed the first real shared compiler-contract slice in
  `SensibLaw/src/policy/compiler_contract.py` and adopted it in AU public
  handoff, GWB public handoff, and Wikidata migration pack outputs. Added
  regression coverage in `SensibLaw/tests/test_compiler_contract.py` plus the
  relevant AU/GWB/Wikidata adopter tests.
- 2026-04-02: Added `docs/planning/au_product_normalization_slice_20260402.md`
  and synced TODO plus compacted context so the next bounded lane is explicit:
  emit the shared `compiler_contract` from the AU fact-review bundle via
  `semantic_context.compiler_contract`.
- 2026-04-02: Landed the AU product-normalization slice by adding an AU
  fact-review bundle adapter to `SensibLaw/src/policy/compiler_contract.py`
  and emitting `semantic_context.compiler_contract` from
  `SensibLaw/src/fact_intake/au_review_bundle.py`. Added regression coverage in
  `SensibLaw/tests/test_compiler_contract.py` and
  `SensibLaw/tests/test_au_fact_review_bundle.py`.
# 2026-04-03

- Wikidata/Nat live-follow now implements `named_query_link` in
  `SensibLaw/src/ontology/wikidata_nat_live_follow_executor.py`, resolving
  locally pinned packet query-link surfaces before revision-locked fallback.
  Focused regression coverage landed in
  `SensibLaw/tests/test_wikidata_nat_live_follow_executor.py`, and the
  split-heavy live campaign rerun now resolves both rows through
  `named_query_link` rather than falling back immediately to
  `named_revision_locked_source`.

- 2026-04-02: Added `docs/planning/gwb_product_normalization_slice_20260402.md`
  and synced TODO plus compacted context so the next bounded lane is explicit:
  emit the shared `compiler_contract` from GWB public review and GWB broader
  review.
- 2026-04-02: Landed the GWB product-normalization slice by adding GWB public
  review and broader-review adapters to
  `SensibLaw/src/policy/compiler_contract.py` and emitting `compiler_contract`
  from `SensibLaw/scripts/build_gwb_public_review.py` and
  `SensibLaw/scripts/build_gwb_broader_review.py`. Added regression coverage in
  `SensibLaw/tests/test_compiler_contract.py`,
  `SensibLaw/tests/test_gwb_public_review.py`, and
  `SensibLaw/tests/test_gwb_broader_review.py`.
- 2026-04-02: Added `docs/planning/promote_abstain_audit_gate_slice_20260402.md`
  and synced TODO plus compacted context so the next bounded lane is explicit:
  add one shared gate record above the normalized AU, GWB, and Wikidata
  products.
# 2026-04-02

- Suite product-stack-first business-logic follow-through:
  - `openrecall` now emits a producer-owned normalized `source_artifact`
    sidecar for captured screenshots via
    `openrecall/openrecall/normalized_artifact.py`
  - `openrecall` now also emits a bounded non-authoritative search-follow
    artifact plus a normalized `derived_product` wrapper for local search
    results, keeping retrieval/follow posture explicit and non-canonical
  - focused OpenRecall coverage landed in
    `openrecall/tests/test_normalized_artifact.py`
  - root cross-family governance now includes the OpenRecall capture artifact
  - `StatiBaker` compiled-state normalization now guarantees retention of the
    canonical compiled-state artifact ID in lineage and supports explicit
    `context_envelope_ref` export without changing reducer ownership
- README, legal moonshot planning, TODO, SensibLaw TODO, compacted context,
  and changelog now carry an explicit legal-moonshot progress read and a
  stable end-state operational flow, so “progress vs total” and “what the
  moonshot actually does” are no longer only chat-local.
- GWB legal-linkage graph summaries now expose bounded source-kind,
  source-family, linkage-kind, review-status, and support-kind distributions
  in both public-review and broader-review artifacts so the derived legal
  surface is more inspectable without adding a separate UI lane.
- AU legal-follow graphs now recover bounded supporting-legislation roles
  (`enabling`, `constraining`, `procedural`, delegated-instrument parent,
  `amending`) and report `supporting_legislation_role_counts` without widening
  the truth boundary.
- GWB legal-linkage graphs now add bounded followed-source nodes when
  source-review receipts already carry HTTP links, keeping the surface
  derived-only and review-first rather than introducing open-ended crawling.
- The fact-review workbench now renders the bounded GWB
  `operator_views.legal_follow_graph` surface directly, so GWB legal-linkage
  inspection has real operator-view parity with the existing AU read-only
  graph posture.
- Docs/TODO/context now treat the legal moonshot as normal program state and
  pin the next bounded GWB cohort candidates as previous US presidents and
  UK Brexit-era politicians, still under the anti-panopticon boundary.
- Docs/TODO/context now also pin the next bounded AU cross-jurisdiction step:
  allow one explicit AU -> UK/British follow hop when current evidence already
  points there, while keeping it provenance-backed, derived-only, review-first,
  and explicitly not a general common-law ancestry crawl.
- README, planning, TODO, context, and anti-panopticon red-team docs now also
  elevate Brexit from a mere cohort hint to a named bounded legal-union
  proving ground, while keeping it explicitly non-surveillance and
  review-first.
- AU legal-follow now emits one derived UK/British follow target when current
  receipt/ref/citation evidence already points there, keeping the hop
  provenance-backed, review-first, and non-recursive.
- GWB legal-linkage now classifies followed-source legal URLs into bounded
  cite classes and reports Brexit-related follow counts where the existing
  source text/URLs already carry that pressure.
- GWB legal-linkage can now also seed followed-source receipts from the
  canonical foundation-source catalog when a review row already names a known
  UK/EU legal source, which gives the Brexit proving ground a bounded
  non-crawling legal-cite follow path.
