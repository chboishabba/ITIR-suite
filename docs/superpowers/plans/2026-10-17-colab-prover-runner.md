# Colab Prover Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tests-first, exact-SHA, allowlisted Google Colab prover runner that executes Lean/Lake and Agda jobs remotely and publishes replayable compiler receipts through a dedicated GitHub state branch.

**Architecture:** ITIR-suite owns a generic prover-job protocol, policy/argv builder, append-only GitHub relay, runtime receipt model, and worker. Google Colab is only the execution host: `google-colab-cli` is the primary headless runtime control surface, `googlecolab/colab-mcp` is an optional local-agent frontend, and repository verification semantics remain the ITIR job schema plus worker. Runtime queue state lives only on `colab-runner-state`; source code stays on reviewed source branches.

**Tech Stack:** Python 3, pytest, JSON Schema, Git/GitHub REST semantics, Google Colab, `google-colab-cli`, optional `googlecolab/colab-mcp`, `elan`, Lean/Lake, Agda.

**Spec:** `docs/superpowers/specs/2026-10-17-colab-prover-runner-design.md`

## Global Constraints

- Canonical runtime-state branch is exactly `colab-runner-state`.
- Upstream `googlecolab/google-colab-cli` is pinned initially to commit `006ff96ac2d0e4dcfb702467a76493d687929be8`.
- Upstream `googlecolab/colab-mcp` is pinned initially to commit `b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1`.
- Allowed repositories in v1: `chboishabba/dashi_lean4`, `chboishabba/dashi_agda`.
- Allowed operations in v1: `lake_build`, `lake_env_lean`, `agda_module`.
- Every executable job must carry an exact 40-hex commit SHA; mutable refs do not substitute for it.
- Public protocol accepts no arbitrary shell string, arbitrary environment override, arbitrary URL, or arbitrary package-install command.
- Default toolchain policy is `repo_pinned`; Lean jobs respect `lean-toolchain` and Agda jobs record the actual project/runtime Agda configuration.
- Local workstation policy remains: no local `lean`, `lake`, or `agda` compiler builds; local verification is pytest/static review only.
- Compiler success is only a compiler receipt and must not merge code, promote theorem authority, or alter Clay status.
- Jobs are immutable after submission; claim takeover is append-only using generation-suffixed claim files.
- Generated jobs/claims/results/logs must never be committed to `main`.

## Review Focus

- **Concurrent claim race:** two workers seeing the same unclaimed job must produce at most one active execution; the loser must observe the claim collision and abstain.
- **Malformed or hostile path arguments:** absolute paths, `..`, symlink escapes, and shell-like payloads must be rejected before checkout execution.
- **Publish failure after compiler completion:** a durable local terminal result must be republished without rerunning the compiler.
- **Runtime eviction/stale claim:** a later worker must be able to create a recorded takeover generation without overwriting earlier claim history.
- **Repository toolchain mismatch:** `repo_pinned` must never silently force baseline Lean `v4.35.0-rc3` over a checkout's `lean-toolchain`; the receipt must record what actually ran.

---

## File Structure

Create the runner as a small package with thin root scripts:

