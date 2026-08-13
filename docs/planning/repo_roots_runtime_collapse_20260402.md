## Repo Roots Runtime Collapse

Date: 2026-04-02

Decision:
- keep one canonical root/bootstrap substrate in
  `SensibLaw/src/storage/repo_roots.py`
- remove the duplicate `SensibLaw/src/storage/repo_runtime.py`

Reason:
- the remaining `repo_runtime.py` surface only duplicated script-file-based
  repo-root and `SensibLaw`-root resolution that now belongs with the shared
  repo-roots owner
- the remaining adopters were bounded script bootstrap surfaces, so the cut is
  high-signal and low-risk

Result:
- `repo_roots.py` now owns:
  - canonical repo root helpers
  - canonical `SensibLaw` root helpers
  - script-file-based root resolution
  - repo-relative path shaping with external-path fallback
- remaining script adopters now import `repo_roots.py` directly

Acceptance:
- focused repo-root and adopter script tests stay green
- no remaining imports of `src.storage.repo_runtime`
