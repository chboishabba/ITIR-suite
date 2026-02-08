# Grafana Integration: Metrics Scope + Non-Reimplementation Boundary (2026-02-08)

## Goal
Use Grafana as the visualization/alerting surface for ITIR-suite operational metrics without rebuilding Grafana inside ITIR.

ITIR should:
- emit metrics/logs/traces in standard formats
- optionally consume alert signals and a small amount of query output for summaries
- avoid building its own time-series UI, alerting UI, dashboard editor, or query builder

## Core principle: Grafana is the glass, ITIR is the pipe
Grafana:
- dashboards, panels, alert rules, on-call routing (if used), annotations
- correlation across data sources (Prometheus/Loki/Tempo/etc.)

ITIR:
- produces high-signal telemetry with stable naming and low-cardinality labels
- consumes alerts as *observer signals* (not authoritative memory)
- links humans to Grafana for drill-down rather than re-rendering charts

## What we should feed into Grafana (outbound from ITIR)

### 1) Metrics (Prometheus-style)
Operational, privacy-safe, time-series metrics about ITIR components.

Strong default: Prometheus scrape endpoint (`/metrics`) per service.
Fallback: Pushgateway only for batch jobs (avoid push unless necessary).

#### Metric families we care about
**A. Orchestration health**
- `itir_orchestrator_runs_total{status}`
- `itir_orchestrator_run_duration_seconds_bucket{status}`
- `itir_orchestrator_active_runs` (gauge)
- `itir_orchestrator_queue_depth` (gauge)

**B. Context pipeline / envelope build**
- `itir_context_envelope_build_total{status}`
- `itir_context_envelope_build_duration_seconds_bucket{status}`
- `itir_context_envelope_tokens_total{lane}` (counts, not raw text)
- `itir_context_envelope_truncations_total{reason}`
- `itir_context_sources_included_total{source_type}` (chat_export, git, file, transcript, etc.)

**C. Reducer / replay / provenance mechanics**
- `itir_replay_attempts_total{status}`
- `itir_idempotency_conflicts_total{component}`
- `itir_partial_write_recoveries_total{component}`

**D. Connectors / ingest**
- `itir_ingest_events_total{connector,status}`
- `itir_ingest_lag_seconds{connector}` (gauge)
- `itir_ingest_backfill_total{connector,status}`

**E. Crisis-advocacy module (CAM)**
(No PHI. Meta-only.)
- `itir_cam_envelope_activations_total{envelope_id,status}` (keep envelope_id low-cardinality; consider bucketing by class)
- `itir_cam_actions_total{action_type,status}`
- `itir_cam_stop_on_success_total`
- `itir_cam_policy_refusals_total{reason}`

**F. Safety and refusals**
- `itir_guardrail_refusals_total{guardrail,reason}`
- `itir_impersonation_flags_total{channel}`

**G. Infra and resource**
Prefer node-exporter/cAdvisor/etc. for CPU/memory/disk. ITIR only emits app-level resource gauges if they are meaningful:
- `itir_worker_memory_rss_bytes` (optional)
- `itir_db_query_duration_seconds_bucket{db,query_class}`

#### Label policy (avoid cardinality bombs)
Allowed labels (stable, low-cardinality):
- `component`, `connector`, `status`, `action_type`, `source_type`, `reason`, `env`

Avoid labels like:
- user IDs, emails, patient identifiers, message IDs
- `correlation_id` as a label
- unbounded free-text or filenames

If we need per-run correlation, use traces + exemplars (see below), not metric labels.

### 2) Logs (Loki)
Ship structured JSON logs to Loki via promtail/agent.
Requirements:
- include `correlation_id`, `causation_id`, `idempotency_key` in log fields (not labels)
- include `component`, `level`, `event_type`
- redact/suppress PHI by default; prefer hashes/IDs that map back to local authoritative stores

### 3) Traces (Tempo / OpenTelemetry)
Use OpenTelemetry tracing across orchestrator + connectors + reducers.
Requirements:
- propagate `trace_id` across service boundaries
- attach `correlation_id` as a span attribute
- use exemplars from metrics to traces if available

### 4) Annotations (optional, but useful)
Use Grafana annotations to mark:
- deployments
- schema freezes
- connector outages
- large backfills / replays

This keeps “why did the graph change?” inside Grafana without building our own incident UI.

## What we should get from Grafana (inbound to ITIR)

### 1) Alert notifications (primary)
Grafana Alerting can POST to a webhook. Treat these as an *observer feed*:
- alert fired/resolved
- severity
- labels (service/component)
- link to dashboard/panel/rule

ITIR should ingest these as:
- non-authoritative signals that can trigger operator attention, runbooks, or safe automation
- link-first artifacts (store Grafana URL + minimal fields)

### 2) “What’s broken?” summaries (optional, thin)
If we want ITIR to produce a daily/weekly sitrep:
- query Grafana API for current alert states and a small set of “headline metrics” (last value only)
- embed links to Grafana dashboards for drilldown

Hard rule: do not reproduce charts or build a dashboard renderer in ITIR.

### 3) Dashboard URLs as first-class references
Store canonical links (by UID/panel ID) in ITIR docs/runbooks so agents can route humans to “the glass” instantly.

## Health data vs “health of the system”
Be explicit:
- Grafana is appropriate for *system health* and *pipeline health*.
- Grafana should not be used to store or visualize PHI/medical record content.

If “health” metrics are needed:
- emit meta-only counts and states (export succeeded, connector lag, record counts)
- never emit patient-level details, names, diagnoses, or free-text

## Minimal integration plan (no Grafana reimplementation)
1. Emit Prometheus metrics (`/metrics`) from the orchestrator and key adapters.
2. Ship structured logs to Loki (or keep local logs if Loki isn’t in scope yet).
3. Add OpenTelemetry tracing for cross-component latency and correlation.
4. Ingest Grafana alert webhooks into an `observer:grafana_alerts` lane.
5. Add a “sitrep” command that summarizes current alert states and links to Grafana dashboards.

## Open questions (to decide before implementation)
- Data plane: Prometheus vs Grafana Agent vs OTEL Collector as the central collector?
- Hosting: local docker-compose vs existing org Grafana stack?
- Where do we store Grafana references (UIDs, dashboard links) so they are stable across environments?
- Do we need on-call escalation (Grafana OnCall) now, or just alert webhooks?

