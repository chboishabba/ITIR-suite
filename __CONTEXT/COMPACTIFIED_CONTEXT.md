# Compactified Context (ITIR-suite)

## 2026-02-06
- Documented suite-wide user stories and invariants for context preservation,
  claim typing, and pattern-only exposure across ITIR/SL/SB.
- Added "context is mandatory" invariant and knowledge-state overlay notes to
  `docs/itir_model.md`.
- Updated `TODO.md` with implementation tasks tied to the new user stories.
- Added ADR-CTX-001 and supporting UI and doctrine specs in `docs/planning/`.
- Added Context Envelope schema draft and UI invariant test checklist; added
  front-page context line to `README.md`.
- Added Context Envelope DB sketch, fixtures, and test runner template in
  `docs/planning/`.
- Added validation notes to context schema and a stub validator script in
  `docs/planning/`.
- Added `docs/planning/README.md` with validation stub guidance.

## 2026-02-07
- Synced live conversation `698686e2-6e48-839e-ad0f-91e6fa4697f8`
  (`OSS-Fuzz Bug Detection`) via `re_gpt.cli --view` with network approval.
- Confirmed latest assistant reply timestamp
  `2026-02-07T03:05:48.055634Z`.
- Captured selector-DSL direction as the current normative-graph focus for
  follow-on planning and implementation.
- Added phase/layout scaffolding for Fuzzymodo selector DSL across
  `.planning/phases/16-fuzzymodo-selector-dsl/`,
  `docs/planning/fuzzymodo/`, and `fuzzymodo/`.
- Added separate Casey Git Clone scaffold across
  `.planning/phases/17-casey-git-clone/`,
  `docs/planning/casey-git-clone/`, and `casey-git-clone/`.
- Defined intended intersections, interaction flow, and exchange channels
  inside `fuzzymodo/docs/interfaces.md` and
  `casey-git-clone/docs/interfaces.md`.
- Updated both project READMEs and `TODO.md` so implementation tasks map
  directly to the new channel contracts.
- Expanded the same interface-contract structure across all core ITIR component
  directories and added suite index `docs/planning/project_interfaces.md`.
- Documented ITIR-suite explicitly as orchestration control plane in
  `README.md` and added `docs/planning/itir_orchestrator.md` with channel-level
  orchestration contract.
- Moved detailed ITIR object model ownership to
  `SensibLaw/docs/itir_model.md` and reduced root `docs/itir_model.md` to a
  control-plane pointer.
- Refreshed live conversation `698686e2-6e48-839e-ad0f-91e6fa4697f8` and
  confirmed newer assistant state at `2026-02-07T03:05:48.055634Z`.
- Added conversation step mapping artifacts:
  - `docs/planning/fuzzymodo/conversation_step_map.md` (updated)
  - `docs/planning/fuzzymodo/speculation_policy.md` (new)
  - `docs/planning/casey-git-clone/conversation_step_map.md` (new)
- Implemented Fuzzymodo evaluator + speculation primitives and tests:
  - `fuzzymodo/src/selector_dsl/evaluator.py`
  - `fuzzymodo/src/selector_dsl/speculation.py`
  - `fuzzymodo/tests/test_evaluator.py`
  - `fuzzymodo/tests/test_speculation.py`
- Implemented Casey core model + non-blocking operations and tests:
  - `casey-git-clone/src/casey_git_clone/models.py`
  - `casey-git-clone/src/casey_git_clone/operations.py`
  - `casey-git-clone/tests/test_models.py`
  - `casey-git-clone/tests/test_operations.py`
- Added project changelogs:
  - `fuzzymodo/CHANGELOG.md`
  - `casey-git-clone/CHANGELOG.md`
- Added evidence-first ITIR definition source file from chat archive extracts:
  - `__CONTEXT/ITIR_DEFINITION_CONTEXT.md`
- Added ITIR definition ratification draft with explicit accepted/rejected/pending clauses:
  - `__CONTEXT/ITIR_DEFINITION_RATIFICATION.md`
- Applied user adjudication to six key definition snippets:
  - marked `investigative operating system` and `one system/modes` as qualified
    metaphors/doctrine, not canonical runtime identity.
  - affirmed `ITIR-suite` meta-repo/control-plane and SB product distinction.
  - re-scoped `re-segment time` as boundary guardrail, not default ITIR action.
