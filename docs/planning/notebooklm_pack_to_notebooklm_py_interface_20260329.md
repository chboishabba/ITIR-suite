# notebooklm-pack to notebooklm-py interface - 2026-03-29

## Goal

Define the clean interface between the sibling `../notebooklm-pack` utility and
the existing NotebookLM lanes already documented in this repo.

The point is not to widen `ZOS`, `JMD`, or `SL` semantics.
The point is to make `notebooklm-pack` usable as an upstream source-pack
producer for the NotebookLM interfaces we already own.

## Existing suite posture

Current NotebookLM surface in this repo already has three useful layers:

1. source ingress
   - `notebooklm-py/docs/interfaces.md`
   - Channel A: notebook/source ingress
2. observer and metadata capture
   - `StatiBaker/docs/notebooklm_connector.md`
   - `docs/planning/notebooklm_metadata_review_parity_20260311.md`
3. additive interaction capture
   - `docs/planning/notebooklm_interaction_capture_contract_20260311.md`

That means the missing piece is not downstream consumption.
The missing piece is an explicit upstream source-pack handoff.

## What notebooklm-pack contributes

The sibling Rust tool already does one bounded job well:

- collect text across repos
- cluster repo content into a bounded number of NotebookLM-ready source files
- emit a manifest describing those source files

That maps cleanly onto NotebookLM source ingress.

## Service reading

ITIL:
- `notebooklm-pack` = source preparation service
- `notebooklm-py` = notebook operation and artifact generation service
- `StatiBaker` / `SensibLaw` = observer, reuse, and downstream review service

These should remain separate services with explicit handoffs.

## Quality reading

ISO 9001:
- accept `notebooklm-pack` as a deterministic packer only
- require manifest-backed traceability from packed source file to downstream
  notebook/source/artifact observations

Every later NotebookLM source loaded from a packed file should be traceable
back to:

- pack run
- contributing repos
- output source file
- content hash

## Defect reading

Six Sigma:
- main defect risk is provenance loss between:
  - packed repo bundle
  - NotebookLM source object
  - later NotebookLM artifacts
- second defect risk is over-clustering unrelated repos into one source file

Controls:
- keep the pack manifest
- keep content hashes
- preserve contributing repo lists
- never treat a pack cluster as a semantic truth object
- reject oversized packed sources before upload:
  - `500000` words per source
  - `200 MiB` per local file upload

## C4 placement

Container order:

1. repo corpus
2. `notebooklm-pack`
3. `notebooklm-py` source ingress
4. NotebookLM operations/artifacts
5. StatiBaker metadata and interaction capture
6. SensibLaw reuse/read-model lanes

This is a tooling-to-observer path, not a truth-promotion path.

## Proposed interface contract

### Channel P1: Pack production

Producer:
- `../notebooklm-pack`

Input:
- repo list file or repo root directory
- max source count

Output:
- packed NotebookLM source files
- manifest entries with:
  - `file`
  - `repos`
  - `words`
  - `bytes`

Recommended additions if wrapped from this repo:
- `pack_run_id`
- `created_at`
- `source_file_hash`
- `repo_scan_root`
- `max_sources`

### Channel P2: NotebookLM source ingress

Consumer:
- `notebooklm-py`

Input:
- packed source files from P1
- optional target notebook id / title
- optional import directives or notebook creation policy

Output:
- NotebookLM source state
- notebook identifiers
- source identifiers when available

### Channel P3: Observer linkage

Consumer:
- `StatiBaker` NotebookLM connector

Input:
- normal NotebookLM metadata and interaction capture

Required linkage fields to retain or derive:
- notebook id/hash
- source title
- source status
- source URL or local ingest reference if present
- pack run id if known
- source file hash if known

### Channel P4: Downstream reuse

Consumer:
- `SensibLaw`
- other source/review lanes

Use:
- source-local snippet reuse
- artifact review
- notebook/source coverage reporting

Non-use:
- not a direct truth-promotion lane
- not a `ZOS` or `JMD` semantic contract

## Minimal repo-side wrapper shape

If implemented later, the wrapper should be tiny:

