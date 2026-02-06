# StatiBaker Sprint Plan (2026-02-05)

Source: planning discussion captured in `__CONTEXT/CONTEXT.md` (see “StatiBaker Sprint Plan” section).
Scope: StatiBaker core, adapters, and contracts only. No UI work.

## Sprint 1 — SB Core Hardening & Temporal Trust
Goal: make SB boringly correct across repeated days.
Primary artifacts: guard tests, invariants doc section, multi-day replay logs.

Acceptance criteria:
- Guard tests exist and pass: SB never re-tokenizes, summarizes, or promotes artifact content.
- Re-running the same day yields identical outputs.
- Carryover ages correctly across multiple days.
- Daily brief is structurally readable without interpretation.

Non-goals:
- No new adapters.
- No OCR.
- No UI changes.

## Sprint 2 — External Observation Without Authority
Goal: ingest external signals without letting them define SB boundaries.
Primary artifacts: Wazuh lifecycle adapter, Prometheus adapter, determinism tests, `/metrics` endpoint.

Scope:
- Wazuh lifecycle adapter (boot, suspend/resume, network up/down, service restarts only).
- Prometheus adapter (numeric summaries only; must not create/split activity events).
- SB `/metrics` endpoint (health counters only).
- Determinism tests (same input → same signals; failure → missing data noted).

Non-goals:
- No alerting dashboards.
- No interpretation of failures.

## Sprint 3 — Boundary Definition & Read Surfaces
Goal: define safe integration contracts so future work cannot contaminate SB.
Primary artifacts: OCR adapter contract, Android status contract, read-only query surface spec.

Scope:
- OCR adapter contract (design-only; snapshots in, derived artifacts out; manual promotion only).
- Android status contract (coarse signals only).
- Read-only query surface (list events, carryover, provenance).
- ITIR ingest validation (activity_event immutability; annotation-only overlays).

Non-goals:
- No OCR runtime.
- No recall UI.

## Recommended sequence
1. Sprint 1
2. Sprint 2
3. Sprint 3

Rationale: lock SB as a temporal reducer before ingesting external signals or defining integration contracts.
