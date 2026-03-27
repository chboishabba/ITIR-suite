# Workspace Coordination Boundary (2026-03-27)

This note decides whether the current cross-repo work should move into a new
top-level project directory or continue across the existing repositories.

## ZKP Frame

O:
- User plus current workspace repositories.
- `ITIR-suite` is the suite-level orchestrator/control plane.
- `dashi_agda` owns upstream formal/perf witness material.
- `FRACDASH` owns the compressed executable/formal bridge subset.
- Other repos remain producer- or consumer-specific components.

R:
- Avoid creating a new project directory unless it reduces ambiguity rather
  than duplicating governance.
- Keep component ownership clear.
- Keep suite-level planning/context in one canonical place.
- Allow new subprojects only when they have independent runtime/build or
  transport semantics.

C:
- `ITIR-suite/docs/planning/itir_orchestrator.md`
- `ITIR-suite/docs/planning/itir_mcp_dioxus_contract_20260326.md`
- `ITIR-suite/COMPACTIFIED_CONTEXT.md`
- `ITIR-suite/TODO.md`
- `ITIR-suite/CHANGELOG.md`
- cross-repo state in `dashi_agda/` and `FRACDASH/`

S:
- `ITIR-suite` already declares itself the orchestration layer for the
  workspace and already owns cross-project planning/context.
- `FRACDASH` already has strong repo-local memory, but it is specific to the
  executable/formal bridge lane rather than the whole suite.
- `dashi_agda` is authoritative for its own upstream formal source surface and
  should not become the global coordination repo.
- A new top-level coordination repo would currently duplicate planning files,
  TODOs, and context without adding a distinct runtime boundary.
- A dedicated subproject is still justified when it introduces a real adapter
  or transport surface, for example `ITIR-suite/itir-mcp/`.

L:
- ad hoc cross-repo work
- declared suite orchestrator
- canonical coordination boundary
- optional dedicated subprojects when runtime semantics justify them

P:
- Continue working across the existing repositories.
- Use `ITIR-suite` as the canonical coordination/control-plane repo for
  cross-repo planning, context, and promotion decisions.
- Keep repo-local contracts and implementation notes inside the owning repo.
- Do not create a new top-level project directory for coordination alone at
  this stage.
- Revisit the boundary only if a new coordinator needs its own build/runtime,
  release cycle, or transport contract that does not fit as an `ITIR-suite`
  subproject.

G:
- No new coordination repo without a distinct executable/runtime purpose.
- Cross-repo decisions must be recorded in `ITIR-suite` first.
- Repo-local semantics remain authoritative in the owning repository.

F:
- The missing piece was an explicit boundary decision, not a missing folder.
- Future reevaluation trigger: coordination logic grows into a standalone
  runtime rather than docs/context/orchestration only.

## Decision

Use `ITIR-suite` as the control plane and continue working across several
repositories.

Do not create a new top-level project directory now.

## Practical rule

- Put suite-level planning, cross-repo TODOs, and coordination notes in
  `ITIR-suite`.
- Put upstream formal/perf source work in `dashi_agda`.
- Put executable bridge/compression runtime work in `FRACDASH`.
- Create a new project directory only when it is a genuine product/adapter
  with its own runtime boundary, similar to `ITIR-suite/itir-mcp/`, rather
  than a second control-plane repo.
