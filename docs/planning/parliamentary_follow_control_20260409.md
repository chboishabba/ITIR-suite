# Parliamentary Follow/Ranking Control

Date: 2026-04-09

## Purpose

Ensure parliamentary materials (debates, committee reports, ministerial statements) provide interpretive guidance in the Iraq/Brexit proving chains without outranking treaties, statutes, or binding cases; when the Iraq record evolves, keep this wording aligned so the broader-review summary keeps naming the latest event.

## Guidance

- Each parliamentary source adds a modest derived boost; our Iraq/Brexit proving checkpoints show how debates close contextual gaps while the follow artifact keeps speaker identity and challengeability metadata visible, ensuring the recommendation stays non-binding.
- Outputs list the boosted score plus the raw base, keeping ranking control transparent.
- Ranking remains bounded: parliamentary boosts only affect priority when they complement statutory paths, never replacing them.

## Tests

- `SensibLaw/tests/test_parliamentary_follow_control.py` verifies base score handling, multi-source stacking, and explicit source list.

## Residual Risks

- Fixture-based weights might need tuning once more parliamentary material varieties arrive; keep derived labels inspectable to avoid misleading operators.
