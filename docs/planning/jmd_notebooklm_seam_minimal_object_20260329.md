# JMD NotebookLM seam minimal object - 2026-03-29

## Goal

Disambiguate the smallest useful JMD-facing object for the now-live
NotebookLM pack/ingest loop without pretending that NotebookLM metadata is
already a JMD transport or proof contract.

This note is driven by the broader March 29 conversation:

- `notebooklm-pack` is valid as NotebookLM source preparation
- `notebooklm-py` is a real NotebookLM push/pull surface
- the live loop is now validated locally
- `JMD` still remains a separate receipt/proof/transport question

## Broader conversation alignment

The current repo conversation already pins four relevant boundaries:

1. `SL` remains truth authority
2. `ZOS` remains proposal-side and must re-enter through admissibility
3. `JMD` remains a future external object/receipt/transport surface, not a
   generic synonym for "anything with metadata"
4. NotebookLM is useful as an external notebook/artifact loop, but still sits
   in an observer/preparation lane unless explicitly promoted

So the goal is not "make NotebookLM into JMD".
The goal is to define the smallest seam object that can later be consumed by a
bounded JMD bridge if that becomes useful.

## ITIL reading

Service split:

- `notebooklm-pack`:
  source preparation
- `notebooklm-py`:
  NotebookLM push/pull
- `StatiBaker`:
  observer capture
- future `JMD` bridge:
  external object/receipt projection

Current service outcome:

- pack manifest to NotebookLM notebook/source linkage is now operational

Current service non-outcome:

- no JMD receipt contract yet
- no JMD transport contract yet

## ISO 9001 reading

The seam object is acceptable only if:

- every field is provenance-backed
- nothing in the object implies semantic authority it does not have
- it is possible to distinguish receipt-grade fields from observer metadata
- the object can be mapped forward without lossy reconstruction

## Six Sigma reading

Primary defect to avoid:

- treating ordinary observer metadata as if it were a receipt or proof object

Secondary defect:

- losing the chain between pack source, NotebookLM source, and later artifact

Control rule:

- classify each field as either:
  - identity/linkage
  - observer metadata
  - receipt candidate

## C4 placement

This seam belongs between:

1. notebooklm-pack manifest output
2. notebooklm-py notebook/source/artifact state
3. future StatiBaker capture
4. future optional JMD projection

It does not belong inside:

- `SL` truth promotion
- `ZOS` ranking/admissibility
- affidavit claim reconciliation

## Minimal seam object

Recommended name:

- `NotebookLMExternalLink.v1`

Minimum fields:

- `seam_id`
- `created_at`
- `pack_run_id`
- `source_file_hash`
- `source_file`
- `contributing_repos`
- `notebook_id`
- `notebook_title`
- `notebook_source_id`
- `notebook_source_title`
- `artifact_ids`
- `capture_mode`
- `observer_class`

### Field meaning

- `pack_run_id`:
  ties the object back to a concrete pack execution
- `source_file_hash`:
  the strongest identity anchor for the packed source payload
- `notebook_id` and `notebook_source_id`:
  external NotebookLM object linkage
- `artifact_ids`:
  additive downstream outputs, possibly empty
- `capture_mode`:
  `dry_run`, `execute`, or later observer replay mode
- `observer_class`:
  explicit reminder that this object is observational unless promoted

## Mapping asked for in the conversation

### Map pack run, source hash, notebook id, source id, artifact id

Direct mapping is:

- pack run -> `pack_run_id`
- source hash -> `source_file_hash`
- notebook id -> `notebook_id`
- source id -> `notebook_source_id`
- artifact id(s) -> `artifact_ids`

These are enough to reconstruct the live external linkage without inventing
transport semantics.

## Receipt vs observer metadata

### Observer metadata

Treat these as observer metadata by default:

- `notebook_title`
- `notebook_source_title`
- source status
- summary text
- artifact counts
- source counts
- generated NotebookLM prose summaries

These are useful, but they are not proof-carrying receipts.

### JMD receipt candidates

Treat these as receipt candidates only if later wrapped in a proper JMD
contract:

- `pack_run_id`
- `source_file_hash`
- immutable manifest path or digest
- artifact id plus export ref, when linked to a stable captured artifact
- execution environment lineage fields if later added

The distinction is:

- observer metadata says what the external system reported
- a JMD receipt says what this repo is willing to treat as a stable,
  replayable, audit-grade acknowledgement object

## Decision

For the current NotebookLM seam:

- define the seam object now
- keep it observational now
- do not call it a JMD receipt yet

Use the seam object to preserve linkage.
Only call something a JMD receipt once the wire/object contract is explicit
enough to support replay, acknowledgement, and proof expectations.

## Practical next step

1. Freeze `NotebookLMExternalLink.v1` as the bounded seam object
2. Persist or emit it beside the existing result artifact
3. Classify fields explicitly as observer metadata vs receipt candidates
4. Only after that, decide whether a tiny JMD projection is worthwhile