- `tools/colab-runner/pyproject.toml` — package metadata and runtime/test dependencies.
- `tools/colab-runner/README.md` — operator-facing setup, notebook launcher, security model, and acceptance workflow.
- `tools/colab-runner/src/itir_colab_runner/model.py` — typed job/result/claim models, canonical serialization, digest construction.
- `tools/colab-runner/src/itir_colab_runner/policy.py` — repository/operation allowlists, path validation, deterministic argv construction.
- `tools/colab-runner/src/itir_colab_runner/github_relay.py` — abstract relay interface plus GitHub-backed append-only implementation.
- `tools/colab-runner/src/itir_colab_runner/executor.py` — exact-SHA checkout/worktree orchestration and subprocess lifecycle.
- `tools/colab-runner/src/itir_colab_runner/runtime_receipt.py` — prover/runtime version and memory metadata.
- `tools/colab-runner/src/itir_colab_runner/worker.py` — poll/claim/execute/publish state machine.
- `scripts/colab_submit.py` — thin submitter CLI over the shared package.
- `scripts/colab_worker.py` — thin long-running worker CLI.
- `scripts/colab_bootstrap_provers.py` — idempotent Colab environment bootstrap and environment receipt.
- `schemas/colab_prover_job_v1.schema.json` — job wire contract.
- `schemas/colab_prover_result_v1.schema.json` — terminal result wire contract.
- `tests/test_colab_prover_protocol.py` — protocol/policy/digest contract tests.
- `tests/test_colab_prover_relay.py` — claim/idempotency/log-publish relay tests using a fake relay backend.
- `tests/test_colab_prover_worker.py` — worker state-machine tests with fake executor and fake relay.
- `tests/test_colab_prover_bootstrap.py` — bootstrap plan/idempotency/version-policy tests without installing compilers.

Do not place notebook-specific semantics in the package. The user's Colab notebook remains a thin launcher for bootstrap + worker.

---

### Task 1: Package Skeleton, Schemas, and Canonical Job Model

**Files:**
- Create: `tools/colab-runner/pyproject.toml`
- Create: `tools/colab-runner/src/itir_colab_runner/__init__.py`
- Create: `tools/colab-runner/src/itir_colab_runner/model.py`
- Create: `schemas/colab_prover_job_v1.schema.json`
- Create: `schemas/colab_prover_result_v1.schema.json`
- Create: `tests/test_colab_prover_protocol.py`

**Interfaces:**
- Produces: `ProverJob`, `ClaimReceipt`, `ProverResult`, `canonical_json_bytes(value) -> bytes`, `job_digest(job) -> str`, `load_job(data) -> ProverJob`, `load_result(data) -> ProverResult`.
- Later tasks must use these models rather than hand-assembling relay JSON.

- [ ] **Step 1: Write failing protocol tests**

Add tests asserting:

```python
def test_valid_lake_build_job_round_trips(): ...
def test_valid_agda_module_job_round_trips(): ...
def test_job_requires_exact_40_hex_sha(): ...
def test_unknown_repository_is_rejected(): ...
def test_unknown_operation_is_rejected(): ...
def test_canonical_job_digest_is_stable_across_key_order(): ...
def test_result_status_is_limited_to_terminal_v1_values(): ...
```

Pin the exact repository/operation enums and `schema_version` values from the spec.

- [ ] **Step 2: Run the protocol tests and verify RED**

Run:

```bash
pytest tests/test_colab_prover_protocol.py -v
```

Expected: failures because schemas/package/model functions do not yet exist.

- [ ] **Step 3: Add package metadata and JSON schemas**

`pyproject.toml` must expose the package from `src/`, use Python 3.11+ compatibility, and declare only the dependencies required by the generic runner core and schema validation. The job schema must pin:

- `schema_version = colab_prover_job_v1`
- repository enum of the two approved repos
- operation enum of the three approved operations
- exact-SHA regex `^[0-9a-fA-F]{40}$`
- `toolchain_policy = repo_pinned` in v1
- bounded positive `timeout_seconds`
- typed `arguments` selected by operation

The result schema must pin terminal statuses `SUCCEEDED`, `FAILED`, `REJECTED`, `ABORTED` and require job digest, resolved SHA, argv, timing, runtime/toolchain receipt fields, and ordered log references.

- [ ] **Step 4: Implement canonical model loading and digesting**

Implement:

```python
def canonical_json_bytes(value: object) -> bytes: ...
def load_job(data: Mapping[str, object]) -> ProverJob: ...
def load_result(data: Mapping[str, object]) -> ProverResult: ...
def job_digest(job: ProverJob) -> str: ...
```

Digest is SHA-256 over canonical UTF-8 JSON with sorted keys and stable separators. Reject invalid schema data before constructing typed models.

- [ ] **Step 5: Run protocol tests and verify GREEN**

