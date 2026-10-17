---
name: autonomous-orchestrator
description: Runs restartable autonomous orchestration loops across Antigravity and Codex, using shared durable state files, bounded fanout delegation, ZKP framing, and MCP control tools.
---

# Autonomous Orchestrator (Antigravity & Codex Unified)

This skill provides an autonomous, restartable orchestration control plane for long-running multi-agent research and engineering across both **Antigravity** and **Codex**.

It bridges:
1. **Antigravity subagents & background tasks** (`invoke_subagent`, `manage_task`, `schedule`)
2. **Codex CLI & tmux runners** (`codex --yolo exec`)
3. **Model Context Protocol (`itir-mcp`)**: `itir.ao.status`, `itir.ao.claim_lane`, `itir.ao.heartbeat`, `itir.ao.report_result`, `itir.ao.gap_check`
4. **StatiBaker Runsheet & Kanboard**: Native ingestion of `.autonomous-orchestrator/` states via `sb.ao_kanboard_control`
5. **Exact PNF Gap Comparator**: Provenance-backed difference $\Delta_{\text{Gap}} = \mathcal{M}_{\text{informal}} \ominus \mathcal{M}_{\text{formal}}$

---

## 1. Canonical Control Plane (`.autonomous-orchestrator/`)

Every runner (whether executed under Antigravity or Codex) reads and writes to the shared directory:

- `status.json` or `status.<id>.json`: Current state machine snapshot.
- `heartbeat.<id>.json`: Periodic liveness proof with `state` (`busy`, `done`, `blocked`, `degraded`, `stalled`), phase, current step, and child PID.
- `registry.json`: Live roster of all active and held runners across all lanes.
- `lane_claims/<id>.json`: Active lane reservation (`--lane`, `--lane-claim`, `--parent-orchestrator-id`).
- `parent_reports/<parent>.json`: Rolling history of completion, validation, and escalation receipts.

---

## 2. Bounded Delegation Policy

The control plane enforces strict fanout bounds to prevent infinite agent recursions:

- **Root Orchestrator** may launch up to 6 Section Managers.
- **Section Managers** may launch up to 6 Worker descendants.
- **Workers** are leaves and may NOT spawn further descendants.
- **No Repeated Refinement Rule**: A lane may refine an ambiguous blocker once. The subsequent result must be material code progress, a typed compiler failure (with exact symbol/error), or an authority escalation. A second blocker-map-only report is rejected.

---

## 3. ZKP Problem Framing Standard (`O, R, C, S, L, P, G, F`)

Every child run and delegated subtask must begin and report back with the compact ZKP frame:

- **O (Objective)**: Concise statement of what is being proven or implemented.
- **R (Reality)**: Current verified ground truth from repo files / proof ASTs.
- **C (Context)**: Upstream dependencies, threads, or specifications involved.
- **S (Scope)**: Exact files or boundaries permitted to be modified.
- **L (Limits)**: Constraints, invariant preservation, or performance bounds.
- **P (Plan)**: Discrete, falsifiable steps.
- **G (Gaps / $\Delta_{\text{Gap}}$)**: Exact unformalized premises or unaddressed formal invariants.
- **F (Formal Receipt)**: The cryptographic hash, compiler exit code, or PNF multiset equality proof.

---

## 4. MCP Tools Reference (`itir-mcp`)

When running in Antigravity or Codex with MCP enabled, invoke:

- `itir.ao.status`: Query the entire active runner registry, claims, and heartbeats.
- `itir.ao.claim_lane`: Secure a lane claim before starting execution.
- `itir.ao.heartbeat`: Pulse liveness during execution.
- `itir.ao.report_result`: Record completion or escalation with ZKP frame into the parent report.
- `itir.ao.gap_check`: Compute exact multiset difference against an Agda/Lean formal AST.

---

## 5. Python Runner Invocations

The colocated runner can be launched directly:

```bash
# Antigravity/Codex shared runner:
python3 /home/c/.codex/skills/autonomous-orchestrator/orchestrator.py \
  --orchestrator-id physics_lead_1 \
  --lane physics_unification \
  --lane-claim "Navier Stokes C/D bounds on dashi_lean4#53" \
  --loop
```

Or via Antigravity subagent invocation:
```python
invoke_subagent(
    TypeName="self",
    Role="Navier-Stokes Section Manager",
    Prompt="Claim lane 'physics_unification' with ID 'ns_fefferman_cd' and discharge A2 high-envelope invariants."
)
```
