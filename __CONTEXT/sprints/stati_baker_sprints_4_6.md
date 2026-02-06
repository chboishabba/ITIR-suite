# StatiBaker Sprint Plan (4–6, 2026-02-05)

Source: continuation planning notes for post–Sprint 1–3 execution.

## Sprint 4 — Stress, Absence, and Drift Characterisation
Goal: validate SB honesty under missing/partial data and characterize drift without acting on it.

Work items:
- Drift signal probes (read-only counters only).
- Absence/failure runs (no git activity, Wazuh off, Prometheus down, partial logs).
- Manual review of 5–7 consecutive daily briefs.
- Document drift concepts in `DRIFT_SIGNALS.md`.

Acceptance criteria:
- Explicit gaps when inputs are missing.
- Drift indicators exist but do nothing.
- No semantic language creeps into SB outputs.

Non-goals:
- No Phase-2 compression.
- No UI.
- No OCR runtime.

## Sprint 5 — Phase-2 Compression (Selective)
Goal: implement minimal Phase-2 compression guided by real usage.

Work items:
- Go/no-go decision for Phase-2 based on Sprint 4 findings.
- Implement 1–2 loss profiles with explicit expansion contracts.
- Tests proving compress → expand preserves declared structure.
- Brief-level validation for truthfulness and carryover visibility.

Acceptance criteria:
- Loss profiles are explicit and tested.
- Expanded views reproduce original structure within declared loss.

Non-goals:
- No ML or heuristic prioritization.
- No cross-day “insights.”

## Sprint 6 — Read Surfaces, Agents, and Containment
Goal: expose SB state read-only without authority leakage.

Work items:
- Finalize read-only query surface (CLI/MCP/HTTP).
- Agent containment rules (no re-segmentation, no summary injection).
- ITIR overlay validation hard reject on mutation attempts.
- Explicit Android adapter decision (implement or defer).

Acceptance criteria:
- Stable read surface with provenance.
- ITIR ingest contract enforced by tests.

Non-goals:
- No autonomous agents.
- No personalization.