Run the Task 1 test file only; expected all PASS.

- [ ] **Step 6: Commit Task 1**

```bash
git add tools/colab-runner schemas tests/test_colab_prover_protocol.py
git commit -m "feat(colab-runner): add prover job and result protocol"
```

---

### Task 2: Security Policy and Deterministic Argv Builders

**Files:**
- Create: `tools/colab-runner/src/itir_colab_runner/policy.py`
- Modify: `tests/test_colab_prover_protocol.py`

**Interfaces:**
- Consumes: `ProverJob` from Task 1.
- Produces: `validate_job_policy(job) -> None`, `build_argv(job, checkout: Path) -> list[str]`, `validate_relative_source_path(checkout, relative_path, suffix) -> Path`.

- [ ] **Step 1: Add failing policy tests**

Add tests for:

```python
def test_lake_build_argv_is_vector_not_shell_string(): ...
def test_lake_env_lean_rejects_absolute_path(): ...
def test_lake_env_lean_rejects_parent_traversal(): ...
def test_lake_env_lean_rejects_wrong_suffix(): ...
def test_agda_module_rejects_parent_traversal(): ...
def test_shell_metacharacters_do_not_create_shell_execution_surface(): ...
def test_repo_pinned_is_the_only_v1_toolchain_policy(): ...
def test_symlink_escape_is_rejected(): ...
```

For the symlink test, create a temporary checkout root with a symlink pointing outside and assert rejection after real-path resolution.

- [ ] **Step 2: Run targeted policy tests and verify RED**

Expected: missing policy functions.

- [ ] **Step 3: Implement policy validators and argv construction**

Signatures:

```python
def validate_job_policy(job: ProverJob) -> None: ...
def validate_relative_source_path(checkout: Path, relative_path: str, suffix: str) -> Path: ...
def build_argv(job: ProverJob, checkout: Path) -> list[str]: ...
```

Pinned expansion rules:

- `lake_build`: `['lake', 'build', target]`
- `lake_env_lean`: `['lake', 'env', 'lean', validated_relative_path]`
- `agda_module`: deterministic Agda argv from validated `.agda` path plus named profile/include selection; no arbitrary passthrough flags.

Use `subprocess` argv semantics only; no `shell=True` path exists in this package.

- [ ] **Step 4: Run protocol/policy tests and verify GREEN**

Run `pytest tests/test_colab_prover_protocol.py -v`.

- [ ] **Step 5: Commit Task 2**

```bash
git add tools/colab-runner/src/itir_colab_runner/policy.py tests/test_colab_prover_protocol.py
git commit -m "feat(colab-runner): enforce prover execution policy"
```

---

### Task 3: Append-Only Relay and Claim/Takeover Semantics

**Files:**
- Create: `tools/colab-runner/src/itir_colab_runner/github_relay.py`
- Create: `tests/test_colab_prover_relay.py`

**Interfaces:**
- Consumes: Task 1 model serialization/digests.
- Produces generic `Relay` protocol and concrete `GitHubRelay`; key methods:

```python
submit_job(job: ProverJob) -> str
list_pending_jobs() -> list[str]
read_job(job_id: str) -> ProverJob
try_create_claim(job: ProverJob, worker_id: str, now: datetime) -> ClaimReceipt | None
create_takeover_claim(job: ProverJob, previous: ClaimReceipt, worker_id: str, now: datetime) -> ClaimReceipt
publish_log_chunks(job_id: str, chunks: Sequence[bytes]) -> list[LogChunkRef]
publish_result(result: ProverResult) -> None
```

- [ ] **Step 1: Write fake-backend relay tests first**

Tests must cover:

```python
def test_submit_is_idempotent_for_same_job_id_and_digest(): ...
def test_conflicting_job_id_reuse_is_rejected(): ...
def test_only_one_worker_wins_initial_claim(): ...
def test_claim_generation_paths_are_append_only(): ...
def test_stale_takeover_creates_next_generation_without_overwrite(): ...
def test_log_chunks_have_deterministic_order_and_sha256(): ...
def test_publish_result_is_idempotent_for_same_terminal_receipt(): ...
def test_publish_result_rejects_conflicting_terminal_receipt(): ...
```

