# AO-OP-1 — Canonical evidence-to-handoff operator workflow

Status: source-written, **not locally executed or CI-verified**. GitHub main is the code authority; canonical structurer archive owns corpus records, re-gpt owns transport receipts, and SensibLaw/SLR owns semantic/formal evidence.

## Roadmap and user-story boundary

The suite is comparatively mature at provenance and review, but lacks low-friction end-to-end operator workflows. AO-OP-1 addresses the shared evidence-to-review handoff used by ITIR-US-11/12/15/16 and the suite-wide context and no-unreviewed-authority invariants. It does not complete their full UI or domain-specific acceptance criteria.

Root ROADMAP.md remains intentionally unchanged: open PR #34 owns overlapping AO/Dioxus roadmap/planner work. This slice is independent of that PR.

## Operator contract

Read-only MCP tool: `itir.ao.operator_workflow`. Required: `archive_db` (explicit canonical SQLite locator), `candidates` (1–64 objects, unique canonical_thread_id, explicit bounded task_atom and optional typed/PNF/repo/formal receipt references). Optional: `max_items` (1–8), `operation_receipts` (default false), `receipt_db` (mandatory when operation_receipts is true). No model, reasoning-effort, create-thread or transport controls.

The tool composes the existing `build_frontier` ledger and typed-reference validator, `build_work_packet` and `governed_handoff` bounded source selections, and `operation_review`. It returns only candidate dispositions, source digests, typed status, PNF packet ID, operation disposition, next-review action and truncation/absence receipts. Task content is represented by a digest, not echoed. Output is bounded to 24,000 serialized characters; oversized results fail closed. Selection is sorted by canonical ID and capped; omission is explicit.

A completed transport operation alone is not semantic or formal verification. Missing canonical source, ambiguous source identity, held typed reference, absent semantic PNF/SLR producer, missing receipt locator, or async_starting/commit_unknown produces a hold. The current lexical packet does not establish verified semantic PNF: the workflow abstains from promotion. Reviewable candidate does not mean dispatchable. No source bodies, session secrets, transport credentials, automatic retries, resends, browser/DOM fallback, roster writes, archive writes, or direct POST.

## Acceptance and independent verification

```bash
python -m unittest discover -s tests -p 'test_operator_workflow.py' -v
python -m unittest discover -s tests -p 'test_frontier_evidence_engine.py' -v
python -m unittest discover -s tests -p 'test_frontier_typed_references.py' -v
python -m unittest discover -s tests -p 'test_pnf_work_packet_provider.py' -v
python -m unittest discover -s tests -p 'test_governed_revival_handoff.py' -v
ruff check itir-mcp/src/itir_mcp/operator_workflow.py itir-mcp/src/itir_mcp/frontier_tools.py tests/test_operator_workflow.py
```

Also run a caller-owned production smoke from `cwd=itir-mcp` with `PYTHONPATH=src`, using a temporary canonical SQLite fixture, `build_default_registry().invoke("itir.ao.operator_workflow", payload)`, and asserting a successful tool envelope, held/unverified authority and unchanged fixture corpus. No real account, browser or external service is needed.

These are intended commands only; no local tests or CI were run during the GitHub-only implementation.

## Exclusions and formalization gap

Excluded: PR #34 planning, root roadmap rewrite, legacy daemon, UI, autonomous dispatch, PostgreSQL, SLRW, semantic parser, formal gap resolution, session refresh and model controls.

Formal model remains an unverified specification: Promoted implies Verified; Selected implies canonical source exists; Ambiguous implies Held; read-only implies no corpus delta. Python fixture tests can witness operational behavior but no Agda/Lean kernel-verified refinement from this composer to those properties has been established.
