# SB/Casey/JesusCrust Followthrough (2026-02-07)

This document materializes the requested followthrough from the three live threads:

- `6986c9f5-3988-839d-ad80-9338ea8a04eb` (`Conductor vs SB/ITIR`)
  - Latest assistant timestamp: `2026-02-08T03:09:11.241219Z`
- `6986ccc6-a58c-83a1-9c72-76c671dd7af0` (`Codeex and Vibe Faster`)
  - Latest assistant timestamp: `2026-02-07T05:34:09.991600Z`
- `6986c16d-e97c-839b-82b8-425b1e5a5e6d` (`GPU Methodology for CPU`)
  - Latest assistant timestamp: `2026-02-07T05:23:13.297950Z`
- Live revalidation artifact:
  - `__CONTEXT/last_sync/20260208T054446Z_latest_triplet_6986c9f5_6986ccc6_6986c16d.tsv`

---

## 0. Thread Synthesis (Flow / Blockers / Progress)

### 0.1 `6986c9f5-3988-839d-ad80-9338ea8a04eb` (Conductor vs SB/ITIR)
- Flow:
  - shifted from tool comparison to memory authority and cloud/control-plane economics.
  - converged on "Cloud as Observer, Not Authority" and "Database != Memory".
  - clarified non-overlap between execution platforms (Convex/Agent HQ) and SB memory scope.
  - latest turn tightened boundary against digital-forensics toolchains
    (EnCase/TSK/Autopsy): post-mortem analyzers vs SB as living, loss-aware memory.
- Blockers:
  - platform retention/billing can silently erase reconstructible history.
  - execution-layer convenience pressures scope creep into memory authority.
  - risk of conflating repo/app state with durable historical truth.
  - product positioning drift: treating forensic analysis tools as memory-plane substitutes.
- Progress:
  - SB observer-boundary docs and context notes were updated in-repo.
  - ADR direction and acceptance-check framing are now explicit and test-oriented.
  - this document now provides implementation-ready invariants/checks in sections `1.1`-`1.5`.
  - boundary language now includes explicit "forensics != canonical memory" framing.

### 0.2 `6986ccc6-a58c-83a1-9c72-76c671dd7af0` (Codeex and Vibe Faster)
- Flow:
  - identified "parallelizer" as multi-thread orchestration, not a new VCS model.
  - mapped agent-thread workflow to explicit boundary commits and manager-level coordination.
- Blockers:
  - temptation to leak orchestration semantics into core versioning state model.
  - lack of codified pre/post contracts and deterministic rollback tests in the Casey lane.
- Progress:
  - live thread captured in Casey conversation mapping artifacts.
  - explicit model, operation, failure, and test plans are now documented in sections
    `2.1`-`2.5`.
  - environment proposal added in section `2.6`.

### 0.3 `6986c16d-e97c-839b-82b8-425b1e5a5e6d` (GPU Methodology for CPU / JavaCrust-adjacent)
- Flow:
  - separated orchestration (human/agent thread management) from execution (kernel run).
  - reinforced run-to-completion and commit/fallback boundaries as first-class.
  - positioned JesusCrust as execution substrate, not memory authority.
- Blockers:
  - risk of mid-execution hooks and interactive mutation paths breaking determinism.
  - missing explicit cross-project boundary contract between JesusCrust execution events
    and SB memory ingest.
- Progress:
  - JesusCrust now present in repo and referenced by concrete contract files.
  - integration notes and ADR-ready boundary wording are captured in sections
    `3.1`-`3.5`.

---

## 1. SB/Fuzzer Thread

