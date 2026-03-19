# Casey Git Clone x Fuzzymodo Interface Contract (2026-03-19)

## Purpose
Define the minimal read-only handoff from `casey-git-clone` into `fuzzymodo`
so Casey can externalize its candidate lattice for reasoning without
transferring workspace/collapse authority.

## Resolved context
- Casey surface doctrine sharpened on 2026-03-19:
  - `SL` provides the shared representation substrate
  - `casey-git-clone` owns mutable possibility state (`S/L`) and operational
    publish/collapse/build surfaces
  - `fuzzymodo` owns selector/query reasoning (`R`) and compression-gap style
    comparison (`F_c`)
  - `StatiBaker` remains the observer-only governance memory layer
- Supporting archived/live thread metadata already recorded in:
  - `COMPACTIFIED_CONTEXT.md`
  - `__CONTEXT/COMPACTIFIED_CONTEXT.md`

## Boundary statement
`casey-git-clone` may cross into `fuzzymodo` only through a read-only exported
candidate-state payload.

`fuzzymodo` may:
- query Casey candidate/path/workspace/build facts
- rank or filter candidates
- emit advisory recommendations and gap reports

`fuzzymodo` must not:
- mutate Casey runtime state
- choose or trigger collapse directly
- become the source of truth for Casey workspaces, trees, or builds

## Intended role split
- Casey answers: what candidate realities currently coexist?
- fuzzymodo answers: which candidate realities best satisfy constraints or unify
  cleanly?

## Channel mapping

### Channel A: Casey lattice export
- Producer: `casey-git-clone`
- Consumer: `fuzzymodo`
- Transport:
  - JSON-serializable Python structure first
  - file/CLI adapter acceptable for the local Casey testbed
- Stability rule:
  - same Casey tree/workspace/build state -> same export payload

### Channel B: Advisory decision return
- Producer: `fuzzymodo`
- Consumer: `casey-git-clone`
- Transport: structured JSON-serializable result
- Authority rule:
  - advisory only
  - Casey may render, inspect, or optionally consume the result, but Casey
    remains the only component that performs collapse/build decisions

## Minimal Casey export payload

```json
{
  "casey_export_version": "casey.facts.v1",
  "tree_id": "tree-...",
  "workspace": {
    "ws_id": "alice",
    "user": "alice",
    "head_tree_id": "tree-...",
    "policy": {
      "prefer_author": "alice",
      "tie_break": "stable_hash"
    },
    "selection": [
      {
        "path": "src/main.c",
        "selected_fv_id": "fv-..."
      }
    ]
  },
  "paths": [
    {
      "path": "src/main.c",
      "candidate_count": 2,
      "selected_fv_id": "fv-...",
      "candidates": [
        {
          "fv_id": "fv-a",
          "blob_id": "blob-a",
          "author": "alice",
          "created_at": "2026-03-19T10:00:00+00:00",
          "base_fv_id": "fv-base",
          "summary": null
        },
        {
          "fv_id": "fv-b",
          "blob_id": "blob-b",
          "author": "bob",
          "created_at": "2026-03-19T10:01:00+00:00",
          "base_fv_id": "fv-base",
          "summary": null
        }
      ]
    }
  ],
  "build": null
}
```

### Required semantics
- export only explicit Casey state:
  - tree id
  - workspace id/user/policy/selection
  - path candidate sets
  - candidate provenance fields already known to Casey
- preserve candidate multiplicity; do not collapse the lattice in export
- expose selected candidate separately from candidate membership
- support optional build context when reasoning is scoped to an existing frozen
  build

### Forbidden semantics
- raw blob bytes in the core reasoning export
- implicit “best candidate” claims from Casey
- hidden normalization that rewrites candidate lineage

## Minimal fuzzymodo advisory payload

```json
{
  "fuzzymodo_result_version": "fuzzymodo.casey.advisory.v1",
  "tree_id": "tree-...",
  "workspace_id": "alice",
  "path_results": [
    {
      "path": "src/main.c",
      "recommended_fv_id": "fv-a",
      "candidate_rankings": [
        {
          "fv_id": "fv-a",
          "score": 0.92,
          "reason_codes": ["selector_match", "preferred_author"]
        },
        {
          "fv_id": "fv-b",
          "score": 0.61,
          "reason_codes": ["selector_match"]
        }
      ],
      "gap": {
        "gap_kind": "candidate_divergence",
        "severity": "medium",
        "explanation": "two viable candidates remain unresolved"
      }
    }
  ],
  "evaluated_at": "2026-03-19T10:02:00+00:00"
}
```

### Required semantics
- advisory ranking only
- explicit path scoping
- explicit gap payload, even if gap is `none`
- deterministic output for same selector + same Casey export

### Forbidden semantics
- mutation commands
- “collapse now” instructions
- hidden policy imports that would make fuzzymodo the governance owner

## Current implementation reality
- `casey-git-clone` currently implements:
  - deterministic model/operation primitives
  - Casey-owned local runtime store
  - local CLI testbed over init/workspace/publish/sync/collapse/build
- `casey-git-clone` does not yet implement the Casey -> fuzzymodo export
  adapter defined here.
- `fuzzymodo` currently implements:
  - selector evaluation primitives
  - hashing/canonicalization
  - speculation/retirement helpers
- `fuzzymodo` does not yet implement the Casey-specific advisory adapter or the
  richer per-path ranking/gap return payload defined here.

## Decision
The contract is confirmed at the documentation level.

What is confirmed:
- the seam is read-only from Casey to fuzzymodo
- Casey exports lattice/provenance state
- fuzzymodo returns advisory rankings + gap reports
- Casey retains collapse/build authority

What remains to implement:
- Casey export adapter over runtime/tree/workspace/build state
- fuzzymodo Casey-evaluation adapter consuming that export
- end-to-end tests for export -> advisory result over the minimal Casey testbed
