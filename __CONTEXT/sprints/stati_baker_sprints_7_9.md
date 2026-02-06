# StatiBaker Sprint Plan (7–9, 2026-02-05)

Source: continuation planning notes for post–Sprint 4–6 execution.

## Sprint 7 — Portability & Replay Integrity
Goal: export a self-describing bundle that replays deterministically.

Work items (implemented):
- Define bundle layout (`sb-bundle/` with state, drift, ledger, artifacts, manifest).
- Add bundle exporter and verifier.
- Cross-host replay test (same outputs or explicit rejection).

Acceptance criteria:
- Bundle contains hashes and policy receipts.
- `verify-bundle` recomputes drift and checks manifest hashes.

Non-goals:
- Sync or cloud distribution.
- Live updating.

## Sprint 8 — Time Hygiene & Long-Run Decay
Goal: document aging and saturation behavior without auto-deletion.

Work items (implemented):
- Document time-decay policy (what ages, what never ages, what expires).
- Define carryover saturation handling (labels only, no summaries).
- Calendar/inactivity stress test (ordering + carryover stability).

Acceptance criteria:
- Aging behavior is explicit and visible.
- No silent forgetting.

Non-goals:
- Importance scoring.
- Cleanup automation.

## Sprint 9 — Boundary Lock & Red Team Pass
Goal: surface failure modes and reject authority violations loudly.

Work items (implemented):
- Red-team scenarios (event injection, re-segmentation, summary injection, metric
  smuggling, command/RCE, credential leakage, path traversal).
- Add DoS/resource-exhaustion handling notes (refusal or saturation markers only).
- Failure mode catalog updates (`FAILURE_MODES.md`) with blast-radius rules.
- Map SB invariants to centralized failure classes (fast propagation, hidden coupling).
- Boundary assertions via tests.

Acceptance criteria:
- Violations are rejected or surfaced.
- No silent corruption paths.

Non-goals:
- Hardening for hostile environments.
