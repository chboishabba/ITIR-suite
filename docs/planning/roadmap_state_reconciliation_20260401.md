# Roadmap / State Reconciliation 2026-04-01

## Purpose

Freeze the live substrate status before the major user-story pass so the next
implementation rounds are chosen from actual code state rather than stale TODO
language.

## Read

- Root docs were lagging the current substrate work.
- The most important mismatch was in the wiki revision monitor lane and the
  `chat_context_resolver` / wiki-timeline runtime seams.
- Remaining AAO Svelte route-shell work is now mostly presentation-only and
  should not outrank Python/store/runtime normalization.

## Current state

- The active meta-priority is:
  - shared Python/store/runtime owner first
  - cross-lane reuse second
  - local cleanup last
- The wiki revision monitor lane is now materially closer to canonical form:
  - SQLite-first read models
  - no DB blob fallback
  - no query-time JSON fallback
  - default timeline/AOO extraction now runs in-process
- The remaining writer-side revision-monitor state is narrower than older docs
  implied, but not fully artifact-free:
  - duplicate/default-path JSON sidecars were reduced
  - some runner-side JSON artifacts still remain as temporary tool-input or
    export-only surfaces pending final contract cleanup
- `chat_context_resolver` is materially thinner than the older roadmap still
  implied.
- Generic and AAO wiki-timeline runtime policy now sit behind Python-owned
  query/runtime helpers; remaining Svelte residue is demoted unless it reveals
  hidden runtime logic.

## Remaining pre-user-story rounds

1. One real roadmap/state reconciliation round across root docs and repo-local
   TODO/context files.
2. One remaining wiki revision monitor contract-cleanup round.
3. Maybe one or two more cross-lane substrate promotions only if they are
   clearly high leverage.

## Governance

- ITIL:
  treat this as a controlled prioritization correction before the next work
  package.
- ISO 9000:
  the documented state must match the implemented state before broader product
  prioritization.
- Six Sigma:
  remove planning variance caused by stale status signals before selecting the
  next lane.
- C4:
  keep canonical behavior in shared Python/store/runtime containers, not route
  shells or routine JSON artifacts.

## Immediate consequence

Do not start the major user-story pass yet.

First, freeze one nonblocking lane per worker across:

- roadmap/state reconciliation
- remaining wiki revision monitor contract cleanup
- one or two clearly high-leverage cross-lane substrate promotions
