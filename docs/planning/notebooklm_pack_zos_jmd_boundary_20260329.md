# notebooklm-pack vs ZOS/JMD boundary - 2026-03-29

## Scope

Assess the newly added sibling repo `../notebooklm-pack` against the current
`ZOS`, `JMD`, and `SL` boundary notes before treating it as evidence for any
bridge or push/pull expansion.

## Sources checked

- sibling repo:
  - `../notebooklm-pack/Cargo.toml`
  - `../notebooklm-pack/src/main.rs`
- existing repo notes:
  - `docs/planning/jmd_push_pull_surfaces_and_blockers_20260329.md`
  - `docs/planning/temp_zos_sl_bridge_impl_review_20260329.md`
  - `docs/planning/zos_sl_zelph_contract_findings_20260328.md`
- sibling docs path:
  - `/home/c/Documents/code/kant-zk-pastebin/DOCS.md`
  - status: symlink exists, but the target
    `/home/mdupont/DOCS/services/kant-pastebin/README.md` is not available in
    this environment

## What notebooklm-pack actually is

The sibling repo is a bounded Rust utility that:

- scans repos or a repo list
- collects text files by extension
- skips large vendor/build directories
- writes per-repo temporary text bundles
- clusters repos by sampled trigram Jaccard overlap
- emits at most a configured number of NotebookLM-ready source files

Its contract is operational and packaging-oriented, not semantic:

- input:
  repo paths
- processing:
  text collection plus lightweight n-gram clustering
- output:
  NotebookLM source packs and a manifest

## What it is not

It is not, by itself:

- a `ZOS <-> SL` contract surface
- a `JMD` object or push/pull contract
- a proof/admissibility layer
- a semantic manifold or resonance implementation
- evidence that JMD host semantics are pinned

It does not currently expose:

- `ZOS`
- `JMD`
- `SL`
- `Zelph`
- `Casey`
- admissibility
- manifold/domain semantics
- promotion/truth state

## ITIL reading

Service role:
- ingestion/packaging helper for NotebookLM source preparation

Service boundary:
- upstream convenience utility only

Current service value:
- faster repo-to-NotebookLM source packing

Current non-value:
- no change to the `ZOS`, `JMD`, or `SL` service boundary

## ISO 9001 reading

Quality interpretation:
- acceptable to use as a packaging helper
- not acceptable to cite as semantic or governance evidence

Acceptance rule:
- if used, record it as a source-pack preparation tool only
- do not promote it into bridge/governance docs as if it defined transport,
  proof, or truth boundaries

## Six Sigma reading

Main defect risk:
- category error

Failure mode:
- treating a repo-packing utility as evidence for `ZOS`/`JMD`/publish semantics

Control:
- keep notebook/source packing separate from semantic bridge and admissibility
  work

## C4 reading

If referenced inside this repo, it belongs at most in:

- tooling / preprocessing

It does not belong in:

- claim reconciliation
- `ZOS <-> SL` truth boundary
- `JMD` push/pull contract
- promotion or admissibility layers

## Decision

Treat `../notebooklm-pack` as a bounded external utility for NotebookLM source
packing only.

Do not use it to widen:

- `TEMP_zos_sl_bridge_impl`
- `itir_jmd_bridge`
- `ZOS <-> SL` contract claims
- JMD push/pull or receipt claims

Refined reading after live NotebookLM validation:

- the packer now participates in a real NotebookLM push/pull loop through the
  repo wrapper and local `notebooklm` CLI
- that strengthens the NotebookLM integration claim
- it still does not, by itself, strengthen any JMD receipt or transport claim
- the correct next JMD move is to freeze a minimal seam object and classify
  its fields into observer metadata versus receipt candidates

## Practical next step

If we want to reference it later, do so only as:

- repo-text collection helper
- NotebookLM source bundling helper

and keep all `ZOS`/`JMD`/truth-boundary claims pinned to the existing planning
notes, not to this pack.
