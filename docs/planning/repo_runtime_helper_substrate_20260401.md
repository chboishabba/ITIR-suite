# Repo Runtime Helper Substrate 2026-04-01

## Goal

Add one obvious shared home for script-level repo/runtime root resolution:

- `SensibLaw/src/storage/repo_runtime.py`

with the smallest useful surface:

- `resolve_repo_root(script_file: str | Path) -> Path`
- `resolve_sensiblaw_root(script_file: str | Path) -> Path`
- `relative_repo_path(path: str | Path, *, repo_root: Path) -> str`

## First adopters

Keep adoption narrow and boilerplate-focused:

- `SensibLaw/scripts/report_wiki_random_timeline_readiness.py`
- `SensibLaw/scripts/report_wiki_random_article_ingest_coverage.py`
- one manifest consumer:
  - `SensibLaw/scripts/run_fact_semantic_benchmark_matrix.py`

## Non-goals

- no manifest registry
- no export-policy changes
- no broad script-sweep migration

## Acceptance gate

- focused helper tests pass
- the first adopter scripts no longer derive repo/SensibLaw roots inline via
  hardcoded parent math