Use an in-memory content-addressed backend that models GitHub create-if-absent conflicts; do not require network access.

- [ ] **Step 2: Run relay tests and verify RED**

Run `pytest tests/test_colab_prover_relay.py -v`.

- [ ] **Step 3: Implement relay path conventions and fakeable storage boundary**

Canonical paths:

```text
.itir/colab/jobs/<job-id>.json
.itir/colab/claims/<job-id>.0000.json
.itir/colab/claims/<job-id>.0001.json
.itir/colab/results/<job-id>.json
.itir/colab/logs/<job-id>/<chunk-index>.txt
```

All runtime writes target branch `colab-runner-state`. The implementation must use optimistic create/update rules and must never force-push that branch.

- [ ] **Step 4: Implement `GitHubRelay` with an injectable GitHub content client**

Keep the HTTP/GitHub client dependency behind a minimal adapter so unit tests remain offline. A failed create caused by an already-existing path must be re-read and compared by digest/content rather than blindly retried.

- [ ] **Step 5: Run relay + protocol tests and verify GREEN**

- [ ] **Step 6: Commit Task 3**

```bash
git add tools/colab-runner/src/itir_colab_runner/github_relay.py tests/test_colab_prover_relay.py
git commit -m "feat(colab-runner): add append-only GitHub relay"
```

---

### Task 4: Runtime Receipts, Log Redaction, and Subprocess Executor

**Files:**
- Create: `tools/colab-runner/src/itir_colab_runner/runtime_receipt.py`
- Create: `tools/colab-runner/src/itir_colab_runner/executor.py`
- Modify: `tests/test_colab_prover_protocol.py`
- Create/Modify: `tests/test_colab_prover_worker.py`

**Interfaces:**
- Produces:

```python
collect_runtime_receipt(operation: str, checkout: Path) -> RuntimeReceipt
redact_text(text: str, secrets: Sequence[str]) -> str
chunk_log(data: bytes, max_bytes: int) -> list[bytes]
prepare_checkout(repository: str, commit_sha: str, workspace: Path) -> Checkout
execute_job(job: ProverJob, checkout: Checkout, secrets: Sequence[str]) -> ExecutionOutcome
```

- [ ] **Step 1: Add failing runtime/executor tests**

Cover:

```python
def test_secret_redaction_removes_configured_token_values(): ...
def test_log_chunking_respects_max_bytes_and_reassembles_exactly(): ...
def test_runtime_receipt_serializes_memory_and_tool_versions(): ...
def test_prepare_checkout_requests_exact_detached_sha_not_branch(): ...
def test_executor_uses_shell_false_semantics(): ...
def test_nonzero_exit_becomes_failed_outcome_not_exception_loss(): ...
def test_timeout_becomes_aborted_outcome_with_logs(): ...
```

Subprocess/git operations are injected fakes in tests; do not run Lean/Agda locally.

- [ ] **Step 2: Run tests and verify RED**

- [ ] **Step 3: Implement runtime receipt collection**

Record Python version, OS/kernel, CPU count, memory before/after, and operation-relevant `lean --version` / `lake --version` / `agda --version` outputs through argv subprocesses only. Missing optional metadata should be represented explicitly, not crash the job.

- [ ] **Step 4: Implement checkout/execution lifecycle**

`prepare_checkout` must clone/fetch only the approved repo, verify the requested commit exists, and materialize a detached exact-SHA worktree. `execute_job` obtains argv from Task 2 and invokes it with timeout, captured stdout/stderr, `shell=False`, and a minimal inherited environment.

- [ ] **Step 5: Implement deterministic log chunking/redaction**

Redact configured sensitive values before chunk hashing/publication. Chunks must reassemble byte-for-byte to the redacted log stream.

