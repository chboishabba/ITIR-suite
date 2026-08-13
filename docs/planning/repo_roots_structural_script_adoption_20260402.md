## Repo Roots Structural Script Adoption

Date: 2026-04-02

Decision:
- continue the canonical `repo_roots.py` adoption through the tested
  structural-review script family before widening further

Scope:
- `SensibLaw/scripts/build_wikidata_structural_handoff.py`
- `SensibLaw/scripts/build_wikidata_structural_review.py`
- `SensibLaw/scripts/build_wikidata_dense_structural_review.py`
- `SensibLaw/scripts/build_gwb_broader_corpus_checkpoint.py`

Reason:
- these scripts still carried local `REPO_ROOT` / `SENSIBLAW_ROOT` bootstrap
  math even after the canonical root substrate existed
- they already have focused regression coverage, so this is a safe
  high-signal adoption slice

Result:
- the structural-review family and adjacent broader-checkpoint script now
  source repo and `SensibLaw` roots from
  `SensibLaw/src/storage/repo_roots.py`
- local root boilerplate is reduced without changing artifact semantics

Acceptance:
- focused Wikidata structural and broader checkpoint tests stay green
- source-level checks pin `repo_root()` / `sensiblaw_root()` adoption in the
  adopted scripts
