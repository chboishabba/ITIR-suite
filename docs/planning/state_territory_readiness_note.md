# State Regulation & Territory Readiness Note (2026-04-04)

State regulations and US territories already fit the normalized contract provided the pipeline retains the same invariants: clear contract completeness, provenance, live/fallback visibility, translation/alignment boundedness, and follow-readiness.

For US territories we introduce a `territory_hybrid_risk` signal that captures when a source unit needs both federal oversight and territorial authorization before it can be promoted.

Key expectations:

* `readiness_signals.territory_hybrid_risk` must be present and true for territory-based records so governance knows the risk class needs human coordination even when other contract fields pass.
* The normalized contract remains the same; the hybrid signal does not block, but it must be visible via metrics/control surfaces so follow operators can trigger extra confirmation steps.

This note informs the metrics extension that now surfaces the hybrid signal as a readiness metric.