- [ ] **Step 6: Run protocol + executor tests and verify GREEN**

- [ ] **Step 7: Commit Task 4**

```bash
git add tools/colab-runner/src/itir_colab_runner/{runtime_receipt.py,executor.py} tests
git commit -m "feat(colab-runner): execute exact-SHA prover jobs"
```

---

### Task 5: Worker State Machine and Durable Publication Retry

**Files:**
- Create: `tools/colab-runner/src/itir_colab_runner/worker.py`
- Create/Modify: `tests/test_colab_prover_worker.py`
- Create: `scripts/colab_worker.py`

**Interfaces:**
- Consumes: relay, policy, executor, models from Tasks 1–4.
- Produces:

```python
run_one_job(relay: Relay, executor: Executor, worker_id: str, now: datetime) -> WorkerOutcome
run_poll_loop(...)
```

- [ ] **Step 1: Write worker tests first**

Cover:

```python
def test_worker_rejects_invalid_job_before_checkout(): ...
def test_worker_claims_before_execution(): ...
def test_claim_loser_does_not_execute(): ...
def test_successful_execution_publishes_logs_then_terminal_result(): ...
def test_compiler_nonzero_publishes_failed_result(): ...
def test_publish_failure_retains_local_terminal_result_for_retry_without_reexecution(): ...
def test_stale_claim_takeover_is_recorded_before_retry_execution(): ...
def test_worker_never_mutates_source_repository_or_pr_state(): ...
```

For the publication-retry test, count executor calls and assert exactly one execution across multiple publish attempts.

- [ ] **Step 2: Run worker tests and verify RED**

- [ ] **Step 3: Implement one-job state machine**

Order is fixed:

```text
read -> validate -> claim -> prepare -> RUNNING -> execute -> redact/chunk -> persist local terminal receipt -> publish chunks -> publish result
```

If publication fails after terminal execution, later retries begin from the durable local terminal receipt and skip execution.

- [ ] **Step 4: Implement thin worker CLI**

`scripts/colab_worker.py` only parses worker/state options, loads GitHub credentials from environment/Colab Secrets injection, constructs shared package objects, and calls poll-loop APIs. It must expose no arbitrary command-execution flag.

- [ ] **Step 5: Run all runner unit tests and verify GREEN**

```bash
pytest tests/test_colab_prover_protocol.py tests/test_colab_prover_relay.py tests/test_colab_prover_worker.py -v
```

- [ ] **Step 6: Commit Task 5**

```bash
git add tools/colab-runner/src/itir_colab_runner/worker.py scripts/colab_worker.py tests/test_colab_prover_worker.py
git commit -m "feat(colab-runner): add idempotent Colab worker"
```

---

### Task 6: Submitter CLI and State-Branch Bootstrap

**Files:**
- Create: `scripts/colab_submit.py`
- Modify: `tests/test_colab_prover_relay.py`
- Modify: `tools/colab-runner/README.md`

**Interfaces:**
- Produces a thin CLI capable of creating validated job JSON and submitting it to `colab-runner-state` through the relay.

- [ ] **Step 1: Add failing submitter tests**

Pin:

```python
def test_submitter_requires_exact_sha(): ...
def test_submitter_cannot_submit_arbitrary_operation(): ...
def test_submitter_same_job_is_idempotent(): ...
def test_submitter_conflicting_job_id_is_rejected(): ...
def test_state_branch_name_is_fixed_to_colab_runner_state(): ...
```

- [ ] **Step 2: Run targeted tests and verify RED**

- [ ] **Step 3: Implement `scripts/colab_submit.py`**

CLI accepts only typed fields required to build a v1 job. It does not accept a raw JSON command string or raw shell command. It prints the job ID, digest, repository, SHA, and state-branch path after successful submission.

- [ ] **Step 4: Document orphan/state-branch initialization**

README must explain one-time creation of `colab-runner-state` as a runtime-only branch and explicitly state that generated state is never merged back to `main`.

- [ ] **Step 5: Run relay/submitter tests and verify GREEN**

