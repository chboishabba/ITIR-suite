# Git Artifact Hygiene (ITIR-suite) (2026-02-08)

## Problem statement
ITIR-suite produces many local artifacts (logs, dashboards, SQLite archives, exports).
We need to ensure these do not accidentally get committed/pushed to GitHub.

This is both:
- privacy/sensitivity (chat previews, local telemetry, tokens/cookies)
- repo hygiene (large binary churn, noisy diffs)

## Repo topology note: superproject + submodules
This workspace is a superproject with many git submodules (e.g. `StatiBaker/`).

Important consequence:
- A top-level `.gitignore` does **not** apply inside submodules.
- Each submodule needs its own ignore and/or output directory discipline.

## Current guardrails (superproject)
Top-level `.gitignore` already ignores common sensitive artifacts:
- `*.sqlite`, `*.sqlite3`, `*.db`, logs, secrets, and `storage_state.json` (NotebookLM cookies/tokens).
We added:
- `docs/_site/` (built docs site output).

## Current guardrails (StatiBaker submodule)
StatiBaker historically has a tracked `runs/` directory in its own repo, which means:
- generating dashboards under `runs/` will dirty tracked files
- those changes are easy to accidentally commit

To avoid this, we changed the default runs root used by SB scripts:
- Default runs root is now `runs_local/` (gitignored).
- Override via `SB_RUNS_ROOT` environment variable if you explicitly want a different location.

Changes made:
- `StatiBaker/.gitignore`: ignore `runs_local/`
- `StatiBaker/scripts/run_day.sh`: uses `RUNS_ROOT="${SB_RUNS_ROOT:-$ROOT_DIR/runs_local}"`
- `StatiBaker/scripts/run_day_notebooklm_auto.sh`: writes NotebookLM artifacts under the same runs root
- `StatiBaker/scripts/build_dashboard.py`: default `--runs-root` is `$SB_RUNS_ROOT` or `<sb-root>/runs_local`
- `StatiBaker/docs/web_module_map.md`, `StatiBaker/README.md`: updated docs to refer to `<runs-root>/...`

## Recommended practice
1. Treat `runs_local/` as the default "private workspace" artifact root.
2. Keep tracked sample outputs (if any) separate and never write personal runs into them.
3. Before pushing, check both:
   - superproject status: `git status`
   - submodule statuses: `git submodule foreach --recursive 'git status --porcelain | head'`

## Known cleanup opportunity (tracked sensitive files)
If any sensitive artifacts are already tracked in git history (e.g. chat sqlite DBs, WAL/SHM files),
`.gitignore` is not sufficient: they should be removed from tracking and ideally scrubbed from history.

This note is deliberately separate from implementation so it can be handled with appropriate care.

## Gitleaks note (false positives vs real leaks)
We observed `gitleaks detect` flagging a false positive in `data/pdfs/sample.json`
(`tokenizer_id: lexeme_normalizer_v1` matched the generic API key rule due to
the `token*` substring).

Mitigation:
- Add the exact fingerprints to `.gitleaksignore` so future scans are clean
  without weakening the generic ruleset.

