# Wikidata Hotspot Eval Adapter Boundary V2 (2026-03-25)

## Decision
If the hotspot lane ever adds live execution, `v2` should allow only a thin
adapter-command wrapper.

It should not add:

- direct provider SDKs
- provider-specific auth/config handling
- free-form answer normalization inside `SensibLaw`
- prompt optimization logic

## Why
The current `v1` evaluator is strong because it is:

- deterministic
- replayable
- provenance-safe
- separable from model-running policy

Adding direct provider logic would blur the line between:

- structural benchmark generation/scoring
- model orchestration infrastructure

That is a poor fit for this repo.

## Allowed `v2` surface
If needed later, permit:

- `sensiblaw wikidata hotspot-eval --adapter-command ...`

Where the adapter command:

- is fully external to `SensibLaw`
- receives enough context to run the questions
- returns the same normalized response-bundle schema already accepted by `v1`

The adapter wrapper would be convenience-only. It would not redefine the
canonical evaluator contract.

## Required invariants
Any `v2` adapter-command feature must preserve:

- the existing response-bundle schema as the truth-bearing handoff
- deterministic replay from saved response bundles
- no hidden provider fallback behavior
- no hidden normalization from raw prose to `yes` / `no` / `abstain`
- fake-adapter test coverage before any real-run examples are accepted

## Out of scope
Still out of scope after this note:

- direct OpenAI/Anthropic/etc. integration in the hotspot evaluator
- API key/env management inside hotspot CLI code
- model selection policy inside `SensibLaw`
- treating live execution as required for benchmark validity

## Promotion rule
Only build the adapter-command wrapper if a real workflow is blocked by
external response-bundle generation alone.

Until then, keep live execution outside `SensibLaw`.