- [ ] **Step 6: Commit Task 6**

```bash
git add scripts/colab_submit.py tools/colab-runner/README.md tests/test_colab_prover_relay.py
git commit -m "feat(colab-runner): add validated job submitter"
```

---

### Task 7: Idempotent Colab Prover Bootstrap

**Files:**
- Create: `scripts/colab_bootstrap_provers.py`
- Create: `tests/test_colab_prover_bootstrap.py`
- Modify: `tools/colab-runner/README.md`

**Interfaces:**
- Produces:

```python
build_bootstrap_plan(platform: PlatformFacts) -> BootstrapPlan
apply_bootstrap_plan(plan: BootstrapPlan, runner: CommandRunner) -> BootstrapReceipt
```

- [ ] **Step 1: Write bootstrap tests first**

Cover:

```python
def test_bootstrap_pins_google_colab_cli_commit(): ...
def test_bootstrap_pins_colab_mcp_commit_as_optional_frontend(): ...
def test_bootstrap_baseline_lean_is_v4_35_0_rc3(): ...
def test_repo_pinned_policy_does_not_override_checkout_lean_toolchain(): ...
def test_bootstrap_is_idempotent_when_tools_already_match(): ...
def test_bootstrap_receipt_records_actual_versions(): ...
def test_bootstrap_plan_never_serializes_github_token(): ...
```

Tests inspect plans/receipts with a fake command runner; they must not install toolchains locally.

- [ ] **Step 2: Run bootstrap tests and verify RED**

- [ ] **Step 3: Implement deterministic bootstrap planning**

Plan checks/installs:

- Git
- Python package environment for runner
- `elan`
- baseline Lean `v4.35.0-rc3`
- Lake availability through the Lean toolchain
- Agda and required stdlib/package support
- pinned `google-colab-cli`
- optional pinned `colab-mcp`

Keep package-manager specifics isolated in the bootstrap script/profile and emit every planned/applied step into a receipt without secrets.

- [ ] **Step 4: Implement `repo_pinned` precedence**

When a checkout contains `lean-toolchain`, execution uses that repository declaration even if baseline Lean differs. The bootstrap receipt records baseline and actual repo toolchain separately.

- [ ] **Step 5: Run bootstrap tests and verify GREEN**

- [ ] **Step 6: Commit Task 7**

```bash
git add scripts/colab_bootstrap_provers.py tests/test_colab_prover_bootstrap.py tools/colab-runner/README.md
git commit -m "feat(colab-runner): bootstrap Colab prover toolchains"
```

---

### Task 8: Operator Documentation and Notebook Launcher Contract

**Files:**
- Modify: `tools/colab-runner/README.md`
- Create: `docs/colab-prover-runner-notebook.md`
- Modify: `tests/test_colab_prover_protocol.py`

**Interfaces:**
- Documentation only; no notebook becomes the source of truth.

- [ ] **Step 1: Add static documentation contract tests**

Tests should assert the docs contain:

- exact bootstrap script invocation;
- exact worker invocation;
- `colab-runner-state` warning;
- Colab Secrets requirement;
- prohibition on secret embedding;
- statement that notebook cells are launchers only;
- no local Lean/Agda execution instruction for the workstation;
- upstream pin SHAs.

- [ ] **Step 2: Run static doc tests and verify RED**

- [ ] **Step 3: Write operator guide and notebook launcher recipe**

The notebook recipe must be minimal:

```text
clone/fetch ITIR-suite exact runner SHA
load GitHub token from Colab Secrets into process environment
python scripts/colab_bootstrap_provers.py
python scripts/colab_worker.py --poll
```

Do not embed the token, custom prover logic, or repository mutation logic in notebook cells.

- [ ] **Step 4: Run documentation contract tests and verify GREEN**

- [ ] **Step 5: Commit Task 8**

```bash
git add tools/colab-runner/README.md docs/colab-prover-runner-notebook.md tests/test_colab_prover_protocol.py
git commit -m "docs(colab-runner): add Colab operator launcher guide"
```

