# TODO (ITIR-suite)

## Last assessed
- 2026-03-26

## Submodule TODO snapshot
- SensibLaw: S6 in progress with S6.5 external consumer contracts stubbed; near-term focus on schema freezes, sprint selection, Sprint 9 UI hardening, ingestion discipline tasks, and bounded citation-follow expansion; Sprint S7 checklist targets API/CLI projections, golden tests, and red-flag guards.
- SL-reasoner: no TODOs found.
- tircorder-JOBBIE: accessibility TODOs (extend ARIA roles/labels, add `aria-live`, automate audits, expand manual testing).
- Web transition:
  - treat `itir-svelte/` as the sole intended web interface
  - keep `tircorder-JOBBIE/Pelican/` and `tircorder-JOBBIE/Zola/` as
    reference-only during migration
  - do not add new product-facing web work to Pelican/Zola; port needed
    behavior into `itir-svelte/` and delete legacy surfaces later
- WhisperX-WebUI: README TODO list appears complete; translation PRs requested.
- reverse-engineered-chatgpt: README TODOs remaining (better error handling, improve documentation); TODO.md items all completed.
- chat-export-structurer: no TODOs found.
- StatiBaker: pending work across intent/scope, temporal reduction rules (carryover/new/resolved), atom/handle definitions, integration adapters for TIRC/SL/ITIR refs, and guard tests that prevent content summarization.
- notebooklm-py:
  - keep a bounded live E2E smoke path healthy (`auth check --test` + readonly
    notebook/query smoke) before attempting broader network/generation runs
  - ensure the local test environment actually carries NotebookLM dev test deps
    (`pytest-asyncio`, `pytest-timeout`) in the repo-root `.venv` before
    treating E2E failures as API/auth issues
- NotebookLM suite standardization:
  - DONE: bounded live smoke in the repo-root `.venv`
  - DONE: first metadata/review parity slice via producer-owned observer
    read-model/query helpers and source-summary text-unit projection
  - DONE: define and implement the bounded NotebookLM interaction lane
    (`conversation_observed`, `note_observed`, separate normalized signal,
    query/read-model helpers, no dashboard session claims)
  - next: decide whether a later interaction-grade capture/session contract
    should be sourced from richer NotebookLM events or remain review-only
  - later: define a separate interaction-grade NotebookLM activity contract
    before treating NotebookLM as a first-class SB usage lane
- Chatistics: no TODOs found.
- pyThunderbird: no TODOs found.

## Active TODOs
## Priority legend
- [P0] Blocking / core platform correctness
- [P1] Near-term platform capability unlocks
- [P2] Important but deferrable
- [P3] Nice-to-have / polish

- [P1] Workspace coordination boundary discipline:
  - use `docs/planning/workspace_coordination_boundary_20260327.md` as the
    current control-plane decision
  - keep suite-level coordination, promotion rules, and cross-repo TODOs in
    `ITIR-suite`
  - keep repo-local contracts and implementation notes in the owning repos
    such as `dashi_agda` and `FRACDASH`
  - do not create a new top-level coordination project directory unless the
    new surface has its own runtime/build or transport boundary
  - when a new adapter/product lane is justified, prefer a bounded
    subproject inside `ITIR-suite` first, following the existing `itir-mcp`
    pattern

- [P1] Cross-repo user-story + feedback receipt lane:
  - use `docs/planning/repo_user_story_state_and_feedback_20260327.md` as the
    current cross-repo audit baseline
  - use `docs/planning/feedback_receipt_contract_20260327.md` as the canonical
    receipt contract for persisted user feedback evidence
  - keep the distinction explicit between:
    - story-derived / proxy frustrations
    - actual user interview / usability receipts
  - add a bounded feedback-receipt contract for:
    - competitor/workflow frustrations
    - frustrations with our current surfaces
    - likes/delight/retention signals
  - DONE: first bounded persisted receiver + query surface in `itir.sqlite`
    for `feedback.receipt.v1`
  - DONE: first capture helpers/import seams via
    `SensibLaw/scripts/query_fact_review.py`:
    - `feedback-add`
    - `feedback-import`
  - DONE: first collector-facing UI capture surface in
    `itir-svelte /corpora/processed/personal`
    over the canonical receiver:
    - one-receipt add form
    - JSONL paste/import form
    - recent receipt cards
  - DONE: first bounded source-linked drill-ins from feedback receipts back to
    internal surfaces/workbenches where the receipt already names or safely
    implies one
  - DONE: provenance-first receipt drill-ins now prefer stronger canonical
    refs where present:
    - canonical thread id
    - fact-review selector refs
    - internal route refs
  - DONE: the collector UI now captures stronger canonical refs explicitly:
    - canonical thread id
    - fact-review selector refs
  - next: improve collector/operator UX beyond raw field entry / JSONL paste,
    and extend explicit capture to more canonical object families where
    product/value justifies it
  - use the receipts to prioritize:
    - product-flow smoothing in `itir-svelte`
    - SB operator ergonomics
    - capture/transcription setup friction
    - cross-product handoff clarity

- [P1] Cross-source follow/review control-plane parity:
  - use `SensibLaw/docs/planning/cross_source_follow_control_plane_20260327.md`
    as the current portable queue/control-plane contract
  - DONE: first shared `follow.control.v1` control plane now exists in
    `SensibLaw/src/fact_intake/control_plane.py`
  - DONE: first concrete adopters now span more than one lane:
    - AU `authority_follow`
    - generic fact-review `intake_triage`
    - generic fact-review `contested_items`
  - DONE: `itir-svelte /graphs/fact-review` now renders these
    control-plane-backed queues generically instead of treating AU authority
    follow as a one-off renderer
  - next: extend the same portable queue grammar to the next real unresolved
    source families rather than cloning AU-specific semantics:
    - transcript/message follow-needed queues
    - affidavit/source-review queues
    - other bounded corpus/workbench operator queues with real unresolved work

- [P1] itir-svelte a11y coverage expansion:
  - extend rendered-DOM label/state assertions across remaining graph/workbench routes
  - add keyboard navigation/focus/activation tests for transcript/document/folder viewers and graph controls
  - add one axe-based browser smoke for `/viewers/hca-case` and primary graph routes
  - keep Pelican/Zola reference-only; direct new UI work/testing to itir-svelte
- [P1] SensibLaw authority retrieval operator seam:
  - DONE: document the canonical bounded workflow in
    `SensibLaw/docs/sources_contract.md`,
    `SensibLaw/docs/cli_examples.md`, and
    `SensibLaw/docs/user_stories.md`
  - DONE: add repo-owned CLI paths for:
    - AustLII search/fetch -> local paragraph-indexed inspection
    - JADE known-citation/url fetch -> local paragraph-indexed inspection
    - JADE best-effort search -> fetch -> local paragraph-indexed inspection
  - DONE: add fixture-backed tests and live-opt-in canary coverage for both
    seams, plus adapter/url-contract coverage for JADE MNC resolution
  - DONE: split mixed source tests/helpers so generic paragraph and authority
    logic no longer sits behind AustLII-named modules/files
  - DONE: implement the now-approved direct AustLII known-authority seam so
    neutral citations can resolve deterministically to canonical AustLII case
    URLs without going through SINO
  - DONE: extend bounded citation-follow to use AustLII search as the last
    resort after JADE exact MNC and deterministic AustLII case-URL derivation
  - DONE: expose the AU authority-follow operator queue in
    `itir-svelte /graphs/fact-review` for AU selectors by bridging the AU
    `demo-bundle` operator view rather than widening the generic persisted
    fact-review workbench contract
- [P1] Agent test-loop ledger followthrough:
  - keep `docs/planning/agent_test_loop.md` check-ins restricted to completed loops with exact commands and terminal outcomes
  - finish or explicitly retire the lanes currently recorded as starts only:
    - `Codex-Lumen`
    - `Antigravity-Loom`
    - `Antigravity-Pulse`
    - `Antigravity-Nova`
    - `Antigravity-Archive`
    - `Antigravity-Flux-Wiki`
  - if `Antigravity-Titan` is kept as a completed lane, rerun and record the exact
    `SensibLaw` / `StatiBaker` slice commands that justify the pass counts rather
    than only the benchmark matrix command
- [P1] Shared SL reducer adoption across products:
  - use `sensiblaw.interfaces.shared_reducer` as the supported cross-product
    lexer/reducer API
  - migrate first real runtime consumer paths in SB, TiRC, and ITIR-facing UI
    from doc-only boundary assumptions to adapter-backed canonical refs
  - keep any local tokenizer/indexing heuristics explicitly non-canonical
  - add cross-product guard tests so no product imports SL tokenizer internals
    directly for runtime integration
  - make adapter-produced tokenizer profile / canonical refs visible in
    receipts, overlays, or read models where cross-product preservation matters
  - for future text/graph/lexer bridges, require the Dashifine-style staging:
    - canonical shared state first
    - reversible serialization second
    - conservative baseline graph/overlay third
    - informative non-local graph/overlay scoring last
  - bridge guardrail checklist (keep visible for reviewers):
    - [ ] single canonical source record identified
    - [ ] reversible serializer exercised in tests/fixtures
    - [ ] baseline graph/overlay emits provenance and is replayable
    - [ ] non-local graph variant justified by semantic/window signal, not
          just density/connectivity lift
    - [ ] scoring rule prefers semantic/provenance agreement over raw graph
          lift
    - [ ] overlay outputs labelled `derived_only` in adapters/config
  - do not treat higher graph density/connectivity by itself as bridge success;
    require semantic/provenance usefulness criteria too
  - keep the product boundary explicit in docs and adapters:
    - `TextGraphs`-style layers stay non-canonical analytical/diagnostic or
      candidate-producing overlays
    - canonical semantic/provenance truth begins only at promotion
    - do not let SL reducer work drift into a generic token-graph clone
  - architecture governance followthrough from
    `docs/architecture/admissibility_lattice.md`:
    - type lattice levels explicitly where contracts are still near-canonical
      or informal
    - formalize promotion contracts as the sole path to truth-bearing records
    - formalize supersession instead of silent promoted-record mutation
    - enforce downstream consumer discipline around overlays vs promoted state
    - label non-canonical overlays explicitly in cross-project adapters
  - DONE: add compact `TextGraphs` x `SensibLaw` bridge note:
    `docs/planning/textgraphs_sl_bridge_contract_20260324.md`
  - clarify the bridge doctrine explicitly:
    `TextGraphs` proposes, `SensibLaw` promotes, `Zelph` reasons
  - keep the two SL lanes distinct in future docs and adapters:
    - canonical reducer lane = authority substrate
    - spaCy lane = auxiliary interpretation
  - if a future text-graph layer is added on the SL side, mark it explicitly
    as `derived_only` and keep it outside the canonical reducer contract; add a
    per-adapter toggle/field so overlays cannot be consumed without opt-in
- [P2] SensibLaw x Glasslane / Mirror packaging slice:
  - use chat thread `Aptos cryptocurrency overview`
    (`691ac8a3-4a30-8320-bd5f-f66efc3145e7`,
    canonical `dff5b29b89818300e7e352c0247c4cef3823bcfd`) as the current
    product-positioning source
  - package SensibLaw/TiRC for Mirror as the missing `human risk layer` rather
    than as a competing crypto research assistant
  - keep the stage/market read explicit in any packaging draft:
    - Mirror / Glasslane currently reads as tiny, founder-led, pre-PMF, and
      Discord/chatbot-first rather than as a mature institutional product
    - claimed professional buyers should be treated separately from the visible
      retail/KOL-style community mix
    - NFT/token monetization ideas in the source thread increase the value of a
      provenance/governance-first counterposition
  - draft product-facing materials for:
    - `Crypto Consumer Harm Observatory (CCHO)`
    - `Risk & Behavioural Pattern Analytics` for exchanges/wallets
    - `High-Trust Explainability Layer` for boards/regulators
  - define the minimum reusable Ribbon stream-layer surface for this pitch:
    - Ribbon remains the named operator-facing surface / embed target
    - stream types for finance, conversation, obligation, and other
      timeline-aligned conserved/derived signals feed Ribbon
    - change-point / pattern-event outputs
    - provenance-safe API/export surfaces for partner embedding
  - keep crypto/regtech positioning focused on provenance, guardrails, and
    explainable pattern detection instead of generic market commentary
