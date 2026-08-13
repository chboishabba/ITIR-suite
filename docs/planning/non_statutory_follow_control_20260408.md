# Non-Statutory Authority Follow Control

Date: 2026-04-08

## Purpose

Ground the limited proof/control surface for standards, inquiries, and regulator guidance linking into statutory or case-based follow artifacts without implying they carry binding force.

## Guidance

- Each non-statutory vouch (standard, inquiry, regulator guidance) adds a fixed boost to follow rank yet keeps the final output clearly labeled as derived/non-binding.
- Outputs display both the base priority and the boost, so operators can see how the non-statutory layer nudged the follow ordering toward statute/case mapping.
- Mixed scenarios (standard+statute, inquiry+reform, regulator-guidance+enforcement) remain bounded within the normalized follow/ranking surface; no new ingestion is triggered.

## Tests

- `SensibLaw/tests/test_non_statutory_follow_control.py` checks base score, multi-source stacking, and default handling.

## Residual Risks

- The weight schedule is fixture-driven; if real volumes require dynamic scaling, follow this surface with caution and adjust weights before promoting to broader policy.
