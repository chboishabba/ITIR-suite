# Workbench Implementation Spec

## Goal
Implement the graph/review interaction contracts for recent workbench pages with explicit state reason codes, bounded graph drill-in, and synchronized selection behavior.

## In scope
- `/arguments/thread/[threadId]`
- `/graphs/narrative-compare`
- `/graphs/wiki-revision-contested`
- Shared review-state helper and regression guards.

## Out of scope
- Global graph expansion across corpus.
- New extraction pipelines.
- Styling-system redesign.

## Success criteria
- All three pages expose explicit review state reasons.
- Narrative compare supports row selection + bounded graph drill-in.
- Thread workbench and contested wiki use consistent state signaling.
- Regression tests reference the new interaction model and state wiring.
