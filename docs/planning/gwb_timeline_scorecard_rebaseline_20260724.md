# GWB Timeline Scorecard Rebaseline

Date: 2026-07-24

## Decision

The versioned regression baseline for the current GWB corpus is:

```text
223 document-local source-backed event rows
```

The earlier test expectation of 320 is preserved as a superseded,
unreconciled expectation. The corpus is not padded, duplicated, or silently
reclassified to satisfy the older number.

The machine-readable receipt is:

```text
baselines/gwb_timeline_scorecard_v0_2.json
```

and can be checked with:

```text
python scripts/check_gwb_timeline_baseline.py --observed-count 223
```

## Scope

This is a regression inventory baseline. It measures the local event rows
admitted by the versioned corpus and current counting contract.

It does not assert:

- that 223 is a complete history of the George W. Bush period;
- that every cross-document overlap has been reconciled;
- that the event braid is globally linear or complete;
- that absent events do not exist;
- that a local event candidate has been promoted to historical truth.

That distinction follows the existing event-braid doctrine:

```text
source -> local event -> candidate cross-source edge -> partial-order braid
```

Only source-backed lineage may support wider reconciliation, and uncertain
branches remain explicit.

## Change rule

A later baseline may differ from 223 only through a new receipt identifying:

- the exact source revisions;
- the source-admission profile;
- the deduplication/counting contract;
- added or removed event-lineage references;
- why the prior baseline no longer represents the curated corpus.

A changed count without those coordinates is a regression failure, not an
implicit rebaseline.
