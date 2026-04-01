# Repo Roots Substrate 2026-04-01

## Purpose

Provide one reusable owner for repo-root and SensibLaw-root resolution so
manifest-heavy scripts and reporting entrypoints stop duplicating the same
path boilerplate.

## Current state

- Shared helper:
  - `SensibLaw/src/storage/repo_roots.py`
- First adopters:
  - `SensibLaw/scripts/build_gwb_corpus_scorecard.py`
  - `SensibLaw/scripts/source_pack_manifest_pull.py`
  - `SensibLaw/scripts/source_pack_authority_follow.py`
  - `SensibLaw/scripts/report_wiki_random_timeline_readiness.py`
  - `SensibLaw/scripts/report_wiki_random_article_ingest_coverage.py`
- Existing tests:
  - `SensibLaw/tests/test_repo_roots.py`
  - `SensibLaw/tests/test_gwb_corpus_scorecard.py`
  - `SensibLaw/tests/test_wiki_random_timeline_readiness.py`
  - `SensibLaw/tests/test_wiki_random_article_ingest_coverage.py`

## Read

- Repo-root / SensibLaw-root path derivation is a reusable substrate, not lane
  cleanup.
- The helper should be shared across scripts that consume manifests, produce
  scorecards, or need repo-relative path shaping.
- This sits below the SQLite/runtime substrate work and above any local
  cosmetic cleanup.

## Next

- Adopt `repo_roots.py` in the remaining manifest-aware scripts that still
  hard-code their repo/path bootstrap.
- Keep the helper small and avoid growing it into a general manifest registry.
