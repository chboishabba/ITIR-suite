# Deterministic Speaker Inference v1

## Summary

Speaker inference for transcript/message corpora must remain a reviewed,
deterministic downstream layer. It is not part of canonical token identity and
must not invent speakers from weak evidence.

This v1 design covers message archives, bracketed chat transcripts, and future
TiRCorder/ITIR transcript material. It explicitly supports abstention.

## Allowed evidence signals

Primary signals:
- explicit speaker labels in the source text
- known participant sets supplied with the source
- message/turn structure and adjacency
- timestamp continuity
- reviewed disagreement/entropy heuristics where the corpus already preserves
  competing narratives or turn ownership structure

Secondary signals:
- sentiment/concern style overlays may be used only as weak tie-breakers after
  primary structural evidence has narrowed the candidate set

Disallowed as primary assignment signals:
- subtitle timing ranges alone
- open-world identity linking
- generative guesses
- sentiment/emotion scores by themselves

## Output contract

Each inferred assignment should emit:
- candidate speaker ID or canonical local label
- confidence tier
- explicit reason codes
- evidence receipt describing which deterministic signals were used
- abstention reason when no safe assignment can be made

The inference layer must preserve the distinction between:
- observed speaker labels
- inferred speaker assignments
- unresolved turns

## Current repo alignment

- TiRCorder already has sentiment utilities and planning/docs that treat
  sentiment as an overlay layer, not as transcript identity.
- Transcript adapter tests currently forbid emitting `summary`, `sentiment`,
  `intent`, `emotion`, or `diagnosis` fields in the base adapter output.
- Current TODO direction already points toward known participants plus
  disagreement/entropy heuristics rather than speculative inference.

## Deferred work

- Formalize deterministic disagreement/entropy heuristics for speaker
  coalescence in DASHI/ITIR terms.
- Define how participant rosters enter the inference path for archive/chat
  sources.
- Add fixture-backed acceptance tests only after those heuristics are pinned.
