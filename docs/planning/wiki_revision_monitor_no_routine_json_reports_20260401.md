# Wiki Revision Monitor No Routine JSON Reports 2026-04-01

## Purpose

Freeze the revision-monitor export posture after the SQLite-first query/runtime
 work:

- SQLite is the canonical operational store
- query/read models are the structured access surface
- routine JSON sidecars are not a valid report format or storage layer

## Decision

On the default runner path:

- do not write pair-report JSON artifacts
- do not write contested-graph JSON artifacts
- do not treat pair-report or graph paths as routine runtime-state fields

If a human-facing artifact is needed later, it should be generated on demand
from SQLite as a real presentation/export surface such as HTML, not persisted
automatically as JSON.

If machine-facing sharing is needed later, the trusted posture is:

- logical artifact identity
- artifact revision
- content digest
- sink refs
- acknowledgement / receipt

not routine local JSON files or local filesystem paths.

## Scope

Primary code surfaces:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`
- `SensibLaw/src/wiki_timeline/revision_pack_summary.py`
- `SensibLaw/src/wiki_timeline/revision_monitor_read_models.py`

Primary contract/tests:

- `SensibLaw/docs/wiki_revision_pack_runner_contract_v0_3.md`
- `SensibLaw/tests/test_wiki_revision_pack_runner.py`
- `SensibLaw/tests/test_revision_pack_summary.py`
- `SensibLaw/tests/test_revision_monitor_query.py`
- `SensibLaw/tests/test_revision_monitor_read_models.py`

## Governance

- ITIL:
  treat this as a standard-change contraction of duplicate report surfaces
- ISO 9000:
  one canonical source, one explicit export process
- Six Sigma:
  remove variance caused by duplicate JSON report outputs
- C4:
  keep canonical behavior in the SQLite/read-model container, not in routine
  artifact files