1. run `notebooklm-pack`
2. read the emitted manifest
3. compute hashes for packed source files
4. enforce NotebookLM-safe per-source upload caps
5. ingest those files through `notebooklm-py`
6. persist a small linkage record mapping:
   - pack run
   - packed file
   - contributing repos
   - NotebookLM notebook/source ids

## Recommended schema additions

If we add a local linkage artifact, keep it bounded:

### pack run record
- `pack_run_id`
- `created_at`
- `input_mode`
- `input_ref`
- `max_sources`
- `max_words_per_source`
- `max_bytes_per_source`

### packed source record
- `pack_run_id`
- `source_file`
- `source_file_hash`
- `repos`
- `words`
- `bytes`

### notebooklm link record
- `pack_run_id`
- `source_file_hash`
- `notebook_id`
- `notebook_title`
- `notebook_source_id`
- `captured_at`

## Decision

The correct integration is:

- `notebooklm-pack` as upstream pack producer
- `notebooklm-py` as source-ingest and operation surface
- `StatiBaker` as observer/metadata layer
- `SensibLaw` as downstream read/reuse consumer

Do not integrate it as:

- a `ZOS` bridge
- a `JMD` bridge
- a semantic classifier
- a proof or admissibility surface

## Immediate next step

If implementation is desired, the first bounded change should be:

- a small wrapper or manifest-normalizer that:
  - runs `notebooklm-pack`
  - normalizes the emitted manifest with `pack_run_id`, `created_at`, and
    source file hashes
  - prepares deterministic `notebooklm-py` source-ingest commands
  - records notebook/source linkage when real ingest is enabled

Implementation posture:
- dry-run first
- explicit command plan output before any live NotebookLM mutation
- live ingest only when auth/context is already available

Current implementation status:
- landed wrapper:
  - `scripts/notebooklm_pack_ingest.py`
- landed focused regression coverage:
  - `tests/test_notebooklm_pack_ingest.py`
- current wrapper supports:
  - normalizing `notebooklm-pack` manifest output
  - computing source file hashes
  - emitting `pack_run` and `packed_sources` linkage records
  - producing a deterministic `notebooklm` command plan
  - optional live execution behind `--execute`
  - automatic discovery of the local `notebooklm` CLI from the repo `.venv`

## Live validation result

Live validation is now complete against the local authenticated NotebookLM
environment.

What was confirmed:

- local auth is present and usable
- live notebook creation works
- live packed-source upload works
- live source waiting works
- live source/artifact/status listing works
- the wrapper now works without manual shell `PATH` injection

Real mismatches discovered and fixed during validation:

- `notebooklm create --json` returns a nested `notebook` object rather than a
  top-level `id`
- `notebooklm source add --json` returns a nested `source` object rather than
  a top-level `source_id`
- this local CLI version does not support `--interval` on `source wait`
- the wrapper originally assumed a globally installed `notebooklm` binary,
  while the live executable here is at
  `/home/c/Documents/code/ITIR-suite/.venv/bin/notebooklm`

Persistent validation notebook now kept:

- title:
  `ITIR notebooklm-pack integration`
- notebook id:
  `ad2bbd9a-2c9c-47ee-a607-f2b735999d99`
- notebook url:
  `https://notebooklm.google.com/notebook/ad2bbd9a-2c9c-47ee-a607-f2b735999d99`

Current seeded linkage artifact:

- result artifact:
  `/home/c/Documents/code/ITIR-suite/.cache_local/notebooklm_pack_runs/20260329_persistent_integration_seed/result.json`
- manifest:
  `/home/c/Documents/code/ITIR-suite/.cache_local/notebooklm_pack_runs/20260329_persistent_integration_seed/pack_out/manifest.json`

Observed success signal from the kept notebook:

- NotebookLM produced a coherent summary describing the notebook as a
  two-source integration over `notebooklm-py` and the packer seam, which is a
  practical confirmation that the pack->ingest loop is working as intended.

Current remaining gap:
- later StatiBaker linkage enrichment is still open
- JMD alignment is still conceptual only until the seam object and
  receipt-vs-observer distinction are frozen explicitly

That is the honest interface seam.
