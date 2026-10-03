# GOV-1 / REL / INV architecture diagrams

This bundle is the repo-owned PlantUML view of the GOV-1 integrated control case and the REL/INV investigative loop.

The diagrams intentionally keep separate:

- semantic authority and UI projection;
- Pareto frontier membership and access/executability;
- service/change state and evidence/certification state;
- MatterContext visibility and privacy/security processing authority;
- runtime receipts and formal proof premises;
- acquisition priority and truth, evidence independence, semantic admission, or access authority.

Files:

1. `01_system_context.puml` — C4-style suite context.
2. `02_container_control_boundaries.puml` — authority/control containers.
3. `03_control_case_trace.puml` — UserStory → Requirement → Risk → Control → Evidence → CAPA → Release.
4. `04_inv_acquisition_sequence.puml` — REL residual → INV acquisition → canonical source → selective reopening → Compare_q.
5. `05_gui_projection_semantics.puml` — Investigate / Inspect / Graph projections and UI firewalls.
6. `06_deployment_trust_boundaries.puml` — local-first deployment, PII/provider/formal boundaries.
7. `07_service_evidence_lifecycle.puml` — ITIL-like service lifecycle versus evidence state.

The standards attached to GOV-1 are engineering control lenses and do not by themselves establish certification.