---

### Task 9: Full Local Static Verification and PR Handoff

**Files:**
- No new production files unless failures reveal a defect.

**Interfaces:**
- Produces a source branch ready for Colab acceptance testing; does not perform Lean/Agda builds locally.

- [ ] **Step 1: Run the complete runner test suite locally**

```bash
pytest \
  tests/test_colab_prover_protocol.py \
  tests/test_colab_prover_relay.py \
  tests/test_colab_prover_worker.py \
  tests/test_colab_prover_bootstrap.py -v
```

Expected: all PASS.

- [ ] **Step 2: Perform static arbitrary-shell audit**

Search the runner package/scripts for `shell=True`, `bash -c`, `os.system`, unvalidated `subprocess` strings, and raw job-provided environment interpolation. Expected: none in executable paths.

- [ ] **Step 3: Verify source branch does not contain runtime queue artifacts**

Expected: no `.itir/colab/jobs`, claims, results, or logs committed to the reviewed source branch.

- [ ] **Step 4: Open/update ITIR-suite PR**

PR description must state that real prover acceptance has not yet run, list the exact upstream pins, and link the spec/plan.

- [ ] **Step 5: Commit any verification-only fixes separately**

Do not squash evidence-relevant fixes into earlier commits before review.

---

### Task 10: First Real Colab Acceptance Jobs

**Files:**
- Runtime-only writes on `colab-runner-state`.
- Source changes only if an acceptance failure identifies a runner defect.

**Interfaces:**
- Consumes the merged/approved runner source branch and provisioned user Colab High-RAM runtime.
- Produces real `colab_prover_result_v1` receipts visible through GitHub.

- [ ] **Step 1: Initialize the runtime-state branch and start worker in Colab**

In the provisioned notebook/runtime, checkout the exact ITIR runner commit, load the fine-grained GitHub token from Colab Secrets, run bootstrap, then run the poll worker. Do not run these commands on the local workstation.

- [ ] **Step 2: Submit a narrow Lean acceptance job**

Use exact current `dashi_lean4` commit SHA and operation `lake_build`. Prefer a known bounded target first; if `QuantumMereology` is the selected acceptance target, record it explicitly in the job.

Expected receipt: terminal `SUCCEEDED` or an actionable compiler `FAILED`; either outcome must include exact SHA, argv, tool versions, memory metadata, and log hashes.

- [ ] **Step 3: Submit a narrow Agda acceptance job**

Use exact current `dashi_agda` commit SHA and operation `agda_module` for one canonical safe module, initially a small canonical module rather than the full repository.

Expected receipt semantics are the same as Lean.

- [ ] **Step 4: Test ChatGPT relay visibility**

Using only the existing GitHub connector, read the submitted job and terminal result/log refs from `colab-runner-state`. Confirm no direct Colab/MCP connection is required for result inspection.

- [ ] **Step 5: Exercise one failure path intentionally**

Submit a valid-policy job that is expected to produce a compiler nonzero exit at an exact test SHA, or use a controlled fixture repo state if available. Confirm it becomes `FAILED`, not `REJECTED`, and that logs are retained.

- [ ] **Step 6: Exercise claim idempotency**

Run/restart a second worker while an already-claimed test job exists and confirm no duplicate compiler execution occurs.

- [ ] **Step 7: Record acceptance report**

Add a reviewed source document such as `docs/reports/2026-10-17-colab-prover-runner-acceptance.md` containing only non-secret job IDs, exact source SHAs, result statuses, toolchain versions, and observed runtime facts. Runtime queue artifacts remain on `colab-runner-state`.

---

## Execution Sequence

Tasks 1–8 are source implementation and must follow TDD. Task 9 is the local static gate. Task 10 is the first real compiler gate and runs only in the provisioned Colab environment.

Do not collapse Task 10 into source implementation: the runner should be reviewable/testable without requiring a live Colab allocation, and real compiler receipts should remain independently auditable.