### 1.1 Hard invariants (SB <-> fuzzer integration)
1. Fuzzer outputs are observational inputs only; they never become authoritative state.
2. Every derived claim must retain a provenance pointer to raw event/input artifacts.
3. Loss is explicit: truncation, summarization, and expiry require machine-readable annotations.
4. Replay must be deterministic from fixed inputs and fixed policy version.
5. Cloud/provider availability cannot be required to reconstruct prior state.
6. Missing data is represented as absence, not inferred continuity.
7. Execution telemetry and policy decisions are split artifacts.
8. Promotion from observed to declared state requires explicit act + receipt.
9. Cross-tool ingestion must be schema-validated before persistence.
10. Rejections are first-class events with reason codes and source IDs.
11. Time ordering is explicit (UTC timestamps, monotonic ordering where possible).
12. Version drift is recorded (schema version + policy hash per ingest batch).

### 1.2 Acceptance checks (mechanically testable)
1. Cloud removal test: disable network/provider credentials; replay and query historical records locally.
2. Expiry test: simulate upstream retention gap; ensure explicit `loss_reason=expired_upstream`.
3. Billing pressure test: forbid paid re-fetch paths in replay; replay remains complete from local bundle.
4. Non-inventive test: inject missing interval; pipeline must emit gap markers, no synthetic fill.
5. Determinism test: same fixture + same policy hash -> identical normalized output hash.
6. Provenance test: every promoted artifact must include source URI/ID and acquisition timestamp.
7. Rejection-path test: malformed observer payload logs structured reject event and does not mutate state.
8. Schema version test: mixed-version payloads are rejected or migrated with explicit receipt.

### 1.3 Minimal observer/loss schema

```json
{
  "schema_version": "sb.observer.v1",
  "event_id": "uuid",
  "ts_utc": "2026-02-07T06:10:06.463491Z",
  "source": {
    "tool": "codeex|convex|github|custom",
    "provider": "openai|github|self-hosted|other",
    "conversation_id": "optional-chat-id",
    "uri": "optional-pointer"
  },
  "kind": "session_started|session_completed|pr_opened|pr_merged|ci_finished|reject",
  "provenance": {
    "artifact_ids": ["..."],
    "policy_hash": "sha256:...",
    "ingest_hash": "sha256:..."
  },
  "loss": {
    "is_lossy": false,
    "reason": "expired_upstream|truncated|aggregated|none",
    "detail": ""
  }
}
```

### 1.4 Mapping to current artifacts (file targets)
1. SB invariants and contracts:
   - `StatiBaker/docs/tool_interop_observer_contract.md`
   - `StatiBaker/CONTEXT.md`
   - `StatiBaker/COMPACTIFIED_CONTEXT.md`
2. Fuzzymodo planning and policy:
   - `docs/planning/fuzzymodo/speculation_policy.md`
   - `docs/planning/fuzzymodo/conversation_step_map.md`
3. Suite context sync and tracked thread IDs:
   - `__CONTEXT/convo_ids.md`
   - `__CONTEXT/COMPACTIFIED_CONTEXT.md`
4. Suite TODO pipeline:
   - `TODO.md` (implementation tasks)

### 1.5 Axiom: Database != Memory
Database state is current execution truth for a running system; memory state is historical reconstruction truth across system lifetimes. A database can be deleted, migrated, or superseded without preserving meaning continuity. SB therefore treats databases as observers of history, never the sole authority over it.

---

## 2. Casey-Git Thread

### 2.1 Model constraints (state-machine style)
1. `PathState` may hold multiple candidates; superposition is valid state, not error.
2. `WorkspaceView.selection` is explicit and user-controlled.
3. Sync/publish operations are non-blocking and do not force collapse.
4. Collapse is explicit command only; never implicit during sync/publish.
5. Build snapshots are immutable once emitted.
6. IDs/hashes are canonicalized and deterministic.
7. Threaded orchestration is external to model semantics.

### 2.2 Operation contracts (pre/post)
1. `sync`:
   - pre: valid remote refs
   - post: candidate set may increase; no forced selection change
2. `publish`:
   - pre: active selection defined
   - post: emitted artifact points to explicit selection hash
3. `collapse`:
   - pre: conflict/superposed candidates exist
   - post: single candidate selected with collapse receipt
4. `snapshot_build`:
   - pre: selected candidate and deterministic build recipe
   - post: immutable snapshot ID + provenance pointer
