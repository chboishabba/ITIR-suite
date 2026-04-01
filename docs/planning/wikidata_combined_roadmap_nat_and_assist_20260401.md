# Wikidata Combined Roadmap: Nat And Assist

Date: 2026-04-01

## Purpose

Record the current execution-order roadmap across:

- the Nat migration lane
- the broader Peter/Ege/Rosario assist lane

## Current Progress

### Nat

- bounded mainline: complete
- wider proof lane: complete
- wider online lane: held pending better reviewer-packet support
- non-company axis integration only, meaning the current company-focused
  tranche is a calibration step rather than a new expansion

### Assist Lane

- still partial and review-first
- continue only with materially broader bounded coverage

## Recommended Order

1. build the generic Nat reviewer-packet layer:
   - contract
   - parser
   - bounded follow receipts
   - packet attachment to held split rows
2. use that packet layer to make the wider Nat review-and-split lane more
   usable at scale
3. continue Cohort C only as a distinct policy-risk branch
4. advance the assist lane only when broader bounded coverage or better
   culprit-oriented reporting is real

## Why This Order

Nat already proved:

- checked-safe handling
- wider direct-safe scarcity
- split-plan verification

So the highest-value next layer is reviewer throughput, not more proof that the
hard rows are hard.