- [P1] Mary-parity fact-management roadmap (new top SL-facing priority):
  - use `docs/planning/mary_parity_roadmap_20260315.md` as the planning source
    for near-term SL execution
  - archived context inputs resolved on 2026-03-18:
    - `69b90f8b-3cf8-839c-bffe-b7da95565338` / `Zelph 0.9.5 Update`
      -> tiny deterministic SL -> Zelph bridge demo
    - `69b9f131-bb3c-839c-b2cd-233b4af8c72a` / `Branch · Zelph 0.9.5 Update`
      -> Stefan-facing upstream-positioning refinement
    - `69b75a97-6784-839b-bc2b-3824717279e0` / `ITIR SensibLaw Model`
      -> formalization plus file-search fallback for partial snippets
    - `69b7e167-53d8-839d-a9e6-56b239746525` / `Governance Model Mapping`
      -> explicit operator mapping for convergence/proof/ZK reasoning
    - `69b7e164-d0a8-839d-8418-41769163ba6d` / `Formal Model Application`
      -> state-compiler / prototype application over uploaded files
    - `69ba8956-35b8-839b-9707-f8c91c2b02dd` /
      `Ambiguity of "Community"`
    - `69ba8c55-163c-839d-86b9-6c366a8dc29a` /
      `Formal Model to Engine`
      -> keep ingest/lexer/compression state/lattice/gap roles explicit
    - `69b7eb5b-0c78-839d-9012-a484905fdf0c` / `Model Mapping to Casey`
      -> keep Casey state/lattice/governance boundaries explicit
    - `69ba3af2-5df8-839b-bd8a-7c865be0b052` /
      `Casey Git Clone Differences`
      -> emphasize candidate lattice, explicit collapse, workspace selection,
         and immutable build projections in Casey-facing docs/adapters
  - Zelph external collaboration followthrough:
    - use `docs/planning/zelph_external_handoff_20260320.md` as the canonical
      Stefan-facing repo note
    - use `docs/planning/wikidata_zelph_single_handoff_20260325.md` as the
      canonical first-link handoff when the audience spans both the Wikidata
      Ontology Working Group and Zelph
    - real-first rule:
      synthetic fixtures are regression/contract material only and should not
      be used as the headline Zelph/demo evidence when real run-derived
      artifacts exist
    - canonical pack spec/manifest now live in:
      `docs/planning/zelph_real_world_pack_v1_20260324.md`,
      `docs/planning/zelph_real_world_pack_v1.manifest.json`
    - outward-facing promotion pack now lives in:
      `docs/planning/zelph_real_world_pack_v1_5_20260324.md`,
      `docs/planning/zelph_real_world_pack_v1_5.manifest.json`
    - current broader-companion pack now lives in:
      `docs/planning/zelph_real_world_pack_v1_6_20260325.md`,
      `docs/planning/zelph_real_world_pack_v1_6.manifest.json`
    - next public-entity handoff spec now live in:
      `docs/planning/gwb_zelph_handoff_v1_20260324.md`
    - GWB completeness note now live in:
      `docs/planning/gwb_completeness_scorecard_20260324.md`
    - AU checked handoff + completeness notes now live in:
      `docs/planning/au_zelph_handoff_v1_20260324.md`,
      `docs/planning/au_completeness_scorecard_20260324.md`
    - DONE: keep the outward-facing handoff wording behavior-level rather than
      role-label-driven (reversion detection / volatility /
      reversion-without-context risk, not a formal `wiki sentinel` ontology
      claim)
    - prepare a deliberately shareable Zelph pack:
      - DONE: lead with the deterministic DB/rule-atom export path (`SensibLaw/sl_zelph_demo/compile_db.py`, `db_rules.zlp`, `db_run.sh`, `tests/test_sl_zelph_demo_tools.py`) so Zelph devs see the authoritative handoff
      - DONE: canonical V1 scope is the safer 2-slice pack:
        `itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`
        plus
        `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`
      - keep the ranked transcript bundles as internal/next-pack candidates:
        `itir-svelte/tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json`,
        `itir-svelte/tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json`
      - document an ontology/predicate-as-node example (`SensibLaw/sl_zelph_demo/ontology_demo.zph`, `ontology_rules.zlp`, `lex_to_zelph.py`) to demonstrate richer schema exports
      - keep the wiki/review run only as bounded historical context, not as the
        headline case
      - include only reviewed/sanitized real artifacts and scripts/tests that
        verify the export story
      - next recommended artifact after canonical V1:
        GWB public-entity handoff using the reviewed linkage seed plus the
        deterministic linkage and semantic report surfaces
      - DONE: first checked GWB handoff artifact now exists as both prose and
        machine-readable outputs under
        `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`
      - DONE: AU now has parity checked outputs under
        `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`
      - DONE: first broader GWB checkpoint now exists under
        `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
      - DONE: public-bios broader-source input is no longer title-only;
        `SensibLaw/scripts/build_gwb_public_bios_rich_timeline.py` now builds
        `SensibLaw/demo/ingest/gwb/public_bios_v1/wiki_timeline_gwb_public_bios_v1_rich.json`
- [P1] Zelph partial-load / HF manifest promotion harness:
  - use `docs/planning/zelph_partial_load_harness_20260326.md` as the harness contract
  - keep `tools/run_zelph_partial_load_harness.py` as the acceptance runner for:
    - direct `.bin` selector health
    - manifest selector health
    - fallback detection vs direct chunk-read success
  - run it on `wikidata-20171227-pruned.bin` first; use the 2026 bin as the heavier follow-up lane
  - do not treat manifest chunk transport as promoted until the harness shows direct success without fallback on the relevant selector cases
  - next widen the contract to:
    - `nodeOfName=0`
    - mixed section selectors
  - use `docs/planning/zelph_node_route_sidecar_20260326.md` as the next design source once transport coverage is fully green
        from raw HTML cue-bearing snippets
      - DONE: broader-source diagnostics now live under
        `SensibLaw/tests/fixtures/zelph/gwb_broader_promotion_diagnostics_v1/`
        with builder
        `SensibLaw/scripts/build_gwb_broader_promotion_diagnostics.py`
      - DONE: AU broader diagnostics companion now lives under
        `SensibLaw/tests/fixtures/zelph/au_broader_corpus_diagnostics_v1/`
- [P1] Suite MCP scaffold and SensibLaw-first adapter lane:
  - use `docs/planning/itir_mcp_dioxus_contract_20260326.md` as the governing
    contract
  - create and keep `itir-mcp/` as a root-owned suite adapter project rather
    than embedding MCP transport into producer repos by default
  - first implementation scope:
    - deterministic, read-only tool registry
    - SensibLaw-backed obligation tools only
    - local tests for registry/spec behavior
  - next integration scope:
    - stdio/server transport wiring
    - one Dioxus backend/native client seam
    - reuse existing Dioxus MCP-like playground as a debug/operator surface,
      not the canonical suite transport layer
  - do not:
    - expose broad mutable actions first
    - treat browser `dioxus/web` as a direct stdio MCP host
    - let `itir-mcp` redefine producer semantics or canonical schemas
      - DONE: shared CLI runtime/progress now reaches the deeper Wikidata and
        Wikipedia inner loops too:
        `src/ontology/wikidata.py::find_qualifier_drift_candidates(...)` and
        `src/wiki_timeline/revision_pack_runner.py::run(...)`, with renderer
        coverage in `SensibLaw/tests/test_cli_runtime.py`
        with builder
        `SensibLaw/scripts/build_au_broader_corpus_diagnostics.py`
      - current broader GWB bottleneck:
        public-bios and corpus/book lanes now contribute matched seed support;
        after richer public-bios event shaping plus broader-source seed-backed
        semantic backfill, and after corpus sentence-priority shaping over the
        full `Decision Points` text, they contribute promoted confirmation of
        the existing Supreme Court review relation family and one genuinely new
        broader-source public-law family plus one executive-action family:
        `George W. Bush -> signed -> No Child Left Behind Act`
        and
        `George W. Bush -> signed -> Northwestern Hawaiian Islands Marine National Monument`
        and one new corpus-lane broader relation:
        `George W. Bush -> ruled_by -> Supreme Court of the United States`
      - corpus-book broader confirmation now also includes one already-checked
        legal-action family:
        `George W. Bush -> vetoed -> Stem Cell Research Enhancement Act`
        via a memoir-rooted first-person legal-action path
      - quality guard added:
        father/family-history bare-`Bush` corpus rows now abstain instead of
        silently resolving to George W. Bush
      - next GWB step:
        improve candidate quality, mention/object resolution, and promotion
        readiness for the next broader-source family after Supreme Court review
        + NCLB + marine-monument + the new corpus review/nomination confirms,
        before adding more source files or loosening promotion policy
    - keep the handoff note explicit about current repo-facing Zelph dev contact
      surfaces:
      `sl_zelph_demo/*_run.sh`, `compile_db.py`, `lex_to_zelph.py`,
      `scripts/zelph_runner.py`, `src/zelph_bridge.py`,
      `tests/test_sl_zelph_demo_tools.py`
    - decide whether the first external pack should stay strictly demo-level or
      declare one small formal export contract
    - decide whether uncertainty/probability handling stays purely upstream for
      the first collaboration slice
    - explicit current gap:
      there is not yet a repo-stable real chat-history run artifact strong
      enough for the next Zelph pack; find or prepare one from actual
      chat-history DB runs focused on development/math/general reasoning or
      public events
    - logic-tree artifacts may assist the future chat lane, but they are not
      the canonical first chat demo artifact
    - GWB handoff followthrough:
      - DONE: first checked GWB export is both a reviewed JSON/prose slice and
        a compiled Zelph fact bundle
      - treat the intended destination explicitly as complete GWB/topic
        understanding, not merely a bounded handoff slice
      - keep scoring the current checked artifact as a checkpoint toward that
        destination
      - current checked scorecard lives at:
        `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.scorecard.json`
      - keep the first bounded Zelph rules small:
        `executive_public_law_action` and
        `needs_review_due_to_ambiguity`
      - do not mistake the checked handoff for full GWB completeness:
        broaden future completeness passes to cover the wider in-repo source
        inventory under `SensibLaw/demo/ingest/gwb/`, including public bios,
        corpus timeline material, and book sources
      - build a machine-readable broader GWB corpus scorecard artifact so
        source-family breadth is measured from repo artifacts rather than only
        discussed in prose
      - DONE: first broader GWB corpus scorecard now exists under
        `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`
      - next concrete GWB move:
        build a broader extraction checkpoint over the checked handoff timeline,
        public-bios timeline, and corpus/book timeline so relation coverage is
        measured across real source families rather than only inventoried
      - DONE: first broader GWB extraction checkpoint now exists under
        `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
      - next concrete GWB bottleneck:
        improve broader-source promotion/admissibility because the first wider
        checkpoint added source families but did not add new promoted relations
    - AU handoff followthrough:
      - do not mistake the checked AU workbench slice
        (`SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`) for full AU
        corpus completeness
      - Mary-parity workbench checkpoints prove operator review/handoff quality,
        not exhaustive extraction over a long transcript or larger corpus
      - broaden future AU completeness passes using fuller transcript/corpus
        surfaces such as transcript-semantic runs, transcript fact-review
        bundles, and reviewed WhisperX-derived imports where available
      - build a machine-readable broader AU corpus scorecard artifact so the
        current 3-fact checkpoint is explicitly contextualized inside the wider
        persisted real-bundle lane
      - DONE: first broader AU corpus scorecard now exists under
        `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`
      - DONE: promote the checked GWB artifact into outward-facing Zelph pack
        `v1.5`
      - broaden GWB completeness from the checked slice scorecard to wider
        real-run metrics
    - AU parity followthrough:
      - DONE: bring AU up to the same checked handoff shape as GWB
      - broaden AU completeness from the checked workbench checkpoint to wider
        AU semantic/report coverage
      - DONE: first real HCA transcript structural/legal checkpoint now exists
        under
        `SensibLaw/tests/fixtures/zelph/au_real_transcript_structural_checkpoint_v1/`
      - DONE: first real HCA dense transcript substrate artifact now exists
        under
        `SensibLaw/tests/fixtures/zelph/au_real_transcript_dense_substrate_v1/`
        with a secondary review-overlay projection reusing
        `fact.review.bundle.v1`
      - DONE: the dense AU hearing lane now also carries a first classified
        `hearing_act` layer and bounded `procedural_move` assembly above the
        flatter transcript-bearing fact substrate
      - treat dense transcript-bearing fact/statement counts as primary AU
        substrate output, not as a failure mode to be collapsed immediately
      - current AU blocker is narrower now:
        convert more of the real HCA hearing lane from dense transcript
        substrate into reviewed fact/event coverage without pretending the
        generic transcript fact-review path is already clean enough
      - ingestion UX followthrough:
        - DONE: add opt-in `--progress` stage reporting to
          `build_au_transcript_structural_checkpoint.py` and
          `build_au_transcript_dense_substrate.py`
        - DONE: propagate the same opt-in `--progress` contract into
          `transcript_semantic.py` and `transcript_fact_review.py`
        - DONE: fact-intake persistence now reports nested section progress
          with totals, elapsed seconds, and items/second instead of a blind
          `persist_started` marker
        - DONE: section progress now also emits estimated seconds remaining,
          estimated finish time, and a heuristic confidence interval
        - next: standardize the same `--progress` contract across longer
          builders/ingesters so operators can see stage movement without
          changing default quiet/scriptable behavior
        - DONE: add shared CLI progress/logging helper with human-readable
          stderr progress as the default operator surface, optional `json`
          progress for wrappers, terminal `bar` mode for local operators, and
          `--log-level` plumbing
        - first rollout targets:
          - DONE: `au_fact_review.py`
          - DONE: `gwb_corpus_timeline_build.py`
          - DONE: `build_gwb_public_bios_rich_timeline.py`
          - DONE: `build_gwb_broader_corpus_checkpoint.py`
          - DONE: `build_gwb_broader_promotion_diagnostics.py`
          - DONE: `run_wikidata_qualifier_drift_scan.py`
          - DONE: `wiki_revision_pack_runner.py`
        - next: lift the same shared helper into the remaining long-running
          import/extract/build scripts and add a richer bar renderer only if the
          current terminal bar mode proves insufficient
        - DONE: expose `--reviewed-event-limit` on
          `build_au_transcript_dense_substrate.py` so reviewed hearing-event
          projection size can be tuned without editing code
      - dense hearing overlay followthrough:
        - DONE: add a first AU hearing-procedural reviewed projection over the
          dense substrate so party submissions, court interventions, and
          statute-heavy turns are surfaced explicitly
        - DONE: add a first hearing-act / procedural-move assembly layer above
          that projection so the dense hearing lane now exposes local procedural
          structure, not just scored turns
        - DONE: add a first conservative hearing-event assembly layer above the
          procedural-move layer so the AU dense hearing lane now reaches bounded
          hearing-event structure as well
        - DONE: extend that hearing-event layer to cover short local
          bench↔counsel exchanges and authority/submission clusters rather than
          only one-move lifts
        - DONE: expose event-assembly coverage metrics over the procedural-move
          layer so AU progress is measurable as coverage, not only event count
        - DONE: preserve explicit speaker continuity through hearing acts,
          procedural moves, and assembled events so bench/counsel exchange
          assembly is less dependent on topic overlap alone
        - DONE: tighten the conservative event contract so local cues, speaker
          continuity, and bounded topic continuity all contribute to coverage
        - DONE: preserve transcript-order semantics through procedural moves so
          exchange/event assembly operates on hearing order rather than ranked
          move order
        - DONE: normalize section references and case-style authority cues into
          topic continuity tokens so legal-substance carryover is stronger
        - DONE: derive a reviewed hearing-event projection from the assembled
          event layer so operator-facing AU review is not only a dense fact
          overlay
        - DONE: run and record a 24-item reviewed hearing-event projection
          quality pass on the real HCA dense substrate using
          `--reviewed-event-limit 24`, and classify it as a high-coverage but
          not-yet-trusted reviewed-operator queue
        - DONE: document that same pass in
          `docs/planning/au_completeness_scorecard_20260324.md` under
          the new 24 reviewed-item quality rubric section
        - next: improve reviewed event assembly coverage from that
          hearing-act/procedural-move/event stack instead of treating the
          hearing as a flat fact bucket
        - next: codify a minimum-quality filter before promotion (actor/date
          continuity, truncation-free chunks, and statement-production readiness)
    - current corpus-expansion priority order:
      - 1. broader AU transcript / reviewed WhisperX-backed corpus coverage on
           top of the new dense transcript substrate
      - 2. next genuinely new GWB broader-source family beyond current public
        bios + corpus/book gains
      - 3. safe real chat-history lane
    - archived context input resolved on 2026-03-20:
      - `69bca95c-4f7c-839e-8b3a-3c5e273f185a` / `ZK in Legal Context`
      -> family-court `Magellan` / `Lighthouse` / `Evatt` pathways are a real
         institutional entry point for privacy-preserving verification, but this
         remains future product-positioning context rather than a near-term
         implementation milestone
  - treat Mary Technology as the benchmark for:
    - fact management
    - chronology / timeline handling
    - provenance and contestation of statements
    - litigation-workflow operator surfaces
  - position current ontology/bridge/branch-set work as support infrastructure
  - Wikipedia ingest generalization harness:
    - keep the random-page article-ingest report regime-aware and honest
    - DONE: add dominant-regime counts and follow-yield summaries so page
      shapes can be falsified by distribution, not just by a few hand-picked
      fixtures
    - DONE: keep follow-yield as a 50/50 blend of followed-link relevance and
      follow-target quality, where follow-target quality is driven by richness,
      non-list structure, regime similarity, and information gain
    - DONE: extend the graph probe with hop-1/hop-2 decay and best-path
      probing based on hop qualities plus regime coherence before trying
      heavier graph analytics
    - first live recursive campaign result:
      - root relevance remained very high (`0.982143`) while followed-link
        relevance dropped to `0.5625`
      - follow-target quality averaged `0.446047`
      - hop-2 quality did not collapse on the first 8-page slice
        (`0.471626` vs hop-1 `0.446047`)
      - best-path stayed above average candidate path quality by `0.055025`
      - worst follow pages clustered around `non_list_score = 0.0`, especially
        list/year/generic aggregation pages
    - add repeat-run campaign tooling so operators can archive multiple random
      runs and compare regime/follow/path distributions without hand-editing
      temp paths
    - add failure-clustering outputs over weak follow targets so listiness,
      regime jump, low information gain, and thin-follow failures separate
      cleanly in the reports
    - tighten non-list / generic-aggregation discrimination using page title
      and warning-level cues before touching richer graph analytics
    - DONE: stop `non_list_score` from treating raw wikitext category residue
      as evidence that an ordinary page is list-like
    - corrected 3-run post-fix aggregate:
      - 24 root pages across 3 runs kept the regime split stable
      - root-link relevance stayed very high (`0.981941`)
      - followed-link relevance stayed much lower (`0.5`)
      - follow-target quality averaged `0.506859`
      - hop decay stayed near zero (`0.000996`)
      - `list_like_follow` remained the largest weak-follow bucket and
        `low_information_gain_follow` remained the second
    - next implementation slice:
      - DONE: keep the current 4-part follow-target-quality blend unchanged
      - DONE: keep the current weak-follow thresholds unchanged
      - DONE: expand `non_list_score` / `list_like_follow` with continuation
        specificity, not a new score component
      - DONE: use bounded title heuristics plus mostly lexical parent-child
        specificity checks
      - DONE: explicitly target:
        - admin/place adjacency pages
        - year/edition/championship umbrella pages
        - broad generic concept pages with little specificity lift
    - next validation step:
      - rerun the existing 3x8 campaign after this slice before touching
        `low_information_gain_follow`
      - compare `list_like_follow`, `low_information_gain_follow`,
        `follow_target_quality_score`, and `best_path_vs_avg_gap`
    - add fixed-manifest rescoring / before-after comparison tooling so future
      scorer changes are measured on the same manifests, not only on fresh
      random slices
    - next scoring slice after that comparison:
      - DONE: keep the current score shape unchanged
      - DONE: tighten the existing information-gain component for
        related-but-generic continuations
      - DONE: explicitly target:
        - older year/edition umbrella continuations
        - broad championship/conference parent pages
        - broad parent concepts with little novelty lift
      - next validation step:
        - rescore the same manifests with the new scorer
        - compare before/after reports with the fixed-manifest comparison tool
        - then rerun the normal 3x8 live campaign
    - fixed-manifest slice-2 result:
      - same-manifest comparison did NOT show a clean scoring improvement
      - `list_like_follow` stayed unchanged on the stored manifests
      - `low_information_gain_follow` rose only slightly
      - `follow_target_quality_score` fell (`0.525836 -> 0.507564`)
      - `best_path_vs_avg_gap` improved slightly (`0.047057 -> 0.050072`)
      - `hop_quality_decay` stayed effectively flat (`-0.021348 -> -0.019689`)
    - next refinement after that result:
      - DONE: keep the fixed-manifest compare path
      - DONE: keep the information-gain reason instrumentation
      - soften/narrow score penalties so title-shape cues alone do not drive
        the information-gain score down
      - require co-occurrence between broad/year/umbrella generalization cues
        and low-novelty / same-neighborhood-no-lift evidence before the main
        information-gain penalties apply
    - narrowed `v0_9` result on the same manifests:
      - weak-follow bucket counts stayed unchanged
      - average `follow_target_quality_score` stayed nearly flat rather than
        being materially pulled down
      - hop decay and best-path gap stayed effectively stable
      - information-gain reasons remained visible even when they did not
        trigger a score penalty
    - next scoring slice after `v0_9`:
      - add a content-based continuation-lift signal inside the existing
        information-gain component
      - use follow-page relation-bearing structure and novel-term lift to
        distinguish genuinely informative continuations from mere title-shape
        matches
      - do not add another top-level follow-quality component
      - validate on the same fixed manifests first, then rerun the live 3x8
        campaign
    - keep page-family labels as derived debug output only
  - define the minimum parity deliverable as:
    - source/excerpt/statement capture
    - a small explicit observation layer with a stable low-cardinality
      predicate catalog for the first factual substrate
    - chronology over captured facts/statements

- [P2] JMD/SL graph usefulness criteria:
  - add one compact contract note or fixture showing how a canonical object or
    article state projects into:
    - reversible token/span state
    - conservative graph/overlay view
    - one informative non-local graph/overlay variant
  - define how ITIR judges graph usefulness:
    - not just density/SCC/centrality lift
    - but whether the graph surface helps expose semantic drift, provenance
      conflicts, chronology tension, or repeated structure in a way the base
      serialization does not
  - keep the admissibility boundary explicit:
    - source anchors are canonical substrate
    - candidate and graph overlays are non-authoritative
    - only promotion creates truth-bearing canonical records
  - include one explicit comparison table in a future planning note:
    - text-surface graph observables
    - versus canonical semantic/provenance graph/export outputs
    - contestable fact/claim handling
    - operator review / curation surfaces
    - external-reference/linkage support for the fact layer
  - use `docs/planning/textgraphs_sl_bridge_contract_20260324.md` as the
    narrow bridge boundary note for what may cross between text-surface graph
    overlays and SL canonical lanes
  - immediate scaffold followthrough:
    - add canonical `ObservationRecord` storage/reporting between statements and
      facts
    - add deterministic `EventCandidate` assembly over observations with
      evidence/attribute tables
    - formalize structural IDs vs run IDs so execution context never rewrites
      content identity
    - make abstention explicit in fact/observation/event status handling rather
      than relying on row absence
    - keep the first predicate catalog small and stable rather than trying to
      encode the whole law at intake time
    - compare/align this lane against existing projection-style observation
      types (`CaseObservation`, `ActionObservation`, `DecisionObservation`)
    - keep events derived and reconstructable from observation evidence rather
      than treating them as a new canonical truth layer
    - keep language/jurisdiction variation in normalization packs and concept
      mappings rather than branching assembler logic
  - user-story-informed next slice:
    - expand Mary-parity operator pressure against
      `docs/user_stories.md`
    - use
      `docs/planning/mary_parity_user_story_acceptance_matrix_20260315.md`
      as the acceptance matrix for transcript/AU fact-review work
    - use
      `docs/planning/mary_parity_gap_analysis_20260315.md`
      to prioritize:
      1. richer review queue reasons and contested/chronology triage
      2. source workflow run -> fact-review run reopen mapping
      3. widened legal/procedural observation visibility
  - DONE in current loop:
    - add role-meaningful review queue reasons
      (`missing_date`, `missing_actor`, `contradictory_chronology`,
      `statement_only_fact`, `procedural_significance`, `source_conflict`)
    - add source-label-centric listing and latest reopen/query support for
      persisted fact-review runs
    - add bounded operator views (`intake_triage`, `chronology_prep`,
      `procedural_posture`, `contested_items`)
    - add story-driven acceptance reports over persisted runs
    - add a thin read-only fact-review workbench in `itir-svelte`
      (`/graphs/fact-review`) over the same persisted contract
  - next parity pressure:
    - DONE: add a canonical Wave 1 legal fixture manifest plus batch acceptance
      runner over transcript/AU persisted runs
    - DONE: tighten workbench/operator surfaces with grouped issue filters,
      source-centric reopen navigation, and dated/approximate/undated
      chronology separation
    - DONE: tighten the `itir-svelte` fact-review route/server contract with
      explicit Mary-consumed typing for reopen navigation, issue filters, and
      inspector classification
    - tighten role-specific pass/partial/fail gaps exposed by the new Wave 1
      batch report before moving to claim/theory layers
    - next immediate Mary-parity operator step:
      - validate `/graphs/fact-review` behavior against persisted
        `wave1_legal` runs instead of only route-string regressions
      - add focused UI validation for:
        - source-centric reopen chip behavior
        - canonical issue-filter switching
        - inspector classification rendering
        - chronology bucket rendering
      - treat `wave1_legal` as the hard UI/operator gate before broadening
        more semantic families or substrate surfaces
    - explicitly add fixture families for:
      - contested Wikipedia/Wikidata/public-figure moderation
      - lawyer/public-knowledge legality assessment (including GWB and Trump
        style lanes, with proven-illegal, legally dubious, and clearly
        authorized comparisons where possible)
      - family-law / child-sensitive / cross-side handoff
      - medical-negligence / professional-discipline overlap
      - personal-to-professional handoff and anti-AI-psychosis resistance
    - DONE: green the explicit acceptance-wave program through:
      - `wave1_legal`
      - `wave2_balanced`
      - `wave3_trauma_advocacy`
      - `wave3_public_knowledge`
      - `wave4_family_law`
      - `wave4_medical_regulatory`
      - `wave5_handoff_false_coherence`
  - next parity audit priority:
      - broaden real-fixture depth for waves that remain synthetic-heavy,
        especially:
        - `wave3_public_knowledge`
        - `wave4_family_law`
        - `wave4_medical_regulatory`
      - run an operator/workbench/export polish audit over the green waves
        before adding another major semantic family
  - next legal-operator coverage lane:
    - use `docs/planning/affidavit_coverage_review_lane_20260325.md` as the
      planning source
    - DONE: add a first bounded `affidavit_coverage_review` implementation lane
      at:
      - `SensibLaw/scripts/build_affidavit_coverage_review.py`
      - `SensibLaw/tests/test_affidavit_coverage_review.py`
    - keep extending that lane over:
      - persisted AU/transcript dense-substrate or fact-review source rows
      - one affidavit/declaration draft input
    - first contract should surface:
      - `covered`
      - `partial`
      - `missing_review`
      - `contested_source`
      - `abstained_source`
      - `unsupported_affidavit`
    - keep governance explicit:
      - high-recall source extraction is not the same as promoted reviewed fact
      - contested or abstained rows must not silently become omissions
      - preserve provenance from affidavit proposition -> source row -> excerpt
    - next:
      - widen source-input support from fact-review bundles and bounded AU
        slices toward richer AU dense-substrate/source-row reuse
      - DONE: add one repo-stable AU dense-substrate checked fixture/artifact
        for this lane:
        - `SensibLaw/scripts/build_au_dense_affidavit_coverage_review.py`
        - `SensibLaw/tests/test_au_dense_affidavit_coverage_review.py`
        - `SensibLaw/tests/fixtures/zelph/au_dense_affidavit_coverage_review_v1/`
      - DONE: add one repo-stable AU-specific checked fixture/artifact for this
        lane:
        - `SensibLaw/scripts/build_au_affidavit_coverage_review.py`
        - `SensibLaw/tests/test_au_affidavit_coverage_review.py`
        - `SensibLaw/tests/fixtures/zelph/au_affidavit_coverage_review_v1/`
  - after parity substrate is credible, fold back into:
    - explicit Observation / Claim contracts
    - deterministic `source/excerpt -> observation -> event/fact -> norm -> claim`
    - typed guarded state transitions
    - p-adic / ultrametric retrieval experiments
  - Dependencies:
    - archived thread `Insights from Whitepaper`
      (`69b41f22-a514-839f-946c-fa0e9f75cc46`)
    - `docs/planning/sl_whitepaper_followthrough_20260314.md`
    - current ontology bridge / external-ref / branch-set work in `SensibLaw`
- [P2] Wikidata ontology integration working (end-to-end):
  - align with `SensibLaw/docs/wikidata_queries.md` and `SensibLaw/docs/ONTOLOGY_EXTERNAL_REFS.md`
  - implement the deterministic projection/instability model in `docs/planning/time_series_transformations.md`
  - confirm ontology DB upsert flow + provenance contract for Wikidata refs
  - Dependencies:
    - operator spec: `SensibLaw/docs/wikidata_epistemic_projection_operator_spec_v0_1.md`
    - transition plan + slice decision: `SensibLaw/docs/planning/wikidata_transition_plan_20260306.md`
    - reproducible input slice (two dumps or two edit windows)
- [P1] Wikidata hotspot benchmark lane:
  - use `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md` as the
    planning source
  - use `docs/planning/wikidata_hotspot_pack_contract_20260325.md` as the
    current schema/generator/evaluator contract
  - use `docs/planning/wikidata_hotspot_pilot_pack_v1.manifest.json` as the
    ratified pilot-pack manifest
  - DONE: define the first emitted cluster-pack JSON schema in the hotspot pack
    contract
  - DONE: promote the pilot pack to `v1` at the manifest/contract level
  - DONE: promote the finance and software entity-kind-collapse examples into
    local slice-backed fixtures:
    - `SensibLaw/tests/fixtures/wikidata/finance_entity_kind_collapse_pack_v0/slice.json`
    - `SensibLaw/tests/fixtures/wikidata/software_entity_kind_collapse_pack_v0/slice.json`
  - DONE: implement the first minimal generation surface:
    - module: `SensibLaw/src/ontology/wikidata_hotspot.py`
    - CLI: `sensiblaw wikidata hotspot-generate-clusters`
    - tests:
      - `SensibLaw/tests/test_wikidata_hotspot.py`
      - `SensibLaw/tests/test_wikidata_hotspot_cli.py`
  - DONE: implement the first score-only evaluator surface:
    - module: `SensibLaw/src/ontology/wikidata_hotspot_eval.py`
    - CLI: `sensiblaw wikidata hotspot-eval`
    - tests:
      - `SensibLaw/tests/test_wikidata_hotspot_eval.py`
  - current `v1` boundary:
    - emitted cluster packs carry deterministic `question_id` fields
    - evaluator input is normalized response-bundle JSON
    - live provider execution remains out of scope
      - `SensibLaw/tests/test_wikidata_hotspot_cli.py`
  - DONE: add all-manifest generation coverage, not only selected-pack tests
  - DONE: add canned evaluator response-bundle fixtures for nontrivial hotspot
    families:
    - `SensibLaw/tests/fixtures/wikidata/hotspot_eval_v1/qualifier_drift_p166_live_pack_v1_responses_consistent.json`
    - `SensibLaw/tests/fixtures/wikidata/hotspot_eval_v1/software_entity_kind_collapse_pack_v0_responses_inconsistent.json`
    - `SensibLaw/tests/fixtures/wikidata/hotspot_eval_v1/finance_entity_kind_collapse_pack_v0_responses_incomplete.json`
  - define hotspot families as the benchmark-generation primitive:
    - mixed-order
    - entity-kind collapse
    - SCC/circular subclass
    - property/constraint pressure
    - qualifier drift
    - typed parthood ambiguity
  - build a small fixture-backed pilot pack spanning at least:
    - one mixed-order example
    - one SCC example
    - one qualifier-drift example
    - one finance/product-service-category entity-kind-collapse example
    - one software/project/artifact entity-kind-collapse example
  - preserve provenance from pinned slice/revision pair -> hotspot family ->
    generated cluster family
  - DONE: separate backing state from readiness state in the hotspot manifest:
    - `status` remains provenance/backing
    - `promotion_status` now carries `candidate|anchored|promotable|promoted`
    - `hold_reason` is required for non-promoted entries
  - DONE: classify the current pilot-manifest packs under the promotion ladder
  - keep `v1` evaluator scope score-only:
    - normalized labels required in the input response bundle
    - no direct provider execution in this slice
  - do not flatten `P31` and `P279` into one benchmark relation without also
    retaining the original structural pathology that made the hotspot useful
  - define the win condition against IBM-style hotspot work as:
    - better hotspot legibility
    - better provenance
    - cross-domain generality
    - deterministic rerun stability
    - explainable failure modes
  - next docs-first checkpoint:
    - decide whether `v2` should stop at a thin adapter-command wrapper or keep
      live execution permanently external
    - if adapter-command support is ever added, require the same response-bundle
      schema as the canonical replay surface
    - decide later whether splitting hotspot implementation into separate
      manifest/cluster/eval modules actually improves maintainability enough to
      justify churn
- [P1] Wikidata `P2738` disjointness parity lane:
  - use `docs/planning/wikidata_parity_gap_note_rosario_ege_20260325.md` as
    the current comparison note against Rosario and Ege/Peter
  - use `docs/planning/wikidata_p2738_disjointness_lane_20260325.md` as the
    bounded design note for the next parity slice
  - DONE: implement the first standalone deterministic lane:
    - module:
      `SensibLaw/src/ontology/wikidata_disjointness.py`
    - CLI:
      `sensiblaw wikidata disjointness-report`
    - tests:
      - `SensibLaw/tests/test_wikidata_disjointness.py`
      - `SensibLaw/tests/test_wikidata_disjointness_cli.py`
    - fixture pack:
      `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_pilot_pack_v1/slice.json`
  - implemented `v1` report surface now covers:
    - pairwise disjoint class extraction from `P2738` + `P11260`
    - subclass violations over local `P279` closure
    - instance violations over local `P31` + `P279` closure
    - bounded culprit class and culprit item surfacing
    - one reviewer-facing deterministic JSON report
  - DONE: add one real Wikidata-backed baseline pack beside the synthetic pilot:
    - `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_nucleon_real_pack_v1/slice.json`
  - DONE: add one real Wikidata-backed contradiction pack:
    - `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_fixed_construction_real_pack_v1/slice.json`
  - DONE: freeze the report contract in:
    - `docs/planning/wikidata_disjointness_report_contract_v1_20260325.md`
  - DONE: decide lane relationship for now:
    - disjointness remains a sibling lane, not a hotspot family
    - only revisit hotspot integration after more real packs exist and the
      report contract stays stable
  - DONE: freeze disjointness promotion-ladder policy at the docs/governance
    layer while keeping `wikidata_disjointness_report/v1` observational
  - DONE: add machine-readable disjointness case governance:
    - `docs/planning/wikidata_disjointness_case_index_v1.json`
  - DONE: add a callable live scan script for WDQS-backed contradiction
    discovery:
    - `SensibLaw/scripts/run_wikidata_disjointness_candidate_scan.py`
  - DONE: split candidate discovery into explicit backends:
    - `wdqs` for live subclass/instance scans
    - `zelph` for local instance scans from explicit pair seeds
  - DONE: add the first repo-owned disjoint-pair seed surface for local scans:
    - `SensibLaw/data/ontology/wikidata_disjointness_pair_seed_v1.json`
  - DONE: tighten culprit semantics with downstream impact counts and
    explanation linkage on instance rows
  - keep the live scan script read-only and network-dependent:
    - fixture packs remain manually pinned after review
    - do not auto-materialize repo fixtures from live query output
  - current zelph boundary is explicit:
    - local instance contradictions only for now
    - do not claim direct `P2738` qualifier mining from `.bin` imports yet
  - local pruned-bin posture is now explicit:
    - `wikidata-20171227-pruned.bin` and
      `wikidata-20260309-all-pruned.bin` are runtime-only negative controls
    - both bins are still retained locally for now and remain materially large
      (`~1.4 GiB` and `~5.6 GiB`)
    - baseline profile, wide profile, bounded profile, exact-QID checks, and a
      seedless contradiction scan on the newer pruned bin all returned zero
      useful local signal
    - treat live/current WDQS-backed Wikidata probing as the primary discovery
      surface for new contradiction packs
  - evaluate Zelph `.bin` sharding/remote-read feasibility:
    - bin format is Cap'n Proto `ZelphImpl` with chunked left/right adjacency
      and name maps; counts and `chunkIndex` per section are stored in the
      header; chunks are written as sequential packed messages
    - current loader streams all chunks into memory; no offset table or partial
      load
    - DONE: added header-only serialized inspection in the Zelph clone via
      `.stat-file <file.bin>`
    - DONE: added sidecar byte-offset index generation in the Zelph clone via
      `.index-file <file.bin> <output.json>`
    - DONE: added selector-based partial materialization in the Zelph clone via
      `network::Zelph::BinChunkSelection`,
      `load_from_file(filename, selection)`, and
      `.load-partial <file.bin> ...`
    - DONE: partial mode now blocks inference, pruning, cleanup, and direct
      edit/save/import commands so the first sharding surface stays read-only
    - DONE: defined the first HF hosting/query contract as
      `zelph-hf-layout/v1` in
      `docs/planning/zelph_hf_storage_contract_20260326.md`
    - DONE: added a manifest builder for `.bin + sidecar index` at
      `tools/build_zelph_hf_manifest.py`
    - DONE: validated the manifest builder with
      `tests/test_build_zelph_hf_manifest.py`
    - DONE: extended manifest builder for `zelph-hf-layout/v2` with explicit
      section-object paths and optional shard emission (`--layout v2 --emit-shards`)
    - DONE: added an exact prototype route-sidecar builder at
      `tools/zelph_bin_route_builder.cpp`
    - DONE: manifest builder can now advertise an optional
      `zelph-node-route/v1` sidecar via `--node-route`
    - DONE: patched Zelph partial loader now consumes the prototype route
      sidecar for opt-in routed partial loads:
      - `route-node=<id,...>` resolves chunk indexes for `left`, `right`,
        and `nameOfNode`
      - `route-name=<exact>` + `route-lang=<lang>` resolves `nodeOfName`
      - validated locally against the 2017 shard layout produced by the harness
    - DONE: hosted HF manifest/object consumption now works end-to-end for the
      minimal proof repo after:
      - remote manifest prefetch
      - correct `hf://` -> `resolve/main/...` raw-file URL mapping
    - DONE: added fetch-budget estimator:
      `tools/estimate_zelph_shard_fetch_budget.py`
    - DONE: `acrion/zelph#25` merged into `develop`
    - DONE: bounded proof artifacts are now mirrored across:
      - HF dataset shard/query proofs
      - HF bucket storage for the shared-contract companion pack
      - IPFS bounded proof roots
    - current measured 2026 envelope:
      - route-node median about `51.95 MiB`
      - route-node p95 about `60.63 MiB`
      - route-node max about `700.53 MiB`
      - route-name median about `21.70 MiB`
    - next steps:
      - await upstream review / merge decision on the follow-up fix:
        `acrion/zelph#26`
      - treat the Zelph shard/HF/IPFS lane as handoff-complete unless new
        upstream review feedback arrives
      - simulate/query-shape a `zelph-hf-layout/v3` bucketed shard contract as
        documented in
        `docs/planning/zelph_hf_v3_shard_contract_20260326.md`
      - DONE: first lower-bound `v3` simulation indicates rebucketing is worth
        building:
        - adjacency `256` buckets -> route-node average about `17.94 MiB`
        - adjacency `512` buckets -> route-node average about `8.97 MiB`
        - names `128` buckets -> route-name average about `4.40 MiB`
      - reduce shard granularity and/or add a second routing tier so typical
        remote routed lookups are materially below the current `~52 MiB` median
        for route-node on the 2026 artifact
      - move `zelph-node-route/v1` from large JSON prototype toward a denser
        long-term representation (binary or sqlite-style sidecar)
      - compare the Zelph shard family against the Kant shard family only after
        the shared artifact contract is frozen in
        `docs/planning/zelph_kant_zos_shard_contract_matrix_20260327.md`
        and
        `docs/planning/shared_shard_artifact_contract_v1_20260327.md`
      - DONE: first shared-contract builder slice now exists:
        - `tools/build_shared_shard_artifact_contract.py`
        - `tests/test_build_shared_shard_artifact_contract.py`
        - emits JSON and CBOR projections from one Zelph manifest-derived
          logical artifact
      - DONE: first real dual-sink shared-contract projection now exists for
        the 2026 v3 Zelph proof artifact:
        - `tools/build_ipfs_shard_ref_map.py`
        - `tests/test_build_ipfs_shard_ref_map.py`
        - emits deterministic `ipfs://` refs for all logical shards plus the
          routing index, then rebuilds the same logical contract with both HF
          and IPFS object refs attached
      - do not claim the current Zelph sharder is globally optimal yet; current
        evidence only supports that it is the best fit so far for query-shaped
        remote graph reads
      - teach the partial loader to consume the sidecar offset index directly
        rather than streaming the whole file sequentially
      - add a local seek / remote object-fetch transport abstraction around the
        same selector-based loader so HF hosting becomes execution-capable
      - add v2 manifest consumption in the loader transport
  - next external-method question for the Zelph developer:
    - once sidecar-driven seek exists, ask for review on whether the current
      `.bin` format should embed offsets in-header or keep them as sidecars
  - only after the current lane has:
    - one real baseline pack
    - one real contradiction pack
    - stable case-index governance
    should disjointness be reconsidered as a hotspot family candidate
 - [P1] Wikidata page-review candidate governance:
  - DONE: add a machine-readable candidate index for page-reviewed non-core
    cases:
    - `docs/planning/wikidata_page_review_candidate_index_v1.json`
  - DONE: classify the current entity-kind page-review examples under the same
    readiness ladder and hold-reason taxonomy
  - keep this lane separate from the existing hotspot lane until the report
    contract is stable
  - note the positioning clearly:
    - Rosario parity is now meaningful but partial
    - Ege/Peter parity is no longer blocked on total absence of `P2738`
      disjointness work; remaining gap is broader coverage and closer method
      parity
    - Zelph gives the repo a complementary downstream reviewed-structure lane,
      but does not substitute for disjointness-specific parity
- [P1] Checked wiki/Wikidata handoff parity:
  - use `docs/planning/wikidata_structural_handoff_v1_20260325.md` as the
    planning source
  - DONE: build the first checked artifact:
    - `SensibLaw/scripts/build_wikidata_structural_handoff.py`
    - `SensibLaw/tests/test_wikidata_structural_handoff.py`
    - `SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/`
  - build one checked artifact parallel to the GWB/AU handoff shape:
    - `SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/`
    - `wikidata_structural_handoff_v1.slice.json`
    - `wikidata_structural_handoff_v1.summary.md`
    - `wikidata_structural_handoff_v1.facts.zlp`
    - `wikidata_structural_handoff_v1.rules.zlp`
    - `wikidata_structural_handoff_v1.engine.json`
    - `wikidata_structural_handoff_v1.scorecard.json`
  - include as bounded inputs only:
    - promoted hotspot exemplars
    - one held/promotable hotspot review pack
    - real disjointness baseline + contradiction cases
    - importer-backed qualifier baseline slice
  - keep this as readability/handoff followthrough, not a broad new ingest lane
  - do not move frozen outward-facing Zelph pack `v1.6` automatically
    because of this artifact
  - current achieved condition:
    - one human-legible wiki/Wikidata handoff now exists without needing the
      reader to assemble status notes manually
- [P1] SL observation + case-construction followthrough:
  - note: now explicitly phase-two after Mary-parity fact-layer work, not the
    first user-facing SL milestone
  - the 2026-03-18 archive pass sharpened the implementation boundary:
    - keep uploaded-file handling explicitly partial and file-search backed
    - keep the governance/proof operator explicit rather than implicit
    - frame the bridge work as a compact demo or state-compiler prototype,
      not a full Zelph integration
  - use `docs/planning/sl_whitepaper_followthrough_20260314.md` as the
    planning source for the next SL-facing architecture/spec pass
  - DONE: ratify explicit `Observation` and `Claim` contracts before adding more
    doctrinal node types, now concretized with
    `SensibLaw/schemas/sl.observation_claim.contract.v1.schema.yaml`
  - define the deterministic seam for
    `source/excerpt -> observation -> event/fact -> norm -> claim`
  - define RDF/Wikidata projection/export as an interoperability boundary, not
    the core SL authority model
  - queue legal versioning and jurisdiction as the next infrastructure slice
    after the observation seam is explicit
  - add a bounded typed-transition receipt design for
    `state + observation + norm -> updated state`
  - keep unresolved normative placeholders (for example `community`) as
    text-grounded observation/norm-reference surfaces until explicit legal
    context resolves them; do not force Wikidata/entity identity too early
  - define a narrow Wikidata prepopulation target
    (jurisdictions, courts, legislation, cases/citations, actor identity,
    temporal validity relations) instead of generic triple sync
  - decide whether to prototype p-adic / ultrametric case similarity as an
    explanation-first retrieval lane before any embedding-first default
  - Dependencies:
    - archived thread `Insights from Whitepaper`
      (`69b41f22-a514-839f-946c-fa0e9f75cc46`)
    - `docs/user_stories.md` claim-discipline requirements
    - current Wikidata planning docs and ontology external-ref contracts
- [P3] GWB seed pipeline completion (Wikipedia -> seed envelope -> ontology refs):
  - see `docs/planning/wiki_ingest_fact_tree_gwb_20260210.md` and `docs/planning/wiki_ingest_run_notes_20260210.md`
  - Dependencies:
    - revision-locked snapshots via pywikibot/MediaWiki (`SensibLaw/.cache_local/wiki_snapshots*`)
    - candidate extraction artifacts (`SensibLaw/scripts/wiki_candidates_extract.py`, `SensibLaw/.cache_local/wiki_candidates_gwb.json`)
    - ontology external-refs upsert path (`python -m cli ontology external-refs-upsert`)
    - optional: Graphviz `dot` for SVG rendering
- [P3] AAO timeline graph surface stabilization:
  - ensure `itir-svelte` AAO routes stay aligned with `docs/planning/wiki_timeline_extraction_gwb_20260211.md`
  - Dependencies:
    - base timeline artifact `SensibLaw/.cache_local/wiki_timeline_gwb.json`
    - AAO extractor `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
    - extraction profile `SensibLaw/policies/wiki_timeline_aoo_profile_v1.json`
    - run with project venv for spaCy parser lane (see `docs/planning/wiki_timeline_extraction_gwb_20260211.md`)
    - admissibility gate: `docs/planning/oac_object_admissibility_contract_v1_20260211.md`
- [P1] Wikipedia random article-ingest coverage followthrough:
  - DONE: define the parent contract for revision-locked random-page article ingest
    over arbitrary Wikipedia prose rather than treating the lane as
    revision-volatility or date-anchor-only work
  - DONE: keep timeline readiness as a derived chronology surface over broader
    article ingestion, not as the only quality score
  - DONE: add unit-test-backed article-wide sentence ingestion scoring so simple
    cases like `Jane patted the cat` retain who-did-what structure cleanly
  - DONE: add bounded one-hop follow support to the random-page manifest path with
    explicit caps and replayable child snapshot linkage
  - DONE: retarget `Antigravity-Aether` toward article-ingest coverage and timeline-
    enabling test expansion rather than reversion/sentinel work
  - DONE: realign the lane around one canonical wiki-state compiler with
    article-ingest, timeline, and revision projections instead of treating the
    timeline extractor as the ingest ontology
  - DONE: keep the timeline name but allow ordered undated events with explicit
    anchor-status markers instead of date-only inclusion
  - DONE: split the article-ingest report into dual-track coverage vs honesty
    scoring so extraction blowups/noisy bindings stop looking like near-perfect
    ingest
  - DONE: add scorer-only honesty diagnostics for observation explosion, text
    hygiene, actor-action binding, object binding, and timeline honesty ratios
  - DONE: add a third scorer-only calibration layer for abstention quality,
    sentence-link relevance, claim/attribution grounding, and heuristic
    page-family stratification
  - DONE: add a small regime vector to the canonical article state and make
    the ingest report emit regime-aware honesty/calibration scores alongside
    the legacy compatibility outputs
  - DONE: rerun the stored random-page manifest against the honesty +
    calibration surfaces and record the main pressure points
  - rerun the stored random-page manifest again after the regime layer so the
    summary averages and family buckets can be compared against the new
    regime-aware outputs
  - DONE: run the one-hop generalization smoke on a larger live random-page
    slice and confirm the report now surfaces dominant-regime counts and
    follow-yield summaries in addition to the page-level scores
  - use the rerun findings to tighten family-aware summary interpretation:
    - abstention calibration is already informative on `Agrega` and
      `Euchlaena deductaria`
    - link relevance currently saturates on the stored manifest and still needs
      a stronger centrality/follow-yield formulation before it becomes a useful
      discriminator
  - keep reducer/tokenizer reporting as companion diagnostics and rerun legal-
    specific comparisons separately instead of making them the whole lane
  - pressure-test the article-ingest report across more arbitrary non-legal
    pages before tightening score thresholds
  - pressure-test the new page-family heuristics on a broader stored random
    slice before treating family-level averages as stable
  - revisit weak-object penalties after the abstention/link calibration pass so
    taxonomy/catalog pages do not look uniformly broken when the real problem is
    page-shape mismatch
  - recover the graph-quality follow-up thread
    `69c0bd1d-389c-8399-a23e-10efab70a1a9` after the `re_gpt` auth-bootstrap
    fix and fold any `PositiveBorelMeasure` / graph-centrality guidance into
    the Wikipedia ingest metrics docs
  - debug the live ChatGPT refresh path around online UUID
    `69c0b4d1-d714-839b-b21c-ce162292db4f`:
    - do not assume token staleness from the current failure mode
    - inspect whether `re_gpt` / `pull_to_structurer.py` is issuing a malformed
      POST or otherwise broken auth/request sequence when trying to refresh an
      already-ingested thread
    - once fixed, re-verify that thread and fold any sharper repo-facing
      wording back into the Wikipedia ingest docs/context
  - fix `re_gpt` auth bootstrap for live UUID pulls:
    - when `/api/auth/session` returns only `WARNING_BANNER`, treat it as a
      frontend-cookie hydration failure first, not an automatic token-expiry
      diagnosis
    - hydrate frontend cookies from `https://chatgpt.com/` and retry the auth
      session call in both sync and async clients
    - do not treat the Cloudflare/Playwright browser solver path as the current
      target fix; use it only as an experimental fallback while direct web pull
      bootstrap is being repaired
    - DONE: preserve non-empty session cookies when frontend responses hand
      back blank `__Secure-next-auth.session-token` values
    - DONE: add fallback parsing of `client-bootstrap` access tokens plus an
      async sync-bootstrap escape hatch
    - still unresolved: the current session-token-only frontend path renders
      `client-bootstrap` as logged out on `/` and `/c/<uuid>`, so recoverability
      of thread `69c0bd1d-389c-8399-a23e-10efab70a1a9` likely needs either a
      browser-authenticated fetch path or a different auth source than the
      current `re_gpt` token flow
  - support chunked local session-token files:
    - read `~/.chatgpt_session_new` when present
    - concatenate raw non-empty lines as token chunks before auth bootstrap
    - keep the existing `config.ini` / `~/.chatgpt_session` precedence intact
  - deepen the shared-reducer non-legal comparison slice so it becomes more
    useful on ordinary encyclopedia prose rather than only as a companion
    diagnostic
- [P2] Wikipedia revision harness followthrough:
  - DONE: define the first monitor pack and dedicated runner/state-store contract
  - DONE: define a second curated high-contestation monitor pack to complement
    the ontology-stress pack
  - DONE: land rolling current-vs-last-seen runner over live Wikipedia article packs
  - DONE: document the history-aware runner contract and suite interface
    posture for SB / SL-reasoner / fuzzymodo / casey-git-clone
  - DONE: implement bounded revision-history polling and candidate-pair
    scoring over recent article history windows
  - DONE: add section-aware diff targeting and pair-level report wrappers over
    the existing revision harness
  - DONE: attach bounded review-context joins from existing Wikidata
    diagnostics and bridge aliases to revision issue packets
  - DONE: add pack-level triage summaries and direct-consumer article severity
    surfaces
  - DONE: add contested-region graph artifacts/read models plus a dedicated
    `itir-svelte` page over the contested pack
  - DONE: expand the contested pack into `wiki_revision_contested_v2` with
    deeper bounded history defaults and graphing enabled
  - DONE: make the revision harness state-first over canonical wiki-state
    bundles, with timeline/graph/editorial summaries treated as derived review
    surfaces
  - run repeated live passes over both curated packs so the lane accumulates
    real `changed` reports rather than mostly baseline/unchanged runs
  - compare volatility classes across packs (ontology-stress vs contested-live)
    before deciding what belongs in a default monitor set
  - decide whether `wiki_revision_contested_v2` should replace
    `wiki_revision_contested_v1` as the canonical contested live pack in docs
    and runbooks, or whether v1 should remain a smaller/lightweight sibling
  - add a bounded query/report contract for mining candidate contested titles
    without turning the lane into an open crawler
  - decide whether triage dashboards should later emit clearly-advisory edit
    suggestions or move directly to a workbench
  - Dependencies:
    - `SensibLaw/docs/wiki_revision_harness_contract_v0_1.md`
    - `SensibLaw/docs/wiki_revision_pack_runner_contract_v0_1.md`
    - `SensibLaw/docs/wiki_revision_pack_runner_contract_v0_2.md`
    - `SensibLaw/docs/planning/wiki_revision_harness_first_pass_20260309.md`
    - `SensibLaw/docs/planning/wiki_revision_contested_pack_20260309.md`
    - `SensibLaw/docs/planning/wiki_revision_history_runner_20260309.md`
    - `SensibLaw/docs/planning/wiki_revision_contested_region_graph_20260309.md`
    - `SensibLaw/scripts/wiki_revision_harness.py`
    - `SensibLaw/data/source_packs/wiki_revision_monitor_v1.json`
    - `SensibLaw/data/source_packs/wiki_revision_contested_v1.json`
    - `SensibLaw/data/source_packs/wiki_revision_contested_v2.json`
- [P1] Recent `itir-svelte` page audit followthrough:
  - DONE: add repeatable localhost audit runner `scripts/check_recent_pages.py`
  - DONE: record first audit findings in `docs/planning/recent_page_audit_20260309.md`
  - DONE: fix `/arguments/thread/69ac40e0-0cfc-839b-b2a8-0de3019379a9` returning HTTP `500`
  - DONE: fix the contested wiki graph lane so a graph-enabled `wiki_revision_contested_v2` run can hydrate `selected_graph` from DB or artifact-backed payloads rather than returning `null`
  - DONE: distinguish `producer run error` vs `changed run with missing graph payload` vs `valid populated graph` in `/graphs/wiki-revision-contested`
  - DONE: refresh contested wiki route default pack to graph-enabled `wiki_revision_contested_v2`
  - DONE: add explicit review-state + selection-bridge wiring for `/arguments/thread/[threadId]`, `/graphs/narrative-compare`, and `/graphs/wiki-revision-contested` with regression guards (including no `localStorage` / JSON UI-state persistence)
  - DONE: align UX/interaction work on `/arguments/thread/[threadId]`,
    `/graphs/narrative-compare`, and `/graphs/wiki-revision-contested` against
    `docs/planning/recent_workbench_page_user_stories_20260310.md`
  - keep `python scripts/check_recent_pages.py` in the manual verification loop whenever recent `itir-svelte` routes or upstream producer contracts change

- Come back to the Duncan/Emma response draft:
  - `docs/planning/response_to_duncan_emma_itir_hospital_advocacy_20260208.md` missed the intended mark (needs a better synthesis/voice and should be evaluated against the actual posting context).
- Tool Use Summary view follow-up:
  - DONE: Shell/hour and Input/hour now hydrate from tool-message bins (chat-archive `exec_command` + `request_user_input`) in the SB reducer layer.
  - DONE: Shell/hour and Input/hour share the same upstream time-binning path (SB reducer `frequency_by_hour`), with explicit regression coverage.
  - DONE: NotebookLM notes-meta interactions are now folded into the tool-use stream (`notebooklm_meta_event` family + hour bins) so tool-use counters and views hydrate from a shared reducer path.
- Grafana integration (do not reimplement Grafana):
  - ratify metrics/logs/traces scope and label/cardinality policy:
    `docs/planning/grafana_integration_metrics_scope_20260208.md`
  - implement Prometheus `/metrics` endpoints for orchestrator + key adapters
  - decide collector path (Prometheus vs Grafana Agent vs OTEL Collector) and hosting
  - add Grafana Alerting webhook ingest as an observer lane (link-first)
  - add a thin sitrep that reports alert state + links to Grafana, not charts
- SensibLaw Ontology DB migration hygiene:
  - DONE: Make SQLite ontology migrations idempotent by tracking applied migrations (do not re-run `001_normative_schema.sql` after `002_normalize_countries.sql` drops transitional columns).
  - DONE: Add guardrails so we don’t accidentally point ontology migrations at VersionedStore ingest DBs (different schema families).
  - DONE: Unblock DBpedia external ref upserts by making `ensure_database()` safe on repeated CLI calls.
  - DONE: DBpedia curation UX: emit a curated batch skeleton from Lookup API results (compatible with `ontology external-refs-upsert`) so we don’t copy/paste candidate URIs by hand.
- Execute assumption stress controls from
  `docs/planning/assumption_stress_test_20260208.md`:
  - DONE: add axis hierarchy policy fixtures and collision tests (`A1` / `Q1`)
  - DONE: implement SB fold-policy receipt + anti-nudge red-team tests (`A2` / `Q2`)
  - DONE: add claim-link provenance quality gates for receipts-backed artifacts (`A3`)
  - add plural-law non-reduction preservation fixtures (`A4` / `Q7`)
  - define encrypted-local performance budget benchmarks and degradation
    contracts (`A5`)
  - define contradiction action-branch protocol tests with uncertainty labels
    and no forced collapse (`A6`)
  - DONE: add deterministic lexical-noise guard fixtures:
    stopwords/number-heavy spans, cross-page artifacts, citation boilerplate
    flooding (`A7`)
  - DONE: add fail-closed CI stub tests for unresolved AIDs/Qx controls, with explicit
    waiver receipt path (`A8`)
  - add summary-lineage guards that block summary-of-summary canonical paths
    unless expanded to raw IDs first (`A9`)
  - define and enforce machine-readable `loss_profile` schema across fold/sitrep/
    receipts surfaces (`A10`)
- Run refactor execution from
  `docs/planning/refactor-master-coordination.md`:
  - keep `Q2`/`Q6`/`Q11` states updated (`OPEN` -> `RATIFIED` -> `IMPLEMENTED`
    -> `VERIFIED`)
  - enforce merge policy checks for all boundary-affecting PRs
  - update sprint gate checklist daily during Sprint 10 execution window
- Execute UI surface linking/integration followthrough from:
  - `docs/planning/ui_surface_registry_20260208.md`
  - `docs/planning/ui_integration_strategy_20260208.md`
  - `docs/planning/ui_surface_manifest.json`
  - add a minimal launcher page that reads the manifest and links native
    interfaces (include WhisperX Gradio + SB dashboard + SL Streamlit)
  - ratify `Q12` in
    `docs/planning/refactor-master-coordination.md` before any federated shell
    implementation
  - add a drift check ensuring registry docs and manifest entries stay aligned
    (no stale ports/commands)
- Add observer stubs + dashboards for:
  - iNaturalist biodiversity (insect trend phase: `upward_knee|peak|declining`)
  - mood self-report (explicit, non-inferential)
  - pet wearables / smart collars (smart-home telemetry, meta-only)
  - health data exports (meta-only by default):
    - FHIR export connector (Bundle/NDJSON) -> story events
    - scans folder connector (DICOM/exported images/PDFs) -> story events
    - doctor notes folder connector (txt/md/pdf refs) -> story events
    - OCR followthrough (handwritten/scanned docs):
      - local OCR pipeline (offline) for PDFs/images, emitting non-authoritative text artifacts linked by hash
      - optional frontier OCR path (explicit opt-in, redaction/cropping guidance, full provenance logging)
- CAM (Crisis-Advocacy Module) followthrough:
  - freeze an escalation envelope schema (machine-checkable): done (`docs/planning/schemas/escalation_envelope.schema.json`)
  - add envelope validation + red-team tests (no misrepresentation, no financial/legal binding, stop-on-success)
  - define CAM audit log artifact contract (after-action record)
- Prospective Sprint 10 (refactor thin slice) from
  `docs/planning/itir_prospective_sprint_10_refactor_20260208.md`:
  - ratify blocking decisions `Q2`, `Q6`, and `Q11` as ADRs before adapter
    freeze
  - freeze `itir.exchange.v1` with required replay/provenance fields including
    reducer version metadata
  - implement shared canonical reducer integration surface for TiRCorder/SB
    clients (Option C posture)
  - wire thin-slice adapters:
    TiRCorder->canonical IDs, SB->canonical ID refs, SB->Ribbon read-only map
  - add sprint gate tests:
    replay no-op/conflict, cross-path identity parity, projection safety, and
    expansion-invariant smoke
- Current execution pass scope (2026-02-07):
  - Convert live + archived Casey/Muratori conversation steps into explicit
    implementation artifacts for `fuzzymodo/` and `casey-git-clone/`.
  - Implement the mapped steps in code with project-local tests. (Done)
- Term sweep follow-ups from
  `__CONTEXT/last_sync/20260207T043655Z_term_sweep_sl_sensiblaw_itir_suite.md`:
  - Add a repeatable term-sweep runbook doc under `docs/planning/` covering
    scope, whole-word matching rules, and output artifact contract.
  - Add/refresh high-signal thread mappings in `__CONTEXT/convo_ids.md` for the
    top titled `SL`/`sensiblaw`/`itir`/`suite` conversations.
- Add a triage rule for overloaded term `suite` (flag likely false positives
  before context ratification).
- Execute chat artifact capture followthrough from
  `docs/planning/chat_artifact_capture_contract_20260208.md`:
  - add deterministic extractor for assistant-generated artifact classes
    (`download_link_artifact`, `inline_file_artifact`,
    `execution_claim_artifact`)
  - emit canonical artifact JSONL records with idempotency/provenance fields
  - add fixture tests for `sandbox:/mnt/data/*`, file-emission text patterns,
    and execution-claim co-occurrence
  - add replay and conflict tests (`same key+same hash` no-op; `same key+different hash` conflict)
- Execute followthrough plan from
  `docs/planning/sb_casey_jesuscrust_followthrough_20260207.md`:
  - implement SB observer/loss schema and refusal-path tests (`1.1`-`1.3`)
  - implement casey operation-contract tests (`2.1`-`2.5`)
  - formalize JesusCrust execution-boundary integration notes and ADR text
    (`3.1`-`3.5`)
- [P0] Execute tokenizer migration plan (regex → deterministic) with parity checks: DONE
  - `docs/planning/tokenizer_migration_plan_20260306.md`
  - GWB route payload parity:
    - `/graphs/wiki-timeline`
    - `/graphs/wiki-timeline-aoo`
    - `/graphs/wiki-timeline-aoo-all`
  - Existing SL ingest regression corpus:
    - `Mabo [No 2]`
    - `House v The King`
    - `Plaintiff S157`
    - `Native Title (NSW) Act 1994`
  - StatiBaker reducer and UI invariants:
    - shared canonical ID stability (same source text via SL/SB paths => same IDs)
    - no SB re-tokenization
    - compress -> expand invariant
    - no summary injection / no re-segmentation
    - context-bound rendering invariants
    - tool-use / chat-context metric stability
- [P1] Execute SL engine/profile followthrough from: DONE (v1 contract + tests)
  `docs/planning/sl_lce_profile_followthrough_20260208.md`:
  - draft domain-neutral engine spec (`docs/planning/compression_engine.md`)
  - define profile contracts (`docs/planning/profile_contracts.md`) for
    `sl_profile`, `sb_profile`, and `infra_profile` boundaries
  - define profile lint rules (`docs/planning/profile_lint_rules.md`) for
    forbidden axes/groups per profile
  - define cross-profile safety tests
    (`docs/planning/cross_profile_safety_tests.md`) that keep compression
    mechanics fixed while admissibility varies
  - Dependencies:
    - SL tokenizer contract: `SensibLaw/docs/tokenizer_contract.md`
    - lexeme layer baseline (see `[P0]` below)
    - decision: canonical token stream (lexeme-derived vs dedicated tokenizer)
    - deterministic multilingual tokenizer replacing regex (Layer‑1 only)
    - migration plan: `docs/planning/tokenizer_migration_plan_20260306.md`
- [P2] Perf-output compression lane:
  - use the resolved `Voxel Promotion and MDL` thread
    (`69c5de94-294c-83a1-a32b-5c1207e7e375`,
    canonical `eb14970bfedb1df596a888683fb509c2c269ef0c`,
    source `db`) as the design basis for a perf-specific pattern extractor
    and streaming MDL compressor
  - keep the binary output format and Fractran mini-compilation as the
    follow-on proof-of-concept path
  - do not treat output compression as solved until the encoding is
    fixture-backed and round-trippable
- Apply refreshed SB boundary guidance from
  `docs/planning/sb_casey_jesuscrust_followthrough_20260207.md`:
  - codify "post-mortem forensic analyzers are observers, not memory
    authorities" in SB interop docs/contracts
  - add acceptance checks ensuring forensic imports cannot mutate canonical
    memory without explicit promotion receipts
- Apply Moltbook feedback intake from
  `docs/planning/moltbook_feedback_alignment_20260208.md`
  (`u/DexterAI`, `u/FiverrClawOfficial`, `u/TipJarBot`):
  - add idempotency and correlation IDs as first-class SB provenance fields
    in event/interface contracts
  - define explicit reversible SB transition contract and belief-time snapshot
    query semantics ("what did we believe at time T?")
  - add replay tests for duplicate retries and partial-write recovery
  - define external-settlement ownership signals (e.g., Base) as observer
    evidence by default, with explicit promotion receipts required for

- Audit-safe capability posture maintenance:
  - keep `docs/planning/itir_capability_posture_20260208.md` updated when new
    “courtroom-grade”/receipts/trauma-context language is added elsewhere
  - add a lint/checklist step to block docs that claim `TARGET` capabilities as
    `CURRENT` without an explicit label or implementation reference
    canonical-state impact
- Implement Fuzzymodo selector DSL parser over
  `docs/planning/fuzzymodo/selector_dsl.schema.json`.
- Implement canonical serialization + hash generation aligned with
  `docs/planning/fuzzymodo/canonical_hashing.md`.
- Add fixture-driven tests for selector and norm-constraint examples in
  `docs/planning/fuzzymodo/fixtures/`.
- Implement Fuzzymodo exchange channels defined in
  `fuzzymodo/docs/interfaces.md`: selector ingress, norm ingress, facts feed,
  decision egress, and replay artifact emission.
- Implement the DB-backed `fuzzymodo -> StatiBaker` seam from
  `docs/planning/fuzzymodo_statiBaker_interface_20260309.md`:
  - SB-owned overlay extension tables for `fuzzymodo_selector_v1`
  - separate decision-ledger persistence with SB reference-only joins
  - end-to-end adapter tests proving no selector/norm authority transfer
- DONE: Casey exchange channels defined in
  `casey-git-clone/docs/interfaces.md` now exist in the local testbed:
  publish ingress, sync command, collapse command, build snapshot egress,
  `casey.facts.v1` export, and `fuzzymodo.casey.advisory.v1` handling.
- DONE: Casey -> fuzzymodo contract from
  `docs/planning/casey_fuzzymodo_interface_contract_20260319.md` is now
  implemented in the local testbed with end-to-end tests over the minimal
  alice/bob flow.
- DONE: Casey -> StatiBaker observer seam from
  `docs/planning/casey_git_clone_statiBaker_interface_20260309.md` and
  `docs/planning/casey_statiBaker_receipt_schema_20260319.md` is now
  end-to-end in the Casey CLI/runtime lane:
  - Casey `publish` / `sync` / `collapse` / `build` emit receipts
    automatically
  - Casey operation/build ledgers persist locally by default
  - Casey observer bundles are emitted for replay/debug
  - `casey_workspace_v1` overlays can be ingested directly into SB dashboard DBs
  - tests cover Casey-ledger lookup and SB overlay ingestion
- Next Casey lane:
  - feed real SL/LCE-derived signals into the optional Casey candidate feature
    bag so Casey -> fuzzymodo divergence reports rely less on Casey-local
    metadata and more on shared compression/representation facts
  - add tighter advisory acceptance tests for explanation-first gap payloads:
    primary-axis selection, structured gap items, and suggested-action
    stability for identical exports
  - expose the same receipt/observer controls through any future non-CLI Casey
    entrypoints so the seam does not remain CLI-only
  - DONE: add broader cross-component interface-conformance checks so Casey/fuzzymodo/SB
    payload fields stay locked across future changes (`casey-git-clone/tests/test_boundary_contract_shapes.py`
    covers core `casey.facts.v1` and `fuzzymodo.casey.advisory.v1` shape invariants)
  - DONE: Casey-vs-git benchmark surface now exists as
    `casey-git-clone/scripts/benchmark_casey_vs_git.py` with:
    - fixed `small/medium/large` tiers
    - `baseline_linear`, `divergence_native`, `build_freeze`, and
      `traceability_cost` lanes
    - both `cli` and `library` surfaces
    - detailed filesize/storage-accounting metrics, not just timing
    - JSON output plus Markdown summary
  - extend the Casey-vs-git benchmark with repeatability baselines and stored
    result snapshots so regressions are easier to compare over time
  - add an explicit interpretation lane for "Casey library vs subprocess git"
    so the repo can distinguish "competing with git if git were in Python"
    from the still-slower Casey CLI path
  - next Casey perf loop should focus on:
    - Python process startup on the CLI lane
    - remaining non-observer CLI command-path overhead after runtime batching
    - observer/receipt cost isolation inside `traceability_cost`
- Keep the JMD/ERDFA shard-graph integration surface documented as future
  awareness only per `docs/planning/jmd_itir_intended_surface_20260319.md`:
  - do not treat it as an active Casey/fuzzymodo/SB contract yet
  - wait for a pinned shard schema / concrete adapter target before code work
  - current reusable HF/shard reference surface is `kant-zk-pastebin`:
    - `src/sheaf.rs` already exposes shard-aware DASL/RDFa section metadata
    - `src/ipfs.rs` already bridges IPFS content addressing with DASL/CBOR
    - `src/bin/freeze_chats.rs` already emits `Shard` / `ShardSet` plus
      `manifest.cbor`
    - `monster` only contributes a consumer-side HF client pattern
    - `huggingface_hub_uploader` and `hugging-push` are generic wrappers, not
      the shard transport contract
  - if a shared publish/pull branch is revived later, align the artifact
    contract to `kant-zk-pastebin` first, then decide whether the runtime
    target is Zelph, ZOS, or a separate transport crate
  - use `docs/planning/zelph_kant_zos_shard_contract_matrix_20260327.md` as
    the current architecture note for the four-axis split:
    - sharder
    - sink
    - consumer runtime
    - shared artifact contract
  - use `docs/planning/shared_shard_artifact_contract_v1_20260327.md` as the
    canonical contract note for:
    - shard identity
    - selector resolution
    - sink abstraction
    - cache/invalidation
    - Zelph consumer obligations
    - ZOS publish/pull obligations
  - current best-fit read is hybrid, not winner-takes-all:
    - Zelph sharder for query-shaped reads
    - Kant sharder for publish/pull packaging
    - HF for practical hosted querying
    - IPFS for immutable publication
- Define the JMD object graph -> SL corpus graph bridge incrementally from
  `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md`:
  - use `docs/planning/jmd_triage_roadmap_20260320.md` as the canonical triage
    note so "JMD integration" stays split into:
    future shard/task surface vs near-term object-to-corpus bridge
  - DONE: pin the first fixture pack in:
    `docs/planning/jmd_fixture_v1_20260320.md`,
    `docs/planning/jmd_fixtures/jmd_sl_ingest_v1.example.json`, and
    `docs/planning/jmd_fixtures/sl_jmd_overlay_v1.example.json`
  - start with read-only JMD -> SL ingest payloads and reversible anchor
    generation only
  - keep SL outputs limited to advisory overlays and optimisation hints until a
    governed promotion path exists
  - preserve three-level identity mapping explicitly:
    JMD object id, SL anchor/group ids, and any higher-level cluster ids
  - route competing reorganisation proposals through Casey rather than letting
    SL or JMD auto-collapse them
  - keep StatiBaker limited to refs/digests/receipts for this bridge, not raw
    mutable corpus state
  - model Rabbit/topic routing and pastebin/IPFS persistence explicitly as JMD
    infrastructure assumptions in the first bridge ingest/overlay prototypes,
    rather than treating ERDFA as an embedding-style side lane
  - treat the currently adjacent concrete repos as the named reference
    implementation surfaces for that planning split:
    `kant-zk-pastebin` for paste/raw retrieval and `erdfa-publish-rs` for
    ERDFA shard production, without promoting either repo to a full runtime
    integration contract yet
  - keep any Rust-facing bridge work at the "programmable transform layer"
    boundary first; do not let Rust/plugin exploration silently become a
    canonical bridge contract before the object/anchor/overlay model is proven
  - define a first provenance-bundle ingest shape for JMD objects that can
    carry:
    binaries, source, debug symbols, traces, models, and prior events as
    linked bundle members rather than a single opaque blob
  - make the DASHI reading of that provenance bundle explicit:
    binaries = decoder/predictor family, source/debug symbols = hypothesis
    space, traces = observed signal, models = selected representative,
    events = causal filtration
  - keep the bridge role split explicit in docs and code:
    ERDFA/DASL = representation/addressing substrate,
    DASHI = quotient/invariance/MDL selection layer,
    SL = reversible anchor/overlay surface
  - when bridge scoring/proof fields are added, require quotient/collapse
    terminology rather than treating `mdl_gain` as a standalone truth scalar
  - add a local Casey/SL-side proof-carrying normalization prototype first;
    do not open a JMD PR until the local graph -> transform plan -> proof
    object loop is stable
  - DONE: local prototype now exists over runtime-bundle projections with
    focused tests and latest-post prototype inspection
  - keep current status explicit in docs:
    proof shape is implemented locally,
    host browse/raw stability is still uncertain,
    replay/cache policy is not yet pinned
  - add a local replay policy for unstable host surfaces:
    cached latest-index entries and cached resolved bundles for prototype
    inspection fallback
  - if a JMD-side PR is eventually needed, keep it tiny and optional:
    `sl:normal_form_cid`, `sl:mdl_proof_cid`,
    `sl:canonicalization_version`
  - add a first local proof object / transform-plan planning note in:
    `docs/planning/jmd_casey_mdl_contract_20260322.md`
  - reserve explicit bridge fields for:
    `corpus_root`, `pipeline_id`, `params_hash`, `metric_commitment`, and
    `score_commitment` so post-entropy style proofs can later attest to corpus,
    transform, and metric honesty without redesigning the object boundary
  - make post-entropy metrics corpus-relative by default in planning/docs:
    `mdl_gain` alone is not enough; maintain separate notions of compression
    gain, novelty/divergence from corpus, coverage/completeness, and replay
    validity
  - before any bridge code starts, require:
    one fixture-backed JMD ingest example, one fixture-backed SL anchor/overlay
    example, and explicit acceptance criteria for reversibility/provenance
  - next implementation followthrough:
    add fixture/schema validation or conformance tests over the pinned example
- Implement cross-project channel adapters and validators per
  `docs/planning/project_interfaces.md` for:
  `SensibLaw/`, `SL-reasoner/`, `tircorder-JOBBIE/`, `StatiBaker/`,
  `WhisperX-WebUI/`, `reverse-engineered-chatgpt/`,
  `chat-export-structurer/`, `notebooklm-py/`, `Chatistics/`,
  `pyThunderbird/`, `SimulStreaming/`, `whisper_streaming/`, and
  `itir-ribbon/`.
- Implement ITIR orchestrator control-plane checks from
  `docs/planning/itir_orchestrator.md`:
  context/planning ingress, contract routing validation, execution sync hooks,
  and artifact egress bookkeeping.
- Add an orchestrator manifest mapping producer->consumer exchange channels
  across all component `docs/interfaces.md` contracts.
- Add interface-contract conformance tests that verify required ingress/egress
  payload fields and provenance metadata across component boundaries.
- Execute four-way intersection followthrough from
  `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md`:
  - define shared exchange envelope schema (`itir.exchange.v1`) with
    `idempotency_key`, `correlation_id`, `causation_id`, and `payload_hash`
  - add adapter contract stubs for edge handoffs:
    TiRCorder->SL, SL->SB, SL->itir-ribbon, TiRCorder->SB, SB->itir-ribbon
  - add cross-component replay/conflict tests:
    same key+same hash no-op, same key+different hash conflict, belief-time
    replay reconstruction
  - add projection safety checks ensuring ribbon diagnostics cannot mutate SL/SB
    authoritative state without promotion receipts
- Resolve idempotency/dedupe cooperation decision queue from
  `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
  before freezing `itir.exchange.v1`:
  - ratify `Q1` timeline axis policy for unified Streamline semantics
  - ratify `Q2` SB "mechanical should" storage contract (flags vs imperative text)
  - ratify `Q3` narrative frame storage model
  - ratify `Q4` dual-role subject/object schema policy
  - ratify `Q5` action kit ontology placement (template vs remedy class)
  - ratify `Q6` authority-crossing conflict domain boundaries
  - ratify `Q7` customary law precedence/reconciliation policy
  - ratify `Q8` expansion trace depth defaults (raw IDs only vs reducer trace)
  - ratify `Q9` evidence overlap cardinality (many-to-many canonical referencing)
  - ratify `Q10` clinic-mode offline inference requirement
  - ratify `Q11` canonical reducer runtime ownership model
    (shared runtime + SL-governed semantics)
- Enforce SL shared-reducer reuse policy from
  `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`:
  - define shared canonical reducer contract surface (service/package + versioning)
  - add TiRCorder adapter contract: transcription/text -> canonical shared IDs
  - add SB adapter contract: reduced records reference canonical shared IDs
  - add drift guard checks that forbid introducing independent canonical token/
    concept identity stores in TiRCorder/SB without explicit ADR override
  - add conformance tests that local heuristic tags are non-canonical unless
    promoted via receipts
- Execute reducer ownership contract from
  `docs/planning/reducer_ownership_contract_20260208.md`:
  - ratify Option C ownership model and capture as ADR
  - define canonical reducer integration surface (package/service API) and
    compatibility matrix
  - add envelope metadata fields for reducer provenance:
    `reducer_runtime_version` and `semantic_contract_version`
  - add canonical consistency tests across SL/TiRCorder/SB integration paths
  - add cross-product identity tests: same text via TiRCorder path vs SB path
    resolves to identical canonical IDs for same reducer/profile version
  - add SB boundary tests asserting SB reducer changes cannot alter canonical
    token/concept identity assignments
- Apply canonical consumption matrix from
  `docs/planning/itir_consumption_matrix_20260208.md`:
  - add adapter conformance checks for declared producer/consumer paths
  - add explicit tests for authority-write null paths (Ribbon->state, SB->capture)
  - ensure diagnostics-only outputs stay non-authoritative without receipts
  - add semantic-anchor conformance checks that SB/TiRCorder labeling paths use
    SL-issued canonical IDs and do not define parallel equivalence logic
- Execute Concept/RuleAtom + Expansion + Contradiction contract from
  `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`:
  - add layer-boundary conformance checks: Concept identity layer vs RuleAtom
    logic layer references
  - add expansion-invariant checks over `C1`/`C2`/`C3`/`C4` reporting surfaces
    for SB SITREPs and receipts packs
  - add contradiction-finder fixtures for cross-system modality clashes and
    `needs_reconciliation` default outputs
  - ratify reconciliation policy linkage with `Q7` (precedence vs parallel
    authority policy)
- Execute TiRC->SL + Context Envelope + Promotion Receipt contract from
  `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`:
  - implement TiRCorder adapter path: transcript text -> shared canonical IDs
  - add conformance tests that TiRCorder heuristics remain non-canonical unless
    promoted via receipts
  - add context-envelope grounding tests that SB context is additive/read-only
    for SL interpretation flows
  - add authority-crossing receipt tests for required envelope linkage fields
    (`event_id`, `idempotency_key`, `payload_hash`, `correlation_id`,
    `causation_id`, authority classes)
- Execute Three Locks + Narrative Sovereignty contract from
  `docs/planning/three_locks_narrative_sovereignty_contract_20260208.md`:
  - implement Frame Compiler hard-fail checks for missing thesis/receipt/action
    locks
  - enforce claim->receipt anchor checks for all public artifact sentences
  - replace any exact "12-word only" gate with quality-gate policy
    (interpretable + receipt-backed + non-contradictory)
  - add anti-gaming tests:
    jargon-stuffed thesis, smooth unanchored thesis, jurisdiction-free action
- Re-run docTR timing on SensibLaw root PDFs using `/Whisper-WebUI/venv` (GPU if available) and record results in `doctr/PROFILE_RUNTIME_NOTES.md` on 2026-02-06.
- Implement timeline ribbon UI: conserved-quantity lens selector, conservation badge, lens inspector, segment tooltips, split/merge checks, and compare overlay (see `SensibLaw/docs/timeline_ribbon.md`).
- Wire ribbon UI to selector contract (`itir-ribbon/ui_contract.md`) and expose conservation metadata for Playwright tests.
- [P0] Implement SensibLaw lexeme layer tables + ingestion + tests (see `SensibLaw/docs/lexeme_layer.md`). DONE
  - Dependencies:
    - canonical text + span invariants (`SensibLaw/docs/tokenizer_contract.md`)
    - deterministic normalization (`SensibLaw/src/text/lexeme_normalizer.py`)
    - lexeme indexing (`SensibLaw/src/text/lexeme_index.py`)
    - storage tables in `SensibLaw/src/storage/versioned_store.py`
- Wire TiRCorder WhisperX-WebUI outputs to SB execution envelopes (adapter + tests + fixture). (Done)
- Fix missing TextSpan errors during PDF ingest for `Mabo [No 2]`, `House v The King`, `Native Title (NSW) Act 1994`, and `Plaintiff S157` (or add an explicit allow-missing-spans flag).
- Implement suite-level context safeguards: context-bound artifact view, epistemic state overlay, and context drift warnings (see `docs/user_stories.md`).
- Implement SL claim typing enforcement with inference-to-evidence graph requirements and denial pattern clustering (see `docs/user_stories.md`).
- Implement SB reputational exposure map and power asymmetry indicators (see `docs/user_stories.md`).
- Define Context Envelope JSON schema (see `docs/planning/adr_ctx_001.md`).
- Add UI invariant tests: no context-free rendering, no silent context loss, and
  irreversible compression (see `docs/planning/ui_context_components.md`).
- Wire Context Envelope validation into ingest and render paths (see
  `docs/planning/context_envelope_schema.md`).
- Implement UI invariant test harness entries for context drift, epistemic
  slider integrity, and interpretation-optional mode (see
  `docs/planning/ui_invariant_tests.md`).
- Draft database schema for context envelope storage (see
  `docs/planning/context_envelope_db_sketch.md`).
- Add minimal JSON fixtures for context envelope validation (see
  `docs/planning/context_envelope_fixtures.json`).
- Add UI invariant test runner template (see
  `docs/planning/ui_invariant_test_runner.md`).
- Choose a JSON Schema validator and wire fixture validation into CI (see
  `docs/planning/context_envelope_validate_stub.py`).
- [P2] Repo artifact hygiene followthrough:
  - DONE: clarify top-level/submodule SQLite risk in
    `docs/planning/git_artifact_hygiene_20260208.md`
  - DONE: stop treating `StatiBaker/runs/dashboard.sqlite` as a normal tracked
    sample artifact; private runs should use `runs_local/` / `SB_RUNS_ROOT`
  - next: audit remaining docs/scripts that still imply a checked-in dashboard
    DB is the normal way to reproduce or test SB locally

## Blockers / constraints
- No explicit blockers listed in submodule TODO files.
- reverse-engineered-chatgpt: send-message testing is stalled due to bot detection (noted in the ITIR-suite README), which may block any tasks that require message sending.