5. `rollback`:
   - pre: prior stable state exists
   - post: state pointer reverts; prior trail retained

### 2.3 Failure modes + rollback semantics
1. Upstream divergence during sync: retain candidates; no auto-collapse.
2. Publish race: reject publish and require explicit refresh/reselect.
3. Hash mismatch on snapshot replay: mark snapshot invalid; keep prior stable pointer.
4. Partial operation crash: recover from last committed boundary only.
5. Policy/schema mismatch: reject mutation and emit structured refusal event.

### 2.4 Determinism + audit checks
1. Same candidate set + same selection + same recipe -> same snapshot hash.
2. Operation log is append-only and order-preserving.
3. Every collapse has actor/time/reason receipt.
4. Replay from operation log reproduces workspace view deterministically.
5. External orchestration metadata (thread IDs/jobs) must not alter core model transitions.

### 2.5 Tests to add (name + intent)
1. `test_sync_preserves_superposition_candidates`
2. `test_publish_requires_explicit_selection`
3. `test_collapse_requires_user_command`
4. `test_snapshot_hash_deterministic_for_fixed_recipe`
5. `test_replay_reconstructs_workspace_selection`
6. `test_external_thread_metadata_non_authoritative`
7. `test_rollback_returns_to_last_committed_boundary`
8. `test_schema_mismatch_rejected_without_mutation`

### 2.6 Proposed dev environment (Theo/parallelizer-aligned, boundary-safe)
1. Orchestration workstation: macOS or Linux laptop for multi-thread agent management.
2. Deterministic execution lane: Linux container/VM with pinned toolchains.
3. Local-first state lane: append-only local event store for history and replay.
4. Optional cloud lane: CI/agents as execution substrate only, never memory authority.
5. Standardized tooling:
   - Python venv for suite scripts
   - Rust toolchain for JesusCrust kernels
   - Node/npm for host and extension prototypes
6. Contract: thread/orchestration metadata is ingested read-only into local history.

---

## 3. JavaCrust/JesusCrust Thread

### 3.1 Principle set (execution boundaries)
1. Orchestration and execution are orthogonal concerns.
2. Run-to-completion boundaries are stability primitives.
3. Commit/fallback boundaries are the only observable mutation points.
4. Human/agent coordination belongs above kernel execution.
5. Memory authority remains outside execution vendors and runtimes.

### 3.2 Stack diagram

```text
Human Orchestrator
  -> Agent Threads (plan/patch proposals)
    -> JesusCrust Kernel (deterministic execution core)
      -> JS Host Sink (commit/fallback boundary)
        -> SB Memory Layer (append-only reconstruction + provenance)
```

### 3.3 Anti-patterns (do-not-do list)
1. Mid-execution mutation hooks into kernel state.
2. Implicit cross-thread state merges without explicit commit boundary.
3. Replacing provenance with summary text.
4. Treating cloud runtime artifacts as canonical memory.
5. Silent fallback/rollback without explicit emitted event.

### 3.4 Integration notes (SB/fuzzymodo/casey-git + JesusCrust)
1. JesusCrust boundary contracts:
   - `JesusCrust/docs/host-core-api.md`
   - `JesusCrust/docs/api.md`
   - `JesusCrust/docs/phase6_README.md`
2. SB ingest shape:
   - consume commit/fallback telemetry as observer events only
   - never infer intent from kernel runtime traces
3. Fuzzymodo alignment:
   - use selector/policy layers for analysis and constraints
   - keep execution telemetry outside normative authority paths
4. Casey alignment:
   - map thread orchestration metadata to operation log receipts
   - preserve explicit collapse and snapshot boundaries

### 3.5 ADR-ready wording
Orchestration improves throughput by parallelizing work streams; execution preserves correctness by enforcing deterministic run-to-completion boundaries; memory preserves accountability by storing append-only provenance across tool lifetimes. These layers may interoperate, but authority must not collapse across them: orchestration never rewrites execution truth, and execution truth never substitutes for memory sovereignty.
