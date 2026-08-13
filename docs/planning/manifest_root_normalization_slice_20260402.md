## Manifest Root Normalization Slice

Date: 2026-04-02

Decision:
- introduce one small shared owner for manifest-path resolution and JSON
  object loading instead of repeating local path math and ad hoc
  `json.loads(path.read_text(...))` in separate lanes

First scope:
- `SensibLaw/src/fact_intake/acceptance_fixtures.py`
- `SensibLaw/scripts/source_pack_manifest_pull.py`

Shared owner:
- `SensibLaw/src/storage/manifest_runtime.py`

Boundary:
- keep this helper narrow
- it may resolve repo-owned manifest/data paths and load top-level JSON
  objects
- it should not become a generic serialization framework

Reason:
- the remaining duplication is now manifest-root and manifest-load policy, not
  more repo-root bootstrap work
- this gives one more reusable Python/store/runtime win before the user-story
  alignment pass

Acceptance:
- acceptance-fixture manifest defaults use the shared root/path helper
- source-pack pull uses the shared JSON-object manifest loader
- focused fixture and source-pack tests stay green
